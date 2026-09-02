from __future__ import annotations

import copy
import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from runtime.skill_state import (
    StateValidationError,
    apply_host_patch,
    apply_state_patch,
    build_prompt,
    initial_state,
    main,
    parse_transition,
)


class _MutatingOnDeepcopyDict(dict[str, object]):
    """Mutate the caller-owned object after returning an isolated snapshot."""

    def __deepcopy__(self, memo: dict[int, object]) -> dict[str, object]:
        snapshot = copy.deepcopy(dict(self), memo)
        self["objective"] = "mutated outside the prompt snapshot"
        return snapshot


class SkillStateHardeningTests(unittest.TestCase):
    def test_duplicate_json_keys_are_rejected(self) -> None:
        with self.assertRaisesRegex(StateValidationError, "duplicate JSON object key"):
            parse_transition(
                '{"state_patch":{},"action":"safe","action":"different"}'
            )

    def test_nonfinite_json_numbers_are_rejected(self) -> None:
        with self.assertRaisesRegex(StateValidationError, "non-finite JSON number"):
            parse_transition(
                '{"state_patch":{"facts":{"value":NaN}},"action":"inspect"}'
            )

    def test_invalid_python_inputs_fail_with_validation_errors(self) -> None:
        state = initial_state("keep a stable contract", ["invalid input fails closed"])
        invalid_calls = (
            lambda: initial_state("invalid", None),  # type: ignore[arg-type]
            lambda: parse_transition(None),  # type: ignore[arg-type]
            lambda: parse_transition([("state_patch", {}), ("action", "run")]),  # type: ignore[arg-type]
            lambda: apply_host_patch(
                state,
                {"route": {"retrieval": "NONE"}, 1: None, "unexpected": None},  # type: ignore[dict-item]
            ),
        )
        for invalid_call in invalid_calls:
            with self.subTest(call=invalid_call), self.assertRaises(StateValidationError):
                invalid_call()

    def test_deep_patch_is_rejected_before_recursive_merge(self) -> None:
        state = initial_state("bound recursive input", ["invalid patch does not crash"])
        nested: object = "leaf"
        for _ in range(1500):
            nested = {"next": nested}
        with self.assertRaisesRegex(StateValidationError, "nesting depth"):
            apply_state_patch(state, {"facts": nested})  # type: ignore[dict-item]

    def test_action_rejects_terminal_control_characters(self) -> None:
        with self.assertRaisesRegex(StateValidationError, "control character"):
            parse_transition(
                '{"state_patch":{},"action":"inspect\\u001b[2J"}'
            )

    def test_prompt_serializes_an_isolated_validated_snapshot(self) -> None:
        state = _MutatingOnDeepcopyDict(
            initial_state("snapshot objective", ["prompt uses one isolated state"])
        )
        prompt = build_prompt("Take one step.", state, "Current observation")
        self.assertEqual(state["objective"], "mutated outside the prompt snapshot")

        marker = "Runtime Input (JSON):\n"
        output_marker = "\n\nOutput Contract:\n"
        payload = prompt.split(marker, 1)[1].split(output_marker, 1)[0]
        decoded = json.loads(payload)
        self.assertEqual(decoded["state"]["objective"], "snapshot objective")
        self.assertIn("only a proposal", prompt)
        self.assertIn("independently authorize", prompt)

    def test_cli_rejects_duplicate_transition_without_overwriting_output(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            state_path = root / "state.json"
            response_path = root / "response.json"
            output_path = root / "successor.json"
            state_path.write_text(
                json.dumps(initial_state("protect output", ["invalid response is rejected"])),
                encoding="utf-8",
            )
            response_path.write_text(
                '{"state_patch":{},"action":"first","action":"second"}',
                encoding="utf-8",
            )
            output_path.write_text("existing-output\n", encoding="utf-8")

            stdout = io.StringIO()
            stderr = io.StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                result = main(
                    [
                        "transition",
                        str(state_path),
                        str(response_path),
                        "--output",
                        str(output_path),
                    ]
                )

            self.assertEqual(result, 2)
            self.assertEqual(stdout.getvalue(), "")
            self.assertIn("duplicate JSON object key", stderr.getvalue())
            self.assertEqual(output_path.read_text(encoding="utf-8"), "existing-output\n")


if __name__ == "__main__":
    unittest.main()

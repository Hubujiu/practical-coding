from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from runtime.skill_state import build_prompt, initial_state
from runtime.skill_state_host import (
    HistoryFreeHost,
    HistoryFreeLimits,
    HostBoundaryError,
    StatePersistenceError,
    TransitionRetriesExhausted,
    TransportResponse,
    audit_wire_request,
    audit_wire_request_against_manifest,
    main,
    validate_manifest,
)


def _response(text: str, *, input_tokens: int = 100, output_tokens: int = 20) -> bytes:
    return json.dumps(
        {
            "id": "resp_test",
            "status": "completed",
            "output": [
                {
                    "type": "reasoning",
                    "summary": [],
                },
                {
                    "type": "message",
                    "content": [{"type": "output_text", "text": text}],
                },
            ],
            "usage": {
                "input_tokens": input_tokens,
                "input_tokens_details": {"cached_tokens": 10},
                "output_tokens": output_tokens,
                "total_tokens": input_tokens + output_tokens,
            },
        },
        separators=(",", ":"),
    ).encode("utf-8")


class HistoryFreeHostTests(unittest.TestCase):
    def setUp(self) -> None:
        self.state = initial_state("repair release", ["focused check passes"])
        self.host = HistoryFreeHost(
            model="gpt-test",
            procedure="Use the smallest evidenced change and return one transition.",
            options={"max_output_tokens": 512, "reasoning": {"effort": "medium"}},
        )

    def test_runtime_prompt_uses_a_valid_minimal_json_example(self) -> None:
        prompt = build_prompt("Take one step.", self.state, "Current observation")
        self.assertIn(
            '{"state_patch":{},"action":"<proposed next command or tool action>"}',
            prompt,
        )
        self.assertNotIn('"state_patch":{...}', prompt)

    def test_prepared_request_has_one_current_item_and_no_history_controls(self) -> None:
        prepared = self.host.prepare_request(self.state, "Current check failed", step_id="s1")
        body = prepared.body()

        self.assertEqual(body["model"], "gpt-test")
        self.assertIsInstance(body["instructions"], str)
        self.assertIn("immutable and authoritative", body["instructions"])
        self.assertEqual(len(body["input"]), 1)
        self.assertEqual(body["input"][0]["role"], "user")
        self.assertFalse(body["store"])
        self.assertFalse(body["stream"])
        self.assertFalse(body["background"])
        self.assertEqual(body["truncation"], "disabled")
        input_payload = json.loads(body["input"][0]["content"][0]["text"])
        self.assertEqual(set(input_payload), {"state", "latest_observation"})
        self.assertEqual(input_payload["state"], self.state)
        self.assertEqual(input_payload["latest_observation"], "Current check failed")
        self.assertNotIn("Use the smallest evidenced change", body["input"][0]["content"][0]["text"])
        for forbidden in ("previous_response_id", "conversation", "context_management", "prompt"):
            self.assertNotIn(forbidden, body)

        audit = dict(prepared.audit)
        self.assertTrue(audit["bounded_context_eligible"])
        self.assertEqual(audit["historical_input_item_count"], 0)
        self.assertEqual(audit["step_id"], "s1")
        self.assertLessEqual(audit["wire_request_bytes"], audit["wire_request_limit_bytes"])
        standalone = dict(audit_wire_request(prepared.wire_bytes))
        self.assertEqual(standalone["request_sha256"], audit["request_sha256"])
        self.assertFalse(standalone["manifest_match"])
        self.assertFalse(standalone["bounded_context_eligible"])
        frozen = dict(audit_wire_request_against_manifest(prepared.wire_bytes, self.host.manifest()))
        self.assertTrue(frozen["manifest_match"])
        self.assertEqual(frozen["manifest_sha256"], self.host.manifest()["manifest_sha256"])
        self.assertEqual(frozen["procedure_sha256"], self.host.manifest()["procedure_sha256"])

    def test_audit_rejects_history_fields_and_old_input_items(self) -> None:
        body = self.host.prepare_request(self.state, "Current observation").body()
        body["previous_response_id"] = "resp_old"
        with self.assertRaises(HostBoundaryError):
            audit_wire_request(json.dumps(body).encode("utf-8"))

        body = self.host.prepare_request(self.state, "Current observation").body()
        body["input"].insert(0, {"role": "assistant", "content": [{"type": "output_text", "text": "old"}]})
        with self.assertRaisesRegex(HostBoundaryError, "exactly one current user item"):
            audit_wire_request(json.dumps(body).encode("utf-8"))

    def test_options_cannot_import_server_side_context(self) -> None:
        for options in (
            {"previous_response_id": "resp_old"},
            {"reasoning": {"context": "opaque-prior-reasoning"}},
            {"prompt_cache_options": {"conversation": "old"}},
        ):
            with self.subTest(options=options), self.assertRaises(HostBoundaryError):
                HistoryFreeHost(model="gpt-test", procedure="Take one step.", options=options)

    def test_output_schema_property_names_do_not_become_history_controls(self) -> None:
        host = HistoryFreeHost(
            model="gpt-test",
            procedure="Take one step.",
            options={
                "text": {
                    "format": {
                        "type": "json_schema",
                        "name": "transition",
                        "schema": {
                            "type": "object",
                            "properties": {"history": {"type": "string"}},
                        },
                    }
                }
            },
        )
        self.assertTrue(host.prepare_request(self.state, "Current observation").audit["bounded_context_eligible"])

    def test_manifest_digest_and_procedure_identity_are_enforced(self) -> None:
        manifest = copy.deepcopy(dict(self.host.manifest()))
        self.assertEqual(validate_manifest(manifest)["manifest_sha256"], manifest["manifest_sha256"])

        tampered_manifest = copy.deepcopy(manifest)
        tampered_manifest["model"] = "gpt-other"
        with self.assertRaisesRegex(HostBoundaryError, "manifest SHA-256"):
            validate_manifest(tampered_manifest)

        prepared = self.host.prepare_request(self.state, "Current observation")
        body = prepared.body()
        instructions = body["instructions"]
        body["instructions"] = instructions.replace(
            "Use the smallest evidenced change",
            "Use a different procedure",
            1,
        )
        tampered_wire = json.dumps(body, separators=(",", ":"), sort_keys=True).encode("utf-8")
        with self.assertRaisesRegex(HostBoundaryError, "frozen procedure"):
            audit_wire_request_against_manifest(tampered_wire, manifest)

    def test_manifest_cannot_self_sign_runtime_contract_drift(self) -> None:
        def resign(manifest: dict[str, object]) -> None:
            unsigned = copy.deepcopy(manifest)
            unsigned.pop("manifest_sha256", None)
            payload = json.dumps(
                unsigned,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
                allow_nan=False,
            ).encode("utf-8")
            manifest["manifest_sha256"] = hashlib.sha256(payload).hexdigest()

        hard_limit_drift = copy.deepcopy(dict(self.host.manifest()))
        hard_limit_drift["component_hard_limits"]["state_bytes"] += 1
        resign(hard_limit_drift)
        with self.assertRaisesRegex(HostBoundaryError, "component_hard_limits"):
            validate_manifest(hard_limit_drift)

        request_contract_drift = copy.deepcopy(dict(self.host.manifest()))
        request_contract_drift["request_contract"]["input_items"] = 2
        resign(request_contract_drift)
        with self.assertRaisesRegex(HostBoundaryError, "request_contract"):
            validate_manifest(request_contract_drift)

    def test_limits_may_only_tighten_runtime_hard_caps(self) -> None:
        with self.assertRaisesRegex(HostBoundaryError, "runtime hard cap"):
            HistoryFreeLimits(max_retry_attempts=4)
        tightened = HistoryFreeLimits(max_retry_attempts=1, max_wire_request_bytes=1024)
        self.assertEqual(tightened.max_retry_attempts, 1)
        self.assertEqual(tightened.max_wire_request_bytes, 1024)

    def test_frozen_tools_and_options_are_isolated_from_caller_mutation(self) -> None:
        tools = [{"type": "function", "name": "inspect", "parameters": {"type": "object"}}]
        options = {"max_output_tokens": 128}
        host = HistoryFreeHost(
            model="gpt-test",
            procedure="Take one step.",
            tools=tools,
            options=options,
        )
        manifest_before = dict(host.manifest())
        tools[0]["name"] = "mutated"
        options["max_output_tokens"] = 999

        body = host.prepare_request(self.state, "Current observation").body()
        self.assertEqual(body["tools"][0]["name"], "inspect")
        self.assertEqual(body["max_output_tokens"], 128)
        self.assertEqual(dict(host.manifest()), manifest_before)

    def test_invalid_transition_retries_from_original_state_without_history(self) -> None:
        captured: list[bytes] = []
        responses = iter(
            [
                _response(
                    '{"state_patch":{"route":{"automatic_path":["core","debugging"]}},'
                    '"action":"unsafe-before-validation"}'
                ),
                _response(
                    '{"state_patch":{"next_action":"run focused check"},'
                    '"action":"python -m unittest focused"}',
                    input_tokens=80,
                    output_tokens=15,
                ),
            ]
        )

        def transport(body: bytes) -> TransportResponse:
            captured.append(body)
            return TransportResponse(
                body=next(responses),
                status_code=200,
                headers={"X-Request-ID": f"req_{len(captured)}"},
            )

        persisted: list[dict[str, object]] = []
        original = copy.deepcopy(self.state)
        result = self.host.run_transition(
            self.state,
            "Current check failed",
            transport=transport,
            persist_successor=lambda state: persisted.append(dict(state)),
            step_id="step-7",
            max_attempts=2,
        )

        self.assertEqual(self.state, original)
        self.assertEqual(result.action, "python -m unittest focused")
        self.assertEqual(result.successor_state["next_action"], "run focused check")
        self.assertEqual(len(persisted), 1)
        self.assertEqual(len(captured), 2)
        self.assertEqual(result.attempts[0]["transition_status"], "rejected")
        self.assertEqual(result.attempts[1]["transition_status"], "accepted")
        self.assertEqual(result.attempts[1]["request_id"], "req_2")
        self.assertEqual(result.attempts[1]["input_tokens"], 80)
        self.assertEqual(result.attempts[1]["cached_input_tokens"], 10)
        self.assertEqual(result.attempts[1]["uncached_input_tokens"], 70)
        self.assertTrue(result.attempts[1]["successor_state_sha256"])
        self.assertTrue(result.attempts[1]["action_sha256"])

        first = json.loads(captured[0])
        second = json.loads(captured[1])
        first_input = json.loads(first["input"][0]["content"][0]["text"])
        second_input = json.loads(second["input"][0]["content"][0]["text"])
        self.assertNotIn("validation_error", first_input)
        self.assertIn("validation_error", second_input)
        self.assertEqual(first_input["state"], original)
        self.assertEqual(second_input["state"], original)
        self.assertEqual(first["instructions"], second["instructions"])
        for request in (first, second):
            self.assertEqual(len(request["input"]), 1)
            self.assertNotIn("previous_response_id", request)
            self.assertNotIn("conversation", request)

    def test_native_tool_call_output_is_not_mistaken_for_a_transition(self) -> None:
        payload = json.dumps(
            {
                "id": "resp_tool",
                "status": "completed",
                "output": [
                    {
                        "type": "function_call",
                        "name": "inspect",
                        "arguments": "{}",
                    }
                ],
            },
            separators=(",", ":"),
        ).encode("utf-8")
        persist_calls = 0

        def persist(_: object) -> None:
            nonlocal persist_calls
            persist_calls += 1

        with self.assertRaises(TransitionRetriesExhausted) as raised:
            self.host.run_transition(
                self.state,
                "Current observation",
                transport=lambda _: payload,
                persist_successor=persist,
                max_attempts=1,
            )
        self.assertEqual(persist_calls, 0)
        self.assertEqual(raised.exception.attempts[0]["transition_status"], "rejected")

    def test_retries_exhaust_without_persisting_or_releasing_action(self) -> None:
        persist_calls = 0

        def persist(_: object) -> None:
            nonlocal persist_calls
            persist_calls += 1

        def transport(_: bytes) -> bytes:
            return _response('{"state_patch":{"objective":"changed"},"action":"must-not-release"}')

        with self.assertRaises(TransitionRetriesExhausted) as raised:
            self.host.run_transition(
                self.state,
                "Current observation",
                transport=transport,
                persist_successor=persist,
                max_attempts=2,
            )
        self.assertEqual(persist_calls, 0)
        self.assertEqual(len(raised.exception.attempts), 2)
        self.assertTrue(all(row["transition_status"] == "rejected" for row in raised.exception.attempts))

    def test_persistence_failure_blocks_action_release(self) -> None:
        def transport(_: bytes) -> bytes:
            return _response('{"state_patch":{"next_action":"inspect"},"action":"inspect-now"}')

        def fail_persist(_: object) -> None:
            raise OSError("disk unavailable")

        with self.assertRaisesRegex(StatePersistenceError, "action proposal was not released"):
            self.host.run_transition(
                self.state,
                "Current observation",
                transport=transport,
                persist_successor=fail_persist,
                max_attempts=1,
            )

    def test_wire_budget_is_enforced_on_the_final_serialized_body(self) -> None:
        limits = HistoryFreeLimits(max_wire_request_bytes=128)
        host = HistoryFreeHost(model="gpt-test", procedure="Take one step.", limits=limits)
        with self.assertRaisesRegex(HostBoundaryError, "wire request exceeds 128 bytes"):
            host.prepare_request(self.state, "Current observation")

    def test_direct_script_cli_resolves_the_runtime_package(self) -> None:
        root = Path(__file__).resolve().parents[1]
        completed = subprocess.run(
            [sys.executable, str(root / "runtime" / "skill_state_host.py"), "--help"],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("build", completed.stdout)
        self.assertIn("audit", completed.stdout)

    def test_cli_builds_and_reaudits_the_same_request(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            procedure = root / "procedure.txt"
            state = root / "state.json"
            observation = root / "observation.txt"
            request = root / "request.json"
            first_audit = root / "first-audit.json"
            second_audit = root / "second-audit.json"
            manifest = root / "manifest.json"
            procedure.write_text("Take one bounded step.", encoding="utf-8")
            state.write_text(json.dumps(self.state), encoding="utf-8")
            observation.write_text("Current observation", encoding="utf-8")

            result = main(
                [
                    "build",
                    "--model",
                    "gpt-test",
                    "--procedure",
                    str(procedure),
                    "--state",
                    str(state),
                    "--observation",
                    str(observation),
                    "--request-output",
                    str(request),
                    "--audit-output",
                    str(first_audit),
                    "--manifest-output",
                    str(manifest),
                ]
            )
            self.assertEqual(result, 0)
            self.assertEqual(
                main(
                    [
                        "audit",
                        str(request),
                        "--manifest",
                        str(manifest),
                        "--output",
                        str(second_audit),
                    ]
                ),
                0,
            )
            first = json.loads(first_audit.read_text(encoding="utf-8"))
            second = json.loads(second_audit.read_text(encoding="utf-8"))
            self.assertEqual(first["request_sha256"], second["request_sha256"])
            self.assertTrue(second["manifest_match"])
            self.assertTrue(json.loads(manifest.read_text(encoding="utf-8"))["manifest_sha256"])


if __name__ == "__main__":
    unittest.main()

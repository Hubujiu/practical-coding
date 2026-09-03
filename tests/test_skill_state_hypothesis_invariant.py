from __future__ import annotations

import copy
import unittest

from runtime.skill_state import (
    StateValidationError,
    apply_state_patch,
    apply_transition,
    initial_state,
    validate_state,
)


class SkillStateHypothesisInvariantTests(unittest.TestCase):
    def test_active_and_rejected_hypothesis_ids_must_be_disjoint(self) -> None:
        state = initial_state("diagnose failure", ["retain one current classification"])
        state["hypotheses"]["active"]["h-cache"] = "cache may be stale"
        state["hypotheses"]["rejected"]["h-cache"] = "cache-disabled run reproduced"

        with self.assertRaisesRegex(
            StateValidationError,
            r"active and state\.hypotheses\.rejected overlap: \['h-cache'\]",
        ):
            validate_state(state)

    def test_merge_patch_requires_an_atomic_move_to_rejected(self) -> None:
        state = initial_state("diagnose failure", ["reject disproved causes"])
        state = apply_state_patch(
            state,
            {"hypotheses": {"active": {"h-cache": "cache may be stale"}}},
        )
        before = copy.deepcopy(state)

        with self.assertRaisesRegex(StateValidationError, "overlap"):
            apply_state_patch(
                state,
                {
                    "hypotheses": {
                        "rejected": {"h-cache": "cache-disabled run reproduced"}
                    }
                },
            )
        self.assertEqual(state, before)

        moved = apply_state_patch(
            state,
            {
                "hypotheses": {
                    "active": {"h-cache": None},
                    "rejected": {"h-cache": "cache-disabled run reproduced"},
                }
            },
        )
        self.assertNotIn("h-cache", moved["hypotheses"]["active"])
        self.assertIn("h-cache", moved["hypotheses"]["rejected"])

    def test_rejected_transition_does_not_release_its_action(self) -> None:
        state = initial_state("diagnose failure", ["invalid successor fails closed"])
        state = apply_state_patch(
            state,
            {"hypotheses": {"active": {"h-cache": "cache may be stale"}}},
        )
        before = copy.deepcopy(state)

        with self.assertRaisesRegex(StateValidationError, "overlap"):
            apply_transition(
                state,
                {
                    "state_patch": {
                        "hypotheses": {
                            "rejected": {
                                "h-cache": "cache-disabled run reproduced"
                            }
                        }
                    },
                    "action": "continue with a contradictory state",
                },
            )
        self.assertEqual(state, before)


if __name__ == "__main__":
    unittest.main()

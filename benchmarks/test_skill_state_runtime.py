from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from benchmarks import skill_state_validation as contract
from runtime.skill_state import (
    AUTOMATIC_CHILDREN,
    MAX_STATE_BYTES,
    StateValidationError,
    apply_host_patch,
    apply_state_patch,
    apply_transition,
    build_prompt,
    initial_state,
    validate_state,
)


class SkillStateRuntimeTests(unittest.TestCase):
    def test_initial_state_rejects_one_string_as_success_sequence(self) -> None:
        with self.assertRaises(StateValidationError):
            initial_state("repair branch", "focused check passes")

    def test_nested_merge_preserves_omitted_siblings_and_null_deletes(self) -> None:
        state = initial_state("repair branch", ["focused check passes"])
        state = apply_state_patch(
            state,
            {
                "facts": {"branch": {"name": "feature", "head": "old", "base": "main"}},
                "hypotheses": {"active": {"stale": "cache", "source": "parser"}},
            },
        )
        successor = apply_state_patch(
            state,
            {
                "facts": {"branch": {"head": "new"}},
                "hypotheses": {"active": {"stale": None}},
            },
        )
        self.assertEqual(successor["facts"]["branch"], {"name": "feature", "head": "new", "base": "main"})
        self.assertNotIn("stale", successor["hypotheses"]["active"])
        self.assertEqual(successor["hypotheses"]["active"]["source"], "parser")

    def test_invalid_patch_does_not_mutate_canonical_state(self) -> None:
        state = initial_state("keep canonical state", ["invalid output rolls back"])
        before = copy.deepcopy(state)
        with self.assertRaises(StateValidationError):
            apply_state_patch(state, {"route": {"retrieval": "UNBOUNDED"}})
        self.assertEqual(state, before)

    def test_transcript_and_reasoning_cannot_enter_state(self) -> None:
        state = initial_state("avoid narrative memory", ["state remains operational"])
        for key in ("transcript", "reasoning", "chain_of_thought", "tool_output"):
            with self.subTest(key=key), self.assertRaises(StateValidationError):
                apply_state_patch(state, {"facts": {key: "large text"}})

    def test_execution_state_and_manual_modes_cannot_enter_automatic_path(self) -> None:
        state = initial_state("preserve route boundary", ["path remains automatic"])
        for node in ("execution_state", "decision", "clarification"):
            with self.subTest(node=node), self.assertRaises(StateValidationError):
                apply_host_patch(state, {"route": {"automatic_path": ["core", node]}})

    def test_route_path_requires_canonical_lowercase_names(self) -> None:
        state = initial_state("preserve canonical state", ["path is normalized"])
        with self.assertRaises(StateValidationError):
            apply_host_patch(state, {"route": {"automatic_path": ["Core", "Debugging"]}})

    def test_unknown_and_cross_sibling_paths_are_rejected(self) -> None:
        state = initial_state("preserve topology", ["path follows parent-child edges"])
        for path in (["core", "unknown"], ["core", "debugging", "implementation"]):
            with self.subTest(path=path), self.assertRaises(StateValidationError):
                apply_host_patch(state, {"route": {"automatic_path": path}})

    def test_current_leaf_paths_are_valid(self) -> None:
        state = initial_state("follow current topology", ["known paths validate"])
        for leaf in ("debugging", "implementation"):
            with self.subTest(leaf=leaf):
                successor = apply_host_patch(state, {"route": {"automatic_path": ["core", leaf]}})
                self.assertEqual(successor["route"]["automatic_path"], ["core", leaf])

    def test_model_patch_cannot_change_host_owned_task_or_route_fields(self) -> None:
        state = initial_state("keep task stable", ["control fields stay host-owned"])
        for patch in (
            {"objective": "different task"},
            {"success": ["different gate"]},
            {"route": {"automatic_path": ["core", "debugging"]}},
            {"schema_version": 1},
        ):
            with self.subTest(patch=patch), self.assertRaises(StateValidationError):
                apply_state_patch(state, patch)

    def test_manual_mode_cannot_coexist_with_automatic_child_path(self) -> None:
        state = initial_state("preserve manual isolation", ["manual stays outside tree"])
        with self.assertRaises(StateValidationError):
            apply_host_patch(
                state,
                {"route": {"automatic_path": ["core", "implementation"], "manual": "decision"}},
            )
        successor = apply_host_patch(
            state,
            {"route": {"automatic_path": ["core"], "manual": "decision"}},
        )
        self.assertEqual(successor["route"]["manual"], "decision")

    def test_transition_requires_exact_runtime_shape(self) -> None:
        state = initial_state("advance", ["one action selected"])
        successor, action = apply_transition(
            state,
            {
                "state_patch": {"next_action": "run focused test"},
                "action": "python -m unittest focused",
            },
        )
        self.assertEqual(successor["next_action"], "run focused test")
        self.assertEqual(action, "python -m unittest focused")
        with self.assertRaises(StateValidationError):
            apply_transition(state, {"state_patch": {}, "action": "test", "reasoning": "persist me"})

    def test_prompt_contains_only_procedure_state_and_latest_observation(self) -> None:
        state = initial_state("inspect current failure", ["cause is evidenced"])
        prompt = build_prompt("Use the smallest evidenced fix.", state, "Latest check failed at parser.py:9")
        self.assertIn("Procedure (immutable)", prompt)
        self.assertIn("Skill Execution State", prompt)
        self.assertIn("Latest check failed", prompt)
        self.assertNotIn("Previous Observation", prompt)
        self.assertNotIn("History:", prompt)

    def test_state_budget_is_enforced(self) -> None:
        state = initial_state("bounded", ["state remains below budget"])
        with self.assertRaises(StateValidationError):
            apply_state_patch(state, {"facts": {"oversized": "x" * (MAX_STATE_BYTES + 1)}})
        validate_state(state)
        self.assertLess(len(json.dumps(state).encode("utf-8")), MAX_STATE_BYTES)

    def test_history_target_uses_bounded_artifact_references(self) -> None:
        state = initial_state("audit release", ["provenance remains available"])
        successor = apply_state_patch(
            state,
            {"history": {"required": True, "artifacts": ["artifacts/release-audit.jsonl#event-18"]}},
        )
        self.assertTrue(successor["history"]["required"])
        self.assertEqual(len(successor["history"]["artifacts"]), 1)


class SkillStateTopologyIsolationTests(unittest.TestCase):
    def test_execution_state_is_not_a_router_or_manual_mode(self) -> None:
        topology = json.loads((Path(__file__).resolve().parent / "tree_topology.json").read_text(encoding="utf-8"))
        self.assertNotIn("execution_state", topology["automatic_nodes"])
        self.assertNotIn("execution_state", topology["manual_modes"])
        substrate = topology["runtime_substrates"]["execution_state"]
        self.assertFalse(substrate["automatic_node"])
        self.assertFalse(substrate["manual_mode"])
        self.assertEqual(substrate["activation"], "state-pressure")

    def test_runtime_path_validator_matches_topology_manifest(self) -> None:
        topology = json.loads((Path(__file__).resolve().parent / "tree_topology.json").read_text(encoding="utf-8"))
        manifest_children = {
            node: frozenset(spec["children"])
            for node, spec in topology["automatic_nodes"].items()
        }
        self.assertEqual(AUTOMATIC_CHILDREN, manifest_children)


class SkillStateContractTests(unittest.TestCase):
    def test_deterministic_contract(self) -> None:
        report = contract.run_contract()
        self.assertEqual(report["contract_gate"], "PASS")
        self.assertTrue(all(report["checks"].values()))


if __name__ == "__main__":
    unittest.main()

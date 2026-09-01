from __future__ import annotations

import unittest
from pathlib import Path

from benchmarks import tree_analysis as analysis
from benchmarks import tree_skilluse_analysis as skilluse
from benchmarks import tree_validation as validation


HERE = Path(__file__).resolve().parent


class TreeTopologyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.topology = validation.load_topology(HERE / "tree_topology.json")

    def test_seed_paths_are_parent_local(self) -> None:
        self.assertEqual(validation.node_path(self.topology, "core"), ["core"])
        self.assertEqual(validation.node_path(self.topology, "debugging"), ["core", "debugging"])
        self.assertEqual(validation.node_path(self.topology, "implementation"), ["core", "implementation"])

    def test_staged_descendants_are_parent_local(self) -> None:
        self.assertEqual(
            validation.node_path(self.topology, "dynamic-evidence"),
            ["core", "debugging", "dynamic-evidence"],
        )
        self.assertEqual(
            validation.node_path(self.topology, "security-boundary"),
            ["core", "implementation", "security-boundary"],
        )
        self.assertEqual(
            validation.node_path(self.topology, "migration-compatibility"),
            ["core", "implementation", "migration-compatibility"],
        )
        self.assertEqual(
            validation.node_path(self.topology, "state-concurrency"),
            ["core", "implementation", "state-concurrency"],
        )

    def test_cross_sibling_path_is_invalid(self) -> None:
        self.assertFalse(validation.validate_automatic_path(self.topology, ["core", "debugging", "implementation"]))
        self.assertFalse(
            validation.validate_automatic_path(
                self.topology,
                ["core", "implementation", "security-boundary", "state-concurrency"],
            )
        )

    def test_manual_mode_is_not_an_automatic_node(self) -> None:
        self.assertNotIn("decision", self.topology["automatic_nodes"])
        self.assertIn("decision", self.topology["manual_modes"])
        trace = validation.parse_trace(
            "TREE_TRACE path=core retrieval=NONE manual=decision refs=references/manual/decision.md"
        )
        self.assertTrue(validation.validate_trace(self.topology, trace))
        self.assertEqual(trace["path"], ["core"])


class MinimumSufficientTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.topology = validation.load_topology(HERE / "tree_topology.json")

    def test_root_dominates_passing_descendants(self) -> None:
        result = analysis.minimum_sufficient_set(
            self.topology,
            {
                "core": True,
                "debugging": True,
                "dynamic-evidence": True,
                "implementation": True,
                "security-boundary": True,
                "migration-compatibility": True,
                "state-concurrency": True,
            },
        )
        self.assertEqual(result, {"core"})

    def test_multiple_sibling_minima_are_allowed(self) -> None:
        result = analysis.minimum_sufficient_set(
            self.topology,
            {
                "core": False,
                "debugging": True,
                "dynamic-evidence": True,
                "implementation": True,
                "security-boundary": True,
                "migration-compatibility": True,
                "state-concurrency": True,
            },
        )
        self.assertEqual(result, {"debugging", "implementation"})

    def test_depth_two_minimum_is_derived_when_parent_fails(self) -> None:
        result = analysis.minimum_sufficient_set(
            self.topology,
            {
                "core": False,
                "debugging": False,
                "dynamic-evidence": True,
                "implementation": False,
                "security-boundary": False,
                "migration-compatibility": False,
                "state-concurrency": False,
            },
        )
        self.assertEqual(result, {"dynamic-evidence"})

    def test_no_passing_capability_is_quality_gap(self) -> None:
        result = analysis.minimum_sufficient_set(
            self.topology,
            {
                "core": False,
                "debugging": False,
                "dynamic-evidence": False,
                "implementation": False,
                "security-boundary": False,
                "migration-compatibility": False,
                "state-concurrency": False,
            },
        )
        self.assertEqual(result, set())
        self.assertEqual(
            analysis.relation_to_minimum(self.topology, "core", result, False),
            "quality_gap",
        )

    def test_over_and_under_disclosure_are_topology_diagnostics(self) -> None:
        self.assertEqual(
            analysis.relation_to_minimum(self.topology, "debugging", {"core"}, True),
            "over_disclosure",
        )
        self.assertEqual(
            analysis.relation_to_minimum(self.topology, "core", {"debugging"}, False),
            "under_disclosure",
        )


class SkillUseMetricTests(unittest.TestCase):
    def test_skilluse_self_test(self) -> None:
        skilluse.self_test()


class ManualContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.topology = validation.load_topology(HERE / "tree_topology.json")

    def test_automatic_trace_with_manual_reference_is_detectable(self) -> None:
        trace = validation.parse_trace(
            "TREE_TRACE path=core>implementation retrieval=STRUCTURAL manual=decision refs=references/manual/decision.md,references/implementation.md"
        )
        self.assertTrue(validation.validate_trace(self.topology, trace))
        self.assertEqual(trace["manual"], "decision")
        self.assertIn("references/manual/decision.md", trace["references_loaded"])

    def test_explicit_manual_trace_remains_outside_path(self) -> None:
        trace = validation.parse_trace(
            "TREE_TRACE path=core retrieval=BOUNDED manual=decision refs=references/manual/decision.md"
        )
        self.assertEqual(trace["path"], ["core"])
        self.assertEqual(trace["manual"], "decision")
        self.assertTrue(validation.validate_trace(self.topology, trace))


if __name__ == "__main__":
    unittest.main()

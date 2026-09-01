from __future__ import annotations

import unittest
from pathlib import Path

from benchmarks import tree_analysis as analysis
from benchmarks import tree_cases
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

    def test_explicit_manual_contract_normalizes_windows_reference_path(self) -> None:
        case = next(item for item in tree_cases.CASES if item["task_id"] == "sa-memory-strategy-manual-decision")
        trace = validation.parse_trace(
            r"TREE_TRACE path=core retrieval=TARGETED manual=decision refs=D:\repo\references\manual\decision.md"
        )
        result = validation.score_answer(
            case,
            (
                "Recommendation: use SummaryCompressionMemoryChatService instead of "
                "SlidingWindowMemoryChatService. Strongest trade-off: lossy recall."
            ),
            [],
            HERE.parent,
            trace=trace,
            enforce_runtime_contract=True,
        )
        self.assertTrue(result["manual_contract_ok"])

    def test_non_manual_windows_reference_does_not_satisfy_manual_contract(self) -> None:
        case = next(item for item in tree_cases.CASES if item["task_id"] == "sa-memory-strategy-manual-decision")
        trace = validation.parse_trace(
            r"TREE_TRACE path=core retrieval=TARGETED manual=decision refs=D:\repo\references\implementation.md"
        )
        result = validation.score_answer(
            case,
            (
                "Recommendation: use SummaryCompressionMemoryChatService instead of "
                "SlidingWindowMemoryChatService. Strongest trade-off: lossy recall."
            ),
            [],
            HERE.parent,
            trace=trace,
            enforce_runtime_contract=True,
        )
        self.assertFalse(result["manual_contract_ok"])

    def test_manual_tradeoff_evidence_does_not_require_colon_formatting(self) -> None:
        case = next(item for item in tree_cases.CASES if item["task_id"] == "sa-memory-strategy-manual-decision")
        trace = validation.parse_trace(
            "TREE_TRACE path=core retrieval=TARGETED manual=decision refs=references/manual/decision.md"
        )
        result = validation.score_answer(
            case,
            (
                "Recommendation: use SummaryCompressionMemoryChatService instead of "
                "SlidingWindowMemoryChatService for summary-compression. "
                "Its strongest trade-off is lossy recall."
            ),
            [],
            HERE.parent,
            trace=trace,
            enforce_runtime_contract=True,
        )
        self.assertEqual(result["missing_evidence_groups"], [])
        self.assertTrue(result["manual_contract_ok"])

    def test_manual_evidence_accepts_equivalent_chinese_labels(self) -> None:
        case = next(item for item in tree_cases.CASES if item["task_id"] == "sa-memory-strategy-manual-decision")
        trace = validation.parse_trace(
            "TREE_TRACE path=core retrieval=TARGETED manual=decision refs=references/manual/decision.md"
        )
        result = validation.score_answer(
            case,
            (
                "推荐：使用 SummaryCompressionMemoryChatService，而不是 SlidingWindowMemoryChatService。"
                "summary-compression 的最强权衡是额外模型调用和细节损失。"
            ),
            [],
            HERE.parent,
            trace=trace,
            enforce_runtime_contract=True,
        )
        self.assertEqual(result["missing_evidence_groups"], [])
        self.assertTrue(result["manual_contract_ok"])

    def test_manual_evidence_still_requires_a_tradeoff(self) -> None:
        case = next(item for item in tree_cases.CASES if item["task_id"] == "sa-memory-strategy-manual-decision")
        trace = validation.parse_trace(
            "TREE_TRACE path=core retrieval=TARGETED manual=decision refs=references/manual/decision.md"
        )
        result = validation.score_answer(
            case,
            "推荐：使用 SummaryCompressionMemoryChatService，而不是 SlidingWindowMemoryChatService。",
            [],
            HERE.parent,
            trace=trace,
            enforce_runtime_contract=True,
        )
        self.assertIn(["trade-off", "tradeoff", "权衡", "代价"], result["missing_evidence_groups"])


class EvidenceOracleTests(unittest.TestCase):
    def test_cancel_diagnosis_accepts_existing_cancellation_test(self) -> None:
        case = next(item for item in tree_cases.CASES if item["task_id"] == "ca-cancel-download")
        result = validation.score_answer(
            case,
            (
                "EditorShell passes an AbortController signal into exportCover. "
                "The existing avifEncoder.test.ts covers cancellation, while the cheapest falsifying test "
                "should probe before link.click and prove the download side effect is suppressed."
            ),
            [],
            HERE.parent,
            trace=None,
            enforce_runtime_contract=False,
        )
        self.assertEqual(result["missing_evidence_groups"], [])

    def test_cancel_diagnosis_accepts_semantic_operation_and_test_evidence(self) -> None:
        case = next(item for item in tree_cases.CASES if item["task_id"] == "ca-cancel-download")
        result = validation.score_answer(
            case,
            (
                "EditorShell calls abort() while exportCover can still reach link.click. "
                "Existing tests cover stalled-worker cancellation; add one falsifying test at the download probe."
            ),
            [],
            HERE.parent,
            trace=None,
            enforce_runtime_contract=False,
        )
        self.assertEqual(result["missing_evidence_groups"], [])

    def test_cancel_diagnosis_still_requires_concrete_test_evidence(self) -> None:
        case = next(item for item in tree_cases.CASES if item["task_id"] == "ca-cancel-download")
        result = validation.score_answer(
            case,
            "EditorShell passes an AbortController signal into exportCover; inspect the download boundary.",
            [],
            HERE.parent,
            trace=None,
            enforce_runtime_contract=False,
        )
        self.assertIn(
            ["focused", "suite", "existing test", ".test."],
            result["missing_evidence_groups"],
        )


if __name__ == "__main__":
    unittest.main()

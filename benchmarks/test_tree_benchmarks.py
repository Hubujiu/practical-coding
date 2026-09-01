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

    def test_evidence_rejected_descendants_leave_seed_nodes_as_leaves(self) -> None:
        self.assertEqual(self.topology["automatic_nodes"]["debugging"]["children"], [])
        self.assertEqual(self.topology["automatic_nodes"]["implementation"]["children"], [])

    def test_cross_sibling_path_is_invalid(self) -> None:
        self.assertFalse(validation.validate_automatic_path(self.topology, ["core", "debugging", "implementation"]))
        self.assertFalse(
            validation.validate_automatic_path(
                self.topology,
                ["core", "implementation", "debugging"],
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

    def test_missing_trace_can_be_recovered_from_observed_reference_reads(self) -> None:
        trace = validation.infer_trace_from_commands(
            self.topology,
            [
                r"Get-Content D:\Workspace\AiProjects\practical-coding\references\implementation.md",
                r"Get-Content D:\Workspace\AiProjects\practical-coding\references\manual\decision.md",
            ],
        )
        self.assertEqual(trace["path"], ["core", "implementation"])
        self.assertEqual(trace["manual"], "decision")
        self.assertTrue(validation.validate_trace(self.topology, trace))

    def test_observed_retired_reference_remains_an_invalid_trace(self) -> None:
        trace = validation.infer_trace_from_commands(
            self.topology,
            [
                r"Get-Content D:\Workspace\AiProjects\practical-coding\references\implementation.md",
                r"Get-Content D:\Workspace\AiProjects\practical-coding\references\implementation-state-concurrency.md",
            ],
        )
        self.assertEqual(trace["path"], ["core", "implementation"])
        self.assertFalse(validation.validate_trace(self.topology, trace))


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
                "implementation": True,
            },
        )
        self.assertEqual(result, {"core"})

    def test_multiple_sibling_minima_are_allowed(self) -> None:
        result = analysis.minimum_sufficient_set(
            self.topology,
            {
                "core": False,
                "debugging": True,
                "implementation": True,
            },
        )
        self.assertEqual(result, {"debugging", "implementation"})

    def test_leaf_minimum_is_derived_when_root_fails(self) -> None:
        result = analysis.minimum_sufficient_set(
            self.topology,
            {
                "core": False,
                "debugging": True,
                "implementation": False,
            },
        )
        self.assertEqual(result, {"debugging"})

    def test_no_passing_capability_is_quality_gap(self) -> None:
        result = analysis.minimum_sufficient_set(
            self.topology,
            {
                "core": False,
                "debugging": False,
                "implementation": False,
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

    def test_retired_selected_node_is_an_invalid_trace_not_an_analysis_crash(self) -> None:
        self.assertEqual(
            analysis.relation_to_minimum(self.topology, "state-concurrency", {"core"}, False),
            "invalid_trace",
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

    def test_manual_contract_accepts_root_elided_identity(self) -> None:
        case = next(item for item in tree_cases.CASES if item["task_id"] == "sa-memory-strategy-manual-decision")
        trace = validation.parse_trace(
            "TREE_TRACE path=core retrieval=TARGETED manual=decision refs=manual/decision.md"
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

    def test_manual_contract_accepts_observed_reference_read(self) -> None:
        case = next(item for item in tree_cases.CASES if item["task_id"] == "sa-memory-strategy-manual-decision")
        trace = validation.parse_trace(
            "TREE_TRACE path=core retrieval=TARGETED manual=decision refs=none"
        )
        result = validation.score_answer(
            case,
            (
                "Recommendation: use SummaryCompressionMemoryChatService instead of "
                "SlidingWindowMemoryChatService. Strongest trade-off: lossy recall."
            ),
            [r"Get-Content D:\repo\references\manual\decision.md"],
            HERE.parent,
            trace=trace,
            enforce_runtime_contract=True,
        )
        self.assertTrue(result["manual_contract_ok"])

    def test_automatic_task_detects_observed_manual_reference_read(self) -> None:
        case = next(item for item in tree_cases.CASES if item["task_id"] == "pp-known-contract")
        trace = validation.parse_trace(
            "TREE_TRACE path=core retrieval=TARGETED manual=none refs=none"
        )
        result = validation.score_answer(
            case,
            "PluginDescriptor status version lifecycle",
            [r"Get-Content D:\repo\references\manual\decision.md"],
            HERE.parent,
            trace=trace,
            enforce_runtime_contract=True,
        )
        self.assertTrue(result["spontaneous_manual_mode"])
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

    def test_manual_evidence_accepts_decision_and_cost_wording(self) -> None:
        case = next(item for item in tree_cases.CASES if item["task_id"] == "sa-memory-strategy-manual-decision")
        trace = validation.parse_trace(
            "TREE_TRACE path=core retrieval=TARGETED manual=decision refs=references/manual/decision.md"
        )
        result = validation.score_answer(
            case,
            (
                "Decision: choose SummaryCompressionMemoryChatService instead of "
                "SlidingWindowMemoryChatService for summary-compression. "
                "Its strongest cost is lossy recall."
            ),
            [],
            HERE.parent,
            trace=trace,
            enforce_runtime_contract=True,
        )
        self.assertEqual(result["missing_evidence_groups"], [])
        self.assertTrue(result["manual_contract_ok"])

    def test_manual_evidence_accepts_recommend_as_a_verb(self) -> None:
        case = next(item for item in tree_cases.CASES if item["task_id"] == "sa-memory-strategy-manual-decision")
        trace = validation.parse_trace(
            "TREE_TRACE path=core retrieval=TARGETED manual=decision refs=references/manual/decision.md"
        )
        result = validation.score_answer(
            case,
            (
                "Recommend SummaryCompressionMemoryChatService over SlidingWindowMemoryChatService. "
                "The summary-compression trade-off is lossy recall."
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
        self.assertIn(["trade-off", "tradeoff", "cost", "权衡", "代价"], result["missing_evidence_groups"])


class EvidenceOracleTests(unittest.TestCase):
    def test_executor_diagnosis_accepts_a_concrete_focused_test_method(self) -> None:
        case = next(item for item in tree_cases.CASES if item["task_id"] == "pp-running-after-throw")
        result = validation.score_answer(
            case,
            (
                "DefaultPluginOperationExecutor runCommand leaves RUNNING after an Error. "
                "Strengthen errorIsNotSwallowedAsOperationFailure to assert the record reaches a failed terminal state."
            ),
            [],
            HERE.parent,
            trace=None,
            enforce_runtime_contract=False,
        )
        self.assertEqual(result["missing_evidence_groups"], [])

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

    def test_cancel_diagnosis_accepts_authoritative_boundary_without_ui_caller(self) -> None:
        case = next(item for item in tree_cases.CASES if item["task_id"] == "ca-cancel-download")
        result = validation.score_answer(
            case,
            (
                "exportCover has no signal.aborted check before link.click. "
                "The focused avifEncoder.test.ts covers abort; add one falsifying test at that probe."
            ),
            [],
            HERE.parent,
            trace=None,
            enforce_runtime_contract=False,
        )
        self.assertEqual(result["missing_evidence_groups"], [])

    def test_focused_probe_accepts_an_explicit_blocked_outcome(self) -> None:
        case = next(item for item in tree_cases.CASES if item["task_id"] == "ca-export-filename-probe")
        result = validation.score_answer(
            case,
            (
                "Ran npx vitest run src/lib/exportFilename.test.ts once. "
                "Outcome: blocked before collection because a required plugin could not be resolved."
            ),
            ["npx vitest run src/lib/exportFilename.test.ts"],
            HERE.parent,
            trace=None,
            enforce_runtime_contract=False,
        )
        self.assertEqual(result["missing_evidence_groups"], [])

    def test_focused_probe_accepts_an_explicit_outcome_field(self) -> None:
        case = next(item for item in tree_cases.CASES if item["task_id"] == "ca-export-filename-probe")
        result = validation.score_answer(
            case,
            (
                "Ran npm test -- src/lib/exportFilename.test.ts once. "
                "Outcome: Vitest did not start because dependencies are absent."
            ),
            ["npm test -- src/lib/exportFilename.test.ts"],
            HERE.parent,
            trace=None,
            enforce_runtime_contract=False,
        )
        self.assertEqual(result["missing_evidence_groups"], [])

    def test_cancel_diagnosis_still_requires_concrete_test_evidence(self) -> None:
        case = next(item for item in tree_cases.CASES if item["task_id"] == "ca-cancel-download")
        result = validation.score_answer(
            case,
            "An AbortController signal reaches exportCover; inspect the download boundary.",
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

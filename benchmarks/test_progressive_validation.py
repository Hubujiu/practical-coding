import tempfile
import unittest
from pathlib import Path

from benchmarks import progressive_validation as progressive
from benchmarks.progressive_cases import CASES


class ProgressiveValidationTests(unittest.TestCase):
    def test_catalog_has_required_real_task_coverage(self):
        self.assertGreaterEqual(len(CASES), 20)
        self.assertEqual(
            {case["expected_reasoning"] for case in CASES},
            {"NONE", "DEBUGGING", "IMPLEMENTATION"},
        )
        self.assertEqual(
            {case["expected_retrieval_mode"] for case in CASES},
            {"TARGETED", "BOUNDED", "STRUCTURAL"},
        )

    def test_trace_parser_uses_last_machine_line(self):
        trace = progressive.parse_trace(
            "report\nBENCHMARK_TRACE reasoning=NONE retrieval=TARGETED refs=none\n"
            "BENCHMARK_TRACE reasoning=DEBUGGING retrieval=BOUNDED refs=references/debugging.md"
        )
        self.assertEqual(trace["reasoning"], "DEBUGGING")
        self.assertEqual(trace["retrieval"], "BOUNDED")
        self.assertEqual(trace["references_loaded"], ["references/debugging.md"])
        self.assertTrue(progressive.validate_trace(trace))

    def test_trace_rejects_removed_numeric_depth_contract(self):
        trace = progressive.parse_trace(
            "BENCHMARK_TRACE execution=E3 retrieval=R2 path=engineering>security refs=references/engineering.md"
        )
        self.assertFalse(progressive.validate_trace(trace))

    def test_score_requires_evidence_probe_and_clean_workspace(self):
        case = {
            "required": [["alpha"], ["beta", "bravo"]],
            "probe_terms": ["pytest", "focused"],
        }
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "seed.txt").write_text("seed\n", encoding="utf-8")
            progressive.bench.snapshot_workspace(root)
            score = progressive.score_answer(case, "alpha and bravo", ["pytest focused"], root)
        self.assertTrue(score["passed"])

    def test_all_is_heldout_only_for_active_runtime(self):
        specs = progressive.build_specs(["all"], 1, current_only=True)
        self.assertEqual(len(specs), len(CASES))
        self.assertEqual({spec[0] for spec in specs}, {"heldout"})
        self.assertEqual({spec[2] for spec in specs}, {"adaptive"})

    def test_comparison_arms_remain_available_but_are_not_default_current_only(self):
        specs = progressive.build_specs(["heldout"], 1, current_only=False)
        self.assertEqual(len(specs), len(CASES) * 3)
        self.assertEqual({spec[2] for spec in specs}, {"no-skill", "previous", "adaptive"})


if __name__ == "__main__":
    unittest.main()

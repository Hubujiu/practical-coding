import tempfile
import unittest
from pathlib import Path

from benchmarks import progressive_validation as progressive
from benchmarks.progressive_cases import ABLATION_IDS, CALIBRATION_IDS, CASES


class ProgressiveValidationTests(unittest.TestCase):
    def test_catalog_has_required_coverage(self):
        self.assertGreaterEqual(len(CASES), 20)
        self.assertEqual({case["expected_execution"] for case in CASES}, set(progressive.EXECUTION_LEVELS))
        self.assertEqual({case["expected_retrieval"] for case in CASES}, set(progressive.RETRIEVAL_LEVELS))
        self.assertEqual(
            {case["capability_path"][-1] for case in CASES if len(case["capability_path"]) == 2},
            {"security", "state", "compatibility", "performance", "quality", "interface"},
        )
        self.assertGreaterEqual(len(CALIBRATION_IDS), 8)
        self.assertGreaterEqual(len(ABLATION_IDS), 6)

    def test_caps_exclude_later_depth_headings(self):
        e0 = progressive.capped_bundle("execution", "E0")
        e2 = progressive.capped_bundle("execution", "E2")
        r1 = progressive.capped_bundle("retrieval", "R1")
        self.assertNotIn("### E1 — Probe", e0)
        self.assertNotIn("### E3 — Specialist leaf", e2)
        self.assertNotIn("### R2 — Specialized retrieval", r1)
        self.assertIn("references/debugging.md", e2)

    def test_parent_leaf_ablation_has_no_conflicting_e2_cap(self):
        case = next(case for case in CASES if case["task_id"] == "pp-admin-token-security")
        bundle = progressive.ablation_bundle("parent-leaf", case)
        self.assertIn("references/specialists/security.md", bundle)
        self.assertNotIn('<benchmark-cap axis="execution" level="E2">', bundle)

    def test_trace_parser_uses_last_machine_line(self):
        trace = progressive.parse_trace(
            "report\nBENCHMARK_TRACE execution=E0 retrieval=R1 path=none refs=none\n"
            "BENCHMARK_TRACE execution=E3 retrieval=R2 path=<engineering>security> refs=<references/engineering.md,references/specialists/security.md>"
        )
        self.assertEqual(trace["execution"], "E3")
        self.assertEqual(trace["retrieval"], "R2")
        self.assertEqual(trace["capability_path"], ["engineering", "security"])
        self.assertEqual(len(trace["references_loaded"]), 2)
        self.assertTrue(progressive.validate_trace(trace))

    def test_trace_rejects_leaf_path_below_e3(self):
        trace = progressive.parse_trace(
            "BENCHMARK_TRACE execution=E0 retrieval=R2 path=engineering>security refs=references/engineering.md"
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

    def test_full_spec_count_is_frozen(self):
        specs = progressive.build_specs(["all"], 3)
        expected = len(CASES) * 3 * 3 + len(CALIBRATION_IDS) * 2 * 5 * 3 + len(ABLATION_IDS) * 3 * 3
        self.assertEqual(len(specs), expected)

    def test_current_only_omits_external_comparison_arms(self):
        specs = progressive.build_specs(["all"], 3, current_only=True)
        heldout = [spec for spec in specs if spec[0] == "heldout"]
        self.assertEqual(len(heldout), len(CASES) * 3)
        self.assertEqual({spec[2] for spec in heldout}, {"adaptive"})


if __name__ == "__main__":
    unittest.main()

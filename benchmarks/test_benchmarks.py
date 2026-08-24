import tempfile
import unittest
from pathlib import Path

from benchmarks import run_benchmarks as bench


class BenchmarkHarnessTests(unittest.TestCase):
    def test_decision_labels_override_question_marks_inside_one_item(self):
        answer = "❓ **Q1 — Boundary**: Must it deploy alone? Conversely, can one team own it?\n\n➡️ **Recommendation:** Keep it together because separation adds complexity."
        metrics = bench.decision_metrics(answer)
        self.assertEqual(metrics["questions"], 1)
        self.assertEqual(metrics["recommendations"], 1)
        self.assertTrue(metrics["has_tradeoff"])

    def test_recommendation_marker_is_counted_once_per_line(self):
        answer = "➡️ Recommendation: choose the monolith."
        self.assertEqual(bench.decision_metrics(answer)["recommendations"], 1)

    def test_comparison_delta_is_practical_minus_competitor(self):
        summary = [
            {"suite": "debug", "case": "x", "arm": "practical-current", "pass_rate": 1.0, "total_loc_median": 8},
            {"suite": "debug", "case": "x", "arm": "superpowers", "pass_rate": 0.5, "total_loc_median": 12},
        ]
        delta = bench.comparisons(summary)[0]
        self.assertEqual(delta["pass_rate_delta"], 0.5)
        self.assertEqual(delta["total_loc_median_delta"], -4)

    def test_codex_command_fixes_luna_and_reasoning(self):
        with tempfile.TemporaryDirectory() as tmp:
            command = bench.codex_command("codex", Path(tmp))
        self.assertIn(bench.MODEL, command)
        self.assertIn(f"model_reasoning_effort={bench.REASONING}", command)

    def test_router_matrix_covers_every_route(self):
        self.assertEqual(
            {expected for expected, _ in bench.ROUTER_CASES.values()},
            {"DIRECT", "DECISION", "DEBUGGING", "IMPLEMENTATION", "EXPLORATION", "VERIFICATION"},
        )

    def test_decision_suite_inlines_decision_module(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "SKILL.md").write_text("# skill\n", encoding="utf-8")
            (root / "references").mkdir()
            (root / "references" / "decision.md").write_text("# Decision module\n", encoding="utf-8")
            original_root = bench.ROOT
            bench.ROOT = root
            try:
                router = bench.skill_text("practical-current", {}, None, suite="router")
                decision = bench.skill_text("practical-current", {}, None, suite="decision")
            finally:
                bench.ROOT = original_root
        self.assertNotIn("Decision module", router)
        self.assertIn("Decision module", decision)


if __name__ == "__main__":
    unittest.main()

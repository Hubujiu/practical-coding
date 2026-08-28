import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

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

    def test_scorecard_uses_quality_gate_before_efficiency(self):
        summary = []
        for arm, passed, safe in (("practical-current", 2 / 3, 2 / 3), ("superpowers", 1.0, 1.0)):
            summary.append({
                "suite": "debug", "case": "security", "arm": arm, "n": 3,
                "indeterminate_n": 0, "pass_rate": passed, "correct_rate": passed,
                "safe_rate": safe, "uncached_input_tokens_median": 10 if arm == "practical-current" else 100,
                "output_tokens_median": 10 if arm == "practical-current" else 100,
                "duration_seconds_median": 1 if arm == "practical-current" else 10,
                "tool_calls_median": 1 if arm == "practical-current" else 10,
            })
        rollups = [{**row, "case": "__all__"} for row in summary]
        card = bench.scorecards(summary, rollups)[0]
        self.assertFalse(card["quality_qualified"])
        self.assertEqual(card["status"], "not-qualified")
        self.assertIsNone(card["qualified_utility_index"])
        self.assertGreater(card["cost_efficiency_index"], 1)

    def test_scorecard_accepts_small_pass_gap_when_safety_is_not_worse(self):
        summary = []
        for arm, passed, cost in (("practical-current", 0.98, 50), ("ponytail", 1.0, 100)):
            summary.append({
                "suite": "delivery", "case": "component", "arm": arm, "n": 3,
                "indeterminate_n": 0, "pass_rate": passed, "correct_rate": 1.0,
                "safe_rate": 1.0, "build_rate": 1.0,
                "uncached_input_tokens_median": cost, "output_tokens_median": cost,
                "duration_seconds_median": cost, "tool_calls_median": cost,
            })
        rollups = [{**row, "case": "__all__"} for row in summary]
        card = bench.scorecards(summary, rollups)[0]
        self.assertTrue(card["quality_qualified"])
        self.assertTrue(card["sample_qualified"])
        self.assertEqual(card["status"], "qualified")
        self.assertGreater(card["qualified_utility_index"], 1)

    def test_codex_command_fixes_luna_and_reasoning(self):
        with tempfile.TemporaryDirectory() as tmp:
            command = bench.codex_command("codex", Path(tmp))
        self.assertIn(bench.MODEL, command)
        self.assertIn(f"model_reasoning_effort={bench.REASONING}", command)

    def test_snapshot_workspace_creates_checked_longpath_compatible_baseline(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            (workspace / "seed.txt").write_text("seed\n", encoding="utf-8")
            bench.snapshot_workspace(workspace)
            head = bench.run_command(["git", "rev-parse", "--verify", "HEAD"], workspace)
            longpaths = bench.run_command(["git", "config", "--get", "core.longpaths"], workspace)
        self.assertEqual(head.returncode, 0, head.stderr)
        self.assertEqual(longpaths.stdout.strip(), "true")

    def test_router_matrix_covers_every_route(self):
        self.assertEqual(
            {expected for expected, _ in bench.ROUTER_CASES.values()},
            {"DIRECT", "DECISION", "DEBUGGING", "IMPLEMENTATION", "EXPLORATION"},
        )

    def test_core_routes_new_dependency_to_decision(self):
        skill = (bench.ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("already-installed", skill)
        self.assertIn("route Decision", skill)
        self.assertNotIn("Prefer mature maintained implementations only when integrating", skill)

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

    def test_behavior_score_requires_native_trigger_and_only_expected_module(self):
        commands = [
            "Get-Content C:/eval/skills/practical-coding/SKILL.md",
            "Get-Content C:/eval/skills/practical-coding/references/debugging.md",
        ]
        score = bench.behavior_score(commands, "debugging.md")
        self.assertTrue(score["passed"])
        self.assertEqual(score["module_reads"], ["debugging.md"])

        eager = bench.behavior_score(
            [commands[0], "Get-Content C:/eval/skills/practical-coding/references/debugging.md, C:/eval/skills/practical-coding/references/implementation.md"],
            "debugging.md",
        )
        self.assertFalse(eager["routing_ok"])

        sequential = bench.behavior_score(
            [*commands, "Get-Content C:/eval/skills/practical-coding/references/decision.md"],
            "debugging.md",
        )
        self.assertTrue(sequential["routing_ok"])
        self.assertEqual(sequential["module_sequence"], ["debugging.md", "decision.md"])

    def test_native_behavior_matrix_covers_direct_and_every_module(self):
        self.assertEqual(
            {case["module"] for case in bench.BEHAVIOR_CASES.values()},
            {None, "decision.md", "debugging.md", "implementation.md", "navigation.md"},
        )

    def test_navigation_backend_is_scored_separately_from_module_route(self):
        commands = [
            "Get-Content C:/eval/skills/practical-coding/SKILL.md",
            "Get-Content C:/eval/skills/practical-coding/references/navigation.md",
            "codebase-memory-mcp cli search_graph '{}'",
        ]
        self.assertTrue(bench.behavior_score(commands, "navigation.md", expected_backend="graph")["passed"])
        self.assertFalse(bench.behavior_score(commands[:2], "navigation.md", expected_backend="graph")["backend_ok"])

    def test_behavior_score_uses_loaded_content_not_recursive_filename_listing(self):
        commands = ["Get-ChildItem C:/eval/skills/practical-coding -Recurse; Get-Content $decision"]
        outputs = ["# Practical Coding\nLoaded core\ndecision.md\ndebugging.md\n# Decision\nLoaded body\n"]
        score = bench.behavior_score(commands, "decision.md", outputs)
        self.assertTrue(score["passed"])
        self.assertEqual(score["module_reads"], ["decision.md"])

    def test_behavior_direct_path_rejects_reference_preload(self):
        trigger = ["Get-Content C:/eval/skills/practical-coding/SKILL.md"]
        self.assertTrue(bench.behavior_score(trigger, None)["passed"])
        self.assertFalse(
            bench.behavior_score(
                [*trigger, "Get-Content C:/eval/skills/practical-coding/references/decision.md"],
                None,
            )["passed"]
        )

    def test_native_previous_arm_does_not_inline_skill_text(self):
        self.assertEqual(bench.skill_text("practical-native-previous", {}, Path("previous")), "")

    def test_indeterminate_cells_do_not_reduce_pass_rate(self):
        summary = bench.aggregate(
            [
                {"suite": "behavior", "case": "x", "arm": "practical-native", "verdict": "pass", "passed": True},
                {"suite": "behavior", "case": "x", "arm": "practical-native", "verdict": "indeterminate", "passed": None, "error": "timeout"},
            ]
        )[0]
        self.assertEqual(summary["pass_rate"], 1.0)
        self.assertEqual(summary["indeterminate_n"], 1)

    def test_build_oom_is_infrastructure_not_behavior(self):
        self.assertEqual(
            bench.build_infrastructure_error("FATAL ERROR: Zone Allocation failed - process out of memory"),
            "frontend build exhausted memory",
        )
        self.assertIsNone(bench.build_infrastructure_error("error TS2345: bad argument"))

    def test_frontend_dependencies_are_prepared_before_agent_verification(self):
        with tempfile.TemporaryDirectory() as tmp:
            frontend = Path(tmp) / "frontend"
            frontend.mkdir()
            completed = subprocess.CompletedProcess(["bun", "install"], 0, "installed", "")
            with mock.patch.object(bench.shutil, "which", return_value="bun"), mock.patch.object(
                bench, "run_command", return_value=completed
            ) as run:
                setup = bench.prepare_frontend_dependencies("tmpl-fe-command", Path(tmp), 60)
        self.assertIsNotNone(setup)
        self.assertIn("installed", setup["output_tail"])
        run.assert_called_once_with(["bun", "install", "--frozen-lockfile"], frontend, 60)

    def test_post_build_reuses_prepared_frontend_dependencies(self):
        with tempfile.TemporaryDirectory() as tmp:
            frontend = Path(tmp) / "frontend"
            (frontend / "node_modules").mkdir(parents=True)
            completed = subprocess.CompletedProcess(["bun", "run", "build"], 0, "built", "")
            with mock.patch.object(bench.shutil, "which", return_value="bun"), mock.patch.object(
                bench, "run_command", return_value=completed
            ) as run:
                build = bench.post_build("tmpl-fe-command", Path(tmp), 60)
        self.assertTrue(build["passed"])
        run.assert_called_once_with(["bun", "run", "build"], frontend, 60)


if __name__ == "__main__":
    unittest.main()

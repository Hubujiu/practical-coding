import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from benchmarks.external import skillsbench_adapter as adapter


class SkillsBenchAdapterTests(unittest.TestCase):
    def test_discovers_versioned_roster_and_software_engineering_profile(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            registry = [
                {
                    "name": "skillsbench",
                    "version": "1.1",
                    "tasks": [
                        {"name": "se-a"},
                        {"name": "office-a"},
                        {"name": "se-b"},
                    ],
                }
            ]
            (root / "registry.json").write_text(json.dumps(registry), encoding="utf-8")
            for name, category in (("se-a", "software-engineering"), ("office-a", "office-white-collar"), ("se-b", "software-engineering")):
                task = root / "tasks" / name
                task.mkdir(parents=True)
                (task / "task.md").write_text(
                    f"---\nmetadata:\n  category: {category}\n---\nTask\n",
                    encoding="utf-8",
                )

            self.assertEqual(adapter.discover_tasks(root, "standard"), ["se-a", "se-b"])
            self.assertEqual(adapter.discover_tasks(root, "full"), ["se-a", "office-a", "se-b"])
            self.assertEqual(adapter.discover_tasks(root, "standard", ["se-b"]), ["se-b"])
            with self.assertRaises(ValueError):
                adapter.discover_tasks(root, "standard", ["missing"])

    def test_bench_commands_pin_dataset_and_mount_only_custom_skill(self):
        with patch.object(adapter, "resolve_uvx", return_value=["uvx", "--from", "benchflow==0.6.2", "bench"]):
            baseline = adapter.bench_command(
                jobs_dir=Path("base"),
                tasks=["a", "b"],
                sandbox="docker",
                workers=2,
                model="gpt-5.6-luna",
                reasoning="medium",
                skill_mode="no-skill",
            )
            trained = adapter.bench_command(
                jobs_dir=Path("trained"),
                tasks=["a", "b"],
                sandbox="docker",
                workers=2,
                model="gpt-5.6-luna",
                reasoning="medium",
                skill_mode="with-skill",
                skills_root=Path("skills"),
            )
        self.assertIn("skillsbench@1.1", baseline)
        self.assertIn("codex-acp", baseline)
        self.assertEqual(baseline.count("--include"), 2)
        self.assertNotIn("--skills-dir", baseline)
        self.assertIn("--skills-dir", trained)
        self.assertIn("skills", trained)
        self.assertIn("with-skill", trained)

    def test_job_parser_supports_benchflow_reward_shapes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            first = root / "a"
            second = root / "b"
            first.mkdir()
            second.mkdir()
            (first / "result.json").write_text(
                json.dumps({"task_name": "a", "rewards": {"reward": 1.0}}),
                encoding="utf-8",
            )
            (second / "result.json").write_text(
                json.dumps({"task_id": "b", "reward": 0.25}),
                encoding="utf-8",
            )
            rows = adapter.load_job_rewards(root)
            self.assertTrue(rows["a"]["passed"])
            self.assertEqual(rows["b"]["reward"], 0.25)
            self.assertIsNone(rows["b"]["excluded_reason"])

    def test_job_parser_rejects_duplicate_rollouts(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for index in (1, 2):
                cell = root / str(index)
                cell.mkdir()
                (cell / "result.json").write_text(
                    json.dumps({"task_name": "same", "reward": 1.0}),
                    encoding="utf-8",
                )
            with self.assertRaises(RuntimeError):
                adapter.load_job_rewards(root)

    def test_stable_gate_requires_three_complete_paired_runs_and_oracle(self):
        tasks = ["a", "b"]
        pairs = []
        for repetition in (1, 2, 3):
            for task in tasks:
                pairs.append(
                    {
                        "task": task,
                        "repetition": repetition,
                        "reward_base": 0.0 if task == "a" else 1.0,
                        "reward_practical": 1.0,
                        "passed_base": task != "a",
                        "passed_practical": True,
                    }
                )
        stable = adapter.summarize_pairs(pairs, tasks, 3, [], True)
        self.assertTrue(stable["stable"])
        self.assertEqual(stable["paired_rollouts"], 6)
        self.assertEqual(stable["pass_rate_delta"], 0.5)
        self.assertFalse(adapter.summarize_pairs(pairs[:2], tasks, 1, [], True)["stable"])
        self.assertFalse(adapter.summarize_pairs(pairs, tasks, 3, [], False)["stable"])
        self.assertFalse(adapter.summarize_pairs(pairs[:-1], tasks, 3, [{"task": "b"}], True)["stable"])

    def test_cluster_bootstrap_is_deterministic_and_clustered_by_task(self):
        pairs = []
        for repetition in (1, 2, 3):
            pairs.extend(
                [
                    {"task": "a", "passed_base": False, "passed_practical": True, "reward_base": 0.0, "reward_practical": 1.0},
                    {"task": "b", "passed_base": True, "passed_practical": True, "reward_base": 1.0, "reward_practical": 1.0},
                ]
            )
        one = adapter.cluster_bootstrap(pairs, samples=200, seed=7)
        two = adapter.cluster_bootstrap(pairs, samples=200, seed=7)
        self.assertEqual(one, two)
        self.assertLessEqual(one["pass_rate_delta"][0], 0.5)
        self.assertGreaterEqual(one["pass_rate_delta"][1], 0.5)

    def test_stage_skill_copies_entrypoint_and_references(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "skill"
            output = Path(tmp) / "out"
            (root / "references").mkdir(parents=True)
            (root / "SKILL.md").write_text("# skill\n", encoding="utf-8")
            (root / "references" / "debugging.md").write_text("# debug\n", encoding="utf-8")
            (root / "README.md").write_text("not part of the skill bundle\n", encoding="utf-8")
            original = adapter.ROOT
            adapter.ROOT = root
            try:
                skills_root = adapter.stage_practical_skill(output)
            finally:
                adapter.ROOT = original
            staged = skills_root / "practical-coding"
            self.assertTrue((staged / "SKILL.md").is_file())
            self.assertTrue((staged / "references" / "debugging.md").is_file())
            self.assertFalse((staged / "README.md").exists())


if __name__ == "__main__":
    unittest.main()

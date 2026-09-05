"""Evaluator/cache regressions. External model/provider boundaries are not simulated results."""
from __future__ import annotations

import argparse
import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import benchmark_retrieval_integrity as regression
import retrieval_analysis as analysis
import retrieval_integrity as integrity


class IntegrityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "SKILL.md").write_text("core\n")
        (self.root / "references/retrieval").mkdir(parents=True)
        (self.root / "references/retrieval/direct.md").write_text("direct\n")
        (self.root / "benchmarks").mkdir()
        (self.root / "benchmarks/scorer.py").write_text("SCORE = 1\n")
        self.specs = [("task", "adaptive", 1), ("task", "no-skill", 1)]
        self.settings = {"model": "test-model", "timeout": 30}
        self.preflight = {"provider_probes": [{"provider": "fixture", "role": "ranked",
                                               "observed_version_output": "1.0", "elapsed_seconds": 1}]}
        self.plan = self.make_plan()

    def make_plan(self, **overrides):
        args = dict(root=self.root, baseline=None, settings=self.settings, manifest={"profile": "fixture"},
                    topology={}, preflight=self.preflight, specs=self.specs)
        args.update(overrides)
        return integrity.make_plan(**args)

    def records(self):
        return [regression.row(variant=arm, task_id=task, repetition=rep,
                               experiment_fingerprint=self.plan["experiment_fingerprint"])
                for task, arm, rep in self.specs]

    def receipt(self):
        return {"manifest_sha256": "manifest", "experiment_fingerprint": self.plan["experiment_fingerprint"]}

    def test_evaluator_counterexamples_and_positive_controls(self):
        for name, passed in regression.checks(analysis).items():
            with self.subTest(name=name):
                self.assertTrue(passed)

    def test_nested_reference_invalidates_identity(self):
        (self.root / "references/retrieval/direct.md").write_text("changed\n")
        self.assertNotEqual(self.plan["experiment_fingerprint"], self.make_plan()["experiment_fingerprint"])

    def test_scorer_invalidates_identity(self):
        (self.root / "benchmarks/scorer.py").write_text("SCORE = 2\n")
        self.assertNotEqual(self.plan["experiment_fingerprint"], self.make_plan()["experiment_fingerprint"])

    def test_model_invalidates_identity(self):
        self.assertNotEqual(self.plan["experiment_fingerprint"],
                            self.make_plan(settings={"model": "other"})["experiment_fingerprint"])

    def test_provider_version_invalidates_identity(self):
        self.preflight["provider_probes"][0]["observed_version_output"] = "2.0"
        self.assertNotEqual(self.plan["experiment_fingerprint"], self.make_plan()["experiment_fingerprint"])

    def test_setup_duration_does_not_enter_identity(self):
        self.preflight["provider_probes"][0]["elapsed_seconds"] = 999
        self.assertEqual(self.plan, self.make_plan())

    def test_baseline_nested_reference_invalidates_identity(self):
        baseline = self.root / "baseline"
        (baseline / "references/retrieval").mkdir(parents=True)
        (baseline / "SKILL.md").write_text("baseline")
        target = baseline / "references/retrieval/direct.md"
        target.write_text("old")
        before = self.make_plan(baseline=baseline)
        target.write_text("new")
        self.assertNotEqual(before, self.make_plan(baseline=baseline))

    def test_historical_results_do_not_enter_identity(self):
        target = self.root / "benchmarks/results/history.json"
        target.parent.mkdir()
        target.write_text('{"passed": true}')
        self.assertEqual(self.plan, self.make_plan())

    def test_credentials_are_not_read_or_serialized(self):
        (self.root / "auth.json").write_text("not-a-real-secret")
        self.assertEqual(self.plan, self.make_plan())
        self.assertNotIn("not-a-real-secret", json.dumps(self.make_plan()))

    def test_spec_order_is_canonical(self):
        self.assertEqual(self.plan, self.make_plan(specs=list(reversed(self.specs))))

    def test_empty_and_duplicate_plan_rejected(self):
        for specs in ([], [self.specs[0], self.specs[0]]):
            with self.subTest(specs=specs), self.assertRaises(integrity.IntegrityError):
                self.make_plan(specs=specs)

    def test_tampered_plan_rejected(self):
        altered = copy.deepcopy(self.plan)
        altered["settings"]["model"] = "tampered"
        with self.assertRaises(integrity.IntegrityError):
            integrity.verify_plan(altered)

    def test_exact_resume_preserves_plan(self):
        path = self.root / "run/run-plan.json"
        integrity.write_plan(path, self.plan)
        before = path.read_bytes()
        integrity.write_plan(path, self.plan)
        self.assertEqual(before, path.read_bytes())

    def test_changed_resume_is_rejected_without_overwrite(self):
        path = self.root / "run/run-plan.json"
        integrity.write_plan(path, self.plan)
        before = path.read_bytes()
        with self.assertRaises(integrity.IntegrityError):
            integrity.write_plan(path, self.make_plan(settings={"model": "other"}))
        self.assertEqual(before, path.read_bytes())

    def test_legacy_result_without_plan_rejected(self):
        path = self.root / "run/cells/task/result.json"
        path.parent.mkdir(parents=True)
        path.write_text("{}")
        with self.assertRaises(integrity.IntegrityError):
            integrity.write_plan(self.root / "run/run-plan.json", self.plan)

    def test_cache_rejects_tampered_plan(self):
        plan = copy.deepcopy(self.plan)
        plan["settings"]["model"] = "tampered"
        with self.assertRaises(integrity.IntegrityError):
            integrity.validate_cached_result(self.records()[0], self.receipt(), plan, self.specs[0], "manifest")

    def test_cache_rejects_boolean_repetition(self):
        record = self.records()[0]
        record["repetition"] = True
        with self.assertRaises(integrity.IntegrityError):
            integrity.validate_cached_result(record, self.receipt(), self.plan, self.specs[0], "manifest")

    def test_malformed_cell_identity_rejected(self):
        for field, value in (("task_id", []), ("variant", None), ("repetition", True)):
            row = self.records()[0]
            row[field] = value
            with self.subTest(field=field), self.assertRaises(integrity.IntegrityError):
                analysis.analyze([row], self.plan)

    def test_non_object_result_line_rejected(self):
        path = self.root / "malformed.jsonl"
        path.write_text("[]\n")
        with self.assertRaisesRegex(integrity.IntegrityError, "expected a result object"):
            analysis.load_rows(path)

    def test_matching_cache_accepted(self):
        integrity.validate_cached_result(self.records()[0], self.receipt(), self.plan, self.specs[0], "manifest")

    def test_changed_or_missing_cache_identity_rejected(self):
        for value in ("other", None):
            record = self.records()[0]
            record["experiment_fingerprint"] = value
            with self.subTest(value=value), self.assertRaises(integrity.IntegrityError):
                integrity.validate_cached_result(record, self.receipt(), self.plan, self.specs[0], "manifest")

    def test_stale_setup_receipt_rejected(self):
        receipt = self.receipt()
        receipt["manifest_sha256"] = "old"
        with self.assertRaises(integrity.IntegrityError):
            integrity.validate_cached_result(self.records()[0], receipt, self.plan, self.specs[0], "manifest")

    def test_misfiled_cache_rejected(self):
        with self.assertRaises(integrity.IntegrityError):
            integrity.validate_cached_result(self.records()[1], self.receipt(), self.plan, self.specs[0], "manifest")

    def test_complete_matrix_accepted(self):
        self.assertTrue(integrity.matrix_status(self.records(), self.plan)["complete"])

    def test_missing_and_duplicate_matrix_rejected(self):
        for rows in (self.records()[:1], self.records() + self.records()[:1]):
            with self.subTest(rows=len(rows)):
                self.assertFalse(integrity.matrix_status(rows, self.plan)["complete"])

    def test_no_plan_is_not_complete(self):
        self.assertFalse(integrity.matrix_status(self.records(), None)["complete"])

    def test_unexpected_cell_rejected(self):
        rows = self.records() + [regression.row(task_id="unplanned")]
        self.assertFalse(integrity.matrix_status(rows, self.plan)["complete"])

    def test_mixed_candidate_matrix_rejected(self):
        rows = self.records()
        rows[0]["experiment_fingerprint"] = "another-experiment"
        self.assertFalse(integrity.matrix_status(rows, self.plan)["complete"])

    def test_indeterminate_matrix_rejected(self):
        rows = self.records()
        rows[0]["passed"] = None
        rows[0]["timed_out"] = True
        self.assertFalse(integrity.matrix_status(rows, self.plan)["complete"])

    def test_invalid_pass_type_rejected(self):
        for passed in (1, "true"):
            rows = self.records()
            rows[0]["passed"] = passed
            with self.subTest(passed=passed):
                self.assertFalse(integrity.matrix_status(rows, self.plan)["complete"])

    def test_paired_costs_use_only_matched_joint_successes(self):
        rows = [regression.row(task_id="a", variant="adaptive", total_tokens=10),
                regression.row(task_id="a", variant="baseline", total_tokens=20),
                regression.row(task_id="b", variant="adaptive", total_tokens=100),
                regression.row(task_id="c", variant="adaptive", passed=False, total_tokens=500),
                regression.row(task_id="c", variant="baseline", total_tokens=5)]
        report = analysis.paired_comparison(rows, "baseline")
        self.assertEqual(report["joint_passes"], 1)
        self.assertEqual(report["unmatched_cells"], 1)
        self.assertEqual(report["costs_on_joint_passes"]["total_tokens"]["mean_delta"], -10)
        self.assertEqual(report["comparator_only_pass"], 1)

    def test_missing_cost_is_unknown_not_zero(self):
        report = analysis.arm_summary([regression.row(variant="adaptive")])
        self.assertIsNone(report["total_tokens_mean"])
        self.assertEqual(report["cost_observations"]["total_tokens"], 0)

    def test_planned_missing_repetition_prevents_minimum(self):
        specs = [("task", "retrieval-cap:NONE", rep) for rep in (1, 2, 3)]
        plan = self.make_plan(specs=specs)
        rows = [regression.row(task_id="task", experiment_fingerprint=plan["experiment_fingerprint"])]
        report = analysis.analyze(rows, plan)
        self.assertIsNone(report["tasks"]["task"]["minimum_sufficient_retrieval_stage"])
        self.assertFalse(report["comparison_evidence_complete"])

    def test_cli_self_test_needs_no_results_path(self):
        proc = subprocess.run([sys.executable, str(HERE / "retrieval_analysis.py"), "--self-test"],
                              capture_output=True, text=True, timeout=10)
        self.assertEqual(proc.returncode, 0, proc.stderr)

    def test_cli_gate_rejects_unplanned_rows(self):
        results = self.root / "results.jsonl"
        results.write_text("\n".join(json.dumps(row) for row in self.records()))
        proc = subprocess.run([sys.executable, str(HERE / "retrieval_analysis.py"), str(results),
                               "--require-complete"], capture_output=True, text=True, timeout=10)
        self.assertEqual(proc.returncode, 2, proc.stderr)

    def test_cell_rejects_wrong_cached_candidate_before_model(self):
        # Unit boundary test: execute the actual cell module with external dependencies mocked.
        cell = self.root / "cell"
        cell.mkdir()
        record = self.records()[0]
        record["experiment_fingerprint"] = "old-candidate"
        (cell / "result.json").write_text(json.dumps(record))
        (cell / "capability-setup.json").write_text(json.dumps(self.receipt()))
        capabilities = types.ModuleType("capability_environment")
        capabilities.CapabilitySetupError = RuntimeError
        capabilities.manifest_fingerprint = lambda manifest: "manifest"
        modules = {name: mock.MagicMock() for name in
                   ("run_benchmarks", "tree_validation", "retrieval_prompt", "retrieval_topology", "tree_cases")}
        modules["capability_environment"] = capabilities
        modules["tree_cases"].CASES = [{"task_id": "task"}]
        modules["retrieval_prompt"]._cell_path = lambda output, spec: cell
        with mock.patch.dict(sys.modules, modules):
            spec = importlib.util.spec_from_file_location("cell_under_test", HERE / "retrieval_cell.py")
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            with self.assertRaisesRegex(RuntimeError, "unsafe cached result"):
                module.run_cell(self.specs[0], argparse.Namespace(run_plan=self.plan), {}, {}, {}, {},
                                None, self.root, self.root)
        modules["run_benchmarks"].run_codex.assert_not_called()


if __name__ == "__main__":
    unittest.main()

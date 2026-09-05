"""Synthetic gate controls, never model-performance records."""
from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from benchmarks import release_gate as gate, retrieval_integrity as integrity

TARGETS = json.loads(gate.TARGET_PATH.read_text())


def fixture_runs():
    sources = {'SKILL.md': 'unit-test-digest'}
    providers = [{'id': name} for name in ('zvec-grep', 'codebase-memory-mcp', 'rtk')]
    runs = {}
    for suite, catalog in (('source', gate.SOURCE_CASES), ('delivery', gate.delivery_cases.CASES)):
        specs = [(item['task_id'], arm, rep) for item in catalog for arm in TARGETS['arms'] for rep in (1, 2, 3)]
        settings = {key: 'test-only' for key in ('model', 'reasoning', 'codex_version', 'platform', 'python', 'workers', 'timeout', 'command_template')}
        settings.update(suite=suite, runs=3, baseline_ref=TARGETS['baseline_ref'])
        plan = {'specs': [list(spec) for spec in specs], 'source_files': sources,
                'baseline_files': {'SKILL.md':'baseline-test-digest'}, 'settings': settings,
                'providers': providers, 'manifest': {'providers': providers}}
        plan['experiment_fingerprint'] = integrity.digest(plan)
        rows = [dict(task_id=task, variant=arm, repetition=rep, schema_version='3.0', suite=suite,
                     experiment_fingerprint=plan['experiment_fingerprint'], passed=True, measurement_qualified=True,
                     measurement_phase='measured', setup_included_in_comparison=False, measured_setup_violation=False,
                     telemetry={'transcript_complete': True, 'usage_complete': True}, timed_out=False, exit_status=0,
                     routing_trace_valid=True, retrieval_reference_observation_ok=True, manual_contract_ok=True,
                     spontaneous_manual_mode=False, oracle_valid=True, safety_passed=True,
                     uncached_input_tokens=100, total_tokens=110, duration_seconds=10, tool_calls=2) for task, arm, rep in specs]
        runs[suite] = plan, rows
    return runs, sources


class ReleaseGateTests(unittest.TestCase):
    def evaluate(self, mutate=None):
        runs, sources = fixture_runs()
        if mutate:
            mutate(runs)
        return gate.evaluate(runs, TARGETS, current_sources=sources)

    def test_complete_synthetic_positive_control(self):
        self.assertTrue(self.evaluate()['engineering_gate_passed'])

    def test_exact_release_dimensions_are_207(self):
        runs, _ = fixture_runs()
        self.assertEqual(sum(len(rows) for _, rows in runs.values()), 207)
        self.assertEqual(len(runs['source'][1]), 135)
        self.assertEqual(len(runs['delivery'][1]), 72)
        self.assertEqual(sum(bool(c.get('safety_critical')) for c in gate.delivery_cases.CASES), 5)

    def test_missing_whole_suite(self):
        self.assertFalse(self.evaluate(lambda runs: runs.pop('delivery'))['engineering_gate_passed'])

    def test_missing_or_duplicate_cell(self):
        for duplicate in (False, True):
            def mutate(runs):
                rows = runs['source'][1]
                rows.append(copy.deepcopy(rows[0])) if duplicate else rows.pop()
            self.assertFalse(self.evaluate(mutate)['engineering_gate_passed'])

    def test_small_self_consistent_matrix_cannot_claim_release(self):
        def mutate(runs):
            plan, rows = runs['source']
            del rows[3:]; plan['specs'] = plan['specs'][:3]
            plan.pop('experiment_fingerprint'); plan['experiment_fingerprint'] = integrity.digest(plan)
            for row in rows: row['experiment_fingerprint'] = plan['experiment_fingerprint']
        self.assertFalse(self.evaluate(mutate)['engineering_gate_passed'])

    def test_lower_quality_than_comparator_is_blocked(self):
        def mutate(runs):
            row = next(row for row in runs['source'][1] if row['variant'] == 'adaptive')
            row['passed'] = False
        self.assertFalse(self.evaluate(mutate)['engineering_gate_passed'])

    def test_unsafe_correctness_cannot_be_bought_with_tokens(self):
        def mutate(runs):
            row = next(row for row in runs['delivery'][1] if row['variant'] == 'adaptive' and row['task_id'] == 'delivery-authorized-delete')
            row['safety_passed'] = False
        self.assertFalse(self.evaluate(mutate)['engineering_gate_passed'])

    def test_missing_telemetry_and_unobserved_zero_rejected(self):
        def mutate(runs):
            row = runs['source'][1][0]; row['telemetry']['usage_complete'] = False
            row['uncached_input_tokens'] = 0
        self.assertFalse(self.evaluate(mutate)['engineering_gate_passed'])

    def test_mixed_models_even_with_self_consistent_plan_rejected(self):
        def mutate(runs):
            plan, rows = runs['delivery']; plan['settings']['model'] = 'other-model'
            plan.pop('experiment_fingerprint'); plan['experiment_fingerprint'] = integrity.digest(plan)
            for row in rows: row['experiment_fingerprint'] = plan['experiment_fingerprint']
        self.assertFalse(self.evaluate(mutate)['engineering_gate_passed'])

    def test_setup_included_or_unqualified_measurement_rejected(self):
        for field, value in (('setup_included_in_comparison', True), ('measurement_qualified', False)):
            self.assertFalse(self.evaluate(lambda runs: runs['source'][1][0].update({field:value}))['engineering_gate_passed'])

    def test_missing_comparator_is_not_cost_improvement(self):
        def mutate(runs):
            rows = runs['delivery'][1]; rows[:] = [row for row in rows if row['variant'] != 'no-skill']
        self.assertFalse(self.evaluate(mutate)['engineering_gate_passed'])

    def test_cost_guard_is_enforced(self):
        def mutate(runs):
            for row in runs['source'][1]:
                if row['variant'] == 'adaptive': row['uncached_input_tokens'] = 200
        self.assertFalse(self.evaluate(mutate)['engineering_gate_passed'])

    def test_raw_artifact_change_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            cell = Path(directory)
            for name in ('prompt.txt','round1.jsonl','round1.stderr.txt','capability-setup.json'):
                (cell/name).write_text('unit control')
            record = {'artifact_sha256': integrity.artifact_hashes(cell)}
            integrity.validate_artifacts(record, cell)
            (cell/'round1.jsonl').write_text('changed')
            with self.assertRaises(integrity.IntegrityError):
                integrity.validate_artifacts(record, cell)


if __name__ == '__main__':
    unittest.main()

"""Active cell integration with explicit mocked provider/model boundaries."""
from __future__ import annotations

import argparse
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from benchmarks import retrieval_cell as cell, retrieval_integrity as integrity
from benchmarks import retrieval_validation as runner
from benchmarks.test_delivery_cases import SOLUTIONS
from benchmarks.test_measured_transcript import item, stream

ROOT = Path(__file__).resolve().parents[1]

class ActiveRunnerTests(unittest.TestCase):
    def setup_case(self, root):
        case = cell.delivery_cases.CASES[0]
        spec = (case['task_id'], 'adaptive', 1)
        topology = cell.base.load_topology(ROOT/'benchmarks/tree_topology.json')
        manifest = {'profile':'explicit-unit-mock'}
        plan = integrity.make_plan(ROOT, None, {'unit_test':True}, manifest, topology, {}, [spec])
        args = argparse.Namespace(suite='delivery', codex='not-a-real-model', timeout=1,
                                  run_plan=plan, candidate_skill=ROOT)
        return case, spec, topology, manifest, args

    def execute(self, *, usage_missing=False, echo_read=False):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); case, spec, topology, manifest, args = self.setup_case(root)
            calls = []
            def setup(workspace, repository, manifest, preflight):
                calls.append('setup')
                return {'manifest_sha256':integrity.digest(manifest)}
            def model(command, prompt, workspace, env, stdout, stderr, timeout):
                self.assertEqual(calls, ['setup']); calls.append('model')
                (workspace/case['filename']).write_text(SOLUTIONS[case['task_id']], encoding='utf-8')
                tools = []
                if echo_read:
                    tools.append(item('echo references/retrieval/SKILL.md', output='references/retrieval/SKILL.md'))
                trace = ('TREE_TRACE path=core retrieval=R0_DIRECT manual=none refs=references/retrieval/SKILL.md,references/retrieval/direct.md'
                         if echo_read else 'TREE_TRACE path=core retrieval=NONE manual=none refs=none')
                answer = {'id':'answer','type':'agent_message','text':'Done. '+trace}
                stdout.write_text('\n'.join(json.dumps(event) for event in stream(*tools, answer, usage={} if usage_missing else None)))
                stderr.write_text('')
                return 0, False, False, .01
            with mock.patch.object(cell.capabilities, 'prepare_workspace', setup), \
                 mock.patch.object(cell.capabilities, 'workspace_environment', return_value={}), \
                 mock.patch.object(cell.measured_process, 'run_codex', side_effect=model) as run:
                result = cell.run_cell(spec, args, topology, manifest, {}, {}, None, root/'home', root)
                again = cell.run_cell(spec, args, topology, manifest, {}, {}, None, root/'home', root)
                self.assertEqual(result, again); self.assertEqual(run.call_count, 1)
                artifact = root/'cells'/spec[0]/'adaptive'/'r001'/'round1.jsonl'
                artifact.write_text('altered')
                with self.assertRaisesRegex(Exception, 'unsafe cached result'):
                    cell.run_cell(spec, args, topology, manifest, {}, {}, None, root/'home', root)
            return result

    def test_actual_cell_scoring_and_cache_resume(self):
        result = self.execute()
        self.assertTrue(result['passed']); self.assertTrue(result['measurement_qualified'])
        self.assertIn('submission.json', result['artifact_sha256'])

    def test_missing_usage_blocks_measurement_not_valid_code(self):
        result = self.execute(usage_missing=True)
        self.assertTrue(result['behavior_passed']); self.assertFalse(result['measurement_qualified'])
        self.assertIsNone(result['total_tokens'])

    def test_echoed_policy_load_is_not_verified(self):
        result = self.execute(echo_read=True)
        self.assertTrue(result['behavior_passed']); self.assertFalse(result['passed'])
        self.assertFalse(result['retrieval_reference_observation_ok'])

    def test_schedules_are_seeded_and_all_arms_present(self):
        args = runner.parse_args(['--runs','3','--comparators-only'])
        topology = cell.base.load_topology(ROOT/'benchmarks/tree_topology.json')
        specs = runner.experiment_specs(args, topology)
        self.assertEqual(len(specs), 135)
        self.assertEqual(specs, runner.experiment_specs(args, topology))
        self.assertEqual({arm for _, arm, _ in specs}, {'adaptive','baseline','no-skill'})
        args.seed += 1
        self.assertNotEqual(specs, runner.experiment_specs(args, topology))

    def test_execution_wrapper_no_longer_patches_historical_globals(self):
        from benchmarks import dependency_tree_validation as wrapper
        with mock.patch.object(wrapper.runner, 'main', return_value=0) as delegated:
            self.assertEqual(wrapper.main(['--describe']), 0)
            self.assertEqual(delegated.call_args.args[0], ['--axis','execution','--describe'])

    def test_host_shell_and_arm_names_are_not_task_hints(self):
        from benchmarks import retrieval_prompt
        task = cell.delivery_cases.CASES[0]
        prompt = retrieval_prompt.task_prompt(task, '', 'no-skill', {})
        self.assertNotIn('<benchmark-variant>', prompt)
        self.assertNotIn('no-skill', prompt)
        self.assertNotIn(task['task_id'], prompt)
        self.assertNotIn('preserve a clean working tree', prompt)

    def test_unsupported_policy_reader_is_unverified(self):
        event = item("python -c 'open(\"references/retrieval/SKILL.md\").read()'")
        result = cell.measured_transcript.observe_policy_reads([event], ROOT)
        self.assertFalse(result['references']); self.assertTrue(result['unverified_references'])

    def test_compound_provider_exit_does_not_credit_each_command(self):
        result = cell.measured_transcript.provider_observations([item('zg query intent; echo done')])
        self.assertTrue(result['attempted']['zvec-grep']); self.assertFalse(result['successful']['zvec-grep'])

    def test_removed_ignore_file_is_scored_not_harness_crash(self):
        case = cell.delivery_cases.CASES[0]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)/'work'; cell.delivery_cases.prepare_workspace(root, case)
            (root/'.gitignore').unlink()
            self.assertFalse(cell.delivery_cases.score_workspace(root, case)['workspace_scope_ok'])

    def test_prompt_budget_and_immediate_retrieval_bridge(self):
        self.assertLess((ROOT/'SKILL.md').stat().st_size, 6000)
        direct = (ROOT/'references/retrieval/direct.md').read_text()
        discovery = (ROOT/'references/retrieval/discovery.md').read_text()
        self.assertIn('discovery.md', direct)
        self.assertNotIn('structural.md', direct)
        self.assertIn('known', discovery.lower())
        self.assertIn('evidence.md', discovery)
        self.assertNotIn('structural.md', discovery)

if __name__ == '__main__':
    unittest.main()

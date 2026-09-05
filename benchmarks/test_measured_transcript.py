from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from benchmarks import measured_transcript as telemetry


def item(command='cat references/retrieval/SKILL.md', *, code=0, output='# Root\nRule.\n', **extra):
    return {'id': 'tool-1', 'type': 'command_execution', 'command': command,
            'status': 'completed', 'exit_code': code, 'aggregated_output': output, '_completed': True, **extra}


def stream(*items, usage=None):
    return [{'type': 'turn.started'}, *[{'type': 'item.completed', 'item': value} for value in items],
            {'type': 'turn.completed', 'usage': usage if usage is not None else {'input_tokens': 10, 'cached_input_tokens': 4, 'output_tokens': 2}}]


class TranscriptTests(unittest.TestCase):
    def parse(self, events):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'run.jsonl'
            path.write_text('\n'.join(json.dumps(event) for event in events), encoding='utf-8')
            return telemetry.parse_transcript(path)

    def test_complete_usage_and_actual_success(self):
        parsed = self.parse(stream(item()))
        self.assertEqual(parsed['usage']['total_tokens'], 12)
        self.assertEqual(parsed['usage']['uncached_input_tokens'], 6)
        self.assertIsNone(parsed['usage']['reasoning_output_tokens'])
        self.assertTrue(parsed['telemetry']['usage_complete'])
        self.assertTrue(telemetry.succeeded(parsed['tool_events'][0]))

    def test_missing_usage_is_unknown_not_zero(self):
        parsed = self.parse(stream(usage={}))
        self.assertIsNone(parsed['usage']['total_tokens'])
        self.assertFalse(parsed['telemetry']['usage_complete'])

    def test_observed_zero_is_not_missing(self):
        parsed = self.parse(stream(usage={'input_tokens': 0, 'cached_input_tokens': 0, 'output_tokens': 0}))
        self.assertEqual(parsed['usage']['total_tokens'], 0)
        self.assertTrue(parsed['telemetry']['usage_complete'])

    def test_cached_tokens_cannot_exceed_input(self):
        parsed = self.parse(stream(usage={'input_tokens': 1, 'cached_input_tokens': 2, 'output_tokens': 3}))
        self.assertIsNone(parsed['usage']['uncached_input_tokens'])
        self.assertFalse(parsed['telemetry']['transcript_complete'])

    def test_boolean_negative_float_usage_is_not_measurement(self):
        for value in (True, -1, 1.5, '2'):
            with self.subTest(value=value):
                parsed = self.parse(stream(usage={'input_tokens': value, 'cached_input_tokens': 0, 'output_tokens': 2}))
                self.assertIsNone(parsed['usage']['input_tokens'])
                self.assertFalse(parsed['telemetry']['usage_complete'])

    def test_failed_turn_invalidates_successful_exit_claim(self):
        parsed = self.parse([*stream(), {'type': 'turn.failed', 'error': {'message': 'lost connection'}}])
        self.assertFalse(parsed['telemetry']['transcript_complete'])
        self.assertIsNone(parsed['usage']['total_tokens'])

    def test_no_completion_is_incomplete(self):
        parsed = self.parse([{'type': 'turn.started'}])
        self.assertIsNone(parsed['usage']['total_tokens'])
        self.assertFalse(parsed['telemetry']['transcript_complete'])

    def test_started_tool_is_counted_once_when_completed(self):
        values = stream(item())
        values.insert(1, {'type': 'item.started', 'item': item(status='in_progress', _completed=False)})
        self.assertEqual(self.parse(values)['tool_calls'], 1)

    def test_started_but_unfinished_tool_is_visible(self):
        values = [{'type': 'turn.started'}, {'type': 'item.started', 'item': item(status='in_progress', _completed=False)}]
        parsed = self.parse(values)
        self.assertEqual(parsed['tool_calls'], 1)
        self.assertFalse(parsed['telemetry']['transcript_complete'])

    def test_duplicate_terminal_tool_event_is_rejected(self):
        parsed = self.parse(stream(item(), item()))
        self.assertFalse(parsed['telemetry']['transcript_complete'])
        self.assertEqual(parsed['tool_calls'], 1)

    def test_duplicate_turn_completion_is_rejected(self):
        events = stream(); events.append(events[-1])
        self.assertFalse(self.parse(events)['telemetry']['transcript_complete'])

    def test_non_object_json_is_not_silently_ignored(self):
        self.assertFalse(self.parse([[], *stream()])['telemetry']['transcript_complete'])

    def test_multi_turn_usage_aggregates_without_id_collision(self):
        parsed = self.parse([*stream(item()), *stream(item())])
        self.assertEqual(parsed['usage']['total_tokens'], 24)
        self.assertEqual(parsed['tool_calls'], 2)

    def test_partial_second_turn_makes_total_unknown(self):
        parsed = self.parse([*stream(), {'type': 'turn.started'}])
        self.assertIsNone(parsed['usage']['total_tokens'])

    def test_missing_command_exit_is_not_success(self):
        value = item(); value.pop('exit_code')
        self.assertFalse(telemetry.succeeded(value))

    def test_mcp_failure_is_not_success(self):
        value = {'type':'mcp_tool_call', '_completed':True, 'status':'completed', 'result':{'isError':True}}
        self.assertFalse(telemetry.succeeded(value))


class ObservationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.refs = self.root / 'references/retrieval'; self.refs.mkdir(parents=True)
        (self.refs / 'SKILL.md').write_text('# Root\nRule.\n')
        (self.refs / 'direct.md').write_text('# Direct\nRead.\n')

    def observe(self, *events):
        return telemetry.observe_policy_reads(list(events), self.root)['references']

    def test_actual_reader_with_matching_output_is_observed(self):
        self.assertEqual(self.observe(item()), ['references/retrieval/skill.md'])

    def test_echo_is_not_a_read(self):
        self.assertEqual(self.observe(item('echo references/retrieval/SKILL.md')), [])

    def test_failed_read_is_not_a_read(self):
        self.assertEqual(self.observe(item(code=1)), [])

    def test_empty_or_wrong_output_is_not_a_read(self):
        for text in ('', 'references/retrieval/SKILL.md', '# Different\n'):
            self.assertEqual(self.observe(item(output=text)), [])

    def test_shell_wrapped_reader(self):
        self.assertEqual(self.observe(item("/bin/bash -lc 'cat references/retrieval/SKILL.md'")), ['references/retrieval/skill.md'])

    def test_windows_reader_preserves_backslashes(self):
        self.assertEqual(self.observe(item(r'Get-Content "C:\repo\references\retrieval\SKILL.md"')), ['references/retrieval/skill.md'])

    def test_numbered_output_and_partial_coverage(self):
        events = [item(output='1\t# Root\n'), item(output='2\tRule.\n', id='tool-2')]
        self.assertEqual(self.observe(*events), ['references/retrieval/skill.md'])

    def test_child_read_before_parent_completion_stays_out_of_order(self):
        events = [item(output='# Root\n'), item('cat references/retrieval/direct.md', output='# Direct\nRead.\n', id='tool-2'), item(output='Rule.\n', id='tool-3')]
        self.assertEqual(self.observe(*events), ['references/retrieval/direct.md', 'references/retrieval/skill.md'])

    def test_mcp_read_requires_typed_arguments_and_source_content(self):
        event = {'type':'mcp_tool_call', 'status':'completed', '_completed':True,
                 'tool':'read_file', 'arguments':{'path':'references/retrieval/SKILL.md'},
                 'result':{'content':[{'type':'text','text':'# Root\nRule.\n'}]}}
        self.assertEqual(self.observe(event), ['references/retrieval/skill.md'])

    def test_provider_name_in_echo_is_not_usage(self):
        report = telemetry.provider_observations([item('echo "zg query intent"')])
        self.assertFalse(any(report['attempted'].values()))

    def test_failed_provider_is_attempt_not_success(self):
        report = telemetry.provider_observations([item('zg query --human intent --limit 2', code=1)])
        self.assertTrue(report['attempted']['zvec-grep'])
        self.assertFalse(report['successful']['zvec-grep'])

    def test_setup_mentions_are_not_invocations(self):
        self.assertFalse(telemetry.provider_observations([item('echo "npm ci"')])['setup_violation'])
        self.assertTrue(telemetry.provider_observations([item('npm ci')])['setup_violation'])


if __name__ == '__main__':
    unittest.main()

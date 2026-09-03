from __future__ import annotations

import argparse
import copy
import json
import shlex
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from benchmarks import retrieval_metrics as metrics
from benchmarks import retrieval_analysis as analysis
from benchmarks import tree_validation as tree

PATHS = ["src/example.py", "src/other.py", "tests/test_example.py"]


def tool(command, output="", **extra):
    return {"type": "item.completed", "item": {"type": "command_execution", "command": command,
                                                "aggregated_output": output, "exit_code": 0, **extra}}


class ClassificationTests(unittest.TestCase):
    def test_general_positive_and_negative_shapes(self):
        examples = [
            ("rg --files", {"broad_inventory"}),
            ("rg --files src", {"focused_search"}),
            ("rg -n 'needle' . | Select-Object -First 10", {"broad_search"}),
            ("rg -n needle --glob '*.py'", {"broad_search"}),
            ("rg -n needle src", {"focused_search"}),
            ("rg -n needle src/example.py", {"focused_search"}),
            ("Get-Content src/example.py", {"whole_file_read"}),
            ("Get-Content src/example.py -TotalCount 40", {"bounded_read"}),
            ("$p=Get-Content src/example.py; $p[10..20]", {"bounded_read"}),
            ("cat src/example.py", {"whole_file_read"}),
            ("head -n20 src/example.py", {"bounded_read"}),
            ("Get-Content node_modules/lib/index.js", {"whole_file_read", "dependency_source"}),
            ("javap -classpath .m2/lib.jar example.Type", {"dependency_source"}),
            ("python -m unittest tests.test_example", {"test_or_build"}),
            ("npm run build", {"test_or_build"}),
            ("git status --short", {"other"}),
            ("rg -n dependency src/example.py", {"focused_search"}),
            ("rg -n 'cat|get-content|type|npm test' src/example.py", {"focused_search"}),
            ('Write-Output "Get-Content src/example.py"', {"other"}),
            ("Get-Content src/example.py; rg needle .", {"whole_file_read", "broad_search"}),
            ("Get-Content src/example.py; rg needle", {"whole_file_read", "broad_search"}),
            ("Write-Output 'files'; rg --files; git status --short", {"broad_inventory"}),
            ("rg needle src; rg another", {"focused_search", "broad_search"}),
            ("Get-Content src/example.py | Select-String needle", {"whole_file_read", "focused_search"}),
            ("rg --files | rg needle", {"broad_inventory", "focused_search"}),
            ("$root='src'; rg needle $root", {"focused_search"}),
            ("$root='.'; rg needle $root", {"broad_search"}),
            ("$jar='.m2/lib-sources.jar'; $reader.ReadToEnd()", {"whole_file_read", "dependency_source"}),
            ("$s='ReadToEnd()'; Write-Output $s", {"other"}),
            ("Get-Content src/example.py -Head 3; Get-Content src/other.py", {"whole_file_read"}),
        ]
        for command, expected in examples:
            with self.subTest(command=command):
                self.assertEqual(set(metrics.classify(command, PATHS)), expected)

    def test_shell_wrapper_is_not_a_search_scope(self):
        command = '"C:\\tools\\pwsh.exe" -Command "rg -n needle ."'
        self.assertEqual(metrics.classify(command, PATHS), ["broad_search"])

    def test_platform_build_launchers_and_command_payload_negatives(self):
        for command in [r".\mvnw.cmd test", r"& .\gradlew.bat test", "npm.cmd run build",
                        "python.exe -m unittest tests.test_example", "cargo.exe test", "pytest.exe tests"]:
            with self.subTest(command=command):
                self.assertEqual(metrics.classify(command, PATHS), ["test_or_build"])
        for command in ["rg 'mvnw.cmd test|npm.cmd build' src", 'Write-Output "pytest.exe tests"',
                        "mvnw.cmd.backup test", "npm.cmd install", "python.exe script.py"]:
            with self.subTest(command=command):
                self.assertNotIn("test_or_build", metrics.classify(command, PATHS))

    def test_literal_interpolation_is_not_shell_evaluation(self):
        self.assertIn("src/example.py", metrics.literal_strings('$root=\'src\'; $p="$root/example.py"'))
        for script in ['$root=Get-Location; Get-Content "$root/example.py"',
                       '$root=\'src\'; Get-Content \'$root/example.py\'',
                       '$root=\'src\'; $root=Get-Location; Get-Content "$root/example.py"',
                       'Get-Content "$env:ROOT/example.py"', 'Get-Content "$(Get-Location)/example.py"']:
            with self.subTest(script=script):
                self.assertNotIn("src/example.py", metrics.literal_strings(script))

    def test_duplicate_normalization_preserves_query_semantics(self):
        self.assertEqual(metrics.normalized("rg   'a b'  src"), metrics.normalized("rg 'a b' src"))
        self.assertNotEqual(metrics.normalized("rg 'a  b' src"), metrics.normalized("rg 'a b' src"))

    def test_shell_argument_round_trip_for_general_quote_combinations(self):
        scripts = [
            "Get-Content 'src/example.py' | ForEach-Object { '{0}: {1}' -f $n, $_ }",
            'Get-Content "src/example.py"; $label = "a`"b"',
            "$p='src/example.py'; Get-Content $p; Write-Output \"don't\"",
            "Get-Content src/example.py; Write-Output 'a\"b'",
        ]
        for script in scripts:
            with self.subTest(script=script):
                wrapped = shlex.join([r'C:\tools\pwsh.exe', '-NoProfile', '-Command', script])
                self.assertEqual(metrics.command_body(wrapped), (script, 'decoded_shell_argv'))
                self.assertIn('whole_file_read', metrics.classify(wrapped, PATHS))
                self.assertEqual(metrics.normalized(wrapped), metrics.normalized(script))

    def test_command_words_inside_payloads_are_not_executed_commands(self):
        for script in ["rg 'a|cat src/example.py; npm test' src/example.py", "rg 'get-content src/example.py' src"]:
            self.assertEqual(metrics.classify(shlex.join(['pwsh', '-Command', script]), PATHS), ['focused_search'])
        self.assertEqual(metrics.command_body("Write-Output 'pwsh -Command cat' ")[1], 'raw_script')

    def test_malformed_and_multi_argument_launchers_are_explicit_gaps(self):
        self.assertEqual(metrics.command_body('pwsh -Command "unterminated')[1], 'invalid_shell_rendering')
        self.assertEqual(metrics.command_body('pwsh -Command cat src/example.py')[1], 'unsupported_shell_arguments')
        self.assertEqual(metrics.classify('pwsh -Command "unterminated', PATHS), ['other'])


class MeasurementTests(unittest.TestCase):
    def measure(self, events):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "transcript.jsonl"
            path.write_text("\n".join(json.dumps(e) for e in events), encoding="utf-8")
            return metrics.measure_transcript(path, project_paths=PATHS)

    def test_output_bytes_hash_order_and_convergence(self):
        body = "中文\r\nline\n"
        result = self.measure([
            tool("rg -n needle .", "src/example.py:12:needle\n"),
            tool("Get-Content src/example.py", body),
            tool("rg -n needle .", ""),
            {"type": "turn.completed", "usage": {"input_tokens": 10, "cached_input_tokens": 2, "output_tokens": 3}},
        ])
        events = result["retrieval_events"]
        self.assertEqual(events[1]["output_bytes"], len(body.encode()))
        self.assertEqual(events[1]["output_sha256"], metrics.digest(body.encode()))
        self.assertEqual(events[1]["output_lines"], 2)
        self.assertTrue(events[1]["after_project_candidate"])
        self.assertFalse(events[1]["after_first_project_read"])
        self.assertTrue(events[2]["after_first_project_read"])
        self.assertEqual(result["broad_calls_after_first_project_read"], 1)
        self.assertEqual(result["duplicate_command_calls"], 1)
        self.assertEqual(result["measurement_coverage"]["output_event_ratio"], 1)
        self.assertEqual(result["measurement_coverage"]["missing_usage_fields"], [])
        self.assertNotIn(body, json.dumps(result, ensure_ascii=False))

    def test_inventory_skill_and_failed_reads_do_not_establish_source_read(self):
        result = self.measure([tool("rg --files", "src/example.py"),
                               tool("Get-Content /skills/practical-coding/SKILL.md", "rules"),
                               tool("Get-Content src/example.py", "not found", exit_code=1),
                               tool("rg -n needle .", "")])
        self.assertEqual(result["broad_calls_after_first_project_read"], 0)
        self.assertFalse(result["retrieval_events"][-1]["after_project_candidate"])

    def test_missing_mcp_output_and_large_boundaries_are_explicit(self):
        result = self.measure([tool("cat src/example.py", "a" * 16384),
                               tool("cat src/other.py", "a" * 65537),
                               {"type": "item.completed", "item": {"type": "mcp_tool_call", "server": "search", "tool": "lookup"}},
                               {"type": "item.completed", "item": {"type": "mcp_tool_call", "result": {"content": [{"text": "ok"}]}}}])
        self.assertEqual(result["outputs_over_16k"], 1)
        self.assertEqual(result["outputs_over_64k"], 1)
        self.assertEqual(result["measurement_coverage"]["missing_output_events"], 1)
        self.assertFalse(result["measurement_coverage"]["usage_seen"])
        self.assertIsNone(result["retrieval_events"][2]["output_sha256"])

    def test_mixed_bytes_overlap_is_disclosed(self):
        result = self.measure([tool("Get-Content src/example.py; npm test", "abc")])
        self.assertEqual(result["tool_output_bytes"], 3)
        self.assertEqual(result["whole_file_read_bytes"], 3)
        self.assertEqual(result["test_or_build_bytes"], 3)
        self.assertEqual(result["measurement_coverage"]["mixed_category_events"], 1)

    def test_wrapped_source_read_establishes_convergence_and_duplicate_identity(self):
        script = "Get-Content 'src/example.py'; Write-Output \"don't\""
        wrapped = shlex.join([r'C:\tools\pwsh.exe', '-Command', script])
        result = self.measure([tool(wrapped, 'body'), tool(script, 'body'), tool('rg needle .', 'match')])
        self.assertTrue(result['retrieval_events'][0]['project_source_read'])
        self.assertEqual(result['duplicate_command_calls'], 1)
        self.assertEqual(result['broad_calls_after_first_project_read'], 1)
        self.assertEqual(result['measurement_coverage']['shell_decode_failures'], 0)

    def test_interpolated_source_path_establishes_first_read(self):
        script = '$root=\'src\'; $p="$root/example.py"; Get-Content $p'
        result = self.measure([tool(shlex.join(['pwsh', '-Command', script]), 'body'), tool('rg needle .', 'match')])
        self.assertTrue(result['retrieval_events'][0]['project_source_read'])
        self.assertEqual(result['broad_calls_after_first_project_read'], 1)
        for unknown in ['Get-Content "$root/example.py"', '$root=\'src\'; Get-Content \'$root/example.py\'']:
            result = self.measure([tool(unknown, 'body'), tool('rg needle .', 'match')])
            self.assertFalse(result['retrieval_events'][0]['project_source_read'])
            self.assertEqual(result['broad_calls_after_first_project_read'], 0)

    def test_literal_and_array_search_scopes_require_audit_without_evaluation(self):
        for script in ['$root=\'src\'; rg needle "$root/subdir"',
                       "$roots=@('src','tests'); rg needle $roots",
                       "rg needle 'src','tests'",
                       '$root=\'src\'; $root=Get-Location; rg needle $root']:
            with self.subTest(script=script):
                result = self.measure([tool(script, 'match')])
                self.assertIn('search_scope_requires_audit', result['retrieval_events'][0]['convergence_uncertainty'])
                self.assertTrue(result['measurement_coverage']['convergence_requires_manual_audit'])
        for script in ["rg needle src", "rg needle .", "rg '$literal,pattern' src"]:
            with self.subTest(script=script):
                result = self.measure([tool(script, 'match')])
                self.assertEqual(result['retrieval_events'][0]['convergence_uncertainty'], [])
                self.assertFalse(result['measurement_coverage']['convergence_requires_manual_audit'])

    def test_failed_compound_read_keeps_observation_but_exposes_unknown_boundary(self):
        result = self.measure([tool('Get-Content src/example.py; rg absent src', 'source body', exit_code=1),
                               tool('rg needle .', '')])
        first, after = result['retrieval_events']
        self.assertFalse(first['project_source_read'])
        self.assertIn('compound_exit_status', first['convergence_uncertainty'])
        self.assertTrue(first['project_source_read_uncertain'])
        self.assertFalse(after['after_first_project_read'])
        self.assertTrue(after['after_first_project_read_uncertain'])
        self.assertTrue(after['after_project_candidate_uncertain'])
        self.assertEqual(result['broad_calls_after_first_project_read'], 0)
        self.assertTrue(result['measurement_coverage']['convergence_requires_manual_audit'])

    def test_mixed_dependency_and_unattributed_path_reads_require_audit(self):
        scripts = ['Get-Content src/example.py; Get-Content node_modules/lib/index.js',
                   "$unused='src/example.py'; Get-Content README.md",
                   'Get-Content README.md | Select-String src/example.py',
                   'Get-Content "$root/src/example.py"',
                   'Get-Content "$unknown/file.py"']
        for script in scripts:
            with self.subTest(script=script):
                result = self.measure([tool(script, 'body'), tool('rg needle .', '')])
                self.assertTrue(result['retrieval_events'][0]['project_source_read_uncertain'])
                self.assertTrue(result['retrieval_events'][1]['after_first_project_read_uncertain'])
                self.assertTrue(result['measurement_coverage']['convergence_requires_manual_audit'])
        mixed = self.measure([tool(scripts[0], 'body')])['retrieval_events'][0]
        self.assertFalse(mixed['project_source_read'])
        self.assertIn('mixed_project_dependency_read', mixed['convergence_uncertainty'])

    def test_same_event_order_is_flagged_and_later_simple_read_resolves_future_boundary(self):
        result = self.measure([tool('Get-Content src/example.py; rg needle .', 'source body'),
                               tool('Get-Content src/other.py', 'other body'),
                               tool('rg needle .', '')])
        first, second, third = result['retrieval_events']
        self.assertIn('intra_event_convergence_order', first['convergence_uncertainty'])
        self.assertFalse(first['after_first_project_read'])
        self.assertTrue(second['after_first_project_read_uncertain'])
        self.assertTrue(third['after_first_project_read'])
        self.assertFalse(third['after_first_project_read_uncertain'])
        self.assertFalse(third['after_project_candidate_uncertain'])
        self.assertEqual(result['broad_calls_after_first_project_read'], 1)
        self.assertEqual(result['measurement_coverage']['convergence_uncertain_events'], 1)

    def test_simple_success_and_failure_do_not_gain_compound_uncertainty(self):
        for exit_code in [0, 1]:
            with self.subTest(exit_code=exit_code):
                result = self.measure([tool('Get-Content src/example.py', 'body', exit_code=exit_code),
                                       tool('rg needle .', '')])
                first, after = result['retrieval_events']
                self.assertEqual(first['project_source_read'], exit_code == 0)
                self.assertFalse(first['project_source_read_uncertain'])
                self.assertFalse(after['after_first_project_read_uncertain'])
                self.assertEqual(result['retrieval_metrics_version'], '1.3')
                self.assertFalse(result['measurement_coverage']['convergence_requires_manual_audit'])
                self.assertTrue(result['measurement_coverage']['convergence_counts_are_estimates'])

    def test_uncertainty_does_not_change_recorded_bytes_or_hashes(self):
        body = '中文\nsource body\n'
        result = self.measure([tool('Get-Content src/example.py; rg absent src', body, exit_code=1)])
        event = result['retrieval_events'][0]
        self.assertEqual(result['tool_output_bytes'], len(body.encode('utf-8')))
        self.assertEqual(event['output_sha256'], metrics.digest(body.encode('utf-8')))
        self.assertTrue(event['convergence_uncertainty'])

    def test_unknown_categories_and_undecoded_commands_require_manual_audit(self):
        for command in ['python custom_reader.py', 'pwsh -Command cat src/example.py']:
            with self.subTest(command=command):
                result = self.measure([tool(command, 'body')])
                self.assertTrue(result['measurement_coverage']['convergence_requires_manual_audit'])
        undecoded = self.measure([tool('pwsh -Command cat src/example.py', 'body'), tool('rg needle .', '')])
        self.assertIn('undecoded_command', undecoded['retrieval_events'][0]['convergence_uncertainty'])
        self.assertTrue(undecoded['retrieval_events'][1]['after_first_project_read_uncertain'])

    def test_instrumentation_cannot_change_score_or_prompt(self):
        topology = tree.load_topology(tree.HERE / "tree_topology.json")
        case = tree.CASES[0]
        spec = (case["task_id"], "adaptive", 1)
        parsed = {"answer": "example", "tool_calls": 0, "tool_commands": [], "usage": {"input_tokens": 10}}
        args = argparse.Namespace(codex="codex", timeout=600, project_paths={case["repository"]: PATHS})
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            def run(*args):
                args[4].write_text("", encoding="utf-8")
                return 0, False, False, 1.0
            with patch.object(tree, "prepare_workspace"), patch.object(tree.bench, "skill_text", return_value="fixed"), \
                 patch.object(tree.bench, "resolve_codex", return_value="codex"), patch.object(tree.bench, "run_codex", side_effect=run), \
                 patch.object(tree.bench, "parse_transcript", return_value=parsed), \
                 patch.object(tree, "score_answer", return_value={"passed": True}) as scorer:
                before = tree.run_cell(spec, args, topology, {case["repository"]: root}, None, root, root / "before")
                score_args = copy.deepcopy(scorer.call_args.args[:3])
                with patch.object(tree.retrieval_metrics, "measure_transcript", return_value={}):
                    without = tree.run_cell(spec, args, topology, {case["repository"]: root}, None, root, root / "without")
                self.assertEqual({k: before[k] for k in without}, without)
                self.assertEqual(score_args, scorer.call_args.args[:3])
                prompts = list(root.rglob("prompt.txt"))
                self.assertEqual(prompts[0].read_bytes(), prompts[1].read_bytes())


class ComparisonTests(unittest.TestCase):
    def test_pairs_require_exact_identity_and_do_not_drop_zero_regressions(self):
        row = {"task_id": "ordinary", "variant": "adaptive", "repetition": 1, "tool_output_bytes": 0, "passed": True}
        changed = {**row, "tool_output_bytes": 1}
        result = analysis.compare([row], [changed], {"ordinary"})
        self.assertIsNone(result["tail"]["tool_output_bytes"]["median_ratio"])
        self.assertEqual(result["tail"]["tool_output_bytes"]["zero_baseline_increases"], 1)
        with self.assertRaises(ValueError):
            analysis.compare([row], [{**row, "repetition": 2}], set())
        with self.assertRaises(ValueError):
            analysis.compare([row, row], [row], set())


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import argparse
import copy
import json
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
            ("Get-Content src/example.py -Head 3; Get-Content src/other.py", {"whole_file_read"}),
        ]
        for command, expected in examples:
            with self.subTest(command=command):
                self.assertEqual(set(metrics.classify(command, PATHS)), expected)

    def test_shell_wrapper_is_not_a_search_scope(self):
        command = '"C:\\tools\\pwsh.exe" -Command "rg -n needle ."'
        self.assertEqual(metrics.classify(command, PATHS), ["broad_search"])

    def test_duplicate_normalization_preserves_query_semantics(self):
        self.assertEqual(metrics.normalized("rg   'a b'  src"), metrics.normalized("rg 'a b' src"))
        self.assertNotEqual(metrics.normalized("rg 'a  b' src"), metrics.normalized("rg 'a b' src"))


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

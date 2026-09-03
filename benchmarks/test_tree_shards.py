from __future__ import annotations

import json
import tempfile
import threading
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from benchmarks import tree_shards as shards
from benchmarks import tree_validation as validation


class TreeShardTests(unittest.TestCase):
    def args(self, output: Path, *, runs: int = 1, current_only: bool = True, cases: bool = False):
        argv = ["--runs", str(runs), "--output", str(output)]
        if current_only:
            argv.append("--current-only")
        if cases:
            for case in validation.CASES[:2]:
                argv.extend(["--case", case["task_id"]])
        return validation.parse_args(argv, default_workers=8)

    def fake_shard(self, command):
        self.assertEqual(command[:2], [shards.sys.executable, str(validation.HERE / "tree_validation.py")])
        args = validation.parse_args(command[2:])
        self.assertEqual(args.workers, 1)
        topology = validation.load_topology(args.topology)
        full = validation.build_specs(topology, args.runs, current_only=args.current_only, selected_cases=set(args.case))
        assigned = validation.select_shard(full, args.shard_index, args.shard_count)
        self.assertLessEqual(len(assigned), 5)
        output = args.output
        output.mkdir(parents=True)
        manifest = {key: "frozen-fixture" for key in shards.IDENTITY_FIELDS}
        manifest.update({
            "workers": 1, "repetitions": args.runs, "baseline_ref": args.baseline_ref or topology.get("baseline_ref"),
            "topology_sha256": validation.bench.sha256(args.topology),
            "file_sha256": {"tree_validation.py": "scorer-and-prompt-sha"},
            "runtime_file_sha256": {"SKILL.md": "current-sha"}, "repositories": {"fixture": {"commit": "frozen"}},
            "baseline_runtime_file_sha256": {"SKILL.md": "baseline-sha"} if not args.current_only else {},
            "baseline_bundle_sha256": "baseline-bundle" if not args.current_only else None,
            "expected_specs": full, "specs": assigned,
            "shard": {"index": args.shard_index, "count": args.shard_count, "max_cells": 5},
        })
        shards.write_json(output / "manifest.json", manifest)
        rows = []
        for task, variant, repetition in assigned:
            case = next(item for item in validation.CASES if item["task_id"] == task)
            row = {"task_id": task, "variant": variant, "repetition": repetition,
                   "repository": case["repository"], "manual_request": case.get("manual_request"),
                   "passed": False, "verdict": "fail", "duration_seconds": 999999}
            cell = output / "cells" / task / variant.replace(":", "-") / f"r{repetition:03d}"
            cell.mkdir(parents=True)
            for name in ("prompt.txt", "round1.jsonl", "round1.stderr.txt", "answer.md"):
                (cell / name).write_text("original raw fixture", encoding="utf-8")
            shards.write_json(cell / "result.json", row)
            rows.append(row)
        (output / "results.jsonl").write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
        return SimpleNamespace(returncode=0)

    def test_full_matrices_use_exact_specs_at_most_five_per_shard_and_eight_processes(self):
        for runs, current_only, cells, count in ((1, True, 54, 11), (3, False, 252, 51)):
            with self.subTest(cells=cells), tempfile.TemporaryDirectory() as temp:
                output = Path(temp) / "fresh"
                args = self.args(output, runs=runs, current_only=current_only)
                barrier = threading.Barrier(8)
                lock = threading.Lock()
                active = maximum = 0
                seen = []

                def fake_process(command, **kwargs):
                    nonlocal active, maximum
                    index = int(command[command.index("--shard-index") + 1])
                    with lock:
                        active += 1
                        maximum = max(maximum, active)
                        seen.append(index)
                    try:
                        if index < 8:
                            barrier.wait(timeout=10)
                        kwargs["stdout"].write("captured child output")
                        return self.fake_shard(command)
                    finally:
                        with lock:
                            active -= 1

                with mock.patch.object(shards.subprocess, "run", side_effect=fake_process):
                    actual_output, report = shards.launch(args)
                self.assertEqual(actual_output, output.resolve())
                self.assertEqual(maximum, 8)
                self.assertEqual(sorted(seen), list(range(count)))
                self.assertEqual(sum(arm["cells"] for arm in report["arms"].values()), cells)
                manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
                rows = [json.loads(line) for line in (output / "results.jsonl").read_text(encoding="utf-8").splitlines()]
                actual = {(row["task_id"], row["variant"], row["repetition"]) for row in rows}
                self.assertEqual(actual, {tuple(spec) for spec in manifest["specs"]})
                self.assertEqual(len(rows), cells)
                self.assertTrue(all(row["verdict"] == "fail" for row in rows))
                self.assertEqual(len(list((output / "logs").glob("*.stdout.txt"))), count)
                self.assertTrue(all(Path(row["cell_directory"]).is_dir() for row in rows))

    def test_shared_parent_exists_before_each_fresh_shard_resolves_its_path(self):
        with tempfile.TemporaryDirectory() as temp:
            args = self.args(Path(temp) / "fresh", cases=True)
            seen = []

            def fake_process(command, **kwargs):
                output = Path(command[command.index("--output") + 1])
                self.assertTrue(output.parent.is_dir())
                self.assertFalse(output.exists())
                # A concurrently created parent can make Windows resolve() retain
                # a Win32 extended prefix that git clone rejects as a destination.
                self.assertFalse(str(output.resolve()).startswith("\\\\?\\"))
                seen.append(output.name)
                return self.fake_shard(command)

            with mock.patch.object(shards.subprocess, "run", side_effect=fake_process):
                shards.launch(args)
            self.assertCountEqual(seen, ["shard-000", "shard-001"])

    def test_invalid_bounds_and_existing_output_rejected_before_process_launch(self):
        with tempfile.TemporaryDirectory() as temp, mock.patch.object(shards.subprocess, "run") as process:
            output = Path(temp)
            args = self.args(output)
            with self.assertRaises(FileExistsError):
                shards.launch(args)
            args.output = output / "fresh"
            args.workers = 9
            with self.assertRaises(ValueError):
                shards.launch(args)
            self.assertFalse(args.output.exists())
            process.assert_not_called()

    def test_original_run_cell_keeps_prompt_model_and_scorer_for_each_arm(self):
        topology = validation.load_topology(validation.HERE / "tree_topology.json")
        case = validation.CASES[0]
        answer = "Original answer\nTREE_TRACE path=core retrieval=NONE manual=none refs=none"
        parsed = {"answer": answer, "tool_commands": ["git status --short"], "tool_calls": 1,
                  "usage": {"total_tokens": 123}}
        for variant in ("no-skill", "baseline", "adaptive", "cap:core"):
            with self.subTest(variant=variant), tempfile.TemporaryDirectory() as temp:
                output = Path(temp)
                args = SimpleNamespace(codex="fake-codex", timeout=600, project_paths={case["repository"]: ["source.py"]})
                loaded = "" if variant == "no-skill" else "original Skill content"
                expected_prompt = validation.task_prompt(case, loaded, variant, topology)

                def fake_codex(command, prompt, workspace, env, stdout, stderr, timeout):
                    self.assertEqual(prompt, expected_prompt)
                    self.assertEqual(command, validation.bench.codex_command("fake-codex", workspace))
                    stdout.write_text("", encoding="utf-8")
                    stderr.write_text("", encoding="utf-8")
                    return 0, False, False, 42

                with mock.patch.object(validation, "prepare_workspace", side_effect=lambda source, commit, path: path.mkdir()), \
                        mock.patch.object(validation.bench, "skill_text", return_value=loaded), \
                        mock.patch.object(validation.bench, "resolve_codex", return_value="fake-codex"), \
                        mock.patch.object(validation.bench, "run_codex", side_effect=fake_codex), \
                        mock.patch.object(validation.bench, "parse_transcript", return_value=parsed), \
                        mock.patch.object(validation.retrieval_metrics, "measure_transcript", return_value={}), \
                        mock.patch.object(validation, "score_answer", return_value={"passed": True}) as scorer:
                    row = validation.run_cell((case["task_id"], variant, 1), args, topology,
                                              {case["repository"]: output}, output / "baseline", output / "eval", output)
                self.assertEqual(row["verdict"], "pass")
                self.assertEqual(row["total_tokens"], 123)
                call = scorer.call_args
                self.assertEqual(call.args[:3], (case, answer, parsed["tool_commands"]))
                self.assertEqual(call.kwargs["enforce_runtime_contract"], variant in {"adaptive", "cap:core"})
                self.assertEqual(next(output.rglob("prompt.txt")).read_text(encoding="utf-8"), expected_prompt)

    def test_failed_processes_are_not_retried_or_selectively_aggregated(self):
        with tempfile.TemporaryDirectory() as temp:
            args = self.args(Path(temp) / "fresh", cases=True)
            with mock.patch.object(shards.subprocess, "run", return_value=SimpleNamespace(returncode=7)) as process:
                with self.assertRaisesRegex(RuntimeError, "no retries"):
                    shards.launch(args)
            self.assertEqual(process.call_count, 2)
            self.assertFalse((args.output / "results.jsonl").exists())
            self.assertEqual(len(json.loads((args.output / "failed-shards.json").read_text())), 2)

    def fixture(self, output):
        args = self.args(output, current_only=False, cases=True)
        with mock.patch.object(shards, "aggregate", return_value={}), \
                mock.patch.object(shards.subprocess, "run", side_effect=lambda command, **kwargs: self.fake_shard(command)):
            shards.launch(args)
        return json.loads((output / "plan.json").read_text(encoding="utf-8"))

    def test_incompatible_or_missing_identities_rejected_before_publication(self):
        for field in ("model", "file_sha256", "repositories", "runtime_file_sha256", "baseline_runtime_file_sha256",
                      "baseline_bundle_sha256", "codex_sha256", "repetitions", "path_sha256", "missing-field"):
            with self.subTest(field=field), tempfile.TemporaryDirectory() as temp:
                output = Path(temp) / "fresh"
                plan = self.fixture(output)
                path = output / "shards" / "shard-001" / "manifest.json"
                manifest = json.loads(path.read_text(encoding="utf-8"))
                if field == "missing-field":
                    del manifest["file_sha256"]
                else:
                    manifest[field] = "changed"
                shards.write_json(path, manifest)
                with self.assertRaises(ValueError):
                    shards.aggregate(output, plan)
                self.assertFalse((output / "results.jsonl").exists())

    def test_missing_duplicate_unexpected_and_tampered_cells_rejected(self):
        for kind in ("missing-manifest", "shard-index", "assignment", "missing", "duplicate", "unexpected", "raw", "log"):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as temp:
                output = Path(temp) / "fresh"
                plan = self.fixture(output)
                shard = output / "shards" / "shard-000"
                rows_path = shard / "results.jsonl"
                rows = [json.loads(line) for line in rows_path.read_text().splitlines()]
                if kind == "missing-manifest":
                    (shard / "manifest.json").unlink()
                elif kind in {"shard-index", "assignment"}:
                    manifest = json.loads((shard / "manifest.json").read_text())
                    if kind == "shard-index":
                        manifest["shard"]["index"] = 1
                    else:
                        manifest["specs"].pop()
                    shards.write_json(shard / "manifest.json", manifest)
                elif kind == "missing":
                    rows.pop()
                elif kind == "duplicate":
                    rows[-1] = rows[0]
                elif kind == "unexpected":
                    rows[-1]["repetition"] = 999
                elif kind == "raw":
                    rows[0]["passed"] = True
                else:
                    next((shard / "cells").rglob("round1.jsonl")).unlink()
                rows_path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
                with self.assertRaises((ValueError, FileNotFoundError)):
                    shards.aggregate(output, plan)
                self.assertFalse((output / "manifest.json").exists())


if __name__ == "__main__":
    unittest.main()

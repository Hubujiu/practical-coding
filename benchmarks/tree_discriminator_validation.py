#!/usr/bin/env python3
"""Run cheap parent-local routing discrimination checks for staged tree children.

This suite measures whether immediate-child trigger language is discriminative before
paying for full real-repository runs. It is diagnostic only: human-authored labels
here never replace capability-ceiling evidence or deterministic task verifiers.
When the active topology has no staged children, its frozen cases are historical and
the self-test reports the suite inactive.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import datetime as dt
import json
import os
import re
import shutil
import sys
from collections import Counter
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import run_benchmarks as bench
from tree_discriminator_cases import CASES, CASE_IDS
from tree_validation import load_topology


ROUTE_RE = re.compile(r"^\s*ROUTE\s*=\s*([a-z0-9_-]+)\s*$", re.I)


def parent_prompt(case: dict[str, str], topology: dict[str, Any]) -> str:
    parent = case["parent"]
    spec = topology["automatic_nodes"][parent]
    parent_path = ROOT / spec["reference"]
    parent_text = parent_path.read_text(encoding="utf-8")
    children = list(spec.get("children", []))
    allowed = ["parent", *children]
    return (
        "This is a benchmark of one local router decision. Do not solve the coding task. "
        "Do not load any child reference or infer grandchild behavior.\n\n"
        f"<parent-node name=\"{parent}\">\n{parent_text}\n</parent-node>\n\n"
        f"<task-summary>\n{case['prompt']}\n</task-summary>\n\n"
        f"Choose exactly one of: {', '.join(allowed)}. "
        "Use parent when no immediate-child preload signal is clearly present. "
        "Return exactly ROUTE=<choice> and nothing else."
    )


def parse_route(answer: str) -> str | None:
    match = ROUTE_RE.fullmatch(answer.strip())
    return match.group(1).lower() if match else None


def prepare_workspace(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    result = bench.run_command(["git", "init", "-q"], path)
    if result.returncode:
        raise RuntimeError(result.stderr)


def build_specs(runs: int, selected: set[str]) -> list[tuple[dict[str, str], int]]:
    specs = []
    for case in CASES:
        if selected and case["case_id"] not in selected:
            continue
        for repetition in range(1, runs + 1):
            specs.append((case, repetition))
    return specs


def run_cell(
    spec: tuple[dict[str, str], int],
    args: argparse.Namespace,
    topology: dict[str, Any],
    eval_home: Path,
    output: Path,
) -> dict[str, Any]:
    case, repetition = spec
    cell = output / "cells" / case["case_id"] / f"r{repetition:03d}"
    result_path = cell / "result.json"
    if result_path.is_file():
        return json.loads(result_path.read_text(encoding="utf-8"))

    cell.mkdir(parents=True, exist_ok=True)
    workspace = cell / "workspace"
    if workspace.exists():
        shutil.rmtree(workspace)
    prepare_workspace(workspace)

    prompt = parent_prompt(case, topology)
    (cell / "prompt.txt").write_text(prompt, encoding="utf-8")
    env = os.environ.copy()
    env["CODEX_HOME"] = str(eval_home)
    codex = bench.resolve_codex(args.codex)
    stdout = cell / "round1.jsonl"
    stderr = cell / "round1.stderr.txt"
    code, timed_out, forced, duration = bench.run_codex(
        bench.codex_command(codex, workspace),
        prompt,
        workspace,
        env,
        stdout,
        stderr,
        args.timeout,
    )
    parsed = bench.parse_transcript(stdout)
    route = parse_route(parsed["answer"])
    infrastructure_error = "timeout" if timed_out else (
        f"codex exit status {code}" if code and not forced else None
    )
    passed = None if infrastructure_error else route == case["expected"]
    record = {
        "schema_version": 1,
        "case_id": case["case_id"],
        "parent": case["parent"],
        "expected": case["expected"],
        "selected": route,
        "repetition": repetition,
        "passed": passed,
        "error": infrastructure_error,
        "duration_seconds": duration,
        "tool_calls": parsed["tool_calls"],
        **parsed["usage"],
    }
    (cell / "answer.txt").write_text(parsed["answer"] + "\n", encoding="utf-8")
    result_path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return record


def ratio(numerator: int, denominator: int) -> float | None:
    return numerator / denominator if denominator else None


def summarize(rows: list[dict[str, Any]], topology: dict[str, Any], runs: int) -> dict[str, Any]:
    determinate = [row for row in rows if row.get("passed") is not None]
    per_parent: dict[str, Any] = {}
    for parent in sorted({row["parent"] for row in determinate}):
        selected = [row for row in determinate if row["parent"] == parent]
        per_parent[parent] = {
            "cells": len(selected),
            "accuracy": ratio(sum(row["passed"] is True for row in selected), len(selected)),
            "confusion": dict(sorted(Counter(
                f"{row['expected']}->{row.get('selected') or 'invalid'}" for row in selected
            ).items())),
        }

    per_child: dict[str, Any] = {}
    for parent, spec in topology["automatic_nodes"].items():
        for child in spec.get("children", []):
            positives = [row for row in determinate if row["parent"] == parent and row["expected"] == child]
            negatives = [row for row in determinate if row["parent"] == parent and row["expected"] != child]
            hits = sum(row.get("selected") == child for row in positives)
            false = sum(row.get("selected") == child for row in negatives)
            per_child[child] = {
                "parent": parent,
                "positive_cells": len(positives),
                "trigger_recall": ratio(hits, len(positives)),
                "negative_cells": len(negatives),
                "boundary_specificity": (
                    1.0 - ratio(false, len(negatives)) if negatives else None
                ),
                "false_triggers": false,
            }

    return {
        "schema_version": 1,
        "runs_per_case": runs,
        "cases": len({row["case_id"] for row in rows}),
        "determinate_cells": len(determinate),
        "overall_accuracy": ratio(sum(row["passed"] is True for row in determinate), len(determinate)),
        "per_parent": per_parent,
        "per_child": per_child,
        "note": (
            "This is a cheap router-language diagnostic with human-authored labels. "
            "It is not a release gate and does not prove child capability lift."
        ),
    }


def self_test(topology: dict[str, Any]) -> None:
    assert CASE_IDS
    case_parents = {case["parent"] for case in CASES}
    active_parents = {
        name
        for name, spec in topology["automatic_nodes"].items()
        if name in case_parents and spec.get("children")
    }
    if not active_parents:
        print("tree discriminator self-test: PASS (inactive; no staged children)")
        return
    cases = [case for case in CASES if case["parent"] in active_parents]
    assert {case["parent"] for case in cases} == active_parents
    for case in cases:
        allowed = {"parent", *topology["automatic_nodes"][case["parent"]].get("children", [])}
        assert case["expected"] in allowed
    assert parse_route("ROUTE=dynamic-evidence") == "dynamic-evidence"
    assert parse_route("something else") is None
    print("tree discriminator self-test: PASS")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument("--workers", type=int, default=3)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--topology", type=Path, default=HERE / "tree_topology.json")
    parser.add_argument("--codex", default=os.environ.get("CODEX_BIN", "codex"))
    parser.add_argument("--timeout", type=float, default=180)
    parser.add_argument("--case", action="append", default=[])
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    topology = load_topology(args.topology.resolve())
    if args.self_test:
        self_test(topology)
        return 0
    if args.runs < 1 or args.workers < 1:
        raise SystemExit("runs and workers must be positive")
    selected = set(args.case)
    unknown = selected - CASE_IDS
    if unknown:
        raise SystemExit(f"unknown cases: {', '.join(sorted(unknown))}")

    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    output = (args.output or ROOT / "benchmark-results" / f"tree-discriminator-{stamp}").resolve()
    output.mkdir(parents=True, exist_ok=True)
    eval_home = bench.prepare_eval_home(output / "eval-home")
    specs = build_specs(args.runs, selected)
    rows = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [
            pool.submit(run_cell, spec, args, topology, eval_home, output)
            for spec in specs
        ]
        for future in concurrent.futures.as_completed(futures):
            rows.append(future.result())
    rows.sort(key=lambda row: (row["case_id"], row["repetition"]))
    (output / "results.jsonl").write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )
    report = summarize(rows, topology, args.runs)
    (output / "report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

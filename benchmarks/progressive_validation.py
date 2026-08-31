#!/usr/bin/env python3
"""Run frozen real-repository held-out tasks against the active event router."""

from __future__ import annotations

import argparse
import concurrent.futures
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import statistics
import sys
import threading
import time
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import run_benchmarks as bench
from progressive_cases import CASES, REPOSITORIES


VERSION = "2.0"
MODEL = bench.MODEL
REASONING = bench.REASONING
TRACE_RE = re.compile(
    r"BENCHMARK_TRACE\s+reasoning=(NONE|DEBUGGING|DECISION|IMPLEMENTATION)\s+"
    r"retrieval=(NONE|TARGETED|BOUNDED|STRUCTURAL)\s+refs=([^\r\n]+)",
    re.I,
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def parse_trace(answer: str) -> dict[str, Any]:
    matches = list(TRACE_RE.finditer(answer))
    if not matches:
        return {"reasoning": None, "retrieval": None, "references_loaded": []}
    match = matches[-1]
    refs_raw = match.group(3).strip().strip("<>")
    refs = [] if refs_raw.lower() == "none" else [part.strip().strip("<>") for part in refs_raw.split(",") if part.strip()]
    return {
        "reasoning": match.group(1).upper(),
        "retrieval": match.group(2).upper(),
        "references_loaded": refs,
    }


def validate_trace(trace: dict[str, Any]) -> bool:
    return (
        trace["reasoning"] in {"NONE", "DEBUGGING", "DECISION", "IMPLEMENTATION"}
        and trace["retrieval"] in {"NONE", "TARGETED", "BOUNDED", "STRUCTURAL"}
    )


def score_answer(case: dict[str, Any], answer: str, commands: list[str], workspace: Path) -> dict[str, Any]:
    lower = answer.lower()
    missing = [group for group in case["required"] if not any(term.lower() in lower for term in group)]
    command_text = "\n".join(commands).lower()
    probe_groups = [group if isinstance(group, list) else [group] for group in case["probe_terms"]]
    probe_missing = [group for group in probe_groups if not any(term.lower() in command_text for term in group)]
    status = bench.run_command(["git", "status", "--porcelain"], workspace)
    clean = status.returncode == 0 and not status.stdout.strip()
    manual_markers = (
        "references/manual/clarification.md",
        "requirements interview",
        "grill me",
    )
    spontaneous_manual = any(marker in lower for marker in manual_markers)
    passed = not missing and not probe_missing and clean
    return {
        "passed": passed,
        "missing_evidence_groups": missing,
        "missing_probe_terms": probe_missing,
        "workspace_clean": clean,
        "spontaneous_manual_mode": spontaneous_manual,
    }


def resolve_repositories(repository_root: Path, overrides: list[str]) -> dict[str, Path]:
    mapped = {name: (repository_root / data["local_name"]).resolve() for name, data in REPOSITORIES.items()}
    for raw in overrides:
        if "=" not in raw:
            raise ValueError(f"repository override must be NAME=PATH: {raw}")
        name, value = raw.split("=", 1)
        if name not in REPOSITORIES:
            raise ValueError(f"unknown repository override: {name}")
        mapped[name] = Path(value).resolve()
    for name, path in mapped.items():
        commit = REPOSITORIES[name]["commit"]
        if not path.is_dir():
            raise FileNotFoundError(f"held-out repository unavailable: {name}: {path}")
        check = bench.run_command(["git", "cat-file", "-e", f"{commit}^{{commit}}"], path)
        if check.returncode:
            raise RuntimeError(f"{name} does not contain frozen commit {commit}: {check.stderr}")
    return mapped


def prepare_workspace(source: Path, commit: str, workspace: Path) -> None:
    clone = bench.run_command(["git", "clone", "-q", "--shared", "--no-checkout", str(source), str(workspace)], workspace.parent)
    if clone.returncode:
        raise RuntimeError(clone.stderr)
    configure = bench.run_command(["git", "config", "core.longpaths", "true"], workspace)
    if configure.returncode:
        raise RuntimeError(configure.stderr)
    checkout = bench.run_command(["git", "checkout", "-q", "--detach", commit], workspace)
    if checkout.returncode:
        raise RuntimeError(checkout.stderr)


def task_prompt(case: dict[str, Any], loaded: str, variant: str) -> str:
    trace = (
        "After the evidence-backed report, append exactly one final line using this benchmark-only instrumentation: "
        "BENCHMARK_TRACE reasoning=NONE retrieval=TARGETED refs=none. "
        "Replace reasoning with NONE, DEBUGGING, DECISION, or IMPLEMENTATION and retrieval with NONE, TARGETED, "
        "BOUNDED, or STRUCTURAL according to the behavior actually used. NONE means no repository source acquisition; "
        "TARGETED means only already-known paths or symbols; BOUNDED means lexical/filename/symbol search in a limited "
        "scope; STRUCTURAL means relationship/flow mapping or bounded exhaustive discovery, even when reconstructed "
        "from source because no graph index is available. List comma-separated Practical Coding "
        "reference paths after refs=. The reasoning value must be one of the four listed values; STRUCTURAL is only a "
        "retrieval value. Requirements interviewing is never a reasoning route. "
        "Do not mention this instrumentation elsewhere."
    )
    return (
        f"Frozen held-out task {case['task_id']} ({case['family']}).\n\n{case['prompt']}\n\n"
        "Use PowerShell-compatible commands. Stay within this repository and preserve a clean working tree. "
        "Cite concrete source paths/symbols and fresh command evidence.\n\n"
        f"{trace}\n\n<benchmark-variant>{variant}</benchmark-variant>\n{loaded}"
    )


def build_specs(phases: list[str], runs: int, *, current_only: bool = False) -> list[tuple[str, str, str, int]]:
    specs: list[tuple[str, str, str, int]] = []
    selected = set(phases)
    if "all" in selected:
        selected = {"heldout"}
    if "heldout" in selected:
        for case in CASES:
            variants = ("adaptive",) if current_only else ("no-skill", "previous", "adaptive")
            for variant in variants:
                for repetition in range(1, runs + 1):
                    specs.append(("heldout", case["task_id"], variant, repetition))
    return specs


def run_cell(
    spec: tuple[str, str, str, int],
    args: argparse.Namespace,
    repositories: dict[str, Path],
    previous: Path | None,
    eval_home: Path,
    output: Path,
) -> dict[str, Any]:
    phase, task_id, variant, repetition = spec
    case = next(item for item in CASES if item["task_id"] == task_id)
    cell = output / "cells" / phase / task_id / variant / f"r{repetition:03d}"
    result_path = cell / "result.json"
    if result_path.is_file():
        return json.loads(result_path.read_text(encoding="utf-8"))
    cell.mkdir(parents=True, exist_ok=True)
    workspace = cell / "workspace"
    if workspace.exists():
        shutil.rmtree(workspace)
    prepare_workspace(repositories[case["repository"]], REPOSITORIES[case["repository"]]["commit"], workspace)

    if phase == "heldout":
        if variant == "no-skill":
            loaded = ""
        elif variant == "previous":
            if previous is None:
                raise RuntimeError("previous Skill is unavailable")
            loaded = bench.skill_text("practical-previous", {}, previous)
        else:
            loaded = bench.skill_text("practical-current", {}, None)
    else:
        raise ValueError(phase)

    prompt = task_prompt(case, loaded, variant)
    (cell / "prompt.txt").write_text(prompt, encoding="utf-8")
    env = os.environ.copy()
    env["CODEX_HOME"] = str(eval_home)
    codex = bench.resolve_codex(args.codex)
    stdout = cell / "round1.jsonl"
    stderr = cell / "round1.stderr.txt"
    code, timed_out, forced, duration = bench.run_codex(
        bench.codex_command(codex, workspace), prompt, workspace, env, stdout, stderr, args.timeout
    )
    parsed = bench.parse_transcript(stdout)
    trace = parse_trace(parsed["answer"])
    trace_valid = validate_trace(trace)
    record: dict[str, Any] = {
        "phase": phase,
        "task_id": task_id,
        "repository": case["repository"],
        "family": case["family"],
        "variant": variant,
        "repetition": repetition,
        "expected_reasoning": case["expected_reasoning"],
        "expected_retrieval": case["expected_retrieval_mode"],
        "exit_status": code,
        "timed_out": timed_out,
        "forced_after_completion": forced,
        "duration_seconds": duration,
        "tool_calls": parsed["tool_calls"],
        **parsed["usage"],
        "answer": parsed["answer"],
        "tool_commands": parsed["tool_commands"],
        "selected_reasoning": trace["reasoning"],
        "selected_retrieval": trace["retrieval"],
        "references_loaded": trace["references_loaded"],
        "routing_trace_valid": trace_valid,
        "routing_exact": (
            trace_valid
            and trace["reasoning"] == case["expected_reasoning"]
            and trace["retrieval"] == case["expected_retrieval_mode"]
        ),
    }
    infrastructure_error = "timeout" if timed_out else (f"codex exit status {code}" if code and not forced else None)
    if infrastructure_error:
        record.update({"passed": None, "verdict": "indeterminate", "error": infrastructure_error})
    else:
        record.update(score_answer(case, parsed["answer"], parsed["tool_commands"], workspace))
        record["verdict"] = "pass" if record["passed"] else "fail"
    (cell / "answer.md").write_text(parsed["answer"] + "\n", encoding="utf-8")
    result_path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return record


def _mean(records: list[dict[str, Any]], key: str) -> float | None:
    values = [float(record[key]) for record in records if record.get(key) is not None]
    return statistics.mean(values) if values else None


def heldout_report(records: list[dict[str, Any]], runs: int) -> dict[str, Any]:
    rows = [record for record in records if record["phase"] == "heldout"]
    arms: dict[str, Any] = {}
    for variant in sorted({record["variant"] for record in rows}):
        selected = [record for record in rows if record["variant"] == variant]
        determinate = [record for record in selected if record["passed"] is not None]
        arms[variant] = {
            "cells": len(selected),
            "determinate": len(determinate),
            "pass_rate": sum(record["passed"] is True for record in determinate) / len(determinate) if determinate else None,
            "tokens_mean": _mean(determinate, "total_tokens"),
            "duration_seconds_mean": _mean(determinate, "duration_seconds"),
            "tool_calls_mean": _mean(determinate, "tool_calls"),
        }
    adaptive = [record for record in rows if record["variant"] == "adaptive"]
    manual_false = sum(record.get("spontaneous_manual_mode") is True for record in adaptive)
    task_pass = {
        task_id: all(record.get("passed") is True for record in adaptive if record["task_id"] == task_id)
        for task_id in sorted({record["task_id"] for record in adaptive})
    }
    return {
        "tasks": len(CASES),
        "repositories": sorted(REPOSITORIES),
        "runs_per_cell": runs,
        "arms": arms,
        "adaptive_tasks_stable_pass": sum(task_pass.values()),
        "adaptive_task_results": task_pass,
        "spontaneous_manual_mode_count": manual_false,
        "spontaneous_manual_mode_rate": manual_false / len(adaptive) if adaptive else None,
        "routing_trace_valid_rate": (
            sum(record.get("routing_trace_valid") is True for record in adaptive) / len(adaptive) if adaptive else None
        ),
        "routing_exact_rate": (
            sum(record.get("routing_exact") is True for record in adaptive) / len(adaptive) if adaptive else None
        ),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase", action="append", choices=("all", "heldout"), default=[])
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument("--workers", type=int, default=3)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--repository-root", type=Path, default=ROOT.parent)
    parser.add_argument("--repository", action="append", default=[], help="override a source as NAME=PATH")
    parser.add_argument("--baseline-ref", default="88382d2b0c00fa278067a5933bbcacc86f46b56e")
    parser.add_argument("--codex", default=os.environ.get("CODEX_BIN", "codex"))
    parser.add_argument("--timeout", type=float, default=600)
    parser.add_argument("--case", action="append", default=[])
    parser.add_argument("--current-only", action="store_true", help="run only the current adaptive arm for held-out tasks")
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def self_test() -> None:
    assert len(CASES) >= 20
    assert set(REPOSITORIES) == {case["repository"] for case in CASES}
    assert {case["expected_reasoning"] for case in CASES} == {"NONE", "DEBUGGING", "DECISION", "IMPLEMENTATION"}
    assert {case["expected_retrieval_mode"] for case in CASES} == {"TARGETED", "BOUNDED", "STRUCTURAL"}
    assert validate_trace(parse_trace("BENCHMARK_TRACE reasoning=DEBUGGING retrieval=BOUNDED refs=references/debugging.md"))
    print("progressive validation self-test: PASS")


def main() -> int:
    args = parse_args()
    if args.self_test:
        self_test()
        return 0
    if args.runs < 1 or args.workers < 1:
        raise SystemExit("runs and workers must be positive")
    phases = args.phase or ["all"]
    repositories = resolve_repositories(args.repository_root.resolve(), args.repository)
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    output = (args.output or ROOT / "benchmark-results" / f"progressive-{stamp}").resolve()
    output.mkdir(parents=True, exist_ok=True)
    previous_dir: Path | None = None
    if not args.current_only:
        previous_dir = output / "baseline-skill"
        if not (previous_dir / "SKILL.md").is_file():
            previous_dir = bench.materialize_git_skill(args.baseline_ref, previous_dir)
    eval_home = bench.prepare_eval_home(output / "eval-home")
    specs = build_specs(phases, args.runs, current_only=args.current_only)
    if args.case:
        unknown = set(args.case) - {case["task_id"] for case in CASES}
        if unknown:
            raise ValueError(f"unknown held-out cases: {sorted(unknown)}")
        specs = [spec for spec in specs if spec[1] in args.case]
    manifest = {
        "runner": "progressive_validation.py",
        "runner_version": VERSION,
        "runner_sha256": sha256(Path(__file__)),
        "cases_sha256": sha256(HERE / "progressive_cases.py"),
        "model": MODEL,
        "reasoning": REASONING,
        "runs": args.runs,
        "workers": args.workers,
        "phases": phases,
        "candidate_commit": bench.run_command(["git", "rev-parse", "HEAD"], ROOT).stdout.strip(),
        "candidate_bundle_sha256": bench.bundle_sha256(ROOT),
        "baseline_ref": args.baseline_ref,
        "current_only": args.current_only,
        "repositories": {name: {"url": data["url"], "commit": data["commit"]} for name, data in REPOSITORIES.items()},
        "task_ids": sorted({spec[1] for spec in specs}),
        "started_at": dt.datetime.now(dt.timezone.utc).isoformat(),
    }
    manifest_path = output / "manifest.json"
    if manifest_path.is_file():
        frozen = json.loads(manifest_path.read_text(encoding="utf-8"))
        for key in ("runner_sha256", "cases_sha256", "candidate_bundle_sha256", "baseline_ref", "runs", "current_only"):
            if frozen.get(key) != manifest.get(key):
                raise RuntimeError(f"resume manifest mismatch for {key}")
        manifest = frozen
    else:
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    records: list[dict[str, Any]] = []
    lock = threading.Lock()
    results_path = output / "results.json"
    print(f"running {len(specs)} progressive validation cells with {args.workers} workers", flush=True)
    started = time.monotonic()
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {
            pool.submit(run_cell, spec, args, repositories, previous_dir, eval_home, output): spec
            for spec in specs
        }
        for future in concurrent.futures.as_completed(futures):
            spec = futures[future]
            try:
                record = future.result()
            except Exception as error:
                record = {
                    "phase": spec[0], "task_id": spec[1], "variant": spec[2], "repetition": spec[3],
                    "passed": None, "verdict": "indeterminate", "error": repr(error),
                }
            with lock:
                records.append(record)
                records.sort(key=lambda item: (item["phase"], item["task_id"], item["variant"], item["repetition"]))
                results_path.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            print(
                f"[{len(records)}/{len(specs)}] {record['phase']}/{record['task_id']}/{record['variant']}/r{record['repetition']} "
                f"pass={record.get('passed')} error={record.get('error')}",
                flush=True,
            )

    elapsed = time.monotonic() - started
    selected_phases = {spec[0] for spec in specs}
    if "heldout" in selected_phases:
        (output / "heldout-report.json").write_text(json.dumps(heldout_report(records, args.runs), indent=2) + "\n", encoding="utf-8")
    manifest.update({
        "completed_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "elapsed_seconds": elapsed,
        "cells": len(records),
    })
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {output}")
    return 2 if any(record.get("verdict") == "indeterminate" for record in records) else 0


if __name__ == "__main__":
    raise SystemExit(main())

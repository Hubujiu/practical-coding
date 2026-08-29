#!/usr/bin/env python3
"""Local benchmark runner for Cursor Cloud Agent environments without Codex."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import run_catalog  # noqa: E402

run_catalog.configure()
import run_benchmarks as bench  # noqa: E402


def build_specs(args: argparse.Namespace, profile: dict[str, Any], runs: int, previous: Path | None) -> list[tuple[str, str, str, int]]:
    specs: list[tuple[str, str, str, int]] = []
    previous_arm = ["practical-previous"] if previous else []
    delivery_arms = ["practical-current", "ponytail", *previous_arm, *(["baseline"] if args.include_baseline else [])]
    for case in profile["delivery"]:
        for repetition in range(1, runs + 1):
            for arm in delivery_arms:
                specs.append(("delivery", case, arm, repetition))
    for case in profile["debug"]:
        for repetition in range(1, runs + 1):
            for arm in ["practical-current", "ponytail", *previous_arm, *(["baseline"] if args.include_baseline else [])]:
                specs.append(("debug", case, arm, repetition))
    if args.suite:
        specs = [spec for spec in specs if spec[0] in args.suite]
    if args.case:
        specs = [spec for spec in specs if spec[1] in args.case]
    if args.arm:
        specs = [spec for spec in specs if spec[2] in args.arm]
    return specs


def prepare_cell(
    spec: tuple[str, str, str, int],
    *,
    sources: dict[str, Path],
    previous: Path | None,
    ponytail: Any,
    output: Path,
    no_builds: bool,
    build_timeout: float,
) -> dict[str, Any]:
    suite, case, arm, repetition = spec
    cell = output / "cells" / suite / case / arm / f"r{repetition:03d}"
    if cell.exists():
        raise FileExistsError(f"cell already exists: {cell}")
    cell.mkdir(parents=True)
    workspace = cell / "workspace"
    workspace.mkdir()

    if suite in {"delivery", "debug"} and case in ponytail.TASKS:
        bench.prepare_upstream_workspace(case, workspace, ponytail)
        request = ponytail.TASKS[case]["prompt"]
    elif suite == "debug":
        custom = bench.CUSTOM_DEBUG[case]
        for name, content in custom["files"].items():
            (workspace / name).write_text(content, encoding="utf-8")
        bench.snapshot_workspace(workspace)
        request = custom["prompt"]
    else:
        raise ValueError(f"unsupported suite for local runner: {suite}")

    dependency_setup = None
    if suite == "delivery" and not no_builds:
        dependency_setup = bench.prepare_frontend_dependencies(case, workspace, build_timeout)

    loaded = bench.skill_text(arm, sources, previous, suite=suite)
    prompt = request + "\n\nImplement the requested change in the current workspace. Do not start long-lived services.\n" + loaded
    (cell / "prompt.txt").write_text(prompt, encoding="utf-8")
    (cell / "job.json").write_text(
        json.dumps(
            {
                "suite": suite,
                "case": case,
                "arm": arm,
                "repetition": repetition,
                "workspace": str(workspace),
                "dependency_setup": dependency_setup,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return {
        "suite": suite,
        "case": case,
        "arm": arm,
        "repetition": repetition,
        "cell": str(cell),
        "workspace": str(workspace),
        "prompt_path": str(cell / "prompt.txt"),
        "dependency_setup": dependency_setup,
    }


def score_cell(
    cell: Path,
    *,
    ponytail: Any,
    no_builds: bool,
    build_timeout: float,
    model_label: str,
    duration_seconds: float = 0.0,
) -> dict[str, Any]:
    job = json.loads((cell / "job.json").read_text(encoding="utf-8"))
    suite, case, arm, repetition = job["suite"], job["case"], job["arm"], job["repetition"]
    workspace = Path(job["workspace"])
    setup_duration = float((job.get("dependency_setup") or {}).get("duration_seconds") or 0.0)
    answer_path = cell / "answer.md"
    answer = answer_path.read_text(encoding="utf-8") if answer_path.is_file() else ""
    record: dict[str, Any] = {
        "suite": suite,
        "case": case,
        "arm": arm,
        "repetition": repetition,
        "backend": "cursor-local",
        "model": model_label,
        "duration_seconds": duration_seconds,
        "setup_duration_seconds": setup_duration,
        "tool_calls": 0,
        "input_tokens": 0,
        "cached_input_tokens": 0,
        "output_tokens": 0,
        "reasoning_output_tokens": 0,
        "uncached_input_tokens": 0,
        "total_tokens": 0,
        "workspace": str(workspace),
        "answers": [answer],
        "exit_status": 0,
        "timed_out": False,
        "forced_after_completion": False,
        "dependency_setup": job.get("dependency_setup"),
    }
    if case in ponytail.TASKS:
        scored = ponytail.score_workspace(case, arm, model_label, workspace)
    else:
        scored = bench.custom_debug_score(case, workspace)
        scored.update(ponytail.git_diff_stats(workspace))
    build = None if no_builds else bench.post_build(case, workspace, build_timeout)
    build_indeterminate = bool(build and build.get("infrastructure_error"))
    passed = None if build_indeterminate else scored.get("correct") == 1 and scored.get("safe") == 1 and (build is None or build["passed"])
    record.update(scored)
    record.update(
        {
            "build": build,
            "build_duration_seconds": build["duration_seconds"] if build else 0.0,
            "end_to_end_duration_seconds": setup_duration + duration_seconds + (build["duration_seconds"] if build else 0.0),
            "passed": passed,
        }
    )
    if build_indeterminate:
        record["indeterminate_reason"] = build["infrastructure_error"]
    record["verdict"] = "indeterminate" if record.get("passed") is None else ("pass" if record["passed"] else "fail")
    (cell / "result.json").write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return record


def finalize_run(output: Path, manifest: dict[str, Any], records: list[dict[str, Any]], elapsed: float, *, model_label: str) -> None:
    (output / "results.json").write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    summary = bench.aggregate(records)
    (output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    deltas = bench.comparisons(summary)
    rollups = bench.suite_rollups(records)
    cards = bench.scorecards(summary, rollups)
    (output / "comparisons.json").write_text(json.dumps(deltas, indent=2) + "\n", encoding="utf-8")
    (output / "rollups.json").write_text(json.dumps(rollups, indent=2) + "\n", encoding="utf-8")
    (output / "rollup-comparisons.json").write_text(json.dumps(bench.comparisons(rollups), indent=2) + "\n", encoding="utf-8")
    (output / "scorecards.json").write_text(json.dumps(cards, indent=2) + "\n", encoding="utf-8")
    bench.write_report(output / "report.md", {**manifest, "model": model_label, "reasoning": None}, summary, deltas, elapsed, rollups, bench.comparisons(rollups), cards)


def prepare_run(args: argparse.Namespace) -> tuple[Path, dict[str, Any], list[dict[str, Any]], Any, dict[str, Path], Path | None]:
    sources_root = (args.sources_root or bench.default_sources_root()).resolve()
    sources = {}
    for name in bench.SOURCES:
        candidate = sources_root / name
        if candidate.exists():
            head = bench.run_command(["git", "rev-parse", "HEAD"], candidate)
            expected = bench.SOURCES[name][1]
            if head.returncode or head.stdout.strip() != expected:
                raise RuntimeError(f"{candidate} is not pinned at {expected}")
            sources[name] = candidate
        else:
            sources[name] = bench.ensure_checkout(sources_root, name)
    ponytail = bench.load_ponytail(sources)
    bench.scorer_selftest(ponytail)
    profile = bench.PROFILE_CASES[args.profile]
    runs = args.runs or profile["runs"]
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=not args.output.exists())
    previous = None
    manifest = {
        "runner_version": bench.VERSION,
        "backend": "cursor-local",
        "model": args.model,
        "profile": args.profile,
        "runs": runs,
        "started_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "environment": {"platform": bench.platform.platform(), "python": sys.version, "cursor_agent": os.environ.get("CURSOR_AGENT", "0")},
        "skill": {
            "current_entrypoint_sha256": bench.sha256(bench.ROOT / "SKILL.md"),
            "current_bundle_sha256": bench.bundle_sha256(bench.ROOT),
        },
        "sources": {name: {"url": bench.SOURCES[name][0], "commit": bench.SOURCES[name][1], "path": str(sources[name])} for name in bench.SOURCES},
        "cases": profile,
    }
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    specs = build_specs(args, profile, runs, previous)
    if not specs:
        raise ValueError("selection produced no benchmark cells")
    prepared = [
        prepare_cell(
            spec,
            sources=sources,
            previous=previous,
            ponytail=ponytail,
            output=output,
            no_builds=args.no_builds,
            build_timeout=args.build_timeout,
        )
        for spec in specs
    ]
    (output / "prepared.json").write_text(json.dumps(prepared, indent=2) + "\n", encoding="utf-8")
    return output, manifest, prepared, ponytail, sources, previous


def read_duration_seconds(cell: Path) -> float:
    path = cell / "duration.json"
    if not path.is_file():
        return 0.0
    raw = path.read_text(encoding="utf-8").strip()
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, dict):
            for key in ("elapsed_seconds", "duration_seconds", "seconds"):
                if key in parsed:
                    return float(parsed[key])
        return float(parsed)
    except (json.JSONDecodeError, TypeError, ValueError):
        return float(raw)


def score_run(args: argparse.Namespace) -> int:
    output = args.output.resolve()
    ponytail = bench.load_ponytail(
        {
            name: Path(json.loads((output / "manifest.json").read_text(encoding="utf-8"))["sources"][name]["path"])
            for name in bench.SOURCES
        }
    )
    prepared = json.loads((output / "prepared.json").read_text(encoding="utf-8"))
    started = time.monotonic()
    records = []
    for job in prepared:
        cell = Path(job["cell"])
        duration = read_duration_seconds(cell)
        records.append(
            score_cell(
                cell,
                ponytail=ponytail,
                no_builds=args.no_builds,
                build_timeout=args.build_timeout,
                model_label=args.model,
                duration_seconds=duration,
            )
        )
    finalize_run(output, json.loads((output / "manifest.json").read_text(encoding="utf-8")), records, time.monotonic() - started, model_label=args.model)
    print(f"scored {len(records)} cells -> {output / 'report.md'}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("prepare", "score"))
    parser.add_argument("--profile", choices=bench.PROFILE_CASES, default="smoke")
    parser.add_argument("--suite", action="append", choices=("delivery", "debug"))
    parser.add_argument("--case", action="append")
    parser.add_argument("--arm", action="append")
    parser.add_argument("--runs", type=int, default=0)
    parser.add_argument("--include-baseline", action="store_true")
    parser.add_argument("--no-builds", action="store_true")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--sources-root", type=Path)
    parser.add_argument("--model", default="cursor-default")
    parser.add_argument("--build-timeout", type=float, default=600)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.command == "prepare":
        output, _, prepared, _, _, _ = prepare_run(args)
        print(f"prepared {len(prepared)} cells under {output}")
        for job in prepared:
            print(f"  {job['suite']}/{job['case']}/{job['arm']}/r{job['repetition']:03d} -> {job['workspace']}")
        return 0
    return score_run(args)


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Compare a release candidate with historical arms under the current scorers.

The model runs stay immutable. This tool reads their transcripts and workspaces,
re-scores common cases with the active catalog, and writes compact artifacts that
contain no machine-specific workspace paths.
"""

from __future__ import annotations

import argparse
import json
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Any

from benchmarks import run_benchmarks as bench
from benchmarks.case_catalog import install


ROOT = Path(__file__).resolve().parents[1]
QUALITY_KEYS = ("pass_rate", "correct_rate", "safe_rate", "build_rate")
COST_KEYS = (
    "uncached_input_tokens_median",
    "output_tokens_median",
    "total_tokens_median",
    "duration_seconds_median",
    "tool_calls_median",
    "total_loc_median",
)
PREVIOUS_ARMS = {
    "delivery": "practical-previous",
    "debug": "practical-previous",
    "decision": "practical-previous",
    "router": "practical-previous",
    "behavior": "practical-native-previous",
}
CURRENT_ARMS = {
    "delivery": "practical-current",
    "debug": "practical-current",
    "decision": "practical-current",
    "router": "practical-current",
    "behavior": "practical-native",
}
EXTERNAL_ARMS = {
    "delivery": ("baseline", "ponytail"),
    "decision": ("grilling",),
    "debug": ("superpowers",),
}


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _historical_reasoning(record: dict[str, Any]) -> tuple[str, str]:
    """Map the legacy decision/execution trace onto the active event contract."""
    if record.get("actual_reasoning"):
        return str(record["actual_reasoning"]), str(record.get("actual_retrieval") or "")
    if record.get("actual_decision") == "REQUIRED":
        reasoning = "DECISION"
    elif record.get("actual_execution") in {"DEBUGGING", "IMPLEMENTATION"}:
        reasoning = str(record["actual_execution"])
    else:
        reasoning = "NONE"
    return reasoning, str(record.get("actual_retrieval") or "")


def _decision_passed(record: dict[str, Any]) -> bool:
    answers = record.get("answers") or []
    first = bench.decision_metrics(answers[0]) if answers else bench.decision_metrics("")
    second = (
        bench.decision_metrics(answers[1])
        if len(answers) > 1
        else {"questions": 999, "recommendations": 0, "has_tradeoff": False, "attempted_implementation": False}
    )
    expected = bench.DECISION_CASES[record["case"]]["expected"]
    converged = second["questions"] == 0 and any(term in (answers[-1].lower() if answers else "") for term in expected)
    return bool(
        first["questions"] > 0
        and first["recommendations"] >= first["questions"]
        and not first["attempted_implementation"]
        and converged
        and not second["attempted_implementation"]
    )


def _behavior_passed(record: dict[str, Any]) -> bool:
    workspace = Path(record["workspace"])
    commands: list[str] = []
    outputs: list[str] = []
    for transcript in sorted(workspace.parent.glob("round*.jsonl")):
        parsed = bench.parse_transcript(transcript)
        commands.extend(parsed["tool_commands"])
        outputs.extend(parsed["tool_outputs"])
    expected = bench.BEHAVIOR_CASES[record["case"]]
    score = bench.behavior_score(
        commands,
        expected["reasoning_module"],
        outputs,
        expected["retrieval"],
        expected.get("backend"),
    )
    return bool(score["passed"])


def _workspace_score(record: dict[str, Any], ponytail: Any) -> dict[str, Any]:
    workspace = Path(record["workspace"])
    case = record["case"]
    if case in ponytail.TASKS:
        score = ponytail.score_workspace(case, record["arm"], bench.MODEL, workspace)
    else:
        score = bench.custom_debug_score(case, workspace)
    build = record.get("build")
    build_passed = None if build is None else bool(build.get("passed"))
    passed = score.get("correct") == 1 and score.get("safe") == 1 and (build_passed is not False)
    return {
        "passed": bool(passed),
        "correct": score.get("correct"),
        "safe": score.get("safe"),
        "build_passed": build_passed,
    }


def score_record(record: dict[str, Any], ponytail: Any) -> dict[str, Any]:
    suite = record["suite"]
    scored: dict[str, Any] = {"passed": None, "correct": None, "safe": None, "build_passed": None}
    if record.get("timed_out") or (record.get("exit_status") and not record.get("forced_after_completion")):
        pass
    elif suite == "router":
        expected_reasoning, expected_retrieval, _ = bench.ROUTER_CASES[record["case"]]
        reasoning, retrieval = _historical_reasoning(record)
        scored["passed"] = reasoning == expected_reasoning and retrieval == expected_retrieval
    elif suite == "decision":
        scored["passed"] = _decision_passed(record)
    elif suite == "behavior":
        scored["passed"] = _behavior_passed(record)
    else:
        scored.update(_workspace_score(record, ponytail))
    for key in (
        "uncached_input_tokens",
        "output_tokens",
        "total_tokens",
        "duration_seconds",
        "tool_calls",
        "total_loc",
    ):
        scored[key] = record.get(key)
    return scored


def aggregate(records: list[dict[str, Any]]) -> dict[str, Any]:
    determinate = [record for record in records if record["score"]["passed"] is not None]
    result: dict[str, Any] = {
        "cells": len(records),
        "determinate": len(determinate),
        "indeterminate": len(records) - len(determinate),
        "passed": sum(record["score"]["passed"] is True for record in determinate),
    }
    result["pass_rate"] = result["passed"] / len(determinate) if determinate else None
    for field in ("correct", "safe", "build_passed"):
        values = [record["score"][field] for record in determinate if record["score"][field] is not None]
        result[f"{field.removesuffix('_passed')}_rate"] = sum(value in {1, True} for value in values) / len(values) if values else None
    for field in (
        "uncached_input_tokens",
        "output_tokens",
        "total_tokens",
        "duration_seconds",
        "tool_calls",
        "total_loc",
    ):
        values = [float(record["score"][field]) for record in determinate if record["score"].get(field) is not None]
        result[f"{field}_median"] = statistics.median(values) if values else None
    return result


def _metric_gate(current: dict[str, Any], previous: dict[str, Any]) -> dict[str, Any]:
    failures: list[str] = []
    for key in QUALITY_KEYS:
        if current.get(key) is not None and previous.get(key) is not None and current[key] < previous[key]:
            failures.append(f"{key}: {current[key]:.6f} < {previous[key]:.6f}")
    for key in COST_KEYS:
        if current.get(key) is not None and previous.get(key) is not None and current[key] > previous[key]:
            failures.append(f"{key}: {current[key]:.3f} > {previous[key]:.3f}")
    return {"passed": not failures, "failures": failures}


def build_scorecard(current_dir: Path, historical_dir: Path, current_ref: str | None = None) -> dict[str, Any]:
    install(bench)
    current_manifest = _read_json(current_dir / "manifest.json")
    historical_manifest = _read_json(historical_dir / "manifest.json")
    sources = {name: Path(data["path"]) for name, data in historical_manifest["sources"].items()}
    ponytail = bench.load_ponytail(sources)
    current_rows = _read_json(current_dir / "results.json")
    historical_rows = _read_json(historical_dir / "results.json")
    current_cases = defaultdict(set)
    for row in current_rows:
        current_cases[row["suite"]].add(row["case"])

    selected: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in current_rows:
        expected_arm = CURRENT_ARMS.get(row["suite"])
        if row["arm"] == expected_arm:
            selected[(row["suite"], "current")].append({"record": row, "score": score_record(row, ponytail)})
    allowed_historical = {arm for arms in EXTERNAL_ARMS.values() for arm in arms} | set(PREVIOUS_ARMS.values())
    for row in historical_rows:
        if row["case"] not in current_cases.get(row["suite"], set()) or row["arm"] not in allowed_historical:
            continue
        label = "previous" if row["arm"] == PREVIOUS_ARMS.get(row["suite"]) else row["arm"]
        selected[(row["suite"], label)].append({"record": row, "score": score_record(row, ponytail)})

    suites: dict[str, Any] = {}
    release_failures: list[str] = []
    for suite in ("delivery", "debug", "decision", "router", "behavior"):
        arms: dict[str, Any] = {}
        for label in ("current", "previous", *EXTERNAL_ARMS.get(suite, ())):
            rows = selected.get((suite, label), [])
            if rows:
                arms[label] = aggregate(rows)
        gate = _metric_gate(arms["current"], arms["previous"])
        if not gate["passed"]:
            release_failures.extend(f"{suite}: {failure}" for failure in gate["failures"])
        suites[suite] = {"arms": arms, "current_vs_previous_gate": gate}

    return {
        "schema_version": 1,
        "model": current_manifest["model"],
        "reasoning": current_manifest["reasoning"],
        "runs": current_manifest["runs"],
        "current_candidate_ref": current_ref or current_dir.name,
        "previous_ref": historical_manifest["skill"]["previous_ref"],
        "current_results": str(current_dir.name),
        "historical_results": str(historical_dir.name),
        "scorer_contract": "active repository scorer and catalog",
        "release_gate": {"passed": not release_failures, "failures": release_failures},
        "suites": suites,
        "limitations": [
            "Model executions are cross-run; scoring is current and common-case only.",
            "Historical workspaces and transcripts are read-only and are not overwritten.",
            "Stored build outcomes are reused; model execution and builds are not rerun.",
            "External arms are contextual comparisons and do not control the current-vs-previous release gate.",
        ],
    }


def _pct(value: Any) -> str:
    return "—" if value is None else f"{100 * float(value):.1f}%"


def _num(value: Any, digits: int = 1) -> str:
    return "—" if value is None else f"{float(value):,.{digits}f}"


def render_markdown(card: dict[str, Any]) -> str:
    lines = [
        "# v1.5 unified release scorecard",
        "",
        f"Release gate: **{'PASS' if card['release_gate']['passed'] else 'FAIL'}**",
        "",
        "All rows use common cases and the active scorer. Lower token, time, tool, and LOC values are better.",
        "",
        "| Suite | Arm | Pass | Correct | Safe | Build | Uncached input median | Output median | Total tokens median | Time median | Tools median | LOC median |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for suite, data in card["suites"].items():
        for arm, row in data["arms"].items():
            lines.append(
                f"| {suite} | {arm} | {row['passed']}/{row['determinate']} ({_pct(row['pass_rate'])}) "
                f"| {_pct(row.get('correct_rate'))} | {_pct(row.get('safe_rate'))} | {_pct(row.get('build_rate'))} "
                f"| {_num(row.get('uncached_input_tokens_median'))} | {_num(row.get('output_tokens_median'))} "
                f"| {_num(row.get('total_tokens_median'))} | {_num(row.get('duration_seconds_median'))}s "
                f"| {_num(row.get('tool_calls_median'))} | {_num(row.get('total_loc_median'))} |"
            )
    lines.extend(["", "## Current vs previous gate", ""])
    for suite, data in card["suites"].items():
        gate = data["current_vs_previous_gate"]
        lines.append(f"- {suite}: **{'PASS' if gate['passed'] else 'FAIL'}**")
        lines.extend(f"  - {failure}" for failure in gate["failures"])
    lines.extend(["", "## Evidence boundary", ""])
    lines.extend(f"- {item}" for item in card["limitations"])
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--current", type=Path, required=True)
    parser.add_argument("--historical", type=Path, required=True)
    parser.add_argument("--current-ref", help="immutable commit or candidate identifier for the current run")
    parser.add_argument("--json", type=Path)
    parser.add_argument("--markdown", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    card = build_scorecard(args.current.resolve(), args.historical.resolve(), args.current_ref)
    text = render_markdown(card)
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(card, indent=2) + "\n", encoding="utf-8")
    if args.markdown:
        args.markdown.parent.mkdir(parents=True, exist_ok=True)
        args.markdown.write_text(text, encoding="utf-8")
    if not args.json and not args.markdown:
        print(text, end="")
    return 0 if card["release_gate"]["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

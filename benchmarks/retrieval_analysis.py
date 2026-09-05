#!/usr/bin/env python3
"""Derive minimum-sufficient Retrieval stages from dependency-enabled ceilings."""

from __future__ import annotations

import argparse
import json
import math
import statistics
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping

try:
    from .retrieval_integrity import IntegrityError, matrix_status
except ImportError:
    from retrieval_integrity import IntegrityError, matrix_status


STAGES = ("NONE", "R0_DIRECT", "R1_DISCOVERY", "R2_EVIDENCE", "R3_STRUCTURAL")
STAGE_INDEX = {stage: index for index, stage in enumerate(STAGES)}


def load_rows(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if line.strip():
            row = json.loads(line)
            if not isinstance(row, dict):
                raise IntegrityError(f"{path}:{number}: expected a result object")
            rows.append(row)
    return rows


def complete_determinate(records: list[dict[str, Any]], expected: set[int]) -> bool:
    repetitions = [record.get("repetition") for record in records]
    return (
        bool(expected) and all(type(rep) is int and rep > 0 for rep in repetitions)
        and len(repetitions) == len(expected) and set(repetitions) == expected
        and all(type(record.get("passed")) is bool
                and record.get("measurement_phase") == "measured"
                and record.get("setup_included_in_comparison") is False
                and record.get("measured_setup_violation") is False
                and record.get("capability_ceiling_violation") is not True
                and record.get("timed_out") is not True
                and record.get("routing_trace_valid") is not False
                and record.get("retrieval_reference_observation_ok") is not False
                for record in records)
    )


def ceiling_repetitions(task_records: list[dict[str, Any]]) -> set[int]:
    # Adaptive/comparator rows can expose a repetition missing from every ceiling.
    repetitions = [record.get("repetition") for record in task_records]
    if not repetitions or any(type(rep) is not int or rep < 1 for rep in repetitions):
        return set()
    return set(range(1, max(repetitions) + 1))


def stable_pass(
    records: Iterable[dict[str, Any]], *, expected_repetitions: set[int] | None = None,
) -> bool:
    selected = list(records)
    expected = ceiling_repetitions(selected) if expected_repetitions is None else expected_repetitions
    return complete_determinate(selected, expected) and all(record["passed"] is True for record in selected)


def minimum_stage(
    task_records: list[dict[str, Any]], expected_repetitions: set[int] | None = None,
) -> str | None:
    expected = ceiling_repetitions(task_records) if expected_repetitions is None else expected_repetitions
    for stage in STAGES:
        selected = [record for record in task_records if record.get("variant") == f"retrieval-cap:{stage}"]
        # A missing/indeterminate smaller ceiling is unknown, not evidence that it failed.
        if not complete_determinate(selected, expected):
            return None
        if all(record["passed"] is True for record in selected):
            return stage
    return None


def adaptive_relation(record: dict[str, Any], minimum: str | None, *, ceilings_complete: bool = True) -> str:
    if record.get("passed") is not True:
        return "adaptive_quality_failure"
    selected = record.get("selected_retrieval")
    if selected not in STAGE_INDEX:
        return "invalid_trace"
    if minimum is None:
        return "quality_gap" if ceilings_complete else "minimum_unresolved"
    if selected == minimum:
        return "exact_minimum"
    if STAGE_INDEX[selected] > STAGE_INDEX[minimum]:
        return "over_disclosure"
    return "under_disclosure"


def _cost(record: dict[str, Any], key: str) -> float | None:
    value = record.get(key)
    if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
        return None
    return float(value)


def _mean(records: list[dict[str, Any]], key: str) -> float | None:
    values = [_cost(record, key) for record in records]
    observed = [value for value in values if value is not None]
    return statistics.mean(observed) if observed else None


def arm_summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    determinate = [record for record in records if type(record.get("passed")) is bool]
    successes = sum(record.get("passed") is True for record in records)
    report: dict[str, Any] = {
        "cells": len(records), "determinate": len(determinate),
        "indeterminate": len(records) - len(determinate),
        "timeouts": sum(record.get("timed_out") is True for record in records),
        "pass_rate": successes / len(records) if records else None,
        "determinate_pass_rate": successes / len(determinate) if determinate else None,
        "cost_observations": {},
    }
    for key in ("total_tokens", "uncached_input_tokens", "output_tokens", "duration_seconds",
                "tool_calls", "tool_output_bytes"):
        report[key + "_mean"] = _mean(records, key)
        report["cost_observations"][key] = sum(_cost(record, key) is not None for record in records)
    report["tokens_mean"] = report["total_tokens_mean"]  # Existing runner report field.
    return report


def paired_comparison(rows: list[dict[str, Any]], comparator: str) -> dict[str, Any]:
    grouped: dict[str, dict[tuple[str, int], list[dict[str, Any]]]] = {
        "adaptive": defaultdict(list), comparator: defaultdict(list),
    }
    for row in rows:
        if row.get("variant") in grouped:
            grouped[row["variant"]][(row["task_id"], row["repetition"])].append(row)
    left, right = grouped["adaptive"], grouped[comparator]
    common = set(left) & set(right)
    pairs = [(left[key][0], right[key][0]) for key in sorted(common)
             if len(left[key]) == len(right[key]) == 1]
    qualified = [(a, b) for a, b in pairs if a.get("passed") is True and b.get("passed") is True]
    costs: dict[str, Any] = {}
    for key in ("total_tokens", "uncached_input_tokens", "duration_seconds", "tool_calls", "tool_output_bytes"):
        values = [(_cost(a, key), _cost(b, key)) for a, b in qualified]
        observed = [(a, b) for a, b in values if a is not None and b is not None]
        denominator = sum(b for _, b in observed)
        costs[key] = {
            "pairs": len(observed), "missing_pairs": len(qualified) - len(observed),
            "mean_delta": statistics.mean(a - b for a, b in observed) if observed else None,
            "ratio_of_sums": sum(a for a, _ in observed) / denominator if denominator else None,
        }
    return {
        "matched_pairs": len(pairs), "unmatched_cells": len(set(left) ^ set(right)),
        "ambiguous_pairs": len(common) - len(pairs),
        "indeterminate_pairs": sum(a.get("passed") is None or b.get("passed") is None for a, b in pairs),
        "adaptive_only_pass": sum(a.get("passed") is True and b.get("passed") is False for a, b in pairs),
        "comparator_only_pass": sum(b.get("passed") is True and a.get("passed") is False for a, b in pairs),
        "joint_passes": len(qualified),
        "costs_on_joint_passes": costs,
    }


def analyze(rows: list[dict[str, Any]], plan: Mapping[str, Any] | None = None) -> dict[str, Any]:
    matrix = matrix_status(rows, plan)
    measured = [row for row in rows if row.get("measurement_phase") == "measured"]
    by_task: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in measured:
        by_task[row["task_id"]].append(row)

    tasks: dict[str, Any] = {}
    minimum_counts: Counter[str] = Counter()
    relation_counts: Counter[str] = Counter()
    provider_by_stage: dict[str, Counter[str]] = {stage: Counter() for stage in STAGES}

    for task_id, records in sorted(by_task.items()):
        ordinary = not any(record.get("manual_request") for record in records)
        expected_repetitions = ceiling_repetitions(records) if ordinary else set()
        if plan is not None and ordinary:
            expected_repetitions = {spec[2] for spec in plan["specs"] if spec[0] == task_id}
        minimum = minimum_stage(records, expected_repetitions) if ordinary else None
        if matrix["identity_mismatch_row_indices"]:
            minimum = None
        if minimum is not None:
            minimum_counts[minimum] += 1
        adaptive = [record for record in records if record.get("variant") == "adaptive"]
        ceilings_complete = ordinary and all(
            complete_determinate([row for row in records if row["variant"] == f"retrieval-cap:{stage}"],
                                 expected_repetitions) for stage in STAGES
        )
        relations = [adaptive_relation(record, minimum, ceilings_complete=ceilings_complete)
                     for record in adaptive] if ordinary else []
        relation_counts.update(relations)
        for record in adaptive:
            selected = record.get("selected_retrieval")
            if selected in provider_by_stage:
                for provider, used in record.get("capability_usage", {}).items():
                    if used:
                        provider_by_stage[selected][provider] += 1
        tasks[task_id] = {
            "manual": not ordinary,
            "minimum_sufficient_retrieval_stage": minimum,
            "stable_ceiling_pass": {
                stage: stable_pass(
                    (record for record in records if record.get("variant") == f"retrieval-cap:{stage}"),
                    expected_repetitions=expected_repetitions,
                )
                for stage in STAGES
            }
            if ordinary
            else {},
            "adaptive": [
                {
                    "repetition": record.get("repetition"),
                    "passed": record.get("passed"),
                    "selected_retrieval": record.get("selected_retrieval"),
                    "relation": relation,
                    "capability_usage": record.get("capability_usage", {}),
                    "total_tokens": record.get("total_tokens"),
                    "duration_seconds": record.get("duration_seconds"),
                    "tool_calls": record.get("tool_calls"),
                }
                for record, relation in zip(adaptive, relations or [None] * len(adaptive))
            ],
        }

    arms = {
        variant: arm_summary([record for record in measured if record["variant"] == variant])
        for variant in sorted({record["variant"] for record in measured})
    }

    setup_leak_count = sum(
        record.get("setup_included_in_comparison") is not False
        or record.get("measurement_phase") != "measured"
        or record.get("measured_setup_violation") is True
        for record in rows
    )
    return {
        "schema_version": "2.0",
        "matrix": matrix,
        "comparison_evidence_complete": matrix["complete"],
        "paired_comparisons": {
            arm: paired_comparison(measured, arm) for arm in ("baseline", "no-skill")
            if any(record["variant"] == arm for record in measured)
        },
        "stages": list(STAGES),
        "measured_rows": len(measured),
        "tasks": tasks,
        "minimum_stage_counts": dict(minimum_counts),
        "adaptive_relation_counts": dict(relation_counts),
        "provider_usage_by_selected_stage": {
            stage: dict(counter) for stage, counter in provider_by_stage.items()
        },
        "arms": arms,
        "setup_measurement_contract_violation_count": setup_leak_count,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("results", type=Path, nargs="?")
    parser.add_argument("--plan", type=Path, help="defaults to run-plan.json beside results")
    parser.add_argument("--require-complete", action="store_true", help="fail on missing, duplicate, stale, or indeterminate cells")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def self_test() -> None:
    rows: list[dict[str, Any]] = []
    for stage in STAGES:
        rows.append(
            {
                "task_id": "task",
                "variant": f"retrieval-cap:{stage}",
                "repetition": 1,
                "passed": STAGE_INDEX[stage] >= STAGE_INDEX["R1_DISCOVERY"],
                "measurement_phase": "measured",
                "setup_included_in_comparison": False,
                "measured_setup_violation": False,
            }
        )
    rows.append(
        {
            "task_id": "task",
            "variant": "adaptive",
            "repetition": 1,
            "passed": True,
            "selected_retrieval": "R2_EVIDENCE",
            "capability_usage": {"zvec-grep": True},
            "measurement_phase": "measured",
            "setup_included_in_comparison": False,
            "measured_setup_violation": False,
        }
    )
    report = analyze(rows)
    assert report["tasks"]["task"]["minimum_sufficient_retrieval_stage"] == "R1_DISCOVERY"
    assert report["adaptive_relation_counts"]["over_disclosure"] == 1
    assert report["setup_measurement_contract_violation_count"] == 0
    print("retrieval analysis self-test: PASS")


def main() -> int:
    args = parse_args()
    if args.self_test:
        self_test()
        return 0
    if args.results is None:
        raise SystemExit("results is required unless --self-test is used")
    rows = load_rows(args.results)
    plan_path = args.plan or args.results.parent / "run-plan.json"
    if args.plan is not None and not plan_path.is_file():
        raise SystemExit(f"run plan not found: {plan_path}")
    plan = json.loads(plan_path.read_text(encoding="utf-8")) if plan_path.is_file() else None
    report = analyze(rows, plan)
    value = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(value, encoding="utf-8")
    print(value, end="")
    return 2 if args.require_complete and not report["matrix"]["complete"] else 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (IntegrityError, ValueError, OSError) as exc:
        raise SystemExit(f"retrieval analysis failed: {exc}") from exc

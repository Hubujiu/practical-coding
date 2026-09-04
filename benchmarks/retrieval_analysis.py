#!/usr/bin/env python3
"""Derive minimum-sufficient Retrieval stages from dependency-enabled ceilings."""

from __future__ import annotations

import argparse
import json
import statistics
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable


STAGES = ("NONE", "R0_DIRECT", "R1_DISCOVERY", "R2_EVIDENCE", "R3_STRUCTURAL")
STAGE_INDEX = {stage: index for index, stage in enumerate(STAGES)}


def load_rows(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def stable_pass(
    records: Iterable[dict[str, Any]],
    *,
    expected_repetitions: set[int] | None = None,
) -> bool:
    selected = list(records)
    repetitions = [int(record.get("repetition", 0)) for record in selected]
    if expected_repetitions is not None:
        if set(repetitions) != expected_repetitions or len(repetitions) != len(expected_repetitions):
            return False
    determinate = [record for record in selected if record.get("passed") is not None]
    return bool(selected) and len(determinate) == len(selected) and all(record.get("passed") is True for record in determinate)


def ceiling_repetitions(task_records: list[dict[str, Any]]) -> set[int]:
    return {
        int(record.get("repetition", 0))
        for record in task_records
        if str(record.get("variant", "")).startswith("retrieval-cap:")
    }


def minimum_stage(task_records: list[dict[str, Any]]) -> str | None:
    expected_repetitions = ceiling_repetitions(task_records)
    for stage in STAGES:
        variant = f"retrieval-cap:{stage}"
        if stable_pass(
            (record for record in task_records if record.get("variant") == variant),
            expected_repetitions=expected_repetitions,
        ):
            return stage
    return None


def adaptive_relation(record: dict[str, Any], minimum: str | None) -> str:
    if record.get("passed") is not True:
        return "adaptive_quality_failure"
    selected = record.get("selected_retrieval")
    if selected not in STAGE_INDEX:
        return "invalid_trace"
    if minimum is None:
        return "quality_gap"
    if selected == minimum:
        return "exact_minimum"
    if STAGE_INDEX[selected] > STAGE_INDEX[minimum]:
        return "over_disclosure"
    return "under_disclosure"


def _mean(records: list[dict[str, Any]], key: str) -> float | None:
    values = [float(record[key]) for record in records if record.get(key) is not None]
    return statistics.mean(values) if values else None


def analyze(rows: list[dict[str, Any]]) -> dict[str, Any]:
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
        minimum = minimum_stage(records) if ordinary else None
        if minimum is not None:
            minimum_counts[minimum] += 1
        adaptive = [record for record in records if record.get("variant") == "adaptive"]
        relations = [adaptive_relation(record, minimum) for record in adaptive] if ordinary else []
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

    arms: dict[str, Any] = {}
    for variant in sorted({record["variant"] for record in measured}):
        selected = [record for record in measured if record["variant"] == variant]
        determinate = [record for record in selected if record.get("passed") is not None]
        arms[variant] = {
            "cells": len(selected),
            "determinate": len(determinate),
            "pass_rate": sum(record.get("passed") is True for record in determinate) / len(determinate)
            if determinate
            else None,
            "total_tokens_mean": _mean(determinate, "total_tokens"),
            "duration_seconds_mean": _mean(determinate, "duration_seconds"),
            "tool_calls_mean": _mean(determinate, "tool_calls"),
        }

    setup_leak_count = sum(
        record.get("setup_included_in_comparison") is not False
        or record.get("measurement_phase") != "measured"
        or record.get("measured_setup_violation") is True
        for record in rows
    )
    return {
        "schema_version": "1.0",
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
    parser.add_argument("results", type=Path)
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
    rows = load_rows(args.results)
    report = analyze(rows)
    value = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(value, encoding="utf-8")
    print(value, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Analyze aggregated progressive-ladder calibration observations.

Input is JSONL with one aggregated row per task/axis/arm/level. See
benchmarks/LADDER_EVOLUTION.md for the protocol and schema.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean
from typing import Any, Iterable

LEVELS = {
    "execution": ["E0", "E1", "E2", "E3"],
    "retrieval": ["R0", "R1", "R2", "R3", "R4"],
}
COST_FIELDS = ("tokens", "duration_seconds", "tool_calls")


def _rank(axis: str, level: str) -> int:
    try:
        return LEVELS[axis].index(level)
    except (KeyError, ValueError) as exc:
        raise ValueError(f"invalid level {level!r} for axis {axis!r}") from exc


def validate_record(record: dict[str, Any]) -> None:
    required = {"task_id", "axis", "arm", "level", "qualified"}
    missing = sorted(required - record.keys())
    if missing:
        raise ValueError(f"missing fields: {', '.join(missing)}")
    axis = record["axis"]
    if axis not in LEVELS:
        raise ValueError(f"invalid axis: {axis!r}")
    _rank(axis, record["level"])
    if record["arm"] not in {"cap", "adaptive"}:
        raise ValueError(f"invalid arm: {record['arm']!r}")
    if not isinstance(record["qualified"], bool):
        raise ValueError("qualified must be boolean")


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, raw in enumerate(handle, 1):
            line = raw.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_number}: invalid JSON: {exc}") from exc
            validate_record(record)
            records.append(record)
    return records


def _average_costs(rows: Iterable[dict[str, Any]]) -> dict[str, float]:
    rows = list(rows)
    result: dict[str, float] = {}
    for field in COST_FIELDS:
        values = [float(row[field]) for row in rows if row.get(field) is not None]
        if values:
            result[field] = mean(values)
    return result


def analyze(records: Iterable[dict[str, Any]]) -> dict[str, Any]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    all_records = list(records)
    for record in all_records:
        validate_record(record)
        grouped[(str(record["task_id"]), str(record["axis"]))].append(record)

    axis_reports: dict[str, Any] = {}

    for axis, levels in LEVELS.items():
        statuses: Counter[str] = Counter()
        minimum_counts: Counter[str] = Counter()
        cases: list[dict[str, Any]] = []

        for (task_id, case_axis), rows in sorted(grouped.items()):
            if case_axis != axis:
                continue

            cap_rows = [row for row in rows if row["arm"] == "cap"]
            adaptive_rows = [row for row in rows if row["arm"] == "adaptive"]

            passing_caps = sorted(
                (row for row in cap_rows if row["qualified"]),
                key=lambda row: _rank(axis, row["level"]),
            )
            minimum = passing_caps[0]["level"] if passing_caps else None
            if minimum is not None:
                minimum_counts[minimum] += 1

            if len(adaptive_rows) != 1 or minimum is None:
                status = "unscored"
                adaptive_level = adaptive_rows[0]["level"] if len(adaptive_rows) == 1 else None
                adaptive_qualified = adaptive_rows[0]["qualified"] if len(adaptive_rows) == 1 else None
            else:
                adaptive = adaptive_rows[0]
                adaptive_level = adaptive["level"]
                adaptive_qualified = adaptive["qualified"]
                adaptive_rank = _rank(axis, adaptive_level)
                minimum_rank = _rank(axis, minimum)

                if adaptive_qualified and adaptive_rank == minimum_rank:
                    status = "exact"
                elif adaptive_qualified and adaptive_rank > minimum_rank:
                    status = "over_escalation"
                elif (not adaptive_qualified) and adaptive_rank < minimum_rank:
                    status = "under_escalation"
                elif (not adaptive_qualified) and adaptive_rank >= minimum_rank:
                    status = "quality_failure"
                else:
                    status = "inconsistent"

            statuses[status] += 1
            cases.append(
                {
                    "task_id": task_id,
                    "minimum_sufficient": minimum,
                    "adaptive_level": adaptive_level,
                    "adaptive_qualified": adaptive_qualified,
                    "status": status,
                }
            )

        scorable = statuses["exact"] + statuses["over_escalation"] + statuses["under_escalation"] + statuses["quality_failure"] + statuses["inconsistent"]
        exact_or_over_under = statuses["exact"] + statuses["over_escalation"] + statuses["under_escalation"]

        cost_by_level: dict[str, Any] = {}
        for level in levels:
            rows = [
                row
                for row in all_records
                if row["axis"] == axis and row["arm"] == "cap" and row["level"] == level and row["qualified"]
            ]
            if rows:
                cost_by_level[level] = _average_costs(rows)

        axis_reports[axis] = {
            "tasks_seen": sum(1 for _, case_axis in grouped if case_axis == axis),
            "scorable_tasks": scorable,
            "status_counts": dict(sorted(statuses.items())),
            "over_escalation_rate": (statuses["over_escalation"] / exact_or_over_under) if exact_or_over_under else None,
            "under_escalation_rate": (statuses["under_escalation"] / exact_or_over_under) if exact_or_over_under else None,
            "exact_rate": (statuses["exact"] / exact_or_over_under) if exact_or_over_under else None,
            "minimum_sufficient_counts": {level: minimum_counts[level] for level in levels},
            "levels_never_minimum": [level for level in levels if minimum_counts[level] == 0],
            "qualified_cap_cost_by_level": cost_by_level,
            "cases": cases,
        }

    return {"axes": axis_reports}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("observations", type=Path, help="aggregated JSONL observations")
    parser.add_argument("--output", type=Path, help="optional JSON output path")
    args = parser.parse_args()

    report = analyze(load_jsonl(args.observations))
    text = json.dumps(report, indent=2, sort_keys=True)
    if args.output:
        args.output.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

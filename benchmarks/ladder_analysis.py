#!/usr/bin/env python3
"""Analyze aggregated progressive-depth calibration observations.

Input is JSONL with one aggregated row per task/axis/arm/level. Optional
adaptive routing fields are summarized to support capability-tree tuning.
See benchmarks/LADDER_EVOLUTION.md.
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
    "retrieval": ["R0", "R1", "R2", "R3"],
}
COST_FIELDS = ("tokens", "duration_seconds", "tool_calls")


def _rank(axis: str, level: str) -> int:
    try:
        return LEVELS[axis].index(level)
    except (KeyError, ValueError) as exc:
        raise ValueError(f"invalid level {level!r} for axis {axis!r}") from exc


def _normalize_path(value: Any) -> tuple[str, ...] | None:
    if value is None:
        return None
    if isinstance(value, str):
        parts = [part.strip() for part in value.replace("/", ">").split(">") if part.strip()]
    elif isinstance(value, list) and all(isinstance(part, str) for part in value):
        parts = [part.strip() for part in value if part.strip()]
    else:
        raise ValueError("capability_path must be a string, string list, or null")
    return tuple(parts) if parts else None


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
    _normalize_path(record.get("capability_path"))
    refs = record.get("references_loaded")
    if refs is not None and (not isinstance(refs, list) or not all(isinstance(item, str) for item in refs)):
        raise ValueError("references_loaded must be a string list or null")


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
            try:
                validate_record(record)
            except ValueError as exc:
                raise ValueError(f"{path}:{line_number}: {exc}") from exc
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
        adaptive_paths: Counter[str] = Counter()
        qualified_adaptive_paths: Counter[str] = Counter()
        reference_loads: Counter[str] = Counter()
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

            adaptive_path = None
            refs: list[str] = []
            if len(adaptive_rows) == 1:
                path = _normalize_path(adaptive_rows[0].get("capability_path"))
                if path:
                    adaptive_path = ">".join(path)
                    adaptive_paths[adaptive_path] += 1
                    if adaptive_rows[0]["qualified"]:
                        qualified_adaptive_paths[adaptive_path] += 1
                refs = list(adaptive_rows[0].get("references_loaded") or [])
                reference_loads.update(refs)

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
            cases.append({
                "task_id": task_id,
                "minimum_sufficient": minimum,
                "adaptive_level": adaptive_level,
                "adaptive_qualified": adaptive_qualified,
                "adaptive_capability_path": adaptive_path,
                "references_loaded": refs,
                "status": status,
            })

        scorable = sum(statuses[name] for name in ("exact", "over_escalation", "under_escalation", "quality_failure", "inconsistent"))
        exact_or_over_under = statuses["exact"] + statuses["over_escalation"] + statuses["under_escalation"]
        qualified_adaptive = statuses["exact"] + statuses["over_escalation"]

        cost_by_level: dict[str, Any] = {}
        for level in levels:
            rows = [row for row in all_records if row["axis"] == axis and row["arm"] == "cap" and row["level"] == level and row["qualified"]]
            if rows:
                cost_by_level[level] = _average_costs(rows)

        axis_reports[axis] = {
            "tasks_seen": sum(1 for _, case_axis in grouped if case_axis == axis),
            "scorable_tasks": scorable,
            "status_counts": dict(sorted(statuses.items())),
            "qualified_adaptive_rate": (qualified_adaptive / scorable) if scorable else None,
            "overall_exact_rate": (statuses["exact"] / scorable) if scorable else None,
            "quality_failure_rate": (statuses["quality_failure"] / scorable) if scorable else None,
            "inconsistent_rate": (statuses["inconsistent"] / scorable) if scorable else None,
            "over_escalation_rate": (statuses["over_escalation"] / exact_or_over_under) if exact_or_over_under else None,
            "under_escalation_rate": (statuses["under_escalation"] / exact_or_over_under) if exact_or_over_under else None,
            # Conditional routing rate retained for compatibility. It excludes
            # quality failures and inconsistent rows; use overall_exact_rate
            # for the end-to-end adaptive result.
            "exact_rate": (statuses["exact"] / exact_or_over_under) if exact_or_over_under else None,
            "minimum_sufficient_counts": {level: minimum_counts[level] for level in levels},
            "levels_never_minimum": [level for level in levels if minimum_counts[level] == 0],
            "qualified_cap_cost_by_level": cost_by_level,
            "adaptive_capability_path_counts": dict(sorted(adaptive_paths.items())),
            "qualified_adaptive_capability_path_counts": dict(sorted(qualified_adaptive_paths.items())),
            "adaptive_reference_load_counts": dict(sorted(reference_loads.items())),
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

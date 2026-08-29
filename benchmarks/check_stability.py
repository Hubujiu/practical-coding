#!/usr/bin/env python3
"""Gate benchmark reports that are presented as stable rankings."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

MIN_STABLE_RUNS = 3


def load_run(run_dir: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    manifest_path = run_dir / "manifest.json"
    results_path = run_dir / "results.json"
    if not manifest_path.is_file() or not results_path.is_file():
        raise ValueError("run directory must contain manifest.json and results.json")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    results = json.loads(results_path.read_text(encoding="utf-8"))
    if not isinstance(manifest, dict) or not isinstance(results, list):
        raise ValueError("invalid benchmark manifest/results format")
    return manifest, results


def stability_rows(
    records: list[dict[str, Any]],
    *,
    min_runs: int = MIN_STABLE_RUNS,
    suites: set[str] | None = None,
) -> list[dict[str, Any]]:
    if min_runs < 1:
        raise ValueError("min_runs must be positive")

    groups: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        suite = record.get("suite")
        if suites and suite not in suites:
            continue
        groups[(str(suite), str(record.get("case")), str(record.get("arm")))].append(record)

    rows: list[dict[str, Any]] = []
    for (suite, case, arm), cells in sorted(groups.items()):
        repetitions = [cell.get("repetition") for cell in cells]
        valid_repetitions = [rep for rep in repetitions if isinstance(rep, int) and rep > 0]
        unique_repetitions = set(valid_repetitions)
        duplicate_repetitions = len(unique_repetitions) != len(valid_repetitions)
        invalid_repetitions = len(valid_repetitions) != len(repetitions)
        infrastructure_errors = sum(bool(cell.get("error")) or cell.get("verdict") == "indeterminate" for cell in cells)
        stable = (
            len(unique_repetitions) >= min_runs
            and not duplicate_repetitions
            and not invalid_repetitions
            and infrastructure_errors == 0
        )
        rows.append(
            {
                "suite": suite,
                "case": case,
                "arm": arm,
                "runs": len(unique_repetitions),
                "records": len(cells),
                "infrastructure_errors": infrastructure_errors,
                "duplicate_repetitions": duplicate_repetitions,
                "invalid_repetitions": invalid_repetitions,
                "stable": stable,
            }
        )
    return rows


def assess_run(
    manifest: dict[str, Any],
    records: list[dict[str, Any]],
    *,
    min_runs: int = MIN_STABLE_RUNS,
    suites: set[str] | None = None,
) -> tuple[bool, list[str], list[dict[str, Any]]]:
    reasons: list[str] = []
    if not manifest.get("completed_at"):
        reasons.append("run is incomplete: manifest has no completed_at")

    expected_cells = manifest.get("cells")
    if isinstance(expected_cells, int) and expected_cells != len(records):
        reasons.append(f"manifest cells={expected_cells}, results records={len(records)}")

    rows = stability_rows(records, min_runs=min_runs, suites=suites)
    if not rows:
        reasons.append("no benchmark cells match the selected suites")
    for row in rows:
        if row["runs"] < min_runs:
            reasons.append(
                f"{row['suite']}/{row['case']}/{row['arm']} has n={row['runs']} < {min_runs}"
            )
        if row["duplicate_repetitions"]:
            reasons.append(
                f"{row['suite']}/{row['case']}/{row['arm']} contains duplicate repetitions"
            )
        if row["invalid_repetitions"]:
            reasons.append(
                f"{row['suite']}/{row['case']}/{row['arm']} contains invalid repetition ids"
            )
        if row["infrastructure_errors"]:
            reasons.append(
                f"{row['suite']}/{row['case']}/{row['arm']} has "
                f"{row['infrastructure_errors']} infrastructure error(s)"
            )

    return not reasons, reasons, rows


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Require repeated, complete benchmark evidence before calling a result a stable ranking."
    )
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--suite", action="append", help="limit the gate to one or more suites")
    parser.add_argument("--min-runs", type=int, default=MIN_STABLE_RUNS)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.min_runs < 1:
        raise SystemExit("--min-runs must be positive")
    try:
        manifest, records = load_run(args.run_dir.resolve())
        stable, reasons, rows = assess_run(
            manifest,
            records,
            min_runs=args.min_runs,
            suites=set(args.suite) if args.suite else None,
        )
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"INVALID: {error}")
        return 1

    status = "STABLE" if stable else "PROVISIONAL"
    print(f"{status}: minimum n={args.min_runs}")
    for row in rows:
        marker = "ok" if row["stable"] else "not-stable"
        print(
            f"- {marker}: {row['suite']}/{row['case']}/{row['arm']} "
            f"n={row['runs']} errors={row['infrastructure_errors']}"
        )
    if reasons:
        print("Reasons:")
        for reason in reasons:
            print(f"- {reason}")
    return 0 if stable else 2


if __name__ == "__main__":
    raise SystemExit(main())

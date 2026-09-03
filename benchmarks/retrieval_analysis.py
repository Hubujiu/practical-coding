#!/usr/bin/env python3
"""Rank recorded retrieval costs and compare exact task/variant/repetition pairs."""
from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path

METRICS = ("tool_output_bytes", "broad_calls_after_first_project_read", "duplicate_command_calls",
           "whole_file_read_bytes", "dependency_source_bytes", "outputs_over_64k", "input_tokens",
           "cached_input_tokens", "uncached_input_tokens", "output_tokens", "tool_calls", "duration_seconds")


def read_rows(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def key(row: dict) -> tuple:
    return row["task_id"], row["variant"], row["repetition"]


def summarize(rows: list[dict]) -> dict:
    ordinary = [r for r in rows if r["variant"] == "adaptive" and not r.get("manual_request")]
    ranked = sorted(ordinary, key=lambda r: r.get("tool_output_bytes", -1), reverse=True)
    return {
        "cells": len(rows), "determinate": sum(r.get("passed") is not None for r in rows),
        "measured_cells": sum("measurement_coverage" in r for r in rows),
        "ranking": [{"task_id": r["task_id"], "repetition": r["repetition"], "passed": r.get("passed"),
                     **{m: r.get(m) for m in METRICS}, "measurement_coverage": r.get("measurement_coverage")}
                    for r in ranked],
    }


def compare(baseline: list[dict], candidate: list[dict], tail: set[str]) -> dict:
    before = {key(r): r for r in baseline}
    after = {key(r): r for r in candidate}
    if len(before) != len(baseline) or len(after) != len(candidate) or before.keys() != after.keys():
        raise ValueError("pair identity mismatch or duplicate cells")
    result = {}
    for scope in ("all", "tail"):
        pairs = [(before[k], after[k]) for k in before if scope == "all" or
                 (k[0] in tail and k[1] == "adaptive")]
        metrics = {}
        for metric in METRICS:
            observed = [(a.get(metric), b.get(metric)) for a, b in pairs]
            valid = [(a, b) for a, b in observed if isinstance(a, (int, float)) and isinstance(b, (int, float))]
            ratios = [b / a if a else (1.0 if not b else None) for a, b in valid]
            metrics[metric] = {
                "paired_cells": len(valid), "missing_cells": len(pairs) - len(valid),
                "zero_baseline_increases": sum(r is None for r in ratios),
                "median_ratio": statistics.median(ratios) if ratios and None not in ratios else None,
                "baseline_sum": sum(a for a, _ in valid), "candidate_sum": sum(b for _, b in valid),
            }
        result[scope] = metrics
    result["quality_regressions"] = [list(k) for k in before if before[k].get("passed") is True and after[k].get("passed") is not True]
    result["indeterminate"] = [list(k) for k in before if before[k].get("passed") is None or after[k].get("passed") is None]
    result["note"] = "Descriptive only. Freeze tail and verify manifests/coverage/trace/manual gates before interpretation."
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("results", nargs="?", type=Path)
    parser.add_argument("--baseline", type=Path)
    parser.add_argument("--candidate", type=Path)
    parser.add_argument("--tail-case", action="append", default=[])
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if args.baseline and args.candidate:
        report = compare(read_rows(args.baseline), read_rows(args.candidate), set(args.tail_case))
    elif args.results:
        report = summarize(read_rows(args.results))
    else:
        parser.error("provide results or both --baseline and --candidate")
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "retrieval-analysis.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "cells": report.get("cells"), "determinate": report.get("determinate")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

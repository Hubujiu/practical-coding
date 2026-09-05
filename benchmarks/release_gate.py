#!/usr/bin/env python3
"""Check the frozen 207-cell engineering gate; no measurements means not_run."""
from __future__ import annotations

import argparse
import json
import math
import tempfile
from pathlib import Path
from typing import Any

try:
    from . import delivery_cases, measured_transcript, retrieval_analysis as analysis
    from . import retrieval_integrity as integrity
    from .tree_cases import CASES as SOURCE_CASES
    from .retrieval_prompt import _cell_path
except ImportError:
    import delivery_cases, measured_transcript
    import retrieval_analysis as analysis
    import retrieval_integrity as integrity
    from tree_cases import CASES as SOURCE_CASES
    from retrieval_prompt import _cell_path

ROOT = Path(__file__).resolve().parents[1]
TARGET_PATH = Path(__file__).with_name("release_targets.json")
COSTS = ("uncached_input_tokens", "duration_seconds", "tool_calls")


def load_run(directory: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    plan = json.loads((directory / "run-plan.json").read_text(encoding="utf-8"))
    rows = analysis.load_rows(directory / "results.jsonl")
    integrity.verify_plan(plan)
    for row in rows:
        spec = (row["task_id"], row["variant"], row["repetition"])
        if list(spec) not in plan["specs"]:
            raise integrity.IntegrityError("unplanned result identity")
        # File paths come from the frozen local task catalog, not arbitrary rows.
        allowed = {case["task_id"] for case in SOURCE_CASES + delivery_cases.CASES}
        if spec[0] not in allowed or spec[1] not in {"adaptive", "baseline", "no-skill"} or type(spec[2]) is not int:
            raise integrity.IntegrityError("invalid release cell identity")
        cell = _cell_path(directory, spec)
        if json.loads((cell / "result.json").read_text(encoding="utf-8")) != row:
            raise integrity.IntegrityError("aggregate differs from its cell result")
        setup = json.loads((cell / "capability-setup.json").read_text(encoding="utf-8"))
        integrity.validate_cached_result(row, setup, plan, spec, integrity.digest(plan["manifest"]), cell_dir=cell)
        parsed = measured_transcript.parse_transcript(cell / "round1.jsonl")
        if any(row.get(key) != value for key, value in parsed["usage"].items()):
            raise integrity.IntegrityError("reported usage differs from raw transcript")
        if row.get("telemetry") != parsed["telemetry"] or row.get("tool_calls") != parsed["tool_calls"]:
            raise integrity.IntegrityError("reported telemetry differs from raw transcript")
        if row.get("suite") == "delivery":
            item = next(case for case in delivery_cases.CASES if case["task_id"] == row["task_id"])
            submission = json.loads((cell / "submission.json").read_text(encoding="utf-8"))
            if not isinstance(submission, dict) or any(
                Path(name).name != name or name not in {item["filename"], ".gitignore"}
                and not (name.startswith("test_") and name.endswith(".py")) for name in submission
            ):
                raise integrity.IntegrityError("invalid archived submission")
            with tempfile.TemporaryDirectory(prefix="release-oracle-") as directory:
                workspace = Path(directory)
                for name, content in submission.items():
                    (workspace / name).write_text(content, encoding="utf-8")
                score = delivery_cases.score_workspace(workspace, item)
                for key in ("behavior_passed", "safety_passed", "oracle_valid", "workspace_scope_ok"):
                    if row.get(key) != score[key]:
                        raise integrity.IntegrityError("archived code no longer reproduces independent oracle results")
    return plan, rows


def evaluate(runs: dict[str, tuple[dict[str, Any], list[dict[str, Any]]]],
             targets: dict[str, Any], *, current_sources: dict[str, str]) -> dict[str, Any]:
    """Pure gate logic. CLI verifies raw evidence before calling this function."""
    checks: list[dict[str, Any]] = []
    metrics: dict[str, Any] = {}
    def check(name: str, passed: bool) -> None:
        checks.append({"check": name, "passed": bool(passed)})
    check("both_suites_present", set(runs) == {"source", "delivery"})
    for suite, catalog in (("source", SOURCE_CASES), ("delivery", delivery_cases.CASES)):
        if suite not in runs:
            continue
        plan, rows = runs[suite]
        integrity.verify_plan(plan)
        settings = plan.get("settings", {})
        expected = {(case["task_id"], arm, rep) for case in catalog for arm in targets["arms"]
                    for rep in range(1, targets["repetitions"] + 1)}
        check(suite + ":full_frozen_matrix", {tuple(spec) for spec in plan["specs"]} == expected
              and integrity.matrix_status(rows, plan)["complete"])
        check(suite + ":current_code_and_oracles", plan.get("source_files") == current_sources)
        check(suite + ":suite_identity", settings.get("suite") == suite and all(row.get("suite") == suite for row in rows))
        check(suite + ":explicit_baseline", settings.get("baseline_ref") == targets["baseline_ref"] and bool(plan.get("baseline_files")))
        check(suite + ":three_runs", settings.get("runs") == targets["repetitions"])
        check(suite + ":telemetry_complete", all(
            row.get("schema_version") == "3.0" and row.get("measurement_qualified") is True
            and row.get("telemetry", {}).get("transcript_complete") is True
            and row.get("telemetry", {}).get("usage_complete") is True
            and row.get("exit_status") == 0 and row.get("timed_out") is False
            and all(type(row.get(key)) in (int, float) and math.isfinite(row[key]) and row[key] >= 0 for key in COSTS)
            for row in rows))
        adaptive = [row for row in rows if row["variant"] == "adaptive"]
        passes = sum(row.get("passed") is True for row in adaptive)
        check(suite + ":quality_floor", passes >= targets[suite]["adaptive_minimum_passes"])
        check(suite + ":runtime_contract", all(
            row.get("routing_trace_valid") is True and row.get("retrieval_reference_observation_ok") is True
            and row.get("manual_contract_ok") is True and row.get("spontaneous_manual_mode") is False for row in adaptive))
        if suite == "delivery":
            safety_ids = {case["task_id"] for case in catalog if case.get("safety_critical")}
            safety = [row for row in adaptive if row["task_id"] in safety_ids]
            check("delivery:all_safety_attempts", len(safety) == targets["safety_critical_delivery_attempts"]
                  and all(row.get("passed") is True and row.get("safety_passed") is True
                          and row.get("oracle_valid") is True for row in safety))
            check("delivery:independent_oracles", all(row.get("oracle_valid") is True for row in rows))
        metrics[suite] = {"adaptive_passes": passes, "adaptive_attempts": len(adaptive), "comparators": {}}
        for comparator in ("baseline", "no-skill"):
            other = [row for row in rows if row["variant"] == comparator]
            check(suite + ":quality_not_lower_than_" + comparator,
                  passes >= sum(row.get("passed") is True for row in other))
            paired = analysis.paired_comparison(rows, comparator)
            check(suite + ":paired_" + comparator,
                  paired["matched_pairs"] == len(expected) // 3 and paired["ambiguous_pairs"] == 0
                  and paired["indeterminate_pairs"] == 0
                  and paired["joint_passes"] >= targets["minimum_joint_success_pairs_per_suite"])
            costs = paired["costs_on_joint_passes"]
            for metric, maximum in targets["maximum_cost_ratios"][comparator].items():
                value = costs[metric]["ratio_of_sums"]
                check(suite + ":" + comparator + ":" + metric,
                      costs[metric]["missing_pairs"] == 0 and value is not None and value <= maximum)
            metrics[suite]["comparators"][comparator] = paired
    if set(runs) == {"source", "delivery"}:
        source, delivery = runs["source"][0], runs["delivery"][0]
        check("cross_suite_same_candidate_and_baseline", source.get("source_files") == delivery.get("source_files")
              and source.get("baseline_files") == delivery.get("baseline_files"))
        keys = ("model", "reasoning", "codex_version", "platform", "python", "workers", "timeout", "command_template")
        check("cross_suite_same_environment", all(source["settings"].get(key) == delivery["settings"].get(key)
                                                   and source["settings"].get(key) is not None for key in keys))
        check("cross_suite_same_providers", source.get("providers") == delivery.get("providers")
              and source["manifest"]["providers"] == delivery["manifest"]["providers"])
        check("required_providers_present", {provider.get("id") for provider in source["manifest"]["providers"]}
              == {"zvec-grep", "codebase-memory-mcp", "rtk"} and len(source.get("providers", [])) == 3)
    ready = all(item["passed"] for item in checks)
    return {"benchmark_kind": "engineering-release-gate", "status": "engineering_gate_passed" if ready else "blocked",
            "engineering_gate_passed": ready, "human_review_required": True, "generalization_proven": False,
            "checks": checks, "metrics": metrics, "limitations": targets["limitations"]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path)
    parser.add_argument("--delivery", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    targets = json.loads(TARGET_PATH.read_text(encoding="utf-8"))
    if not args.source or not args.delivery:
        report = {"benchmark_kind": "engineering-release-gate", "status": "not_run", "model_executed": False,
                  "engineering_gate_passed": False, "targets": targets,
                  "reason": "Both measured source and delivery run directories are required."}
    else:
        try:
            report = evaluate({"source": load_run(args.source), "delivery": load_run(args.delivery)}, targets,
                              current_sources=integrity.source_files(ROOT))
            report["raw_artifacts_verified"] = True
        except (ValueError, KeyError, TypeError, OSError) as exc:
            report = {"benchmark_kind": "engineering-release-gate", "status": "blocked",
                      "engineering_gate_passed": False, "raw_artifacts_verified": False, "error": str(exc)}
    text = json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if report["engineering_gate_passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())

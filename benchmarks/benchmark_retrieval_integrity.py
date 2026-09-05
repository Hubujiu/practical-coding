#!/usr/bin/env python3
"""Compare evaluator invariants, NOT model quality, against a pinned analysis file."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import subprocess
import tempfile
from pathlib import Path
from typing import Any

BASELINE_REF = "942f0aa17bdac381ad50c544683c88e6320e6cf1"
BASELINE_BLOB = "654c6b6854f2d727731b7b83158399fdd9a43f77"
HERE = Path(__file__).resolve().parent


def load_analysis(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load evaluator: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def row(stage: str = "NONE", passed: bool | None = True, repetition: int = 1, **extra: Any) -> dict[str, Any]:
    value = {
        "task_id": "integrity-fixture", "variant": f"retrieval-cap:{stage}",
        "repetition": repetition, "passed": passed,
        "measurement_phase": "measured", "setup_included_in_comparison": False,
        "measured_setup_violation": False,
    }
    value.update(extra)
    return value


def checks(module: Any) -> dict[str, bool]:
    attempts = [row(repetition=i, passed=True if i == 1 else None,
                    variant="adaptive", selected_retrieval="NONE", timed_out=i != 1,
                    total_tokens=i * 100, duration_seconds=i * 10) for i in (1, 2, 3)]
    arm = module.analyze(attempts)["arms"]["adaptive"]
    return {
        "complete_shallow_success": module.minimum_stage([row()]) == "NONE",
        "complete_lower_failure_then_success": module.minimum_stage([row(passed=False), row("R0_DIRECT")]) == "R0_DIRECT",
        "empty_is_not_stable": not module.stable_pass([]),
        "false_is_not_success": not module.stable_pass([row(passed=False)]),
        "missing_lower_ceiling_is_unknown": module.minimum_stage([row("R1_DISCOVERY")]) is None,
        "indeterminate_lower_ceiling_is_unknown": module.minimum_stage([row(passed=None), row("R0_DIRECT")]) is None,
        "duplicate_repetition_rejected": not module.stable_pass([row(), row()]),
        "noncontiguous_repetitions_rejected": not module.stable_pass([row(repetition=1), row(repetition=3)]),
        "setup_contamination_rejected": not module.stable_pass([row(measured_setup_violation=True)]),
        "provider_ceiling_violation_rejected": not module.stable_pass([row(capability_ceiling_violation=True)]),
        "adaptive_exposes_missing_ceiling_repetition": module.minimum_stage([
            row(), row(variant="adaptive", repetition=2, selected_retrieval="NONE")]) is None,
        "timeouts_remain_in_success_denominator": math.isclose(arm["pass_rate"], 1 / 3),
        "timeout_costs_remain_in_aggregate": math.isclose(arm["total_tokens_mean"], 200),
    }


def compare(baseline: Path, candidate: Path) -> dict[str, Any]:
    data = baseline.read_bytes()
    blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
    if blob != BASELINE_BLOB:
        raise ValueError("baseline file is not the pinned, unmodified GitHub blob")
    old = checks(load_analysis(baseline, "integrity_baseline_analysis"))
    new = checks(load_analysis(candidate, "integrity_candidate_analysis"))
    return {
        "benchmark_kind": "evaluator-regression", "model_executed": False,
        "baseline_ref": BASELINE_REF, "baseline_blob": blob,
        "candidate_analysis_sha256": hashlib.sha256(candidate.read_bytes()).hexdigest(),
        "cases": [{"name": name, "baseline_pass": old[name], "candidate_pass": new[name]} for name in old],
        "baseline_passed": sum(old.values()), "candidate_passed": sum(new.values()), "total": len(old),
        "scope": "Synthetic evaluator counterexamples; no routing accuracy, LLM token saving, or provider-performance claim.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline-analysis", type=Path,
                        help="offline source file; its Git blob identity is checked")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="retrieval-integrity-") as directory:
        baseline = args.baseline_analysis
        if baseline is None:
            result = subprocess.run(
                ["git", "show", f"{BASELINE_REF}:benchmarks/retrieval_analysis.py"],
                cwd=HERE.parent, capture_output=True, timeout=30, check=True,
            )
            baseline = Path(directory) / "baseline_analysis.py"
            baseline.write_bytes(result.stdout)
        report = compare(baseline, HERE / "retrieval_analysis.py")
    text = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if report["candidate_passed"] == report["total"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

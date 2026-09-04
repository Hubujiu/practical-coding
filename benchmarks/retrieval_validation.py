#!/usr/bin/env python3
"""Dependency-enabled R0-R3 Retrieval-tree capability-ceiling benchmark."""

from __future__ import annotations

import argparse
import concurrent.futures
import datetime as dt
import json
import os
import statistics
import sys
from pathlib import Path
from typing import Any, Mapping

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import capability_environment as capabilities
import retrieval_cell as cell_runner
import retrieval_prompt as prompt_contract
import retrieval_topology as topology_contract
import run_benchmarks as bench
import tree_validation as base
from tree_cases import CASES

VERSION = "1.0"
MODEL = bench.MODEL
REASONING = bench.REASONING
STAGES = topology_contract.STAGES
STAGE_INDEX = topology_contract.STAGE_INDEX
SETUP_COMMAND_RE = prompt_contract.SETUP_COMMAND_RE
retrieval_nodes = topology_contract.retrieval_nodes
retrieval_declared_prefix = topology_contract.retrieval_declared_prefix
retrieval_prefix = topology_contract.retrieval_prefix
allowed_references = topology_contract.allowed_references
validate_trace = topology_contract.validate_trace
infer_trace = topology_contract.infer_trace
instrumentation = topology_contract.instrumentation
allowed_provider_ids = prompt_contract.allowed_provider_ids
retrieval_ceiling_instruction = prompt_contract.retrieval_ceiling_instruction
capability_note = prompt_contract.capability_note
task_prompt = prompt_contract.task_prompt
build_specs = prompt_contract.build_specs
_cell_path = prompt_contract._cell_path
_provider_usage = prompt_contract._provider_usage
provider_ceiling_violation = prompt_contract.provider_ceiling_violation
run_cell = cell_runner.run_cell

def _mean(records: list[dict[str, Any]], key: str) -> float | None:
    values = [float(record[key]) for record in records if record.get(key) is not None]
    return statistics.mean(values) if values else None


def summary(records: list[dict[str, Any]], runs: int, manifest: Mapping[str, Any], preflight_report: Mapping[str, Any]) -> dict[str, Any]:
    arms: dict[str, Any] = {}
    for variant in sorted({record["variant"] for record in records}):
        selected = [record for record in records if record["variant"] == variant]
        determinate = [record for record in selected if record.get("passed") is not None]
        arms[variant] = {
            "cells": len(selected),
            "determinate": len(determinate),
            "pass_rate": sum(record["passed"] is True for record in determinate) / len(determinate) if determinate else None,
            "tokens_mean": _mean(determinate, "total_tokens"),
            "duration_seconds_mean": _mean(determinate, "duration_seconds"),
            "tool_calls_mean": _mean(determinate, "tool_calls"),
        }
    measured = [record for record in records if record.get("measurement_phase") == "measured"]
    return {
        "runs_per_cell": runs,
        "tasks": len({record["task_id"] for record in records}),
        "repositories": sorted({record["repository"] for record in records}),
        "arms": arms,
        "canonical_retrieval_stages": list(STAGES),
        "trace_valid_rate": sum(record.get("routing_trace_valid") is True for record in measured if record.get("routing_trace_valid") is not None)
        / max(1, sum(record.get("routing_trace_valid") is not None for record in measured)),
        "measured_setup_violation_count": sum(record.get("measured_setup_violation") is True for record in measured),
        "capability_ceiling_violation_count": sum(record.get("capability_ceiling_violation") is True for record in measured),
        "retrieval_reference_observation_violation_count": sum(
            record.get("retrieval_reference_observation_ok") is False for record in measured
        ),
        "provider_usage_counts": {
            provider["id"]: sum(record.get("capability_usage", {}).get(provider["id"]) is True for record in measured)
            for provider in manifest["providers"]
        },
        "capability_profile": {
            "profile": manifest["profile"],
            "manifest_sha256": capabilities.manifest_fingerprint(manifest),
            "required_roles": list(manifest["required_roles"]),
            "preflight": preflight_report,
        },
        "measurement_contract": dict(manifest["measurement_contract"]),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument("--workers", type=int, default=3)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--repository-root", type=Path, default=ROOT.parent)
    parser.add_argument("--repository", action="append", default=[], help="override a source as NAME=PATH")
    parser.add_argument("--topology", type=Path, default=HERE / "tree_topology.json")
    parser.add_argument("--capability-manifest", type=Path, default=HERE / "capability_manifest.json")
    parser.add_argument("--baseline-ref")
    parser.add_argument("--codex", default=os.environ.get("CODEX_BIN", "codex"))
    parser.add_argument("--timeout", type=float, default=600)
    parser.add_argument("--case", action="append", default=[])
    parser.add_argument("--current-only", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def self_test(topology: Mapping[str, Any], manifest: Mapping[str, Any]) -> None:
    nodes = retrieval_nodes(topology)
    assert [nodes[name]["trace_mode"] for name in ("retrieval", "direct", "discovery", "evidence", "structural")] == list(STAGES)
    assert retrieval_prefix(topology, "R3_STRUCTURAL")[-1] == "references/retrieval/structural.md"
    assert len(build_specs(1, current_only=True, selected_cases={"pp-known-contract"})) == 6
    assert allowed_provider_ids("R0_DIRECT") == {"rtk"}
    assert allowed_provider_ids("R1_DISCOVERY") == {"rtk", "zvec-grep"}
    assert allowed_provider_ids("R3_STRUCTURAL") == {"rtk", "zvec-grep", "codebase-memory-mcp"}
    assert manifest["measurement_contract"]["setup_included_in_comparison"] is False
    assert manifest["measurement_contract"]["setup_token_estimate"] is False
    print("retrieval validation self-test: PASS")


def main() -> int:
    args = parse_args()
    topology = base.load_topology(args.topology.resolve())
    manifest = capabilities.load_manifest(args.capability_manifest.resolve())
    retrieval_nodes(topology)
    if args.self_test:
        self_test(topology, manifest)
        return 0
    if args.runs < 1 or args.workers < 1:
        raise SystemExit("runs and workers must be positive")
    selected_cases = set(args.case)
    unknown = selected_cases - {case["task_id"] for case in CASES}
    if unknown:
        raise SystemExit(f"unknown cases: {', '.join(sorted(unknown))}")

    preflight_report = capabilities.preflight(manifest, cwd=ROOT)
    repositories = base.resolve_repositories(args.repository_root.resolve(), args.repository)
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    output = (args.output or ROOT / "benchmark-results" / f"retrieval-{stamp}").resolve()
    output.mkdir(parents=True, exist_ok=True)
    capabilities.write_report(output / "capability-preflight.json", preflight_report)

    baseline_ref = args.baseline_ref or topology.get("baseline_ref")
    baseline_dir: Path | None = None
    if not args.current_only:
        if not baseline_ref:
            raise RuntimeError("baseline_ref is required unless --current-only is used")
        baseline_dir = output / "baseline-skill"
        if not (baseline_dir / "SKILL.md").is_file():
            baseline_dir = bench.materialize_git_skill(str(baseline_ref), baseline_dir)

    eval_home = bench.prepare_eval_home(output / "eval-home")
    specs = build_specs(args.runs, current_only=args.current_only, selected_cases=selected_cases)
    records: list[dict[str, Any]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [
            pool.submit(
                run_cell,
                spec,
                args,
                topology,
                manifest,
                preflight_report,
                repositories,
                baseline_dir,
                eval_home,
                output,
            )
            for spec in specs
        ]
        for future in concurrent.futures.as_completed(futures):
            records.append(future.result())

    records.sort(key=lambda row: (row["task_id"], row["variant"], row["repetition"]))
    rows_path = output / "results.jsonl"
    rows_path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in records), encoding="utf-8")
    report = summary(records, args.runs, manifest, preflight_report)
    report.update(
        {
            "schema_version": VERSION,
            "model": MODEL,
            "reasoning": REASONING,
            "topology": topology,
            "baseline_ref": baseline_ref,
            "results_jsonl": str(rows_path),
        }
    )
    (output / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except capabilities.CapabilityError as exc:
        print(f"retrieval benchmark setup failed: {exc}", file=sys.stderr)
        raise SystemExit(2)

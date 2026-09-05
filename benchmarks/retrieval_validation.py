#!/usr/bin/env python3
"""Frozen dependency-enabled source and delivery evaluation; setup is unmeasured."""
from __future__ import annotations

import argparse
import concurrent.futures
import datetime as dt
import json
import math
import os
import platform
import random
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Mapping

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import capability_environment as capabilities
import delivery_cases
import retrieval_cell as cell_runner
import retrieval_prompt as prompt_contract
import retrieval_topology as topology_contract
import run_benchmarks as bench
import tree_validation as base
from retrieval_analysis import arm_summary
from retrieval_integrity import IntegrityError, make_plan, matrix_status, source_files, write_plan
from tree_cases import CASES, REPOSITORIES

VERSION = "3.0"
MODEL, REASONING = bench.MODEL, bench.REASONING
# Keep the public topology/probe helpers used by existing contract tests.
STAGES, STAGE_INDEX = topology_contract.STAGES, topology_contract.STAGE_INDEX
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


def experiment_specs(args: argparse.Namespace, topology: Mapping[str, Any]) -> list[tuple[str, str, int]]:
    catalog = delivery_cases.CASES if args.suite == "delivery" else CASES
    selected = set(args.case)
    unknown = selected - {case["task_id"] for case in catalog}
    if unknown:
        raise IntegrityError(f"unknown cases: {', '.join(sorted(unknown))}")
    specs = []
    for case in catalog:
        if selected and case["task_id"] not in selected:
            continue
        variants = ["adaptive"] if args.current_only else ["no-skill", "baseline", "adaptive"]
        if not args.comparators_only and not case.get("manual_request"):
            variants += ([f"retrieval-cap:{stage}" for stage in STAGES] if args.axis == "retrieval"
                         else [f"cap:{node}" for node in topology["automatic_nodes"]])
        for repetition in range(1, args.runs + 1):
            specs.extend((case["task_id"], variant, repetition) for variant in variants)
    random.Random(args.seed).shuffle(specs)
    return specs


def effective_manifest(manifest: Mapping[str, Any], suite: str, repositories: set[str]) -> dict[str, Any]:
    result = json.loads(json.dumps(manifest))
    if suite == "delivery":
        result["profile"] += ":delivery-fixtures-v1"
        result["repository_warmups"] = {"delivery-fixtures": {
            "required_binaries": [sys.executable],
            "commands": [{"command": [sys.executable, "-I", "-B", "-c", "import sqlite3, asyncio, threading"],
                          "timeout_seconds": 30}],
        }}
    else:
        result["repository_warmups"] = {key: value for key, value in result["repository_warmups"].items() if key in repositories}
    # Provider requirements and pinned versions are never relaxed per task or arm.
    return result


def prepare_eval_home(path: Path) -> Path:
    source = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")) / "auth.json"
    api_key = bool(os.environ.get("CODEX_API_KEY") or os.environ.get("OPENAI_API_KEY"))
    if not source.is_file() and not api_key:
        raise capabilities.CapabilitySetupError("no Codex auth.json or API credential is available")
    path.mkdir(parents=True, exist_ok=True)
    target = path / "auth.json"
    if api_key:
        if target.exists():
            target.unlink()
    else:
        shutil.copyfile(source, target)  # Never hard-link a mutable credential file.
        target.chmod(0o600)
    return path


def snapshot_skill(source: Path, target: Path) -> Path:
    expected = source_files(source, harness=False)
    if target.exists():
        if source_files(target, harness=False) != expected:
            raise IntegrityError("candidate snapshot changed; use a new output directory")
        return target
    target.mkdir(parents=True)
    for relative in expected:
        destination = target / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source / relative, destination)
    return target


def summary(records: list[dict[str, Any]], runs: int, manifest: Mapping[str, Any], preflight_report: Mapping[str, Any]) -> dict[str, Any]:
    measured = [record for record in records if record.get("measurement_phase") == "measured"]
    return {
        "runs_per_cell": runs, "tasks": len({row["task_id"] for row in measured}),
        "repositories": sorted({row["repository"] for row in measured}),
        "arms": {variant: arm_summary([row for row in measured if row["variant"] == variant])
                 for variant in sorted({row["variant"] for row in measured})},
        "canonical_retrieval_stages": list(STAGES),
        "measured_setup_violation_count": sum(row.get("measured_setup_violation") is True for row in measured),
        "capability_ceiling_violation_count": sum(row.get("capability_ceiling_violation") is True for row in measured),
        "retrieval_reference_observation_violation_count": sum(row.get("retrieval_reference_observation_ok") is False for row in measured),
        "unqualified_measurement_count": sum(row.get("measurement_qualified") is not True for row in measured),
        "provider_usage_counts": {provider["id"]: sum(row.get("capability_usage", {}).get(provider["id"]) is True for row in measured)
                                  for provider in manifest["providers"]},
        "capability_profile": {"profile": manifest["profile"], "manifest_sha256": capabilities.manifest_fingerprint(manifest),
                               "required_roles": list(manifest["required_roles"]), "preflight": preflight_report},
        "measurement_contract": dict(manifest["measurement_contract"]),
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", type=int, default=1)
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--seed", type=int, default=20260904)
    parser.add_argument("--suite", choices=("source", "delivery"), default="source")
    parser.add_argument("--axis", choices=("retrieval", "execution"), default="retrieval")
    parser.add_argument("--comparators-only", action="store_true", help="adaptive/baseline/no-skill, no capability ceilings")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--repository-root", type=Path, default=ROOT.parent)
    parser.add_argument("--repository", action="append", default=[], help="override NAME=PATH")
    parser.add_argument("--topology", type=Path, default=HERE / "tree_topology.json")
    parser.add_argument("--capability-manifest", type=Path, default=HERE / "capability_manifest.json")
    parser.add_argument("--baseline-ref", help="explicit frozen comparator revision; required for paired runs")
    parser.add_argument("--model", default=MODEL)
    parser.add_argument("--reasoning", default=REASONING)
    parser.add_argument("--codex", default=os.environ.get("CODEX_BIN", "codex"))
    parser.add_argument("--timeout", type=float, default=600)
    parser.add_argument("--case", action="append", default=[])
    parser.add_argument("--current-only", action="store_true")
    parser.add_argument("--describe", action="store_true", help="print planned dimensions without executing a model")
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args(argv)


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


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    topology = base.load_topology(args.topology.resolve())
    declared_manifest = capabilities.load_manifest(args.capability_manifest.resolve())
    retrieval_nodes(topology)
    if args.self_test:
        self_test(topology, declared_manifest)
        return 0
    if args.runs < 1 or args.workers < 1 or not math.isfinite(args.timeout) or args.timeout <= 0:
        raise IntegrityError("runs, workers and finite timeout must be positive")
    specs = experiment_specs(args, topology)
    catalog = delivery_cases.CASES if args.suite == "delivery" else CASES
    tasks = {spec[0] for spec in specs}
    repositories_needed = {case["repository"] for case in catalog if case["task_id"] in tasks}
    manifest = effective_manifest(declared_manifest, args.suite, repositories_needed)
    if args.describe:
        print(json.dumps({"benchmark_kind": "run-plan-preview", "model_executed": False,
                          "suite": args.suite, "tasks": len(tasks), "runs": args.runs, "cells": len(specs),
                          "variants": sorted({spec[1] for spec in specs}), "required_roles": manifest["required_roles"]}, indent=2))
        return 0
    if not args.current_only and not args.baseline_ref:
        raise IntegrityError("paired runs require an explicit --baseline-ref")
    codex = bench.resolve_codex(args.codex)
    try:
        probe = subprocess.run([codex, "--version"], capture_output=True, text=True, timeout=30, check=True)
    except (OSError, subprocess.SubprocessError) as exc:
        raise capabilities.CapabilitySetupError(f"Codex preflight failed: {exc}") from exc
    codex_version = (probe.stdout + probe.stderr).strip()
    if not codex_version:
        raise capabilities.CapabilitySetupError("Codex probe returned no version")
    bench.MODEL, bench.REASONING = args.model, args.reasoning
    preflight = capabilities.preflight(manifest, cwd=ROOT)
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    output = (args.output or ROOT / "benchmark-results" / f"{args.suite}-{args.axis}-{stamp}").resolve()
    if output == ROOT or output in ROOT.parents:
        raise IntegrityError("output must not be the repository root or its ancestor")
    output.mkdir(parents=True, exist_ok=True)
    eval_home = prepare_eval_home(output / "eval-home")
    repositories = {}
    if args.suite == "source":
        overrides = dict(value.split("=", 1) for value in args.repository)
        if set(overrides) - set(REPOSITORIES):
            raise IntegrityError("unknown repository override")
        for name in repositories_needed:
            path = Path(overrides.get(name, args.repository_root / REPOSITORIES[name]["local_name"])).resolve()
            subprocess.run(["git", "-C", str(path), "cat-file", "-e", REPOSITORIES[name]["commit"] + "^{commit}"],
                           capture_output=True, check=True, timeout=30)
            repositories[name] = path
    baseline = None
    baseline_ref = args.baseline_ref
    if not args.current_only:
        result = subprocess.run(["git", "rev-parse", "--verify", f"{baseline_ref}^{{commit}}"], cwd=ROOT,
                                capture_output=True, text=True, check=True, timeout=30)
        baseline_ref = result.stdout.strip()
        baseline = output / "baseline-skill" / baseline_ref
        # Reconstruct the exact pinned source before trusting an existing snapshot.
        with tempfile.TemporaryDirectory(prefix="baseline-") as directory:
            fresh = bench.materialize_git_skill(baseline_ref, Path(directory))
            if baseline.exists():
                if source_files(baseline, harness=False) != source_files(fresh, harness=False):
                    raise IntegrityError("baseline snapshot changed; use a new output directory")
            else:
                shutil.copytree(fresh, baseline)
    settings = {"model": args.model, "reasoning": args.reasoning, "timeout": args.timeout,
                "codex": codex, "codex_version": codex_version, "baseline_ref": baseline_ref,
                "runs": args.runs, "workers": args.workers, "seed": args.seed, "suite": args.suite,
                "axis": args.axis, "comparators_only": args.comparators_only,
                "frozen_case_ids": sorted(case["task_id"] for case in catalog),
                "selected_case_ids": sorted(tasks), "schedule": [list(spec) for spec in specs],
                "platform": platform.platform(), "python": platform.python_version(),
                "command_template": bench.codex_command(codex, Path("<workspace>"))}
    args.run_plan = make_plan(ROOT, baseline, settings, manifest, topology, preflight, specs)
    write_plan(output / "run-plan.json", args.run_plan)
    args.candidate_skill = snapshot_skill(ROOT, output / "candidate-skill")
    capabilities.write_report(output / "capability-preflight.json", preflight)
    records = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(run_cell, spec, args, topology, manifest, preflight, repositories,
                               baseline, eval_home, output) for spec in specs]
        for future in concurrent.futures.as_completed(futures):
            records.append(future.result())
    if make_plan(ROOT, baseline, settings, manifest, topology, preflight, specs) != args.run_plan:
        raise IntegrityError("source changed during measurement; this run cannot be promoted")
    if source_files(args.candidate_skill, harness=False) != source_files(ROOT, harness=False):
        raise IntegrityError("candidate snapshot changed during measurement")
    records.sort(key=lambda row: (row["task_id"], row["variant"], row["repetition"]))
    rows_path = output / "results.jsonl"
    rows_path.write_text("".join(json.dumps(row, ensure_ascii=False, allow_nan=False) + "\n" for row in records), encoding="utf-8")
    report = summary(records, args.runs, manifest, preflight)
    report.update(schema_version=VERSION, model=args.model, reasoning=args.reasoning, suite=args.suite,
                  axis=args.axis, topology=topology, baseline_ref=baseline_ref, results_jsonl=str(rows_path),
                  run_plan=str(output / "run-plan.json"), experiment_fingerprint=args.run_plan["experiment_fingerprint"],
                  matrix=matrix_status(records, args.run_plan))
    (output / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["matrix"]["complete"] and not report["unqualified_measurement_count"] else 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (capabilities.CapabilityError, IntegrityError, OSError, subprocess.SubprocessError, ValueError) as exc:
        print(f"benchmark blocked: {exc}", file=sys.stderr)
        raise SystemExit(2)

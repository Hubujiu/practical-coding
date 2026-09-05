"""One dependency-enabled, prewarmed Retrieval benchmark cell."""

from __future__ import annotations

import argparse
import json
import os
import shutil
from pathlib import Path
from typing import Any, Mapping

try:
    from . import capability_environment as capabilities
    from . import retrieval_trace
    from .retrieval_integrity import IntegrityError, validate_cached_result
    from . import run_benchmarks as bench
    from . import tree_validation as base
    from .retrieval_prompt import (
        SETUP_COMMAND_RE, _cell_path, _provider_usage, provider_ceiling_violation, task_prompt
    )
    from .retrieval_topology import STAGE_INDEX, infer_trace, retrieval_declared_prefix, validate_trace
    from .tree_cases import CASES, REPOSITORIES
except ImportError:  # direct script imports from the benchmarks directory
    import capability_environment as capabilities
    import retrieval_trace
    from retrieval_integrity import IntegrityError, validate_cached_result
    import run_benchmarks as bench
    import tree_validation as base
    from retrieval_prompt import SETUP_COMMAND_RE, _cell_path, _provider_usage, provider_ceiling_violation, task_prompt
    from retrieval_topology import STAGE_INDEX, infer_trace, retrieval_declared_prefix, validate_trace
    from tree_cases import CASES, REPOSITORIES

VERSION = "2.0"

def run_cell(
    spec: tuple[str, str, int],
    args: argparse.Namespace,
    topology: Mapping[str, Any],
    manifest: Mapping[str, Any],
    preflight_report: Mapping[str, Any],
    repositories: Mapping[str, Path],
    baseline: Path | None,
    eval_home: Path,
    output: Path,
) -> dict[str, Any]:
    task_id, variant, repetition = spec
    case = next(item for item in CASES if item["task_id"] == task_id)
    cell = _cell_path(output, spec)
    result_path = cell / "result.json"
    setup_path = cell / "capability-setup.json"
    manifest_sha = capabilities.manifest_fingerprint(manifest)
    plan = getattr(args, "run_plan", None)
    if plan is None or list(spec) not in plan.get("specs", []):
        raise capabilities.CapabilitySetupError("cell requires a matching frozen run plan")
    fingerprint = plan["experiment_fingerprint"]
    if result_path.is_file():
        if not setup_path.is_file():
            raise capabilities.CapabilitySetupError(f"measured result has no setup receipt: {result_path}")
        setup = json.loads(setup_path.read_text(encoding="utf-8"))
        if setup.get("manifest_sha256") != manifest_sha:
            raise capabilities.CapabilitySetupError(f"stale setup receipt: {setup_path}")
        record = json.loads(result_path.read_text(encoding="utf-8"))
        try:
            validate_cached_result(record, setup, plan, spec, manifest_sha)
        except IntegrityError as exc:
            raise capabilities.CapabilitySetupError(f"unsafe cached result {result_path}: {exc}") from exc
        return record

    cell.mkdir(parents=True, exist_ok=True)
    workspace = cell / "workspace"
    if workspace.exists():
        shutil.rmtree(workspace)
    base.prepare_workspace(repositories[case["repository"]], REPOSITORIES[case["repository"]]["commit"], workspace)
    setup = capabilities.prepare_workspace(workspace, case["repository"], manifest, preflight_report)
    setup["experiment_fingerprint"] = fingerprint
    capabilities.write_report(setup_path, setup)

    if variant == "no-skill":
        loaded = ""
    elif variant == "baseline":
        if baseline is None:
            raise RuntimeError("baseline Skill is unavailable")
        loaded = bench.skill_text("practical-previous", {}, baseline)
    else:
        loaded = bench.skill_text("practical-current", {}, None)

    prompt = task_prompt(case, loaded, variant, topology)
    (cell / "prompt.txt").write_text(prompt, encoding="utf-8")
    env = os.environ.copy()
    env["CODEX_HOME"] = str(eval_home)
    env.update(capabilities.workspace_environment(workspace, env))
    codex = bench.resolve_codex(args.codex)
    stdout = cell / "round1.jsonl"
    stderr = cell / "round1.stderr.txt"

    # Measured time begins here, after every provider/index/build warm-up has
    # succeeded and its separate receipt has been written.
    code, timed_out, forced, duration = bench.run_codex(
        bench.codex_command(codex, workspace), prompt, workspace, env, stdout, stderr, args.timeout
    )
    parsed = bench.parse_transcript(stdout)
    current_runtime = variant == "adaptive" or variant.startswith("retrieval-cap:")
    trace = retrieval_trace.parse_trace(parsed["answer"]) if current_runtime else None
    trace_source = "reported" if trace and trace.get("path") else None
    if current_runtime and trace and not trace.get("path"):
        trace = infer_trace(topology, parsed["tool_commands"])
        trace_source = "observed-commands"
    ceiling = variant.split(":", 1)[1] if variant.startswith("retrieval-cap:") else None
    trace_valid = validate_trace(topology, trace, ceiling) if current_runtime and trace is not None else None
    terminal_node = trace["path"][-1] if trace and trace.get("path") else None
    setup_violation = bool(SETUP_COMMAND_RE.search("\n".join(parsed["tool_commands"])))
    provider_usage = _provider_usage(parsed["tool_commands"])
    ceiling_violation = provider_ceiling_violation(provider_usage, ceiling)
    observed_retrieval = retrieval_trace.observed_references(parsed["tool_commands"])
    declared_retrieval = [
        base.canonical_reference(reference)
        for reference in (trace or {}).get("references_loaded", [])
        if base.canonical_reference(reference).startswith("references/retrieval/")
    ]
    observation_ok = declared_retrieval == observed_retrieval if current_runtime else None

    record: dict[str, Any] = {
        "schema_version": VERSION,
        "experiment_fingerprint": fingerprint,
        "task_id": task_id,
        "repository": case["repository"],
        "family": case["family"],
        "manual_request": case.get("manual_request"),
        "variant": variant,
        "retrieval_ceiling": ceiling,
        "repetition": repetition,
        "exit_status": code,
        "timed_out": timed_out,
        "forced_after_completion": forced,
        "duration_seconds": duration,
        "tool_calls": parsed["tool_calls"],
        "tool_output_bytes": sum(len(text.encode("utf-8")) for text in parsed.get("tool_outputs", [])),
        **parsed["usage"],
        "answer": parsed["answer"],
        "tool_commands": parsed["tool_commands"],
        "selected_path": trace["path"] if trace else None,
        "selected_terminal_node": terminal_node,
        "selected_depth": topology["automatic_nodes"].get(terminal_node, {}).get("depth") if terminal_node else None,
        "selected_retrieval": trace["retrieval"] if trace else None,
        "selected_retrieval_index": STAGE_INDEX.get(trace["retrieval"]) if trace else None,
        "selected_retrieval_references": retrieval_declared_prefix(topology, trace["retrieval"])
        if trace and trace.get("retrieval") in STAGE_INDEX
        else [],
        "selected_manual": trace["manual"] if trace else None,
        "references_loaded": trace["references_loaded"] if trace else [],
        "routing_trace_valid": trace_valid,
        "routing_trace_source": trace_source,
        "retrieval_reference_observation_ok": observation_ok,
        "observed_retrieval_references": observed_retrieval,
        "capability_usage": provider_usage,
        "capability_ceiling_violation": ceiling_violation,
        "measurement_phase": "measured",
        "setup_included_in_comparison": False,
        "capability_setup_file": str(setup_path),
        "measured_setup_violation": setup_violation,
    }
    infrastructure_error = "timeout" if timed_out else (f"codex exit status {code}" if code and not forced else None)
    if infrastructure_error:
        record.update({"passed": None, "verdict": "indeterminate", "error": infrastructure_error})
    else:
        record.update(
            base.score_answer(
                case,
                parsed["answer"],
                parsed["tool_commands"],
                workspace,
                trace=trace,
                enforce_runtime_contract=current_runtime,
            )
        )
        if current_runtime and not trace_valid:
            record["passed"] = False
            record["routing_trace_error"] = True
        if current_runtime and observation_ok is not True:
            record["passed"] = False
            record["retrieval_reference_observation_error"] = True
        if setup_violation or ceiling_violation:
            record["passed"] = False
        record["verdict"] = "pass" if record["passed"] else "fail"

    (cell / "answer.md").write_text(parsed["answer"] + "\n", encoding="utf-8")
    result_path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return record

"""One frozen, prewarmed source-analysis or executable-delivery benchmark cell."""
from __future__ import annotations

import argparse
import json
import os
import shutil
from pathlib import Path
from typing import Any, Mapping

try:
    from . import capability_environment as capabilities, delivery_cases, measured_process, measured_transcript
    from . import retrieval_trace, run_benchmarks as bench, tree_validation as base
    from .retrieval_integrity import IntegrityError, artifact_hashes, validate_cached_result, write_result
    from .retrieval_prompt import _cell_path, provider_ceiling_violation, task_prompt
    from .retrieval_topology import STAGE_INDEX, retrieval_declared_prefix, validate_trace
    from .tree_cases import CASES, REPOSITORIES
except ImportError:
    import capability_environment as capabilities
    import delivery_cases, measured_process, measured_transcript, retrieval_trace
    import run_benchmarks as bench
    import tree_validation as base
    from retrieval_integrity import IntegrityError, artifact_hashes, validate_cached_result, write_result
    from retrieval_prompt import _cell_path, provider_ceiling_violation, task_prompt
    from retrieval_topology import STAGE_INDEX, retrieval_declared_prefix, validate_trace
    from tree_cases import CASES, REPOSITORIES

VERSION = "3.0"


def load_skill(root: Path) -> str:
    return (f"Practical Coding is loaded below. Read only event-required references from {root / 'references'}.\n"
            f"<loaded-skill name=\"practical-coding\">\n{(root / 'SKILL.md').read_text(encoding='utf-8')}\n</loaded-skill>")


def run_cell(spec: tuple[str, str, int], args: argparse.Namespace, topology: Mapping[str, Any],
             manifest: Mapping[str, Any], preflight_report: Mapping[str, Any], repositories: Mapping[str, Path],
             baseline: Path | None, eval_home: Path, output: Path) -> dict[str, Any]:
    task_id, variant, repetition = spec
    suite = getattr(args, "suite", "source")
    catalog = delivery_cases.CASES if suite == "delivery" else CASES
    case = next(item for item in catalog if item["task_id"] == task_id)
    cell = _cell_path(output, spec)
    result_path, setup_path = cell / "result.json", cell / "capability-setup.json"
    manifest_sha = capabilities.manifest_fingerprint(manifest)
    plan = getattr(args, "run_plan", None)
    if plan is None or list(spec) not in plan.get("specs", []):
        raise capabilities.CapabilitySetupError("cell requires a matching frozen run plan")
    fingerprint = plan["experiment_fingerprint"]
    if result_path.is_file():
        try:
            setup = json.loads(setup_path.read_text(encoding="utf-8"))
            record = json.loads(result_path.read_text(encoding="utf-8"))
            validate_cached_result(record, setup, plan, spec, manifest_sha, cell_dir=cell)
        except (IntegrityError, ValueError, OSError) as exc:
            raise capabilities.CapabilitySetupError(f"unsafe cached result {result_path}: {exc}") from exc
        return record

    cell.mkdir(parents=True, exist_ok=True)
    workspace = cell / "workspace"
    if workspace.exists():
        shutil.rmtree(workspace)
    if suite == "delivery":
        delivery_cases.prepare_workspace(workspace, case)
    else:
        base.prepare_workspace(repositories[case["repository"]], REPOSITORIES[case["repository"]]["commit"], workspace)
    setup = capabilities.prepare_workspace(workspace, case["repository"], manifest, preflight_report)
    setup.update(experiment_fingerprint=fingerprint, cell=list(spec))
    capabilities.write_report(setup_path, setup)

    current = variant == "adaptive" or variant.startswith(("retrieval-cap:", "cap:"))
    source_root = Path(getattr(args, "candidate_skill", bench.ROOT)) if current else baseline
    if variant == "no-skill":
        loaded = ""
    else:
        if source_root is None:
            raise IntegrityError("baseline Skill is unavailable")
        loaded = load_skill(source_root)
    prompt = task_prompt(case, loaded, variant, topology)
    (cell / "prompt.txt").write_text(prompt, encoding="utf-8")
    env = os.environ.copy()
    env["CODEX_HOME"] = str(eval_home)
    if not env.get("CODEX_API_KEY") and env.get("OPENAI_API_KEY"):
        env["CODEX_API_KEY"] = env["OPENAI_API_KEY"]
    env.update(capabilities.workspace_environment(workspace, env))
    codex = bench.resolve_codex(args.codex)
    stdout, stderr = cell / "round1.jsonl", cell / "round1.stderr.txt"
    # Model timing begins only after all provider/index/dependency/build setup.
    code, timed_out, forced, duration = measured_process.run_codex(
        bench.codex_command(codex, workspace), prompt, workspace, env, stdout, stderr, args.timeout)
    parsed = measured_transcript.parse_transcript(stdout)
    trace = retrieval_trace.parse_trace(parsed["answer"]) if current else None
    ceiling = variant.split(":", 1)[1] if variant.startswith("retrieval-cap:") else None
    execution_ceiling = variant.split(":", 1)[1] if variant.startswith("cap:") else None
    trace_valid = validate_trace(topology, trace, ceiling) if current else None
    if execution_ceiling and trace_valid:
        allowed_path = base.node_path(dict(topology), execution_ceiling)
        trace_valid = trace["path"] == allowed_path[:len(trace["path"])] and trace["manual"] == "none"
    observations = measured_transcript.observe_policy_reads(parsed["tool_events"], source_root) if current else None
    observed_refs = observations["references"] if observations else []
    declared = [measured_transcript.canonical_reference(ref) for ref in (trace or {}).get("references_loaded", [])]
    observation_ok = (declared == observed_refs and not observations["unverified_references"]) if current else None
    providers = measured_transcript.provider_observations(parsed["tool_events"])
    setup_violation = providers["setup_violation"]
    ceiling_violation = provider_ceiling_violation(providers["attempted"], ceiling)
    terminal = trace["path"][-1] if trace and trace.get("path") else None
    mode = trace.get("retrieval") if trace else None
    record: dict[str, Any] = {
        "schema_version": VERSION, "experiment_fingerprint": fingerprint, "suite": suite,
        "task_id": task_id, "repository": case["repository"], "family": case["family"],
        "manual_request": case.get("manual_request"), "safety_critical": bool(case.get("safety_critical")),
        "variant": variant, "repetition": repetition, "retrieval_ceiling": ceiling,
        "execution_ceiling": execution_ceiling, "exit_status": code, "timed_out": timed_out,
        "forced_after_completion": forced, "duration_seconds": duration,
        "tool_calls": parsed["tool_calls"], **parsed["usage"],
        "tool_output_bytes": sum(len(text.encode("utf-8")) for text in parsed["tool_outputs"]),
        "telemetry": parsed["telemetry"], "answer": parsed["answer"], "tool_commands": parsed["tool_commands"],
        "selected_path": trace["path"] if trace else None, "selected_terminal_node": terminal,
        "selected_depth": topology["automatic_nodes"].get(terminal, {}).get("depth"),
        "selected_retrieval": mode, "selected_retrieval_index": STAGE_INDEX.get(mode),
        "selected_retrieval_references": retrieval_declared_prefix(topology, mode) if mode in STAGE_INDEX else [],
        "selected_manual": trace["manual"] if trace else None, "references_loaded": declared,
        "routing_trace_valid": trace_valid, "routing_trace_source": "reported" if trace else None,
        "retrieval_reference_observation_ok": observation_ok,
        "observed_retrieval_references": [ref for ref in observed_refs if ref.startswith("references/retrieval/")],
        "policy_read_observations": observations,
        "capability_usage": providers["successful"], "capability_attempts": providers["attempted"],
        "capability_ceiling_violation": ceiling_violation, "measured_setup_violation": setup_violation,
        "measurement_phase": "measured", "setup_included_in_comparison": False,
        "capability_setup_file": str(setup_path),
    }
    failure = ("timeout" if timed_out else f"process exit {code}" if code else
               "incomplete transcript" if not parsed["telemetry"]["transcript_complete"] else None)
    if failure:
        record.update(passed=None, verdict="indeterminate", error=failure)
    else:
        if suite == "delivery":
            score = delivery_cases.score_workspace(workspace, case)
            manual_ok = not current or trace["manual"] == "none"
            score.update(manual_contract_ok=manual_ok, spontaneous_manual_mode=not manual_ok)
            score["passed"] = score["passed"] and manual_ok
        else:
            score = base.score_answer(case, parsed["answer"],
                                      measured_transcript.verified_probe_commands(parsed["tool_events"]),
                                      workspace, trace=trace, enforce_runtime_contract=current)
            score["behavior_passed"] = score["passed"]
        record.update(score)
        if suite == "delivery" and score.get("oracle_valid") is not True:
            failure = "independent oracle unavailable"
            record.update(passed=None, error=failure)
        if current and (not trace_valid or not observation_ok):
            record["passed"] = False
            record["routing_trace_error"] = not trace_valid
            record["retrieval_reference_observation_error"] = not observation_ok
        if setup_violation or ceiling_violation:
            record["passed"] = False
        record["verdict"] = "indeterminate" if failure else "pass" if record["passed"] else "fail"
    if failure:
        record["passed"] = None
    # Missing usage may coexist with correct behavior; it blocks cost/release evidence,
    # not a claim that the actual submitted code was behaviorally wrong.
    record["measurement_qualified"] = (parsed["telemetry"]["usage_complete"] and not failure
                                        and not setup_violation and not ceiling_violation)
    (cell / "answer.md").write_text(parsed["answer"] + "\n", encoding="utf-8")
    if suite == "delivery":
        try:
            submission = delivery_cases.submitted_files(workspace)
        except (OSError, ValueError):
            submission = None
            record["passed"] = False
            record["verdict"] = "fail"
        (cell / "submission.json").write_text(json.dumps(submission, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    record["artifact_sha256"] = artifact_hashes(cell)
    write_result(result_path, record)
    return record

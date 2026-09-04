"""Monkey-patch the historical execution-tree runner with dependency setup."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

try:
    from . import capability_environment as capabilities
    from . import dependency_tree_contract as contract
    from . import retrieval_trace
    from . import tree_validation as base
except ImportError:  # direct script imports from the benchmarks directory
    import capability_environment as capabilities
    import dependency_tree_contract as contract
    import retrieval_trace
    import tree_validation as base


def patch_runner(
    manifest: Mapping[str, Any],
    preflight_report: Mapping[str, Any],
    manifest_path: Path,
) -> None:
    original_prepare_workspace = base.prepare_workspace
    original_allowed_references = base.allowed_references
    original_task_prompt = base.task_prompt
    original_validate_trace = base.validate_trace
    original_infer_trace = base.infer_trace_from_commands
    original_score_answer = base.score_answer
    original_summary = base.summary
    original_run_cell = base.run_cell
    original_run_codex = base.bench.run_codex

    repository_by_local_name = {str(spec["local_name"]): name for name, spec in base.REPOSITORIES.items()}
    repository_by_commit = {str(spec["commit"]): name for name, spec in base.REPOSITORIES.items()}

    def prepare_workspace(source: Path, commit: str, workspace: Path) -> None:
        original_prepare_workspace(source, commit, workspace)
        repository = repository_by_commit.get(commit) or repository_by_local_name.get(source.name)
        if repository is None:
            raise capabilities.CapabilitySetupError(f"no capability warm-up mapping for source: {source}")
        report = capabilities.prepare_workspace(workspace, repository, manifest, preflight_report)
        capabilities.write_report(workspace.parent / "capability-setup.json", report)

    def allowed_references(topology: dict[str, Any]) -> set[str]:
        return contract.extend_allowed_references(topology, original_allowed_references, base.canonical_reference)

    note = contract.capability_note()

    def task_prompt(case: dict[str, Any], loaded: str, variant: str, topology: dict[str, Any]) -> str:
        enriched = note if not loaded else loaded + "\n\n" + note
        return original_task_prompt(case, enriched, variant, topology)

    def validate_trace(topology: dict[str, Any], trace: dict[str, Any]) -> bool:
        return contract.validate_trace(topology, trace, original_validate_trace, base.canonical_reference)

    def infer_trace_from_commands(topology: dict[str, Any], commands: list[str]) -> dict[str, Any]:
        return contract.infer_trace(topology, commands, original_infer_trace, base.canonical_reference)

    def score_answer(*args: Any, **kwargs: Any) -> dict[str, Any]:
        result = original_score_answer(*args, **kwargs)
        commands = args[2] if len(args) >= 3 else kwargs.get("commands", [])
        violation = bool(contract.SETUP_COMMAND_RE.search("\n".join(str(command) for command in commands)))
        result["measured_setup_violation"] = violation
        if violation:
            result["passed"] = False
        return result

    def summary(records: list[dict[str, Any]], runs: int) -> dict[str, Any]:
        report = original_summary(records, runs)
        measured = [record for record in records if record.get("measurement_phase") == "measured"]
        report["capability_profile"] = {
            "profile": manifest["profile"],
            "manifest": str(manifest_path),
            "manifest_sha256": capabilities.manifest_fingerprint(manifest),
            "required_roles": list(manifest["required_roles"]),
            "preflight": preflight_report,
        }
        report["measurement_contract"] = dict(manifest["measurement_contract"])
        report["measured_cells"] = len(measured)
        report["measured_setup_violation_count"] = sum(
            record.get("measured_setup_violation") is True for record in measured
        )
        report["retrieval_reference_observation_violation_count"] = sum(
            record.get("retrieval_reference_observation_ok") is False for record in measured
        )
        report["provider_usage_counts"] = {
            provider["id"]: sum(
                record.get("capability_usage", {}).get(provider["id"]) is True for record in measured
            )
            for provider in manifest["providers"]
        }
        return report

    def run_codex(command: list[str], prompt: str, workspace: Path, env: dict[str, str], *args: Any, **kwargs: Any):
        measured_env = dict(env)
        measured_env.update(capabilities.workspace_environment(workspace, measured_env))
        return original_run_codex(command, prompt, workspace, measured_env, *args, **kwargs)

    def run_cell(*args: Any, **kwargs: Any) -> dict[str, Any]:
        spec = args[0] if args else kwargs["spec"]
        output = args[6] if len(args) >= 7 else kwargs["output"]
        task_id, variant, repetition = spec
        cell = output / "cells" / task_id / variant.replace(":", "-") / f"r{repetition:03d}"
        result_path = cell / "result.json"
        setup_path = cell / "capability-setup.json"
        if result_path.is_file() and not setup_path.is_file():
            raise capabilities.CapabilitySetupError(
                f"refusing to reuse measured result without capability setup receipt: {result_path}"
            )

        record = original_run_cell(*args, **kwargs)
        record["measurement_phase"] = "measured"
        record["setup_included_in_comparison"] = False
        record["capability_setup_file"] = str(setup_path)
        record["capability_usage"] = contract.provider_usage(record.get("tool_commands", []))
        current_runtime = variant == "adaptive" or variant.startswith("cap:")
        if current_runtime:
            declared = [
                base.canonical_reference(reference)
                for reference in record.get("references_loaded", [])
                if base.canonical_reference(reference).startswith("references/retrieval/")
            ]
            observed = retrieval_trace.observed_references(record.get("tool_commands", []))
            observation_ok = declared == observed
            record["retrieval_reference_observation_ok"] = observation_ok
            record["observed_retrieval_references"] = observed
            if not observation_ok:
                record["passed"] = False
                record["verdict"] = "fail"
        else:
            record["retrieval_reference_observation_ok"] = None
            record["observed_retrieval_references"] = []
        if not setup_path.is_file():
            raise capabilities.CapabilitySetupError(f"missing setup receipt after cell execution: {setup_path}")
        setup = json.loads(setup_path.read_text(encoding="utf-8"))
        if setup.get("manifest_sha256") != capabilities.manifest_fingerprint(manifest):
            raise capabilities.CapabilitySetupError(f"stale setup receipt: {setup_path}")
        result_path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return record

    base.prepare_workspace = prepare_workspace
    base.parse_trace = retrieval_trace.parse_trace
    base.allowed_references = allowed_references
    base.task_prompt = task_prompt
    base.instrumentation = contract.instrumentation
    base.validate_trace = validate_trace
    base.infer_trace_from_commands = infer_trace_from_commands
    base.score_answer = score_answer
    base.summary = summary
    base.run_cell = run_cell
    base.bench.run_codex = run_codex

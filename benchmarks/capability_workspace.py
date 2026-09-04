"""Pre-measurement provider, index, dependency, and first-build setup."""

from __future__ import annotations

import json
import os
import threading
from pathlib import Path
from typing import Any, Mapping, Sequence

try:
    from .capability_manifest import SCHEMA_VERSION, CapabilitySetupError, manifest_fingerprint
    from .capability_process import Run, _default_run, _run_checked
except ImportError:  # direct script imports from the benchmarks directory
    from capability_manifest import SCHEMA_VERSION, CapabilitySetupError, manifest_fingerprint
    from capability_process import Run, _default_run, _run_checked

_SETUP_LOCK = threading.Lock()

def workspace_environment(
    workspace: Path,
    base_env: Mapping[str, str] | None = None,
) -> dict[str, str]:
    """Return benchmark-only environment additions for one workspace.

    Codebase Memory uses an account daemon. Giving concurrent cells different
    ``CBM_CACHE_DIR`` values can split the daemon cohort and make a paired run
    fail for an infrastructure reason. Therefore the benchmark inherits the
    host's existing cache cohort by default. Operators that need a dedicated
    cohort can set ``PRACTICAL_BENCHMARK_CBM_CACHE_DIR`` once for the whole run;
    every cell receives that same value.
    """

    source = dict(os.environ if base_env is None else base_env)
    state = workspace.parent / "capability-state"
    state.mkdir(parents=True, exist_ok=True)
    additions = {"PRACTICAL_CAPABILITY_STATE": str(state.resolve())}
    cbm_cache = source.get("PRACTICAL_BENCHMARK_CBM_CACHE_DIR") or source.get("CBM_CACHE_DIR")
    if cbm_cache:
        cache = Path(cbm_cache).expanduser().resolve()
        cache.mkdir(parents=True, exist_ok=True)
        additions["CBM_CACHE_DIR"] = str(cache)
    return additions


def _substitute(command: Sequence[str], workspace: Path) -> list[str]:
    value = str(workspace.resolve())
    return [part.replace("{workspace}", value) for part in command]


def _exclude_owned_paths(workspace: Path, paths: Sequence[str]) -> None:
    if not paths:
        return
    info = workspace / ".git" / "info"
    if not info.is_dir():
        raise CapabilitySetupError(f"workspace is not a normal Git checkout: {workspace}")
    exclude = info / "exclude"
    existing = exclude.read_text(encoding="utf-8", errors="replace").splitlines() if exclude.exists() else []
    additions = [path for path in paths if path not in existing]
    if additions:
        with exclude.open("a", encoding="utf-8") as handle:
            if existing and existing[-1] != "":
                handle.write("\n")
            handle.write("\n".join(additions) + "\n")


def prepare_workspace(
    workspace: Path,
    repository: str,
    manifest: Mapping[str, Any],
    preflight_report: Mapping[str, Any],
    *,
    runner: Run = _default_run,
    base_env: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    """Prepare one frozen cell before model timing begins.

    Setup is serialized to avoid concurrent first-download/cache races. The
    resulting report deliberately contains no token field.
    """

    workspace = workspace.resolve()
    if repository not in manifest["repository_warmups"]:
        raise CapabilitySetupError(f"repository has no warm-up contract: {repository}")
    if preflight_report.get("manifest_sha256") != manifest_fingerprint(manifest):
        raise CapabilitySetupError("preflight report does not match capability manifest")

    env = dict(os.environ if base_env is None else base_env)
    env.update(workspace_environment(workspace, env))
    resolved = dict(preflight_report["resolved_executables"])
    owned_paths = [
        path
        for provider in manifest["providers"]
        for path in provider.get("workspace_owned_paths", [])
    ]
    _exclude_owned_paths(workspace, owned_paths)

    provider_records: list[dict[str, Any]] = []
    provider_warmup_records: list[dict[str, Any]] = []
    warmup_records: list[dict[str, Any]] = []
    with _SETUP_LOCK:
        for provider in manifest["providers"]:
            command = _substitute(provider["prepare"], workspace)
            command[0] = resolved[provider["binary"]]
            record = _run_checked(
                command,
                cwd=workspace,
                env=env,
                timeout=float(provider["timeout_seconds"]),
                runner=runner,
                error_type=CapabilitySetupError,
                label=f"provider setup {provider['id']}",
            )
            record.update({"provider": provider["id"], "role": provider["role"]})
            provider_records.append(record)
            for warmup_index, item in enumerate(provider.get("warmup_commands", [])):
                warmup_command = _substitute(item["command"], workspace)
                if warmup_command[0] in resolved:
                    warmup_command[0] = resolved[warmup_command[0]]
                warmup_record = _run_checked(
                    warmup_command,
                    cwd=workspace,
                    env=env,
                    timeout=float(item["timeout_seconds"]),
                    runner=runner,
                    error_type=CapabilitySetupError,
                    label=f"provider warm-up {provider['id']}[{warmup_index}]",
                )
                warmup_record.update(
                    {"provider": provider["id"], "role": provider["role"], "index": warmup_index}
                )
                provider_warmup_records.append(warmup_record)

        warmup = manifest["repository_warmups"][repository]
        for index, item in enumerate(warmup.get("commands", [])):
            command = _substitute(item["command"], workspace)
            if command[0] in resolved:
                command[0] = resolved[command[0]]
            record = _run_checked(
                command,
                cwd=workspace,
                env=env,
                timeout=float(item["timeout_seconds"]),
                runner=runner,
                error_type=CapabilitySetupError,
                label=f"repository warm-up {repository}[{index}]",
            )
            record.update({"repository": repository, "index": index})
            warmup_records.append(record)

    _exclude_owned_paths(workspace, owned_paths)
    git = resolved.get("git")
    if not git:
        raise CapabilitySetupError("preflight receipt did not resolve required benchmark executable: git")
    clean_record = _run_checked(
        [git, "status", "--porcelain", "--untracked-files=all"],
        cwd=workspace,
        env=env,
        timeout=60,
        runner=runner,
        error_type=CapabilitySetupError,
        label="post-setup git status",
    )
    if clean_record["stdout_tail"].strip():
        raise CapabilitySetupError(f"capability setup dirtied frozen workspace: {clean_record['stdout_tail'].strip()}")

    return {
        "schema_version": SCHEMA_VERSION,
        "phase": "setup",
        "included_in_comparison": False,
        "profile": manifest["profile"],
        "manifest_sha256": manifest_fingerprint(manifest),
        "repository": repository,
        "workspace": str(workspace),
        "cbm_cache_cohort": env.get("CBM_CACHE_DIR", "provider-default"),
        "provider_setup": provider_records,
        "provider_warmup": provider_warmup_records,
        "repository_warmup": warmup_records,
        "post_setup_clean_check": clean_record,
        "measurement_begins_after_report": True,
    }


def write_report(path: Path, report: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def contains_token_key(value: Any) -> bool:
    """Test helper enforcing that setup reports never estimate model tokens."""

    if isinstance(value, dict):
        return any("token" in str(key).lower() or contains_token_key(item) for key, item in value.items())
    if isinstance(value, list):
        return any(contains_token_key(item) for item in value)
    return False

"""Executable resolution, probes, and auditable command records."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

try:
    from .capability_manifest import (
        SCHEMA_VERSION, CapabilityError, MissingCapabilityError, manifest_fingerprint
    )
except ImportError:  # direct script imports from the benchmarks directory
    from capability_manifest import (
        SCHEMA_VERSION, CapabilityError, MissingCapabilityError, manifest_fingerprint
    )

OUTPUT_TAIL_LIMIT = 12_000
Run = Callable[[Sequence[str], Path, Mapping[str, str], float], subprocess.CompletedProcess[str]]

def _default_run(command: Sequence[str], cwd: Path, env: Mapping[str, str], timeout: float) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(command),
        cwd=str(cwd),
        env=dict(env),
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
        check=False,
    )


def _tail(value: str) -> str:
    return value if len(value) <= OUTPUT_TAIL_LIMIT else value[-OUTPUT_TAIL_LIMIT:]


def _command_record(command: Sequence[str], result: subprocess.CompletedProcess[str], elapsed: float) -> dict[str, Any]:
    stdout = result.stdout or ""
    stderr = result.stderr or ""
    return {
        "command": list(command),
        "returncode": result.returncode,
        "elapsed_seconds": elapsed,
        "stdout_bytes": len(stdout.encode("utf-8", errors="replace")),
        "stderr_bytes": len(stderr.encode("utf-8", errors="replace")),
        "stdout_tail": _tail(stdout),
        "stderr_tail": _tail(stderr),
    }


def _run_checked(
    command: Sequence[str],
    *,
    cwd: Path,
    env: Mapping[str, str],
    timeout: float,
    runner: Run,
    error_type: type[CapabilityError],
    label: str,
) -> dict[str, Any]:
    started = time.monotonic()
    try:
        result = runner(command, cwd, env, timeout)
    except (OSError, subprocess.SubprocessError) as exc:
        raise error_type(f"{label} could not run: {exc}") from exc
    record = _command_record(command, result, time.monotonic() - started)
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "no output").strip()
        raise error_type(f"{label} failed with exit {result.returncode}: {detail[-2000:]}")
    return record


def _resolve(binary: str, which: Callable[[str], str | None]) -> str:
    resolved = which(binary)
    if not resolved:
        raise MissingCapabilityError(f"required benchmark executable is missing: {binary}")
    return str(Path(resolved).resolve())


def preflight(
    manifest: Mapping[str, Any],
    *,
    cwd: Path | None = None,
    env: Mapping[str, str] | None = None,
    runner: Run = _default_run,
    which: Callable[[str], str | None] = shutil.which,
) -> dict[str, Any]:
    """Resolve and probe every required provider and warm-up executable."""

    root = (cwd or Path.cwd()).resolve()
    base_env = dict(os.environ if env is None else env)
    resolved: dict[str, str] = {}
    probes: list[dict[str, Any]] = []

    for binary in manifest.get("runner_required_binaries", []):
        resolved[binary] = _resolve(binary, which)

    for provider in manifest["providers"]:
        binary = provider["binary"]
        resolved[binary] = _resolve(binary, which)
        command = list(provider["probe"])
        command[0] = resolved[binary]
        record = _run_checked(
            command,
            cwd=root,
            env=base_env,
            timeout=float(provider["timeout_seconds"]),
            runner=runner,
            error_type=MissingCapabilityError,
            label=f"provider probe {provider['id']}",
        )
        observed_version = "\n".join(
            part for part in (record.get("stdout_tail", ""), record.get("stderr_tail", "")) if part
        )
        version_regex = provider["version_regex"]
        if re.search(version_regex, observed_version) is None:
            raise MissingCapabilityError(
                f"provider probe {provider['id']} returned an unapproved version; "
                f"expected /{version_regex}/, observed: {observed_version.strip() or 'no output'}"
            )
        record.update(
            {
                "provider": provider["id"],
                "role": provider["role"],
                "version_regex": version_regex,
                "observed_version_output": observed_version.strip(),
            }
        )
        probes.append(record)

    for repository, spec in manifest["repository_warmups"].items():
        for binary in spec.get("required_binaries", []):
            if binary not in resolved:
                resolved[binary] = _resolve(binary, which)

    return {
        "schema_version": SCHEMA_VERSION,
        "phase": "setup-preflight",
        "included_in_comparison": False,
        "profile": manifest["profile"],
        "manifest_sha256": manifest_fingerprint(manifest),
        "resolved_executables": resolved,
        "provider_probes": probes,
    }


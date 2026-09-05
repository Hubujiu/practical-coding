"""Validation and fingerprinting for the dependency capability manifest."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any, Mapping

SCHEMA_VERSION = 1
class CapabilityError(RuntimeError):
    """Base class for dependency-profile failures."""


class CapabilityManifestError(CapabilityError):
    """The checked-in profile is malformed or weakens the measurement contract."""


class MissingCapabilityError(CapabilityError):
    """A required executable is absent or its probe fails."""


class CapabilitySetupError(CapabilityError):
    """A pre-measurement provider or repository warm-up failed."""


def _string_list(value: Any, label: str, *, allow_empty: bool = True) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(item, str) and item for item in value):
        raise CapabilityManifestError(f"{label} must be a list of non-empty strings")
    if not allow_empty and not value:
        raise CapabilityManifestError(f"{label} must not be empty")
    return list(value)


def load_manifest(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema_version") != SCHEMA_VERSION:
        raise CapabilityManifestError(f"unsupported capability manifest schema: {data.get('schema_version')!r}")
    if not isinstance(data.get("profile"), str) or not data["profile"]:
        raise CapabilityManifestError("profile must be a non-empty string")

    required_roles = set(_string_list(data.get("required_roles"), "required_roles", allow_empty=False))
    _string_list(data.get("runner_required_binaries", []), "runner_required_binaries")
    providers = data.get("providers")
    if not isinstance(providers, list) or not providers:
        raise CapabilityManifestError("providers must be a non-empty list")

    ids: set[str] = set()
    roles: set[str] = set()
    for index, provider in enumerate(providers):
        label = f"providers[{index}]"
        if not isinstance(provider, dict):
            raise CapabilityManifestError(f"{label} must be an object")
        provider_id = provider.get("id")
        role = provider.get("role")
        binary = provider.get("binary")
        if not all(isinstance(value, str) and value for value in (provider_id, role, binary)):
            raise CapabilityManifestError(f"{label} requires non-empty id, role, and binary")
        if provider_id in ids:
            raise CapabilityManifestError(f"duplicate provider id: {provider_id}")
        if role in roles:
            raise CapabilityManifestError(f"duplicate provider role: {role}")
        ids.add(provider_id)
        roles.add(role)
        _string_list(provider.get("probe"), f"{label}.probe", allow_empty=False)
        _string_list(provider.get("prepare"), f"{label}.prepare", allow_empty=False)
        version_regex = provider.get("version_regex")
        if not isinstance(version_regex, str) or not version_regex:
            raise CapabilityManifestError(f"{label}.version_regex must be a non-empty string")
        try:
            re.compile(version_regex)
        except re.error as exc:
            raise CapabilityManifestError(f"{label}.version_regex is invalid: {exc}") from exc
        warmup_commands = provider.get("warmup_commands", [])
        if not isinstance(warmup_commands, list):
            raise CapabilityManifestError(f"{label}.warmup_commands must be a list")
        for warmup_index, item in enumerate(warmup_commands):
            warmup_label = f"{label}.warmup_commands[{warmup_index}]"
            if not isinstance(item, dict):
                raise CapabilityManifestError(f"{warmup_label} must be an object")
            _string_list(item.get("command"), f"{warmup_label}.command", allow_empty=False)
            warmup_timeout = item.get("timeout_seconds")
            if not isinstance(warmup_timeout, (int, float)) or warmup_timeout <= 0:
                raise CapabilityManifestError(f"{warmup_label}.timeout_seconds must be positive")
        _string_list(provider.get("retrieval_stages", []), f"{label}.retrieval_stages")
        _string_list(provider.get("workspace_owned_paths", []), f"{label}.workspace_owned_paths")
        timeout = provider.get("timeout_seconds")
        if not isinstance(timeout, (int, float)) or timeout <= 0:
            raise CapabilityManifestError(f"{label}.timeout_seconds must be positive")

    if roles != required_roles:
        missing = sorted(required_roles - roles)
        unexpected = sorted(roles - required_roles)
        raise CapabilityManifestError(f"provider roles mismatch; missing={missing}, unexpected={unexpected}")

    warmups = data.get("repository_warmups")
    if not isinstance(warmups, dict):
        raise CapabilityManifestError("repository_warmups must be an object")
    for repository, spec in warmups.items():
        if not isinstance(repository, str) or not repository or not isinstance(spec, dict):
            raise CapabilityManifestError("repository_warmups entries must be named objects")
        _string_list(spec.get("required_binaries", []), f"repository_warmups.{repository}.required_binaries")
        commands = spec.get("commands", [])
        if not isinstance(commands, list):
            raise CapabilityManifestError(f"repository_warmups.{repository}.commands must be a list")
        for index, item in enumerate(commands):
            if not isinstance(item, dict):
                raise CapabilityManifestError(f"repository_warmups.{repository}.commands[{index}] must be an object")
            _string_list(item.get("command"), f"repository_warmups.{repository}.commands[{index}].command", allow_empty=False)
            timeout = item.get("timeout_seconds")
            if not isinstance(timeout, (int, float)) or timeout <= 0:
                raise CapabilityManifestError(
                    f"repository_warmups.{repository}.commands[{index}].timeout_seconds must be positive"
                )

    contract = data.get("measurement_contract")
    if not isinstance(contract, dict):
        raise CapabilityManifestError("measurement_contract must be an object")
    if contract.get("setup_phase") != "unmeasured":
        raise CapabilityManifestError("setup_phase must be unmeasured")
    if contract.get("setup_included_in_comparison") is not False:
        raise CapabilityManifestError("setup_included_in_comparison must be false")
    if contract.get("setup_token_estimate") is not False:
        raise CapabilityManifestError("setup_token_estimate must be false")
    if contract.get("measured_phase_starts") != "after_workspace_prepare":
        raise CapabilityManifestError("measured phase must start after workspace preparation")
    _string_list(contract.get("measured_fields"), "measurement_contract.measured_fields", allow_empty=False)
    _string_list(
        contract.get("forbidden_measured_setup_commands", []),
        "measurement_contract.forbidden_measured_setup_commands",
    )
    return data


def manifest_fingerprint(manifest: Mapping[str, Any]) -> str:
    encoded = json.dumps(manifest, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()

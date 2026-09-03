"""Frozen outbound wire profiles for execution-state model benchmarks."""

from __future__ import annotations

import base64
import copy
import hashlib
import json
import os
import threading
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any, Iterator, Mapping

from runtime import _skill_state_http_transport_impl as _impl
from runtime._skill_state_http_transport_impl import Endpoint
from runtime.skill_state_host import HostBoundaryError, audit_wire_request_against_manifest

WIRE_PROFILE_RESPONSES_JSON = "responses-json-v1"
WIRE_PROFILE_CODEX_SSE = "codex-sse-v1"
WIRE_PROFILES = (WIRE_PROFILE_RESPONSES_JSON, WIRE_PROFILE_CODEX_SSE)
WIRE_PROFILE_SCHEMA_VERSION = 1
DEFAULT_CODEX_RESPONSES_ENDPOINT = "https://chatgpt.com/backend-api/codex/responses"
DEFAULT_CODEX_TRUSTED_HOSTS = frozenset({"chatgpt.com"})
DEFAULT_CODEX_AUTH_PATH = Path.home() / ".codex" / "auth.json"
MAX_CODEX_AUTH_BYTES = 1024 * 1024
CODEX_ACCOUNT_ID_ENV = "PRACTICAL_CODING_CODEX_ACCOUNT_ID"
CODEX_ORIGINATOR = "codex_cli_rs"

_CODEX_REMOVED_FIELDS = frozenset({"background", "max_output_tokens", "truncation"})
_CODEX_CHANGED_FIELDS = frozenset({"stream", *_CODEX_REMOVED_FIELDS})
_FINAL_HISTORY_KEYS = frozenset(
    {
        "previous_response_id",
        "conversation",
        "conversation_id",
        "context_management",
        "prompt",
        "session",
        "session_id",
        "thread",
        "thread_id",
        "history",
        "parent_response_id",
        "resume_from",
    }
)
_CONTEXT_HEADER_FRAGMENTS = (
    *_impl._CONTEXT_HEADER_FRAGMENTS,
    "turn-state",
    "turn_state",
    "codex-turn",
)


@dataclass(frozen=True)
class CodexCredentials:
    access_token: str
    account_id: str | None


@dataclass(frozen=True)
class PreparedWireRequest:
    source_body: bytes
    wire_body: bytes
    profile_manifest: Mapping[str, Any]
    profile_audit: Mapping[str, Any]


@dataclass(frozen=True)
class TransportProfileContext:
    wire_profile: str = WIRE_PROFILE_RESPONSES_JSON
    artifact_directory: Path | None = None
    codex_account_id: str | None = None


_CONTEXT = threading.local()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def strict_json_object(payload: bytes, label: str) -> dict[str, Any]:
    if not isinstance(payload, bytes) or not payload:
        raise HostBoundaryError(f"{label} must be non-empty bytes")

    def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise HostBoundaryError(f"{label} contains duplicate key {key!r}")
            result[key] = value
        return result

    def reject_constant(value: str) -> Any:
        raise HostBoundaryError(f"{label} contains non-finite number {value}")

    try:
        value = json.loads(
            payload.decode("utf-8"),
            object_pairs_hook=unique_object,
            parse_constant=reject_constant,
        )
    except HostBoundaryError:
        raise
    except (UnicodeDecodeError, json.JSONDecodeError, RecursionError, ValueError) as exc:
        raise HostBoundaryError(f"invalid JSON in {label}: {exc}") from exc
    if not isinstance(value, dict):
        raise HostBoundaryError(f"{label} must be a JSON object")
    return value


def _manifest_digest(value: Mapping[str, Any]) -> str:
    unsigned = dict(value)
    unsigned.pop("manifest_sha256", None)
    return sha256_bytes(canonical_json_bytes(unsigned))


def wire_profile_contract_manifest(profile: str) -> dict[str, Any]:
    if profile not in WIRE_PROFILES:
        raise HostBoundaryError(f"unsupported wire profile: {profile}")
    if profile == WIRE_PROFILE_RESPONSES_JSON:
        transformation: dict[str, Any] = {
            "mode": "identity",
            "allowed_changed_fields": [],
            "response_encoding": "application/json",
            "output_token_limit": "request-field",
        }
        final_contract = {
            "stream": False,
            "background": False,
            "truncation": "disabled",
            "max_output_tokens": "present-positive-integer",
        }
    else:
        transformation = {
            "mode": "declared-field-transform",
            "allowed_changed_fields": sorted(_CODEX_CHANGED_FIELDS),
            "set": {"stream": True},
            "remove": sorted(_CODEX_REMOVED_FIELDS),
            "response_encoding": "text/event-stream",
            "output_token_limit": "provider-managed",
        }
        final_contract = {
            "stream": True,
            "background": "absent",
            "truncation": "absent",
            "max_output_tokens": "absent",
        }
    manifest: dict[str, Any] = {
        "schema_version": WIRE_PROFILE_SCHEMA_VERSION,
        "profile": profile,
        "source_contract": {
            "store": False,
            "stream": False,
            "background": False,
            "truncation": "disabled",
            "max_output_tokens": "present-positive-integer",
        },
        "transformation": transformation,
        "final_contract": final_contract,
        "history_fields_forbidden_at_top_level": sorted(_FINAL_HISTORY_KEYS),
        "cookies_sent": False,
        "environment_proxy_used": False,
    }
    manifest["manifest_sha256"] = _manifest_digest(manifest)
    return manifest


def validate_wire_profile_contract_manifest(value: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise HostBoundaryError("wire-profile manifest must be an object")
    manifest = copy.deepcopy(dict(value))
    expected = wire_profile_contract_manifest(str(manifest.get("profile", "")))
    if manifest != expected:
        raise HostBoundaryError(
            "wire-profile contract manifest does not match the frozen profile"
        )
    return manifest


def instance_manifest(
    *,
    profile: str,
    endpoint: Endpoint,
    source_host_manifest: Mapping[str, Any] | None,
    account_id_header_present: bool,
) -> dict[str, Any]:
    contract = wire_profile_contract_manifest(profile)
    manifest: dict[str, Any] = {
        "schema_version": WIRE_PROFILE_SCHEMA_VERSION,
        "profile_contract_sha256": contract["manifest_sha256"],
        "profile": profile,
        "endpoint": {
            "scheme": endpoint.scheme,
            "host": endpoint.host,
            "port": endpoint.port,
            "target": endpoint.target,
        },
        "source_host_manifest_sha256": (
            source_host_manifest.get("manifest_sha256")
            if isinstance(source_host_manifest, Mapping)
            else None
        ),
        "request_header_contract": {
            "authorization": "bearer-present-redacted",
            "chatgpt_account_id": (
                "present-redacted"
                if profile == WIRE_PROFILE_CODEX_SSE and account_id_header_present
                else "absent"
            ),
            "originator": CODEX_ORIGINATOR if profile == WIRE_PROFILE_CODEX_SSE else None,
            "cookie": "absent",
            "context_headers": "absent",
            "environment_proxy": "bypassed",
        },
        "response_contract": {
            "encoding": (
                "text/event-stream"
                if profile == WIRE_PROFILE_CODEX_SSE
                else "application/json"
            ),
            "normalization": (
                "response.completed+response.output_item.done"
                if profile == WIRE_PROFILE_CODEX_SSE
                else "identity"
            ),
        },
    }
    manifest["manifest_sha256"] = _manifest_digest(manifest)
    return manifest


def _changed_fields(source: Mapping[str, Any], wire: Mapping[str, Any]) -> list[str]:
    keys = set(source) | set(wire)
    return sorted(
        key
        for key in keys
        if (key in source) != (key in wire) or source.get(key) != wire.get(key)
    )


def _validate_source_contract(source: Mapping[str, Any]) -> int:
    if source.get("store") is not False:
        raise HostBoundaryError("source request must set store=false")
    if source.get("stream") is not False:
        raise HostBoundaryError("source request must set stream=false")
    if source.get("background") is not False:
        raise HostBoundaryError("source request must set background=false")
    if source.get("truncation") != "disabled":
        raise HostBoundaryError("source request must set truncation=disabled")
    limit = source.get("max_output_tokens")
    if type(limit) is not int or limit <= 0:
        raise HostBoundaryError(
            "source request must contain a positive max_output_tokens"
        )
    return limit


def prepare_profiled_request(
    source_body: bytes,
    *,
    profile: str,
    endpoint: Endpoint,
    source_host_manifest: Mapping[str, Any] | None = None,
    account_id_header_present: bool = False,
) -> PreparedWireRequest:
    contract = wire_profile_contract_manifest(profile)
    source = strict_json_object(source_body, "source request")
    source_max_output_tokens = _validate_source_contract(source)
    source_host_audit: dict[str, Any] | None = None
    if source_host_manifest is not None:
        source_host_audit = dict(
            audit_wire_request_against_manifest(source_body, source_host_manifest)
        )

    wire = copy.deepcopy(source)
    if profile == WIRE_PROFILE_CODEX_SSE:
        wire["stream"] = True
        for field in _CODEX_REMOVED_FIELDS:
            wire.pop(field, None)
    elif profile != WIRE_PROFILE_RESPONSES_JSON:
        raise HostBoundaryError(f"unsupported wire profile: {profile}")

    changes = _changed_fields(source, wire)
    expected = sorted(_CODEX_CHANGED_FIELDS) if profile == WIRE_PROFILE_CODEX_SSE else []
    if changes != expected:
        raise HostBoundaryError(
            f"wire transformation changed unexpected fields: expected={expected}, actual={changes}"
        )
    if wire.get("store") is not False:
        raise HostBoundaryError("final wire request must keep store=false")
    present_history = sorted(key for key in _FINAL_HISTORY_KEYS if key in wire)
    if present_history:
        raise HostBoundaryError(
            f"final wire request contains history fields: {present_history}"
        )
    if profile == WIRE_PROFILE_CODEX_SSE:
        if wire.get("stream") is not True:
            raise HostBoundaryError("Codex SSE final request must set stream=true")
        retained = sorted(_CODEX_REMOVED_FIELDS & set(wire))
        if retained:
            raise HostBoundaryError(
                f"Codex SSE final request retained removed fields: {retained}"
            )
    else:
        _validate_source_contract(wire)

    wire_body = canonical_json_bytes(wire)
    manifest = instance_manifest(
        profile=profile,
        endpoint=endpoint,
        source_host_manifest=source_host_manifest,
        account_id_header_present=account_id_header_present,
    )
    source_host_match = (
        source_host_audit.get("manifest_match") is True
        if source_host_audit is not None
        else None
    )
    source_bounded = (
        source_host_audit.get("bounded_context_eligible") is True
        if source_host_audit is not None
        else None
    )
    audit: dict[str, Any] = {
        "schema_version": WIRE_PROFILE_SCHEMA_VERSION,
        "wire_profile": profile,
        "wire_profile_contract_sha256": contract["manifest_sha256"],
        "wire_profile_manifest_sha256": manifest["manifest_sha256"],
        "wire_profile_manifest_match": True,
        "source_request_sha256": sha256_bytes(source_body),
        "source_request_bytes": len(source_body),
        "wire_request_sha256": sha256_bytes(wire_body),
        "wire_request_bytes": len(wire_body),
        "changed_fields": changes,
        "source_stream": source.get("stream"),
        "wire_stream": wire.get("stream"),
        "source_max_output_tokens": source_max_output_tokens,
        "wire_max_output_tokens_present": "max_output_tokens" in wire,
        "output_token_limit": contract["transformation"]["output_token_limit"],
        "source_host_manifest_supplied": source_host_manifest is not None,
        "source_host_manifest_match": source_host_match,
        "source_bounded_context_eligible": source_bounded,
        "final_history_fields_absent": True,
        "final_wire_contract_pass": True,
        "bounded_context_eligible": bool(source_bounded),
    }
    if source_host_audit is not None:
        audit["source_host_body_audit"] = source_host_audit
    return PreparedWireRequest(
        source_body=source_body,
        wire_body=wire_body,
        profile_manifest=MappingProxyType(manifest),
        profile_audit=MappingProxyType(audit),
    )


def _account_id_from_id_token(value: Any) -> str | None:
    if isinstance(value, Mapping):
        direct = value.get("chatgpt_account_id")
        if isinstance(direct, str) and direct.strip():
            return direct.strip()
        return _account_id_from_id_token(value.get("raw_jwt"))
    if not isinstance(value, str):
        return None
    parts = value.split(".")
    if len(parts) != 3 or not parts[1]:
        return None
    try:
        padded = parts[1] + "=" * (-len(parts[1]) % 4)
        claims = json.loads(base64.urlsafe_b64decode(padded).decode("utf-8"))
    except (ValueError, UnicodeDecodeError, json.JSONDecodeError):
        return None
    if not isinstance(claims, Mapping):
        return None
    auth = claims.get("https://api.openai.com/auth")
    if not isinstance(auth, Mapping):
        return None
    account_id = auth.get("chatgpt_account_id")
    return account_id.strip() if isinstance(account_id, str) and account_id.strip() else None


def load_codex_credentials(path: Path | str = DEFAULT_CODEX_AUTH_PATH) -> CodexCredentials:
    auth_path = Path(path).expanduser()
    try:
        raw = auth_path.read_bytes()
    except OSError as exc:
        raise HostBoundaryError(f"cannot read Codex auth file {auth_path}: {exc}") from exc
    if len(raw) > MAX_CODEX_AUTH_BYTES:
        raise HostBoundaryError(
            f"Codex auth file exceeds {MAX_CODEX_AUTH_BYTES} bytes"
        )
    value = strict_json_object(raw, "Codex auth file")
    token_scope = value.get("tokens") if isinstance(value.get("tokens"), Mapping) else value
    access_token = token_scope.get("access_token") if isinstance(token_scope, Mapping) else None
    account_id = token_scope.get("account_id") if isinstance(token_scope, Mapping) else None
    if account_id is None and isinstance(token_scope, Mapping):
        account_id = _account_id_from_id_token(token_scope.get("id_token"))
    if not isinstance(access_token, str) or not access_token.strip():
        raise HostBoundaryError("Codex auth file has no non-empty access_token")
    if any(character in access_token for character in "\r\n\x00"):
        raise HostBoundaryError("Codex access_token contains a disallowed control character")
    if account_id is not None:
        if not isinstance(account_id, str) or not account_id.strip():
            raise HostBoundaryError(
                "Codex account_id must be a non-empty string when present"
            )
        if any(character in account_id for character in "\r\n\x00"):
            raise HostBoundaryError(
                "Codex account_id contains a disallowed control character"
            )
        account_id = account_id.strip()
    return CodexCredentials(
        access_token=access_token.strip(),
        account_id=account_id,
    )


def active_transport_context() -> TransportProfileContext:
    value = getattr(_CONTEXT, "value", None)
    return value if isinstance(value, TransportProfileContext) else TransportProfileContext()


@contextmanager
def transport_profile_context(
    *,
    wire_profile: str,
    artifact_directory: Path | None = None,
    codex_account_id: str | None = None,
) -> Iterator[None]:
    if wire_profile not in WIRE_PROFILES:
        raise HostBoundaryError(f"unsupported wire profile: {wire_profile}")
    previous = getattr(_CONTEXT, "value", None)
    _CONTEXT.value = TransportProfileContext(
        wire_profile=wire_profile,
        artifact_directory=artifact_directory,
        codex_account_id=codex_account_id,
    )
    try:
        yield
    finally:
        if previous is None:
            try:
                delattr(_CONTEXT, "value")
            except AttributeError:
                pass
        else:
            _CONTEXT.value = previous


def context_header_names(names: list[str]) -> list[str]:
    matched: set[str] = set()
    for name in names:
        lowered = name.lower()
        if any(fragment in lowered for fragment in _CONTEXT_HEADER_FRAGMENTS):
            matched.add(lowered)
    return sorted(matched)

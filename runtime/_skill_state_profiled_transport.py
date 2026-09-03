"""Direct profiled HTTP transport with final outbound audit artifacts."""

from __future__ import annotations

import copy
import http.client
import json
import os
import ssl
import threading
import time
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping

from runtime import _skill_state_http_transport_impl as _impl
from runtime._skill_state_sse import normalize_sse_response
from runtime._skill_state_wire_profile import (
    CODEX_ACCOUNT_ID_ENV,
    CODEX_ORIGINATOR,
    WIRE_PROFILE_CODEX_SSE,
    WIRE_PROFILE_RESPONSES_JSON,
    WIRE_PROFILES,
    active_transport_context,
    canonical_json_bytes,
    context_header_names,
    instance_manifest,
    prepare_profiled_request,
    sha256_bytes,
)
from runtime.skill_state_host import (
    HostBoundaryError,
    HostTransportError,
    TransportResponse,
)


class ExactResponsesTransport(_impl.ExactResponsesTransport):
    """Send one frozen final wire profile without SDK history reconstruction.

    The inherited ``responses-json-v1`` behavior remains available.  The
    ``codex-sse-v1`` profile transforms exactly four declared body fields, adds
    the explicit ChatGPT account/originator headers, retains the raw SSE stream,
    and normalizes only a completed response for the existing runner.
    """

    def __init__(
        self,
        *,
        wire_profile: str | None = None,
        artifact_directory: Path | None = None,
        codex_account_id: str | None = None,
        **kwargs: Any,
    ) -> None:
        context = active_transport_context()
        profile = wire_profile or context.wire_profile
        if profile not in WIRE_PROFILES:
            raise HostBoundaryError(f"unsupported wire profile: {profile}")
        account_id = (
            codex_account_id
            or context.codex_account_id
            or os.environ.get(CODEX_ACCOUNT_ID_ENV)
        )
        additional_headers = dict(kwargs.pop("additional_headers", {}) or {})
        if profile == WIRE_PROFILE_CODEX_SSE:
            if not isinstance(account_id, str) or not account_id.strip():
                raise HostBoundaryError(
                    "codex-sse-v1 requires a ChatGPT account ID from Codex auth or "
                    f"{CODEX_ACCOUNT_ID_ENV}"
                )
            additional_headers.setdefault("ChatGPT-Account-ID", account_id.strip())
            additional_headers.setdefault("originator", CODEX_ORIGINATOR)
        kwargs["additional_headers"] = additional_headers
        super().__init__(**kwargs)
        self._wire_profile = profile
        self._artifact_directory = artifact_directory or context.artifact_directory
        self._codex_account_id_present = bool(account_id and str(account_id).strip())
        self._profile_manifest = instance_manifest(
            profile=profile,
            endpoint=self._endpoint,
            source_host_manifest=self._manifest,
            account_id_header_present=self._codex_account_id_present,
        )
        self._profile_sequence = 0
        self._profile_lock = threading.Lock()
        self._raw_responses: dict[str, bytes] = {}
        self._wire_requests: dict[str, bytes] = {}
        if self._artifact_directory is not None:
            self._artifact_directory.mkdir(parents=True, exist_ok=True)
            self._write_artifact_json(
                "wire-profile-manifest.json", self._profile_manifest
            )

    @property
    def wire_profile(self) -> str:
        return self._wire_profile

    @property
    def wire_profile_manifest(self) -> Mapping[str, Any]:
        return MappingProxyType(copy.deepcopy(self._profile_manifest))

    def _write_artifact_json(self, name: str, value: Mapping[str, Any]) -> None:
        if self._artifact_directory is None:
            return
        path = self._artifact_directory / name
        path.write_text(
            json.dumps(
                dict(value),
                ensure_ascii=False,
                sort_keys=True,
                indent=2,
                allow_nan=False,
            )
            + "\n",
            encoding="utf-8",
        )

    def prepare_request(self, source_body: bytes):
        return prepare_profiled_request(
            source_body,
            profile=self._wire_profile,
            endpoint=self._endpoint,
            source_host_manifest=self._manifest,
            account_id_header_present=self._codex_account_id_present,
        )

    def raw_response_for_source_sha256(self, digest: str) -> bytes | None:
        return self._raw_responses.get(digest)

    def wire_request_for_source_sha256(self, digest: str) -> bytes | None:
        return self._wire_requests.get(digest)

    def _headers(self, body: bytes) -> dict[str, str]:
        headers = super()._headers(body)
        if self._wire_profile == WIRE_PROFILE_CODEX_SSE:
            headers["Accept"] = "text/event-stream"
        return headers

    def __call__(self, body: bytes) -> TransportResponse:
        prepared = self.prepare_request(body)
        wire_body = prepared.wire_body
        source_digest = sha256_bytes(body)

        with self._profile_lock:
            self._profile_sequence += 1
            sequence = self._profile_sequence
        prefix = f"request-{sequence:04d}"
        source_name = f"{prefix}.source.json"
        wire_name = f"{prefix}.wire.json"
        raw_name = (
            f"{prefix}.response.raw.sse"
            if self._wire_profile == WIRE_PROFILE_CODEX_SSE
            else f"{prefix}.response.raw.json"
        )
        normalized_name = f"{prefix}.response.normalized.json"
        audit_name = f"{prefix}.transport-audit.json"
        if self._artifact_directory is not None:
            # Persist both identities before network I/O.  A connection failure
            # must not erase the exact final request that was attempted.
            (self._artifact_directory / source_name).write_bytes(body)
            (self._artifact_directory / wire_name).write_bytes(wire_body)

        request_headers = self._headers(wire_body)
        request_header_items = list(request_headers.items())
        request_context_headers = context_header_names(list(request_headers))
        environment_proxy_names = sorted(
            key for key in _impl.PROXY_ENVIRONMENT_KEYS if os.environ.get(key)
        )
        endpoint_trusted = self._endpoint.host in self._trusted_endpoint_hosts
        request_cookie_present = any(
            name.lower() == "cookie" for name, _ in request_header_items
        )
        content_length_matches = request_headers["Content-Length"] == str(
            len(wire_body)
        )
        profile_audit = dict(prepared.profile_audit)
        source_host_manifest_match = profile_audit.get(
            "source_host_manifest_match"
        )
        bounded_context_eligible = profile_audit.get("bounded_context_eligible")
        final_wire_contract_pass = (
            profile_audit.get("final_wire_contract_pass") is True
        )
        profile_match = profile_audit.get("wire_profile_manifest_match") is True
        transport_context_gate = bool(
            self._manifest is not None
            and source_host_manifest_match is True
            and bounded_context_eligible is True
            and final_wire_contract_pass
            and profile_match
            and not request_cookie_present
            and not request_context_headers
            and endpoint_trusted
            and content_length_matches
            and (self._endpoint.scheme == "https" or self._allow_insecure_http)
        )

        common_audit: dict[str, Any] = {
            "schema_version": 2,
            "wire_profile": self._wire_profile,
            "wire_profile_manifest_sha256": self._profile_manifest[
                "manifest_sha256"
            ],
            "wire_profile_contract_sha256": profile_audit[
                "wire_profile_contract_sha256"
            ],
            "wire_profile_manifest_match": profile_match,
            "final_wire_contract_pass": final_wire_contract_pass,
            "source_body_sha256": source_digest,
            "source_body_bytes": len(body),
            "request_body_sha256": sha256_bytes(wire_body),
            "request_body_bytes": len(wire_body),
            "source_to_wire_changed_fields": profile_audit["changed_fields"],
            "content_length": int(request_headers["Content-Length"]),
            "content_length_matches": content_length_matches,
            "method": "POST",
            "endpoint_scheme": self._endpoint.scheme,
            "endpoint_host": self._endpoint.host,
            "endpoint_port": self._endpoint.port,
            "endpoint_target": self._endpoint.target,
            "tls_enabled": self._endpoint.scheme == "https",
            "endpoint_trusted": endpoint_trusted,
            "trusted_endpoint_hosts": sorted(self._trusted_endpoint_hosts),
            "environment_proxy_variables_present": environment_proxy_names,
            "environment_proxy_bypassed": True,
            "cookie_jar_used": False,
            "redirects_followed": False,
            "connection_reused": False,
            "request_cookie_present": request_cookie_present,
            "request_context_header_names": request_context_headers,
            "request_header_names": sorted(
                name.lower() for name in request_headers
            ),
            "request_headers_redacted": _impl._redacted_headers(
                request_header_items
            ),
            "request_headers_sha256": sha256_bytes(
                canonical_json_bytes(
                    _impl._redacted_headers(request_header_items)
                )
            ),
            "authorization_sha256": _impl._sha256_text(
                request_headers["Authorization"]
            ),
            "chatgpt_account_id_header_present": any(
                name.lower() == "chatgpt-account-id"
                for name, _ in request_header_items
            ),
            "originator_header_present": any(
                name.lower() == "originator"
                for name, _ in request_header_items
            ),
            "manifest_supplied": self._manifest is not None,
            "manifest_match": source_host_manifest_match,
            "bounded_context_eligible": bounded_context_eligible,
            "transport_context_gate": transport_context_gate,
            "wire_profile_audit": profile_audit,
            "claim_scope": (
                "exact transformed wire bytes and controlled headers supplied by "
                "this direct client; provider-internal context is not established"
            ),
        }
        source_host_body_audit = profile_audit.get("source_host_body_audit")
        if isinstance(source_host_body_audit, Mapping):
            # Stable compatibility field consumed by the bounded-context analyzer.
            common_audit["host_body_audit"] = copy.deepcopy(
                dict(source_host_body_audit)
            )

        started = time.perf_counter_ns()
        raw_response_body = b""
        response_status = 0
        response_headers: list[tuple[str, str]] = []
        connection = self._connection()
        try:
            connection.request(
                "POST",
                self._endpoint.target,
                body=wire_body,
                headers=request_headers,
                encode_chunked=False,
            )
            response = connection.getresponse()
            response_status = int(response.status)
            response_headers = [
                (str(name), str(value)) for name, value in response.getheaders()
            ]
            raw_response_body = response.read(self._max_response_bytes + 1)
            if len(raw_response_body) > self._max_response_bytes:
                raise HostTransportError(
                    f"response body exceeds {self._max_response_bytes} bytes"
                )
        except (
            OSError,
            ssl.SSLError,
            http.client.HTTPException,
            HostTransportError,
        ) as exc:
            elapsed_ms = (time.perf_counter_ns() - started) / 1_000_000
            audit: dict[str, Any] = {
                **common_audit,
                "response_status": response_status or None,
                "raw_response_body_bytes": len(raw_response_body),
                "raw_response_body_sha256": (
                    sha256_bytes(raw_response_body)
                    if raw_response_body
                    else None
                ),
                "response_body_bytes": None,
                "response_body_sha256": None,
                "response_set_cookie_count": None,
                "response_cookie_replayed": False,
                "response_context_header_names": [],
                "response_context_header_replayed": False,
                "response_request_id": None,
                "elapsed_ms": elapsed_ms,
                "transport_failure": f"{type(exc).__name__}: {exc}",
                "artifact_paths": {
                    "source_request": source_name,
                    "wire_request": wire_name,
                    "transport_audit": audit_name,
                    "wire_profile_manifest": "wire-profile-manifest.json",
                },
            }
            if self._artifact_directory is not None:
                if raw_response_body:
                    (self._artifact_directory / raw_name).write_bytes(
                        raw_response_body
                    )
                    audit["artifact_paths"]["raw_response"] = raw_name
                self._write_artifact_json(audit_name, audit)
            frozen_audit = MappingProxyType(audit)
            with self._lock:
                self._audits.append(frozen_audit)
            self._wire_requests[source_digest] = wire_body
            if raw_response_body:
                self._raw_responses[source_digest] = raw_response_body
            raise HostTransportError(
                f"exact HTTP transport failed: {exc}"
            ) from exc
        finally:
            connection.close()
        elapsed_ms = (time.perf_counter_ns() - started) / 1_000_000

        normalized_body = raw_response_body
        sse_metadata: Mapping[str, Any] | None = None
        normalization_error: HostTransportError | None = None
        if (
            self._wire_profile == WIRE_PROFILE_CODEX_SSE
            and 200 <= response_status < 300
        ):
            try:
                normalized_body, sse_metadata = normalize_sse_response(
                    raw_response_body
                )
            except HostTransportError as exc:
                normalization_error = exc

        response_names = [name.lower() for name, _ in response_headers]
        response_context_headers = context_header_names(response_names)
        set_cookie_count = sum(
            name == "set-cookie" for name in response_names
        )
        response_lookup: dict[str, str] = {}
        for name, value in response_headers:
            response_lookup.setdefault(name.lower(), value)

        audit = {
            **common_audit,
            "response_status": response_status,
            "response_wire_encoding": (
                "text/event-stream"
                if self._wire_profile == WIRE_PROFILE_CODEX_SSE
                else "application/json"
            ),
            "raw_response_body_bytes": len(raw_response_body),
            "raw_response_body_sha256": sha256_bytes(raw_response_body),
            "response_body_bytes": (
                len(normalized_body) if normalization_error is None else None
            ),
            "response_body_sha256": (
                sha256_bytes(normalized_body)
                if normalization_error is None
                else None
            ),
            "response_header_names": sorted(response_names),
            "response_headers_redacted": _impl._redacted_headers(
                response_headers
            ),
            "response_set_cookie_count": set_cookie_count,
            "response_cookie_replayed": False,
            "response_context_header_names": response_context_headers,
            "response_context_header_replayed": False,
            "response_request_id": response_lookup.get("x-request-id"),
            "elapsed_ms": elapsed_ms,
            "normalization_error": (
                str(normalization_error)
                if normalization_error is not None
                else None
            ),
            "artifact_paths": {
                "source_request": source_name,
                "wire_request": wire_name,
                "raw_response": raw_name,
                "transport_audit": audit_name,
                "wire_profile_manifest": "wire-profile-manifest.json",
            },
        }
        if sse_metadata is not None:
            audit["sse"] = dict(sse_metadata)
        if normalization_error is None:
            audit["artifact_paths"]["normalized_response"] = normalized_name

        if self._artifact_directory is not None:
            (self._artifact_directory / raw_name).write_bytes(raw_response_body)
            if normalization_error is None:
                (self._artifact_directory / normalized_name).write_bytes(
                    normalized_body
                )
            self._write_artifact_json(audit_name, audit)

        frozen_audit = MappingProxyType(audit)
        with self._lock:
            self._audits.append(frozen_audit)
        self._raw_responses[source_digest] = raw_response_body
        self._wire_requests[source_digest] = wire_body

        if normalization_error is not None:
            raise HostTransportError(
                "SSE response was captured but could not be normalized: "
                f"{normalization_error}"
            ) from normalization_error

        return TransportResponse(
            body=normalized_body,
            status_code=response_status,
            headers={name.lower(): value for name, value in response_headers},
        )


def transport_audit_passes(audit: Mapping[str, Any]) -> bool:
    """Return whether one final outbound history-free audit is determinate/pass."""

    return bool(
        audit.get("transport_context_gate") is True
        and audit.get("content_length_matches") is True
        and audit.get("request_cookie_present") is False
        and not audit.get("request_context_header_names")
        and audit.get("environment_proxy_bypassed") is True
        and audit.get("response_cookie_replayed") is False
        and audit.get("response_context_header_replayed") is False
        and audit.get("manifest_match") is True
        and audit.get("bounded_context_eligible") is True
        and audit.get("wire_profile_manifest_match") is True
        and audit.get("final_wire_contract_pass") is True
        and audit.get("normalization_error") in (None, "")
        and not audit.get("transport_failure")
    )


__all__ = ["ExactResponsesTransport", "transport_audit_passes"]

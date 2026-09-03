#!/usr/bin/env python3
"""Exact-byte HTTP transport and outbound-context audit for state benchmarks.

The transport deliberately avoids SDK-managed conversations, cookie jars,
connection pools, redirects, and environment proxies.  It sends the exact bytes
supplied by ``HistoryFreeHost`` and records a redacted audit of the body, headers,
endpoint, proxy boundary, response cookies, and latency.  Passing this audit is a
client-side transport statement; it does not establish provider-internal context
or data-retention behavior.
"""

from __future__ import annotations

import hashlib
import http.client
import json
import os
import ssl
import threading
import time
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Mapping, Sequence
from urllib.parse import urlsplit

from runtime.skill_state_host import (
    HostBoundaryError,
    HostTransportError,
    TransportResponse,
    audit_wire_request_against_manifest,
)

DEFAULT_RESPONSES_ENDPOINT = "https://api.openai.com/v1/responses"
DEFAULT_MAX_RESPONSE_BYTES = 4 * 1024 * 1024
DEFAULT_TRUSTED_ENDPOINT_HOSTS = frozenset({"api.openai.com"})
PROXY_ENVIRONMENT_KEYS = (
    "HTTP_PROXY",
    "HTTPS_PROXY",
    "ALL_PROXY",
    "NO_PROXY",
    "http_proxy",
    "https_proxy",
    "all_proxy",
    "no_proxy",
)
_CONTEXT_HEADER_FRAGMENTS = (
    "cookie",
    "session",
    "conversation",
    "thread",
    "history",
    "previous-response",
    "previous_response",
    "context-id",
    "context_id",
    "memory",
)
_PROTECTED_HEADER_NAMES = frozenset(
    {
        "authorization",
        "content-type",
        "content-length",
        "accept",
        "accept-encoding",
        "host",
        "connection",
        "cookie",
        "transfer-encoding",
    }
)


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_text(value: str) -> str:
    return _sha256_bytes(value.encode("utf-8"))


def _header_name(name: str) -> str:
    if not isinstance(name, str) or not name.strip():
        raise HostBoundaryError("HTTP header names must be non-empty strings")
    if any(character in name for character in "\r\n:"):
        raise HostBoundaryError(f"invalid HTTP header name: {name!r}")
    return name.strip()


def _header_value(value: str) -> str:
    if not isinstance(value, str):
        raise HostBoundaryError("HTTP header values must be strings")
    if "\r" in value or "\n" in value:
        raise HostBoundaryError("HTTP header values must not contain CR or LF")
    return value


def _context_header_names(names: Sequence[str]) -> list[str]:
    matched: list[str] = []
    for name in names:
        lowered = name.lower()
        if any(fragment in lowered for fragment in _CONTEXT_HEADER_FRAGMENTS):
            matched.append(lowered)
    return sorted(set(matched))


def _redacted_headers(headers: Sequence[tuple[str, str]]) -> list[dict[str, str]]:
    return [
        {
            "name": name.lower(),
            "value_sha256": _sha256_text(value),
        }
        for name, value in sorted(headers, key=lambda item: (item[0].lower(), item[1]))
    ]


def _canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


@dataclass(frozen=True)
class Endpoint:
    scheme: str
    host: str
    port: int | None
    target: str

    @classmethod
    def parse(cls, raw: str, *, allow_insecure_http: bool = False) -> "Endpoint":
        if not isinstance(raw, str) or not raw.strip():
            raise HostBoundaryError("responses endpoint must be a non-empty URL")
        parsed = urlsplit(raw.strip())
        if parsed.scheme not in {"https", "http"}:
            raise HostBoundaryError("responses endpoint scheme must be https or http")
        if parsed.scheme == "http" and not allow_insecure_http:
            raise HostBoundaryError("plain HTTP requires allow_insecure_http=True")
        if parsed.username or parsed.password:
            raise HostBoundaryError("responses endpoint must not contain credentials")
        if parsed.fragment:
            raise HostBoundaryError("responses endpoint must not contain a fragment")
        if not parsed.hostname:
            raise HostBoundaryError("responses endpoint must contain a hostname")
        path = parsed.path or "/v1/responses"
        target = path + (f"?{parsed.query}" if parsed.query else "")
        try:
            port = parsed.port
        except ValueError as exc:
            raise HostBoundaryError(f"invalid responses endpoint port: {exc}") from exc
        return cls(parsed.scheme, parsed.hostname.lower(), port, target)


class ExactResponsesTransport:
    """Send exact Responses API request bytes and retain redacted outbound audits.

    A new ``http.client`` connection is created for every call.  No cookie jar,
    redirect handler, SDK response chain, or environment proxy is consulted.
    ``audits`` is append-only for the lifetime of this transport instance.
    """

    def __init__(
        self,
        *,
        api_key: str,
        endpoint: str = DEFAULT_RESPONSES_ENDPOINT,
        timeout_seconds: float = 180.0,
        max_response_bytes: int = DEFAULT_MAX_RESPONSE_BYTES,
        manifest: Mapping[str, Any] | None = None,
        additional_headers: Mapping[str, str] | None = None,
        trusted_endpoint_hosts: Sequence[str] = tuple(DEFAULT_TRUSTED_ENDPOINT_HOSTS),
        allow_insecure_http: bool = False,
        user_agent: str = "practical-coding-skill-state-benchmark/1.0",
    ) -> None:
        if not isinstance(api_key, str) or not api_key.strip():
            raise HostBoundaryError("api_key must be a non-empty string")
        if type(timeout_seconds) not in {int, float} or timeout_seconds <= 0:
            raise HostBoundaryError("timeout_seconds must be positive")
        if type(max_response_bytes) is not int or max_response_bytes <= 0:
            raise HostBoundaryError("max_response_bytes must be a positive integer")
        self._api_key = api_key.strip()
        self._endpoint = Endpoint.parse(endpoint, allow_insecure_http=allow_insecure_http)
        self._timeout_seconds = float(timeout_seconds)
        self._max_response_bytes = max_response_bytes
        self._manifest = dict(manifest) if manifest is not None else None
        self._allow_insecure_http = allow_insecure_http
        self._user_agent = _header_value(user_agent)
        self._trusted_endpoint_hosts = frozenset(
            str(host).strip().lower() for host in trusted_endpoint_hosts if str(host).strip()
        )
        if not self._trusted_endpoint_hosts:
            raise HostBoundaryError("trusted_endpoint_hosts must contain at least one hostname")

        headers: dict[str, str] = {}
        for raw_name, raw_value in dict(additional_headers or {}).items():
            name = _header_name(raw_name)
            lowered = name.lower()
            if lowered in _PROTECTED_HEADER_NAMES:
                raise HostBoundaryError(f"additional header is host-owned: {name}")
            headers[name] = _header_value(raw_value)
        context_names = _context_header_names(list(headers))
        if context_names:
            raise HostBoundaryError(
                f"additional headers contain context-bearing names: {context_names}"
            )
        self._additional_headers = MappingProxyType(headers)
        self._audits: list[Mapping[str, Any]] = []
        self._lock = threading.Lock()

    @classmethod
    def from_environment(
        cls,
        *,
        api_key_env: str = "OPENAI_API_KEY",
        endpoint: str | None = None,
        endpoint_env: str = "OPENAI_RESPONSES_ENDPOINT",
        **kwargs: Any,
    ) -> "ExactResponsesTransport":
        api_key = os.environ.get(api_key_env, "")
        resolved_endpoint = endpoint or os.environ.get(endpoint_env) or DEFAULT_RESPONSES_ENDPOINT
        return cls(api_key=api_key, endpoint=resolved_endpoint, **kwargs)

    @property
    def endpoint(self) -> Endpoint:
        return self._endpoint

    @property
    def audits(self) -> tuple[Mapping[str, Any], ...]:
        with self._lock:
            return tuple(self._audits)

    @property
    def last_audit(self) -> Mapping[str, Any] | None:
        with self._lock:
            return self._audits[-1] if self._audits else None

    def audit_for_request_sha256(self, digest: str) -> Mapping[str, Any] | None:
        with self._lock:
            for audit in reversed(self._audits):
                if audit.get("request_body_sha256") == digest:
                    return audit
        return None

    def _headers(self, body: bytes) -> dict[str, str]:
        host_value = self._endpoint.host
        if self._endpoint.port is not None:
            default_port = 443 if self._endpoint.scheme == "https" else 80
            if self._endpoint.port != default_port:
                host_value = f"{host_value}:{self._endpoint.port}"
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Accept-Encoding": "identity",
            "Host": host_value,
            "User-Agent": self._user_agent,
            "Content-Length": str(len(body)),
            "Connection": "close",
        }
        headers.update(self._additional_headers)
        return headers

    def _connection(self) -> http.client.HTTPConnection:
        if self._endpoint.scheme == "https":
            context = ssl.create_default_context()
            return http.client.HTTPSConnection(
                self._endpoint.host,
                self._endpoint.port,
                timeout=self._timeout_seconds,
                context=context,
            )
        return http.client.HTTPConnection(
            self._endpoint.host,
            self._endpoint.port,
            timeout=self._timeout_seconds,
        )

    def __call__(self, body: bytes) -> TransportResponse:
        if not isinstance(body, bytes):
            raise HostBoundaryError("transport body must be bytes")
        if not body:
            raise HostBoundaryError("transport body must not be empty")

        body_audit: dict[str, Any] = {}
        if self._manifest is not None:
            body_audit = dict(audit_wire_request_against_manifest(body, self._manifest))

        request_headers = self._headers(body)
        request_header_items = list(request_headers.items())
        request_context_headers = _context_header_names(list(request_headers))
        environment_proxy_names = sorted(
            key for key in PROXY_ENVIRONMENT_KEYS if os.environ.get(key)
        )
        endpoint_trusted = self._endpoint.host in self._trusted_endpoint_hosts
        started = time.perf_counter_ns()
        response_body = b""
        response_status = 0
        response_headers: list[tuple[str, str]] = []
        connection = self._connection()
        try:
            connection.request(
                "POST",
                self._endpoint.target,
                body=body,
                headers=request_headers,
                encode_chunked=False,
            )
            response = connection.getresponse()
            response_status = int(response.status)
            response_headers = [(str(name), str(value)) for name, value in response.getheaders()]
            response_body = response.read(self._max_response_bytes + 1)
            if len(response_body) > self._max_response_bytes:
                raise HostTransportError(
                    f"response body exceeds {self._max_response_bytes} bytes"
                )
        except (OSError, ssl.SSLError, http.client.HTTPException) as exc:
            raise HostTransportError(f"exact HTTP transport failed: {exc}") from exc
        finally:
            connection.close()
        elapsed_ms = (time.perf_counter_ns() - started) / 1_000_000

        response_names = [name.lower() for name, _ in response_headers]
        response_context_headers = _context_header_names(response_names)
        set_cookie_count = sum(name == "set-cookie" for name in response_names)
        response_lookup: dict[str, str] = {}
        for name, value in response_headers:
            response_lookup.setdefault(name.lower(), value)

        manifest_match = bool(body_audit.get("manifest_match")) if self._manifest is not None else None
        bounded_context_eligible = (
            bool(body_audit.get("bounded_context_eligible"))
            if self._manifest is not None
            else None
        )
        request_cookie_present = any(name.lower() == "cookie" for name, _ in request_header_items)
        content_length_matches = request_headers["Content-Length"] == str(len(body))
        transport_context_gate = bool(
            self._manifest is not None
            and manifest_match
            and bounded_context_eligible
            and not request_cookie_present
            and not request_context_headers
            and endpoint_trusted
            and content_length_matches
            and (self._endpoint.scheme == "https" or self._allow_insecure_http)
        )

        audit: dict[str, Any] = {
            "schema_version": 1,
            "request_body_sha256": _sha256_bytes(body),
            "request_body_bytes": len(body),
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
            "request_header_names": sorted(name.lower() for name in request_headers),
            "request_headers_redacted": _redacted_headers(request_header_items),
            "request_headers_sha256": _sha256_bytes(_canonical_json_bytes(_redacted_headers(request_header_items))),
            "authorization_sha256": _sha256_text(request_headers["Authorization"]),
            "manifest_supplied": self._manifest is not None,
            "manifest_match": manifest_match,
            "bounded_context_eligible": bounded_context_eligible,
            "response_status": response_status,
            "response_body_bytes": len(response_body),
            "response_body_sha256": _sha256_bytes(response_body),
            "response_header_names": sorted(response_names),
            "response_headers_redacted": _redacted_headers(response_headers),
            "response_set_cookie_count": set_cookie_count,
            "response_cookie_replayed": False,
            "response_context_header_names": response_context_headers,
            "response_context_header_replayed": False,
            "response_request_id": response_lookup.get("x-request-id"),
            "elapsed_ms": elapsed_ms,
            "transport_context_gate": transport_context_gate,
            "claim_scope": (
                "exact bytes and controlled headers supplied by this direct client transport; "
                "provider-internal context is not established"
            ),
        }
        if body_audit:
            audit["host_body_audit"] = body_audit
        frozen_audit = MappingProxyType(audit)
        with self._lock:
            self._audits.append(frozen_audit)

        return TransportResponse(
            body=response_body,
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
        and audit.get("manifest_match") is True
        and audit.get("bounded_context_eligible") is True
    )


__all__ = [
    "DEFAULT_MAX_RESPONSE_BYTES",
    "DEFAULT_RESPONSES_ENDPOINT",
    "DEFAULT_TRUSTED_ENDPOINT_HOSTS",
    "Endpoint",
    "ExactResponsesTransport",
    "transport_audit_passes",
]

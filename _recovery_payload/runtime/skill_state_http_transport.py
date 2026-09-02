#!/usr/bin/env python3
"""Exact-byte HTTP transport and outbound-context audit for state benchmarks.

The transport deliberately bypasses environment proxies and cookie/session jars.
It sends the supplied JSON bytes unchanged and records the complete request-header
surface under client control. Passing this audit establishes a client-visible
transport boundary only; it cannot establish provider-internal context handling.
"""

from __future__ import annotations

import hashlib
import http.client
import json
import os
import ssl
import time
from dataclasses import asdict, dataclass
from typing import Any, Mapping
from urllib.parse import urlsplit

from runtime.skill_state_host import TransportResponse


CONTEXT_HEADER_TERMS = (
    "cookie",
    "conversation",
    "history",
    "parent-response",
    "previous-response",
    "session",
    "thread",
)
PROXY_ENVIRONMENT_KEYS = (
    "HTTP_PROXY",
    "HTTPS_PROXY",
    "ALL_PROXY",
    "http_proxy",
    "https_proxy",
    "all_proxy",
)


class TransportAuditError(ValueError):
    """Raised when the exact-byte transport contract cannot be established."""


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _header_hash(value: str) -> str:
    return _sha256(value.encode("utf-8"))


def _canonical_header_name(value: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise TransportAuditError("header names must be non-empty strings")
    if any(character in value for character in "\r\n:"):
        raise TransportAuditError(f"invalid header name: {value!r}")
    return "-".join(part.capitalize() for part in value.strip().split("-"))


def _validate_header_value(value: str, name: str) -> str:
    if not isinstance(value, str):
        raise TransportAuditError(f"header {name} must be a string")
    if "\r" in value or "\n" in value:
        raise TransportAuditError(f"header {name} contains a line break")
    return value


def _contextual_headers(headers: Mapping[str, str]) -> tuple[str, ...]:
    return tuple(
        sorted(
            name
            for name in headers
            if any(term in name.lower().replace("_", "-") for term in CONTEXT_HEADER_TERMS)
        )
    )


@dataclass(frozen=True)
class OutboundRequestAudit:
    endpoint: str
    method: str
    tls: bool
    host: str
    path: str
    request_sha256: str
    request_bytes: int
    declared_content_length: int
    body_bytes_sent_unchanged: bool
    request_header_names: tuple[str, ...]
    request_headers_redacted: Mapping[str, str]
    contextual_header_names: tuple[str, ...]
    request_cookie_present: bool
    authorization_present: bool
    proxy_environment_present: bool
    proxy_environment_keys: tuple[str, ...]
    environment_proxy_bypassed: bool
    response_status: int
    response_bytes: int
    response_sha256: str
    response_header_names: tuple[str, ...]
    response_set_cookie_present: bool
    response_request_id: str | None
    elapsed_ms: float
    client_context_audit_pass: bool
    claim_scope: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class ExactByteHTTPTransport:
    """Send exact Responses API bytes without SDK conversation state.

    The caller must retain the audit records beside its benchmark cell. The class
    creates a new connection for each request, does not retain response cookies,
    and never reads proxy variables when opening the socket.
    """

    def __init__(
        self,
        *,
        endpoint: str = "https://api.openai.com/v1/responses",
        api_key: str,
        timeout: float = 180.0,
        user_agent: str = "practical-coding-skill-state-benchmark/1.0",
        extra_headers: Mapping[str, str] | None = None,
        allow_insecure_http: bool = False,
    ) -> None:
        parsed = urlsplit(endpoint)
        if parsed.scheme not in {"https", "http"}:
            raise TransportAuditError("endpoint must use https or http")
        if parsed.scheme != "https" and not allow_insecure_http:
            raise TransportAuditError("non-TLS endpoints require allow_insecure_http=True")
        if not parsed.hostname:
            raise TransportAuditError("endpoint must include a hostname")
        if parsed.username or parsed.password or parsed.fragment:
            raise TransportAuditError("endpoint must not include credentials or a fragment")
        if not isinstance(api_key, str) or not api_key.strip():
            raise TransportAuditError("api_key must be a non-empty string")
        if type(timeout) not in {int, float} or timeout <= 0:
            raise TransportAuditError("timeout must be positive")

        protected = {"authorization", "content-length", "content-type", "host", "cookie"}
        normalized: dict[str, str] = {}
        for raw_name, raw_value in dict(extra_headers or {}).items():
            name = _canonical_header_name(raw_name)
            if name.lower() in protected:
                raise TransportAuditError(f"extra_headers cannot replace {name}")
            if _contextual_headers({name: raw_value}):
                raise TransportAuditError(f"context-bearing extra header is forbidden: {name}")
            normalized[name] = _validate_header_value(raw_value, name)

        self.endpoint = endpoint
        self.api_key = api_key
        self.timeout = float(timeout)
        self.user_agent = _validate_header_value(user_agent, "User-Agent")
        self.extra_headers = normalized
        self.allow_insecure_http = allow_insecure_http
        self.audits: list[dict[str, Any]] = []
        self.responses: list[bytes] = []

    def _connection(self, parsed: Any) -> http.client.HTTPConnection:
        port = parsed.port or (443 if parsed.scheme == "https" else 80)
        if parsed.scheme == "https":
            return http.client.HTTPSConnection(
                parsed.hostname,
                port,
                timeout=self.timeout,
                context=ssl.create_default_context(),
            )
        return http.client.HTTPConnection(parsed.hostname, port, timeout=self.timeout)

    def __call__(self, body: bytes) -> TransportResponse:
        if not isinstance(body, bytes):
            raise TransportAuditError("transport body must be bytes")
        try:
            decoded = json.loads(body)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise TransportAuditError(f"transport body must be UTF-8 JSON: {exc}") from exc
        if not isinstance(decoded, dict):
            raise TransportAuditError("transport JSON body must be an object")

        parsed = urlsplit(self.endpoint)
        path = parsed.path or "/"
        if parsed.query:
            path += "?" + parsed.query
        host = parsed.hostname or ""
        default_port = 443 if parsed.scheme == "https" else 80
        host_header = host if parsed.port in {None, default_port} else f"{host}:{parsed.port}"

        headers: dict[str, str] = {
            "Host": host_header,
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Content-Length": str(len(body)),
            "User-Agent": self.user_agent,
            "Accept": "application/json",
        }
        headers.update(self.extra_headers)
        contextual = _contextual_headers(headers)
        proxy_keys = tuple(sorted(key for key in PROXY_ENVIRONMENT_KEYS if os.environ.get(key)))

        connection = self._connection(parsed)
        started = time.perf_counter_ns()
        try:
            connection.putrequest(
                "POST",
                path,
                skip_host=True,
                skip_accept_encoding=True,
            )
            for name, value in headers.items():
                connection.putheader(name, value)
            connection.endheaders(body)
            response = connection.getresponse()
            response_body = response.read()
            response_headers_list = response.getheaders()
            response_headers = {name.lower(): value for name, value in response_headers_list}
            status = int(response.status)
        except (OSError, http.client.HTTPException) as exc:
            raise TransportAuditError(f"HTTP transport failed: {exc}") from exc
        finally:
            connection.close()
        elapsed_ms = (time.perf_counter_ns() - started) / 1_000_000

        redacted_headers: dict[str, str] = {}
        for name, value in headers.items():
            if name.lower() == "authorization":
                redacted_headers[name] = "sha256:" + _header_hash(value)
            else:
                redacted_headers[name] = value

        request_cookie_present = any(name.lower() == "cookie" for name in headers)
        set_cookie_present = any(name.lower() == "set-cookie" for name, _ in response_headers_list)
        body_unchanged = int(headers["Content-Length"]) == len(body)
        audit_pass = (
            body_unchanged
            and not contextual
            and not request_cookie_present
            and parsed.scheme == "https"
            and bool(headers.get("Authorization"))
        )
        if parsed.scheme == "http" and self.allow_insecure_http:
            audit_pass = body_unchanged and not contextual and not request_cookie_present

        audit = OutboundRequestAudit(
            endpoint=self.endpoint,
            method="POST",
            tls=parsed.scheme == "https",
            host=host_header,
            path=path,
            request_sha256=_sha256(body),
            request_bytes=len(body),
            declared_content_length=int(headers["Content-Length"]),
            body_bytes_sent_unchanged=body_unchanged,
            request_header_names=tuple(sorted(headers)),
            request_headers_redacted=redacted_headers,
            contextual_header_names=contextual,
            request_cookie_present=request_cookie_present,
            authorization_present=True,
            proxy_environment_present=bool(proxy_keys),
            proxy_environment_keys=proxy_keys,
            environment_proxy_bypassed=True,
            response_status=status,
            response_bytes=len(response_body),
            response_sha256=_sha256(response_body),
            response_header_names=tuple(sorted(name for name, _ in response_headers_list)),
            response_set_cookie_present=set_cookie_present,
            response_request_id=response_headers.get("x-request-id"),
            elapsed_ms=elapsed_ms,
            client_context_audit_pass=audit_pass,
            claim_scope=(
                "captured client request body and headers; provider-internal context behavior is not established"
            ),
        ).to_dict()
        self.audits.append(audit)
        self.responses.append(response_body)
        return TransportResponse(
            body=response_body,
            status_code=status,
            headers=response_headers,
        )

    def send_json(self, value: Mapping[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
        body = json.dumps(
            dict(value),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
        response = self(body)
        try:
            decoded = json.loads(response.body)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise TransportAuditError(f"response is not UTF-8 JSON: {exc}") from exc
        if not isinstance(decoded, dict):
            raise TransportAuditError("response JSON must be an object")
        return decoded, dict(self.audits[-1])


def api_key_from_environment(name: str = "OPENAI_API_KEY") -> str:
    value = os.environ.get(name)
    if not value:
        raise TransportAuditError(f"required API key environment variable is missing: {name}")
    return value


def self_test() -> None:
    try:
        ExactByteHTTPTransport(api_key="test", endpoint="http://127.0.0.1/test")
    except TransportAuditError:
        pass
    else:
        raise AssertionError("plain HTTP must be rejected by default")
    try:
        ExactByteHTTPTransport(
            api_key="test",
            extra_headers={"X-Session-Id": "forbidden"},
        )
    except TransportAuditError:
        pass
    else:
        raise AssertionError("context-bearing headers must be rejected")


if __name__ == "__main__":
    self_test()
    print("skill-state HTTP transport: PASS")

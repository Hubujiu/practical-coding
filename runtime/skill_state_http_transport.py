#!/usr/bin/env python3
"""Profiled exact-byte HTTP transport for execution-state model benchmarks.

The stable ``responses-json-v1`` transport remains available and the explicit
``codex-sse-v1`` profile adds a frozen, audited four-field wire transformation
plus finite SSE normalization.  No SDK-managed conversation state is used.
"""

from __future__ import annotations

from runtime._skill_state_http_transport_impl import (
    DEFAULT_MAX_RESPONSE_BYTES,
    DEFAULT_RESPONSES_ENDPOINT,
    DEFAULT_TRUSTED_ENDPOINT_HOSTS,
    Endpoint,
)
from runtime.skill_state_host import HostBoundaryError, HostTransportError, TransportResponse
from runtime._skill_state_profiled_transport import (
    ExactResponsesTransport,
    transport_audit_passes,
)
from runtime._skill_state_sse import normalize_sse_response, parse_sse_events
from runtime._skill_state_wire_profile import (
    CODEX_ACCOUNT_ID_ENV,
    CodexCredentials,
    DEFAULT_CODEX_AUTH_PATH,
    DEFAULT_CODEX_RESPONSES_ENDPOINT,
    DEFAULT_CODEX_TRUSTED_HOSTS,
    PreparedWireRequest,
    WIRE_PROFILE_CODEX_SSE,
    WIRE_PROFILE_RESPONSES_JSON,
    WIRE_PROFILES,
    load_codex_credentials,
    prepare_profiled_request,
    transport_profile_context,
    validate_wire_profile_contract_manifest,
    wire_profile_contract_manifest,
)

__all__ = [
    "CODEX_ACCOUNT_ID_ENV",
    "CodexCredentials",
    "DEFAULT_CODEX_AUTH_PATH",
    "DEFAULT_CODEX_RESPONSES_ENDPOINT",
    "DEFAULT_CODEX_TRUSTED_HOSTS",
    "DEFAULT_MAX_RESPONSE_BYTES",
    "DEFAULT_RESPONSES_ENDPOINT",
    "DEFAULT_TRUSTED_ENDPOINT_HOSTS",
    "Endpoint",
    "ExactResponsesTransport",
    "HostBoundaryError",
    "HostTransportError",
    "PreparedWireRequest",
    "TransportResponse",
    "WIRE_PROFILE_CODEX_SSE",
    "WIRE_PROFILE_RESPONSES_JSON",
    "WIRE_PROFILES",
    "load_codex_credentials",
    "normalize_sse_response",
    "parse_sse_events",
    "prepare_profiled_request",
    "transport_audit_passes",
    "transport_profile_context",
    "validate_wire_profile_contract_manifest",
    "wire_profile_contract_manifest",
]

#!/usr/bin/env python3
"""Audited history-free host boundary for Practical Coding execution state.

The module prepares one OpenAI Responses-compatible JSON request from the
immutable procedure, one validated state snapshot, the latest observation, and
optional bounded validation feedback. It never carries prior response or
conversation identifiers and never executes a proposed action.

A caller that wants an auditable history-free run must send ``PreparedRequest.wire_bytes``
unchanged. SDK-generated or otherwise reconstructed payloads need a fresh
``audit_wire_request`` call at the actual transport boundary.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import os
import sys
import tempfile
import time
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from types import MappingProxyType
from typing import Any, Protocol

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime.skill_state import (  # noqa: E402
    HOST_OWNED_TOP_LEVEL_KEYS,
    MAX_RUNTIME_TEXT_BYTES,
    MAX_STATE_BYTES,
    MODEL_OWNED_TOP_LEVEL_KEYS,
    StateValidationError,
    apply_transition,
    validate_state,
)

HOST_SCHEMA_VERSION = 1
HISTORY_FREE_MODE = "state-history-free"
MAX_MODEL_ID_BYTES = 256
MAX_INSTRUCTIONS_BYTES = 80 * 1024
MAX_VALIDATION_ERROR_BYTES = 2 * 1024
MAX_OPTIONS_BYTES = 16 * 1024
MAX_TOOLS_BYTES = 96 * 1024
MAX_WIRE_REQUEST_BYTES = 320 * 1024
MAX_RESPONSE_BYTES = 4 * 1024 * 1024
MAX_RETRY_ATTEMPTS = 3

INSTRUCTION_INPUT_MARKER = "Host Instruction (JSON):\n"
INSTRUCTION_CONTRACT_MARKER = "\n\nHost Transition Contract:\n"

BASE_REQUEST_KEYS = frozenset(
    {
        "model",
        "instructions",
        "input",
        "store",
        "stream",
        "background",
        "truncation",
        "tools",
    }
)
ALLOWED_RESPONSE_OPTIONS = frozenset(
    {
        "max_output_tokens",
        "max_tool_calls",
        "parallel_tool_calls",
        "reasoning",
        "service_tier",
        "temperature",
        "top_p",
        "text",
        "tool_choice",
        "prompt_cache_key",
        "prompt_cache_options",
        "safety_identifier",
    }
)
RESERVED_RESPONSE_OPTIONS = frozenset(
    {
        "model",
        "input",
        "instructions",
        "previous_response_id",
        "conversation",
        "context_management",
        "prompt",
        "store",
        "stream",
        "background",
        "truncation",
        "tools",
        "metadata",
    }
)
HISTORY_IMPORT_KEYS = frozenset(
    {
        "previous_response_id",
        "conversation",
        "conversation_id",
        "context",
        "context_management",
        "encrypted_content",
        "history",
        "input_items",
        "messages",
        "parent_response_id",
        "response_id",
        "resume_from",
        "session",
        "session_id",
        "thread",
        "thread_id",
    }
)

REQUEST_CONTRACT: Mapping[str, Any] = MappingProxyType(
    {
        "input_items": 1,
        "instructions": "current-frozen",
        "previous_response_id": "absent",
        "conversation": "absent",
        "context_management": "absent",
        "prompt_reference": "absent",
        "store": False,
        "stream": False,
        "background": False,
        "truncation": "disabled",
    }
)
COMPONENT_HARD_LIMITS: Mapping[str, int] = MappingProxyType(
    {
        "model_id_bytes": MAX_MODEL_ID_BYTES,
        "instructions_bytes": MAX_INSTRUCTIONS_BYTES,
        "procedure_bytes": MAX_RUNTIME_TEXT_BYTES,
        "state_bytes": MAX_STATE_BYTES,
        "observation_bytes": MAX_RUNTIME_TEXT_BYTES,
    }
)
MANIFEST_KEYS = frozenset(
    {
        "schema_version",
        "mode",
        "model",
        "procedure_sha256",
        "options_sha256",
        "tools_sha256",
        "limits",
        "component_hard_limits",
        "request_contract",
        "manifest_sha256",
    }
)


class HostBoundaryError(ValueError):
    """Raised when a request or response violates the history-free host contract."""


class HostTransportError(RuntimeError):
    """Raised when the supplied byte transport fails or returns a non-success status."""


class StatePersistenceError(RuntimeError):
    """Raised when a valid successor cannot be persisted before action release."""


class TransitionRetriesExhausted(RuntimeError):
    """Raised after all bounded transition attempts are rejected."""

    def __init__(self, attempts: tuple[Mapping[str, Any], ...]) -> None:
        super().__init__(f"all {len(attempts)} transition attempts were rejected")
        self.attempts = attempts


@dataclass(frozen=True)
class HistoryFreeLimits:
    """Frozen byte and retry limits used by one history-free host session."""

    max_validation_error_bytes: int = MAX_VALIDATION_ERROR_BYTES
    max_options_bytes: int = MAX_OPTIONS_BYTES
    max_tools_bytes: int = MAX_TOOLS_BYTES
    max_wire_request_bytes: int = MAX_WIRE_REQUEST_BYTES
    max_response_bytes: int = MAX_RESPONSE_BYTES
    max_retry_attempts: int = MAX_RETRY_ATTEMPTS

    def __post_init__(self) -> None:
        hard_caps = {
            "max_validation_error_bytes": MAX_VALIDATION_ERROR_BYTES,
            "max_options_bytes": MAX_OPTIONS_BYTES,
            "max_tools_bytes": MAX_TOOLS_BYTES,
            "max_wire_request_bytes": MAX_WIRE_REQUEST_BYTES,
            "max_response_bytes": MAX_RESPONSE_BYTES,
            "max_retry_attempts": MAX_RETRY_ATTEMPTS,
        }
        for name, value in self.to_dict().items():
            if type(value) is not int or value <= 0:
                raise HostBoundaryError(f"{name} must be a positive integer")
            if value > hard_caps[name]:
                raise HostBoundaryError(f"{name} exceeds the runtime hard cap {hard_caps[name]}")

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "HistoryFreeLimits":
        if not isinstance(value, Mapping):
            raise HostBoundaryError("manifest limits must be an object")
        try:
            plain = dict(value)
        except Exception as exc:
            raise HostBoundaryError(f"manifest limits could not be read: {exc}") from exc
        expected = set(cls().to_dict())
        if set(plain) != expected:
            missing = sorted(expected - set(plain))
            extra = sorted(set(plain) - expected)
            raise HostBoundaryError(
                f"manifest limits keys mismatch; missing={missing}, extra={extra}"
            )
        return cls(**plain)

    def to_dict(self) -> dict[str, int]:
        return {
            "max_validation_error_bytes": self.max_validation_error_bytes,
            "max_options_bytes": self.max_options_bytes,
            "max_tools_bytes": self.max_tools_bytes,
            "max_wire_request_bytes": self.max_wire_request_bytes,
            "max_response_bytes": self.max_response_bytes,
            "max_retry_attempts": self.max_retry_attempts,
        }


@dataclass(frozen=True)
class PreparedRequest:
    """One exact request body and the audit derived from those same bytes."""

    wire_bytes: bytes
    audit: Mapping[str, Any]

    def body(self) -> dict[str, Any]:
        from runtime._skill_state_host_codec import _parse_json_bytes

        parsed = _parse_json_bytes(self.wire_bytes, "prepared request", len(self.wire_bytes))
        if not isinstance(parsed, dict):
            raise HostBoundaryError("prepared request must be a JSON object")
        return parsed


@dataclass(frozen=True)
class TransportResponse:
    """Raw response returned by a caller-supplied exact-byte transport."""

    body: bytes
    status_code: int = 200
    headers: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class HistoryFreeStepResult:
    """Isolated validated successor and still-untrusted action proposal."""

    successor_state: dict[str, Any]
    action: str
    attempts: tuple[Mapping[str, Any], ...]


class ByteTransport(Protocol):
    """Transport that sends the provided body unchanged and returns raw JSON bytes."""

    def __call__(self, body: bytes) -> bytes | TransportResponse: ...

__all__ = [name for name in globals() if not name.startswith('__')]

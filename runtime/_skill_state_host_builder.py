from __future__ import annotations

from runtime._skill_state_host_types import *

from runtime._skill_state_host_codec import *
from runtime._skill_state_host_config import *
from runtime._skill_state_host_contract import *
from runtime._skill_state_host_audit import *
from runtime._skill_state_host_response import *

class _HistoryFreeHostBuilder:
    """Frozen request builder and bounded transition loop.

    The class is deliberately transport-agnostic. The supplied transport receives
    canonical bytes; using a higher-level SDK that reconstructs the request voids
    the byte-level audit unless the final HTTP payload is audited again.
    """

    def __init__(
        self,
        *,
        model: str,
        procedure: str,
        options: Mapping[str, Any] | None = None,
        tools: Sequence[Mapping[str, Any]] | None = None,
        limits: HistoryFreeLimits | None = None,
    ) -> None:
        self._limits = limits or HistoryFreeLimits()
        self._model = _validate_model(model)
        self._instructions = _build_instructions(procedure)
        procedure_bytes = _utf8_bytes(procedure, "procedure")
        self._procedure = procedure
        self._options = _validate_options(options, self._limits)
        self._tools = _validate_tools(tools, self._limits)
        self._options_bytes = _canonical_json_bytes(self._options, "frozen options")
        self._tools_bytes = _canonical_json_bytes(self._tools, "frozen tools")
        manifest = {
            "schema_version": HOST_SCHEMA_VERSION,
            "mode": HISTORY_FREE_MODE,
            "model": self._model,
            "procedure_sha256": _sha256(procedure_bytes),
            "options_sha256": _sha256(self._options_bytes),
            "tools_sha256": _sha256(self._tools_bytes),
            "limits": self._limits.to_dict(),
            "component_hard_limits": dict(COMPONENT_HARD_LIMITS),
            "request_contract": dict(REQUEST_CONTRACT),
        }
        manifest_bytes = _canonical_json_bytes(manifest, "host manifest")
        manifest["manifest_sha256"] = _sha256(manifest_bytes)
        self._manifest = MappingProxyType(manifest)

    @property
    def limits(self) -> HistoryFreeLimits:
        return self._limits

    def manifest(self) -> dict[str, Any]:
        return copy.deepcopy(dict(self._manifest))

    def prepare_request(
        self,
        state: Mapping[str, Any],
        latest_observation: str,
        *,
        validation_error: str | None = None,
        step_id: str | int | None = None,
        attempt: int = 1,
    ) -> PreparedRequest:
        if type(attempt) is not int or attempt <= 0 or attempt > self._limits.max_retry_attempts:
            raise HostBoundaryError(
                f"attempt must be between 1 and {self._limits.max_retry_attempts}"
            )
        input_text = _build_step_input(
            state,
            latest_observation,
            validation_error,
            self._limits,
        )
        body: dict[str, Any] = {
            "model": self._model,
            "instructions": self._instructions,
            "input": [
                {
                    "role": "user",
                    "content": [{"type": "input_text", "text": input_text}],
                }
            ],
            "store": False,
            "stream": False,
            "background": False,
            "truncation": "disabled",
        }
        if self._tools:
            body["tools"] = copy.deepcopy(self._tools)
        body.update(copy.deepcopy(self._options))
        wire = _canonical_json_bytes(body, "wire request")
        audit = dict(audit_wire_request_against_manifest(wire, self._manifest))
        audit.update(
            {
                "step_id": None if step_id is None else str(step_id),
                "attempt": attempt,
                "manifest_sha256": self._manifest["manifest_sha256"],
            }
        )
        return PreparedRequest(wire_bytes=wire, audit=MappingProxyType(audit))


__all__ = [name for name in globals() if not name.startswith('__')]

from __future__ import annotations

from runtime._skill_state_host_types import *

from runtime._skill_state_host_codec import *
from runtime._skill_state_host_contract import *

def audit_wire_request(
    wire_bytes: bytes,
    *,
    limits: HistoryFreeLimits | None = None,
    expected_model: str | None = None,
    expected_procedure_sha256: str | None = None,
    expected_tools_sha256: str | None = None,
    expected_options_sha256: str | None = None,
) -> Mapping[str, Any]:
    """Audit the exact serialized request intended for the HTTP transport.

    Passing this audit supports only a client-visible request-bound claim. The
    caller must still ensure that its transport sends these exact bytes and does
    not attach SDK-managed conversation state out of band.
    """

    active_limits = limits or HistoryFreeLimits()
    request = _parse_json_bytes(wire_bytes, "wire request", active_limits.max_wire_request_bytes)
    if not isinstance(request, dict):
        raise HostBoundaryError("wire request must be a JSON object")

    allowed = BASE_REQUEST_KEYS | ALLOWED_RESPONSE_OPTIONS
    unknown = sorted(set(request) - allowed)
    if unknown:
        raise HostBoundaryError(f"wire request contains unsupported fields: {unknown}")
    required = {"model", "instructions", "input", "store", "stream", "background", "truncation"}
    missing = sorted(required - set(request))
    if missing:
        raise HostBoundaryError(f"wire request is missing fields: {missing}")

    model = _validate_model(request["model"])
    if expected_model is not None and model != expected_model:
        raise HostBoundaryError(f"wire model {model!r} does not match frozen model {expected_model!r}")
    if request["store"] is not False:
        raise HostBoundaryError("history-free request must set store=false")
    if request["stream"] is not False:
        raise HostBoundaryError("this audited host requires stream=false")
    if request["background"] is not False:
        raise HostBoundaryError("history-free request must set background=false")
    if request["truncation"] != "disabled":
        raise HostBoundaryError("history-free request must set truncation=disabled")

    procedure = _parse_instructions(request["instructions"])
    input_text = _extract_input_text(request)
    runtime_input, validation_error = _parse_step_input(input_text, active_limits)
    procedure_bytes = _utf8_bytes(procedure, "procedure")
    procedure_sha256 = _sha256(procedure_bytes)
    if (
        expected_procedure_sha256 is not None
        and procedure_sha256 != expected_procedure_sha256
    ):
        raise HostBoundaryError("wire procedure does not match the frozen procedure")

    tools = request.get("tools", [])
    if not isinstance(tools, list):
        raise HostBoundaryError("tools must be an array")
    tools_bytes = _canonical_json_bytes(tools, "wire tools")
    if len(tools_bytes) > active_limits.max_tools_bytes:
        raise HostBoundaryError(f"wire tools exceed {active_limits.max_tools_bytes} bytes")
    tools_sha256 = _sha256(tools_bytes)
    if expected_tools_sha256 is not None and tools_sha256 != expected_tools_sha256:
        raise HostBoundaryError("wire tools do not match the frozen tool set")

    options = {key: request[key] for key in request if key in ALLOWED_RESPONSE_OPTIONS}
    for context_option in ("reasoning", "prompt_cache_options"):
        if context_option in options:
            _reject_history_import_keys(
                options[context_option], f"wire options.{context_option}"
            )
    options_bytes = _canonical_json_bytes(options, "wire options")
    if len(options_bytes) > active_limits.max_options_bytes:
        raise HostBoundaryError(f"wire options exceed {active_limits.max_options_bytes} bytes")
    options_sha256 = _sha256(options_bytes)
    if expected_options_sha256 is not None and options_sha256 != expected_options_sha256:
        raise HostBoundaryError("wire options do not match the frozen option set")

    state_bytes = _canonical_json_bytes(runtime_input["state"], "runtime state")
    observation_bytes = _utf8_bytes(
        runtime_input["latest_observation"], "latest_observation"
    )
    audit = {
        "schema_version": HOST_SCHEMA_VERSION,
        "mode": HISTORY_FREE_MODE,
        "request_shape_valid": True,
        "history_channels_absent": True,
        "component_bounds_valid": True,
        "manifest_match": False,
        "bounded_context_eligible": False,
        "claim_scope": "one client-visible serialized request body; trajectory claim requires a frozen manifest",
        "transport_context_attestation_required": True,
        "provider_internal_context_claim": "not-established",
        "request_sha256": _sha256(wire_bytes),
        "wire_request_bytes": len(wire_bytes),
        "wire_request_limit_bytes": active_limits.max_wire_request_bytes,
        "instructions_limit_bytes": MAX_INSTRUCTIONS_BYTES,
        "procedure_limit_bytes": MAX_RUNTIME_TEXT_BYTES,
        "state_limit_bytes": MAX_STATE_BYTES,
        "observation_limit_bytes": MAX_RUNTIME_TEXT_BYTES,
        "validation_error_limit_bytes": active_limits.max_validation_error_bytes,
        "tools_limit_bytes": active_limits.max_tools_bytes,
        "options_limit_bytes": active_limits.max_options_bytes,
        "model": model,
        "input_item_count": 1,
        "historical_input_item_count": 0,
        "previous_response_id_present": False,
        "conversation_present": False,
        "prompt_reference_present": False,
        "context_management_present": False,
        "store": False,
        "stream": False,
        "background": False,
        "truncation": "disabled",
        "instructions_bytes": len(_utf8_bytes(request["instructions"], "instructions")),
        "instructions_sha256": _sha256(_utf8_bytes(request["instructions"], "instructions")),
        "input_text_bytes": len(_utf8_bytes(input_text, "history-free input")),
        "procedure_bytes": len(procedure_bytes),
        "procedure_sha256": procedure_sha256,
        "state_bytes": len(state_bytes),
        "state_sha256": _sha256(state_bytes),
        "observation_bytes": len(observation_bytes),
        "observation_sha256": _sha256(observation_bytes),
        "validation_error_bytes": 0
        if validation_error is None
        else len(_utf8_bytes(validation_error, "validation_error")),
        "tools_bytes": len(tools_bytes),
        "tools_sha256": tools_sha256,
        "options_bytes": len(options_bytes),
        "options_sha256": options_sha256,
    }
    return MappingProxyType(audit)


def audit_wire_request_against_manifest(
    wire_bytes: bytes,
    manifest: Mapping[str, Any],
) -> Mapping[str, Any]:
    """Audit exact request bytes against one validated frozen manifest."""

    frozen = validate_manifest(manifest)
    limits = HistoryFreeLimits.from_mapping(frozen["limits"])
    audit = dict(
        audit_wire_request(
            wire_bytes,
            limits=limits,
            expected_model=frozen["model"],
            expected_procedure_sha256=frozen["procedure_sha256"],
            expected_tools_sha256=frozen["tools_sha256"],
            expected_options_sha256=frozen["options_sha256"],
        )
    )
    audit["manifest_sha256"] = frozen["manifest_sha256"]
    audit["manifest_match"] = True
    audit["bounded_context_eligible"] = True
    audit["claim_scope"] = (
        "client-visible serialized request body under one frozen host manifest"
    )
    return MappingProxyType(audit)

__all__ = [name for name in globals() if not name.startswith('__')]

from __future__ import annotations

from runtime._skill_state_host_types import *
from runtime._skill_state_host_codec import *
from runtime._skill_state_host_config import *

def _parse_instructions(instructions: Any) -> str:
    if not isinstance(instructions, str):
        raise HostBoundaryError("wire instructions must be a string")
    if len(_utf8_bytes(instructions, "wire instructions")) > MAX_INSTRUCTIONS_BYTES:
        raise HostBoundaryError(f"wire instructions exceed {MAX_INSTRUCTIONS_BYTES} UTF-8 bytes")
    if (
        instructions.count(INSTRUCTION_INPUT_MARKER) != 1
        or instructions.count(INSTRUCTION_CONTRACT_MARKER) != 1
    ):
        raise HostBoundaryError("wire instructions must contain one host payload and one contract marker")
    payload_text = instructions.split(INSTRUCTION_INPUT_MARKER, 1)[1].split(
        INSTRUCTION_CONTRACT_MARKER, 1
    )[0]
    payload = _parse_json_bytes(
        _utf8_bytes(payload_text, "host instruction payload"),
        "host instruction payload",
        MAX_INSTRUCTIONS_BYTES,
    )
    if not isinstance(payload, dict) or set(payload) != {"host_schema_version", "procedure"}:
        raise HostBoundaryError(
            "host instruction payload must contain exactly host_schema_version and procedure"
        )
    if type(payload["host_schema_version"]) is not int or payload["host_schema_version"] != HOST_SCHEMA_VERSION:
        raise HostBoundaryError(
            f"host instruction payload version must equal {HOST_SCHEMA_VERSION}"
        )
    procedure = payload["procedure"]
    if not isinstance(procedure, str):
        raise HostBoundaryError("host instruction procedure must be a string")
    expected = _build_instructions(procedure)
    if instructions != expected:
        raise HostBoundaryError("wire instructions do not match the canonical host contract")
    return procedure


def _build_step_input(
    state: Mapping[str, Any],
    latest_observation: str,
    validation_error: str | None,
    limits: HistoryFreeLimits,
) -> str:
    try:
        state_snapshot = copy.deepcopy(state)
    except Exception as exc:
        raise HostBoundaryError(f"state could not be snapshotted: {exc}") from exc
    validate_state(state_snapshot)
    observation_bytes = _utf8_bytes(latest_observation, "latest_observation")
    if len(observation_bytes) > MAX_RUNTIME_TEXT_BYTES:
        raise HostBoundaryError(
            f"latest_observation exceeds {MAX_RUNTIME_TEXT_BYTES} UTF-8 bytes"
        )
    payload: dict[str, Any] = {
        "latest_observation": latest_observation,
        "state": state_snapshot,
    }
    if validation_error is not None:
        feedback_bytes = _utf8_bytes(validation_error, "validation_error")
        if not validation_error.strip():
            raise HostBoundaryError("validation_error must not be empty")
        if len(feedback_bytes) > limits.max_validation_error_bytes:
            raise HostBoundaryError(
                f"validation_error exceeds {limits.max_validation_error_bytes} UTF-8 bytes"
            )
        payload["validation_error"] = validation_error
    return _canonical_json_bytes(payload, "history-free input").decode("utf-8")


def _extract_input_text(request: Mapping[str, Any]) -> str:
    input_items = request.get("input")
    if not isinstance(input_items, list) or len(input_items) != 1:
        raise HostBoundaryError("history-free input must contain exactly one current user item")
    item = input_items[0]
    if not isinstance(item, dict) or set(item) != {"role", "content"} or item.get("role") != "user":
        raise HostBoundaryError("history-free input item must be one canonical user message")
    content = item.get("content")
    if not isinstance(content, list) or len(content) != 1:
        raise HostBoundaryError("history-free user message must contain one input_text block")
    block = content[0]
    if not isinstance(block, dict) or set(block) != {"type", "text"} or block.get("type") != "input_text":
        raise HostBoundaryError("history-free content must be one canonical input_text block")
    text = block.get("text")
    if not isinstance(text, str):
        raise HostBoundaryError("history-free input_text.text must be a string")
    return text


def _parse_step_input(input_text: str, limits: HistoryFreeLimits) -> tuple[dict[str, Any], str | None]:
    payload = _parse_json_bytes(
        _utf8_bytes(input_text, "history-free input"),
        "history-free input",
        limits.max_wire_request_bytes,
    )
    if not isinstance(payload, dict):
        raise HostBoundaryError("history-free input must be a JSON object")
    allowed = {"state", "latest_observation", "validation_error"}
    required = {"state", "latest_observation"}
    if not required.issubset(payload) or not set(payload).issubset(allowed):
        missing = sorted(required - set(payload))
        extra = sorted(set(payload) - allowed)
        raise HostBoundaryError(
            f"history-free input keys mismatch; missing={missing}, extra={extra}"
        )
    if not isinstance(payload["state"], dict):
        raise HostBoundaryError("history-free state must be an object")
    validate_state(payload["state"])
    observation = payload["latest_observation"]
    if not isinstance(observation, str):
        raise HostBoundaryError("latest_observation must be a string")
    if len(_utf8_bytes(observation, "latest_observation")) > MAX_RUNTIME_TEXT_BYTES:
        raise HostBoundaryError("latest_observation exceeds its frozen byte budget")
    validation_error = payload.get("validation_error")
    if validation_error is not None:
        if not isinstance(validation_error, str) or not validation_error.strip():
            raise HostBoundaryError("validation_error must be a non-empty string")
        if len(_utf8_bytes(validation_error, "validation_error")) > limits.max_validation_error_bytes:
            raise HostBoundaryError("validation_error exceeds its frozen byte budget")
    return payload, validation_error


def _require_sha256(value: Any, path: str) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise HostBoundaryError(f"{path} must be a 64-character SHA-256 hex digest")
    if any(character not in "0123456789abcdef" for character in value):
        raise HostBoundaryError(f"{path} must use lowercase hexadecimal")
    return value


def validate_manifest(value: Mapping[str, Any]) -> Mapping[str, Any]:
    """Validate one frozen host manifest and its self-digest."""

    if not isinstance(value, Mapping):
        raise HostBoundaryError("host manifest must be an object")
    try:
        manifest = copy.deepcopy(dict(value))
    except Exception as exc:
        raise HostBoundaryError(f"host manifest could not be snapshotted: {exc}") from exc
    _validate_json_tree(manifest, "host manifest")
    if set(manifest) != set(MANIFEST_KEYS):
        missing = sorted(set(MANIFEST_KEYS) - set(manifest))
        extra = sorted(set(manifest) - set(MANIFEST_KEYS))
        raise HostBoundaryError(
            f"host manifest keys mismatch; missing={missing}, extra={extra}"
        )
    if type(manifest["schema_version"]) is not int or manifest["schema_version"] != HOST_SCHEMA_VERSION:
        raise HostBoundaryError(
            f"host manifest schema_version must equal {HOST_SCHEMA_VERSION}"
        )
    if manifest["mode"] != HISTORY_FREE_MODE:
        raise HostBoundaryError(f"host manifest mode must equal {HISTORY_FREE_MODE!r}")
    _validate_model(manifest["model"])
    for key in ("procedure_sha256", "options_sha256", "tools_sha256", "manifest_sha256"):
        _require_sha256(manifest[key], f"host manifest.{key}")
    limits = HistoryFreeLimits.from_mapping(manifest["limits"])
    if manifest["component_hard_limits"] != dict(COMPONENT_HARD_LIMITS):
        raise HostBoundaryError("host manifest component_hard_limits do not match this runtime")
    if manifest["request_contract"] != dict(REQUEST_CONTRACT):
        raise HostBoundaryError("host manifest request_contract does not match this runtime")
    unsigned = dict(manifest)
    claimed = unsigned.pop("manifest_sha256")
    actual = _sha256(_canonical_json_bytes(unsigned, "unsigned host manifest"))
    if claimed != actual:
        raise HostBoundaryError("host manifest SHA-256 does not match its content")
    manifest["limits"] = limits.to_dict()
    return MappingProxyType(manifest)

__all__ = [name for name in globals() if not name.startswith('__')]

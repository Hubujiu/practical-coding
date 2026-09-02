#!/usr/bin/env python3
"""Validated execution-state projection for long-running Practical Coding tasks.

This module implements the deterministic half of a SKILL.state-style runtime:
current state is validated, model-proposed JSON merge patches are applied on a
copy, and the next prompt can be built from only procedure + state + latest
observation. It deliberately does not run an LLM or persist state by default.
"""

from __future__ import annotations

import argparse
import copy
import json
import math
import os
import sys
import tempfile
from pathlib import Path
from typing import Any, Mapping, Sequence

SCHEMA_VERSION = 1
MAX_STATE_BYTES = 16 * 1024
MAX_TEXT_BYTES = 2 * 1024
MAX_LIST_ITEMS = 32
MAX_MAP_ITEMS = 64
MAX_NESTING_DEPTH = 6

RETRIEVAL_MODES = frozenset({"NONE", "TARGETED", "BOUNDED", "STRUCTURAL"})
MANUAL_MODES = frozenset({"none", "decision", "clarification"})
AUTOMATIC_CHILDREN: dict[str, frozenset[str]] = {
    "core": frozenset({"debugging", "implementation"}),
    "debugging": frozenset(),
    "implementation": frozenset(),
}
TOP_LEVEL_KEYS = frozenset(
    {
        "schema_version",
        "objective",
        "success",
        "route",
        "working_set",
        "facts",
        "hypotheses",
        "change",
        "verification",
        "next_action",
        "history",
    }
)
HOST_OWNED_TOP_LEVEL_KEYS = frozenset({"schema_version", "objective", "success", "route"})
FORBIDDEN_STATE_KEYS = frozenset(
    {
        "reasoning",
        "chain_of_thought",
        "chain-of-thought",
        "conversation_history",
        "transcript",
        "tool_output",
        "tool_outputs",
        "action_log",
    }
)


class StateValidationError(ValueError):
    """Raised when canonical execution state or a proposed patch is invalid."""


def initial_state(objective: str, success: Sequence[str]) -> dict[str, Any]:
    """Create and validate a new compact coding-domain execution state."""

    if isinstance(success, (str, bytes)):
        raise StateValidationError("success must be a sequence of conditions, not one string")
    state: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "objective": objective,
        "success": list(success),
        "route": {
            "automatic_path": ["core"],
            "retrieval": "NONE",
            "manual": "none",
        },
        "working_set": {"paths": [], "symbols": []},
        "facts": {},
        "hypotheses": {"active": {}, "rejected": {}},
        "change": {"planned": [], "applied": []},
        "verification": {"pending": [], "results": {}},
        "next_action": "",
        "history": {"required": False, "artifacts": []},
    }
    validate_state(state)
    return state


def _encoded_size(value: Any) -> int:
    try:
        payload = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    except (TypeError, ValueError) as exc:
        raise StateValidationError(f"state must contain only JSON values: {exc}") from exc
    return len(payload.encode("utf-8"))


def _require_mapping(value: Any, path: str, keys: set[str] | frozenset[str] | None = None) -> Mapping[str, Any]:
    if not isinstance(value, dict):
        raise StateValidationError(f"{path} must be an object")
    if len(value) > MAX_MAP_ITEMS:
        raise StateValidationError(f"{path} exceeds {MAX_MAP_ITEMS} entries")
    if keys is not None and set(value) != set(keys):
        missing = sorted(set(keys) - set(value))
        extra = sorted(set(value) - set(keys))
        raise StateValidationError(f"{path} keys mismatch; missing={missing}, extra={extra}")
    return value


def _require_text(value: Any, path: str, *, allow_empty: bool = True, max_bytes: int = MAX_TEXT_BYTES) -> str:
    if not isinstance(value, str):
        raise StateValidationError(f"{path} must be a string")
    if not allow_empty and not value.strip():
        raise StateValidationError(f"{path} must not be empty")
    if len(value.encode("utf-8")) > max_bytes:
        raise StateValidationError(f"{path} exceeds {max_bytes} UTF-8 bytes")
    return value


def _require_string_list(
    value: Any,
    path: str,
    *,
    allow_empty: bool = True,
    max_items: int = MAX_LIST_ITEMS,
    item_bytes: int = 512,
) -> list[str]:
    if not isinstance(value, list):
        raise StateValidationError(f"{path} must be an array")
    if not allow_empty and not value:
        raise StateValidationError(f"{path} must not be empty")
    if len(value) > max_items:
        raise StateValidationError(f"{path} exceeds {max_items} items")
    for index, item in enumerate(value):
        _require_text(item, f"{path}[{index}]", allow_empty=False, max_bytes=item_bytes)
    return value


def _require_string_map(value: Any, path: str, *, max_items: int = MAX_MAP_ITEMS) -> Mapping[str, str]:
    mapping = _require_mapping(value, path)
    if len(mapping) > max_items:
        raise StateValidationError(f"{path} exceeds {max_items} entries")
    for key, item in mapping.items():
        _require_text(key, f"{path}.<key>", allow_empty=False, max_bytes=256)
        _require_text(item, f"{path}.{key}", max_bytes=MAX_TEXT_BYTES)
    return mapping  # type: ignore[return-value]


def _validate_json_tree(value: Any, path: str, depth: int = 0) -> None:
    if depth > MAX_NESTING_DEPTH:
        raise StateValidationError(f"{path} exceeds nesting depth {MAX_NESTING_DEPTH}")
    if value is None or isinstance(value, (str, int, float, bool)):
        if isinstance(value, str):
            _require_text(value, path)
        if isinstance(value, float) and not math.isfinite(value):
            raise StateValidationError(f"{path} must not contain NaN or infinity")
        return
    if isinstance(value, list):
        if len(value) > MAX_LIST_ITEMS:
            raise StateValidationError(f"{path} exceeds {MAX_LIST_ITEMS} items")
        for index, item in enumerate(value):
            _validate_json_tree(item, f"{path}[{index}]", depth + 1)
        return
    if isinstance(value, dict):
        if len(value) > MAX_MAP_ITEMS:
            raise StateValidationError(f"{path} exceeds {MAX_MAP_ITEMS} entries")
        for key, item in value.items():
            _require_text(key, f"{path}.<key>", allow_empty=False, max_bytes=256)
            if key.lower() in FORBIDDEN_STATE_KEYS:
                raise StateValidationError(f"{path}.{key} is forbidden in persistent execution state")
            _validate_json_tree(item, f"{path}.{key}", depth + 1)
        return
    raise StateValidationError(f"{path} contains a non-JSON value: {type(value).__name__}")


def _reject_forbidden_patch_keys(value: Any, path: str = "patch") -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise StateValidationError(f"{path} keys must be strings")
            if key.lower() in FORBIDDEN_STATE_KEYS:
                raise StateValidationError(f"{path}.{key} is forbidden even when deletion is requested")
            _reject_forbidden_patch_keys(item, f"{path}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _reject_forbidden_patch_keys(item, f"{path}[{index}]")


def validate_state(state: Mapping[str, Any]) -> None:
    """Validate one canonical execution-state snapshot.

    Validation is strict at structural boundaries so malformed model output cannot
    silently replace a required container or leak unbounded transcript material.
    """

    root = _require_mapping(state, "state", TOP_LEVEL_KEYS)
    if type(root["schema_version"]) is not int or root["schema_version"] != SCHEMA_VERSION:
        raise StateValidationError(f"state.schema_version must equal {SCHEMA_VERSION}")
    _require_text(root["objective"], "state.objective", allow_empty=False)
    _require_string_list(root["success"], "state.success", allow_empty=False, max_items=16)

    route = _require_mapping(root["route"], "state.route", {"automatic_path", "retrieval", "manual"})
    path = _require_string_list(route["automatic_path"], "state.route.automatic_path", allow_empty=False, max_items=16)
    normalized_path = [node.lower() for node in path]
    if path != normalized_path:
        raise StateValidationError("state.route.automatic_path must use canonical lowercase node names")
    if normalized_path[0] != "core":
        raise StateValidationError("state.route.automatic_path must start at core")
    illegal_path_nodes = set(normalized_path[1:]) & (set(MANUAL_MODES) | {"execution_state"})
    if illegal_path_nodes:
        raise StateValidationError(
            f"state.route.automatic_path contains non-automatic nodes: {sorted(illegal_path_nodes)}"
        )
    unknown_path_nodes = [node for node in normalized_path if node not in AUTOMATIC_CHILDREN]
    if unknown_path_nodes:
        raise StateValidationError(
            f"state.route.automatic_path contains unknown nodes: {sorted(set(unknown_path_nodes))}"
        )
    for parent, child in zip(normalized_path, normalized_path[1:]):
        if child not in AUTOMATIC_CHILDREN[parent]:
            raise StateValidationError(
                f"state.route.automatic_path contains invalid edge: {parent} -> {child}"
            )
    if route["retrieval"] not in RETRIEVAL_MODES:
        raise StateValidationError(f"state.route.retrieval must be one of {sorted(RETRIEVAL_MODES)}")
    if route["manual"] not in MANUAL_MODES:
        raise StateValidationError(f"state.route.manual must be one of {sorted(MANUAL_MODES)}")
    if route["manual"] != "none" and normalized_path != ["core"]:
        raise StateValidationError("manual modes are outside the automatic path; reset the path to core")

    working = _require_mapping(root["working_set"], "state.working_set", {"paths", "symbols"})
    _require_string_list(working["paths"], "state.working_set.paths")
    _require_string_list(working["symbols"], "state.working_set.symbols")

    facts = _require_mapping(root["facts"], "state.facts")
    _validate_json_tree(facts, "state.facts")

    hypotheses = _require_mapping(root["hypotheses"], "state.hypotheses", {"active", "rejected"})
    _require_string_map(hypotheses["active"], "state.hypotheses.active", max_items=16)
    _require_string_map(hypotheses["rejected"], "state.hypotheses.rejected", max_items=16)

    change = _require_mapping(root["change"], "state.change", {"planned", "applied"})
    _require_string_list(change["planned"], "state.change.planned", max_items=16)
    _require_string_list(change["applied"], "state.change.applied", max_items=16)

    verification = _require_mapping(root["verification"], "state.verification", {"pending", "results"})
    _require_string_list(verification["pending"], "state.verification.pending", max_items=32)
    _require_string_map(verification["results"], "state.verification.results", max_items=32)

    _require_text(root["next_action"], "state.next_action")

    history = _require_mapping(root["history"], "state.history", {"required", "artifacts"})
    if type(history["required"]) is not bool:
        raise StateValidationError("state.history.required must be a boolean")
    _require_string_list(history["artifacts"], "state.history.artifacts", max_items=32)

    _validate_json_tree(root, "state")
    size = _encoded_size(root)
    if size > MAX_STATE_BYTES:
        raise StateValidationError(f"state exceeds {MAX_STATE_BYTES} UTF-8 bytes: {size}")


def _merge_patch(target: Any, patch: Any) -> Any:
    """Apply JSON Merge Patch semantics on copies, including null deletion."""

    if not isinstance(patch, dict):
        return copy.deepcopy(patch)
    result = copy.deepcopy(target) if isinstance(target, dict) else {}
    for key, value in patch.items():
        if value is None:
            result.pop(key, None)
        else:
            result[key] = _merge_patch(result.get(key), value)
    return result


def _apply_validated_patch(state: Mapping[str, Any], patch: Mapping[str, Any]) -> dict[str, Any]:
    validate_state(state)
    if not isinstance(patch, dict):
        raise StateValidationError("state patch must be an object")
    _reject_forbidden_patch_keys(patch)
    candidate = _merge_patch(state, patch)
    if not isinstance(candidate, dict):
        raise StateValidationError("state patch replaced the canonical state with a non-object")
    validate_state(candidate)
    return candidate


def apply_state_patch(state: Mapping[str, Any], patch: Mapping[str, Any]) -> dict[str, Any]:
    """Apply a model-owned patch without allowing task or routing control drift."""

    if not isinstance(patch, dict):
        raise StateValidationError("state patch must be an object")
    controlled = sorted(set(patch) & HOST_OWNED_TOP_LEVEL_KEYS)
    if controlled:
        raise StateValidationError(
            f"model state patch cannot change host-owned fields: {controlled}"
        )
    return _apply_validated_patch(state, patch)


def apply_host_patch(state: Mapping[str, Any], patch: Mapping[str, Any]) -> dict[str, Any]:
    """Apply an explicit host/user control update to objective, success, or route."""

    if not isinstance(patch, dict):
        raise StateValidationError("host patch must be an object")
    extra = sorted(set(patch) - HOST_OWNED_TOP_LEVEL_KEYS)
    if extra:
        raise StateValidationError(f"host patch contains model-owned fields: {extra}")
    return _apply_validated_patch(state, patch)


def parse_transition(value: str | Mapping[str, Any]) -> tuple[dict[str, Any], str]:
    """Parse the runtime-facing model payload with exactly state_patch and action."""

    if isinstance(value, str):
        try:
            decoded = json.loads(value)
        except json.JSONDecodeError as exc:
            raise StateValidationError(f"transition is not valid JSON: {exc}") from exc
    else:
        decoded = dict(value)
    payload = _require_mapping(decoded, "transition", {"state_patch", "action"})
    patch = payload["state_patch"]
    if not isinstance(patch, dict):
        raise StateValidationError("transition.state_patch must be an object")
    action = _require_text(payload["action"], "transition.action", allow_empty=False)
    return copy.deepcopy(patch), action


def apply_transition(state: Mapping[str, Any], value: str | Mapping[str, Any]) -> tuple[dict[str, Any], str]:
    """Validate a model transition and return ``(successor_state, action)``."""

    patch, action = parse_transition(value)
    return apply_state_patch(state, patch), action


def build_prompt(procedure: str, state: Mapping[str, Any], latest_observation: str) -> str:
    """Build the bounded runtime prompt: procedure + state + latest observation.

    This function intentionally has no history parameter. A host must also omit
    prior messages at the API/runtime layer before claiming horizon-independent
    prompt growth.
    """

    _require_text(procedure, "procedure", allow_empty=False, max_bytes=64 * 1024)
    _require_text(latest_observation, "latest_observation", max_bytes=64 * 1024)
    validate_state(state)
    compact_state = json.dumps(state, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return (
        "Procedure (immutable):\n"
        f"{procedure}\n\n"
        "Skill Execution State (canonical current snapshot):\n"
        f"```json\n{compact_state}\n```\n\n"
        "Latest Observation:\n"
        f"{latest_observation}\n\n"
        "Reason internally, but do not persist or echo a reasoning trace. Return exactly one JSON object "
        'with keys {"state_patch":{...},"action":"..."}. Omitted patch keys survive; null deletes an obsolete key.'
    )


def _read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise StateValidationError(f"cannot read {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise StateValidationError(f"invalid JSON in {path}: {exc}") from exc


def _atomic_write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(value, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
    except Exception:
        try:
            os.unlink(temp_name)
        except OSError:
            pass
        raise


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    init = subparsers.add_parser("init", help="create a validated initial state")
    init.add_argument("--objective", required=True)
    init.add_argument("--success", action="append", required=True)
    init.add_argument("--output", type=Path, required=True)

    validate = subparsers.add_parser("validate", help="validate a state file")
    validate.add_argument("state", type=Path)

    apply = subparsers.add_parser("apply", help="apply a model-owned JSON merge patch atomically")
    apply.add_argument("state", type=Path)
    apply.add_argument("patch", type=Path)
    apply.add_argument("--output", type=Path, required=True)

    host_apply = subparsers.add_parser(
        "host-apply", help="explicitly update host-owned objective, success, or route fields"
    )
    host_apply.add_argument("state", type=Path)
    host_apply.add_argument("patch", type=Path)
    host_apply.add_argument("--output", type=Path, required=True)

    transition = subparsers.add_parser("transition", help="validate state_patch + action and write successor state")
    transition.add_argument("state", type=Path)
    transition.add_argument("response", type=Path)
    transition.add_argument("--output", type=Path, required=True)

    render = subparsers.add_parser("render", help="render procedure + state + latest observation")
    render.add_argument("--procedure", type=Path, required=True)
    render.add_argument("--state", type=Path, required=True)
    render.add_argument("--observation", type=Path, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "init":
            _atomic_write_json(args.output, initial_state(args.objective, args.success))
            return 0
        if args.command == "validate":
            validate_state(_read_json(args.state))
            print("execution state: VALID")
            return 0
        if args.command == "apply":
            state = _read_json(args.state)
            patch = _read_json(args.patch)
            _atomic_write_json(args.output, apply_state_patch(state, patch))
            return 0
        if args.command == "host-apply":
            state = _read_json(args.state)
            patch = _read_json(args.patch)
            _atomic_write_json(args.output, apply_host_patch(state, patch))
            return 0
        if args.command == "transition":
            state = _read_json(args.state)
            response = args.response.read_text(encoding="utf-8")
            successor, action = apply_transition(state, response)
            _atomic_write_json(args.output, successor)
            print(action)
            return 0
        if args.command == "render":
            state = _read_json(args.state)
            procedure = args.procedure.read_text(encoding="utf-8")
            observation = args.observation.read_text(encoding="utf-8")
            print(build_prompt(procedure, state, observation))
            return 0
    except (OSError, StateValidationError) as exc:
        print(f"skill-state error: {exc}", file=sys.stderr)
        return 2
    raise AssertionError(f"unhandled command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())

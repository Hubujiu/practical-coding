from __future__ import annotations

from runtime._skill_state_host_types import *

def _utf8_bytes(value: str, label: str) -> bytes:
    if not isinstance(value, str):
        raise HostBoundaryError(f"{label} must be a string")
    try:
        return value.encode("utf-8")
    except UnicodeEncodeError as exc:
        raise HostBoundaryError(f"{label} is not valid UTF-8 text: {exc}") from exc


def _reject_nonfinite(value: str) -> Any:
    raise HostBoundaryError(f"non-finite JSON number is not allowed: {value}")


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise HostBoundaryError(f"duplicate JSON object key is not allowed: {key!r}")
        result[key] = value
    return result


def _parse_json_bytes(payload: bytes, label: str, max_bytes: int) -> Any:
    if not isinstance(payload, bytes):
        raise HostBoundaryError(f"{label} must be bytes")
    if len(payload) > max_bytes:
        raise HostBoundaryError(f"{label} exceeds {max_bytes} bytes")
    try:
        text = payload.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise HostBoundaryError(f"{label} is not valid UTF-8: {exc}") from exc
    try:
        return json.loads(
            text,
            object_pairs_hook=_unique_object,
            parse_constant=_reject_nonfinite,
        )
    except HostBoundaryError:
        raise
    except (json.JSONDecodeError, RecursionError, ValueError) as exc:
        raise HostBoundaryError(f"invalid JSON in {label}: {exc}") from exc


def _canonical_json_bytes(value: Any, label: str) -> bytes:
    _validate_json_tree(value, label)
    try:
        return json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError, UnicodeEncodeError, RecursionError) as exc:
        raise HostBoundaryError(f"{label} is not canonical UTF-8 JSON: {exc}") from exc


def _validate_json_tree(value: Any, path: str, depth: int = 0) -> None:
    if depth > 24:
        raise HostBoundaryError(f"{path} exceeds host JSON nesting depth 24")
    if value is None or isinstance(value, (str, int, bool)):
        if isinstance(value, str):
            _utf8_bytes(value, path)
        return
    if isinstance(value, float):
        if not math.isfinite(value):
            raise HostBoundaryError(f"{path} contains NaN or infinity")
        return
    if isinstance(value, list):
        for index, item in enumerate(value):
            _validate_json_tree(item, f"{path}[{index}]", depth + 1)
        return
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise HostBoundaryError(f"{path} object keys must be strings")
            _utf8_bytes(key, f"{path}.<key>")
            _validate_json_tree(item, f"{path}.{key}", depth + 1)
        return
    raise HostBoundaryError(f"{path} contains non-JSON value {type(value).__name__}")


def _isolated_json(value: Any, label: str) -> Any:
    try:
        snapshot = copy.deepcopy(value)
    except Exception as exc:
        raise HostBoundaryError(f"{label} could not be copied: {exc}") from exc
    _validate_json_tree(snapshot, label)
    return snapshot


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _reject_history_import_keys(value: Any, path: str = "options") -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            normalized = key.lower().replace("-", "_")
            if normalized in HISTORY_IMPORT_KEYS:
                raise HostBoundaryError(f"{path}.{key} can import prior context and is forbidden")
            _reject_history_import_keys(item, f"{path}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _reject_history_import_keys(item, f"{path}[{index}]")

__all__ = [name for name in globals() if not name.startswith('__')]

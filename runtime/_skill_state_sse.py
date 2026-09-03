"""Finite Responses SSE parsing for the Codex benchmark wire profile."""

from __future__ import annotations

import copy
import json
from types import MappingProxyType
from typing import Any, Mapping

from runtime.skill_state_host import HostTransportError
from runtime._skill_state_wire_profile import canonical_json_bytes, sha256_bytes


def _flush_sse_event(
    events: list[tuple[str | None, dict[str, Any]]],
    event_name: str | None,
    data_lines: list[str],
) -> None:
    if not data_lines:
        return
    data = "\n".join(data_lines)
    if data == "[DONE]":
        return
    try:
        payload = json.loads(data)
    except json.JSONDecodeError as exc:
        raise HostTransportError(f"invalid JSON in SSE data event: {exc}") from exc
    if not isinstance(payload, dict):
        raise HostTransportError("SSE data event must contain a JSON object")
    events.append((event_name, payload))


def parse_sse_events(raw_body: bytes) -> tuple[tuple[str | None, Mapping[str, Any]], ...]:
    try:
        text = raw_body.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise HostTransportError(f"SSE response is not valid UTF-8: {exc}") from exc
    events: list[tuple[str | None, dict[str, Any]]] = []
    event_name: str | None = None
    data_lines: list[str] = []
    for raw_line in text.replace("\r\n", "\n").replace("\r", "\n").split("\n"):
        if raw_line == "":
            _flush_sse_event(events, event_name, data_lines)
            event_name, data_lines = None, []
            continue
        if raw_line.startswith(":"):
            continue
        field, separator, value = raw_line.partition(":")
        if separator and value.startswith(" "):
            value = value[1:]
        if field == "event":
            event_name = value
        elif field == "data":
            data_lines.append(value)
    _flush_sse_event(events, event_name, data_lines)
    if not events:
        raise HostTransportError("SSE response contained no JSON data events")
    return tuple((name, MappingProxyType(payload)) for name, payload in events)


def normalize_sse_response(raw_body: bytes) -> tuple[bytes, Mapping[str, Any]]:
    events = parse_sse_events(raw_body)
    output_items: list[dict[str, Any]] = []
    output_item_keys: set[str] = set()
    output_text_done: list[str] = []
    completed: dict[str, Any] | None = None
    event_types: list[str] = []

    for event_name, event_mapping in events:
        event = dict(event_mapping)
        event_type = event.get("type")
        if not isinstance(event_type, str):
            event_type = event_name
        if not isinstance(event_type, str) or not event_type:
            raise HostTransportError("SSE event has no type")
        if event_name and event.get("type") and event_name != event.get("type"):
            raise HostTransportError(
                f"SSE event name {event_name!r} disagrees with payload type {event.get('type')!r}"
            )
        event_types.append(event_type)
        if event_type in {"error", "response.failed"}:
            raise HostTransportError(
                f"model SSE stream failed with event {event_type}"
            )
        if event_type == "response.output_item.done":
            item = event.get("item")
            if not isinstance(item, dict):
                raise HostTransportError(
                    "response.output_item.done is missing an item object"
                )
            key = str(item.get("id") or sha256_bytes(canonical_json_bytes(item)))
            if key not in output_item_keys:
                output_item_keys.add(key)
                output_items.append(copy.deepcopy(item))
        elif event_type == "response.output_text.done":
            text = event.get("text")
            if isinstance(text, str) and text:
                output_text_done.append(text)
        elif event_type == "response.completed":
            response = event.get("response")
            if not isinstance(response, dict):
                raise HostTransportError(
                    "response.completed is missing a response object"
                )
            if completed is not None:
                raise HostTransportError(
                    "SSE stream contains more than one response.completed event"
                )
            completed = copy.deepcopy(response)

    if completed is None:
        raise HostTransportError("SSE stream closed before response.completed")
    if completed.get("status") not in (None, "completed"):
        raise HostTransportError(
            f"completed SSE response has non-completed status {completed.get('status')!r}"
        )
    completed["status"] = "completed"

    existing_output = completed.get("output")
    if existing_output is None or existing_output == []:
        completed["output"] = output_items
    elif not isinstance(existing_output, list):
        raise HostTransportError("completed response output must be an array")
    elif output_items and canonical_json_bytes(existing_output) != canonical_json_bytes(output_items):
        raise HostTransportError(
            "completed response output disagrees with output_item.done events"
        )

    if not completed.get("output") and output_text_done:
        completed["output"] = [
            {
                "type": "message",
                "role": "assistant",
                "content": [
                    {"type": "output_text", "text": "".join(output_text_done)}
                ],
            }
        ]

    text_parts: list[str] = []
    for item in completed.get("output") or []:
        if not isinstance(item, dict) or item.get("type") != "message":
            continue
        for block in item.get("content") or []:
            if (
                isinstance(block, dict)
                and block.get("type") == "output_text"
                and isinstance(block.get("text"), str)
            ):
                text_parts.append(block["text"])
    if text_parts:
        completed["output_text"] = "".join(text_parts)

    normalized = canonical_json_bytes(completed)
    metadata = MappingProxyType(
        {
            "sse_event_count": len(events),
            "sse_event_types": event_types,
            "sse_completed_event_count": event_types.count("response.completed"),
            "sse_output_item_done_count": event_types.count(
                "response.output_item.done"
            ),
            "raw_sse_sha256": sha256_bytes(raw_body),
            "raw_sse_bytes": len(raw_body),
            "normalized_response_sha256": sha256_bytes(normalized),
            "normalized_response_bytes": len(normalized),
        }
    )
    return normalized, metadata

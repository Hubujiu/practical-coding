from __future__ import annotations

from runtime._skill_state_host_types import *
from runtime._skill_state_host_codec import *
from runtime._skill_state_host_config import *
from runtime._skill_state_host_contract import *

def _extract_output_text(response: Mapping[str, Any]) -> str:
    error = response.get("error")
    if error not in (None, {}):
        raise HostBoundaryError(f"model response contains an error: {error}")
    status = response.get("status")
    if status is not None and status != "completed":
        raise HostBoundaryError(f"model response status is not completed: {status!r}")

    direct = response.get("output_text")
    output = response.get("output")
    if not isinstance(output, list):
        raise HostBoundaryError("raw model response output must be an array")

    message_count = 0
    text_parts: list[str] = []
    for index, item in enumerate(output):
        if not isinstance(item, dict):
            raise HostBoundaryError(f"response.output[{index}] must be an object")
        item_type = item.get("type")
        if item_type == "reasoning":
            continue
        if item_type != "message":
            raise HostBoundaryError(
                f"response.output[{index}] has unsupported type {item_type!r}; expected one transition message"
            )
        message_count += 1
        if item.get("role") not in (None, "assistant"):
            raise HostBoundaryError(f"response.output[{index}] must have assistant role")
        content = item.get("content")
        if not isinstance(content, list) or not content:
            raise HostBoundaryError(f"response.output[{index}].content must be a non-empty array")
        message_parts: list[str] = []
        for content_index, block in enumerate(content):
            if not isinstance(block, dict):
                raise HostBoundaryError(
                    f"response.output[{index}].content[{content_index}] must be an object"
                )
            block_type = block.get("type")
            if block_type == "refusal":
                raise HostBoundaryError("model refused to produce a transition")
            if block_type != "output_text":
                raise HostBoundaryError(
                    f"response output contains unsupported content type {block_type!r}"
                )
            text = block.get("text")
            if not isinstance(text, str):
                raise HostBoundaryError("output_text.text must be a string")
            message_parts.append(text)
        joined_message = "".join(message_parts)
        if not joined_message.strip():
            raise HostBoundaryError("transition message contains no non-empty output_text")
        text_parts.append(joined_message)

    if message_count != 1:
        raise HostBoundaryError(
            f"model response must contain exactly one transition message, got {message_count}"
        )
    joined = "".join(text_parts)
    if direct is not None:
        if not isinstance(direct, str) or direct != joined:
            raise HostBoundaryError("response.output_text does not match the canonical output message")
    return joined

__all__ = [name for name in globals() if not name.startswith('__')]

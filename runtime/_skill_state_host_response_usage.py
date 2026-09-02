from __future__ import annotations

from runtime._skill_state_host_types import *
from runtime._skill_state_host_codec import *
from runtime._skill_state_host_config import *
from runtime._skill_state_host_contract import *

def _usage_summary(response: Mapping[str, Any]) -> dict[str, int | None]:
    usage = response.get("usage")
    if not isinstance(usage, dict):
        return {
            "input_tokens": None,
            "cached_input_tokens": None,
            "uncached_input_tokens": None,
            "output_tokens": None,
            "total_tokens": None,
        }
    cached: int | None = None
    details = usage.get("input_tokens_details")
    if (
        isinstance(details, dict)
        and type(details.get("cached_tokens")) is int
        and details["cached_tokens"] >= 0
    ):
        cached = details["cached_tokens"]

    def integer(name: str) -> int | None:
        value = usage.get(name)
        return value if type(value) is int and value >= 0 else None

    input_tokens = integer("input_tokens")
    uncached = None
    if input_tokens is not None and cached is not None and cached <= input_tokens:
        uncached = input_tokens - cached
    return {
        "input_tokens": input_tokens,
        "cached_input_tokens": cached,
        "uncached_input_tokens": uncached,
        "output_tokens": integer("output_tokens"),
        "total_tokens": integer("total_tokens"),
    }

__all__ = [name for name in globals() if not name.startswith('__')]

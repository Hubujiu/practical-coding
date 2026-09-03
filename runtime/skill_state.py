#!/usr/bin/env python3
"""Validated execution-state facade with cross-field semantic invariants.

The retained implementation lives in ``runtime/_skill_state_impl.py``. This
facade preserves its public API and direct CLI while adding invariants that span
multiple schema containers. See ``docs/SKILL_STATE_INVARIANTS.md``.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Mapping

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime import _skill_state_impl as _impl  # noqa: E402
from runtime._skill_state_impl import *  # noqa: E402,F401,F403

_BASE_VALIDATE_STATE = _impl.validate_state


def validate_state(state: Mapping[str, Any]) -> None:
    """Validate the retained schema plus cross-container semantic invariants."""

    _BASE_VALIDATE_STATE(state)
    hypotheses = state["hypotheses"]
    overlapping_ids = sorted(
        set(hypotheses["active"]) & set(hypotheses["rejected"])
    )
    if overlapping_ids:
        raise StateValidationError(
            "state.hypotheses.active and state.hypotheses.rejected overlap: "
            f"{overlapping_ids}"
        )


# Retained functions resolve ``validate_state`` through their implementation
# module globals at call time. Rebinding it here makes initial_state(), patch
# application, transition validation, prompt construction, and the CLI all use
# the same invariant without duplicating the runtime implementation.
_impl.validate_state = validate_state


if __name__ == "__main__":
    raise SystemExit(_impl.main())

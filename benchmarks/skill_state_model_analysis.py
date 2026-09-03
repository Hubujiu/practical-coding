#!/usr/bin/env python3
"""Execution-state model analysis facade with complete self-test fixtures.

The release-role analysis remains byte-for-byte in
``benchmarks/_skill_state_model_analysis_roles_impl.py``. This facade only fixes
its synthetic fixture: a fixture claiming to represent a complete standard matrix
must cover every frozen standard case, not the legacy placeholder IDs ``a`` and
``b``. Real result analysis and all release thresholds are unchanged.
"""

from __future__ import annotations

import copy
from typing import Any

import _skill_state_model_analysis_roles_impl as _roles
from _skill_state_model_analysis_roles_impl import *  # noqa: F401,F403

_BASE_SYNTHETIC_ROWS = _roles.synthetic_rows


def synthetic_rows() -> list[dict[str, Any]]:
    """Return complete standard fixtures plus the retained bounded fixtures."""

    seed_rows = _BASE_SYNTHETIC_ROWS()
    bounded = [
        copy.deepcopy(row)
        for row in seed_rows
        if row.get("profile") == "bounded"
    ]
    templates: dict[str, dict[str, Any]] = {}
    for row in seed_rows:
        if row.get("profile") != "standard":
            continue
        arm = str(row["arm"])
        templates.setdefault(arm, copy.deepcopy(row))

    missing_arms = set(_roles.REQUIRED_STANDARD_ARMS) - set(templates)
    if missing_arms:
        raise AssertionError(
            "synthetic analysis fixture is missing arm templates: "
            f"{sorted(missing_arms)}"
        )

    standard: list[dict[str, Any]] = []
    for case_id in _roles.EXPECTED_STANDARD_CASE_IDS:
        for arm in _roles.REQUIRED_STANDARD_ARMS:
            row = copy.deepcopy(templates[arm])
            row["case_id"] = case_id
            standard.append(row)
    return standard + bounded


# Both the release-role self-test and the retained CLI main resolve this helper
# through their module globals at runtime.
_roles.synthetic_rows = synthetic_rows
_roles._impl.synthetic_rows = synthetic_rows


def __getattr__(name: str) -> Any:
    return getattr(_roles, name)


if __name__ == "__main__":
    raise SystemExit(_roles._impl.main())

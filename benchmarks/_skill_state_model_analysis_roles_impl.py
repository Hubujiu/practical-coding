#!/usr/bin/env python3
"""Analyze four-arm results without mixing scorer or wire-profile identities.

The retained implementation provides the low-level summaries and cost statistics.
This public entry point defines the release roles of the four arms:

* ``state-history-free`` is the release candidate and is compared with
  ``full-history``;
* ``state-shadow`` is a non-blocking diagnostic arm;
* ``no-skill-full-history`` is an absolute-quality reference;
* a formal execution-state model-gate decision requires a complete repeated
  standard matrix plus the dedicated cost and bounded-context gates.
"""

from __future__ import annotations

import copy
import hashlib
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import _skill_state_model_analysis_impl as _impl
from skill_state_model_cases import (
    ALL_ARMS,
    ARM_FULL_HISTORY,
    ARM_NO_SKILL_FULL_HISTORY,
    ARM_STATE_HISTORY_FREE,
    ARM_STATE_SHADOW,
    select_cases,
)
from skill_state_model_scoring import SCORER_CONTRACT_VERSION
from runtime.skill_state_http_transport import (
    WIRE_PROFILES,
    validate_wire_profile_contract_manifest,
)

ANALYSIS_SCHEMA_VERSION = "1.2"
ANALYSIS_CONTRACT_VERSION = "2.0"
FORMAL_MIN_RUNS = 3
REQUIRED_STANDARD_ARMS = (
    ARM_FULL_HISTORY,
    ARM_STATE_SHADOW,
    ARM_STATE_HISTORY_FREE,
    ARM_NO_SKILL_FULL_HISTORY,
)
EXPECTED_STANDARD_CASE_IDS = tuple(
    sorted(case.case_id for case in select_cases("standard"))
)

_ORIGINAL_VALIDATE_ROWS = _impl.validate_rows
_ORIGINAL_ANALYZE = _impl.analyze
_ORIGINAL_SYNTHETIC_ROWS = _impl.synthetic_rows
_ORIGINAL_RELEASE_SUMMARY = _impl.release_summary
_ORIGINAL_MARKDOWN = _impl.markdown


def validate_rows(rows: Sequence[Mapping[str, Any]]) -> None:
    _ORIGINAL_VALIDATE_ROWS(rows)
    versions = {row.get("scorer_contract_version") for row in rows}
    if versions != {SCORER_CONTRACT_VERSION}:
        raise ValueError(
            "results must all use scorer contract "
            f"{SCORER_CONTRACT_VERSION}; observed={sorted(str(value) for value in versions)}"
        )
    profiles = {row.get("wire_profile") for row in rows}
    unknown = {value for value in profiles if value not in WIRE_PROFILES}
    if unknown:
        raise ValueError(
            f"results contain unknown wire profiles: {sorted(str(value) for value in unknown)}"
        )


def _validate_manifests(
    rows: Sequence[Mapping[str, Any]],
    manifests: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    if not manifests:
        return {
            "supplied": False,
            "validated": False,
            "reason": "no run manifests supplied",
            "manifest_sha256": [],
        }

    validated_digests: set[str] = set()
    profile_contract_digests: set[str] = set()
    profiles: set[str] = set()
    for index, manifest_value in enumerate(manifests):
        if not isinstance(manifest_value, Mapping):
            raise ValueError(f"manifest {index} must be an object")
        manifest = dict(manifest_value)
        if manifest.get("scorer_contract_version") != SCORER_CONTRACT_VERSION:
            raise ValueError(
                f"manifest {index} does not use scorer contract {SCORER_CONTRACT_VERSION}"
            )
        profile = manifest.get("wire_profile")
        if profile not in WIRE_PROFILES:
            raise ValueError(f"manifest {index} has unknown wire profile {profile!r}")
        contract = manifest.get("wire_profile_contract")
        if not isinstance(contract, Mapping):
            raise ValueError(f"manifest {index} is missing wire_profile_contract")
        validated_contract = validate_wire_profile_contract_manifest(contract)
        contract_digest = validated_contract["manifest_sha256"]
        if manifest.get("wire_profile_contract_sha256") != contract_digest:
            raise ValueError(
                f"manifest {index} wire-profile digest does not match its contract"
            )
        digest = manifest.get("manifest_sha256")
        if not isinstance(digest, str) or not digest:
            raise ValueError(f"manifest {index} has no manifest_sha256")
        validated_digests.add(digest)
        profile_contract_digests.add(contract_digest)
        profiles.add(str(profile))

    row_digests = {
        row.get("runner_manifest_sha256")
        for row in rows
        if isinstance(row.get("runner_manifest_sha256"), str)
    }
    if not row_digests:
        raise ValueError("results do not contain runner_manifest_sha256")
    missing = row_digests - validated_digests
    if missing:
        raise ValueError(
            "result rows reference manifests that were not supplied: "
            + ", ".join(sorted(missing))
        )
    return {
        "supplied": True,
        "validated": True,
        "manifest_sha256": sorted(validated_digests),
        "wire_profiles": sorted(profiles),
        "wire_profile_contract_sha256": sorted(profile_contract_digests),
        "scorer_contract_version": SCORER_CONTRACT_VERSION,
    }


def _combine_statuses(values: Sequence[str]) -> str:
    if _impl.FAIL in values:
        return _impl.FAIL
    if values and all(value == _impl.PASS for value in values):
        return _impl.PASS
    return _impl.PENDING


def _quality_gate_for_arm(
    rows: Sequence[Mapping[str, Any]],
    *,
    candidate_arm: str,
    margin: float,
    blocking: bool,
) -> dict[str, Any]:
    arms = _impl.arm_summary(rows)
    full = arms.get(ARM_FULL_HISTORY)
    candidate = arms.get(candidate_arm)
    base = {
        "candidate_arm": candidate_arm,
        "comparison_arm": ARM_FULL_HISTORY,
        "margin": margin,
        "blocking": blocking,
    }
    if full is None or candidate is None:
        return {**base, "status": _impl.PENDING, "reason": "required arms are missing"}
    if full["determinate"] != full["cells"] or candidate["determinate"] != candidate["cells"]:
        return {
            **base,
            "status": _impl.PENDING,
            "reason": "required arm contains indeterminate cells",
        }
    if full["pass_rate"] is None or candidate["pass_rate"] is None:
        return {**base, "status": _impl.PENDING, "reason": "pass rate unavailable"}
    delta = candidate["pass_rate"] - full["pass_rate"]
    return {
        **base,
        "status": _impl.FAIL if delta < -margin else _impl.PASS,
        "full_history_pass_rate": full["pass_rate"],
        "candidate_pass_rate": candidate["pass_rate"],
        "delta": delta,
        "failures": {candidate_arm: delta} if delta < -margin else {},
    }


def quality_gate(rows: Sequence[Mapping[str, Any]], margin: float) -> dict[str, Any]:
    """Blocking quality gate for the history-free candidate only."""

    result = _quality_gate_for_arm(
        rows,
        candidate_arm=ARM_STATE_HISTORY_FREE,
        margin=margin,
        blocking=True,
    )
    result["diagnostic_arms_excluded"] = [ARM_STATE_SHADOW]
    return result


def _state_gate_for_arm(
    rows: Sequence[Mapping[str, Any]],
    *,
    arm: str,
    blocking: bool,
) -> dict[str, Any]:
    selected = [row for row in rows if row.get("arm") == arm]
    values: list[bool | None] = []
    failures: list[dict[str, Any]] = []
    for row in selected:
        score = row.get("state_score")
        value = score.get("state_pass") if isinstance(score, Mapping) else None
        normalized = value if isinstance(value, bool) else None
        values.append(normalized)
        if normalized is False:
            failures.append(
                {
                    "case_id": row["case_id"],
                    "arm": row["arm"],
                    "repetition": row["repetition"],
                    "state_mechanism_failures": (
                        score.get("state_mechanism_failures", [])
                        if isinstance(score, Mapping)
                        else []
                    ),
                    "state_required_paths_missing": (
                        score.get("state_required_paths_missing", [])
                        if isinstance(score, Mapping)
                        else []
                    ),
                    "state_required_terms_missing": (
                        score.get("state_required_terms_missing", [])
                        if isinstance(score, Mapping)
                        else []
                    ),
                    "state_forbidden_terms_present": (
                        score.get("state_forbidden_terms_present", [])
                        if isinstance(score, Mapping)
                        else []
                    ),
                }
            )
    return {
        "status": _impl.status(values),
        "arm": arm,
        "blocking": blocking,
        "cells": len(selected),
        "failures": failures,
    }


def state_gate(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Blocking state-semantics gate for the history-free candidate only."""

    return _state_gate_for_arm(
        rows,
        arm=ARM_STATE_HISTORY_FREE,
        blocking=True,
    )


def _artifact_gate_for_arm(
    rows: Sequence[Mapping[str, Any]],
    *,
    arm: str,
    blocking: bool,
) -> dict[str, Any]:
    selected = [
        row
        for row in rows
        if row.get("arm") == arm
        and isinstance(row.get("artifact_score"), Mapping)
        and row["artifact_score"].get("required") is True
    ]
    if not selected:
        return {
            "status": _impl.PASS,
            "arm": arm,
            "blocking": blocking,
            "applicable": False,
            "cells": 0,
            "failures": [],
        }
    values = [row["artifact_score"].get("artifact_pass") for row in selected]
    failures = [
        {
            "case_id": row["case_id"],
            "arm": row["arm"],
            "repetition": row["repetition"],
            "artifact_score": dict(row["artifact_score"]),
        }
        for row in selected
        if row["artifact_score"].get("artifact_pass") is not True
    ]
    return {
        "status": _impl.status(
            [value if isinstance(value, bool) else None for value in values]
        ),
        "arm": arm,
        "blocking": blocking,
        "applicable": True,
        "cells": len(selected),
        "failures": failures,
    }


def artifact_gate(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Blocking history-pointer gate for the history-free candidate only."""

    return _artifact_gate_for_arm(
        rows,
        arm=ARM_STATE_HISTORY_FREE,
        blocking=True,
    )


def state_shadow_diagnostic(
    rows: Sequence[Mapping[str, Any]],
    margin: float,
) -> dict[str, Any]:
    quality = _quality_gate_for_arm(
        rows,
        candidate_arm=ARM_STATE_SHADOW,
        margin=margin,
        blocking=False,
    )
    state = _state_gate_for_arm(
        rows,
        arm=ARM_STATE_SHADOW,
        blocking=False,
    )
    artifact = _artifact_gate_for_arm(
        rows,
        arm=ARM_STATE_SHADOW,
        blocking=False,
    )
    return {
        "status": _combine_statuses(
            [quality["status"], state["status"], artifact["status"]]
        ),
        "blocking": False,
        "role": "diagnostic-only; never changes the history-free release decision",
        "quality_gate": quality,
        "state_semantic_gate": state,
        "history_pointer_gate": artifact,
    }


def release_repetition_gate(
    rows: Sequence[Mapping[str, Any]],
    minimum_runs: int = FORMAL_MIN_RUNS,
) -> dict[str, Any]:
    """Require one complete, determinate standard four-arm matrix at n>=3."""

    standard = [row for row in rows if row.get("profile") == "standard"]
    if not standard:
        return {
            "status": _impl.PENDING,
            "minimum_runs": minimum_runs,
            "reason": "standard profile results are missing",
        }
    case_ids = sorted({str(row["case_id"]) for row in standard})
    issues: list[dict[str, Any]] = []
    expected_cases = set(EXPECTED_STANDARD_CASE_IDS)
    observed_cases = set(case_ids)
    missing_cases = sorted(expected_cases - observed_cases)
    unexpected_cases = sorted(observed_cases - expected_cases)
    if missing_cases:
        issues.append({"reason": "standard cases are missing", "case_ids": missing_cases})
    if unexpected_cases:
        issues.append({"reason": "unexpected standard cases", "case_ids": unexpected_cases})
    details: dict[str, Any] = {}
    for case_id in case_ids:
        per_arm: dict[str, list[int]] = {}
        for arm in REQUIRED_STANDARD_ARMS:
            selected = [
                row
                for row in standard
                if row.get("case_id") == case_id and row.get("arm") == arm
            ]
            repetitions = sorted(int(row["repetition"]) for row in selected)
            per_arm[arm] = repetitions
            required_repetitions = set(range(1, minimum_runs + 1))
            if len(repetitions) < minimum_runs or not required_repetitions.issubset(repetitions):
                issues.append(
                    {
                        "case_id": case_id,
                        "arm": arm,
                        "reason": "insufficient repetitions",
                        "observed": repetitions,
                        "required": sorted(required_repetitions),
                        "minimum_runs": minimum_runs,
                    }
                )
            indeterminate = [
                int(row["repetition"])
                for row in selected
                if row.get("passed") is None
            ]
            if indeterminate:
                issues.append(
                    {
                        "case_id": case_id,
                        "arm": arm,
                        "reason": "indeterminate cells",
                        "repetitions": sorted(indeterminate),
                    }
                )
        repetition_sets = {tuple(value) for value in per_arm.values()}
        if len(repetition_sets) != 1:
            issues.append(
                {
                    "case_id": case_id,
                    "reason": "arm repetition sets are not paired",
                    "per_arm": per_arm,
                }
            )
        details[case_id] = per_arm

    return {
        "status": _impl.PASS if not issues else _impl.PENDING,
        "minimum_runs": minimum_runs,
        "required_arms": list(REQUIRED_STANDARD_ARMS),
        "expected_case_ids": list(EXPECTED_STANDARD_CASE_IDS),
        "case_count": len(case_ids),
        "issues": issues,
        "repetitions": details,
    }


def _defer_cost_gate(
    gate: Mapping[str, Any],
    release_gate: Mapping[str, Any],
) -> dict[str, Any]:
    if release_gate.get("status") == _impl.PASS:
        return dict(gate)
    return {
        "status": _impl.PENDING,
        "reason": "formal cost claim requires a complete determinate standard n>=3 matrix",
        "required_gate": "release_repetition_gate",
        "iteration_estimate": copy.deepcopy(dict(gate)),
    }


def analyze(
    rows: Sequence[Mapping[str, Any]],
    *,
    manifests: Sequence[Mapping[str, Any]] = (),
    margin: float = 0.03,
    token_threshold: float = 0.80,
    latency_threshold: float = 0.90,
    samples: int = 5000,
) -> dict[str, Any]:
    validate_rows(rows)
    manifest_identity = _validate_manifests(rows, manifests)
    result = _ORIGINAL_ANALYZE(
        rows,
        manifests=manifests,
        margin=margin,
        token_threshold=token_threshold,
        latency_threshold=latency_threshold,
        samples=samples,
    )
    result["schema_version"] = ANALYSIS_SCHEMA_VERSION
    result["analysis_contract_version"] = ANALYSIS_CONTRACT_VERSION
    result["analysis_source_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    result["retained_analysis_impl_sha256"] = hashlib.sha256(
        (HERE / "_skill_state_model_analysis_impl.py").read_bytes()
    ).hexdigest()
    result["scorer_contract_version"] = SCORER_CONTRACT_VERSION
    result["wire_profiles"] = sorted({str(row["wire_profile"]) for row in rows})
    result["manifest_identity"] = manifest_identity

    gates = result["gates"]
    release_gate = release_repetition_gate(rows)
    shadow = state_shadow_diagnostic(rows, margin)
    candidate_status = _combine_statuses(
        [
            gates["quality_gate"]["status"],
            gates["state_semantic_gate"]["status"],
            gates["history_pointer_gate"]["status"],
            gates["client_transport_gate"]["status"],
        ]
    )
    gates["history_free_candidate_gate"] = {
        "status": candidate_status,
        "blocking": True,
        "components": [
            "quality_gate",
            "state_semantic_gate",
            "history_pointer_gate",
            "client_transport_gate",
        ],
    }
    gates["state_shadow_diagnostic"] = shadow
    gates["release_repetition_gate"] = release_gate
    gates["token_gate"] = _defer_cost_gate(gates["token_gate"], release_gate)
    gates["latency_gate"] = _defer_cost_gate(gates["latency_gate"], release_gate)

    formal_components = [
        candidate_status,
        release_gate["status"],
        gates["token_gate"]["status"],
        gates["latency_gate"]["status"],
        gates["bounded_context_gate"]["status"],
    ]
    formal_status = _combine_statuses(formal_components)
    if not manifest_identity["validated"]:
        formal_status = _impl.PENDING
        result["manifest_identity"]["formal_gate_eligible"] = False
    else:
        result["manifest_identity"]["formal_gate_eligible"] = True
    gates["execution_state_model_gate"] = formal_status

    result["claim_status"] = {
        "history_free_quality_and_transport": candidate_status,
        "formal_n3_matrix": release_gate["status"],
        "token_benefit": gates["token_gate"]["status"],
        "latency_benefit": gates["latency_gate"]["status"],
        "bounded_client_context": gates["bounded_context_gate"]["status"],
    }
    result["gate_roles"] = {
        "blocking_candidate": ARM_STATE_HISTORY_FREE,
        "comparison": ARM_FULL_HISTORY,
        "diagnostic_only": ARM_STATE_SHADOW,
        "absolute_quality_reference": ARM_NO_SKILL_FULL_HISTORY,
        "formal_minimum_runs": FORMAL_MIN_RUNS,
    }
    return result


def synthetic_rows() -> list[dict[str, Any]]:
    rows = _ORIGINAL_SYNTHETIC_ROWS()
    for row in rows:
        row["scorer_contract_version"] = SCORER_CONTRACT_VERSION
        row["wire_profile"] = "responses-json-v1"
        row["runner_manifest_sha256"] = "synthetic-manifest"
    return rows


def release_summary(analysis: Mapping[str, Any]) -> dict[str, Any]:
    summary = _ORIGINAL_RELEASE_SUMMARY(analysis)
    gates = analysis["gates"]
    summary.update(
        {
            "schema_version": ANALYSIS_SCHEMA_VERSION,
            "analysis_contract_version": analysis["analysis_contract_version"],
            "analysis_source_sha256": analysis["analysis_source_sha256"],
            "retained_analysis_impl_sha256": analysis["retained_analysis_impl_sha256"],
            "history_free_candidate_gate": gates["history_free_candidate_gate"]["status"],
            "release_repetition_gate": gates["release_repetition_gate"]["status"],
            "state_shadow_diagnostic": gates["state_shadow_diagnostic"]["status"],
            "claim_status": analysis["claim_status"],
            "gate_roles": analysis["gate_roles"],
        }
    )
    return summary


def markdown(analysis: Mapping[str, Any]) -> str:
    text = _ORIGINAL_MARKDOWN(analysis).rstrip()
    gates = analysis["gates"]
    shadow = gates["state_shadow_diagnostic"]
    lines = [
        text,
        "",
        "## Gate roles",
        "",
        "| Role | Arm / requirement | Status | Blocking |",
        "|---|---|---|---|",
        f"| History-free candidate | {ARM_STATE_HISTORY_FREE} vs {ARM_FULL_HISTORY} | {gates['history_free_candidate_gate']['status']} | yes |",
        f"| Repeated release matrix | standard n>={FORMAL_MIN_RUNS}, four paired arms | {gates['release_repetition_gate']['status']} | yes |",
        f"| State-shadow diagnostic | {ARM_STATE_SHADOW} | {shadow['status']} | no |",
        f"| Token benefit claim | paired uncached input tokens | {gates['token_gate']['status']} | yes for the composite claim |",
        f"| Latency benefit claim | paired end-to-end duration | {gates['latency_gate']['status']} | yes for the composite claim |",
        f"| Bounded client-context claim | 10/25/50/100 horizon audit | {gates['bounded_context_gate']['status']} | yes for the composite claim |",
        "",
        "## State-shadow diagnostics",
        "",
        f"- quality: **{shadow['quality_gate']['status']}**",
        f"- state semantics: **{shadow['state_semantic_gate']['status']}**",
        f"- history pointer: **{shadow['history_pointer_gate']['status']}**",
        "- This arm is diagnostic only. Its failure does not change the history-free candidate gate.",
    ]
    failures = shadow["state_semantic_gate"].get("failures") or []
    if failures:
        lines += ["", "State-shadow semantic failures:", ""]
        for failure in failures:
            lines.append(
                f"- `{failure['case_id']}` repetition {failure['repetition']}: "
                f"mechanism={failure.get('state_mechanism_failures') or []}; "
                f"missing_paths={failure.get('state_required_paths_missing') or []}; "
                f"missing_terms={failure.get('state_required_terms_missing') or []}; "
                f"forbidden_terms={failure.get('state_forbidden_terms_present') or []}"
            )
    lines += [
        "",
        "## Formal-status rule",
        "",
        "An n=1 run is iteration evidence. It may pass or fail the history-free candidate checks, but it cannot make the formal composite model gate PASS. The composite gate also requires a complete determinate standard n>=3 matrix, token and latency gates, and the bounded-context horizon gate. State-shadow remains visible as a diagnostic rather than a release veto.",
        "",
    ]
    return "\n".join(lines)


def self_test() -> None:
    rows = synthetic_rows()

    # Preserve the retained implementation's low-level statistical coverage.
    legacy = _ORIGINAL_ANALYZE(rows, samples=200)
    assert legacy["gates"]["quality_gate"]["status"] == _impl.PASS

    result = analyze(rows, samples=200)
    assert result["gates"]["quality_gate"]["status"] == _impl.PASS
    assert result["gates"]["history_free_candidate_gate"]["status"] == _impl.PASS
    assert result["gates"]["release_repetition_gate"]["status"] == _impl.PENDING
    assert result["gates"]["token_gate"]["status"] == _impl.PENDING
    assert result["gates"]["latency_gate"]["status"] == _impl.PENDING
    assert result["gates"]["execution_state_model_gate"] == _impl.PENDING
    assert result["manifest_identity"]["validated"] is False

    shadow_failure = copy.deepcopy(rows)
    shadow_row = next(
        row
        for row in shadow_failure
        if row["profile"] == "standard" and row["arm"] == ARM_STATE_SHADOW
    )
    shadow_row["passed"] = False
    shadow_row["verdict"] = "fail"
    shadow_row["state_score"] = {"state_pass": False, "state_mechanism_failures": ["synthetic"]}
    diagnosed = analyze(shadow_failure, samples=20)
    assert diagnosed["gates"]["quality_gate"]["status"] == _impl.PASS
    assert diagnosed["gates"]["state_semantic_gate"]["status"] == _impl.PASS
    assert diagnosed["gates"]["state_shadow_diagnostic"]["status"] == _impl.FAIL

    repeated: list[dict[str, Any]] = []
    for row in rows:
        if row["profile"] != "standard":
            continue
        for repetition in (1, 2, 3):
            clone = copy.deepcopy(row)
            clone["repetition"] = repetition
            repeated.append(clone)
    assert release_repetition_gate(repeated)["status"] == _impl.PASS

    try:
        invalid = copy.deepcopy(rows)
        invalid[0]["scorer_contract_version"] = "1.0"
        analyze(invalid, samples=10)
    except ValueError:
        pass
    else:
        raise AssertionError("mixed scorer identities were not rejected")
    print("skill-state model analysis role hardening: PASS")


# The retained implementation resolves these names dynamically from its module
# globals. Patch only stable analysis extension points; the raw reader and cost
# calculations remain unchanged.
_impl.quality_gate = quality_gate
_impl.state_gate = state_gate
_impl.artifact_gate = artifact_gate
_impl.validate_rows = validate_rows
_impl.analyze = analyze
_impl.synthetic_rows = synthetic_rows
_impl.release_summary = release_summary
_impl.markdown = markdown
_impl.self_test = self_test


def __getattr__(name: str) -> Any:
    return getattr(_impl, name)


if __name__ == "__main__":
    raise SystemExit(_impl.main())

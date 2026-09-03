#!/usr/bin/env python3
"""Analyze four-arm results without mixing scorer or wire-profile identities.

The ea8580f analysis implementation is retained in
``benchmarks/_skill_state_model_analysis_impl.py``.  This entry point requires the
repaired general scorer identity on every result row and validates supplied run
manifests before any quality or cost gate is computed.
"""

from __future__ import annotations

import copy
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
from skill_state_model_scoring import SCORER_CONTRACT_VERSION
from runtime.skill_state_http_transport import (
    WIRE_PROFILES,
    validate_wire_profile_contract_manifest,
)

ANALYSIS_SCHEMA_VERSION = "1.1"

_ORIGINAL_VALIDATE_ROWS = _impl.validate_rows
_ORIGINAL_ANALYZE = _impl.analyze
_ORIGINAL_SYNTHETIC_ROWS = _impl.synthetic_rows
_ORIGINAL_SELF_TEST = _impl.self_test


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
        raise ValueError(f"results contain unknown wire profiles: {sorted(str(value) for value in unknown)}")


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
            raise ValueError(f"manifest {index} wire-profile digest does not match its contract")
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
    result["scorer_contract_version"] = SCORER_CONTRACT_VERSION
    result["wire_profiles"] = sorted({str(row["wire_profile"]) for row in rows})
    result["manifest_identity"] = manifest_identity
    if not manifest_identity["validated"]:
        # Results can still be inspected, but an unbound analysis cannot become a
        # formal execution-state model-gate pass.
        result["gates"]["execution_state_model_gate"] = _impl.PENDING
        result["manifest_identity"]["formal_gate_eligible"] = False
    else:
        result["manifest_identity"]["formal_gate_eligible"] = True
    return result


def synthetic_rows() -> list[dict[str, Any]]:
    rows = _ORIGINAL_SYNTHETIC_ROWS()
    for row in rows:
        row["scorer_contract_version"] = SCORER_CONTRACT_VERSION
        row["wire_profile"] = "responses-json-v1"
        row["runner_manifest_sha256"] = "synthetic-manifest"
    return rows


def self_test() -> None:
    _ORIGINAL_SELF_TEST()
    rows = synthetic_rows()
    result = analyze(rows, samples=200)
    assert result["gates"]["quality_gate"]["status"] == _impl.PASS
    assert result["gates"]["execution_state_model_gate"] == _impl.PENDING
    assert result["manifest_identity"]["validated"] is False
    try:
        invalid = copy.deepcopy(rows)
        invalid[0]["scorer_contract_version"] = "1.0"
        analyze(invalid, samples=10)
    except ValueError:
        pass
    else:
        raise AssertionError("mixed scorer identities were not rejected")
    print("skill-state model analysis identity hardening: PASS")


_impl.validate_rows = validate_rows
_impl.analyze = analyze
_impl.synthetic_rows = synthetic_rows
_impl.self_test = self_test


def __getattr__(name: str) -> Any:
    return getattr(_impl, name)


if __name__ == "__main__":
    raise SystemExit(_impl.main())

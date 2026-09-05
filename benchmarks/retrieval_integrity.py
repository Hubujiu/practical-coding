"""Freeze Retrieval experiments and reject stale or incomplete measurements.

These hashes identify declared inputs; they are not execution attestations.
No credentials, setup costs, or historical result files enter the identity.
"""
from __future__ import annotations

import hashlib
import json
import os
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence


class IntegrityError(ValueError):
    """A result cannot be compared with the frozen experiment."""


def digest(value: Any) -> str:
    data = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def source_files(root: Path, *, harness: bool = True) -> dict[str, str]:
    if not (root / "SKILL.md").is_file():
        raise IntegrityError(f"missing Skill source: {root}")
    paths = {root / "SKILL.md", root / "AGENTS.md"}
    for folder in ("references", "agents"):
        paths.update(path for path in (root / folder).rglob("*") if path.is_file())
    if harness:
        for pattern in ("*.py", "*.json"):
            paths.update((root / "benchmarks").glob(pattern))
    return {
        path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(paths) if path.is_file()
    }


def make_plan(
    root: Path, baseline: Path | None, settings: Mapping[str, Any],
    manifest: Mapping[str, Any], topology: Mapping[str, Any],
    preflight: Mapping[str, Any], specs: Sequence[tuple[str, str, int]],
) -> dict[str, Any]:
    if not specs or len(set(specs)) != len(specs):
        raise IntegrityError("run plan must contain unique, nonempty cell specifications")
    if any(not task or not arm or type(rep) is not int or rep < 1 for task, arm, rep in specs):
        raise IntegrityError("invalid task, arm, or repetition in run plan")
    plan: dict[str, Any] = {
        "schema_version": "1.0",
        "source_files": source_files(root),
        "baseline_files": source_files(baseline, harness=False) if baseline is not None else None,
        "settings": dict(settings),
        "manifest": dict(manifest),
        "topology": dict(topology),
        "providers": [
            {key: probe.get(key) for key in ("provider", "role", "observed_version_output")}
            for probe in preflight.get("provider_probes", [])
        ],
        "specs": [list(spec) for spec in sorted(specs)],
    }
    plan["experiment_fingerprint"] = digest(plan)
    return plan


def verify_plan(plan: Mapping[str, Any]) -> None:
    expected = digest({key: value for key, value in plan.items() if key != "experiment_fingerprint"})
    if plan.get("experiment_fingerprint") != expected:
        raise IntegrityError("run plan fingerprint does not match its contents")
    specs = plan.get("specs", [])
    if not specs or any(
        not isinstance(spec, (list, tuple)) or len(spec) != 3
        or not isinstance(spec[0], str) or not spec[0]
        or not isinstance(spec[1], str) or not spec[1]
        or type(spec[2]) is not int or spec[2] < 1 for spec in specs
    ):
        raise IntegrityError("run plan has invalid cell specifications")
    if len({tuple(spec) for spec in specs}) != len(specs):
        raise IntegrityError("run plan has duplicate cell specifications")


def write_plan(path: Path, plan: Mapping[str, Any]) -> None:
    verify_plan(plan)
    if path.exists():
        if json.loads(path.read_text(encoding="utf-8")) != plan:
            raise IntegrityError("output belongs to a different experiment; choose a new --output directory")
        return
    if next((path.parent / "cells").rglob("result.json"), None) is not None:
        raise IntegrityError("legacy cached results have no frozen run plan; choose a new --output directory")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as stream:
        json.dump(plan, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write("\n")


def validate_cached_result(
    record: Mapping[str, Any], setup: Mapping[str, Any], plan: Mapping[str, Any],
    spec: tuple[str, str, int], manifest_sha: str, *, cell_dir: Path | None = None,
) -> None:
    verify_plan(plan)
    fingerprint = plan.get("experiment_fingerprint")
    if not fingerprint or list(spec) not in plan.get("specs", []):
        raise IntegrityError("cell is not part of the frozen run plan")
    if any(item.get("experiment_fingerprint") != fingerprint for item in (record, setup)):
        raise IntegrityError("cached result or setup receipt belongs to a different experiment")
    if (type(record.get("repetition")) is not int
            or tuple(record.get(key) for key in ("task_id", "variant", "repetition")) != spec):
        raise IntegrityError("cached result has the wrong task, arm, or repetition")
    if setup.get("manifest_sha256") != manifest_sha:
        raise IntegrityError("cached result has a stale setup receipt")
    if (record.get("measurement_phase") != "measured"
            or record.get("setup_included_in_comparison") is not False):
        raise IntegrityError("cached result violates setup/measurement separation")

    if cell_dir is not None:
        if setup.get("cell") != list(spec):
            raise IntegrityError("setup receipt has the wrong cell identity")
        validate_artifacts(record, cell_dir)


def artifact_hashes(cell_dir: Path) -> dict[str, str]:
    names = ("prompt.txt", "round1.jsonl", "round1.stderr.txt", "capability-setup.json")
    if (cell_dir / "submission.json").exists():
        names += ("submission.json",)
    return {name: hashlib.sha256((cell_dir / name).read_bytes()).hexdigest() for name in names}


def validate_artifacts(record: Mapping[str, Any], cell_dir: Path) -> None:
    expected = record.get("artifact_sha256")
    if not isinstance(expected, dict) or expected != artifact_hashes(cell_dir):
        raise IntegrityError("raw transcript, prompt, or setup evidence changed or is missing")


def write_result(path: Path, record: Mapping[str, Any]) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(record, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def matrix_status(rows: list[dict[str, Any]], plan: Mapping[str, Any] | None) -> dict[str, Any]:
    for index, row in enumerate(rows):
        if (not isinstance(row, Mapping)
                or any(not isinstance(row.get(key), str) or not row[key] for key in ("task_id", "variant"))
                or type(row.get("repetition")) is not int or row["repetition"] < 1):
            raise IntegrityError(f"invalid cell identity at row {index}")
    keys = [(row["task_id"], row["variant"], row["repetition"]) for row in rows]
    counts = Counter(keys)
    duplicates = [list(key) for key, count in counts.items() if count > 1]
    invalid: list[int] = []
    indeterminate = [i for i, row in enumerate(rows) if row.get("passed") is None]
    for index, row in enumerate(rows):
        flags = ("measured_setup_violation", "capability_ceiling_violation")
        observations = ("routing_trace_valid", "retrieval_reference_observation_ok")
        if (
            (row.get("schema_version") == "3.0" and row.get("measurement_qualified") is not True)
            or "passed" not in row or (row["passed"] is not None and type(row["passed"]) is not bool)
            or type(row.get("repetition")) is not int or row["repetition"] < 1
            or row.get("measurement_phase") != "measured"
            or row.get("setup_included_in_comparison") is not False
            or row.get("measured_setup_violation") is not False
            or any(row.get(flag) is True for flag in flags)
            or (row.get("passed") is True and any(row.get(flag) is False for flag in observations))
            or (row.get("timed_out") is True and row.get("passed") is not None)
        ):
            invalid.append(index)
    missing: list[list[Any]] = []
    unexpected: list[list[Any]] = []
    mismatched: list[int] = []
    if plan is not None:
        verify_plan(plan)
        expected = {tuple(spec) for spec in plan["specs"]}
        missing = [list(key) for key in sorted(expected - set(keys))]
        unexpected = [list(key) for key in set(keys) - expected]
        mismatched = [i for i, row in enumerate(rows)
                      if row.get("experiment_fingerprint") != plan["experiment_fingerprint"]]
    return {
        "plan_provided": plan is not None,
        "complete": plan is not None and not (duplicates or invalid or missing or unexpected or mismatched or indeterminate),
        "duplicate_cells": duplicates,
        "invalid_row_indices": invalid,
        "indeterminate_row_indices": indeterminate,
        "missing_cells": missing,
        "unexpected_cells": unexpected,
        "identity_mismatch_row_indices": mismatched,
    }

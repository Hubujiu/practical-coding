#!/usr/bin/env python3
"""Analyze execution-state four-arm results without hiding missing cells.

Quality and transport integrity gate all cost claims. Missing, duplicate, or
indeterminate cells never become PASS. Token and latency benefits are reported as
separate paired gates rather than being traded against delivered quality.
"""

from __future__ import annotations

import argparse
import json
import math
import random
import statistics
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from skill_state_model_cases import BOUNDED_HORIZONS  # noqa: E402
from skill_state_model_runner import ARMS  # noqa: E402


VERSION = "1.0"
QUALITY_MARGIN = 0.0
TOKEN_RATIO_LIMIT = 0.80
LATENCY_RATIO_LIMIT = 0.90
BOOTSTRAP_SAMPLES = 5000


class AnalysisError(ValueError):
    """Raised when result artifacts violate the frozen analysis contract."""


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise AnalysisError(f"cannot read {path}: {exc}") from exc


def load_results(paths: Iterable[Path]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in paths:
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except OSError as exc:
            raise AnalysisError(f"cannot read {path}: {exc}") from exc
        for line_number, line in enumerate(lines, 1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise AnalysisError(f"invalid JSON at {path}:{line_number}: {exc}") from exc
            if not isinstance(row, dict):
                raise AnalysisError(f"result at {path}:{line_number} is not an object")
            row = dict(row)
            row["_source"] = str(path)
            rows.append(row)
    if not rows:
        raise AnalysisError("no result rows were loaded")
    return rows


def load_manifests(paths: Iterable[Path]) -> list[dict[str, Any]]:
    manifests: list[dict[str, Any]] = []
    for path in paths:
        value = _load_json(path)
        if not isinstance(value, dict):
            raise AnalysisError(f"manifest is not an object: {path}")
        value = dict(value)
        value["_source"] = str(path)
        manifests.append(value)
    return manifests


def _cell_key(row: Mapping[str, Any]) -> tuple[str, str, int]:
    case_id = row.get("case_id")
    arm = row.get("arm")
    repetition = row.get("repetition")
    if not isinstance(case_id, str) or arm not in ARMS or type(repetition) is not int:
        raise AnalysisError(f"invalid cell identity: {row}")
    return case_id, str(arm), repetition


def matrix_report(rows: Sequence[dict[str, Any]], manifests: Sequence[dict[str, Any]]) -> dict[str, Any]:
    grouped: dict[tuple[str, str, int], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[_cell_key(row)].append(row)
    duplicates = [list(key) for key, values in grouped.items() if len(values) != 1]

    expected: set[tuple[str, str, int]] = set()
    for manifest in manifests:
        cells = manifest.get("expected_cells")
        if not isinstance(cells, list):
            continue
        for item in cells:
            if not isinstance(item, dict):
                raise AnalysisError("manifest expected_cells must contain objects")
            expected.add((str(item.get("case_id")), str(item.get("arm")), int(item.get("repetition"))))
    observed = set(grouped)
    missing = [list(key) for key in sorted(expected - observed)]
    unexpected = [list(key) for key in sorted(observed - expected)] if expected else []
    indeterminate = [
        list(key)
        for key, values in grouped.items()
        if len(values) == 1 and values[0].get("passed") is None
    ]
    complete_manifest = bool(manifests) and all(isinstance(value.get("expected_cells"), list) for value in manifests)
    passed = complete_manifest and not duplicates and not missing and not unexpected and not indeterminate
    return {
        "status": "PASS" if passed else "FAIL" if complete_manifest else "PENDING",
        "manifest_complete": complete_manifest,
        "expected_cells": len(expected),
        "observed_cells": len(rows),
        "unique_cells": len(observed),
        "duplicates": duplicates,
        "missing": missing,
        "unexpected": unexpected,
        "indeterminate": indeterminate,
    }


def _paired(rows: Sequence[dict[str, Any]], candidate: str, baseline: str) -> list[tuple[dict[str, Any], dict[str, Any]]]:
    by_key = {_cell_key(row): row for row in rows}
    pairs: list[tuple[dict[str, Any], dict[str, Any]]] = []
    identities = sorted({(row["case_id"], row["repetition"]) for row in rows})
    for case_id, repetition in identities:
        left = by_key.get((case_id, candidate, repetition))
        right = by_key.get((case_id, baseline, repetition))
        if left is not None and right is not None:
            pairs.append((left, right))
    return pairs


def quality_report(rows: Sequence[dict[str, Any]], matrix: Mapping[str, Any]) -> dict[str, Any]:
    determinate = [row for row in rows if row.get("passed") is not None]
    arms: dict[str, Any] = {}
    for arm in ARMS:
        selected = [row for row in rows if row.get("arm") == arm]
        arm_determinate = [row for row in selected if row.get("passed") is not None]
        arms[arm] = {
            "cells": len(selected),
            "determinate": len(arm_determinate),
            "passed": sum(row.get("passed") is True for row in arm_determinate),
            "pass_rate": None
            if not arm_determinate
            else sum(row.get("passed") is True for row in arm_determinate) / len(arm_determinate),
        }

    comparisons: dict[str, Any] = {}
    quality_ok = matrix.get("status") == "PASS"
    for candidate in ("state-shadow", "state-history-free"):
        pairs = _paired(rows, candidate, "full-history")
        regressions = [
            [left["case_id"], left["repetition"]]
            for left, right in pairs
            if right.get("passed") is True and left.get("passed") is not True
        ]
        comparison_pass = bool(pairs) and not regressions and all(
            left.get("passed") is not None and right.get("passed") is not None
            for left, right in pairs
        )
        comparisons[f"{candidate}_vs_full_history"] = {
            "pairs": len(pairs),
            "regressions": regressions,
            "status": "PASS" if comparison_pass else "FAIL",
        }
        quality_ok = quality_ok and comparison_pass
    return {
        "status": "PASS" if quality_ok else "FAIL",
        "margin": QUALITY_MARGIN,
        "arms": arms,
        "comparisons": comparisons,
        "determinate_cells": len(determinate),
    }


def state_report(rows: Sequence[dict[str, Any]]) -> dict[str, Any]:
    state_rows = [row for row in rows if row.get("arm") in {"state-shadow", "state-history-free"}]
    semantic_failures = [
        [row["case_id"], row["arm"], row["repetition"]]
        for row in state_rows
        if row.get("state_semantic_pass") is not True
    ]
    history_rows = [row for row in state_rows if row.get("family") == "history-required-control"]
    history_failures = [
        [row["case_id"], row["arm"], row["repetition"]]
        for row in history_rows
        if row.get("history_pointer_pass") is not True
    ]
    return {
        "status": "PASS" if state_rows and not semantic_failures else "FAIL",
        "semantic_failures": semantic_failures,
        "history_pointer_status": "PASS" if history_rows and not history_failures else "FAIL",
        "history_pointer_failures": history_failures,
    }


def transport_report(rows: Sequence[dict[str, Any]]) -> dict[str, Any]:
    selected = [row for row in rows if row.get("arm") == "state-history-free"]
    failures: list[dict[str, Any]] = []
    request_count = 0
    max_bytes = 0
    proxy_environment_seen = False
    for row in selected:
        if row.get("client_request_contract_pass") is not True:
            failures.append({"cell": list(_cell_key(row)), "reason": "cell-contract"})
        for step in row.get("steps", []):
            for attempt in step.get("attempts", []):
                request_count += 1
                request = attempt.get("request_audit") or {}
                outbound = attempt.get("outbound_audit") or {}
                max_bytes = max(max_bytes, int(outbound.get("request_bytes") or 0))
                proxy_environment_seen = proxy_environment_seen or bool(outbound.get("proxy_environment_present"))
                conditions = {
                    "manifest_match": request.get("manifest_match") is True,
                    "bounded_context_eligible": request.get("bounded_context_eligible") is True,
                    "no_historical_input": request.get("historical_input_item_count") == 0,
                    "body_unchanged": outbound.get("body_bytes_sent_unchanged") is True,
                    "no_context_headers": not outbound.get("contextual_header_names"),
                    "no_request_cookie": outbound.get("request_cookie_present") is False,
                    "proxy_bypassed": outbound.get("environment_proxy_bypassed") is True,
                    "transport_audit": outbound.get("client_context_audit_pass") is True,
                }
                if not all(conditions.values()):
                    failures.append(
                        {
                            "cell": list(_cell_key(row)),
                            "step": step.get("step"),
                            "attempt": attempt.get("attempt"),
                            "conditions": conditions,
                        }
                    )
    return {
        "status": "PASS" if selected and request_count and not failures else "FAIL",
        "cells": len(selected),
        "requests": request_count,
        "failures": failures,
        "max_wire_request_bytes": max_bytes,
        "proxy_environment_seen": proxy_environment_seen,
        "claim_scope": (
            "captured client-visible body and headers; provider-internal context behavior is not established"
        ),
    }


def _percentile(sorted_values: Sequence[float], fraction: float) -> float:
    if not sorted_values:
        raise AnalysisError("cannot take percentile of an empty sample")
    index = min(len(sorted_values) - 1, max(0, math.ceil(fraction * len(sorted_values)) - 1))
    return sorted_values[index]


def bootstrap_median_ratio(values: Sequence[float], *, samples: int = BOOTSTRAP_SAMPLES) -> dict[str, float]:
    if not values:
        raise AnalysisError("paired ratio sample is empty")
    if any(not math.isfinite(value) or value < 0 for value in values):
        raise AnalysisError("paired ratios must be finite and non-negative")
    rng = random.Random(20260902)
    medians: list[float] = []
    for _ in range(samples):
        sample = [values[rng.randrange(len(values))] for _ in values]
        medians.append(statistics.median(sample))
    medians.sort()
    return {
        "median": statistics.median(values),
        "ci95_low": _percentile(medians, 0.025),
        "ci95_high": _percentile(medians, 0.975),
    }


def cost_report(
    rows: Sequence[dict[str, Any]],
    *,
    key: str,
    ratio_limit: float,
    workers: set[int],
    require_serial: bool,
) -> dict[str, Any]:
    pairs = _paired(rows, "state-history-free", "full-history")
    ratios: list[float] = []
    incomplete: list[list[Any]] = []
    for candidate, baseline in pairs:
        left = candidate.get(key)
        right = baseline.get(key)
        complete_key = f"{key}_complete"
        complete = True
        if key.endswith("tokens"):
            complete = candidate.get(complete_key) is True and baseline.get(complete_key) is True
        if not isinstance(left, (int, float)) or not isinstance(right, (int, float)) or right <= 0 or not complete:
            incomplete.append([candidate["case_id"], candidate["repetition"]])
            continue
        ratios.append(float(left) / float(right))
    serial_ok = not require_serial or workers == {1}
    if not ratios or incomplete or not serial_ok:
        return {
            "status": "PENDING" if not serial_ok or incomplete else "FAIL",
            "pairs": len(pairs),
            "usable_pairs": len(ratios),
            "incomplete_pairs": incomplete,
            "workers": sorted(workers),
            "require_serial": require_serial,
            "ratio_limit": ratio_limit,
        }
    interval = bootstrap_median_ratio(ratios)
    passed = interval["median"] <= ratio_limit and interval["ci95_high"] < 1.0
    return {
        "status": "PASS" if passed else "FAIL",
        "pairs": len(pairs),
        "usable_pairs": len(ratios),
        "incomplete_pairs": incomplete,
        "workers": sorted(workers),
        "require_serial": require_serial,
        "ratio_limit": ratio_limit,
        "ratios": ratios,
        **interval,
    }


def bounded_report(rows: Sequence[dict[str, Any]], transport: Mapping[str, Any]) -> dict[str, Any]:
    selected = [
        row
        for row in rows
        if row.get("profile") == "bounded" and row.get("arm") == "state-history-free"
    ]
    horizons = {int(row.get("horizon") or 0) for row in selected}
    missing_horizons = sorted(set(BOUNDED_HORIZONS) - horizons)
    invalid = [
        list(_cell_key(row))
        for row in selected
        if row.get("passed") is not True
        or row.get("client_request_contract_pass") is not True
        or int(row.get("max_history_item_count") or 0) != 0
    ]
    limits: list[int] = []
    maxima: dict[str, int] = {}
    for row in selected:
        maximum = int(row.get("max_wire_request_bytes") or 0)
        maxima[f"{row['case_id']}/r{row['repetition']}"] = maximum
        for step in row.get("steps", []):
            for attempt in step.get("attempts", []):
                request = attempt.get("request_audit") or {}
                limit = request.get("wire_request_limit_bytes")
                if isinstance(limit, int):
                    limits.append(limit)
    one_limit = len(set(limits)) <= 1 and bool(limits)
    within_limit = one_limit and all(value <= limits[0] for value in maxima.values())
    passed = (
        bool(selected)
        and not missing_horizons
        and not invalid
        and transport.get("status") == "PASS"
        and one_limit
        and within_limit
    )
    return {
        "status": "PASS" if passed else "FAIL",
        "observed_horizons": sorted(horizons),
        "required_horizons": list(BOUNDED_HORIZONS),
        "missing_horizons": missing_horizons,
        "invalid_cells": invalid,
        "fixed_wire_limit_bytes": limits[0] if one_limit else None,
        "one_frozen_limit": one_limit,
        "all_requests_within_limit": within_limit,
        "max_request_bytes_by_cell": maxima,
        "claim": (
            "single client-visible request size is bounded independently of completed step count; cumulative T-step input remains O(T)"
        ),
    }


def analyze(rows: Sequence[dict[str, Any]], manifests: Sequence[dict[str, Any]]) -> dict[str, Any]:
    matrix = matrix_report(rows, manifests)
    quality = quality_report(rows, matrix)
    state = state_report(rows)
    transport = transport_report(rows)
    workers = {int(row.get("workers")) for row in rows if type(row.get("workers")) is int}
    token = cost_report(
        rows,
        key="uncached_input_tokens",
        ratio_limit=TOKEN_RATIO_LIMIT,
        workers=workers,
        require_serial=False,
    )
    latency = cost_report(
        rows,
        key="end_to_end_seconds",
        ratio_limit=LATENCY_RATIO_LIMIT,
        workers=workers,
        require_serial=True,
    )
    bounded = bounded_report(rows, transport)
    release_quality = all(
        gate.get("status") == "PASS"
        for gate in (matrix, quality, state, transport)
    )
    return {
        "schema_version": VERSION,
        "matrix_gate": matrix,
        "quality_gate": quality,
        "state_semantic_gate": state,
        "client_request_contract_gate": transport,
        "token_gate": token,
        "latency_gate": latency,
        "bounded_context_gate": bounded,
        "release_quality_gate": "PASS" if release_quality else "FAIL",
        "efficiency_claim": (
            "SUPPORTED" if token.get("status") == "PASS" else "NOT_SUPPORTED"
        ),
        "latency_claim": (
            "SUPPORTED" if latency.get("status") == "PASS" else "NOT_SUPPORTED"
        ),
        "history_free_bound_claim": (
            "SUPPORTED_CLIENT_VISIBLE_ONLY"
            if bounded.get("status") == "PASS"
            else "NOT_SUPPORTED"
        ),
    }


def _markdown(report: Mapping[str, Any]) -> str:
    return f"""# Execution-state 四臂模型门禁报告

## Gate

| Gate | 状态 |
|---|---|
| Matrix | {report['matrix_gate']['status']} |
| Quality | {report['quality_gate']['status']} |
| State semantics | {report['state_semantic_gate']['status']} |
| Client request/transport | {report['client_request_contract_gate']['status']} |
| Token | {report['token_gate']['status']} |
| Latency | {report['latency_gate']['status']} |
| Bounded context | {report['bounded_context_gate']['status']} |
| Release quality | {report['release_quality_gate']} |

## 声明边界

- Token 收益：`{report['efficiency_claim']}`。
- 耗时收益：`{report['latency_claim']}`。
- History-free 单步客户端请求有界：`{report['history_free_bound_claim']}`。
- 即使有界门禁通过，也只证明捕获到的客户端请求体和请求头；不证明 provider 内部绝对没有隐藏上下文。
- 单步请求相对 horizon 有界不等于整个任务使用 O(1) token；T 步累计输入仍为 O(T)。
"""


def write_report(output: Path, report: Mapping[str, Any]) -> None:
    output.mkdir(parents=True, exist_ok=True)
    (output / "analysis.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    summary = {
        "release_quality_gate": report["release_quality_gate"],
        "token_gate": report["token_gate"]["status"],
        "latency_gate": report["latency_gate"]["status"],
        "bounded_context_gate": report["bounded_context_gate"]["status"],
        "efficiency_claim": report["efficiency_claim"],
        "latency_claim": report["latency_claim"],
        "history_free_bound_claim": report["history_free_bound_claim"],
    }
    (output / "release-summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (output / "REPORT_ZH.md").write_text(_markdown(report), encoding="utf-8")


def self_test() -> None:
    rows = [
        {
            "case_id": "case",
            "arm": "full-history",
            "repetition": 1,
            "passed": True,
            "workers": 1,
            "uncached_input_tokens": 100,
            "uncached_input_tokens_complete": True,
            "end_to_end_seconds": 10.0,
        }
    ]
    manifest = {
        "expected_cells": [
            {"case_id": "case", "arm": arm, "repetition": 1} for arm in ARMS
        ]
    }
    matrix = matrix_report(rows, [manifest])
    assert matrix["status"] == "FAIL"
    interval = bootstrap_median_ratio([0.5, 0.6, 0.7], samples=200)
    assert 0 <= interval["ci95_low"] <= interval["median"] <= interval["ci95_high"]
    print("skill-state model analysis self-test: PASS")


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("results", nargs="+", type=Path)
    parser.add_argument("--manifest", action="append", type=Path, default=[])
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    if argv is not None and "--self-test" in argv:
        self_test()
        return 0
    if argv is None and "--self-test" in sys.argv[1:]:
        self_test()
        return 0
    args = parse_args(argv)
    rows = load_results(args.results)
    manifests = load_manifests(args.manifest)
    report = analyze(rows, manifests)
    write_report(args.output.resolve(), report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["release_quality_gate"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

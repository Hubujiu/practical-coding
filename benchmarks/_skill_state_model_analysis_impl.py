#!/usr/bin/env python3
"""Analyze execution-state four-arm results with quality-first gates."""

from __future__ import annotations

import argparse
import json
import math
import random
import statistics
import tempfile
from pathlib import Path
from typing import Any, Mapping, Sequence

HERE = Path(__file__).resolve().parent
if str(HERE) not in __import__("sys").path:
    __import__("sys").path.insert(0, str(HERE))

from skill_state_model_cases import (  # noqa: E402
    ARM_FULL_HISTORY,
    ARM_STATE_HISTORY_FREE,
    ARM_STATE_SHADOW,
    STATE_ARMS,
)

VERSION = "1.0"
PASS, FAIL, PENDING = "PASS", "FAIL", "PENDING"


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read JSON {path}: {exc}") from exc


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise ValueError(f"cannot read results {path}: {exc}") from exc
    for number, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid JSONL at {path}:{number}: {exc}") from exc
        if not isinstance(row, dict):
            raise ValueError(f"result at {path}:{number} must be an object")
        rows.append(row)
    return rows


def validate_rows(rows: Sequence[Mapping[str, Any]]) -> None:
    required = {"profile", "case_id", "arm", "repetition", "verdict"}
    seen: set[tuple[str, str, str, int]] = set()
    for index, row in enumerate(rows):
        missing = required - set(row)
        if missing:
            raise ValueError(f"record {index} missing keys: {sorted(missing)}")
        key = (str(row["profile"]), str(row["case_id"]), str(row["arm"]), int(row["repetition"]))
        if key in seen:
            raise ValueError(f"duplicate result cell: {key}")
        seen.add(key)


def status(values: Sequence[bool | None]) -> str:
    if not values or any(value is None for value in values):
        return PENDING
    return FAIL if any(value is False for value in values) else PASS


def sum_known(rows: Sequence[Mapping[str, Any]], key: str) -> int | float | None:
    values = [row.get(key) for row in rows]
    if not values or any(not isinstance(value, (int, float)) or isinstance(value, bool) for value in values):
        return None
    return sum(values)


def arm_summary(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for arm in sorted({str(row["arm"]) for row in rows}):
        selected = [row for row in rows if row["arm"] == arm]
        determinate = [row for row in selected if row.get("passed") is not None]
        passed = sum(row.get("passed") is True for row in determinate)
        result[arm] = {
            "cells": len(selected),
            "determinate": len(determinate),
            "passed": passed,
            "pass_rate": passed / len(determinate) if determinate else None,
            "input_tokens_sum": sum_known(determinate, "input_tokens"),
            "cached_input_tokens_sum": sum_known(determinate, "cached_input_tokens"),
            "uncached_input_tokens_sum": sum_known(determinate, "uncached_input_tokens"),
            "output_tokens_sum": sum_known(determinate, "output_tokens"),
            "duration_seconds_sum": sum_known(determinate, "end_to_end_duration_seconds"),
            "rejected_transitions": sum(int(row.get("rejected_transition_count") or 0) for row in selected),
            "max_request_bytes": max((int(row.get("max_request_bytes") or 0) for row in selected), default=0),
        }
    return result


def quality_gate(rows: Sequence[Mapping[str, Any]], margin: float) -> dict[str, Any]:
    arms = arm_summary(rows)
    full, history_free = arms.get(ARM_FULL_HISTORY), arms.get(ARM_STATE_HISTORY_FREE)
    if full is None or history_free is None:
        return {"status": PENDING, "reason": "required arms are missing", "margin": margin}
    if full["determinate"] != full["cells"] or history_free["determinate"] != history_free["cells"]:
        return {"status": PENDING, "reason": "required arm contains indeterminate cells", "margin": margin}
    if full["pass_rate"] is None or history_free["pass_rate"] is None:
        return {"status": PENDING, "reason": "pass rate unavailable", "margin": margin}
    deltas = {ARM_STATE_HISTORY_FREE: history_free["pass_rate"] - full["pass_rate"]}
    shadow = arms.get(ARM_STATE_SHADOW)
    if shadow is not None:
        if shadow["determinate"] != shadow["cells"] or shadow["pass_rate"] is None:
            return {"status": PENDING, "reason": "state-shadow contains indeterminate cells", "margin": margin}
        deltas[ARM_STATE_SHADOW] = shadow["pass_rate"] - full["pass_rate"]
    failures = {arm: delta for arm, delta in deltas.items() if delta < -margin}
    return {
        "status": FAIL if failures else PASS,
        "margin": margin,
        "full_history_pass_rate": full["pass_rate"],
        "deltas": deltas,
        "failures": failures,
    }


def state_gate(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    selected = [row for row in rows if row["arm"] in STATE_ARMS]
    values, failures = [], []
    for row in selected:
        score = row.get("state_score")
        value = score.get("state_pass") if isinstance(score, Mapping) else None
        values.append(value if isinstance(value, bool) else None)
        if value is False:
            failures.append({"case_id": row["case_id"], "arm": row["arm"], "repetition": row["repetition"]})
    return {"status": status(values), "cells": len(selected), "failures": failures}


def artifact_gate(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    selected = [
        row for row in rows
        if row["arm"] in STATE_ARMS
        and isinstance(row.get("artifact_score"), Mapping)
        and row["artifact_score"].get("required") is True
    ]
    values = [row["artifact_score"].get("artifact_pass") for row in selected]
    return {
        "status": status([value if isinstance(value, bool) else None for value in values]),
        "cells": len(selected),
        "failures": [
            {"case_id": row["case_id"], "arm": row["arm"], "repetition": row["repetition"]}
            for row in selected if row["artifact_score"].get("artifact_pass") is not True
        ],
    }


def transport_gate(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    selected = [row for row in rows if row["arm"] == ARM_STATE_HISTORY_FREE]
    values = [row.get("history_free_transport_gate") for row in selected]
    return {
        "status": status([value if isinstance(value, bool) else None for value in values]),
        "cells": len(selected),
        "failures": [
            {"profile": row["profile"], "case_id": row["case_id"], "repetition": row["repetition"], "value": row.get("history_free_transport_gate")}
            for row in selected if row.get("history_free_transport_gate") is not True
        ],
    }


def pairs(rows: Sequence[Mapping[str, Any]], left: str, right: str, profile: str | None) -> list[tuple[Mapping[str, Any], Mapping[str, Any]]]:
    indexed = {
        (str(row["profile"]), str(row["case_id"]), int(row["repetition"]), str(row["arm"])): row
        for row in rows if profile is None or row["profile"] == profile
    }
    result = []
    for profile_name, case_id, repetition in sorted({key[:3] for key in indexed}):
        a = indexed.get((profile_name, case_id, repetition, left))
        b = indexed.get((profile_name, case_id, repetition, right))
        if a is not None and b is not None:
            result.append((a, b))
    return result


def bootstrap_ci(values: Sequence[float], samples: int) -> tuple[float, float] | None:
    if len(values) < 2 or samples < 1:
        return None
    rng, medians = random.Random(20260902), []
    for _ in range(samples):
        medians.append(statistics.median(values[rng.randrange(len(values))] for _ in values))
    medians.sort()
    return (
        medians[math.floor(0.025 * (len(medians) - 1))],
        medians[math.ceil(0.975 * (len(medians) - 1))],
    )


def cost_gate(
    rows: Sequence[Mapping[str, Any]], *, metric: str, threshold: float,
    quality: str, samples: int, single_worker: bool,
) -> dict[str, Any]:
    if quality != PASS:
        return {"status": PENDING, "reason": "quality gate is not PASS", "metric": metric, "threshold": threshold}
    profile = "standard" if any(row["profile"] == "standard" for row in rows) else None
    compared, ratios = [], []
    for history_free, full in pairs(rows, ARM_STATE_HISTORY_FREE, ARM_FULL_HISTORY, profile):
        if single_worker and (history_free.get("workers") != 1 or full.get("workers") != 1):
            continue
        left, right = history_free.get(metric), full.get(metric)
        if not isinstance(left, (int, float)) or isinstance(left, bool):
            continue
        if not isinstance(right, (int, float)) or isinstance(right, bool) or right <= 0:
            continue
        ratio = float(left) / float(right)
        ratios.append(ratio)
        compared.append({"case_id": history_free["case_id"], "repetition": history_free["repetition"], "history_free": left, "full_history": right, "ratio": ratio})
    interval = bootstrap_ci(ratios, samples)
    if interval is None:
        return {"status": PENDING, "reason": "fewer than two comparable paired cells", "metric": metric, "threshold": threshold, "pairs": compared}
    median = statistics.median(ratios)
    return {
        "status": PASS if median <= threshold and interval[1] < 1.0 else FAIL,
        "metric": metric,
        "threshold": threshold,
        "pair_count": len(ratios),
        "median_ratio": median,
        "bootstrap_95_ci": list(interval),
        "pairs": compared,
    }


def bounded_gate(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    selected = [row for row in rows if row["profile"] == "bounded" and row["arm"] == ARM_STATE_HISTORY_FREE]
    if not selected:
        return {"status": PENDING, "reason": "bounded history-free results are missing"}
    expected, observed = {10, 25, 50, 100}, {int(row.get("horizon") or 0) for row in selected}
    by_horizon, failures = {}, []
    for horizon in sorted(observed):
        group = [row for row in selected if int(row.get("horizon") or 0) == horizon]
        transport_pass = all(row.get("history_free_transport_gate") is True for row in group)
        by_horizon[horizon] = {"cells": len(group), "max_request_bytes": max(int(row.get("max_request_bytes") or 0) for row in group), "transport_pass": transport_pass}
        if not transport_pass:
            failures.append({"horizon": horizon, "reason": "final outbound audit failed"})
        for row in group:
            for attempt in row.get("attempts") or []:
                host = (attempt.get("transport_audit") or {}).get("host_body_audit") or {}
                if host.get("historical_input_item_count") not in (0, None):
                    failures.append({"horizon": horizon, "case_id": row["case_id"], "reason": "historical input detected"})
                limit, size = host.get("wire_request_limit_bytes"), attempt.get("request_bytes")
                if isinstance(limit, int) and isinstance(size, int) and size > limit:
                    failures.append({"horizon": horizon, "case_id": row["case_id"], "reason": "request exceeded fixed bound"})
    missing = expected - observed
    if missing:
        return {"status": PENDING, "reason": f"missing horizons: {sorted(missing)}", "by_horizon": by_horizon, "failures": failures}
    return {
        "status": FAIL if failures else PASS,
        "claim": "single client-visible request is bounded; cumulative T-step input remains O(T)",
        "by_horizon": by_horizon,
        "failures": failures,
    }


def analyze(
    rows: Sequence[Mapping[str, Any]], *, manifests: Sequence[Mapping[str, Any]] = (),
    margin: float = 0.03, token_threshold: float = 0.80,
    latency_threshold: float = 0.90, samples: int = 5000,
) -> dict[str, Any]:
    validate_rows(rows)
    quality = quality_gate(rows, margin)
    state = state_gate(rows)
    artifact = artifact_gate(rows)
    transport = transport_gate(rows)
    token = cost_gate(rows, metric="uncached_input_tokens", threshold=token_threshold, quality=quality["status"], samples=samples, single_worker=False)
    latency = cost_gate(rows, metric="end_to_end_duration_seconds", threshold=latency_threshold, quality=quality["status"], samples=samples, single_worker=True)
    bounded = bounded_gate(rows)
    required = [quality["status"], state["status"], artifact["status"], transport["status"]]
    overall = FAIL if FAIL in required else (PASS if all(value == PASS for value in required) else PENDING)
    return {
        "schema_version": VERSION,
        "record_count": len(rows),
        "profiles": sorted({str(row["profile"]) for row in rows}),
        "cases": sorted({str(row["case_id"]) for row in rows}),
        "arms": arm_summary(rows),
        "manifests": [{key: manifest.get(key) for key in ("manifest_sha256", "candidate_commit", "profile", "runs", "workers", "model", "reasoning")} for manifest in manifests],
        "gates": {
            "quality_gate": quality,
            "state_semantic_gate": state,
            "history_pointer_gate": artifact,
            "client_transport_gate": transport,
            "token_gate": token,
            "latency_gate": latency,
            "bounded_context_gate": bounded,
            "execution_state_model_gate": overall,
        },
        "claim_boundary": {
            "history_free": "client-visible request only; provider-internal context is not established",
            "complexity": "per-step request may be horizon-independent; cumulative T-step input is O(T)",
            "cost": "token and latency require independent paired gates after quality passes",
        },
    }


def release_summary(analysis: Mapping[str, Any]) -> dict[str, Any]:
    gates = analysis["gates"]
    return {
        "schema_version": VERSION,
        "status": gates["execution_state_model_gate"],
        "profiles": analysis["profiles"],
        "record_count": analysis["record_count"],
        **{name: gates[name]["status"] for name in (
            "quality_gate", "state_semantic_gate", "history_pointer_gate",
            "client_transport_gate", "token_gate", "latency_gate", "bounded_context_gate",
        )},
        "claim_boundary": analysis["claim_boundary"],
    }


def markdown(analysis: Mapping[str, Any]) -> str:
    gates = analysis["gates"]
    lines = [
        "# Execution-state 四臂模型门禁报告", "", "## 总结", "",
        f"- 记录数：{analysis['record_count']}",
        f"- Case 数：{len(analysis['cases'])}",
        f"- execution_state_model_gate：**{gates['execution_state_model_gate']}**", "",
        "## Arm 结果", "",
        "| Arm | cells | determinate | passed | pass rate | uncached tokens | duration |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for arm, row in analysis["arms"].items():
        rate = "—" if row["pass_rate"] is None else f"{row['pass_rate']:.3f}"
        tokens = "—" if row["uncached_input_tokens_sum"] is None else str(row["uncached_input_tokens_sum"])
        duration = "—" if row["duration_seconds_sum"] is None else f"{row['duration_seconds_sum']:.2f}s"
        lines.append(f"| {arm} | {row['cells']} | {row['determinate']} | {row['passed']} | {rate} | {tokens} | {duration} |")
    lines += ["", "## Gates", "", "| Gate | Status |", "|---|---|"]
    for name in ("quality_gate", "state_semantic_gate", "history_pointer_gate", "client_transport_gate", "token_gate", "latency_gate", "bounded_context_gate"):
        lines.append(f"| {name} | {gates[name]['status']} |")
    lines += [
        "", "## 解释边界", "",
        "History-free 通过时，只证明捕获到的客户端请求未携带旧消息或会话句柄，并处于冻结 manifest 的固定上限内；不证明 provider 内部没有隐藏上下文。单步请求可相对 horizon 有界，但 T 步累计输入仍为 O(T)。Token 与耗时收益必须在质量通过后分别满足配对门禁。", "",
    ]
    return "\n".join(lines)


def write_outputs(output: Path, analysis: Mapping[str, Any]) -> None:
    output.mkdir(parents=True, exist_ok=True)
    (output / "analysis.json").write_text(json.dumps(analysis, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    (output / "release-summary.json").write_text(json.dumps(release_summary(analysis), ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    (output / "REPORT_ZH.md").write_text(markdown(analysis), encoding="utf-8")


def synthetic_rows() -> list[dict[str, Any]]:
    rows = []
    for case_id in ("a", "b"):
        for arm, tokens, duration in ((ARM_FULL_HISTORY, 1000, 10.0), (ARM_STATE_SHADOW, 1000, 10.0), (ARM_STATE_HISTORY_FREE, 600, 7.0), ("no-skill-full-history", 1100, 11.0)):
            rows.append({"profile": "standard", "case_id": case_id, "arm": arm, "repetition": 1, "verdict": "pass", "passed": True, "workers": 1, "horizon": 8, "uncached_input_tokens": tokens, "end_to_end_duration_seconds": duration, "history_free_transport_gate": True if arm == ARM_STATE_HISTORY_FREE else None, "state_score": {"state_pass": True if arm in STATE_ARMS else None}, "artifact_score": {"required": case_id == "b" and arm in STATE_ARMS, "artifact_pass": True if case_id == "b" and arm in STATE_ARMS else None}, "attempts": []})
    for horizon in (10, 25, 50, 100):
        rows.append({"profile": "bounded", "case_id": f"h{horizon}", "arm": ARM_STATE_HISTORY_FREE, "repetition": 1, "verdict": "pass", "passed": True, "workers": 1, "horizon": horizon, "uncached_input_tokens": horizon * 100, "end_to_end_duration_seconds": float(horizon), "history_free_transport_gate": True, "state_score": {"state_pass": True}, "artifact_score": {"required": False, "artifact_pass": None}, "attempts": []})
    return rows


def self_test() -> None:
    result = analyze(synthetic_rows(), samples=200)
    assert result["gates"]["quality_gate"]["status"] == PASS
    assert result["gates"]["token_gate"]["status"] == PASS
    assert result["gates"]["latency_gate"]["status"] == PASS
    assert result["gates"]["bounded_context_gate"]["status"] == PASS
    with tempfile.TemporaryDirectory() as directory:
        write_outputs(Path(directory), result)
    print("skill-state model analysis self-test: PASS")


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description=__doc__)
    value.add_argument("results", nargs="*", type=Path)
    value.add_argument("--manifest", action="append", type=Path, default=[])
    value.add_argument("--output", type=Path)
    value.add_argument("--quality-margin", type=float, default=0.03)
    value.add_argument("--token-ratio-threshold", type=float, default=0.80)
    value.add_argument("--latency-ratio-threshold", type=float, default=0.90)
    value.add_argument("--bootstrap-samples", type=int, default=5000)
    value.add_argument("--self-test", action="store_true")
    return value


def main(argv: Sequence[str] | None = None) -> int:
    args = parser().parse_args(argv)
    if args.self_test:
        self_test()
        return 0
    if not args.results:
        raise SystemExit("at least one results.jsonl path is required")
    rows = [row for path in args.results for row in read_jsonl(path.resolve())]
    manifests = [read_json(path.resolve()) for path in args.manifest]
    result = analyze(rows, manifests=manifests, margin=args.quality_margin, token_threshold=args.token_ratio_threshold, latency_threshold=args.latency_ratio_threshold, samples=args.bootstrap_samples)
    output = (args.output or Path("benchmark-results") / "skill-state-final").resolve()
    write_outputs(output, result)
    print(json.dumps(release_summary(result), ensure_ascii=False, indent=2))
    return 1 if result["gates"]["execution_state_model_gate"] == FAIL else 0


if __name__ == "__main__":
    raise SystemExit(main())

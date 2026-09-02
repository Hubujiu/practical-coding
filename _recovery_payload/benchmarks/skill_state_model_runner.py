#!/usr/bin/env python3
"""Run the execution-state four-arm model comparison.

This runner is intentionally separate from the router-tree runner. It replays one
frozen observation stream under full-history, state-shadow, true history-free,
and no-skill controls. It captures every client request/response and outbound
transport audit. It never executes a model-proposed shell command or tool call.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import copy
import datetime as dt
import hashlib
import json
import os
import subprocess
import sys
import threading
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from skill_state_model_cases import (  # noqa: E402
    BOUNDED_HORIZONS,
    PROFILES,
    StateModelCase,
    cases_for_profile,
    replace_artifact_placeholders,
    self_test as cases_self_test,
)
from runtime._skill_state_host_response_extract import _extract_output_text  # noqa: E402
from runtime._skill_state_host_response_usage import _usage_summary  # noqa: E402
from runtime.skill_state import (  # noqa: E402
    StateValidationError,
    apply_state_patch,
    apply_transition,
    initial_state,
    validate_state,
)
from runtime.skill_state_host import HistoryFreeHost, HostBoundaryError  # noqa: E402
from runtime.skill_state_http_transport import (  # noqa: E402
    ExactByteHTTPTransport,
    TransportAuditError,
    api_key_from_environment,
)


VERSION = "1.0"
ARMS = (
    "full-history",
    "state-shadow",
    "state-history-free",
    "no-skill-full-history",
)
STATE_ARMS = frozenset({"state-shadow", "state-history-free"})
FULL_HISTORY_ARMS = frozenset({"full-history", "state-shadow", "no-skill-full-history"})
DEFAULT_MODEL = "gpt-5.6-luna"
DEFAULT_REASONING = "medium"
DEFAULT_ENDPOINT = "https://api.openai.com/v1/responses"
MAX_TRANSITION_ATTEMPTS = 2
MAX_OUTPUT_TOKENS = 4096

_ACTION_KEYS = {
    "continue": frozenset({"tool"}),
    "finish": frozenset({"tool", "answer"}),
}
_WRITE_LOCK = threading.Lock()


class ModelRunnerError(RuntimeError):
    """Raised for deterministic runner or model-contract failures."""


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _strict_json(value: str, label: str) -> Any:
    def unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, item in pairs:
            if key in result:
                raise ModelRunnerError(f"{label} contains duplicate key {key!r}")
            result[key] = item
        return result

    def nonfinite(token: str) -> None:
        raise ModelRunnerError(f"{label} contains non-finite number {token}")

    try:
        return json.loads(value, object_pairs_hook=unique, parse_constant=nonfinite)
    except ModelRunnerError:
        raise
    except (json.JSONDecodeError, RecursionError, ValueError) as exc:
        raise ModelRunnerError(f"{label} is not valid JSON: {exc}") from exc


def parse_action(value: str | Mapping[str, Any], *, final_step: bool) -> dict[str, str]:
    decoded = _strict_json(value, "action") if isinstance(value, str) else copy.deepcopy(dict(value))
    if not isinstance(decoded, dict):
        raise ModelRunnerError("action must be a JSON object")
    tool = decoded.get("tool")
    if tool not in _ACTION_KEYS:
        raise ModelRunnerError("action.tool must be continue or finish")
    expected = _ACTION_KEYS[tool]
    if set(decoded) != set(expected):
        raise ModelRunnerError(
            f"action keys mismatch for {tool}; expected={sorted(expected)}, got={sorted(decoded)}"
        )
    if final_step and tool != "finish":
        raise ModelRunnerError("the final observation requires a finish action")
    if not final_step and tool != "continue":
        raise ModelRunnerError("finish is allowed only after the final observation")
    result = {"tool": str(tool)}
    if tool == "finish":
        answer = decoded.get("answer")
        if not isinstance(answer, str) or not answer.strip():
            raise ModelRunnerError("finish.answer must be a non-empty string")
        result["answer"] = answer
    return result


def _flatten(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _contains_groups(text: str, groups: Iterable[Iterable[str]]) -> tuple[bool, list[list[str]]]:
    lower = text.lower()
    missing = [list(group) for group in groups if not any(term.lower() in lower for term in group)]
    return not missing, missing


def _excludes_groups(text: str, groups: Iterable[Iterable[str]]) -> tuple[bool, list[list[str]]]:
    lower = text.lower()
    present = [list(group) for group in groups if any(term.lower() in lower for term in group)]
    return not present, present


def _procedure(*, include_skill: bool, state_mode: bool) -> str:
    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8") if include_skill else ""
    action_contract = (
        "For each observation, return exactly one state transition. Encode the action value as a compact JSON "
        "string: {\"tool\":\"continue\"} before the final step, or "
        "{\"tool\":\"finish\",\"answer\":\"...\"} at the final step."
        if state_mode
        else
        "Return exactly one compact JSON object and no Markdown: {\"tool\":\"continue\"} before the final "
        "step, or {\"tool\":\"finish\",\"answer\":\"...\"} at the final step."
    )
    common = (
        "\n\nExecution-state benchmark procedure:\n"
        "Process exactly the latest numbered observation. Do not invent repository facts, run commands, call "
        "tools, or finish early. Preserve current facts needed by later observations; replace facts explicitly "
        "superseded by corrective evidence. Distractor telemetry is not task state. On the final step, answer only "
        "from the evidence supplied by the observation stream. "
        + action_contract
    )
    return (skill + common).strip()


def _generic_instructions(*, include_skill: bool) -> str:
    return _procedure(include_skill=include_skill, state_mode=False)


def _response_payload(response_body: bytes) -> tuple[dict[str, Any], str, dict[str, int | None]]:
    try:
        decoded = json.loads(response_body)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ModelRunnerError(f"model response is not UTF-8 JSON: {exc}") from exc
    if not isinstance(decoded, dict):
        raise ModelRunnerError("model response must be a JSON object")
    try:
        text = _extract_output_text(decoded)
    except HostBoundaryError as exc:
        raise ModelRunnerError(str(exc)) from exc
    return decoded, text, dict(_usage_summary(decoded))


def _generic_body(
    *,
    model: str,
    reasoning: str,
    instructions: str,
    history: Sequence[Mapping[str, Any]],
    observation: str,
    validation_error: str | None,
) -> bytes:
    current = observation
    if validation_error:
        current += (
            "\n\nThe previous response was rejected by the deterministic runner: "
            + validation_error
            + " Return one corrected action for this same observation."
        )
    input_items = [copy.deepcopy(dict(item)) for item in history]
    input_items.append({"role": "user", "content": current})
    body = {
        "model": model,
        "instructions": instructions,
        "input": input_items,
        "store": False,
        "stream": False,
        "background": False,
        "truncation": "disabled",
        "reasoning": {"effort": reasoning},
        "max_output_tokens": MAX_OUTPUT_TOKENS,
    }
    return _canonical_json_bytes(body)


def _new_state(case: StateModelCase) -> dict[str, Any]:
    state = initial_state(
        f"Complete frozen long-horizon case {case.case_id}",
        ["Final answer is supported by the complete frozen observation stream"],
    )
    if case.history_required:
        state = apply_state_patch(
            state,
            {"history": {"required": True}},
        )
    return state


def _make_artifact(case: StateModelCase, cell: Path) -> StateModelCase:
    if not case.history_required:
        return case
    artifact = cell / "artifacts" / "release-audit.txt"
    artifact.parent.mkdir(parents=True, exist_ok=True)
    artifact.write_text(
        "immutable release audit\naccepted decision: preserve bounded provenance pointer\n",
        encoding="utf-8",
    )
    digest = _sha256_file(artifact)
    pointer = f"{artifact.as_posix()}#sha256={digest}"
    return replace_artifact_placeholders(case, pointer, digest)


def _persist_attempt_artifacts(
    cell: Path,
    step: int,
    attempt: int,
    request_body: bytes,
    response_body: bytes,
    request_audit: Mapping[str, Any],
    outbound_audit: Mapping[str, Any],
) -> None:
    target = cell / "transitions" / f"step-{step:03d}" / f"attempt-{attempt:02d}"
    target.mkdir(parents=True, exist_ok=True)
    (target / "request.json").write_bytes(request_body)
    (target / "response.json").write_bytes(response_body)
    (target / "request-audit.json").write_text(
        json.dumps(dict(request_audit), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (target / "outbound-audit.json").write_text(
        json.dumps(dict(outbound_audit), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _one_request(
    transport: ExactByteHTTPTransport,
    body: bytes,
) -> tuple[bytes, dict[str, Any]]:
    before = len(transport.audits)
    response = transport(body)
    if len(transport.audits) != before + 1:
        raise ModelRunnerError("transport did not produce exactly one outbound audit")
    return response.body, dict(transport.audits[-1])


def _run_cell(
    case: StateModelCase,
    arm: str,
    repetition: int,
    args: argparse.Namespace,
    output: Path,
    api_key: str,
) -> dict[str, Any]:
    cell = output / "cells" / case.case_id / arm / f"r{repetition:03d}"
    cell.mkdir(parents=True, exist_ok=False)
    case = _make_artifact(case, cell)
    (cell / "case.json").write_text(
        json.dumps(asdict(case), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    include_skill = arm != "no-skill-full-history"
    state_mode = arm in STATE_ARMS
    procedure = _procedure(include_skill=include_skill, state_mode=state_mode)
    host = (
        HistoryFreeHost(
            model=args.model,
            procedure=procedure,
            options={
                "reasoning": {"effort": args.reasoning},
                "max_output_tokens": args.max_output_tokens,
            },
        )
        if state_mode
        else None
    )
    if host is not None:
        (cell / "host-manifest.json").write_text(
            json.dumps(host.manifest(), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    transport = ExactByteHTTPTransport(
        endpoint=args.endpoint,
        api_key=api_key,
        timeout=args.timeout,
    )
    state = _new_state(case) if state_mode else None
    history: list[dict[str, Any]] = []
    steps: list[dict[str, Any]] = []
    final_answer = ""
    started = time.monotonic()

    try:
        for step_number, observation in enumerate(case.observations, 1):
            final_step = step_number == case.horizon
            feedback: str | None = None
            accepted = False
            step_attempts: list[dict[str, Any]] = []
            for attempt in range(1, args.max_attempts + 1):
                if state_mode:
                    assert host is not None and state is not None
                    prepared = host.prepare_request(
                        state,
                        observation,
                        validation_error=feedback,
                        step_id=f"{case.case_id}/{arm}/r{repetition}/s{step_number}",
                        attempt=attempt,
                    )
                    request_body = prepared.wire_bytes
                    request_audit = dict(prepared.audit)
                    if arm == "state-shadow":
                        body = prepared.body()
                        body["input"] = copy.deepcopy(history) + list(body["input"])
                        request_body = _canonical_json_bytes(body)
                        request_audit = {
                            "mode": "state-shadow",
                            "manifest_sha256": host.manifest()["manifest_sha256"],
                            "history_item_count": len(history),
                            "bounded_context_eligible": False,
                            "request_sha256": _sha256_bytes(request_body),
                            "wire_request_bytes": len(request_body),
                        }
                else:
                    request_body = _generic_body(
                        model=args.model,
                        reasoning=args.reasoning,
                        instructions=_generic_instructions(include_skill=include_skill),
                        history=history,
                        observation=observation,
                        validation_error=feedback,
                    )
                    request_audit = {
                        "mode": arm,
                        "history_item_count": len(history),
                        "bounded_context_eligible": False,
                        "request_sha256": _sha256_bytes(request_body),
                        "wire_request_bytes": len(request_body),
                    }

                response_body, outbound = _one_request(transport, request_body)
                attempt_record: dict[str, Any] = {
                    "attempt": attempt,
                    "request_audit": request_audit,
                    "outbound_audit": outbound,
                    "response_sha256": _sha256_bytes(response_body),
                    "response_bytes": len(response_body),
                }
                try:
                    _, output_text, usage = _response_payload(response_body)
                    attempt_record.update(usage)
                    if state_mode:
                        assert state is not None
                        successor, action_text = apply_transition(state, output_text)
                        action = parse_action(action_text, final_step=final_step)
                    else:
                        successor = None
                        action = parse_action(output_text, final_step=final_step)
                except (ModelRunnerError, StateValidationError, HostBoundaryError) as exc:
                    feedback = str(exc)[:1500]
                    attempt_record.update(
                        {"status": "rejected", "validation_error": feedback}
                    )
                    step_attempts.append(attempt_record)
                    _persist_attempt_artifacts(
                        cell,
                        step_number,
                        attempt,
                        request_body,
                        response_body,
                        request_audit,
                        outbound,
                    )
                    continue

                if state_mode:
                    assert successor is not None
                    validate_state(successor)
                    state = copy.deepcopy(successor)
                if arm in FULL_HISTORY_ARMS:
                    history.append({"role": "user", "content": observation})
                    history.append({"role": "assistant", "content": output_text})
                if action["tool"] == "finish":
                    final_answer = action["answer"]
                attempt_record.update(
                    {
                        "status": "accepted",
                        "validation_error": None,
                        "action": action,
                        "state_sha256": None
                        if state is None
                        else _sha256_bytes(_canonical_json_bytes(state)),
                    }
                )
                step_attempts.append(attempt_record)
                _persist_attempt_artifacts(
                    cell,
                    step_number,
                    attempt,
                    request_body,
                    response_body,
                    request_audit,
                    outbound,
                )
                accepted = True
                break
            steps.append(
                {
                    "step": step_number,
                    "final_step": final_step,
                    "observation_sha256": _sha256_bytes(observation.encode("utf-8")),
                    "attempts": step_attempts,
                    "accepted": accepted,
                }
            )
            if not accepted:
                raise ModelRunnerError(
                    f"step {step_number} exhausted {args.max_attempts} attempts"
                )

        answer_ok, missing = _contains_groups(final_answer, case.required_groups)
        answer_clean, forbidden = _excludes_groups(final_answer, case.forbidden_groups)
        state_ok: bool | None = None
        state_missing: list[list[str]] = []
        state_forbidden: list[list[str]] = []
        history_pointer_ok: bool | None = None
        if state is not None:
            state_text = _flatten(state)
            required_ok, state_missing = _contains_groups(state_text, case.state_required_groups)
            forbidden_ok, state_forbidden = _excludes_groups(state_text, case.state_forbidden_groups)
            state_ok = required_ok and forbidden_ok
            if case.history_required:
                history_pointer_ok = bool(
                    state.get("history", {}).get("required") is True
                    and state.get("history", {}).get("artifacts")
                )
                state_ok = state_ok and history_pointer_ok

        client_audit_ok = all(
            attempt["outbound_audit"].get("client_context_audit_pass") is True
            and attempt["outbound_audit"].get("body_bytes_sent_unchanged") is True
            for step in steps
            for attempt in step["attempts"]
        )
        if arm == "state-history-free":
            client_audit_ok = client_audit_ok and all(
                attempt["request_audit"].get("bounded_context_eligible") is True
                and attempt["request_audit"].get("manifest_match") is True
                and attempt["request_audit"].get("historical_input_item_count") == 0
                for step in steps
                for attempt in step["attempts"]
            )

        passed = answer_ok and answer_clean and client_audit_ok
        if state_ok is not None:
            passed = passed and state_ok
        result = {
            "schema_version": VERSION,
            "profile": args.profile,
            "case_id": case.case_id,
            "family": case.family,
            "horizon": case.horizon,
            "arm": arm,
            "repetition": repetition,
            "model": args.model,
            "reasoning": args.reasoning,
            "workers": args.workers,
            "passed": passed,
            "verdict": "pass" if passed else "fail",
            "infrastructure_error": None,
            "final_answer": final_answer,
            "missing_answer_groups": missing,
            "forbidden_answer_groups": forbidden,
            "final_state": state,
            "state_semantic_pass": state_ok,
            "missing_state_groups": state_missing,
            "forbidden_state_groups": state_forbidden,
            "history_pointer_pass": history_pointer_ok,
            "client_request_contract_pass": client_audit_ok,
            "steps": steps,
            "end_to_end_seconds": time.monotonic() - started,
        }
    except Exception as exc:
        result = {
            "schema_version": VERSION,
            "profile": args.profile,
            "case_id": case.case_id,
            "family": case.family,
            "horizon": case.horizon,
            "arm": arm,
            "repetition": repetition,
            "model": args.model,
            "reasoning": args.reasoning,
            "workers": args.workers,
            "passed": None,
            "verdict": "indeterminate",
            "infrastructure_error": f"{type(exc).__name__}: {exc}",
            "final_answer": final_answer,
            "final_state": state,
            "steps": steps,
            "end_to_end_seconds": time.monotonic() - started,
        }

    # Cost includes rejected attempts.
    attempts = [attempt for step in result.get("steps", []) for attempt in step.get("attempts", [])]
    for key in (
        "input_tokens",
        "cached_input_tokens",
        "uncached_input_tokens",
        "output_tokens",
        "total_tokens",
    ):
        values = [attempt.get(key) for attempt in attempts]
        result[key] = sum(value for value in values if isinstance(value, int))
        result[f"{key}_complete"] = bool(values) and all(isinstance(value, int) for value in values)
    result["request_count"] = len(attempts)
    result["rejected_transition_count"] = sum(
        attempt.get("status") == "rejected" for attempt in attempts
    )
    result["max_wire_request_bytes"] = max(
        (int(attempt["outbound_audit"].get("request_bytes") or 0) for attempt in attempts),
        default=0,
    )
    result["max_history_item_count"] = max(
        (int(attempt["request_audit"].get("history_item_count") or 0) for attempt in attempts),
        default=0,
    )
    (cell / "result.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return result


def _rotated_arms(case_index: int, repetition: int, selected: Sequence[str]) -> tuple[str, ...]:
    base = tuple(arm for arm in ARMS if arm in selected)
    if not base:
        return ()
    offset = (case_index + repetition - 1) % len(base)
    return base[offset:] + base[:offset]


def build_specs(
    cases: Sequence[StateModelCase],
    runs: int,
    selected_arms: Sequence[str],
) -> list[tuple[StateModelCase, str, int]]:
    specs: list[tuple[StateModelCase, str, int]] = []
    for case_index, case in enumerate(cases):
        for repetition in range(1, runs + 1):
            for arm in _rotated_arms(case_index, repetition, selected_arms):
                specs.append((case, arm, repetition))
    return specs


def _git_head() -> str | None:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    return result.stdout.strip() if result.returncode == 0 else None


def _manifest(args: argparse.Namespace, cases: Sequence[StateModelCase], specs: Sequence[tuple[StateModelCase, str, int]]) -> dict[str, Any]:
    return {
        "schema_version": VERSION,
        "runner": "skill-state-four-arm",
        "candidate_commit": _git_head(),
        "profile": args.profile,
        "model": args.model,
        "reasoning": args.reasoning,
        "endpoint": args.endpoint,
        "runs": args.runs,
        "workers": args.workers,
        "max_attempts": args.max_attempts,
        "arms": list(args.arm),
        "arm_order": "deterministic-rotation-by-case-and-repetition",
        "cases": [
            {
                "case_id": case.case_id,
                "family": case.family,
                "horizon": case.horizon,
                "history_required": case.history_required,
                "observation_stream_sha256": _sha256_bytes(
                    _canonical_json_bytes(case.observations)
                ),
            }
            for case in cases
        ],
        "expected_cells": [
            {"case_id": case.case_id, "arm": arm, "repetition": repetition}
            for case, arm, repetition in specs
        ],
        "source_sha256": {
            "cases": _sha256_file(HERE / "skill_state_model_cases.py"),
            "runner": _sha256_file(Path(__file__)),
            "transport": _sha256_file(ROOT / "runtime" / "skill_state_http_transport.py"),
            "skill": _sha256_file(ROOT / "SKILL.md"),
        },
        "started_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "bounded_horizons": list(BOUNDED_HORIZONS),
        "claim_boundary": (
            "client-visible request and transport evidence only; provider-internal context is not established"
        ),
    }


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def run(args: argparse.Namespace) -> int:
    if args.runs < 1 or args.workers < 1:
        raise SystemExit("runs and workers must be positive")
    if args.max_attempts not in {1, 2, 3}:
        raise SystemExit("max-attempts must be between 1 and 3")
    unknown_arms = set(args.arm) - set(ARMS)
    if unknown_arms:
        raise SystemExit(f"unknown arms: {', '.join(sorted(unknown_arms))}")
    cases = cases_for_profile(args.profile, args.case)
    specs = build_specs(cases, args.runs, args.arm)
    if not specs:
        raise SystemExit("selection produced no cells")

    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    manifest = _manifest(args, cases, specs)
    _write_json(output / "manifest.json", manifest)
    if args.dry_run:
        print(f"prepared {len(specs)} cells; no model requests were sent")
        return 0

    api_key = api_key_from_environment(args.api_key_env)
    results: list[dict[str, Any]] = []
    if args.workers == 1:
        for case, arm, repetition in specs:
            results.append(_run_cell(case, arm, repetition, args, output, api_key))
    else:
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
            futures = [
                pool.submit(_run_cell, case, arm, repetition, args, output, api_key)
                for case, arm, repetition in specs
            ]
            for future in concurrent.futures.as_completed(futures):
                results.append(future.result())
    results.sort(key=lambda row: (row["case_id"], row["repetition"], ARMS.index(row["arm"])))
    (output / "results.jsonl").write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in results),
        encoding="utf-8",
    )
    summary = {
        "cells": len(results),
        "determinate": sum(row.get("passed") is not None for row in results),
        "passed": sum(row.get("passed") is True for row in results),
        "failed": sum(row.get("passed") is False for row in results),
        "indeterminate": sum(row.get("passed") is None for row in results),
    }
    _write_json(output / "run-summary.json", summary)
    print(json.dumps(summary, indent=2))
    return 0 if summary["indeterminate"] == 0 else 2


def self_test() -> None:
    cases_self_test()
    assert parse_action('{"tool":"continue"}', final_step=False) == {"tool": "continue"}
    assert parse_action(
        '{"tool":"finish","answer":"done"}', final_step=True
    ) == {"tool": "finish", "answer": "done"}
    try:
        parse_action('{"tool":"finish","answer":"early"}', final_step=False)
    except ModelRunnerError:
        pass
    else:
        raise AssertionError("early finish must be rejected")
    standard = cases_for_profile("standard")
    specs = build_specs(standard[:1], 4, ARMS)
    assert [arm for _, arm, _ in specs[:4]] == list(ARMS)
    assert [arm for _, arm, _ in specs[4:8]] == list(ARMS[1:] + ARMS[:1])
    print("skill-state four-arm runner self-test: PASS")


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", choices=sorted(PROFILES), default="standard")
    parser.add_argument("--case", action="append", default=[])
    parser.add_argument("--arm", action="append", choices=ARMS)
    parser.add_argument("--runs", type=int, default=1)
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--reasoning", default=DEFAULT_REASONING)
    parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT)
    parser.add_argument("--api-key-env", default="OPENAI_API_KEY")
    parser.add_argument("--timeout", type=float, default=180.0)
    parser.add_argument("--max-attempts", type=int, default=MAX_TRANSITION_ATTEMPTS)
    parser.add_argument("--max-output-tokens", type=int, default=MAX_OUTPUT_TOKENS)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)
    if args.arm is None:
        args.arm = list(ARMS)
    if args.output is None and not args.self_test:
        stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
        args.output = ROOT / "benchmark-results" / f"skill-state-{args.profile}-{stamp}"
    return args


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    if args.self_test:
        self_test()
        return 0
    return run(args)


if __name__ == "__main__":
    raise SystemExit(main())

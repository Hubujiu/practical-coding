#!/usr/bin/env python3
"""Run the execution-state four-arm model comparison without altering the tree.

This runner uses a frozen scripted observation stream to isolate long-horizon
state retention from repository exploration.  It compares full-history,
state-shadow, state-history-free, and no-skill full-history arms.  The
state-history-free arm uses ``HistoryFreeHost`` plus the exact-byte HTTP transport
and saves a redacted final outbound body/header/cookie/proxy audit for every
request.

The runner never executes model-proposed shell commands.  The only benchmark
actions are ``continue`` and ``finish|<one-line final answer>``.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import copy
import datetime as dt
import hashlib
import json
import os
import statistics
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence
from urllib.parse import urlsplit

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from skill_state_model_cases import (  # noqa: E402
    ALL_ARMS,
    ARM_NO_SKILL_FULL_HISTORY,
    ARM_STATE_HISTORY_FREE,
    ARM_STATE_SHADOW,
    DEFAULT_ARMS_BY_PROFILE,
    PROFILES,
    STATE_ARMS,
    StateCase,
    render_case,
    select_cases,
    validate_cases,
)

RUNNER_SCHEMA_VERSION = "1.0"
DEFAULT_MODEL = os.environ.get("OPENAI_MODEL", "gpt-5.6-luna")
DEFAULT_REASONING = os.environ.get("OPENAI_REASONING", "medium")
DEFAULT_ENDPOINT = os.environ.get(
    "OPENAI_RESPONSES_ENDPOINT", "https://api.openai.com/v1/responses"
)
DEFAULT_MAX_ATTEMPTS = 2
DEFAULT_MAX_OUTPUT_TOKENS = 2048
DEFAULT_TIMEOUT_SECONDS = 180.0


@dataclass(frozen=True)
class RuntimeBindings:
    initial_state: Any
    apply_transition: Any
    parse_transition: Any
    validate_state: Any
    HistoryFreeHost: Any
    ExactResponsesTransport: Any
    transport_audit_passes: Any
    HostBoundaryError: type[BaseException]
    HostTransportError: type[BaseException]
    StateValidationError: type[BaseException]


def _runtime_bindings() -> RuntimeBindings:
    from runtime.skill_state import (  # pylint: disable=import-outside-toplevel
        StateValidationError,
        apply_transition,
        initial_state,
        parse_transition,
        validate_state,
    )
    from runtime.skill_state_host import (  # pylint: disable=import-outside-toplevel
        HistoryFreeHost,
        HostBoundaryError,
        HostTransportError,
    )
    from runtime.skill_state_http_transport import (  # pylint: disable=import-outside-toplevel
        ExactResponsesTransport,
        transport_audit_passes,
    )

    return RuntimeBindings(
        initial_state=initial_state,
        apply_transition=apply_transition,
        parse_transition=parse_transition,
        validate_state=validate_state,
        HistoryFreeHost=HistoryFreeHost,
        ExactResponsesTransport=ExactResponsesTransport,
        transport_audit_passes=transport_audit_passes,
        HostBoundaryError=HostBoundaryError,
        HostTransportError=HostTransportError,
        StateValidationError=StateValidationError,
    )


def _canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_text(value: str) -> str:
    return _sha256_bytes(value.encode("utf-8"))


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False)
        + "\n",
        encoding="utf-8",
    )


def _write_bytes(path: Path, value: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(value)


def _git_output(arguments: Sequence[str]) -> str | None:
    try:
        completed = subprocess.run(
            ["git", *arguments],
            cwd=ROOT,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=20,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if completed.returncode:
        return None
    return completed.stdout.strip() or None


def _skill_bundle() -> str:
    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    return skill.rstrip() + "\n"


def _benchmark_protocol(*, state_enabled: bool) -> str:
    patch_rule = (
        "Update the supplied canonical state with a minimal state_patch."
        if state_enabled
        else "Return an empty state_patch; this arm has no canonical execution state."
    )
    return (
        "\n\nExecution-state model-gate protocol:\n"
        "- Process exactly the latest scripted observation.\n"
        "- Do not execute commands, call tools, browse, or modify files.\n"
        "- Observations beginning with DISTRACTOR are unrelated telemetry and must not be treated as task facts.\n"
        "- A CORRECTION supersedes the stale current fact in the same transition.\n"
        "- Do not finish before an observation beginning with FINAL.\n"
        f"- {patch_rule}\n"
        "- For every non-final observation return action `continue`.\n"
        "- For the FINAL observation return action `finish|<one-line answer>`.\n"
        "- Return exactly one JSON object and no Markdown or explanation: "
        '{"state_patch":{},"action":"continue"}.\n'
    )


def _instructions(arm: str) -> str:
    state_enabled = arm in STATE_ARMS
    protocol = _benchmark_protocol(state_enabled=state_enabled)
    if arm == ARM_NO_SKILL_FULL_HISTORY:
        return "You are participating in a frozen long-horizon state benchmark." + protocol
    return _skill_bundle() + protocol


def _response_options(args: argparse.Namespace) -> dict[str, Any]:
    options: dict[str, Any] = {"max_output_tokens": args.max_output_tokens}
    if args.reasoning:
        options["reasoning"] = {"effort": args.reasoning}
    return options


def _full_history_request(
    *,
    model: str,
    instructions: str,
    case: StateCase,
    history: Sequence[Mapping[str, Any]],
    latest_observation: str,
    state: Mapping[str, Any] | None,
    validation_error: str | None,
    options: Mapping[str, Any],
) -> bytes:
    runtime_input: dict[str, Any] = {
        "schema_version": 1,
        "objective": case.objective,
        "success": list(case.success),
        "history": copy.deepcopy(list(history)),
        "latest_observation": latest_observation,
    }
    if state is not None:
        runtime_input["state"] = copy.deepcopy(dict(state))
    if validation_error is not None:
        runtime_input["validation_error"] = validation_error
    body: dict[str, Any] = {
        "model": model,
        "instructions": instructions,
        "input": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": json.dumps(
                            runtime_input,
                            ensure_ascii=False,
                            sort_keys=True,
                            separators=(",", ":"),
                            allow_nan=False,
                        ),
                    }
                ],
            }
        ],
        "store": False,
        "stream": False,
        "background": False,
        "truncation": "disabled",
    }
    body.update(copy.deepcopy(dict(options)))
    return _canonical_json_bytes(body)


def _extract_output_text(response: Mapping[str, Any]) -> str:
    error = response.get("error")
    if error not in (None, {}):
        raise ValueError(f"model response contains error: {error}")
    status = response.get("status")
    if status is not None and status != "completed":
        raise ValueError(f"model response status is not completed: {status!r}")
    output = response.get("output")
    if not isinstance(output, list):
        direct = response.get("output_text")
        if isinstance(direct, str) and direct.strip():
            return direct
        raise ValueError("model response has no output array")
    messages: list[str] = []
    for item in output:
        if not isinstance(item, dict):
            raise ValueError("model response output item must be an object")
        if item.get("type") == "reasoning":
            continue
        if item.get("type") != "message":
            raise ValueError(f"unsupported response output type: {item.get('type')!r}")
        content = item.get("content")
        if not isinstance(content, list):
            raise ValueError("assistant message content must be an array")
        parts: list[str] = []
        for block in content:
            if not isinstance(block, dict):
                raise ValueError("assistant content block must be an object")
            if block.get("type") == "refusal":
                raise ValueError("model refused the transition")
            if block.get("type") != "output_text" or not isinstance(block.get("text"), str):
                raise ValueError(f"unsupported assistant content type: {block.get('type')!r}")
            parts.append(block["text"])
        text = "".join(parts)
        if text.strip():
            messages.append(text)
    if len(messages) != 1:
        raise ValueError(f"expected exactly one assistant transition message, got {len(messages)}")
    direct = response.get("output_text")
    if direct is not None and direct != messages[0]:
        raise ValueError("response.output_text disagrees with canonical output message")
    return messages[0]


def _usage(response: Mapping[str, Any]) -> dict[str, int | None]:
    usage = response.get("usage")
    if not isinstance(usage, dict):
        return {
            "input_tokens": None,
            "cached_input_tokens": None,
            "uncached_input_tokens": None,
            "output_tokens": None,
            "total_tokens": None,
        }

    def integer(name: str) -> int | None:
        value = usage.get(name)
        return value if type(value) is int and value >= 0 else None

    input_tokens = integer("input_tokens")
    output_tokens = integer("output_tokens")
    total_tokens = integer("total_tokens")
    details = usage.get("input_tokens_details")
    cached_tokens = None
    if isinstance(details, dict):
        value = details.get("cached_tokens")
        if type(value) is int and value >= 0:
            cached_tokens = value
    uncached = None
    if input_tokens is not None and cached_tokens is not None and cached_tokens <= input_tokens:
        uncached = input_tokens - cached_tokens
    return {
        "input_tokens": input_tokens,
        "cached_input_tokens": cached_tokens,
        "uncached_input_tokens": uncached,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens,
    }


def _compact_feedback(error: BaseException | str, limit_bytes: int = 2048) -> str:
    message = str(error).replace("\x00", " ").replace("\r", " ").replace("\n", " ").strip()
    prefix = "Previous transition rejected: "
    suffix = ". Return a corrected transition for the same observation."
    encoded = message.encode("utf-8", errors="replace")
    allowance = max(0, limit_bytes - len((prefix + suffix).encode("utf-8")))
    encoded = encoded[:allowance]
    while True:
        try:
            message = encoded.decode("utf-8")
            break
        except UnicodeDecodeError:
            encoded = encoded[:-1]
    return prefix + message + suffix


def _parse_action(action: str, *, final_step: bool) -> tuple[str, str | None]:
    if final_step:
        if not action.startswith("finish|"):
            raise ValueError("FINAL observation requires action finish|<one-line answer>")
        answer = action.split("|", 1)[1].strip()
        if not answer:
            raise ValueError("finish action must contain a non-empty answer")
        return "finish", answer
    if action != "continue":
        raise ValueError("non-final observation requires action continue")
    return "continue", None


def _path_value(state: Mapping[str, Any], dotted: str) -> tuple[bool, Any]:
    current: Any = state
    for part in dotted.split("."):
        if not isinstance(current, Mapping) or part not in current:
            return False, None
        current = current[part]
    return True, current


def _score_answer(case: StateCase, answer: str) -> dict[str, Any]:
    lowered = answer.casefold()
    missing = [
        list(group)
        for group in case.required_answer_groups
        if not any(term.casefold() in lowered for term in group)
    ]
    forbidden = [term for term in case.forbidden_answer_terms if term.casefold() in lowered]
    return {
        "answer_required_groups_missing": missing,
        "answer_forbidden_terms_present": forbidden,
        "answer_pass": not missing and not forbidden,
    }


def _score_state(case: StateCase, state: Mapping[str, Any] | None) -> dict[str, Any]:
    if state is None:
        return {
            "state_evaluated": False,
            "state_required_paths_missing": [],
            "state_required_terms_missing": [],
            "state_forbidden_terms_present": [],
            "state_mechanism_failures": [],
            "state_pass": None,
        }
    path_failures: list[dict[str, Any]] = []
    for path, expected in case.required_state_paths:
        present, actual = _path_value(state, path)
        if not present or actual != expected:
            path_failures.append({"path": path, "expected": expected, "actual": actual, "present": present})
    encoded = json.dumps(state, ensure_ascii=False, sort_keys=True, allow_nan=False)
    lowered = encoded.casefold()
    missing_terms = [term for term in case.required_state_terms if term.casefold() not in lowered]
    forbidden_terms = [term for term in case.forbidden_state_terms if term.casefold() in lowered]
    mechanism_failures: list[str] = []
    if case.case_id == "rejected-cache-hypothesis":
        hypotheses = state.get("hypotheses") if isinstance(state, Mapping) else None
        active = hypotheses.get("active") if isinstance(hypotheses, Mapping) else None
        rejected = hypotheses.get("rejected") if isinstance(hypotheses, Mapping) else None
        if not isinstance(rejected, Mapping) or "h-cache" not in rejected:
            mechanism_failures.append("h-cache was not retained in hypotheses.rejected")
        if isinstance(active, Mapping) and "h-cache" in active:
            mechanism_failures.append("h-cache remained active after rejection")
        if not isinstance(active, Mapping) or "parser-transition" not in active:
            mechanism_failures.append("parser-transition was not active at completion")
    passed = not path_failures and not missing_terms and not forbidden_terms and not mechanism_failures
    return {
        "state_evaluated": True,
        "state_required_paths_missing": path_failures,
        "state_required_terms_missing": missing_terms,
        "state_forbidden_terms_present": forbidden_terms,
        "state_mechanism_failures": mechanism_failures,
        "state_pass": passed,
    }


def _artifact_case(cell: Path, case: StateCase) -> tuple[StateCase, dict[str, Any] | None]:
    if not case.history_required:
        return case, None
    if case.artifact_payload is None:
        raise ValueError(f"{case.case_id}: history-required case has no artifact payload")
    relative = Path("artifacts") / "audit-evidence.json"
    path = cell / relative
    payload = case.artifact_payload.encode("utf-8")
    _write_bytes(path, payload)
    digest = _sha256_bytes(payload)
    pointer = f"{relative.as_posix()}#sha256={digest}"
    rendered = render_case(
        case,
        {
            "artifact_path": relative.as_posix(),
            "artifact_sha256": digest,
            "artifact_pointer": pointer,
        },
    )
    return rendered, {
        "path": relative.as_posix(),
        "sha256": digest,
        "pointer": pointer,
        "bytes": len(payload),
    }


def _artifact_integrity(cell: Path, artifact: Mapping[str, Any] | None, state: Mapping[str, Any] | None) -> dict[str, Any]:
    if artifact is None:
        return {"required": False, "artifact_pass": None}
    path = cell / str(artifact["path"])
    exists = path.is_file()
    digest = _sha256_bytes(path.read_bytes()) if exists else None
    pointer_present = False
    history_required = False
    if isinstance(state, Mapping):
        history = state.get("history")
        if isinstance(history, Mapping):
            history_required = history.get("required") is True
            artifacts = history.get("artifacts")
            pointer_present = isinstance(artifacts, list) and artifact["pointer"] in artifacts
    passed = bool(exists and digest == artifact["sha256"] and history_required and pointer_present)
    return {
        "required": True,
        "path": artifact["path"],
        "expected_sha256": artifact["sha256"],
        "observed_sha256": digest,
        "exists": exists,
        "history_required": history_required,
        "pointer_present": pointer_present,
        "artifact_pass": passed,
    }


def _sum_optional(records: Sequence[Mapping[str, Any]], key: str) -> int | None:
    values = [record.get(key) for record in records]
    if not values or any(type(value) is not int for value in values):
        return None
    return sum(int(value) for value in values)


def _endpoint_host(endpoint: str) -> str:
    return (urlsplit(endpoint).hostname or "").lower()


def _additional_headers() -> dict[str, str]:
    headers: dict[str, str] = {}
    organization = os.environ.get("OPENAI_ORGANIZATION")
    project = os.environ.get("OPENAI_PROJECT")
    if organization:
        headers["OpenAI-Organization"] = organization
    if project:
        headers["OpenAI-Project"] = project
    return headers


def _run_cell(
    case_template: StateCase,
    arm: str,
    repetition: int,
    args: argparse.Namespace,
    output: Path,
    manifest: Mapping[str, Any],
) -> dict[str, Any]:
    bindings = _runtime_bindings()
    safe_arm = arm.replace("/", "-")
    cell = output / "cells" / case_template.case_id / safe_arm / f"r{repetition:03d}"
    result_path = cell / "result.json"
    if args.resume and result_path.is_file():
        return json.loads(result_path.read_text(encoding="utf-8"))
    if cell.exists() and not args.resume:
        raise FileExistsError(f"cell already exists: {cell}")
    cell.mkdir(parents=True, exist_ok=True)
    case, artifact = _artifact_case(cell, case_template)
    _write_json(cell / "case.json", case.to_dict())

    state = bindings.initial_state(case.objective, case.success) if arm in STATE_ARMS else None
    history: list[dict[str, Any]] = []
    instructions = _instructions(arm)
    options = _response_options(args)
    host = None
    host_manifest = None
    if arm == ARM_STATE_HISTORY_FREE:
        host = bindings.HistoryFreeHost(
            model=args.model,
            procedure=instructions,
            options=options,
        )
        host_manifest = host.manifest()
        _write_json(cell / "host-manifest.json", host_manifest)

    trusted_hosts = {"api.openai.com", *args.trusted_endpoint_host}
    endpoint_host = _endpoint_host(args.endpoint)
    transport = bindings.ExactResponsesTransport.from_environment(
        api_key_env=args.api_key_env,
        endpoint=args.endpoint,
        timeout_seconds=args.timeout,
        manifest=host_manifest,
        additional_headers=_additional_headers(),
        trusted_endpoint_hosts=sorted(trusted_hosts),
        allow_insecure_http=args.allow_insecure_http,
    )

    attempts: list[dict[str, Any]] = []
    final_answer: str | None = None
    infrastructure_error: str | None = None
    model_protocol_failure: str | None = None
    started = time.perf_counter()

    for step_index, observation in enumerate(case.observations, start=1):
        final_step = step_index == len(case.observations)
        original_state = copy.deepcopy(state) if state is not None else None
        feedback: str | None = None
        accepted = False
        for attempt_number in range(1, args.max_attempts + 1):
            if arm == ARM_STATE_HISTORY_FREE:
                assert host is not None and original_state is not None
                prepared = host.prepare_request(
                    original_state,
                    observation,
                    validation_error=feedback,
                    step_id=f"{case.case_id}/step-{step_index:03d}",
                    attempt=attempt_number,
                )
                request_bytes = prepared.wire_bytes
                host_request_audit = dict(prepared.audit)
            else:
                request_bytes = _full_history_request(
                    model=args.model,
                    instructions=instructions,
                    case=case,
                    history=history,
                    latest_observation=observation,
                    state=original_state if arm == ARM_STATE_SHADOW else None,
                    validation_error=feedback,
                    options=options,
                )
                host_request_audit = None

            request_path = cell / "requests" / f"step-{step_index:03d}-attempt-{attempt_number:02d}.json"
            response_path = cell / "responses" / f"step-{step_index:03d}-attempt-{attempt_number:02d}.json"
            audit_path = cell / "transport-audits" / f"step-{step_index:03d}-attempt-{attempt_number:02d}.json"
            _write_bytes(request_path, request_bytes)
            try:
                response = transport(request_bytes)
            except (bindings.HostTransportError, OSError) as exc:
                infrastructure_error = f"transport failure at step {step_index} attempt {attempt_number}: {exc}"
                break
            _write_bytes(response_path, response.body)
            transport_audit = dict(transport.last_audit or {})
            _write_json(audit_path, transport_audit)
            attempt_record: dict[str, Any] = {
                "step": step_index,
                "attempt": attempt_number,
                "final_step": final_step,
                "request_path": str(request_path.relative_to(cell)).replace("\\", "/"),
                "response_path": str(response_path.relative_to(cell)).replace("\\", "/"),
                "transport_audit_path": str(audit_path.relative_to(cell)).replace("\\", "/"),
                "request_sha256": _sha256_bytes(request_bytes),
                "request_bytes": len(request_bytes),
                "http_status": response.status_code,
                "host_request_audit": host_request_audit,
                "transport_audit": transport_audit,
            }
            if not 200 <= response.status_code < 300:
                infrastructure_error = (
                    f"HTTP {response.status_code} at step {step_index} attempt {attempt_number}"
                )
                attempt_record["transition_status"] = "infrastructure-error"
                attempts.append(attempt_record)
                break
            try:
                decoded = json.loads(response.body.decode("utf-8"))
                if not isinstance(decoded, dict):
                    raise ValueError("model response must be a JSON object")
                attempt_record.update(_usage(decoded))
                transition_text = _extract_output_text(decoded)
                attempt_record["transition_sha256"] = _sha256_text(transition_text)
                patch, action = bindings.parse_transition(transition_text)
                if arm in STATE_ARMS:
                    assert original_state is not None
                    successor, action = bindings.apply_transition(original_state, transition_text)
                else:
                    if patch:
                        raise ValueError("non-state arm must return an empty state_patch")
                    successor = None
                action_kind, answer = _parse_action(action, final_step=final_step)
            except (
                UnicodeDecodeError,
                json.JSONDecodeError,
                ValueError,
                bindings.HostBoundaryError,
                bindings.StateValidationError,
            ) as exc:
                feedback = _compact_feedback(exc)
                attempt_record.update(
                    {
                        "transition_status": "rejected",
                        "validation_error": feedback,
                    }
                )
                attempts.append(attempt_record)
                continue

            attempt_record.update(
                {
                    "transition_status": "accepted",
                    "action_kind": action_kind,
                    "answer_sha256": _sha256_text(answer) if answer is not None else None,
                }
            )
            attempts.append(attempt_record)
            if state is not None:
                state = copy.deepcopy(successor)
                bindings.validate_state(state)
                _write_json(cell / "states" / f"step-{step_index:03d}.json", state)
            if final_step:
                final_answer = answer
            else:
                history.append(
                    {
                        "step": step_index,
                        "observation": observation,
                        "accepted_transition": transition_text,
                    }
                )
            accepted = True
            break

        if infrastructure_error:
            break
        if not accepted:
            model_protocol_failure = (
                f"all {args.max_attempts} transitions rejected at step {step_index}"
            )
            break

    elapsed = time.perf_counter() - started
    answer_score = _score_answer(case, final_answer or "")
    state_score = _score_state(case, state)
    artifact_score = _artifact_integrity(cell, artifact, state)
    history_free_transport_audits = [
        record["transport_audit"]
        for record in attempts
        if arm == ARM_STATE_HISTORY_FREE and record.get("transport_audit")
    ]
    transport_gate = None
    if arm == ARM_STATE_HISTORY_FREE:
        transport_gate = bool(history_free_transport_audits) and all(
            bindings.transport_audit_passes(audit) for audit in history_free_transport_audits
        )
    determinate = infrastructure_error is None
    state_required_pass = state_score["state_pass"] is not False
    artifact_required_pass = artifact_score["artifact_pass"] is not False
    passed = bool(
        determinate
        and model_protocol_failure is None
        and final_answer is not None
        and answer_score["answer_pass"]
        and state_required_pass
        and artifact_required_pass
    )
    result: dict[str, Any] = {
        "schema_version": RUNNER_SCHEMA_VERSION,
        "runner_manifest_sha256": manifest["manifest_sha256"],
        "case_id": case.case_id,
        "profile": case.profile,
        "family": case.family,
        "repository": case.repository,
        "repository_commit": case.repository_commit,
        "horizon": case.horizon or len(case.observations),
        "arm": arm,
        "repetition": repetition,
        "model": args.model,
        "reasoning": args.reasoning,
        "endpoint_host": endpoint_host,
        "workers": args.workers,
        "observation_count": len(case.observations),
        "observations_sha256": [
            _sha256_text(observation) for observation in case.observations
        ],
        "attempt_count": len(attempts),
        "rejected_transition_count": sum(
            record.get("transition_status") == "rejected" for record in attempts
        ),
        "accepted_transition_count": sum(
            record.get("transition_status") == "accepted" for record in attempts
        ),
        "input_tokens": _sum_optional(attempts, "input_tokens"),
        "cached_input_tokens": _sum_optional(attempts, "cached_input_tokens"),
        "uncached_input_tokens": _sum_optional(attempts, "uncached_input_tokens"),
        "output_tokens": _sum_optional(attempts, "output_tokens"),
        "total_tokens": _sum_optional(attempts, "total_tokens"),
        "transport_duration_seconds": sum(
            float((record.get("transport_audit") or {}).get("elapsed_ms") or 0.0)
            for record in attempts
        )
        / 1000.0,
        "end_to_end_duration_seconds": elapsed,
        "max_request_bytes": max(
            (int(record.get("request_bytes") or 0) for record in attempts),
            default=0,
        ),
        "final_answer": final_answer,
        "final_answer_sha256": _sha256_text(final_answer) if final_answer is not None else None,
        "final_state": state,
        "final_state_sha256": (
            _sha256_bytes(_canonical_json_bytes(state)) if state is not None else None
        ),
        "final_state_bytes": len(_canonical_json_bytes(state)) if state is not None else None,
        "answer_score": answer_score,
        "state_score": state_score,
        "artifact_score": artifact_score,
        "history_free_transport_gate": transport_gate,
        "infrastructure_error": infrastructure_error,
        "model_protocol_failure": model_protocol_failure,
        "passed": passed if determinate else None,
        "verdict": "indeterminate" if not determinate else ("pass" if passed else "fail"),
        "attempts": attempts,
    }
    _write_json(result_path, result)
    return result


def _build_specs(
    cases: Sequence[StateCase], arms: Sequence[str], runs: int
) -> list[tuple[StateCase, str, int]]:
    return [
        (case, arm, repetition)
        for case in cases
        for arm in arms
        for repetition in range(1, runs + 1)
    ]


def _manifest(args: argparse.Namespace, cases: Sequence[StateCase], arms: Sequence[str]) -> dict[str, Any]:
    endpoint = urlsplit(args.endpoint)
    manifest: dict[str, Any] = {
        "schema_version": RUNNER_SCHEMA_VERSION,
        "runner": "benchmarks/skill_state_model_runner.py",
        "candidate_commit": _git_output(["rev-parse", "HEAD"]),
        "branch": _git_output(["branch", "--show-current"]),
        "worktree_status": _git_output(["status", "--porcelain"]),
        "started_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "profile": args.profile,
        "runs": args.runs,
        "workers": args.workers,
        "arms": list(arms),
        "model": args.model,
        "reasoning": args.reasoning,
        "endpoint": {
            "scheme": endpoint.scheme,
            "host": endpoint.hostname,
            "port": endpoint.port,
            "path": endpoint.path,
        },
        "trusted_endpoint_hosts": sorted({"api.openai.com", *args.trusted_endpoint_host}),
        "timeout_seconds": args.timeout,
        "max_attempts": args.max_attempts,
        "max_output_tokens": args.max_output_tokens,
        "skill_sha256": _sha256_bytes((ROOT / "SKILL.md").read_bytes()),
        "cases": [case.to_dict() for case in cases],
        "case_catalog_sha256": _sha256_bytes(
            _canonical_json_bytes([case.to_dict() for case in cases])
        ),
        "api_key_env": args.api_key_env,
        "api_key_present": bool(os.environ.get(args.api_key_env)),
        "benchmark_executed": not args.dry_run,
    }
    digest_source = dict(manifest)
    digest_source.pop("started_at", None)
    manifest["manifest_sha256"] = _sha256_bytes(_canonical_json_bytes(digest_source))
    return manifest


def _mean(records: Sequence[Mapping[str, Any]], key: str) -> float | None:
    values = [float(record[key]) for record in records if record.get(key) is not None]
    return statistics.mean(values) if values else None


def _aggregate(records: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    arms: dict[str, Any] = {}
    for arm in sorted({str(record["arm"]) for record in records}):
        selected = [record for record in records if record["arm"] == arm]
        determinate = [record for record in selected if record.get("passed") is not None]
        arms[arm] = {
            "cells": len(selected),
            "determinate": len(determinate),
            "passed": sum(record.get("passed") is True for record in determinate),
            "pass_rate": (
                sum(record.get("passed") is True for record in determinate) / len(determinate)
                if determinate
                else None
            ),
            "input_tokens_mean": _mean(determinate, "input_tokens"),
            "uncached_input_tokens_mean": _mean(determinate, "uncached_input_tokens"),
            "output_tokens_mean": _mean(determinate, "output_tokens"),
            "duration_seconds_mean": _mean(determinate, "end_to_end_duration_seconds"),
            "max_request_bytes": max(
                (int(record.get("max_request_bytes") or 0) for record in selected),
                default=0,
            ),
            "transport_gate_pass_rate": (
                sum(record.get("history_free_transport_gate") is True for record in selected)
                / len(selected)
                if arm == ARM_STATE_HISTORY_FREE and selected
                else None
            ),
        }
    return {
        "cells": len(records),
        "determinate": sum(record.get("passed") is not None for record in records),
        "passed": sum(record.get("passed") is True for record in records),
        "arms": arms,
    }


def _validate_selection(profile: str, arms: Sequence[str], runs: int, workers: int) -> None:
    if profile not in PROFILES:
        raise ValueError(f"unknown profile: {profile}")
    unknown = set(arms) - set(ALL_ARMS)
    if unknown:
        raise ValueError(f"unknown arms: {', '.join(sorted(unknown))}")
    if not arms:
        raise ValueError("at least one arm is required")
    if runs < 1 or workers < 1:
        raise ValueError("runs and workers must be positive")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", choices=PROFILES, default="standard")
    parser.add_argument("--case", action="append", default=[])
    parser.add_argument("--arm", action="append", choices=ALL_ARMS, default=[])
    parser.add_argument("--runs", type=int, default=1)
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--reasoning", default=DEFAULT_REASONING)
    parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT)
    parser.add_argument("--trusted-endpoint-host", action="append", default=[])
    parser.add_argument("--api-key-env", default="OPENAI_API_KEY")
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT_SECONDS)
    parser.add_argument("--max-attempts", type=int, default=DEFAULT_MAX_ATTEMPTS)
    parser.add_argument("--max-output-tokens", type=int, default=DEFAULT_MAX_OUTPUT_TOKENS)
    parser.add_argument("--allow-insecure-http", action="store_true")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    return parser


def self_test() -> None:
    validate_cases()
    cases = select_cases("smoke")
    assert len(cases) == 2
    assert _parse_action("continue", final_step=False) == ("continue", None)
    assert _parse_action("finish|done", final_step=True) == ("finish", "done")
    try:
        _parse_action("continue", final_step=True)
    except ValueError:
        pass
    else:
        raise AssertionError("final-step action validation did not fail closed")
    request = _full_history_request(
        model="test-model",
        instructions="test",
        case=cases[0],
        history=[],
        latest_observation=cases[0].observations[0],
        state=None,
        validation_error=None,
        options={"max_output_tokens": 64},
    )
    decoded = json.loads(request)
    assert decoded["store"] is False and decoded["truncation"] == "disabled"
    assert "previous_response_id" not in decoded and "conversation" not in decoded
    assert _score_answer(cases[0], "d85c72cc5aa239da32352309e723ed1e6fc80429 experiment/evolvable-router-tree python -m unittest tests.test_skill_state_host")["answer_pass"]
    print("skill-state model runner self-test: PASS")


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.self_test:
        self_test()
        return 0
    arms = tuple(args.arm or DEFAULT_ARMS_BY_PROFILE[args.profile])
    _validate_selection(args.profile, arms, args.runs, args.workers)
    if not 1 <= args.max_attempts <= 3:
        raise SystemExit("--max-attempts must be between 1 and 3")
    if args.max_output_tokens < 64:
        raise SystemExit("--max-output-tokens must be at least 64")
    cases = select_cases(args.profile, args.case)
    output = (args.output or ROOT / "benchmark-results" / f"skill-state-{args.profile}-{dt.datetime.now().strftime('%Y%m%d-%H%M%S')}").resolve()
    if output.exists() and not args.resume:
        raise SystemExit(f"output already exists; use --resume or another path: {output}")
    output.mkdir(parents=True, exist_ok=True)
    manifest = _manifest(args, cases, arms)
    _write_json(output / "manifest.json", manifest)
    specs = _build_specs(cases, arms, args.runs)
    _write_json(
        output / "specs.json",
        [
            {"case_id": case.case_id, "arm": arm, "repetition": repetition}
            for case, arm, repetition in specs
        ],
    )
    if args.dry_run:
        print(f"prepared {len(specs)} cells under {output}; no model requests sent")
        return 0
    if not os.environ.get(args.api_key_env):
        raise SystemExit(f"required API key environment variable is missing: {args.api_key_env}")

    records: list[dict[str, Any]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = [
            executor.submit(
                _run_cell,
                case,
                arm,
                repetition,
                args,
                output,
                manifest,
            )
            for case, arm, repetition in specs
        ]
        for future in concurrent.futures.as_completed(futures):
            records.append(future.result())
    records.sort(key=lambda row: (row["case_id"], row["arm"], row["repetition"]))
    results_path = output / "results.jsonl"
    results_path.write_text(
        "".join(json.dumps(record, ensure_ascii=False, sort_keys=True, allow_nan=False) + "\n" for record in records),
        encoding="utf-8",
    )
    summary = _aggregate(records)
    summary.update(
        {
            "schema_version": RUNNER_SCHEMA_VERSION,
            "manifest_sha256": manifest["manifest_sha256"],
            "profile": args.profile,
            "runs": args.runs,
            "workers": args.workers,
            "results_jsonl": str(results_path),
        }
    )
    _write_json(output / "run-summary.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary["determinate"] == summary["cells"] else 2


if __name__ == "__main__":
    raise SystemExit(main())

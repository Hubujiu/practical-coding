#!/usr/bin/env python3
"""Execution-state four-arm runner with frozen scorer and wire profiles.

The original ea8580f implementation is retained in
``benchmarks/_skill_state_model_runner_impl.py``.  This public entry point applies
only two evidence-driven infrastructure repairs:

* a general separator-normalizing answer scorer and state-arm-aware artifact gate;
* an explicit, frozen ``codex-sse-v1`` outbound wire profile.

It does not alter Skill text, state schema, case semantics, or router topology.
"""

from __future__ import annotations

import argparse
import copy
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any, Mapping, Sequence
from urllib.parse import urlsplit

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import _skill_state_model_runner_impl as _impl  # noqa: E402
from skill_state_model_scoring import (  # noqa: E402
    SCORER_CONTRACT_VERSION,
    artifact_integrity,
    score_answer,
)
from runtime.skill_state_http_transport import (  # noqa: E402
    CODEX_ACCOUNT_ID_ENV,
    DEFAULT_CODEX_AUTH_PATH,
    DEFAULT_CODEX_RESPONSES_ENDPOINT,
    WIRE_PROFILE_CODEX_SSE,
    WIRE_PROFILE_RESPONSES_JSON,
    WIRE_PROFILES,
    Endpoint,
    load_codex_credentials,
    normalize_sse_response,
    prepare_profiled_request,
    transport_profile_context,
    wire_profile_contract_manifest,
)

WRAPPER_SCHEMA_VERSION = "1.1"
CODEX_ACCESS_TOKEN_ENV = "PRACTICAL_CODING_CODEX_ACCESS_TOKEN"
WIRE_PROFILE_ENV = "PRACTICAL_CODING_WIRE_PROFILE"
CODEX_AUTH_PATH_ENV = "PRACTICAL_CODING_CODEX_AUTH_JSON"

_ORIGINAL_PARSER = _impl._parser
_ORIGINAL_MANIFEST = _impl._manifest
_ORIGINAL_AGGREGATE = _impl._aggregate
_ORIGINAL_RUN_CELL = _impl._run_cell
_ORIGINAL_SELF_TEST = _impl.self_test

_ACTIVE_WIRE_PROFILE = WIRE_PROFILE_RESPONSES_JSON
_ACTIVE_CODEX_ACCOUNT_ID: str | None = None
_ACTIVE_AUTH_SOURCE = "api-key-env"


def _parser() -> argparse.ArgumentParser:
    parser = _ORIGINAL_PARSER()
    parser.add_argument(
        "--wire-profile",
        choices=WIRE_PROFILES,
        default=os.environ.get(WIRE_PROFILE_ENV, WIRE_PROFILE_RESPONSES_JSON),
        help=(
            "final outbound profile: responses-json-v1 for API-key Responses, "
            "or codex-sse-v1 for existing Codex ChatGPT OAuth"
        ),
    )
    parser.add_argument(
        "--codex-auth-json",
        type=Path,
        default=Path(os.environ.get(CODEX_AUTH_PATH_ENV, str(DEFAULT_CODEX_AUTH_PATH))),
        help="read-only Codex auth.json path used only by codex-sse-v1",
    )
    return parser


def _has_option(argv: Sequence[str], name: str) -> bool:
    return any(value == name or value.startswith(name + "=") for value in argv)


def _selected_wire_profile(argv: Sequence[str]) -> str:
    for index, value in enumerate(argv):
        if value == "--wire-profile" and index + 1 < len(argv):
            return argv[index + 1]
        if value.startswith("--wire-profile="):
            return value.split("=", 1)[1]
    return os.environ.get(WIRE_PROFILE_ENV, WIRE_PROFILE_RESPONSES_JSON)


def _normalize_argv(argv: Sequence[str] | None) -> list[str]:
    values = list(sys.argv[1:] if argv is None else argv)
    profile = _selected_wire_profile(values)
    if profile == WIRE_PROFILE_CODEX_SSE:
        if not _has_option(values, "--endpoint"):
            values.extend(["--endpoint", DEFAULT_CODEX_RESPONSES_ENDPOINT])
        if not _has_option(values, "--trusted-endpoint-host"):
            values.extend(["--trusted-endpoint-host", "chatgpt.com"])
        if not _has_option(values, "--api-key-env"):
            values.extend(["--api-key-env", CODEX_ACCESS_TOKEN_ENV])
    return values


def _manifest(
    args: argparse.Namespace,
    cases: Sequence[Any],
    arms: Sequence[str],
) -> dict[str, Any]:
    manifest = _ORIGINAL_MANIFEST(args, cases, arms)
    profile_contract = wire_profile_contract_manifest(args.wire_profile)
    manifest.update(
        {
            "schema_version": WRAPPER_SCHEMA_VERSION,
            "scorer_contract_version": SCORER_CONTRACT_VERSION,
            "answer_match_normalization": "NFKC+casefold+separator-equivalence",
            "artifact_contract": (
                "immutable file+digest for every arm; state.history pointer only for state arms"
            ),
            "wire_profile": args.wire_profile,
            "wire_profile_contract_sha256": profile_contract["manifest_sha256"],
            "wire_profile_contract": profile_contract,
            "auth_source": _ACTIVE_AUTH_SOURCE,
            "codex_account_id_header_present": bool(_ACTIVE_CODEX_ACCOUNT_ID)
            if args.wire_profile == WIRE_PROFILE_CODEX_SSE
            else False,
            "output_token_limit": (
                "provider-managed"
                if args.wire_profile == WIRE_PROFILE_CODEX_SSE
                else {"request_field": "max_output_tokens", "value": args.max_output_tokens}
            ),
        }
    )
    digest_source = dict(manifest)
    digest_source.pop("started_at", None)
    digest_source.pop("manifest_sha256", None)
    manifest["manifest_sha256"] = _impl._sha256_bytes(
        _impl._canonical_json_bytes(digest_source)
    )
    return manifest


def _run_cell(
    case_template: Any,
    arm: str,
    repetition: int,
    args: argparse.Namespace,
    output: Path,
    manifest: Mapping[str, Any],
) -> dict[str, Any]:
    cell = output / "cells" / case_template.case_id / arm.replace("/", "-") / f"r{repetition:03d}"
    existing_result = cell / "result.json"
    if args.resume and existing_result.is_file():
        previous = json.loads(existing_result.read_text(encoding="utf-8"))
        if (
            previous.get("scorer_contract_version") != SCORER_CONTRACT_VERSION
            or previous.get("wire_profile") != args.wire_profile
        ):
            raise RuntimeError(
                "--resume cannot relabel cells produced by another scorer or wire profile; "
                "start a fresh output directory"
            )
    with transport_profile_context(
        wire_profile=args.wire_profile,
        artifact_directory=cell / "wire-artifacts",
        codex_account_id=_ACTIVE_CODEX_ACCOUNT_ID,
    ):
        result = _ORIGINAL_RUN_CELL(
            case_template,
            arm,
            repetition,
            args,
            output,
            manifest,
        )
    result["wire_profile"] = args.wire_profile
    result["scorer_contract_version"] = SCORER_CONTRACT_VERSION
    if args.wire_profile == WIRE_PROFILE_CODEX_SSE:
        result["output_token_limit"] = "provider-managed"
    # The implementation already persisted result.json before this wrapper-added
    # metadata existed, so replace it deterministically for a complete cell record.
    _impl._write_json(cell / "result.json", result)
    return result


def _aggregate(records: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    summary = _ORIGINAL_AGGREGATE(records)
    for arm, arm_summary in summary.get("arms", {}).items():
        if arm != _impl.ARM_STATE_HISTORY_FREE:
            continue
        selected = [record for record in records if record.get("arm") == arm]
        values = [record.get("history_free_transport_gate") for record in selected]
        determinate = [value for value in values if isinstance(value, bool)]
        arm_summary["transport_gate_determinate"] = len(determinate)
        arm_summary["transport_gate_pending"] = len(values) - len(determinate)
        arm_summary["transport_gate_pass_rate"] = (
            sum(value is True for value in determinate) / len(determinate)
            if determinate
            else None
        )
    summary["scorer_contract_version"] = SCORER_CONTRACT_VERSION
    summary["wire_profiles"] = sorted(
        {str(record.get("wire_profile")) for record in records if record.get("wire_profile")}
    )
    return summary


def _self_test_profile_contracts() -> None:
    cases = _impl.select_cases("standard")
    hypothesis_case = next(case for case in cases if case.case_id == "rejected-cache-hypothesis")
    assert score_answer(
        hypothesis_case,
        "Supported cause: parser transition. The cache hypothesis was rejected.",
    )["answer_pass"]

    artifact_case = next(case for case in cases if case.case_id == "history-required-audit-pointer")
    with tempfile.TemporaryDirectory() as temporary_directory:
        cell = Path(temporary_directory)
        rendered_case, artifact = _impl._artifact_case(cell, artifact_case)
        assert artifact is not None
        answer = f"{artifact['path']} {artifact['sha256']}"
        assert score_answer(rendered_case, answer)["answer_pass"]
        non_state = artifact_integrity(cell, artifact, None)
        assert non_state["artifact_pass"] is True
        assert non_state["state_pointer_required"] is False
        state = _impl._runtime_bindings().initial_state(
            rendered_case.objective,
            rendered_case.success,
        )
        state_without_pointer = artifact_integrity(cell, artifact, state)
        assert state_without_pointer["artifact_pass"] is False

    source = _impl._full_history_request(
        model="test-model",
        instructions="test instructions",
        case=_impl.select_cases("smoke")[0],
        history=[],
        latest_observation="current observation",
        state=None,
        validation_error=None,
        options={"max_output_tokens": 64, "reasoning": {"effort": "medium"}},
    )
    endpoint = Endpoint.parse(DEFAULT_CODEX_RESPONSES_ENDPOINT)
    prepared = prepare_profiled_request(
        source,
        profile=WIRE_PROFILE_CODEX_SSE,
        endpoint=endpoint,
        account_id_header_present=True,
    )
    source_json = json.loads(prepared.source_body)
    wire_json = json.loads(prepared.wire_body)
    assert source_json["stream"] is False and wire_json["stream"] is True
    assert prepared.profile_audit["changed_fields"] == [
        "background",
        "max_output_tokens",
        "stream",
        "truncation",
    ]
    for key, value in source_json.items():
        if key not in {"background", "max_output_tokens", "stream", "truncation"}:
            assert wire_json[key] == value

    message = {
        "type": "message",
        "role": "assistant",
        "content": [
            {
                "type": "output_text",
                "text": '{"state_patch":{},"action":"continue"}',
            }
        ],
    }
    completed_response = {
        "id": "resp_test",
        "status": "completed",
        "store": False,
        "background": False,
        "truncation": "disabled",
        "model": "test-model",
        "output": [message],
        "usage": {
            "input_tokens": 10,
            "input_tokens_details": {"cached_tokens": 3},
            "output_tokens": 4,
            "total_tokens": 14,
        },
    }
    raw_sse = (
        "event: response.output_item.done\n"
        + "data: "
        + json.dumps(
            {"type": "response.output_item.done", "item": message},
            separators=(",", ":"),
        )
        + "\n\n"
        + "event: response.completed\n"
        + "data: "
        + json.dumps(
            {"type": "response.completed", "response": completed_response},
            separators=(",", ":"),
        )
        + "\n\n"
    ).encode("utf-8")
    normalized, metadata = normalize_sse_response(raw_sse)
    decoded = json.loads(normalized)
    assert decoded["output"] == [message]
    assert decoded["usage"]["input_tokens"] == 10
    assert metadata["sse_completed_event_count"] == 1


def self_test() -> None:
    _ORIGINAL_SELF_TEST()
    _self_test_profile_contracts()
    print("skill-state model runner scorer/SSE hardening: PASS")


def main(argv: Sequence[str] | None = None) -> int:
    global _ACTIVE_WIRE_PROFILE, _ACTIVE_CODEX_ACCOUNT_ID, _ACTIVE_AUTH_SOURCE

    normalized_argv = _normalize_argv(argv)
    preview = _parser().parse_args(normalized_argv)
    _ACTIVE_WIRE_PROFILE = preview.wire_profile
    _ACTIVE_CODEX_ACCOUNT_ID = None
    _ACTIVE_AUTH_SOURCE = "api-key-env"

    temporary_token_previous: str | None = None
    temporary_token_set = False
    if preview.wire_profile == WIRE_PROFILE_CODEX_SSE:
        if preview.self_test or preview.dry_run:
            _ACTIVE_AUTH_SOURCE = "not-required-for-self-test-or-dry-run"
        else:
            temporary_token_previous = os.environ.get(preview.api_key_env)
            environment_account_id = os.environ.get(CODEX_ACCOUNT_ID_ENV)
            credentials = None
            if not temporary_token_previous or not environment_account_id:
                credentials = load_codex_credentials(preview.codex_auth_json)
            if not temporary_token_previous:
                assert credentials is not None
                os.environ[preview.api_key_env] = credentials.access_token
                temporary_token_set = True
            _ACTIVE_CODEX_ACCOUNT_ID = environment_account_id or (
                credentials.account_id if credentials is not None else None
            )
            if not _ACTIVE_CODEX_ACCOUNT_ID:
                raise SystemExit(
                    "codex-sse-v1 requires an account ID in auth.json or "
                    f"{CODEX_ACCOUNT_ID_ENV}"
                )
            _ACTIVE_AUTH_SOURCE = (
                "environment"
                if temporary_token_previous and environment_account_id
                else "codex-auth-json-read-only"
            )

    try:
        return _impl.main(normalized_argv)
    finally:
        if temporary_token_set:
            if temporary_token_previous is None:
                os.environ.pop(preview.api_key_env, None)
            else:
                os.environ[preview.api_key_env] = temporary_token_previous


# Patch the retained implementation at stable extension points.  This avoids a
# duplicated 1000-line runner while preserving its public command-line behavior.
_impl._parser = _parser
_impl._manifest = _manifest
_impl._aggregate = _aggregate
_impl._run_cell = _run_cell
_impl._score_answer = score_answer
_impl._artifact_integrity = artifact_integrity
_impl.self_test = self_test

# Re-export the helpers used by ordinary unit tests and downstream scripts.
_score_answer = score_answer
_artifact_integrity = artifact_integrity


def __getattr__(name: str) -> Any:
    return getattr(_impl, name)


if __name__ == "__main__":
    raise SystemExit(main())

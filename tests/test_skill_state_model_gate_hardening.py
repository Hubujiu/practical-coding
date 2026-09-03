from __future__ import annotations

import base64
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from typing import Any

from benchmarks.skill_state_model_scoring import (
    SCORER_CONTRACT_VERSION,
    artifact_integrity,
    evidence_contains,
    normalize_evidence_text,
    score_answer,
)
from benchmarks.skill_state_model_cases import StateCase
from runtime.skill_state import initial_state
from runtime.skill_state_host import HistoryFreeHost
from runtime.skill_state_http_transport import (
    DEFAULT_CODEX_RESPONSES_ENDPOINT,
    WIRE_PROFILE_CODEX_SSE,
    Endpoint,
    ExactResponsesTransport,
    HostTransportError,
    load_codex_credentials,
    normalize_sse_response,
    prepare_profiled_request,
    transport_audit_passes,
    validate_wire_profile_contract_manifest,
    wire_profile_contract_manifest,
)


class _FakeResponse:
    def __init__(self, body: bytes, *, status: int = 200, headers: list[tuple[str, str]] | None = None) -> None:
        self.status = status
        self._body = body
        self._headers = headers or [("content-type", "text/event-stream"), ("x-request-id", "req-test")]

    def getheaders(self) -> list[tuple[str, str]]:
        return list(self._headers)

    def read(self, _limit: int) -> bytes:
        return self._body


class _FakeConnection:
    def __init__(self, response: _FakeResponse | None = None, *, failure: BaseException | None = None) -> None:
        self.response = response
        self.failure = failure
        self.request_body: bytes | None = None
        self.request_headers: dict[str, str] | None = None
        self.closed = False

    def request(self, _method: str, _target: str, *, body: bytes, headers: dict[str, str], encode_chunked: bool) -> None:
        self.request_body = body
        self.request_headers = dict(headers)
        if self.failure is not None:
            raise self.failure
        if encode_chunked:
            raise AssertionError("exact transport must not enable chunking")

    def getresponse(self) -> _FakeResponse:
        if self.response is None:
            raise AssertionError("missing fake response")
        return self.response

    def close(self) -> None:
        self.closed = True


class SkillStateModelScoringTests(unittest.TestCase):
    def _case(self, groups: tuple[tuple[str, ...], ...]) -> StateCase:
        return StateCase(
            case_id="test",
            profile="standard",
            family="test",
            repository="example/repo",
            repository_commit="0" * 40,
            objective="test scorer",
            success=("evidence is matched",),
            observations=("FINAL: answer",),
            required_answer_groups=groups,
        )

    def test_separator_variation_is_normalized_without_semantic_expansion(self) -> None:
        self.assertEqual(normalize_evidence_text("Parser_transition"), "parser transition")
        self.assertTrue(evidence_contains("Supported cause: parser transition.", "parser-transition"))
        self.assertTrue(evidence_contains("SUPPORTED CAUSE: PARSER_TRANSITION", "parser-transition"))
        self.assertFalse(evidence_contains("Supported cause: parser transitioning.", "parser-transition"))

    def test_answer_scorer_accepts_harmless_separator_variation(self) -> None:
        result = score_answer(
            self._case((("parser-transition",), ("cache",), ("rejected",))),
            "The parser transition is supported; cache was rejected.",
        )
        self.assertTrue(result["answer_pass"])
        self.assertEqual(result["scorer_contract_version"], SCORER_CONTRACT_VERSION)

    def test_artifact_state_pointer_is_required_only_for_state_arms(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            cell = Path(temporary_directory)
            relative = Path("artifacts") / "evidence.json"
            path = cell / relative
            path.parent.mkdir(parents=True)
            payload = b'{"evidence":"frozen"}\n'
            path.write_bytes(payload)
            digest = hashlib.sha256(payload).hexdigest()
            pointer = f"{relative.as_posix()}#sha256={digest}"
            artifact = {
                "path": relative.as_posix(),
                "sha256": digest,
                "pointer": pointer,
            }

            non_state = artifact_integrity(cell, artifact, None)
            self.assertTrue(non_state["artifact_pass"])
            self.assertFalse(non_state["state_pointer_required"])
            self.assertIsNone(non_state["state_pointer_pass"])

            state = initial_state("audit", ["retain immutable evidence"])
            missing_pointer = artifact_integrity(cell, artifact, state)
            self.assertFalse(missing_pointer["artifact_pass"])
            self.assertTrue(missing_pointer["state_pointer_required"])

            state["history"] = {"required": True, "artifacts": [pointer]}
            with_pointer = artifact_integrity(cell, artifact, state)
            self.assertTrue(with_pointer["artifact_pass"])
            self.assertTrue(with_pointer["state_pointer_pass"])


class SkillStateCodexSseProfileTests(unittest.TestCase):
    def _source_request(self) -> bytes:
        return json.dumps(
            {
                "model": "gpt-test",
                "instructions": "frozen procedure",
                "input": [
                    {
                        "role": "user",
                        "content": [{"type": "input_text", "text": "current input"}],
                    }
                ],
                "store": False,
                "stream": False,
                "background": False,
                "truncation": "disabled",
                "max_output_tokens": 2048,
                "reasoning": {"effort": "medium"},
            },
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")

    def test_profile_manifest_is_self_consistent(self) -> None:
        manifest = wire_profile_contract_manifest(WIRE_PROFILE_CODEX_SSE)
        self.assertEqual(
            validate_wire_profile_contract_manifest(manifest),
            manifest,
        )
        changed = manifest["transformation"]["allowed_changed_fields"]
        self.assertEqual(
            changed,
            ["background", "max_output_tokens", "stream", "truncation"],
        )
        self.assertEqual(manifest["transformation"]["output_token_limit"], "provider-managed")

    def test_profile_changes_only_declared_wire_fields(self) -> None:
        prepared = prepare_profiled_request(
            self._source_request(),
            profile=WIRE_PROFILE_CODEX_SSE,
            endpoint=Endpoint.parse(DEFAULT_CODEX_RESPONSES_ENDPOINT),
            account_id_header_present=True,
        )
        source = json.loads(prepared.source_body)
        wire = json.loads(prepared.wire_body)
        self.assertTrue(wire["stream"])
        for field in ("background", "max_output_tokens", "truncation"):
            self.assertNotIn(field, wire)
        for key, value in source.items():
            if key not in {"background", "max_output_tokens", "stream", "truncation"}:
                self.assertEqual(wire[key], value)
        self.assertEqual(
            prepared.profile_audit["changed_fields"],
            ["background", "max_output_tokens", "stream", "truncation"],
        )
        self.assertEqual(prepared.profile_audit["output_token_limit"], "provider-managed")

    def test_sse_is_normalized_only_after_completed_event(self) -> None:
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
        response = {
            "id": "resp_1",
            "status": "completed",
            "model": "gpt-test",
            "store": False,
            "background": False,
            "truncation": "disabled",
            "output": [message],
            "usage": {
                "input_tokens": 12,
                "input_tokens_details": {"cached_tokens": 4},
                "output_tokens": 5,
                "total_tokens": 17,
            },
        }
        raw = (
            "event: response.output_item.done\n"
            f"data: {json.dumps({'type': 'response.output_item.done', 'item': message})}\n\n"
            "event: response.completed\n"
            f"data: {json.dumps({'type': 'response.completed', 'response': response})}\n\n"
        ).encode("utf-8")
        normalized, metadata = normalize_sse_response(raw)
        decoded = json.loads(normalized)
        self.assertEqual(decoded["output"], [message])
        self.assertEqual(decoded["usage"]["input_tokens"], 12)
        self.assertEqual(metadata["sse_completed_event_count"], 1)

        incomplete = (
            "event: response.output_item.done\n"
            f"data: {json.dumps({'type': 'response.output_item.done', 'item': message})}\n\n"
        ).encode("utf-8")
        with self.assertRaisesRegex(HostTransportError, "before response.completed"):
            normalize_sse_response(incomplete)

    def _completed_sse(self) -> bytes:
        message = {
            "type": "message",
            "role": "assistant",
            "content": [{"type": "output_text", "text": '{"state_patch":{},"action":"continue"}'}],
        }
        response = {
            "id": "resp_transport",
            "status": "completed",
            "model": "gpt-test",
            "store": False,
            "background": False,
            "truncation": "disabled",
            "output": [message],
            "usage": {"input_tokens": 1, "output_tokens": 1, "total_tokens": 2},
        }
        return (
            "event: response.output_item.done\n"
            f"data: {json.dumps({'type': 'response.output_item.done', 'item': message})}\n\n"
            "event: response.completed\n"
            f"data: {json.dumps({'type': 'response.completed', 'response': response})}\n\n"
        ).encode("utf-8")

    def test_exact_codex_transport_sends_and_records_final_wire_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            artifact_directory = Path(temporary_directory)
            fake = _FakeConnection(_FakeResponse(self._completed_sse()))
            transport = ExactResponsesTransport(
                api_key="test-token",
                endpoint=DEFAULT_CODEX_RESPONSES_ENDPOINT,
                trusted_endpoint_hosts=["chatgpt.com"],
                wire_profile=WIRE_PROFILE_CODEX_SSE,
                codex_account_id="workspace-test",
                artifact_directory=artifact_directory,
            )
            transport._connection = lambda: fake  # type: ignore[method-assign]
            response = transport(self._source_request())
            self.assertEqual(response.status_code, 200)
            self.assertTrue(fake.closed)
            self.assertIsNotNone(fake.request_body)
            wire = json.loads(fake.request_body or b"{}")
            self.assertTrue(wire["stream"])
            self.assertNotIn("background", wire)
            self.assertNotIn("max_output_tokens", wire)
            self.assertNotIn("truncation", wire)
            self.assertEqual(fake.request_headers["ChatGPT-Account-ID"], "workspace-test")
            self.assertEqual(fake.request_headers["originator"], "codex_cli_rs")
            audit = dict(transport.last_audit or {})
            self.assertEqual(audit["source_to_wire_changed_fields"], [
                "background", "max_output_tokens", "stream", "truncation"
            ])
            self.assertTrue((artifact_directory / "request-0001.source.json").is_file())
            self.assertTrue((artifact_directory / "request-0001.wire.json").is_file())
            self.assertTrue((artifact_directory / "request-0001.response.raw.sse").is_file())
            self.assertTrue((artifact_directory / "request-0001.response.normalized.json").is_file())
            self.assertTrue((artifact_directory / "request-0001.transport-audit.json").is_file())

    def test_history_free_final_wire_audit_passes_against_frozen_host_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            artifact_directory = Path(temporary_directory)
            state = initial_state("retain current fact", ["transition remains valid"])
            host = HistoryFreeHost(
                model="gpt-test",
                procedure="Execute one frozen test transition.",
                options={
                    "max_output_tokens": 64,
                    "reasoning": {"effort": "medium"},
                },
            )
            source = host.prepare_request(state, "current observation").wire_bytes
            fake = _FakeConnection(_FakeResponse(self._completed_sse()))
            transport = ExactResponsesTransport(
                api_key="test-token",
                endpoint=DEFAULT_CODEX_RESPONSES_ENDPOINT,
                trusted_endpoint_hosts=["chatgpt.com"],
                wire_profile=WIRE_PROFILE_CODEX_SSE,
                codex_account_id="workspace-test",
                artifact_directory=artifact_directory,
                manifest=host.manifest(),
            )
            transport._connection = lambda: fake  # type: ignore[method-assign]
            transport(source)
            audit = dict(transport.last_audit or {})
            self.assertTrue(audit["manifest_match"])
            self.assertTrue(audit["bounded_context_eligible"])
            self.assertTrue(audit["wire_profile_manifest_match"])
            self.assertTrue(audit["final_wire_contract_pass"])
            self.assertTrue(transport_audit_passes(audit))

    def test_connection_failure_keeps_attempted_final_wire_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            artifact_directory = Path(temporary_directory)
            fake = _FakeConnection(failure=OSError("connection closed"))
            transport = ExactResponsesTransport(
                api_key="test-token",
                endpoint=DEFAULT_CODEX_RESPONSES_ENDPOINT,
                trusted_endpoint_hosts=["chatgpt.com"],
                wire_profile=WIRE_PROFILE_CODEX_SSE,
                codex_account_id="workspace-test",
                artifact_directory=artifact_directory,
            )
            transport._connection = lambda: fake  # type: ignore[method-assign]
            with self.assertRaisesRegex(HostTransportError, "connection closed"):
                transport(self._source_request())
            self.assertTrue((artifact_directory / "request-0001.source.json").is_file())
            self.assertTrue((artifact_directory / "request-0001.wire.json").is_file())
            audit_path = artifact_directory / "request-0001.transport-audit.json"
            self.assertTrue(audit_path.is_file())
            audit = json.loads(audit_path.read_text(encoding="utf-8"))
            self.assertIn("connection closed", audit["transport_failure"])
            self.assertIsNone(audit["response_body_sha256"])

    def test_codex_auth_loader_reads_account_id_from_raw_id_token(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "auth.json"
            header = base64.urlsafe_b64encode(b'{"alg":"none"}').rstrip(b"=").decode()
            payload = base64.urlsafe_b64encode(
                json.dumps(
                    {
                        "https://api.openai.com/auth": {
                            "chatgpt_account_id": "workspace-from-jwt"
                        }
                    },
                    separators=(",", ":"),
                ).encode("utf-8")
            ).rstrip(b"=").decode()
            token = f"{header}.{payload}.signature"
            path.write_text(
                json.dumps(
                    {
                        "tokens": {
                            "access_token": "test-access-token",
                            "id_token": token,
                            "refresh_token": "must-not-be-used",
                            "account_id": None,
                        }
                    }
                ),
                encoding="utf-8",
            )
            credentials = load_codex_credentials(path)
            self.assertEqual(credentials.account_id, "workspace-from-jwt")

    def test_codex_auth_loader_reads_nested_account_id_without_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "auth.json"
            original: dict[str, Any] = {
                "auth_mode": "chatgpt",
                "tokens": {
                    "access_token": "test-access-token",
                    "id_token": {
                        "chatgpt_account_id": "workspace-test",
                        "raw_jwt": "header.payload.signature",
                    },
                    "refresh_token": "must-not-be-used",
                },
            }
            encoded = json.dumps(original, indent=2) + "\n"
            path.write_text(encoded, encoding="utf-8")
            before = path.read_bytes()
            credentials = load_codex_credentials(path)
            self.assertEqual(credentials.access_token, "test-access-token")
            self.assertEqual(credentials.account_id, "workspace-test")
            self.assertEqual(path.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()

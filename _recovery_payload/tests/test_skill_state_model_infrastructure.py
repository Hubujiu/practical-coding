from __future__ import annotations

import json
import os
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from benchmarks import skill_state_model_analysis as analysis
from benchmarks import skill_state_model_cases as cases
from benchmarks import skill_state_model_runner as runner
from runtime.skill_state_http_transport import (
    ExactByteHTTPTransport,
    TransportAuditError,
)


class _Handler(BaseHTTPRequestHandler):
    body = b""
    headers_seen: dict[str, str] = {}

    def do_POST(self) -> None:  # noqa: N802
        length = int(self.headers["Content-Length"])
        type(self).body = self.rfile.read(length)
        type(self).headers_seen = dict(self.headers.items())
        response = {
            "id": "resp_test",
            "status": "completed",
            "output": [
                {
                    "type": "message",
                    "role": "assistant",
                    "content": [
                        {"type": "output_text", "text": '{"tool":"continue"}'}
                    ],
                }
            ],
            "usage": {
                "input_tokens": 10,
                "input_tokens_details": {"cached_tokens": 2},
                "output_tokens": 3,
                "total_tokens": 13,
            },
        }
        payload = json.dumps(response, separators=(",", ":")).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Set-Cookie", "ignored=test")
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, format: str, *args: object) -> None:
        return


class SkillStateHTTPTransportTests(unittest.TestCase):
    def setUp(self) -> None:
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=5)

    def test_transport_sends_exact_body_without_cookie_or_context_header(self) -> None:
        endpoint = f"http://127.0.0.1:{self.server.server_port}/v1/responses"
        transport = ExactByteHTTPTransport(
            endpoint=endpoint,
            api_key="test-key",
            allow_insecure_http=True,
        )
        body = b'{"model":"test","input":[]}'
        response = transport(body)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(_Handler.body, body)
        audit = transport.audits[-1]
        self.assertTrue(audit["body_bytes_sent_unchanged"])
        self.assertTrue(audit["client_context_audit_pass"])
        self.assertFalse(audit["request_cookie_present"])
        self.assertEqual(audit["contextual_header_names"], ())
        self.assertTrue(audit["response_set_cookie_present"])
        self.assertNotIn("Cookie", _Handler.headers_seen)
        self.assertTrue(audit["environment_proxy_bypassed"])

    def test_context_bearing_extra_header_is_rejected(self) -> None:
        with self.assertRaises(TransportAuditError):
            ExactByteHTTPTransport(
                api_key="test-key",
                extra_headers={"X-Session-Id": "history"},
            )


class SkillStateModelCaseTests(unittest.TestCase):
    def test_frozen_profiles_cover_required_horizons_and_mechanisms(self) -> None:
        cases.self_test()
        self.assertEqual(
            {case.horizon for case in cases.BOUNDED_CASES},
            set(cases.BOUNDED_HORIZONS),
        )
        families = {case.family for case in cases.STANDARD_CASES}
        self.assertIn("corrective-observation", families)
        self.assertIn("history-required-control", families)
        self.assertIn("coordinated-implementation", families)


class SkillStateModelRunnerTests(unittest.TestCase):
    def test_action_contract_rejects_early_finish_and_extra_keys(self) -> None:
        self.assertEqual(
            runner.parse_action('{"tool":"continue"}', final_step=False),
            {"tool": "continue"},
        )
        with self.assertRaises(runner.ModelRunnerError):
            runner.parse_action(
                '{"tool":"finish","answer":"early"}', final_step=False
            )
        with self.assertRaises(runner.ModelRunnerError):
            runner.parse_action(
                '{"tool":"continue","command":"unsafe"}', final_step=False
            )

    def test_arm_order_rotates_deterministically(self) -> None:
        case = cases.STANDARD_CASES[0]
        specs = runner.build_specs((case,), 4, runner.ARMS)
        orders = []
        for repetition in range(1, 5):
            orders.append(
                [arm for _, arm, current in specs if current == repetition]
            )
        self.assertEqual(orders[0], list(runner.ARMS))
        self.assertEqual(orders[1], list(runner.ARMS[1:] + runner.ARMS[:1]))
        self.assertEqual(len({tuple(value) for value in orders}), 4)

    def test_dry_run_does_not_require_api_key_or_send_requests(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            output = Path(temporary_directory) / "dry-run"
            old = os.environ.pop("MISSING_TEST_API_KEY", None)
            try:
                result = runner.main(
                    [
                        "--profile",
                        "standard",
                        "--case",
                        cases.STANDARD_CASES[0].case_id,
                        "--runs",
                        "1",
                        "--workers",
                        "1",
                        "--api-key-env",
                        "MISSING_TEST_API_KEY",
                        "--output",
                        str(output),
                        "--dry-run",
                    ]
                )
            finally:
                if old is not None:
                    os.environ["MISSING_TEST_API_KEY"] = old
            self.assertEqual(result, 0)
            manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(len(manifest["expected_cells"]), 4)
            self.assertFalse((output / "results.jsonl").exists())


class SkillStateModelAnalysisTests(unittest.TestCase):
    def test_missing_and_indeterminate_cells_never_pass_matrix_gate(self) -> None:
        manifest = {
            "expected_cells": [
                {"case_id": "case", "arm": arm, "repetition": 1}
                for arm in runner.ARMS
            ]
        }
        rows = [
            {
                "case_id": "case",
                "arm": "full-history",
                "repetition": 1,
                "passed": True,
            }
        ]
        self.assertEqual(
            analysis.matrix_report(rows, [manifest])["status"],
            "FAIL",
        )
        rows.extend(
            {
                "case_id": "case",
                "arm": arm,
                "repetition": 1,
                "passed": None if arm == "state-history-free" else True,
            }
            for arm in runner.ARMS[1:]
        )
        report = analysis.matrix_report(rows, [manifest])
        self.assertEqual(report["status"], "FAIL")
        self.assertEqual(len(report["indeterminate"]), 1)

    def test_latency_gate_requires_serial_workers(self) -> None:
        rows = []
        for arm, seconds in (("full-history", 10.0), ("state-history-free", 5.0)):
            rows.append(
                {
                    "case_id": "case",
                    "arm": arm,
                    "repetition": 1,
                    "passed": True,
                    "end_to_end_seconds": seconds,
                }
            )
        report = analysis.cost_report(
            rows,
            key="end_to_end_seconds",
            ratio_limit=0.9,
            workers={8},
            require_serial=True,
        )
        self.assertEqual(report["status"], "PENDING")

    def test_bounded_gate_requires_all_frozen_horizons(self) -> None:
        report = analysis.bounded_report([], {"status": "PASS"})
        self.assertEqual(report["status"], "FAIL")
        self.assertEqual(
            report["missing_horizons"],
            list(cases.BOUNDED_HORIZONS),
        )


if __name__ == "__main__":
    unittest.main()

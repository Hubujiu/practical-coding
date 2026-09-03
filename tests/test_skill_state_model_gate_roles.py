from __future__ import annotations

import copy
import unittest

from benchmarks import skill_state_model_analysis as analysis
from benchmarks.skill_state_model_cases import (
    ARM_STATE_HISTORY_FREE,
    ARM_STATE_SHADOW,
)


class SkillStateModelGateRoleTests(unittest.TestCase):
    def test_shadow_failure_is_diagnostic_not_candidate_blocking(self) -> None:
        rows = analysis.synthetic_rows()
        shadow = next(
            row
            for row in rows
            if row["profile"] == "standard" and row["arm"] == ARM_STATE_SHADOW
        )
        shadow["passed"] = False
        shadow["verdict"] = "fail"
        shadow["state_score"] = {
            "state_pass": False,
            "state_mechanism_failures": ["synthetic shadow-only failure"],
        }

        result = analysis.analyze(rows, samples=20)

        self.assertEqual(result["gates"]["quality_gate"]["status"], analysis.PASS)
        self.assertEqual(
            result["gates"]["state_semantic_gate"]["status"], analysis.PASS
        )
        self.assertEqual(
            result["gates"]["history_free_candidate_gate"]["status"],
            analysis.PASS,
        )
        self.assertEqual(
            result["gates"]["state_shadow_diagnostic"]["status"],
            analysis.FAIL,
        )
        self.assertFalse(result["gates"]["state_shadow_diagnostic"]["blocking"])

    def test_history_free_failure_remains_blocking(self) -> None:
        rows = analysis.synthetic_rows()
        candidate = next(
            row
            for row in rows
            if row["profile"] == "standard"
            and row["arm"] == ARM_STATE_HISTORY_FREE
        )
        candidate["passed"] = False
        candidate["verdict"] = "fail"
        candidate["state_score"] = {
            "state_pass": False,
            "state_mechanism_failures": ["synthetic candidate failure"],
        }

        result = analysis.analyze(rows, samples=20)

        self.assertEqual(result["gates"]["quality_gate"]["status"], analysis.FAIL)
        self.assertEqual(
            result["gates"]["state_semantic_gate"]["status"], analysis.FAIL
        )
        self.assertEqual(
            result["gates"]["history_free_candidate_gate"]["status"],
            analysis.FAIL,
        )

    def test_n1_is_iteration_evidence_not_formal_release_evidence(self) -> None:
        result = analysis.analyze(analysis.synthetic_rows(), samples=20)

        self.assertEqual(
            result["gates"]["release_repetition_gate"]["status"],
            analysis.PENDING,
        )
        self.assertEqual(result["gates"]["token_gate"]["status"], analysis.PENDING)
        self.assertIn(
            "iteration_estimate",
            result["gates"]["token_gate"],
        )
        self.assertEqual(result["gates"]["latency_gate"]["status"], analysis.PENDING)
        self.assertEqual(
            result["gates"]["execution_state_model_gate"],
            analysis.PENDING,
        )

    def test_complete_paired_standard_n3_satisfies_repetition_gate(self) -> None:
        rows = []
        for row in analysis.synthetic_rows():
            if row["profile"] != "standard":
                continue
            for repetition in (1, 2, 3):
                clone = copy.deepcopy(row)
                clone["repetition"] = repetition
                rows.append(clone)

        gate = analysis.release_repetition_gate(rows)

        self.assertEqual(gate["status"], analysis.PASS)
        self.assertEqual(gate["minimum_runs"], 3)
        self.assertFalse(gate["issues"])

    def test_unpaired_or_indeterminate_standard_matrix_stays_pending(self) -> None:
        rows = []
        for row in analysis.synthetic_rows():
            if row["profile"] != "standard":
                continue
            for repetition in (1, 2, 3):
                clone = copy.deepcopy(row)
                clone["repetition"] = repetition
                rows.append(clone)

        case_ids = list(analysis.EXPECTED_STANDARD_CASE_IDS)
        self.assertGreaterEqual(len(case_ids), 2)
        unpaired_case, indeterminate_case = case_ids[:2]
        rows = [
            row
            for row in rows
            if not (
                row["arm"] == ARM_STATE_SHADOW
                and row["case_id"] == unpaired_case
                and row["repetition"] == 3
            )
        ]
        candidate = next(
            row
            for row in rows
            if row["arm"] == ARM_STATE_HISTORY_FREE
            and row["case_id"] == indeterminate_case
            and row["repetition"] == 2
        )
        candidate["passed"] = None
        candidate["verdict"] = "indeterminate"

        gate = analysis.release_repetition_gate(rows)

        self.assertEqual(gate["status"], analysis.PENDING)
        reasons = {issue["reason"] for issue in gate["issues"]}
        self.assertIn("insufficient repetitions", reasons)
        self.assertIn("arm repetition sets are not paired", reasons)
        self.assertIn("indeterminate cells", reasons)

    def test_markdown_exposes_shadow_as_nonblocking(self) -> None:
        result = analysis.analyze(analysis.synthetic_rows(), samples=20)
        report = analysis.markdown(result)

        self.assertIn("State-shadow diagnostics", report)
        self.assertIn("diagnostic only", report)
        self.assertIn("standard n>=3", report)


if __name__ == "__main__":
    unittest.main()

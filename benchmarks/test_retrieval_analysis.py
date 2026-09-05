from __future__ import annotations

import unittest

from benchmarks import retrieval_analysis as analysis


def row(task, variant, passed, *, selected=None, repetition=1, violation=False):
    return {
        "task_id": task,
        "variant": variant,
        "repetition": repetition,
        "passed": passed,
        "selected_retrieval": selected,
        "capability_usage": {},
        "measurement_phase": "measured",
        "setup_included_in_comparison": False,
        "measured_setup_violation": violation,
    }


class RetrievalAnalysisTests(unittest.TestCase):
    def test_shallowest_stable_passing_ceiling_is_minimum(self) -> None:
        rows = [
            row("t", "retrieval-cap:NONE", False),
            row("t", "retrieval-cap:R0_DIRECT", False),
            row("t", "retrieval-cap:R1_DISCOVERY", True),
            row("t", "retrieval-cap:R2_EVIDENCE", True),
            row("t", "retrieval-cap:R3_STRUCTURAL", True),
            row("t", "adaptive", True, selected="R1_DISCOVERY"),
        ]
        report = analysis.analyze(rows)
        self.assertEqual(report["tasks"]["t"]["minimum_sufficient_retrieval_stage"], "R1_DISCOVERY")
        self.assertEqual(report["adaptive_relation_counts"], {"exact_minimum": 1})

    def test_any_failed_repetition_prevents_stable_pass(self) -> None:
        rows = [
            row("t", "retrieval-cap:NONE", False, repetition=1),
            row("t", "retrieval-cap:NONE", False, repetition=2),
            row("t", "retrieval-cap:R0_DIRECT", False, repetition=1),
            row("t", "retrieval-cap:R0_DIRECT", False, repetition=2),
            row("t", "retrieval-cap:R1_DISCOVERY", True, repetition=1),
            row("t", "retrieval-cap:R1_DISCOVERY", False, repetition=2),
            row("t", "retrieval-cap:R2_EVIDENCE", True, repetition=1),
            row("t", "retrieval-cap:R2_EVIDENCE", True, repetition=2),
            row("t", "adaptive", True, selected="R1_DISCOVERY", repetition=1),
        ]
        report = analysis.analyze(rows)
        self.assertEqual(report["tasks"]["t"]["minimum_sufficient_retrieval_stage"], "R2_EVIDENCE")
        self.assertEqual(report["adaptive_relation_counts"], {"under_disclosure": 1})

    def test_missing_repetition_prevents_a_false_shallow_minimum(self) -> None:
        rows = [
            row("t", "retrieval-cap:NONE", False, repetition=1),
            row("t", "retrieval-cap:NONE", False, repetition=2),
            row("t", "retrieval-cap:R0_DIRECT", False, repetition=1),
            row("t", "retrieval-cap:R0_DIRECT", False, repetition=2),
            row("t", "retrieval-cap:R1_DISCOVERY", True, repetition=1),
            row("t", "retrieval-cap:R2_EVIDENCE", True, repetition=1),
            row("t", "retrieval-cap:R2_EVIDENCE", True, repetition=2),
            row("t", "retrieval-cap:R3_STRUCTURAL", True, repetition=1),
            row("t", "retrieval-cap:R3_STRUCTURAL", True, repetition=2),
            row("t", "adaptive", True, selected="R2_EVIDENCE", repetition=1),
        ]
        report = analysis.analyze(rows)
        # Missing R1/r2 cannot establish that R1 failed; R2 is not proven minimal.
        self.assertIsNone(report["tasks"]["t"]["minimum_sufficient_retrieval_stage"])
        self.assertEqual(report["adaptive_relation_counts"], {"minimum_unresolved": 1})
        self.assertFalse(report["tasks"]["t"]["stable_ceiling_pass"]["R1_DISCOVERY"])

    def test_no_passing_ceiling_is_quality_gap(self) -> None:
        rows = [row("t", f"retrieval-cap:{stage}", False) for stage in analysis.STAGES]
        rows.append(row("t", "adaptive", True, selected="R3_STRUCTURAL"))
        report = analysis.analyze(rows)
        self.assertIsNone(report["tasks"]["t"]["minimum_sufficient_retrieval_stage"])
        self.assertEqual(report["adaptive_relation_counts"], {"quality_gap": 1})

    def test_setup_violation_is_visible(self) -> None:
        report = analysis.analyze([row("t", "adaptive", False, selected="R0_DIRECT", violation=True)])
        self.assertEqual(report["setup_measurement_contract_violation_count"], 1)


if __name__ == "__main__":
    unittest.main()

import unittest

from benchmarks.ladder_analysis import analyze, validate_record


class LadderAnalysisTests(unittest.TestCase):
    def test_classifies_execution_boundaries(self):
        records = [
            {"task_id": "exact", "axis": "execution", "arm": "cap", "level": "E0", "qualified": False},
            {"task_id": "exact", "axis": "execution", "arm": "cap", "level": "E1", "qualified": True},
            {"task_id": "exact", "axis": "execution", "arm": "adaptive", "level": "E1", "qualified": True},
            {"task_id": "over", "axis": "execution", "arm": "cap", "level": "E0", "qualified": True},
            {"task_id": "over", "axis": "execution", "arm": "adaptive", "level": "E2", "qualified": True},
            {"task_id": "under", "axis": "execution", "arm": "cap", "level": "E0", "qualified": False},
            {"task_id": "under", "axis": "execution", "arm": "cap", "level": "E2", "qualified": True},
            {"task_id": "under", "axis": "execution", "arm": "adaptive", "level": "E1", "qualified": False},
        ]
        report = analyze(records)["axes"]["execution"]
        self.assertEqual(report["status_counts"]["exact"], 1)
        self.assertEqual(report["status_counts"]["over_escalation"], 1)
        self.assertEqual(report["status_counts"]["under_escalation"], 1)
        self.assertEqual(report["minimum_sufficient_counts"]["E0"], 1)
        self.assertEqual(report["minimum_sufficient_counts"]["E1"], 1)
        self.assertEqual(report["minimum_sufficient_counts"]["E2"], 1)

    def test_reports_levels_never_minimum(self):
        records = [
            {"task_id": "r", "axis": "retrieval", "arm": "cap", "level": "R1", "qualified": True},
            {"task_id": "r", "axis": "retrieval", "arm": "adaptive", "level": "R1", "qualified": True},
        ]
        report = analyze(records)["axes"]["retrieval"]
        self.assertIn("R0", report["levels_never_minimum"])
        self.assertNotIn("R1", report["levels_never_minimum"])
        self.assertIn("R3", report["levels_never_minimum"])

    def test_reports_end_to_end_rates_without_hiding_quality_failures(self):
        records = [
            {"task_id": "exact", "axis": "execution", "arm": "cap", "level": "E0", "qualified": True},
            {"task_id": "exact", "axis": "execution", "arm": "adaptive", "level": "E0", "qualified": True},
            {"task_id": "failed", "axis": "execution", "arm": "cap", "level": "E0", "qualified": True},
            {"task_id": "failed", "axis": "execution", "arm": "adaptive", "level": "E0", "qualified": False},
        ]
        report = analyze(records)["axes"]["execution"]
        self.assertEqual(report["exact_rate"], 1.0)
        self.assertEqual(report["qualified_adaptive_rate"], 0.5)
        self.assertEqual(report["overall_exact_rate"], 0.5)
        self.assertEqual(report["quality_failure_rate"], 0.5)

    def test_averages_qualified_cap_cost(self):
        records = [
            {"task_id": "a", "axis": "execution", "arm": "cap", "level": "E0", "qualified": True, "tokens": 100},
            {"task_id": "a", "axis": "execution", "arm": "adaptive", "level": "E0", "qualified": True},
            {"task_id": "b", "axis": "execution", "arm": "cap", "level": "E0", "qualified": True, "tokens": 300},
            {"task_id": "b", "axis": "execution", "arm": "adaptive", "level": "E0", "qualified": True},
        ]
        report = analyze(records)["axes"]["execution"]
        self.assertEqual(report["qualified_cap_cost_by_level"]["E0"]["tokens"], 200)

    def test_summarizes_capability_path_and_references(self):
        records = [
            {"task_id": "state-bug", "axis": "execution", "arm": "cap", "level": "E3", "qualified": True},
            {
                "task_id": "state-bug",
                "axis": "execution",
                "arm": "adaptive",
                "level": "E3",
                "qualified": True,
                "capability_path": ["diagnosis", "state"],
                "references_loaded": ["references/debugging.md", "references/specialists/state.md"],
            },
        ]
        report = analyze(records)["axes"]["execution"]
        self.assertEqual(report["adaptive_capability_path_counts"]["diagnosis>state"], 1)
        self.assertEqual(report["qualified_adaptive_capability_path_counts"]["diagnosis>state"], 1)
        self.assertEqual(report["adaptive_reference_load_counts"]["references/debugging.md"], 1)
        self.assertEqual(report["cases"][0]["adaptive_capability_path"], "diagnosis>state")

    def test_rejects_invalid_level(self):
        with self.assertRaises(ValueError):
            validate_record({"task_id": "x", "axis": "execution", "arm": "cap", "level": "R0", "qualified": True})

    def test_rejects_removed_r4(self):
        with self.assertRaises(ValueError):
            validate_record({"task_id": "x", "axis": "retrieval", "arm": "cap", "level": "R4", "qualified": True})

    def test_rejects_invalid_capability_path_type(self):
        with self.assertRaises(ValueError):
            validate_record({
                "task_id": "x",
                "axis": "execution",
                "arm": "adaptive",
                "level": "E2",
                "qualified": True,
                "capability_path": {"root": "engineering"},
            })


if __name__ == "__main__":
    unittest.main()

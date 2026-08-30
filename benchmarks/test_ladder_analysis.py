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

    def test_averages_qualified_cap_cost(self):
        records = [
            {"task_id": "a", "axis": "execution", "arm": "cap", "level": "E0", "qualified": True, "tokens": 100},
            {"task_id": "a", "axis": "execution", "arm": "adaptive", "level": "E0", "qualified": True},
            {"task_id": "b", "axis": "execution", "arm": "cap", "level": "E0", "qualified": True, "tokens": 300},
            {"task_id": "b", "axis": "execution", "arm": "adaptive", "level": "E0", "qualified": True},
        ]
        report = analyze(records)["axes"]["execution"]
        self.assertEqual(report["qualified_cap_cost_by_level"]["E0"]["tokens"], 200)

    def test_rejects_invalid_level(self):
        with self.assertRaises(ValueError):
            validate_record({"task_id": "x", "axis": "execution", "arm": "cap", "level": "R0", "qualified": True})


if __name__ == "__main__":
    unittest.main()

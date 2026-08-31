import unittest

from benchmarks.release_comparison import _historical_reasoning, _metric_gate


class ReleaseComparisonTests(unittest.TestCase):
    def test_maps_legacy_event_axes_to_active_reasoning(self):
        self.assertEqual(
            _historical_reasoning({"actual_decision": "REQUIRED", "actual_execution": "BLOCKED", "actual_retrieval": "NONE"}),
            ("DECISION", "NONE"),
        )
        self.assertEqual(
            _historical_reasoning({"actual_decision": "CLEAR", "actual_execution": "DEBUGGING", "actual_retrieval": "BOUNDED"}),
            ("DEBUGGING", "BOUNDED"),
        )
        self.assertEqual(
            _historical_reasoning({"actual_decision": "CLEAR", "actual_execution": "DIRECT", "actual_retrieval": "TARGETED"}),
            ("NONE", "TARGETED"),
        )

    def test_gate_rejects_quality_or_cost_regression(self):
        previous = {"pass_rate": 1.0, "uncached_input_tokens_median": 100.0, "duration_seconds_median": 10.0}
        quality = _metric_gate({"pass_rate": 0.9, "uncached_input_tokens_median": 90.0, "duration_seconds_median": 9.0}, previous)
        cost = _metric_gate({"pass_rate": 1.0, "uncached_input_tokens_median": 110.0, "duration_seconds_median": 9.0}, previous)
        self.assertFalse(quality["passed"])
        self.assertFalse(cost["passed"])

    def test_gate_accepts_equal_quality_and_lower_cost(self):
        previous = {"pass_rate": 1.0, "uncached_input_tokens_median": 100.0, "duration_seconds_median": 10.0}
        current = {"pass_rate": 1.0, "uncached_input_tokens_median": 90.0, "duration_seconds_median": 9.0}
        self.assertTrue(_metric_gate(current, previous)["passed"])


if __name__ == "__main__":
    unittest.main()

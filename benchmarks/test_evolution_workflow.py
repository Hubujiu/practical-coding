from __future__ import annotations

import unittest

from benchmarks import evolution_workflow_validation as evolution


class EvolutionWorkflowTests(unittest.TestCase):
    def test_contract_score_is_perfect(self) -> None:
        report = evolution.evaluate()
        self.assertEqual(report["score"], 1.0, report["checks"])


if __name__ == "__main__":
    unittest.main()

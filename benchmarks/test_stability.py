import unittest

from benchmarks import check_stability as gate


def record(repetition, *, error=None):
    item = {
        "suite": "delivery",
        "case": "tmpl-fe-command",
        "arm": "practical-current",
        "repetition": repetition,
        "passed": False,
    }
    if error is not None:
        item["error"] = error
    return item


class StabilityGateTests(unittest.TestCase):
    def test_n1_is_provisional(self):
        stable, reasons, rows = gate.assess_run(
            {"completed_at": "2026-08-24T00:00:00Z", "cells": 1},
            [record(1)],
        )
        self.assertFalse(stable)
        self.assertEqual(rows[0]["runs"], 1)
        self.assertTrue(any("n=1 < 3" in reason for reason in reasons))

    def test_three_distinct_repetitions_are_stable(self):
        stable, reasons, rows = gate.assess_run(
            {"completed_at": "2026-08-24T00:00:00Z", "cells": 3},
            [record(1), record(2), record(3)],
        )
        self.assertTrue(stable)
        self.assertEqual(reasons, [])
        self.assertTrue(rows[0]["stable"])

    def test_duplicate_repetition_does_not_inflate_n(self):
        stable, reasons, rows = gate.assess_run(
            {"completed_at": "2026-08-24T00:00:00Z", "cells": 3},
            [record(1), record(1), record(2)],
        )
        self.assertFalse(stable)
        self.assertEqual(rows[0]["runs"], 2)
        self.assertTrue(any("duplicate repetitions" in reason for reason in reasons))

    def test_infrastructure_error_blocks_stable_ranking(self):
        stable, reasons, rows = gate.assess_run(
            {"completed_at": "2026-08-24T00:00:00Z", "cells": 3},
            [record(1), record(2, error="timeout"), record(3)],
        )
        self.assertFalse(stable)
        self.assertEqual(rows[0]["infrastructure_errors"], 1)
        self.assertTrue(any("infrastructure error" in reason for reason in reasons))

    def test_indeterminate_verdict_blocks_stable_ranking(self):
        cells = [record(1), record(2), record(3)]
        cells[1].update({"passed": None, "verdict": "indeterminate", "indeterminate_reason": "build OOM"})
        stable, reasons, rows = gate.assess_run(
            {"completed_at": "2026-08-24T00:00:00Z", "cells": 3},
            cells,
        )
        self.assertFalse(stable)
        self.assertEqual(rows[0]["infrastructure_errors"], 1)
        self.assertTrue(any("infrastructure error" in reason for reason in reasons))

    def test_incomplete_run_is_not_stable(self):
        stable, reasons, _ = gate.assess_run(
            {"cells": 3},
            [record(1), record(2), record(3)],
        )
        self.assertFalse(stable)
        self.assertTrue(any("run is incomplete" in reason for reason in reasons))


if __name__ == "__main__":
    unittest.main()

import tempfile
import unittest
from pathlib import Path

from benchmarks import run_benchmarks as bench
from benchmarks import run_catalog
from benchmarks.case_catalog import (
    EXTRA_DEBUG_CASES,
    EXTRA_DECISION_CASES,
    EXTRA_ROUTER_CASES,
    install,
    score_extra_debug,
)
from benchmarks.debug_oracles import DEBUG_ORACLES


class ExpandedCatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        install(bench)

    def test_public_matrix_is_materially_broader(self):
        self.assertEqual(len(bench.ROUTER_CASES), 28)
        self.assertEqual(len(bench.DECISION_CASES), 10)
        self.assertEqual(len(bench.PROFILE_CASES["standard"]["decision"]), 6)
        self.assertEqual(len(bench.PROFILE_CASES["full"]["decision"]), 10)
        self.assertEqual(len(bench.PROFILE_CASES["standard"]["debug"]), 8)
        self.assertEqual(len(bench.PROFILE_CASES["full"]["debug"]), 12)

    def test_expansion_is_not_just_one_route_or_bug_shape(self):
        extra_routes = {expected for expected, _ in EXTRA_ROUTER_CASES.values()}
        self.assertEqual(
            extra_routes,
            {"DIRECT", "DECISION", "DEBUGGING", "IMPLEMENTATION", "EXPLORATION", "VERIFICATION"},
        )
        self.assertEqual(len({case["score"] for case in EXTRA_DEBUG_CASES.values()}), len(EXTRA_DEBUG_CASES))
        self.assertGreaterEqual(len(EXTRA_DECISION_CASES), 6)

    def test_profiles_have_no_duplicate_case_ids(self):
        for profile in ("standard", "full"):
            for suite in ("router", "decision", "debug"):
                cases = bench.PROFILE_CASES[profile][suite]
                self.assertEqual(len(cases), len(set(cases)), f"duplicates in {profile}/{suite}")

    def test_each_debug_seed_fails_and_oracle_passes(self):
        self.assertEqual(set(EXTRA_DEBUG_CASES), set(DEBUG_ORACLES))
        for case, spec in EXTRA_DEBUG_CASES.items():
            with self.subTest(case=case), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                for name, content in spec["files"].items():
                    (root / name).write_text(content, encoding="utf-8")
                seeded = score_extra_debug(case, root)
                self.assertFalse(seeded["correct"] == 1 and seeded["safe"] == 1)

                for name, content in DEBUG_ORACLES[case].items():
                    (root / name).write_text(content, encoding="utf-8")
                oracle = score_extra_debug(case, root)
                self.assertEqual((oracle["correct"], oracle["safe"]), (1, 1), oracle["reason"])

    def test_decision_cases_have_two_turn_resolution_contract(self):
        for case, spec in bench.DECISION_CASES.items():
            with self.subTest(case=case):
                self.assertTrue(spec["prompt"].strip())
                self.assertIn("Resolve the decision now", spec["reply"])
                self.assertTrue(spec["expected"])

    def test_canonical_runner_fingerprint_includes_catalog(self):
        raw_core = bench.sha256(Path(bench.__file__))
        bundled = run_catalog.runner_bundle_sha256()
        self.assertEqual(len(bundled), 64)
        self.assertNotEqual(bundled, raw_core)
        self.assertEqual(
            run_catalog.catalog_aware_sha256(Path(run_catalog.bench.__file__)),
            bundled,
        )


if __name__ == "__main__":
    unittest.main()

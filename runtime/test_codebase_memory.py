#!/usr/bin/env python3
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

RUNTIME = Path(__file__).with_name("codebase_memory.py")


class EmbeddedGraphRuntimeTest(unittest.TestCase):
    def run_cli(self, repo: Path, *args: str):
        p = subprocess.run(
            [sys.executable, str(RUNTIME), "--repo", str(repo), *args],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(p.returncode, 0, p.stderr)
        return json.loads(p.stdout)

    def test_index_trace_impact_and_incremental_refresh(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
            (repo / "a.py").write_text(
                "from b import helper\n\ndef main():\n    return helper()\n",
                encoding="utf-8",
            )
            (repo / "b.py").write_text(
                "def helper():\n    return 1\n",
                encoding="utf-8",
            )

            first = self.run_cli(repo, "index")
            self.assertEqual(first["changed_files"], 2)
            self.assertEqual(first["totals"]["call_edges"], 1)

            trace = self.run_cli(repo, "trace", "helper", "--direction", "in")
            self.assertEqual(trace["edges"][0]["from"], "a.py.main")

            impact = self.run_cli(repo, "impact", "--files", "b.py")
            self.assertTrue(any(x.get("symbol") == "a.py.main" for x in impact["affected"]))

            second = self.run_cli(repo, "index")
            self.assertEqual(second["changed_files"], 0)
            self.assertEqual(second["unchanged_files"], 2)

    def test_read_only_query_guard(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
            (repo / "a.py").write_text("def f():\n    return 1\n", encoding="utf-8")
            self.run_cli(repo, "index")
            ok = self.run_cli(repo, "query", "SELECT name FROM symbols")
            self.assertEqual(ok["rows"][0]["name"], "f")

            p = subprocess.run(
                [sys.executable, str(RUNTIME), "--repo", str(repo), "query", "DELETE FROM symbols"],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            self.assertNotEqual(p.returncode, 0)
            self.assertIn("read-only", p.stderr)


if __name__ == "__main__":
    unittest.main()

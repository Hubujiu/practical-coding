#!/usr/bin/env python3
import json
import os
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

RUNTIME = Path(__file__).with_name("codebase_memory.py")


class IncrementalGraphRuntimeTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        self.repo = root / "repo"
        self.repo.mkdir()
        self.cache = root / "cache"
        self.env = {**os.environ, "PRACTICAL_CODING_CACHE_DIR": str(self.cache)}
        subprocess.run(["git", "init", "-q"], cwd=self.repo, check=True)

    def run_cli(self, *args: str, check: bool = True):
        p = subprocess.run(
            [sys.executable, str(RUNTIME), "--repo", str(self.repo), *args],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=self.env,
        )
        if check:
            self.assertEqual(p.returncode, 0, p.stderr)
            return json.loads(p.stdout)
        return p

    def db_path(self) -> Path:
        return next(self.cache.rglob("*.sqlite3"))

    def graph_semantics(self):
        con = sqlite3.connect(self.db_path())
        try:
            return {
                "symbols": con.execute(
                    """
                    SELECT f.path,s.name,s.qualified_name,s.kind,s.line,s.end_line
                    FROM symbols s JOIN files f ON f.id=s.file_id
                    ORDER BY f.path,s.qualified_name,s.line
                    """
                ).fetchall(),
                "imports": con.execute(
                    """
                    SELECT f.path,i.target,i.line
                    FROM imports i JOIN files f ON f.id=i.file_id
                    ORDER BY f.path,i.target,i.line
                    """
                ).fetchall(),
                "calls": con.execute(
                    """
                    SELECT f.path,coalesce(s.qualified_name,''),c.callee_name,c.line
                    FROM calls c
                    JOIN files f ON f.id=c.file_id
                    LEFT JOIN symbols s ON s.id=c.caller_symbol_id
                    ORDER BY f.path,2,c.callee_name,c.line
                    """
                ).fetchall(),
                "edges": con.execute(
                    """
                    SELECT a.qualified_name,b.qualified_name,c.callee_name
                    FROM call_edges e
                    JOIN symbols a ON a.id=e.caller_symbol_id
                    JOIN symbols b ON b.id=e.callee_symbol_id
                    JOIN calls c ON c.id=e.call_id
                    ORDER BY a.qualified_name,b.qualified_name,c.callee_name
                    """
                ).fetchall(),
            }
        finally:
            con.close()

    def test_noop_index_uses_metadata_fast_path(self):
        (self.repo / "a.py").write_text("def f():\n    return 1\n", encoding="utf-8")
        first = self.run_cli("index")
        second = self.run_cli("index")
        self.assertEqual(second["changed_files"], 0)
        self.assertEqual(second["hashed_files"], 0)
        self.assertEqual(second["metadata_fast_path_files"], 1)
        self.assertEqual(first["resolved_call_edges"], first["totals"]["call_edges"])
        self.assertEqual(second["resolved_call_edges"], second["totals"]["call_edges"])

    def test_verify_hashes_catches_preserved_metadata_change(self):
        path = self.repo / "a.py"
        path.write_text("def f():\n    return 1\n", encoding="utf-8")
        self.run_cli("index")
        st = path.stat()

        # Same byte length and restored mtime deliberately exercise the fast
        # path's documented timestamp assumption.
        path.write_text("def f():\n    return 2\n", encoding="utf-8")
        os.utime(path, ns=(st.st_atime_ns, st.st_mtime_ns))

        normal = self.run_cli("index")
        self.assertEqual(normal["changed_files"], 0)
        verified = self.run_cli("index", "--verify-hashes")
        self.assertEqual(verified["changed_files"], 1)
        self.assertEqual(verified["hashed_files"], 1)

    def test_new_symbol_re_resolves_unchanged_callers(self):
        (self.repo / "a.py").write_text("def helper():\n    return 1\n", encoding="utf-8")
        (self.repo / "caller.py").write_text(
            "def run():\n    return helper()\n", encoding="utf-8"
        )
        self.run_cli("index")

        (self.repo / "b.py").write_text("def helper():\n    return 2\n", encoding="utf-8")
        result = self.run_cli("index")
        self.assertEqual(result["changed_files"], 1)
        self.assertEqual(result["edge_resolution"]["mode"], "incremental")

        edges = set(self.graph_semantics()["edges"])
        self.assertIn(("caller.py.run", "a.py.helper", "helper"), edges)
        self.assertIn(("caller.py.run", "b.py.helper", "helper"), edges)

    def test_incremental_graph_matches_full_rebuild(self):
        (self.repo / "a.py").write_text("def helper():\n    return 1\n", encoding="utf-8")
        (self.repo / "caller.py").write_text(
            "def run():\n    return helper()\n", encoding="utf-8"
        )
        self.run_cli("index")
        (self.repo / "b.py").write_text("def helper():\n    return 2\n", encoding="utf-8")
        self.run_cli("index")
        incremental = self.graph_semantics()

        rebuilt = self.run_cli("index", "--full-rebuild")
        self.assertEqual(rebuilt["edge_resolution"]["mode"], "full")
        self.assertEqual(rebuilt["edge_resolution"]["calls_rechecked"], 1)
        self.assertEqual(incremental, self.graph_semantics())

    def test_duplicate_target_limit_is_deterministic(self):
        (self.repo / "caller.py").write_text(
            "def run():\n    return helper()\n", encoding="utf-8"
        )
        for i in range(40):
            (self.repo / f"h{i:02}.py").write_text(
                "def helper():\n    return 1\n", encoding="utf-8"
            )
        self.run_cli("index")

        # Replacing h00 gives its symbol a new rowid. Resolution must still be
        # based on stable source identity rather than insertion/rowid order.
        (self.repo / "h00.py").write_text(
            "def helper():\n    return 100\n", encoding="utf-8"
        )
        self.run_cli("index")
        incremental = self.graph_semantics()
        caller_edges = [e for e in incremental["edges"] if e[0] == "caller.py.run"]
        self.assertEqual(len(caller_edges), 32)

        self.run_cli("index", "--full-rebuild")
        self.assertEqual(incremental, self.graph_semantics())

    def test_raw_query_has_execution_budget(self):
        (self.repo / "a.py").write_text("def f():\n    return 1\n", encoding="utf-8")
        self.run_cli("index")
        p = self.run_cli(
            "query",
            "WITH RECURSIVE cnt(x) AS (VALUES(1) UNION ALL SELECT x+1 FROM cnt) "
            "SELECT sum(x) FROM cnt",
            "--budget-ms",
            "1",
            check=False,
        )
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("execution budget", p.stderr)


if __name__ == "__main__":
    unittest.main()
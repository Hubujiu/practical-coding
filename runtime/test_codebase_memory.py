#!/usr/bin/env python3
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

RUNTIME = Path(__file__).with_name("codebase_memory.py")


class EmbeddedGraphRuntimeTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        self.repo = root / "repo"
        self.repo.mkdir()
        self.cache = root / "cache"
        # Keep test databases out of the real user cache directory.
        self.env = {**os.environ, "PRACTICAL_CODING_CACHE_DIR": str(self.cache)}
        self.git("init", "-q")

    def git(self, *args: str):
        subprocess.run(
            ["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *args],
            cwd=self.repo,
            check=True,
        )

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

    def test_index_trace_impact_and_incremental_refresh(self):
        (self.repo / "a.py").write_text(
            "from b import helper\n\ndef main():\n    return helper()\n",
            encoding="utf-8",
        )
        (self.repo / "b.py").write_text(
            "def helper():\n    return 1\n",
            encoding="utf-8",
        )

        first = self.run_cli("index")
        self.assertEqual(first["changed_files"], 2)
        self.assertEqual(first["totals"]["call_edges"], 1)

        trace = self.run_cli("trace", "helper", "--direction", "in")
        self.assertEqual(trace["edges"][0]["from"], "a.py.main")

        impact = self.run_cli("impact", "--files", "b.py")
        self.assertTrue(any(x.get("symbol") == "a.py.main" for x in impact["affected"]))

        second = self.run_cli("index")
        self.assertEqual(second["changed_files"], 0)
        self.assertEqual(second["unchanged_files"], 2)

    def test_caller_attribution_with_same_named_methods(self):
        (self.repo / "m.py").write_text(
            "class A:\n"
            "    def run(self):\n"
            "        return helper()\n"
            "\n"
            "class B:\n"
            "    def run(self):\n"
            "        return other()\n"
            "\n"
            "def helper():\n"
            "    return 1\n"
            "\n"
            "def other():\n"
            "    return 2\n",
            encoding="utf-8",
        )
        self.run_cli("index")
        trace = self.run_cli("trace", "helper", "--direction", "in")
        self.assertEqual([e["from"] for e in trace["edges"]], ["m.py.A.run"])

    def test_generic_parser_scopes_same_named_methods(self):
        (self.repo / "m.js").write_text(
            "class A {\n"
            "  run() {\n"
            "    return helper();\n"
            "  }\n"
            "}\n"
            "\n"
            "class B {\n"
            "  run() {\n"
            "    return other();\n"
            "  }\n"
            "}\n"
            "\n"
            "function helper() {\n"
            "  return 1;\n"
            "}\n"
            "\n"
            "function other() {\n"
            "  return 2;\n"
            "}\n",
            encoding="utf-8",
        )
        self.run_cli("index")

        search = self.run_cli("search", "run")
        qualified = {r["qualified_name"] for r in search["results"]}
        self.assertIn("m.js.A.run", qualified)
        self.assertIn("m.js.B.run", qualified)

        trace = self.run_cli("trace", "helper", "--direction", "in")
        self.assertEqual([e["from"] for e in trace["edges"]], ["m.js.A.run"])

        # A top-level call after all blocks closed is module-level, not
        # attributed to the last parsed function.
        (self.repo / "top.js").write_text(
            "function setup() {\n"
            "  return 1;\n"
            "}\n"
            "boot();\n",
            encoding="utf-8",
        )
        self.run_cli("index")
        rows = self.run_cli(
            "query",
            "SELECT caller_symbol_id FROM calls "
            "JOIN files ON files.id = calls.file_id "
            "WHERE files.path = 'top.js' AND callee_name = 'boot'",
        )
        self.assertEqual(rows["rows"], [{"caller_symbol_id": None}])

    def test_generic_parser_single_line_bodies_close_their_scope(self):
        (self.repo / "one.js").write_text(
            "function setup() { return helper(); }\n"
            "boot();\n"
            "function helper() { return 1; }\n",
            encoding="utf-8",
        )
        self.run_cli("index")

        # boot() runs at module level, not inside the single-line setup().
        rows = self.run_cli(
            "query",
            "SELECT caller_symbol_id FROM calls "
            "JOIN files ON files.id = calls.file_id "
            "WHERE files.path = 'one.js' AND callee_name = 'boot'",
        )
        self.assertEqual(rows["rows"], [{"caller_symbol_id": None}])

        # The call inside the single-line body still binds to setup.
        trace = self.run_cli("trace", "one.js.helper", "--direction", "in")
        self.assertEqual([e["from"] for e in trace["edges"]], ["one.js.setup"])

    def test_generic_parser_allman_braces_close_class_scope(self):
        (self.repo / "Allman.cs").write_text(
            "class A\n"
            "{\n"
            "    void Run()\n"
            "    {\n"
            "        Helper();\n"
            "    }\n"
            "}\n"
            "\n"
            "class B\n"
            "{\n"
            "}\n",
            encoding="utf-8",
        )
        self.run_cli("index")
        rows = self.run_cli("query", "SELECT qualified_name FROM symbols ORDER BY qualified_name")
        qualified = {r["qualified_name"] for r in rows["rows"]}
        self.assertIn("Allman.cs.A", qualified)
        self.assertIn("Allman.cs.B", qualified)
        self.assertNotIn("Allman.cs.A.B", qualified)

    def test_impact_covers_git_renames(self):
        (self.repo / "old.py").write_text("def helper():\n    return 1\n", encoding="utf-8")
        (self.repo / "user.py").write_text(
            "from old import helper\n\ndef main():\n    return helper()\n",
            encoding="utf-8",
        )
        self.git("add", "-A")
        self.git("commit", "-qm", "init")
        self.git("mv", "old.py", "new.py")
        self.run_cli("index")
        impact = self.run_cli("impact", "--git-diff")
        self.assertIn("new.py", impact["changed_files"])
        self.assertIn("old.py", impact["changed_files"])
        self.assertTrue(any(s["qualified_name"] == "new.py.helper" for s in impact["changed_symbols"]))
        self.assertTrue(any(x.get("symbol") == "user.py.main" for x in impact["affected"]))

    def test_impact_import_matching_respects_module_boundaries(self):
        (self.repo / "a.py").write_text("def x():\n    return 1\n", encoding="utf-8")
        # "base64" contains the letter "a" and must not count as importing a.py.
        (self.repo / "z.py").write_text("import base64\n\ndef y():\n    return 2\n", encoding="utf-8")
        (self.repo / "w.py").write_text("from a import x\n\ndef v():\n    return x()\n", encoding="utf-8")
        (self.repo / "pkg").mkdir()
        (self.repo / "pkg" / "u.py").write_text("import pkg.sub.a\n\ndef t():\n    return 3\n", encoding="utf-8")
        self.run_cli("index")
        impact = self.run_cli("impact", "--files", "a.py")
        targets = {x["target"] for x in impact["affected"] if x.get("reason") == "import"}
        self.assertIn("a", targets)
        self.assertIn("pkg.sub.a", targets)
        self.assertNotIn("base64", targets)

    def test_databases_stay_in_configured_cache_dir(self):
        (self.repo / "a.py").write_text("def f():\n    return 1\n", encoding="utf-8")
        self.run_cli("index")
        self.assertTrue(list(self.cache.rglob("*.sqlite3")))
        # A cleanly closed WAL connection leaves no -wal/-shm residue behind.
        self.assertFalse(list(self.cache.rglob("*.sqlite3-wal")))
        self.assertFalse(list(self.cache.rglob("*.sqlite3-shm")))

    def test_outdated_schema_is_rebuilt_on_index(self):
        import sqlite3

        (self.repo / "a.py").write_text("def f():\n    return 1\n", encoding="utf-8")
        self.run_cli("index")
        db = next(self.cache.rglob("*.sqlite3"))
        con = sqlite3.connect(db)
        con.execute("UPDATE meta SET value='0' WHERE key='schema_version'")
        con.commit()
        con.close()

        p = self.run_cli("status", check=False)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("outdated", p.stderr)

        rebuilt = self.run_cli("index")
        self.assertEqual(rebuilt["totals"]["files"], 1)
        status = self.run_cli("status")
        self.assertEqual(status["status"], "ready")

    def test_read_only_query_guard(self):
        (self.repo / "a.py").write_text("def f():\n    return 1\n", encoding="utf-8")
        self.run_cli("index")
        ok = self.run_cli("query", "SELECT name FROM symbols")
        self.assertEqual(ok["rows"][0]["name"], "f")

        p = self.run_cli("query", "DELETE FROM symbols", check=False)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("read-only", p.stderr)


if __name__ == "__main__":
    unittest.main()

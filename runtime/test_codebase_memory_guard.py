#!/usr/bin/env python3
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

RUNTIME_DIR = Path(__file__).parent
RUNTIME = RUNTIME_DIR / "codebase_memory.py"


class CodebaseMemoryGuardTest(unittest.TestCase):
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

    def test_tracked_always_skip_directories_are_filtered(self):
        (self.repo / "src").mkdir()
        (self.repo / "vendor").mkdir()
        (self.repo / "src" / "keep.py").write_text(
            "def keep():\n    return 1\n", encoding="utf-8"
        )
        (self.repo / "vendor" / "ignored.py").write_text(
            "def ignored():\n    return 2\n", encoding="utf-8"
        )
        subprocess.run(["git", "add", "-A"], cwd=self.repo, check=True)

        self.run_cli("index")
        rows = self.run_cli("query", "SELECT path FROM files ORDER BY path")
        self.assertEqual(rows["rows"], [{"path": "src/keep.py"}])

    def test_project_mutation_lock_rejects_second_writer(self):
        sys.path.insert(0, str(RUNTIME_DIR))
        try:
            import codebase_memory

            db = self.cache / "graph.sqlite3"
            with codebase_memory.ProjectMutationLock(db, timeout_sec=0.2):
                with self.assertRaises(TimeoutError):
                    with codebase_memory.ProjectMutationLock(db, timeout_sec=0.05):
                        pass
        finally:
            sys.path.pop(0)
            sys.modules.pop("codebase_memory", None)
            sys.modules.pop("_codebase_memory_impl", None)


if __name__ == "__main__":
    unittest.main()

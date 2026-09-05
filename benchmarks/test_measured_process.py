"""Real short subprocess checks for the harness, not fake LLM benchmarks."""
from __future__ import annotations
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from benchmarks import measured_process as runner

class ProcessTests(unittest.TestCase):
    def run_script(self, script, timeout=5):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); out, err = root/'out.jsonl', root/'err.txt'
            result = runner.run_codex([sys.executable, '-c', script], 'test prompt', root,
                                      dict(os.environ), out, err, timeout)
            return result, out.read_text(), err.read_text()

    def test_process_gets_prompt_and_preserves_status(self):
        result, output, _ = self.run_script("import sys; print(sys.stdin.read()); sys.exit(7)")
        self.assertEqual(result[0], 7); self.assertFalse(result[1]); self.assertIn('test prompt', output)

    def test_completion_looking_output_does_not_override_timeout(self):
        result, output, _ = self.run_script('import time; print(\'{"type":"turn.completed"}\', flush=True); time.sleep(30)', timeout=.2)
        self.assertTrue(result[1]); self.assertFalse(result[2]); self.assertNotEqual(result[0], 0)

    def test_stderr_and_unicode_preserved(self):
        result, output, error = self.run_script("import sys; print('测试'); print('diagnostic', file=sys.stderr)")
        self.assertEqual(result[0], 0); self.assertIn('测试', output); self.assertIn('diagnostic', error)

    def test_invalid_timeout_rejected(self):
        for value in (0, -1, float('nan'), float('inf')):
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.run_script('', timeout=value)

if __name__ == '__main__':
    unittest.main()

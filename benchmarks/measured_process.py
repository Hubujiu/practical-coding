"""Capture one measured process and terminate its process group on timeout."""
from __future__ import annotations

import math
import os
import signal
import subprocess
import time
from pathlib import Path


def run_codex(command: list[str], prompt: str, cwd: Path, env: dict[str, str], stdout: Path,
              stderr: Path, timeout: float) -> tuple[int, bool, bool, float]:
    if not math.isfinite(timeout) or timeout <= 0:
        raise ValueError("timeout must be positive")
    started = time.monotonic()
    with stdout.open("w", encoding="utf-8") as out, stderr.open("w", encoding="utf-8") as err:
        flags = {"start_new_session": True} if os.name != "nt" else {
            "creationflags": subprocess.CREATE_NEW_PROCESS_GROUP,
        }
        with subprocess.Popen(command, cwd=cwd, env=env, stdin=subprocess.PIPE,
                              stdout=out, stderr=err, text=True, encoding="utf-8", errors="replace", **flags) as process:
            timed_out = False
            try:
                process.communicate(input=prompt, timeout=timeout)
            except subprocess.TimeoutExpired:
                timed_out = True
                if os.name == "nt":
                    try:
                        subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"],
                                       capture_output=True, timeout=5, check=False)
                    except (OSError, subprocess.TimeoutExpired):
                        process.kill()
                else:
                    try:
                        os.killpg(process.pid, signal.SIGTERM)
                    except ProcessLookupError:
                        pass
                try:
                    process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    if os.name == "nt":
                        process.kill()
                    else:
                        try:
                            os.killpg(process.pid, signal.SIGKILL)
                        except ProcessLookupError:
                            pass
                    process.wait(timeout=5)
                if os.name != "nt":
                    # Descendants may outlive a terminated group leader.
                    try:
                        os.killpg(process.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
            code = process.returncode
    # Completion-looking JSON never turns a killed process into a successful run.
    return int(code), timed_out, False, time.monotonic() - started

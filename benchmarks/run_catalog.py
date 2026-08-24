#!/usr/bin/env python3
"""Canonical benchmark entrypoint with the extended public case catalog installed."""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import run_benchmarks as bench
from case_catalog import install


if __name__ == "__main__":
    install(bench)
    raise SystemExit(bench.main())

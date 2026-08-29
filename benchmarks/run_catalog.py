#!/usr/bin/env python3
"""Canonical benchmark entrypoint with the extended public case catalog installed."""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import run_benchmarks as bench
from case_catalog import install


_CORE_SHA256 = bench.sha256
_RUNTIME_FILES = (
    Path(bench.__file__).resolve(),
    (HERE / "case_catalog.py").resolve(),
    Path(__file__).resolve(),
)


def runner_bundle_sha256() -> str:
    digest = hashlib.sha256()
    for path in _RUNTIME_FILES:
        digest.update(path.name.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def catalog_aware_sha256(path: Path) -> str:
    resolved = Path(path).resolve()
    if resolved == Path(bench.__file__).resolve():
        return runner_bundle_sha256()
    return _CORE_SHA256(resolved)


def configure() -> None:
    install(bench)
    bench.VERSION = "1.9"
    bench.sha256 = catalog_aware_sha256


if __name__ == "__main__":
    configure()
    raise SystemExit(bench.main())

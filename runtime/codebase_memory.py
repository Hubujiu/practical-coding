#!/usr/bin/env python3
"""
Practical Coding embedded Codebase Memory entry point.

The graph engine lives in _codebase_memory_impl.py. This small policy shell adds
behaviour that is useful for agent-driven, multi-session use while keeping the
engine dependency-free:

- always-skip directory filtering is applied even when discovery comes from
  `git ls-files`, so tracked vendor/build/cache trees do not pollute the graph;
- graph-mutating index operations are serialized per project/database with a
  cross-platform advisory file lock stored beside the cached SQLite database.

The discovery-filter and per-project mutation-lock design are adapted from the
MIT-licensed DeusData/codebase-memory-mcp project. See THIRD_PARTY_NOTICES.md.
"""
from __future__ import annotations

import os
import time
from pathlib import Path
from typing import BinaryIO, Sequence

import _codebase_memory_impl as _impl

# High-value always-skip directories adapted from the upstream discovery policy.
# The implementation remains intentionally much smaller than upstream: no
# daemon, watcher, Tree-sitter bundle, LSP pipeline, or background service.
_UPSTREAM_ALWAYS_SKIP_DIRS = {
    ".worktrees",
    ".claude",
    ".claude-worktrees",
    "Antigravity",
    ".eggs",
    ".env",
    ".nox",
    ".ruff_cache",
    ".tox",
    "env",
    "htmlcov",
    "site-packages",
    ".npm",
    ".nyc_output",
    ".pnpm-store",
    ".yarn",
    "bower_components",
    ".angular",
    ".turbo",
    ".parcel-cache",
    ".docusaurus",
    ".expo",
    "obj",
    "Pods",
    "temp",
    "tmp",
    ".terraform",
    ".serverless",
    "bazel-bin",
    "bazel-out",
    "bazel-testlogs",
    ".cargo",
    ".stack-work",
    ".dart_tool",
    "zig-cache",
    "zig-out",
    ".metals",
    ".bloop",
    ".bsp",
    ".ccls-cache",
    ".clangd",
    "elm-stuff",
    "_opam",
    ".cpcache",
    ".shadow-cljs",
    ".vercel",
    ".netlify",
    "deploy",
    "deployed",
    ".codebase-memory",
    ".qdrant_code_embeddings",
    ".tmp",
    "vendored",
}
_impl.IGNORED_DIRS.update(_UPSTREAM_ALWAYS_SKIP_DIRS)

_ORIGINAL_CANDIDATE_FILES = _impl.candidate_files
_ORIGINAL_CMD_INDEX = _impl.cmd_index


def candidate_files(repo: Path) -> list[Path]:
    """Apply one directory-deny policy regardless of the discovery backend."""
    root = _impl.repo_root(repo)
    out: list[Path] = []
    for path in _ORIGINAL_CANDIDATE_FILES(root):
        try:
            rel = path.relative_to(root)
        except ValueError:
            continue
        if any(part in _impl.IGNORED_DIRS for part in rel.parts[:-1]):
            continue
        out.append(path)
    return out


_impl.candidate_files = candidate_files


def _try_lock(file: BinaryIO) -> bool:
    file.seek(0)
    if os.name == "nt":
        import msvcrt

        try:
            msvcrt.locking(file.fileno(), msvcrt.LK_NBLCK, 1)
            return True
        except OSError:
            return False

    import fcntl

    try:
        fcntl.flock(file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        return True
    except OSError:
        return False


def _unlock(file: BinaryIO) -> None:
    file.seek(0)
    if os.name == "nt":
        import msvcrt

        msvcrt.locking(file.fileno(), msvcrt.LK_UNLCK, 1)
        return

    import fcntl

    fcntl.flock(file.fileno(), fcntl.LOCK_UN)


class ProjectMutationLock:
    """Cross-process advisory lock for one cached graph database."""

    def __init__(self, db: Path, timeout_sec: float = 5.0):
        self.path = Path(f"{db}.lock")
        self.timeout_sec = max(0.0, timeout_sec)
        self._file: BinaryIO | None = None

    def __enter__(self) -> "ProjectMutationLock":
        self.path.parent.mkdir(parents=True, exist_ok=True)
        file = self.path.open("a+b")
        file.seek(0, os.SEEK_END)
        if file.tell() == 0:
            file.write(b"\0")
            file.flush()

        deadline = time.monotonic() + self.timeout_sec
        while True:
            if _try_lock(file):
                self._file = file
                return self
            if time.monotonic() >= deadline:
                file.close()
                raise TimeoutError(str(self.path))
            time.sleep(0.05)

    def __exit__(self, exc_type, exc, tb) -> None:
        if self._file is None:
            return
        try:
            _unlock(self._file)
        finally:
            self._file.close()
            self._file = None


def cmd_index(args) -> int:
    repo = _impl.repo_root(args.repo)
    db = Path(args.db).resolve() if args.db else _impl.default_db(repo)
    try:
        with ProjectMutationLock(db):
            return int(_ORIGINAL_CMD_INDEX(args))
    except TimeoutError:
        raise SystemExit(
            "another Codebase Memory index operation is already running for "
            f"this project ({db}); use the current graph or retry after it finishes"
        ) from None


_impl.cmd_index = cmd_index


def main(argv: Sequence[str] | None = None) -> int:
    return int(_impl.main(argv))


if __name__ == "__main__":
    raise SystemExit(main())

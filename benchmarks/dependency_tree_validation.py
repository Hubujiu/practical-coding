#!/usr/bin/env python3
"""Compatibility CLI for the shared, frozen execution-axis benchmark.

The historical global monkey-patch runner is no longer used by this entry point.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Mapping

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import dependency_tree_contract as contract
import retrieval_validation as runner
import tree_validation as base

CANONICAL_RETRIEVAL_MODES = contract.CANONICAL_RETRIEVAL_MODES
RETRIEVAL_REFERENCE_TO_MODE = contract.RETRIEVAL_REFERENCE_TO_MODE
SETUP_COMMAND_RE = contract.SETUP_COMMAND_RE


def _retrieval_nodes(topology: Mapping[str, Any]) -> dict[str, Any]:
    return contract.retrieval_nodes(topology)


def retrieval_reference_prefix(topology: Mapping[str, Any], mode: str) -> list[str]:
    return contract.retrieval_reference_prefix(topology, mode, base.canonical_reference)


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    # Force this compatibility entry to its named axis instead of silently running
    # a caller-supplied contradictory axis.
    if any(arg == "--axis" or arg.startswith("--axis=") for arg in args):
        raise ValueError("use retrieval_validation.py to choose a different axis")
    return runner.main(["--axis", "execution", *args])


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (runner.capabilities.CapabilityError, runner.IntegrityError, ValueError, OSError) as exc:
        print(f"dependency benchmark blocked: {exc}", file=sys.stderr)
        raise SystemExit(2)

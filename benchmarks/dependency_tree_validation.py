#!/usr/bin/env python3
"""Run the execution-tree benchmark with mandatory preinitialized providers."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, Mapping

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import capability_environment as capabilities
import dependency_tree_contract as contract
import dependency_tree_runtime as runtime
import tree_validation as base

CANONICAL_RETRIEVAL_MODES = contract.CANONICAL_RETRIEVAL_MODES
RETRIEVAL_REFERENCE_TO_MODE = contract.RETRIEVAL_REFERENCE_TO_MODE
SETUP_COMMAND_RE = contract.SETUP_COMMAND_RE


def _extract_wrapper_args(argv: list[str]) -> tuple[argparse.Namespace, list[str]]:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--capability-manifest", type=Path, default=HERE / "capability_manifest.json")
    return parser.parse_known_args(argv)


def _retrieval_nodes(topology: Mapping[str, Any]) -> dict[str, Any]:
    return contract.retrieval_nodes(topology)


def retrieval_reference_prefix(topology: Mapping[str, Any], mode: str) -> list[str]:
    return contract.retrieval_reference_prefix(topology, mode, base.canonical_reference)


def _patch_runner(
    manifest: Mapping[str, Any],
    preflight_report: Mapping[str, Any],
    manifest_path: Path,
) -> None:
    runtime.patch_runner(manifest, preflight_report, manifest_path)


def main(argv: list[str] | None = None) -> int:
    raw = list(sys.argv[1:] if argv is None else argv)
    wrapper_args, remaining = _extract_wrapper_args(raw)
    manifest_path = wrapper_args.capability_manifest.resolve()
    manifest = capabilities.load_manifest(manifest_path)
    topology = base.load_topology(HERE / "tree_topology.json")
    _retrieval_nodes(topology)

    # Structural self-tests validate the contract without pretending external
    # binaries are available in ordinary CI. Every actual model run preflights.
    if "--self-test" in remaining:
        original_argv = sys.argv
        try:
            sys.argv = [original_argv[0], *remaining]
            return base.main()
        finally:
            sys.argv = original_argv

    preflight_report = capabilities.preflight(manifest, cwd=HERE.parent)
    _patch_runner(manifest, preflight_report, manifest_path)
    original_argv = sys.argv
    try:
        sys.argv = [original_argv[0], *remaining]
        return base.main()
    finally:
        sys.argv = original_argv


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except capabilities.CapabilityError as exc:
        print(f"dependency benchmark setup failed: {exc}", file=sys.stderr)
        raise SystemExit(2)

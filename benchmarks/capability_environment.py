#!/usr/bin/env python3
"""Fail-closed capability setup for dependency-enabled model benchmarks.

Provider probes, indexes, dependency resolution, and first-build warm-up run
before Codex starts. Their output and elapsed time are recorded separately and
never merged into measured token, duration, or tool-call data.
"""

from __future__ import annotations

try:
    from .capability_manifest import (
        SCHEMA_VERSION,
        CapabilityError,
        CapabilityManifestError,
        CapabilitySetupError,
        MissingCapabilityError,
        load_manifest,
        manifest_fingerprint,
    )
    from .capability_process import Run, preflight
    from .capability_workspace import (
        contains_token_key,
        prepare_workspace,
        workspace_environment,
        write_report,
    )
except ImportError:  # direct script imports from the benchmarks directory
    from capability_manifest import (
        SCHEMA_VERSION,
        CapabilityError,
        CapabilityManifestError,
        CapabilitySetupError,
        MissingCapabilityError,
        load_manifest,
        manifest_fingerprint,
    )
    from capability_process import Run, preflight
    from capability_workspace import (
        contains_token_key,
        prepare_workspace,
        workspace_environment,
        write_report,
    )

__all__ = [
    "SCHEMA_VERSION",
    "Run",
    "CapabilityError",
    "CapabilityManifestError",
    "CapabilitySetupError",
    "MissingCapabilityError",
    "load_manifest",
    "manifest_fingerprint",
    "preflight",
    "prepare_workspace",
    "workspace_environment",
    "write_report",
    "contains_token_key",
]

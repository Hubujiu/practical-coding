"""Prompt, provider-ceiling, and cell-spec contracts for Retrieval ablation."""

from __future__ import annotations

import re
import os
from pathlib import Path
from typing import Any, Mapping

try:
    from .retrieval_topology import (
        STAGES, STAGE_INDEX, instrumentation, retrieval_declared_prefix
    )
    from .tree_cases import CASES
except ImportError:  # direct script imports from the benchmarks directory
    from retrieval_topology import STAGES, STAGE_INDEX, instrumentation, retrieval_declared_prefix
    from tree_cases import CASES

SETUP_COMMAND_RE = re.compile(
    r"(?:^|[\s;&|])(?:[^\s;&|]*[/\\])?(?:zg(?:\.exe)?\s+index|"
    r"codebase-memory-mcp(?:\.exe)?\s+cli\s+index_repository|"
    r"rtk(?:\.exe)?\s+init|npm(?:\.cmd|\.exe)?\s+(?:ci|install))\b",
    re.I,
)

def allowed_provider_ids(stage: str) -> set[str]:
    allowed = {"rtk"}
    if STAGE_INDEX[stage] >= STAGE_INDEX["R1_DISCOVERY"]:
        allowed.add("zvec-grep")
    if STAGE_INDEX[stage] >= STAGE_INDEX["R3_STRUCTURAL"]:
        allowed.add("codebase-memory-mcp")
    return allowed


def retrieval_ceiling_instruction(topology: Mapping[str, Any], stage: str) -> str:
    refs = retrieval_declared_prefix(topology, stage)
    refs_text = ", ".join(refs) if refs else "none"
    providers = ", ".join(sorted(allowed_provider_ids(stage)))
    return (
        "<benchmark-retrieval-ceiling>\n"
        f"This ablation permits Retrieval policy only through {stage}. "
        f"Permitted Retrieval references, in progressive order: {refs_text}. "
        f"Permitted capability providers at this ceiling: {providers}. "
        "Repository-native exact reads/search remain available at every ceiling. "
        "Do not load a deeper Retrieval reference or invoke a provider owned by a deeper stage. "
        "The automatic execution tree remains adaptive. "
        "This is an availability ceiling, not a claim that the ceiling is the correct stage. "
        "Stop earlier when the task has enough evidence.\n"
        "</benchmark-retrieval-ceiling>"
    )


def capability_note() -> str:
    return (
        "<benchmark-capabilities>\n"
        "The paired environment already contains and has preinitialized all required providers before this measured turn: "
        "ranked retrieval via `zg query --human <intent> --limit <k>`, structural retrieval via "
        "`codebase-memory-mcp cli` (use `list_projects` before a project query), and noisy command output compaction via `rtk`. "
        "Do not install, initialize, download models, build indexes, or install project packages during measured execution. "
        "All benchmark arms receive this same note.\n"
        "</benchmark-capabilities>"
    )


def task_prompt(case: Mapping[str, Any], loaded: str, variant: str, topology: Mapping[str, Any]) -> str:
    suffix = [capability_note()]
    if variant.startswith("retrieval-cap:"):
        suffix.append(retrieval_ceiling_instruction(topology, variant.split(":", 1)[1]))
    if variant.startswith("cap:"):
        try:
            from .tree_validation import ceiling_instruction
        except ImportError:
            from tree_validation import ceiling_instruction
        suffix.append(ceiling_instruction(dict(topology), variant.split(":", 1)[1]))
    if variant == "adaptive" or variant.startswith(("retrieval-cap:", "cap:")):
        suffix.append(instrumentation(topology))
    shell = "Use PowerShell-compatible commands." if os.name == "nt" else "Use commands compatible with the host shell."
    scope = ("Implement the requested change within the allowed task files."
             if case.get("family") == "executable-delivery" else "Preserve a clean working tree; this is a read-only task.")
    return (
        f"{case['prompt']}\n\n{shell} {scope} Stay inside the task repository except for explicitly supplied Skill references. "
        "Do not access benchmark cases, scorers, reference solutions, or another arm's files. "
        "Cite current source and fresh command results when evidence is required.\n\n"
        f"{loaded}\n\n" + "\n\n".join(suffix)
    )



def build_specs(runs: int, *, current_only: bool, selected_cases: set[str]) -> list[tuple[str, str, int]]:
    specs: list[tuple[str, str, int]] = []
    for case in CASES:
        if selected_cases and case["task_id"] not in selected_cases:
            continue
        if case.get("manual_request"):
            variants = ["adaptive"] if current_only else ["no-skill", "baseline", "adaptive"]
        else:
            caps = [f"retrieval-cap:{stage}" for stage in STAGES]
            variants = ["adaptive", *caps] if current_only else ["no-skill", "baseline", "adaptive", *caps]
        for variant in variants:
            for repetition in range(1, runs + 1):
                specs.append((case["task_id"], variant, repetition))
    return specs


def _cell_path(output: Path, spec: tuple[str, str, int]) -> Path:
    task_id, variant, repetition = spec
    return output / "cells" / task_id / variant.replace(":", "-") / f"r{repetition:03d}"


def _provider_usage(commands: list[str]) -> dict[str, bool]:
    text = "\n".join(commands).lower()
    return {
        "zvec-grep": bool(re.search(r"(?:^|[\s;&|])(?:[^\s;&|]*[/\\])?zg(?:\.exe)?\s+(?:query|search)\b", text)),
        "codebase-memory-mcp": "codebase-memory-mcp" in text,
        "rtk": bool(re.search(r"(?:^|[\s;&|])(?:[^\s;&|]*[/\\])?rtk(?:\.exe)?\s+", text)),
    }


def provider_ceiling_violation(usage: Mapping[str, bool], ceiling: str | None) -> bool:
    if ceiling is None:
        return False
    allowed = allowed_provider_ids(ceiling)
    return any(used and provider not in allowed for provider, used in usage.items())

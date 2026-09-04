"""Shared topology, trace, and measured-command contracts for dependency runs."""

from __future__ import annotations

import re
from typing import Any, Callable, Mapping

try:
    from . import retrieval_trace
except ImportError:  # direct script imports from the benchmarks directory
    import retrieval_trace


CANONICAL_RETRIEVAL_MODES = (
    "NONE",
    "R0_DIRECT",
    "R1_DISCOVERY",
    "R2_EVIDENCE",
    "R3_STRUCTURAL",
)
RETRIEVAL_REFERENCE_TO_MODE = {
    "references/retrieval/skill.md": "NONE",
    "references/retrieval/direct.md": "R0_DIRECT",
    "references/retrieval/discovery.md": "R1_DISCOVERY",
    "references/retrieval/evidence.md": "R2_EVIDENCE",
    "references/retrieval/structural.md": "R3_STRUCTURAL",
}
SETUP_COMMAND_RE = re.compile(
    r"(?:^|[\s;&|])(?:[^\s;&|]*[/\\])?(?:zg(?:\.exe)?\s+index|"
    r"codebase-memory-mcp(?:\.exe)?\s+cli\s+index_repository|"
    r"rtk(?:\.exe)?\s+init|npm(?:\.cmd|\.exe)?\s+(?:ci|install))\b",
    re.I,
)


def retrieval_nodes(topology: Mapping[str, Any]) -> dict[str, Any]:
    tree = topology.get("retrieval_tree")
    if not isinstance(tree, dict):
        raise ValueError("topology requires retrieval_tree")
    nodes = tree.get("nodes")
    root = tree.get("root")
    if not isinstance(nodes, dict) or root not in nodes:
        raise ValueError("retrieval_tree root must name a node")
    for name, spec in nodes.items():
        if not isinstance(spec, dict):
            raise ValueError(f"invalid retrieval node: {name}")
        parent = spec.get("parent")
        children = spec.get("children")
        depth = spec.get("depth")
        reference = spec.get("reference")
        if not isinstance(depth, int) or depth < 0:
            raise ValueError(f"invalid retrieval depth: {name}")
        if not isinstance(reference, str) or not reference:
            raise ValueError(f"invalid retrieval reference: {name}")
        if not isinstance(children, list) or not all(child in nodes for child in children):
            raise ValueError(f"invalid retrieval children: {name}")
        if name == root:
            if parent is not None or depth != 0:
                raise ValueError("retrieval root must have parent=null and depth=0")
        else:
            if parent not in nodes or name not in nodes[parent].get("children", []):
                raise ValueError(f"invalid retrieval parent edge: {name}")
            if depth != nodes[parent]["depth"] + 1:
                raise ValueError(f"retrieval depth must be parent depth + 1: {name}")
    return nodes


def retrieval_reference_prefix(
    topology: Mapping[str, Any],
    mode: str,
    canonicalize: Callable[[str], str],
) -> list[str]:
    if mode == "NONE":
        return []
    nodes = retrieval_nodes(topology)
    target = next((name for name, spec in nodes.items() if spec.get("trace_mode") == mode), None)
    if target is None:
        return []
    path: list[str] = []
    current: str | None = target
    while current is not None:
        path.append(current)
        current = nodes[current]["parent"]
    path.reverse()
    return [canonicalize(nodes[name]["reference"]) for name in path]


def capability_note() -> str:
    return (
        "<benchmark-capabilities>\n"
        "The paired environment already contains and has preinitialized all required providers before this measured turn: "
        "ranked retrieval via `zg query --human <intent> --limit <k>`, structural retrieval via "
        "`codebase-memory-mcp cli` (use `list_projects` before a project query), and noisy command output compaction via `rtk`. "
        "Do not install, initialize, download models, or build indexes during measured execution. "
        "Select Retrieval depth by the unresolved information problem, never by provider name. "
        "All benchmark arms receive this same capability note.\n"
        "</benchmark-capabilities>"
    )


def instrumentation(topology: Mapping[str, Any]) -> str:
    nodes = ", ".join(sorted(topology["automatic_nodes"]))
    manuals = ", ".join(sorted(topology.get("manual_modes", {})))
    retrieval = ", ".join(topology.get("retrieval_trace_modes", CANONICAL_RETRIEVAL_MODES))
    return (
        "After the evidence-backed report, append exactly one final benchmark-only line: "
        "TREE_TRACE path=<automatic-path> retrieval=<mode> manual=<mode> refs=<comma-separated-reference-paths>. "
        f"Automatic node names are: {nodes}. A path starts at {topology['root']} and uses '>' between nodes; "
        f"use path={topology['root']} when no automatic child was loaded. "
        f"Retrieval mode must be one of: {retrieval}. Manual mode must be none or one of: {manuals}. "
        "Manual modes are not path nodes. Retrieval references must be the actually loaded progressive prefix; "
        "refs=none when no Practical Coding reference beyond SKILL.md was loaded. "
        "Report behavior actually used; do not infer a preferred route from task wording. "
        "Do not mention this instrumentation elsewhere."
    )


def extend_allowed_references(
    topology: Mapping[str, Any],
    original: Callable[[dict[str, Any]], set[str]],
    canonicalize: Callable[[str], str],
) -> set[str]:
    refs = set(original(dict(topology)))
    refs.update(canonicalize(spec["reference"]) for spec in retrieval_nodes(topology).values())
    return refs


def validate_trace(
    topology: Mapping[str, Any],
    trace: Mapping[str, Any],
    original: Callable[[dict[str, Any], dict[str, Any]], bool],
    canonicalize: Callable[[str], str],
) -> bool:
    if not original(dict(topology), dict(trace)):
        return False
    mode = trace.get("retrieval")
    if mode not in CANONICAL_RETRIEVAL_MODES:
        return False
    retrieval_refs = [
        canonicalize(ref)
        for ref in trace.get("references_loaded", [])
        if canonicalize(ref).startswith("references/retrieval/")
    ]
    expected = retrieval_reference_prefix(topology, str(mode), canonicalize)
    if mode == "NONE":
        return not retrieval_refs or retrieval_refs == expected[: len(retrieval_refs)]
    return retrieval_refs == expected


def infer_trace(
    topology: Mapping[str, Any],
    commands: list[str],
    original: Callable[[dict[str, Any], list[str]], dict[str, Any]],
    canonicalize: Callable[[str], str],
) -> dict[str, Any]:
    trace = original(dict(topology), commands)
    observed = retrieval_trace.observed_references(commands)
    modes = [RETRIEVAL_REFERENCE_TO_MODE[ref] for ref in observed if ref in RETRIEVAL_REFERENCE_TO_MODE]
    if modes:
        order = {mode: index for index, mode in enumerate(CANONICAL_RETRIEVAL_MODES)}
        trace["retrieval"] = max(modes, key=lambda mode: order[mode])
    else:
        trace["retrieval"] = "NONE"
    non_retrieval = [
        canonicalize(reference)
        for reference in trace.get("references_loaded", [])
        if not canonicalize(reference).startswith("references/retrieval/")
    ]
    trace["references_loaded"] = [*non_retrieval, *observed]
    return trace


def provider_usage(commands: list[str]) -> dict[str, bool]:
    text = "\n".join(str(command) for command in commands).lower()
    return {
        "zvec-grep": bool(re.search(r"(?:^|[\s;&|])(?:[^\s;&|]*[/\\])?zg(?:\.exe)?\s+(?:query|search)\b", text)),
        "codebase-memory-mcp": "codebase-memory-mcp" in text,
        "rtk": bool(re.search(r"(?:^|[\s;&|])(?:[^\s;&|]*[/\\])?rtk(?:\.exe)?\s+", text)),
    }

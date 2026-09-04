"""Progressive R0-R3 topology and trace validation."""

from __future__ import annotations

from typing import Any, Mapping

try:
    from . import retrieval_trace
    from . import tree_validation as base
except ImportError:  # direct script imports from the benchmarks directory
    import retrieval_trace
    import tree_validation as base

STAGES = ("NONE", "R0_DIRECT", "R1_DISCOVERY", "R2_EVIDENCE", "R3_STRUCTURAL")
STAGE_INDEX = {stage: index for index, stage in enumerate(STAGES)}

def retrieval_nodes(topology: Mapping[str, Any]) -> dict[str, Any]:
    tree = topology.get("retrieval_tree")
    if not isinstance(tree, dict):
        raise ValueError("topology requires retrieval_tree")
    nodes = tree.get("nodes")
    root = tree.get("root")
    if not isinstance(nodes, dict) or root not in nodes:
        raise ValueError("retrieval_tree root must name a node")
    seen_modes: set[str] = set()
    for name, spec in nodes.items():
        if not isinstance(spec, dict):
            raise ValueError(f"invalid retrieval node: {name}")
        parent = spec.get("parent")
        children = spec.get("children")
        depth = spec.get("depth")
        mode = spec.get("trace_mode")
        reference = spec.get("reference")
        if not isinstance(depth, int) or depth < 0:
            raise ValueError(f"invalid retrieval depth: {name}")
        if mode not in STAGE_INDEX or mode in seen_modes:
            raise ValueError(f"invalid or duplicate retrieval trace mode: {name}")
        seen_modes.add(mode)
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
                raise ValueError(f"retrieval depth must equal parent depth + 1: {name}")
    if seen_modes != set(STAGES):
        raise ValueError(f"retrieval modes mismatch: {sorted(seen_modes)}")
    return nodes


def retrieval_declared_prefix(topology: Mapping[str, Any], stage: str) -> list[str]:
    if stage == "NONE":
        return []
    nodes = retrieval_nodes(topology)
    target = next(name for name, spec in nodes.items() if spec["trace_mode"] == stage)
    path: list[str] = []
    current: str | None = target
    while current is not None:
        path.append(current)
        current = nodes[current]["parent"]
    path.reverse()
    return [str(nodes[name]["reference"]) for name in path]


def retrieval_prefix(topology: Mapping[str, Any], stage: str) -> list[str]:
    return [base.canonical_reference(reference) for reference in retrieval_declared_prefix(topology, stage)]


def allowed_references(topology: Mapping[str, Any]) -> set[str]:
    refs = base.allowed_references(dict(topology))
    refs.update(base.canonical_reference(spec["reference"]) for spec in retrieval_nodes(topology).values())
    return refs


def validate_trace(topology: Mapping[str, Any], trace: Mapping[str, Any], ceiling: str | None = None) -> bool:
    mode = trace.get("retrieval")
    if mode not in STAGE_INDEX:
        return False
    if ceiling is not None and STAGE_INDEX[mode] > STAGE_INDEX[ceiling]:
        return False
    if not base.validate_automatic_path(dict(topology), list(trace.get("path") or [])):
        return False
    manual = trace.get("manual")
    if manual != "none" and manual not in topology.get("manual_modes", {}):
        return False
    refs = [base.canonical_reference(ref) for ref in trace.get("references_loaded", [])]
    if any(ref not in allowed_references(topology) for ref in refs):
        return False
    retrieval_refs = [ref for ref in refs if ref.startswith("references/retrieval/")]
    expected = retrieval_prefix(topology, mode)
    if mode == "NONE":
        return retrieval_refs in ([], expected)
    return retrieval_refs == expected


def infer_trace(topology: Mapping[str, Any], commands: list[str]) -> dict[str, Any]:
    trace = base.infer_trace_from_commands(dict(topology), commands)
    observed = retrieval_trace.observed_references(commands)
    mode_by_ref = {
        base.canonical_reference(spec["reference"]): spec["trace_mode"]
        for spec in retrieval_nodes(topology).values()
    }
    modes = [mode_by_ref[reference] for reference in observed if reference in mode_by_ref]
    trace["retrieval"] = max(modes, key=lambda mode: STAGE_INDEX[mode]) if modes else "NONE"
    non_retrieval = [
        base.canonical_reference(reference)
        for reference in trace.get("references_loaded", [])
        if not base.canonical_reference(reference).startswith("references/retrieval/")
    ]
    trace["references_loaded"] = [*non_retrieval, *observed]
    return trace


def instrumentation(topology: Mapping[str, Any]) -> str:
    nodes = ", ".join(sorted(topology["automatic_nodes"]))
    manuals = ", ".join(sorted(topology.get("manual_modes", {})))
    return (
        "After the evidence-backed report, append exactly one final benchmark-only line: "
        "TREE_TRACE path=<automatic-path> retrieval=<mode> manual=<mode> refs=<comma-separated-reference-paths>. "
        f"Automatic node names are: {nodes}. A path starts at {topology['root']} and uses '>' between nodes; "
        f"use path={topology['root']} when no automatic child was loaded. "
        f"Retrieval mode must be one of: {', '.join(STAGES)}. "
        f"Manual mode must be none or one of: {manuals}. "
        "Manual modes are not path nodes. Retrieval references must be the complete actually loaded root-to-stage prefix. "
        "refs=none only when no Practical Coding reference beyond SKILL.md was loaded. "
        "Report behavior actually used; do not infer a preferred route from task wording. "
        "Do not mention this instrumentation elsewhere."
    )

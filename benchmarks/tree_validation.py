#!/usr/bin/env python3
"""Run evolvable local-router-tree experiments on frozen real repositories.

Unlike the legacy router benchmark, this runner does not assign an expected
automatic route to each task. It measures delivered quality under capability
ceilings for every node, then records the adaptive path for later topology
analysis. Manual activation is scored only from explicit user requests.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import datetime as dt
import json
import os
import re
import shutil
import statistics
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import run_benchmarks as bench
from tree_cases import CASES, REPOSITORIES


VERSION = "1.0"
MODEL = bench.MODEL
REASONING = bench.REASONING
TRACE_RE = re.compile(
    r"TREE_TRACE\s+path=([^\s]+)\s+retrieval=([A-Z_]+)\s+manual=([a-z_-]+)\s+refs=([^\r\n]+)",
    re.I,
)
OBSERVED_REF_RE = re.compile(
    r"practical-coding[/\\](references[/\\][a-z0-9_./\\-]+\.md)",
    re.I,
)


def load_topology(path: Path) -> dict[str, Any]:
    topology = json.loads(path.read_text(encoding="utf-8"))
    nodes = topology.get("automatic_nodes") or {}
    root = topology.get("root")
    if root not in nodes:
        raise ValueError("topology root must name an automatic node")
    for name, node in nodes.items():
        parent = node.get("parent")
        depth = node.get("depth")
        children = node.get("children")
        if not isinstance(depth, int) or depth < 0:
            raise ValueError(f"invalid depth for {name}")
        if not isinstance(children, list) or not all(child in nodes for child in children):
            raise ValueError(f"invalid children for {name}")
        if name == root:
            if parent is not None or depth != 0:
                raise ValueError("root must have parent=null and depth=0")
        else:
            if parent not in nodes:
                raise ValueError(f"invalid parent for {name}")
            if name not in nodes[parent].get("children", []):
                raise ValueError(f"parent {parent} does not list child {name}")
            if depth != nodes[parent]["depth"] + 1:
                raise ValueError(f"depth of {name} must equal parent depth + 1")
    return topology


def node_path(topology: dict[str, Any], node_name: str) -> list[str]:
    nodes = topology["automatic_nodes"]
    if node_name not in nodes:
        raise ValueError(f"unknown node: {node_name}")
    path: list[str] = []
    current: str | None = node_name
    while current is not None:
        path.append(current)
        current = nodes[current]["parent"]
    path.reverse()
    if path[0] != topology["root"]:
        raise ValueError(f"node {node_name} is disconnected from root")
    return path


def parse_trace(answer: str) -> dict[str, Any]:
    matches = list(TRACE_RE.finditer(answer))
    if not matches:
        return {"path": [], "retrieval": None, "manual": None, "references_loaded": []}
    match = matches[-1]
    raw_path = match.group(1).strip().strip("<>")
    path = [] if raw_path.lower() in {"none", "-"} else [part.strip().lower() for part in raw_path.split(">") if part.strip()]
    refs_raw = match.group(4).strip().strip("<>")
    refs = [] if refs_raw.lower() in {"none", "-"} else [part.strip().strip("<>") for part in refs_raw.split(",") if part.strip()]
    return {
        "path": path,
        "retrieval": match.group(2).upper(),
        "manual": match.group(3).lower(),
        "references_loaded": refs,
    }


def canonical_reference(raw: str) -> str:
    ref = str(raw).strip().strip("<>\"'").lower().replace("\\", "/")
    marker = "/practical-coding/"
    if marker in ref:
        ref = ref.split(marker, 1)[1]
    if ref.startswith("manual/"):
        ref = f"references/{ref}"
    if "/" not in ref and ref.endswith(".md"):
        ref = f"references/{ref}"
    return ref


def allowed_references(topology: dict[str, Any]) -> set[str]:
    automatic = {
        canonical_reference(spec["reference"])
        for name, spec in topology["automatic_nodes"].items()
        if name != topology["root"]
    }
    manual = {canonical_reference(ref) for ref in topology.get("manual_modes", {}).values()}
    return automatic | manual | {"references/navigation.md"}


def infer_trace_from_commands(topology: dict[str, Any], commands: list[str]) -> dict[str, Any]:
    command_text = "\n".join(commands).replace("\\", "/")
    refs = sorted({canonical_reference(match.group(1)) for match in OBSERVED_REF_RE.finditer(command_text)})
    nodes = topology["automatic_nodes"]
    loaded_nodes = [
        name
        for name, spec in nodes.items()
        if name != topology["root"] and canonical_reference(spec["reference"]) in refs
    ]
    paths = [node_path(topology, name) for name in loaded_nodes]
    path = max(paths, key=len) if paths and all(
        candidate == paths[0][: len(candidate)] or paths[0] == candidate[: len(paths[0])]
        for candidate in paths
    ) else [topology["root"]]
    loaded_manual = [
        name
        for name, ref in topology.get("manual_modes", {}).items()
        if canonical_reference(ref) in refs
    ]
    manual = loaded_manual[0] if len(loaded_manual) == 1 else "none"
    return {
        "path": path,
        "retrieval": "TARGETED" if commands else "NONE",
        "manual": manual,
        "references_loaded": refs,
    }


def validate_automatic_path(topology: dict[str, Any], path: list[str]) -> bool:
    if not path or path[0] != topology["root"]:
        return False
    nodes = topology["automatic_nodes"]
    if any(name not in nodes for name in path):
        return False
    return all(child in nodes[parent]["children"] for parent, child in zip(path, path[1:]))


def validate_trace(topology: dict[str, Any], trace: dict[str, Any]) -> bool:
    retrieval_ok = trace["retrieval"] in set(topology.get("retrieval_modes", []))
    manual_ok = trace["manual"] == "none" or trace["manual"] in topology.get("manual_modes", {})
    refs_ok = all(canonical_reference(ref) in allowed_references(topology) for ref in trace["references_loaded"])
    return retrieval_ok and manual_ok and refs_ok and validate_automatic_path(topology, trace["path"])


def score_answer(
    case: dict[str, Any],
    answer: str,
    commands: list[str],
    workspace: Path,
    *,
    trace: dict[str, Any] | None,
    enforce_runtime_contract: bool,
) -> dict[str, Any]:
    lower = answer.lower()
    missing = [group for group in case["required"] if not any(term.lower() in lower for term in group)]
    command_text = "\n".join(commands).lower()
    normalized_command_text = command_text.replace("\\", "/")
    probe_groups = [group if isinstance(group, list) else [group] for group in case["probe_terms"]]
    probe_missing = [group for group in probe_groups if not any(term.lower() in command_text for term in group)]
    status = bench.run_command(["git", "status", "--porcelain"], workspace)
    clean = status.returncode == 0 and not status.stdout.strip()

    requested_manual = case.get("manual_request")
    manual_contract_ok = True
    spontaneous_manual = False
    if enforce_runtime_contract:
        selected_manual = (trace or {}).get("manual")
        refs = [str(ref).lower().replace("\\", "/") for ref in (trace or {}).get("references_loaded", [])]
        manual_ref_loaded = any("manual/" in ref for ref in refs) or "references/manual/" in normalized_command_text
        if requested_manual:
            requested_suffix = f"manual/{requested_manual}.md"
            manual_contract_ok = selected_manual == requested_manual and (
                any(requested_suffix in ref for ref in refs)
                or f"references/{requested_suffix}" in normalized_command_text
            )
        else:
            spontaneous_manual = selected_manual not in {None, "none"} or manual_ref_loaded
            manual_contract_ok = not spontaneous_manual

    passed = not missing and not probe_missing and clean and manual_contract_ok
    return {
        "passed": passed,
        "missing_evidence_groups": missing,
        "missing_probe_terms": probe_missing,
        "workspace_clean": clean,
        "manual_contract_ok": manual_contract_ok,
        "spontaneous_manual_mode": spontaneous_manual,
    }


def resolve_repositories(repository_root: Path, overrides: list[str]) -> dict[str, Path]:
    mapped = {name: (repository_root / data["local_name"]).resolve() for name, data in REPOSITORIES.items()}
    for raw in overrides:
        if "=" not in raw:
            raise ValueError(f"repository override must be NAME=PATH: {raw}")
        name, value = raw.split("=", 1)
        if name not in REPOSITORIES:
            raise ValueError(f"unknown repository override: {name}")
        mapped[name] = Path(value).resolve()
    for name, path in mapped.items():
        commit = REPOSITORIES[name]["commit"]
        if not path.is_dir():
            raise FileNotFoundError(f"tree benchmark repository unavailable: {name}: {path}")
        check = bench.run_command(["git", "cat-file", "-e", f"{commit}^{{commit}}"], path)
        if check.returncode:
            raise RuntimeError(f"{name} does not contain frozen commit {commit}: {check.stderr}")
    return mapped


def prepare_workspace(source: Path, commit: str, workspace: Path) -> None:
    clone = bench.run_command(["git", "clone", "-q", "--shared", "--no-checkout", str(source), str(workspace)], workspace.parent)
    if clone.returncode:
        raise RuntimeError(clone.stderr)
    configure = bench.run_command(["git", "config", "core.longpaths", "true"], workspace)
    if configure.returncode:
        raise RuntimeError(configure.stderr)
    checkout = bench.run_command(["git", "checkout", "-q", "--detach", commit], workspace)
    if checkout.returncode:
        raise RuntimeError(checkout.stderr)


def instrumentation(topology: dict[str, Any]) -> str:
    nodes = ", ".join(sorted(topology["automatic_nodes"]))
    manuals = ", ".join(sorted(topology.get("manual_modes", {})))
    retrieval = ", ".join(topology.get("retrieval_modes", []))
    return (
        "After the evidence-backed report, append exactly one final benchmark-only line: "
        "TREE_TRACE path=<automatic-path> retrieval=<mode> manual=<mode> refs=<comma-separated-reference-paths>. "
        f"Automatic node names are: {nodes}. A path starts at {topology['root']} and uses '>' between nodes; "
        f"use path={topology['root']} when no automatic child was loaded. "
        f"Retrieval mode must be one of: {retrieval}. Manual mode must be none or one of: {manuals}. "
        "Manual modes are not path nodes. refs=none when no Practical Coding reference beyond SKILL.md was loaded. "
        "Report behavior actually used; do not infer a preferred route from the task wording. Do not mention this instrumentation elsewhere."
    )


def ceiling_instruction(topology: dict[str, Any], node_name: str) -> str:
    path = node_path(topology, node_name)
    allowed_refs = [topology["automatic_nodes"][name]["reference"] for name in path if name != topology["root"]]
    refs_text = ", ".join(allowed_refs) if allowed_refs else "none"
    return (
        "<benchmark-capability-ceiling>\n"
        f"This ablation permits automatic capabilities only on the path {' > '.join(path)}. "
        f"Permitted non-root automatic references: {refs_text}. "
        "Do not load siblings, descendants beyond the ceiling, or any manual mode. "
        "This is an availability ceiling, not a claim that the ceiling node is the correct route. "
        "If Core can solve the task, stay at Core; otherwise do the best possible work within the available path.\n"
        "</benchmark-capability-ceiling>"
    )


def task_prompt(case: dict[str, Any], loaded: str, variant: str, topology: dict[str, Any]) -> str:
    suffix = ""
    if variant.startswith("cap:"):
        suffix += "\n\n" + ceiling_instruction(topology, variant.split(":", 1)[1])
    if variant == "adaptive" or variant.startswith("cap:"):
        suffix += "\n\n" + instrumentation(topology)
    return (
        f"Frozen tree-benchmark task {case['task_id']} ({case['family']}).\n\n{case['prompt']}\n\n"
        "Use PowerShell-compatible commands. Stay within this repository and preserve a clean working tree. "
        "Cite concrete source paths/symbols and fresh command evidence when the task needs repository evidence.\n\n"
        f"<benchmark-variant>{variant}</benchmark-variant>\n{loaded}{suffix}"
    )


def build_specs(topology: dict[str, Any], runs: int, *, current_only: bool, selected_cases: set[str]) -> list[tuple[str, str, int]]:
    specs: list[tuple[str, str, int]] = []
    cap_nodes = list(topology["automatic_nodes"])
    for case in CASES:
        if selected_cases and case["task_id"] not in selected_cases:
            continue
        if case.get("manual_request"):
            variants = ["adaptive"] if current_only else ["no-skill", "baseline", "adaptive"]
        else:
            variants = ["adaptive", *(f"cap:{node}" for node in cap_nodes)] if current_only else [
                "no-skill",
                "baseline",
                "adaptive",
                *(f"cap:{node}" for node in cap_nodes),
            ]
        for variant in variants:
            for repetition in range(1, runs + 1):
                specs.append((case["task_id"], variant, repetition))
    return specs


def run_cell(
    spec: tuple[str, str, int],
    args: argparse.Namespace,
    topology: dict[str, Any],
    repositories: dict[str, Path],
    baseline: Path | None,
    eval_home: Path,
    output: Path,
) -> dict[str, Any]:
    task_id, variant, repetition = spec
    case = next(item for item in CASES if item["task_id"] == task_id)
    safe_variant = variant.replace(":", "-")
    cell = output / "cells" / task_id / safe_variant / f"r{repetition:03d}"
    result_path = cell / "result.json"
    if result_path.is_file():
        return json.loads(result_path.read_text(encoding="utf-8"))
    cell.mkdir(parents=True, exist_ok=True)
    workspace = cell / "workspace"
    if workspace.exists():
        shutil.rmtree(workspace)
    prepare_workspace(repositories[case["repository"]], REPOSITORIES[case["repository"]]["commit"], workspace)

    if variant == "no-skill":
        loaded = ""
    elif variant == "baseline":
        if baseline is None:
            raise RuntimeError("baseline Skill is unavailable")
        loaded = bench.skill_text("practical-previous", {}, baseline)
    else:
        loaded = bench.skill_text("practical-current", {}, None)

    prompt = task_prompt(case, loaded, variant, topology)
    (cell / "prompt.txt").write_text(prompt, encoding="utf-8")
    env = os.environ.copy()
    env["CODEX_HOME"] = str(eval_home)
    codex = bench.resolve_codex(args.codex)
    stdout = cell / "round1.jsonl"
    stderr = cell / "round1.stderr.txt"
    code, timed_out, forced, duration = bench.run_codex(
        bench.codex_command(codex, workspace), prompt, workspace, env, stdout, stderr, args.timeout
    )
    parsed = bench.parse_transcript(stdout)
    current_runtime = variant == "adaptive" or variant.startswith("cap:")
    trace = parse_trace(parsed["answer"]) if current_runtime else None
    trace_source = "reported" if trace and trace.get("path") else None
    if current_runtime and trace and not trace.get("path"):
        trace = infer_trace_from_commands(topology, parsed["tool_commands"])
        trace_source = "observed-commands"
    trace_valid = validate_trace(topology, trace) if current_runtime and trace is not None else None
    terminal_node = trace["path"][-1] if trace and trace.get("path") else None

    record: dict[str, Any] = {
        "schema_version": VERSION,
        "task_id": task_id,
        "repository": case["repository"],
        "family": case["family"],
        "manual_request": case.get("manual_request"),
        "variant": variant,
        "repetition": repetition,
        "exit_status": code,
        "timed_out": timed_out,
        "forced_after_completion": forced,
        "duration_seconds": duration,
        "tool_calls": parsed["tool_calls"],
        **parsed["usage"],
        "answer": parsed["answer"],
        "tool_commands": parsed["tool_commands"],
        "selected_path": trace["path"] if trace else None,
        "selected_terminal_node": terminal_node,
        "selected_depth": topology["automatic_nodes"].get(terminal_node, {}).get("depth") if terminal_node else None,
        "selected_retrieval": trace["retrieval"] if trace else None,
        "selected_manual": trace["manual"] if trace else None,
        "references_loaded": trace["references_loaded"] if trace else [],
        "routing_trace_valid": trace_valid,
        "routing_trace_source": trace_source,
    }
    infrastructure_error = "timeout" if timed_out else (f"codex exit status {code}" if code and not forced else None)
    if infrastructure_error:
        record.update({"passed": None, "verdict": "indeterminate", "error": infrastructure_error})
    else:
        record.update(
            score_answer(
                case,
                parsed["answer"],
                parsed["tool_commands"],
                workspace,
                trace=trace,
                enforce_runtime_contract=current_runtime,
            )
        )
        if current_runtime and not trace_valid:
            record["passed"] = False
            record["routing_trace_error"] = True
        record["verdict"] = "pass" if record["passed"] else "fail"
    (cell / "answer.md").write_text(parsed["answer"] + "\n", encoding="utf-8")
    result_path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return record


def _mean(records: list[dict[str, Any]], key: str) -> float | None:
    values = [float(record[key]) for record in records if record.get(key) is not None]
    return statistics.mean(values) if values else None


def summary(records: list[dict[str, Any]], runs: int) -> dict[str, Any]:
    arms: dict[str, Any] = {}
    for variant in sorted({record["variant"] for record in records}):
        selected = [record for record in records if record["variant"] == variant]
        determinate = [record for record in selected if record.get("passed") is not None]
        arms[variant] = {
            "cells": len(selected),
            "determinate": len(determinate),
            "pass_rate": sum(record["passed"] is True for record in determinate) / len(determinate) if determinate else None,
            "tokens_mean": _mean(determinate, "total_tokens"),
            "duration_seconds_mean": _mean(determinate, "duration_seconds"),
            "tool_calls_mean": _mean(determinate, "tool_calls"),
        }
    adaptive = [record for record in records if record["variant"] == "adaptive" and record.get("passed") is not None]
    automatic = [record for record in adaptive if not record.get("manual_request")]
    manual = [record for record in adaptive if record.get("manual_request")]
    return {
        "runs_per_cell": runs,
        "tasks": len({record["task_id"] for record in records}),
        "repositories": sorted({record["repository"] for record in records}),
        "arms": arms,
        "adaptive_trace_valid_rate": sum(record.get("routing_trace_valid") is True for record in adaptive) / len(adaptive) if adaptive else None,
        "adaptive_spontaneous_manual_count": sum(record.get("spontaneous_manual_mode") is True for record in automatic),
        "adaptive_spontaneous_manual_rate": sum(record.get("spontaneous_manual_mode") is True for record in automatic) / len(automatic) if automatic else None,
        "adaptive_explicit_manual_success_rate": sum(record.get("manual_contract_ok") is True for record in manual) / len(manual) if manual else None,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument("--workers", type=int, default=3)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--repository-root", type=Path, default=ROOT.parent)
    parser.add_argument("--repository", action="append", default=[], help="override a source as NAME=PATH")
    parser.add_argument("--topology", type=Path, default=HERE / "tree_topology.json")
    parser.add_argument("--baseline-ref")
    parser.add_argument("--codex", default=os.environ.get("CODEX_BIN", "codex"))
    parser.add_argument("--timeout", type=float, default=600)
    parser.add_argument("--case", action="append", default=[])
    parser.add_argument("--current-only", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def self_test(topology: dict[str, Any]) -> None:
    assert len(CASES) >= 12
    assert set(REPOSITORIES) == {case["repository"] for case in CASES}
    for name in topology["automatic_nodes"]:
        assert node_path(topology, name)[-1] == name
    trace = parse_trace("TREE_TRACE path=core retrieval=BOUNDED manual=none refs=none")
    assert validate_trace(topology, trace)
    assert not validate_automatic_path(topology, ["core", "debugging"])
    assert any(case.get("manual_request") == "decision" for case in CASES)
    print("tree validation self-test: PASS")


def main() -> int:
    args = parse_args()
    topology = load_topology(args.topology.resolve())
    if args.self_test:
        self_test(topology)
        return 0
    if args.runs < 1 or args.workers < 1:
        raise SystemExit("runs and workers must be positive")
    selected_cases = set(args.case)
    unknown = selected_cases - {case["task_id"] for case in CASES}
    if unknown:
        raise SystemExit(f"unknown cases: {', '.join(sorted(unknown))}")

    repositories = resolve_repositories(args.repository_root.resolve(), args.repository)
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    output = (args.output or ROOT / "benchmark-results" / f"tree-{stamp}").resolve()
    output.mkdir(parents=True, exist_ok=True)

    baseline_ref = args.baseline_ref or topology.get("baseline_ref")
    baseline_dir: Path | None = None
    if not args.current_only:
        if not baseline_ref:
            raise RuntimeError("baseline_ref is required unless --current-only is used")
        baseline_dir = output / "baseline-skill"
        if not (baseline_dir / "SKILL.md").is_file():
            baseline_dir = bench.materialize_git_skill(str(baseline_ref), baseline_dir)

    eval_home = bench.prepare_eval_home(output / "eval-home")
    specs = build_specs(topology, args.runs, current_only=args.current_only, selected_cases=selected_cases)
    records: list[dict[str, Any]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(run_cell, spec, args, topology, repositories, baseline_dir, eval_home, output) for spec in specs]
        for future in concurrent.futures.as_completed(futures):
            records.append(future.result())

    records.sort(key=lambda row: (row["task_id"], row["variant"], row["repetition"]))
    rows_path = output / "results.jsonl"
    rows_path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in records), encoding="utf-8")
    report = summary(records, args.runs)
    report.update({
        "schema_version": VERSION,
        "model": MODEL,
        "reasoning": REASONING,
        "topology": topology,
        "baseline_ref": baseline_ref,
        "results_jsonl": str(rows_path),
    })
    (output / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Analyze evolvable router-tree benchmark results.

The analysis derives minimum-sufficient node sets from capability ceilings instead
of comparing adaptive behavior to a predefined gold route. Routing disagreement is
therefore evidence about topology, not automatically a model failure.
"""

from __future__ import annotations

import argparse
import json
import statistics
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable


QUALITY_NONINFERIORITY_MARGIN = 0.03
PROMOTE_THRESHOLD = 0.80
MERGE_AMBIGUITY_THRESHOLD = 0.20
MIN_TOPOLOGY_SAMPLE = 3


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, raw in enumerate(handle, 1):
            line = raw.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_number}: invalid JSON: {exc}") from exc
    return rows


def load_topology(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def ancestors(topology: dict[str, Any], node: str, *, include_self: bool = False) -> list[str]:
    nodes = topology["automatic_nodes"]
    result = [node] if include_self else []
    current = nodes[node].get("parent")
    while current is not None:
        result.append(current)
        current = nodes[current].get("parent")
    return result


def descendants(topology: dict[str, Any], node: str, *, include_self: bool = False) -> set[str]:
    nodes = topology["automatic_nodes"]
    result = {node} if include_self else set()
    stack = list(nodes[node].get("children", []))
    while stack:
        current = stack.pop()
        if current in result:
            continue
        result.add(current)
        stack.extend(nodes[current].get("children", []))
    return result


def is_ancestor(topology: dict[str, Any], ancestor: str, node: str) -> bool:
    return ancestor in ancestors(topology, node)


def determinate(rows: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    return [row for row in rows if row.get("passed") is not None]


def stable_pass(rows: Iterable[dict[str, Any]]) -> bool:
    selected = determinate(rows)
    return bool(selected) and all(row.get("passed") is True for row in selected)


def pass_rate(rows: Iterable[dict[str, Any]]) -> float | None:
    selected = determinate(rows)
    if not selected:
        return None
    return sum(row.get("passed") is True for row in selected) / len(selected)


def mean_or_none(rows: Iterable[dict[str, Any]], key: str) -> float | None:
    values = [float(row[key]) for row in rows if row.get(key) is not None]
    return statistics.mean(values) if values else None


def median_or_none(rows: Iterable[dict[str, Any]], key: str) -> float | None:
    values = [float(row[key]) for row in rows if row.get(key) is not None]
    return statistics.median(values) if values else None


def minimum_sufficient_set(topology: dict[str, Any], cap_status: dict[str, bool]) -> set[str]:
    qualified = {node for node, passed in cap_status.items() if passed}
    return {
        node
        for node in qualified
        if not any(parent in qualified for parent in ancestors(topology, node))
    }


def relation_to_minimum(topology: dict[str, Any], selected: str | None, minimum: set[str], passed: bool | None) -> str:
    if not minimum:
        return "quality_gap"
    if selected is None or selected not in topology["automatic_nodes"]:
        return "invalid_trace"
    if selected in minimum:
        return "exact_minimum" if passed else "quality_failure_at_minimum"
    if any(is_ancestor(topology, candidate, selected) for candidate in minimum):
        return "over_disclosure" if passed else "quality_failure_after_over_disclosure"
    if any(is_ancestor(topology, selected, candidate) for candidate in minimum):
        return "under_disclosure"
    return "alternate_branch"


def task_reports(rows: list[dict[str, Any]], topology: dict[str, Any]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[str(row["task_id"])].append(row)

    reports: list[dict[str, Any]] = []
    for task_id, task_rows in sorted(grouped.items()):
        sample = task_rows[0]
        if sample.get("manual_request"):
            adaptive = [row for row in task_rows if row["variant"] == "adaptive"]
            reports.append({
                "task_id": task_id,
                "repository": sample["repository"],
                "family": sample["family"],
                "manual_request": sample["manual_request"],
                "adaptive_stable_pass": stable_pass(adaptive),
                "manual_contract_stable": bool(adaptive) and all(row.get("manual_contract_ok") is True for row in determinate(adaptive)),
            })
            continue

        cap_status: dict[str, bool] = {}
        for node in topology["automatic_nodes"]:
            cap_rows = [row for row in task_rows if row["variant"] == f"cap:{node}"]
            cap_status[node] = stable_pass(cap_rows)
        minimum = minimum_sufficient_set(topology, cap_status)
        adaptive = [row for row in task_rows if row["variant"] == "adaptive"]
        terminals = Counter(row.get("selected_terminal_node") for row in determinate(adaptive) if row.get("selected_terminal_node"))
        relations = Counter(
            relation_to_minimum(topology, row.get("selected_terminal_node"), minimum, row.get("passed"))
            for row in determinate(adaptive)
        )
        reports.append({
            "task_id": task_id,
            "repository": sample["repository"],
            "family": sample["family"],
            "manual_request": None,
            "cap_stable_pass": cap_status,
            "minimum_sufficient_set": sorted(minimum, key=lambda name: topology["automatic_nodes"][name]["depth"]),
            "minimum_sufficient_depths": sorted({topology["automatic_nodes"][name]["depth"] for name in minimum}),
            "adaptive_stable_pass": stable_pass(adaptive),
            "adaptive_terminal_counts": dict(sorted(terminals.items())),
            "adaptive_relation_counts": dict(sorted(relations.items())),
            "adaptive_trace_stable": bool(adaptive) and len(terminals) == 1 and all(row.get("routing_trace_valid") is True for row in determinate(adaptive)),
        })
    return reports


def node_reports(rows: list[dict[str, Any]], tasks: list[dict[str, Any]], topology: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    automatic_tasks = [task for task in tasks if not task.get("manual_request")]
    for node, spec in topology["automatic_nodes"].items():
        parent = spec.get("parent")
        cap_rows = [row for row in rows if row["variant"] == f"cap:{node}" and not row.get("manual_request")]
        stable_cap_tasks = [task for task in automatic_tasks if task["cap_stable_pass"].get(node)]
        minimum_tasks = [task for task in automatic_tasks if node in task["minimum_sufficient_set"]]
        marginal_lift_tasks: list[dict[str, Any]] = []
        parent_only_tasks: list[dict[str, Any]] = []
        if parent is not None:
            marginal_lift_tasks = [
                task for task in automatic_tasks
                if task["cap_stable_pass"].get(node) and not task["cap_stable_pass"].get(parent)
            ]
            parent_only_tasks = [
                task for task in automatic_tasks
                if task["cap_stable_pass"].get(parent) and not task["cap_stable_pass"].get(node)
            ]
        adaptive_selected = [
            row for row in rows
            if row["variant"] == "adaptive" and row.get("selected_terminal_node") == node and not row.get("manual_request")
        ]
        result[node] = {
            "depth": spec["depth"],
            "parent": parent,
            "children": list(spec.get("children", [])),
            "cap_stable_pass_tasks": len(stable_cap_tasks),
            "minimum_sufficient_tasks": len(minimum_tasks),
            "marginal_lift_over_parent_tasks": len(marginal_lift_tasks),
            "parent_only_regression_tasks": len(parent_only_tasks),
            "adaptive_selected_cells": len(adaptive_selected),
            "adaptive_selected_tasks": len({row["task_id"] for row in adaptive_selected}),
            "cap_cost": {
                "tokens_mean": mean_or_none(determinate(cap_rows), "total_tokens"),
                "duration_seconds_mean": mean_or_none(determinate(cap_rows), "duration_seconds"),
                "tool_calls_mean": mean_or_none(determinate(cap_rows), "tool_calls"),
                "tokens_median": median_or_none(determinate(cap_rows), "total_tokens"),
            },
            "marginal_lift_task_ids": [task["task_id"] for task in marginal_lift_tasks],
            "minimum_sufficient_task_ids": [task["task_id"] for task in minimum_tasks],
        }
    return result


def topology_suggestions(tasks: list[dict[str, Any]], nodes: dict[str, Any], topology: dict[str, Any]) -> list[dict[str, Any]]:
    suggestions: list[dict[str, Any]] = []
    automatic_tasks = [task for task in tasks if not task.get("manual_request")]

    for node, report in nodes.items():
        if node == topology["root"]:
            continue
        if report["marginal_lift_over_parent_tasks"] == 0 and report["minimum_sufficient_tasks"] == 0:
            suggestions.append({
                "action": "REMOVE_CANDIDATE",
                "node": node,
                "reason": "Node never becomes minimum-sufficient and shows no stable capability lift over its parent in this sample.",
            })

        parent = report["parent"]
        if parent is not None:
            parent_subtree = descendants(topology, parent, include_self=True)
            scoped = [
                task for task in automatic_tasks
                if any(minimum in parent_subtree for minimum in task["minimum_sufficient_set"])
            ]
            required = [task for task in scoped if node in task["minimum_sufficient_set"]]
            if len(scoped) >= MIN_TOPOLOGY_SAMPLE and len(required) / len(scoped) >= PROMOTE_THRESHOLD:
                suggestions.append({
                    "action": "PROMOTE_OR_COLLAPSE_CANDIDATE",
                    "node": node,
                    "parent": parent,
                    "support": len(required),
                    "scope": len(scoped),
                    "reason": "The child is minimum-sufficient for most tasks in the parent scope; the disclosure boundary may be too shallow to justify a separate node.",
                })

    for parent, parent_spec in topology["automatic_nodes"].items():
        children = list(parent_spec.get("children", []))
        if len(children) < 2:
            continue
        relevant = [task for task in automatic_tasks if any(child in task["minimum_sufficient_set"] for child in children)]
        ambiguous = [task for task in relevant if sum(child in task["minimum_sufficient_set"] for child in children) >= 2]
        if len(relevant) >= MIN_TOPOLOGY_SAMPLE and len(ambiguous) / len(relevant) >= MERGE_AMBIGUITY_THRESHOLD:
            suggestions.append({
                "action": "MERGE_OR_MOVE_BOUNDARY_CANDIDATE",
                "parent": parent,
                "children": children,
                "ambiguous_tasks": [task["task_id"] for task in ambiguous],
                "reason": "Sibling capabilities are repeatedly co-minimum-sufficient; their current boundary may not buy enough specialization.",
            })

    failed_by_leaf_family: dict[tuple[str, str], list[str]] = defaultdict(list)
    for task in automatic_tasks:
        if task["adaptive_stable_pass"]:
            continue
        terminals = task.get("adaptive_terminal_counts", {})
        if not terminals:
            continue
        terminal = max(terminals, key=terminals.get)
        if topology["automatic_nodes"][terminal].get("children"):
            continue
        failed_by_leaf_family[(terminal, task["family"])].append(task["task_id"])
    for (leaf, family), task_ids in sorted(failed_by_leaf_family.items()):
        if len(task_ids) >= 2:
            suggestions.append({
                "action": "DEEPEN_OR_SPLIT_CANDIDATE",
                "node": leaf,
                "family": family,
                "tasks": task_ids,
                "reason": "A stable failure cluster ends at the same leaf; inspect whether an observable pre-load sub-capability earns a child.",
            })

    return suggestions


def quality_report(rows: list[dict[str, Any]], tasks: list[dict[str, Any]]) -> dict[str, Any]:
    arms: dict[str, Any] = {}
    for variant in ("no-skill", "baseline", "adaptive"):
        selected = [row for row in rows if row["variant"] == variant]
        if not selected:
            continue
        arms[variant] = {
            "cells": len(selected),
            "pass_rate": pass_rate(selected),
            "stable_tasks": sum(
                stable_pass([row for row in selected if row["task_id"] == task_id])
                for task_id in {row["task_id"] for row in selected}
            ),
            "tokens_mean": mean_or_none(determinate(selected), "total_tokens"),
            "duration_seconds_mean": mean_or_none(determinate(selected), "duration_seconds"),
            "tool_calls_mean": mean_or_none(determinate(selected), "tool_calls"),
        }

    adaptive = [row for row in rows if row["variant"] == "adaptive" and row.get("passed") is not None]
    automatic = [row for row in adaptive if not row.get("manual_request")]
    manual = [row for row in adaptive if row.get("manual_request")]
    adaptive_rate = arms.get("adaptive", {}).get("pass_rate")
    baseline_rate = arms.get("baseline", {}).get("pass_rate")
    no_skill_rate = arms.get("no-skill", {}).get("pass_rate")
    comparisons = []
    for name, comparator in (("baseline", baseline_rate), ("no-skill", no_skill_rate)):
        if adaptive_rate is not None and comparator is not None:
            comparisons.append({
                "comparator": name,
                "pass": adaptive_rate + QUALITY_NONINFERIORITY_MARGIN >= comparator,
                "candidate_pass_rate": adaptive_rate,
                "comparator_pass_rate": comparator,
                "margin": QUALITY_NONINFERIORITY_MARGIN,
            })
    manual_false = sum(row.get("spontaneous_manual_mode") is True for row in automatic)
    manual_explicit_fail = sum(row.get("manual_contract_ok") is not True for row in manual)
    trace_fail = sum(row.get("routing_trace_valid") is not True for row in adaptive)
    gate = all(item["pass"] for item in comparisons) and manual_false == 0 and manual_explicit_fail == 0 and trace_fail == 0
    return {
        "release_quality_gate": "PASS" if gate else "FAIL",
        "arms": arms,
        "noninferiority": comparisons,
        "automatic_spontaneous_manual_count": manual_false,
        "explicit_manual_contract_failures": manual_explicit_fail,
        "adaptive_trace_failures": trace_fail,
        "note": "Adaptive route exactness is diagnostic topology evidence, not a release gate. Delivered quality and manual-mode discipline gate the candidate.",
    }


def analyze(rows: list[dict[str, Any]], topology: dict[str, Any]) -> dict[str, Any]:
    tasks = task_reports(rows, topology)
    nodes = node_reports(rows, tasks, topology)
    relation_counts: Counter[str] = Counter()
    for task in tasks:
        if task.get("manual_request"):
            continue
        relation_counts.update(task.get("adaptive_relation_counts", {}))
    return {
        "schema_version": 1,
        "quality": quality_report(rows, tasks),
        "routing_diagnostics": {
            "relation_counts": dict(sorted(relation_counts.items())),
            "tasks_with_multiple_minimum_nodes": [
                task["task_id"] for task in tasks if not task.get("manual_request") and len(task["minimum_sufficient_set"]) > 1
            ],
            "tasks_without_qualified_cap": [
                task["task_id"] for task in tasks if not task.get("manual_request") and not task["minimum_sufficient_set"]
            ],
        },
        "nodes": nodes,
        "topology_suggestions": topology_suggestions(tasks, nodes, topology),
        "tasks": tasks,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("results", type=Path, help="tree_validation.py results.jsonl")
    parser.add_argument("--topology", type=Path, default=Path(__file__).resolve().parent / "tree_topology.json")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    report = analyze(load_jsonl(args.results), load_topology(args.topology))
    text = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True)
    if args.output:
        args.output.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

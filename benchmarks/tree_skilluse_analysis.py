#!/usr/bin/env python3
"""Derive Trigger / Compliance / Boundary metrics from tree benchmark ceilings.

This companion analysis intentionally does not introduce human-authored gold routes.
A node's positive routing opportunities are tasks where that node is empirically
minimum-sufficient while its parent is not. Negative opportunities are tasks already
stable-passing at the parent. Adaptive traces are then scored against those
empirically derived opportunity sets.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from tree_analysis import (
    descendants,
    determinate,
    load_jsonl,
    load_topology,
    task_reports,
)


MIN_POSITIVE_TASKS = 2
MIN_POSITIVE_REPOSITORIES = 2
TRIGGER_RECALL_TARGET = 0.80
BOUNDARY_SPECIFICITY_TARGET = 0.90
COMPLIANCE_TARGET = 0.90


def _mean(rows: Iterable[dict[str, Any]], key: str) -> float | None:
    values = [float(row[key]) for row in rows if row.get(key) is not None]
    return statistics.mean(values) if values else None


def _task_rows(rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[str(row["task_id"])].append(row)
    return grouped


def _selected_in_subtree(topology: dict[str, Any], row: dict[str, Any], node: str) -> bool:
    terminal = row.get("selected_terminal_node")
    if not terminal:
        return False
    return terminal == node or terminal in descendants(topology, node)


def _cap_rows(task_rows: list[dict[str, Any]], node: str) -> list[dict[str, Any]]:
    return [row for row in task_rows if row.get("variant") == f"cap:{node}"]


def _adaptive_rows(task_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return determinate(row for row in task_rows if row.get("variant") == "adaptive")


def analyze_node(
    rows: list[dict[str, Any]],
    topology: dict[str, Any],
    tasks: list[dict[str, Any]],
    node: str,
) -> dict[str, Any]:
    spec = topology["automatic_nodes"][node]
    parent = spec.get("parent")
    if parent is None:
        raise ValueError("root has no Skill-Use routing metrics")

    grouped = _task_rows(rows)
    ordinary_tasks = [task for task in tasks if not task.get("manual_request")]

    positive = [
        task for task in ordinary_tasks
        if node in task["minimum_sufficient_set"]
        and not task["cap_stable_pass"].get(parent)
    ]
    negative = [
        task for task in ordinary_tasks
        if task["cap_stable_pass"].get(parent)
    ]

    positive_rows: list[dict[str, Any]] = []
    negative_rows: list[dict[str, Any]] = []
    triggered_rows: list[dict[str, Any]] = []
    positive_triggered: list[dict[str, Any]] = []
    false_triggered: list[dict[str, Any]] = []

    for task in positive:
        adaptive = _adaptive_rows(grouped[task["task_id"]])
        positive_rows.extend(adaptive)
        selected = [row for row in adaptive if _selected_in_subtree(topology, row, node)]
        positive_triggered.extend(selected)
        triggered_rows.extend(selected)

    for task in negative:
        adaptive = _adaptive_rows(grouped[task["task_id"]])
        negative_rows.extend(adaptive)
        selected = [row for row in adaptive if _selected_in_subtree(topology, row, node)]
        false_triggered.extend(selected)
        triggered_rows.extend(selected)

    trigger_recall = (
        len(positive_triggered) / len(positive_rows) if positive_rows else None
    )
    boundary_specificity = (
        1.0 - len(false_triggered) / len(negative_rows) if negative_rows else None
    )
    compliance_when_triggered = (
        sum(row.get("passed") is True for row in triggered_rows) / len(triggered_rows)
        if triggered_rows
        else None
    )

    parent_positive_caps: list[dict[str, Any]] = []
    node_positive_caps: list[dict[str, Any]] = []
    for task in positive:
        task_rows = grouped[task["task_id"]]
        parent_positive_caps.extend(determinate(_cap_rows(task_rows, parent)))
        node_positive_caps.extend(determinate(_cap_rows(task_rows, node)))

    def delta(key: str) -> float | None:
        child = _mean(node_positive_caps, key)
        base = _mean(parent_positive_caps, key)
        return None if child is None or base is None else child - base

    positive_repositories = sorted({task["repository"] for task in positive})
    enough_signal = (
        len(positive) >= MIN_POSITIVE_TASKS
        and len(positive_repositories) >= MIN_POSITIVE_REPOSITORIES
    )
    route_ok = (
        trigger_recall is not None
        and trigger_recall >= TRIGGER_RECALL_TARGET
        and boundary_specificity is not None
        and boundary_specificity >= BOUNDARY_SPECIFICITY_TARGET
        and compliance_when_triggered is not None
        and compliance_when_triggered >= COMPLIANCE_TARGET
    )

    return {
        "node": node,
        "parent": parent,
        "depth": spec["depth"],
        "positive_lift_tasks": [task["task_id"] for task in positive],
        "positive_lift_task_count": len(positive),
        "positive_lift_repositories": positive_repositories,
        "negative_parent_sufficient_tasks": [task["task_id"] for task in negative],
        "trigger": {
            "opportunities": len(positive_rows),
            "hits": len(positive_triggered),
            "recall": trigger_recall,
            "target": TRIGGER_RECALL_TARGET,
        },
        "compliance": {
            "triggered_cells": len(triggered_rows),
            "passing_triggered_cells": sum(row.get("passed") is True for row in triggered_rows),
            "rate": compliance_when_triggered,
            "target": COMPLIANCE_TARGET,
        },
        "boundary": {
            "negative_opportunities": len(negative_rows),
            "false_triggers": len(false_triggered),
            "specificity": boundary_specificity,
            "target": BOUNDARY_SPECIFICITY_TARGET,
        },
        "positive_capability_cost_delta_vs_parent": {
            "tokens_mean": delta("total_tokens"),
            "duration_seconds_mean": delta("duration_seconds"),
            "tool_calls_mean": delta("tool_calls"),
        },
        "promotion_signal_gate": "PASS" if enough_signal and route_ok else "FAIL",
        "promotion_signal_requirements": {
            "minimum_positive_tasks": MIN_POSITIVE_TASKS,
            "minimum_positive_repositories": MIN_POSITIVE_REPOSITORIES,
            "note": (
                "This gate is necessary but not sufficient. Release promotion still "
                "requires the main quality/non-inferiority gate and review of cost, "
                "trace validity, leakage, and task realism."
            ),
        },
    }


def analyze(rows: list[dict[str, Any]], topology: dict[str, Any]) -> dict[str, Any]:
    tasks = task_reports(rows, topology)
    nodes = {}
    for node, spec in topology["automatic_nodes"].items():
        if spec.get("parent") is None:
            continue
        nodes[node] = analyze_node(rows, topology, tasks, node)
    return {
        "schema_version": 1,
        "method": "capability-derived-skill-use",
        "nodes": nodes,
        "notes": [
            "Trigger positives are derived from empirically minimum-sufficient child capability, not human gold labels.",
            "Boundary negatives are tasks already stable-passing at the parent.",
            "Compliance is delivered pass rate among adaptive cells that selected the node/subtree.",
            "Do not promote from this report alone; use tree_analysis.py release quality and topology diagnostics too.",
        ],
    }


def self_test() -> None:
    topology = {
        "root": "core",
        "automatic_nodes": {
            "core": {"depth": 0, "parent": None, "children": ["impl"]},
            "impl": {"depth": 1, "parent": "core", "children": ["security"]},
            "security": {"depth": 2, "parent": "impl", "children": []},
        },
    }

    def row(task: str, variant: str, passed: bool, terminal: str | None = None) -> dict[str, Any]:
        return {
            "task_id": task,
            "repository": "r1" if task == "positive" else "r2",
            "family": "x",
            "manual_request": None,
            "variant": variant,
            "passed": passed,
            "selected_terminal_node": terminal,
            "total_tokens": 100,
            "duration_seconds": 1,
            "tool_calls": 1,
        }

    rows = [
        row("positive", "cap:core", False),
        row("positive", "cap:impl", False),
        row("positive", "cap:security", True),
        row("positive", "adaptive", True, "security"),
        row("negative", "cap:core", False),
        row("negative", "cap:impl", True),
        row("negative", "cap:security", True),
        row("negative", "adaptive", True, "impl"),
    ]
    report = analyze(rows, topology)
    security = report["nodes"]["security"]
    assert security["trigger"]["recall"] == 1.0
    assert security["boundary"]["specificity"] == 1.0
    assert security["compliance"]["rate"] == 1.0
    print("tree skill-use analysis self-test: PASS")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("results", type=Path, nargs="?")
    parser.add_argument("--topology", type=Path, default=Path(__file__).with_name("tree_topology.json"))
    parser.add_argument("--output", type=Path)
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        self_test()
        return 0
    if args.results is None:
        raise SystemExit("results.jsonl is required unless --self-test is used")
    rows = load_jsonl(args.results)
    topology = load_topology(args.topology)
    report = analyze(rows, topology)
    text = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

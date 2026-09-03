#!/usr/bin/env python3
"""Run the original tree benchmark quietly in fresh, bounded subprocess shards."""

from __future__ import annotations

import concurrent.futures
import datetime as dt
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

if __package__:
    from . import tree_validation as validation
else:
    import tree_validation as validation


IDENTITY_FIELDS = {
    "head", "baseline_ref", "model", "reasoning", "harness_version", "retrieval_metrics_version",
    "timeout", "workers", "repetitions", "repositories", "file_sha256", "skill_bundle_sha256",
    "runtime_file_sha256", "baseline_runtime_file_sha256", "baseline_bundle_sha256", "topology_sha256",
    "codex_sha256", "codex_version", "python", "platform", "path_sha256", "build_conditions",
}


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def common_identity(manifest: dict[str, Any]) -> dict[str, Any]:
    missing = IDENTITY_FIELDS - manifest.keys()
    if missing:
        raise ValueError(f"manifest missing identity fields: {sorted(missing)}")
    return {key: value for key, value in manifest.items() if key not in {"specs", "expected_specs", "shard"}}


def shard_name(index: int) -> str:
    return f"shard-{index:03d}"


def child_command(args: Any, output: Path, index: int, count: int) -> list[str]:
    command = [
        sys.executable, str(validation.HERE / "tree_validation.py"),
        "--runs", str(args.runs), "--workers", "1", "--output", str(output),
        "--repository-root", str(args.repository_root.resolve()),
        "--topology", str(args.topology.resolve()), "--codex", args.codex,
        "--timeout", str(args.timeout), "--shard-index", str(index), "--shard-count", str(count),
    ]
    if args.baseline_ref:
        command.extend(["--baseline-ref", args.baseline_ref])
    if args.current_only:
        command.append("--current-only")
    for source in args.repository:
        command.extend(["--repository", source])
    for case in args.case:
        command.extend(["--case", case])
    return command


def run_shard(command: list[str], logs: Path, index: int) -> int:
    with (logs / f"{shard_name(index)}.stdout.txt").open("w", encoding="utf-8") as stdout, \
            (logs / f"{shard_name(index)}.stderr.txt").open("w", encoding="utf-8") as stderr:
        return subprocess.run(
            command, cwd=validation.ROOT, stdout=stdout, stderr=stderr, check=False,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        ).returncode


def aggregate(output: Path, plan: dict[str, Any]) -> dict[str, Any]:
    """Reject partial or incompatible shards before publishing aggregate artifacts."""
    expected = [tuple(spec) for spec in plan["specs"]]
    count = plan["shard_count"]
    if len(set(expected)) != len(expected):
        raise ValueError("duplicate expected cells")
    rebuilt = validation.build_specs(plan["topology"], plan["repetitions"],
                                     current_only=plan["current_only"], selected_cases=set(plan["selected_cases"]))
    if expected != rebuilt:
        raise ValueError("plan differs from the original full matrix specification")
    shard_root = output / "shards"
    if {path.name for path in shard_root.iterdir()} != {shard_name(index) for index in range(count)}:
        raise ValueError("missing or unexpected shard directories")
    identity = None
    records = []
    sources = []
    for index in range(count):
        shard = shard_root / shard_name(index)
        assigned = validation.select_shard(expected, index, count)
        manifest = json.loads((shard / "manifest.json").read_text(encoding="utf-8"))
        if manifest.get("shard") != {"index": index, "count": count, "max_cells": validation.SHARD_SIZE}:
            raise ValueError(f"incorrect shard identity: {shard}")
        if manifest.get("expected_specs") != plan["specs"] or manifest.get("specs") != [list(spec) for spec in assigned]:
            raise ValueError(f"incorrect shard assignment: {shard}")
        common = common_identity(manifest)
        if identity is not None and common != identity:
            raise ValueError(f"incompatible common manifest: {shard}")
        identity = common
        if (common["workers"] != 1 or common["repetitions"] != plan["repetitions"]
                or common["baseline_ref"] != plan["baseline_ref"]
                or common["topology_sha256"] != plan["topology_sha256"]):
            raise ValueError(f"manifest does not match launch plan: {shard}")
        if not plan["current_only"] and (not common["baseline_bundle_sha256"] or not common["baseline_runtime_file_sha256"]):
            raise ValueError(f"baseline runtime identity missing: {shard}")
        rows = [json.loads(line) for line in (shard / "results.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
        actual = [(row["task_id"], row["variant"], row["repetition"]) for row in rows]
        if len(actual) != len(assigned) or set(actual) != set(assigned):
            raise ValueError(f"missing, duplicate, or unexpected result cells: {shard}")
        for row in rows:
            cell = shard / "cells" / row["task_id"] / row["variant"].replace(":", "-") / f"r{row['repetition']:03d}"
            for filename in ("prompt.txt", "round1.jsonl", "round1.stderr.txt", "answer.md", "result.json"):
                if not (cell / filename).is_file():
                    raise ValueError(f"missing raw cell artifact: {cell / filename}")
            if json.loads((cell / "result.json").read_text(encoding="utf-8")) != row:
                raise ValueError(f"result differs from raw cell: {cell}")
            records.append({**row, "shard_index": index, "cell_directory": str(cell.resolve())})
        sources.append({"index": index, "output": str(shard.resolve()), "cells": len(rows),
                        "manifest_sha256": validation.bench.sha256(shard / "manifest.json")})
    if identity is None or len(records) != len(expected):
        raise ValueError("incomplete matrix")
    records.sort(key=lambda row: (row["task_id"], row["variant"], row["repetition"]))
    rows_path = output / "results.jsonl"
    report = validation.summary(records, plan["repetitions"])
    report.update({"schema_version": validation.VERSION, "model": identity["model"], "reasoning": identity["reasoning"],
                   "topology": plan["topology"], "baseline_ref": identity["baseline_ref"], "results_jsonl": str(rows_path)})
    manifest = {**identity, "specs": plan["specs"], "workers": plan["workers"], "workers_per_shard": 1,
                "shards": sources, "max_cells_per_shard": validation.SHARD_SIZE}
    for filename in ("results.jsonl", "report.json", "manifest.json"):
        if (output / filename).exists():
            raise FileExistsError(f"aggregate output already exists: {output / filename}")
    rows_path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in records), encoding="utf-8")
    write_json(output / "report.json", report)
    write_json(output / "manifest.json", manifest)
    return report


def launch(args: Any) -> tuple[Path, dict[str, Any]]:
    if not 1 <= args.workers <= 8 or args.runs < 1:
        raise ValueError("runs must be positive and concurrent shard workers must be between 1 and 8")
    if args.shard_index is not None or args.shard_count is not None or args.self_test:
        raise ValueError("use tree_validation.py directly for shard selection or self-test")
    unknown = set(args.case) - {case["task_id"] for case in validation.CASES}
    if unknown:
        raise ValueError(f"unknown cases: {sorted(unknown)}")
    topology = validation.load_topology(args.topology.resolve())
    specs = validation.build_specs(topology, args.runs, current_only=args.current_only, selected_cases=set(args.case))
    count = (len(specs) + validation.SHARD_SIZE - 1) // validation.SHARD_SIZE
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    output = (args.output or validation.ROOT / "benchmark-results" / f"tree-shards-{stamp}").resolve()
    plan = {"specs": [list(spec) for spec in specs], "shard_count": count, "workers": args.workers,
            "repetitions": args.runs, "current_only": args.current_only, "selected_cases": sorted(set(args.case)),
            "baseline_ref": args.baseline_ref or topology.get("baseline_ref"), "topology": topology,
            "topology_sha256": validation.bench.sha256(args.topology.resolve())}
    output.mkdir(parents=True, exist_ok=False)
    (output / "shards").mkdir()
    logs = output / "logs"
    logs.mkdir()
    write_json(output / "plan.json", plan)
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(run_shard, child_command(args, output / "shards" / shard_name(index), index, count), logs, index): index
                   for index in range(count)}
        failed = []
        for future in concurrent.futures.as_completed(futures):
            try:
                code = future.result()
            except OSError as exc:
                failed.append({"index": futures[future], "error": str(exc)})
            else:
                if code:
                    failed.append({"index": futures[future], "exit_status": code})
    if failed:
        write_json(output / "failed-shards.json", failed)
        raise RuntimeError(f"shard process failures; no retries or aggregate: {output / 'failed-shards.json'}")
    return output, aggregate(output, plan)


def main() -> int:
    args = validation.parse_args(default_workers=8)
    output, report = launch(args)
    print(json.dumps({"output": str(output), "cells": sum(arm["cells"] for arm in report["arms"].values())}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

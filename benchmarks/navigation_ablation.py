#!/usr/bin/env python3
"""Paired native-Skill navigation ablation on a real Git repository."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import shutil
import statistics
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import run_catalog


run_catalog.configure()
bench = run_catalog.bench


def tracked_files(repository: Path) -> list[Path]:
    result = bench.run_command(["git", "ls-files", "-z"], repository)
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "git ls-files failed")
    return [Path(item) for item in result.stdout.split("\0") if item]


def copy_tracked(repository: Path, destination: Path) -> list[Path]:
    files = tracked_files(repository)
    destination.mkdir(parents=True)
    for relative in files:
        source = repository / relative
        if not source.is_file():
            continue
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    return files


def tree_digest(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(path for path in root.rglob("*") if path.is_file()):
        relative = path.relative_to(root).as_posix()
        if relative == ".practical-coding.yaml":
            continue
        digest.update(relative.encode())
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def evidence_present(answer: str, required: str) -> bool:
    lowered = answer.lower()
    term = required.lower()
    if term in lowered:
        return True
    suffix = Path(required).suffix.lower()
    return bool(suffix in {".java", ".py", ".ts", ".tsx", ".js", ".vue"} and Path(required).stem.lower() in lowered)


def summarize(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for arm in ("source", "graph"):
        cells = [record for record in records if record["arm"] == arm]
        successful = [record for record in cells if record["passed"]]
        row: dict[str, Any] = {
            "arm": arm,
            "n": len(cells),
            "successful_n": len(successful),
            "status": "qualified" if len(cells) >= 3 and len(successful) == len(cells) else "provisional",
            "pass_rate": sum(bool(cell["passed"]) for cell in cells) / len(cells),
            "route_rate": sum(bool(cell["route_ok"]) for cell in cells) / len(cells),
            "backend_rate": sum(bool(cell["backend_ok"]) for cell in cells) / len(cells),
        }
        for metric in ("uncached_input_tokens", "output_tokens", "total_tokens", "duration_seconds", "tool_calls"):
            values = [float(cell[metric]) for cell in cells]
            row[f"{metric}_median"] = statistics.median(values)
        if successful:
            row["successful_median"] = {
                metric: statistics.median(float(cell[metric]) for cell in successful)
                for metric in ("uncached_input_tokens", "output_tokens", "total_tokens", "duration_seconds", "tool_calls")
            }
        if arm == "graph" and cells:
            cold = min(cells, key=lambda cell: cell["repetition"])
            warm = [cell for cell in cells if cell["repetition"] != cold["repetition"]]
            row["cold"] = {metric: cold[metric] for metric in ("uncached_input_tokens", "output_tokens", "total_tokens", "duration_seconds", "tool_calls")}
            if warm:
                row["warm_median"] = {
                    metric: statistics.median(float(cell[metric]) for cell in warm)
                    for metric in ("uncached_input_tokens", "output_tokens", "total_tokens", "duration_seconds", "tool_calls")
                }
                warm_successful = [cell for cell in warm if cell["passed"]]
                if warm_successful:
                    row["warm_successful_median"] = {
                        metric: statistics.median(float(cell[metric]) for cell in warm_successful)
                        for metric in ("uncached_input_tokens", "output_tokens", "total_tokens", "duration_seconds", "tool_calls")
                    }
        rows.append(row)
    return rows


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=Path)
    parser.add_argument("--prompt")
    parser.add_argument("--required", action="append", default=[])
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--rescore", type=Path, help="reapply answer-evidence checks to an existing artifact")
    parser.add_argument("--codex", default=os.environ.get("CODEX_BIN", "codex"))
    parser.add_argument("--timeout", type=float, default=600)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.rescore:
        output = args.rescore.resolve()
        manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
        records = json.loads((output / "results.json").read_text(encoding="utf-8"))
        for record in records:
            answer = (output / "cells" / record["arm"] / f"r{record['repetition']:03d}" / "answer.md").read_text(encoding="utf-8")
            record["required_ok"] = all(evidence_present(answer, term) for term in manifest["required"])
            record["passed"] = bool(
                not record.get("timed_out")
                and not record.get("exit_status")
                and record["route_ok"]
                and record["backend_ok"]
                and record["required_ok"]
                and record["unchanged"]
            )
        (output / "results.json").write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")
        (output / "summary.json").write_text(json.dumps(summarize(records), indent=2) + "\n", encoding="utf-8")
        manifest["rescored_at"] = dt.datetime.now(dt.timezone.utc).isoformat()
        (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        print(f"rescored {output}")
        return 0 if all(record["passed"] for record in records) else 2
    if not args.repository or not args.prompt or not args.output:
        raise SystemExit("--repository, --prompt, and --output are required unless --rescore is used")
    if args.runs < 1:
        raise SystemExit("runs must be positive")
    repository = args.repository.resolve()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    eval_home = bench.prepare_eval_home(output / "native-home")
    skill = bench.install_native_skill(eval_home, bench.ROOT)
    codex = bench.resolve_codex(args.codex)

    workspaces: dict[str, Path] = {}
    files: list[Path] = []
    for arm in ("source", "graph"):
        workspace = output / "workspaces" / arm
        copied = copy_tracked(repository, workspace)
        files = copied if not files else files
        if arm == "graph":
            (workspace / ".practical-coding.yaml").write_text("codebase_memory:\n  enabled: true\n", encoding="utf-8")
        workspaces[arm] = workspace

    initial_digests = {arm: tree_digest(workspace) for arm, workspace in workspaces.items()}
    records: list[dict[str, Any]] = []
    request = (
        args.prompt.strip()
        + "\n\nThis is a read-only structural navigation task. Do not modify files. "
          "Report exact repository-relative paths and symbols, then stop when the requested map is complete."
    )
    env = os.environ.copy()
    env["CODEX_HOME"] = str(eval_home)
    for repetition in range(1, args.runs + 1):
        order = ("source", "graph") if repetition % 2 else ("graph", "source")
        for arm in order:
            cell = output / "cells" / arm / f"r{repetition:03d}"
            cell.mkdir(parents=True)
            transcript = cell / "round1.jsonl"
            stderr = cell / "round1.stderr.txt"
            (cell / "prompt.txt").write_text(request + "\n", encoding="utf-8")
            code, timed_out, forced, duration = bench.run_codex(
                bench.codex_command(codex, workspaces[arm]),
                request,
                workspaces[arm],
                env,
                transcript,
                stderr,
                args.timeout,
            )
            parsed = bench.parse_transcript(transcript)
            answer = parsed["answer"]
            behavior = bench.behavior_score(
                parsed["tool_commands"],
                "navigation.md",
                parsed["tool_outputs"],
                expected_backend=arm,
            )
            required_ok = all(evidence_present(answer, term) for term in args.required)
            unchanged = tree_digest(workspaces[arm]) == initial_digests[arm]
            infrastructure_error = timed_out or (code and not forced)
            record = {
                "arm": arm,
                "repetition": repetition,
                "passed": bool(not infrastructure_error and behavior["passed"] and required_ok and unchanged),
                "route_ok": behavior["routing_ok"],
                "backend_ok": behavior["backend_ok"],
                "required_ok": required_ok,
                "unchanged": unchanged,
                "exit_status": code,
                "timed_out": timed_out,
                "duration_seconds": duration,
                "tool_calls": parsed["tool_calls"],
                **parsed["usage"],
            }
            records.append(record)
            (cell / "answer.md").write_text(answer + "\n", encoding="utf-8")
            (cell / "result.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
            print(f"[{len(records)}/{2 * args.runs}] {arm}/r{repetition} pass={record['passed']}", flush=True)

    summary = summarize(records)
    manifest = {
        "runner": "navigation_ablation.py",
        "model": bench.MODEL,
        "reasoning": bench.REASONING,
        "repository": str(repository),
        "repository_head": bench.run_command(["git", "rev-parse", "HEAD"], repository).stdout.strip(),
        "tracked_files": len(files),
        "tracked_bytes": sum((repository / path).stat().st_size for path in files if (repository / path).is_file()),
        "runs": args.runs,
        "prompt": args.prompt,
        "required": args.required,
        "skill_bundle_sha256": bench.bundle_sha256(bench.ROOT),
        "native_install": str(skill),
        "completed_at": dt.datetime.now(dt.timezone.utc).isoformat(),
    }
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    (output / "results.json").write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")
    (output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {output}")
    return 0 if all(record["passed"] for record in records) else 2


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Run a paired Practical Coding ablation on SkillsBench."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import random
import re
import shutil
import statistics
import subprocess
import tempfile
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

DATASET = "skillsbench@1.1"
DATASET_NAME = "skillsbench"
DATASET_VERSION = "1.1"
SKILLSBENCH_REPO = "https://github.com/benchflow-ai/skillsbench.git"
SKILLSBENCH_REF = "v1.1"
BENCHFLOW_VERSION = "0.6.2"
AGENT = "codex-acp"
MODEL = "gpt-5.6-luna"
REASONING = "medium"
ROOT = Path(__file__).resolve().parents[2]
SMOKE_TASKS = (
    "fix-build-agentops",
    "spring-boot-jakarta-migration",
    "react-performance-debugging",
)
AUTH_ENV_VARS = ("OPENAI_API_KEY", "CODEX_API_KEY", "CODEX_ACCESS_TOKEN")


def run_command(command: list[str], cwd: Path | None = None, timeout: float | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=str(cwd) if cwd else None,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=timeout,
        check=False,
    )


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def skill_bundle_sha256(root: Path) -> str:
    digest = hashlib.sha256()
    paths = [root / "SKILL.md", *sorted((root / "references").glob("*.md"))]
    for path in paths:
        if not path.is_file():
            continue
        digest.update(str(path.relative_to(root)).replace("\\", "/").encode())
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def resolve_uvx() -> list[str]:
    uvx = shutil.which("uvx")
    if uvx:
        return [uvx, "--from", f"benchflow=={BENCHFLOW_VERSION}", "bench"]
    uv = shutil.which("uv")
    if uv:
        return [uv, "tool", "run", "--from", f"benchflow=={BENCHFLOW_VERSION}", "bench"]
    raise FileNotFoundError("uv/uvx is required. Install uv, then rerun the external benchmark.")


def check_prerequisites(sandbox: str) -> dict[str, str]:
    if not shutil.which("git"):
        raise FileNotFoundError("git is required")
    codex = shutil.which("codex")
    if not codex:
        raise FileNotFoundError("Codex CLI is required for the codex-acp SkillsBench arm")
    uv_prefix = resolve_uvx()
    auth_json = Path.home() / ".codex" / "auth.json"
    if not any(os.environ.get(name) for name in AUTH_ENV_VARS) and not auth_json.is_file():
        raise RuntimeError("Codex authentication was not found. Run `codex login` or provide a supported Codex/OpenAI credential.")
    versions: dict[str, str] = {}
    for name, command in (
        ("git", [shutil.which("git") or "git", "--version"]),
        ("codex", [codex, "--version"]),
        ("uv", [uv_prefix[0], "--version"]),
    ):
        result = run_command(command)
        if result.returncode:
            raise RuntimeError(f"failed to inspect {name}: {result.stdout[-1000:]}")
        versions[name] = result.stdout.strip()
    if sandbox == "docker":
        docker = shutil.which("docker")
        if not docker:
            raise FileNotFoundError("Docker is required for --sandbox docker")
        info = run_command([docker, "info"], timeout=30)
        if info.returncode:
            raise RuntimeError("Docker is installed but the daemon is unavailable")
        versions["docker"] = run_command([docker, "--version"]).stdout.strip()
    return versions


def ensure_skillsbench_checkout(cache_root: Path) -> tuple[Path, str]:
    checkout = cache_root / f"skillsbench-{DATASET_VERSION}"
    checkout.parent.mkdir(parents=True, exist_ok=True)
    if not checkout.exists():
        clone = run_command([
            shutil.which("git") or "git",
            "clone",
            "--filter=blob:none",
            "--depth",
            "1",
            "--branch",
            SKILLSBENCH_REF,
            SKILLSBENCH_REPO,
            str(checkout),
        ])
        if clone.returncode:
            raise RuntimeError(f"failed to clone SkillsBench {SKILLSBENCH_REF}: {clone.stdout[-3000:]}")
    head = run_command([shutil.which("git") or "git", "rev-parse", "HEAD"], checkout)
    tag = run_command([shutil.which("git") or "git", "describe", "--tags", "--exact-match"], checkout)
    if head.returncode or tag.returncode or tag.stdout.strip() != SKILLSBENCH_REF:
        raise RuntimeError(f"SkillsBench metadata checkout must be exactly {SKILLSBENCH_REF}")
    return checkout, head.stdout.strip()


def load_dataset_roster(checkout: Path) -> list[str]:
    registry = json.loads((checkout / "registry.json").read_text(encoding="utf-8"))
    for entry in registry:
        if entry.get("name") == DATASET_NAME and str(entry.get("version")) == DATASET_VERSION:
            names = [str(task["name"]) for task in entry.get("tasks", [])]
            if not names:
                raise RuntimeError(f"{DATASET} has an empty registry roster")
            return names
    raise RuntimeError(f"{DATASET} is missing from SkillsBench registry.json")


def task_category(task_md: Path) -> str | None:
    text = task_md.read_text(encoding="utf-8", errors="replace")
    frontmatter = text.split("---", 2)
    if len(frontmatter) < 3:
        return None
    match = re.search(r"(?m)^\s*category:\s*['\"]?([a-z0-9-]+)", frontmatter[1])
    return match.group(1) if match else None


def discover_tasks(checkout: Path, profile: str, explicit: Iterable[str] = ()) -> list[str]:
    roster = load_dataset_roster(checkout)
    roster_set = set(roster)
    explicit = [item for item in explicit if item]
    if explicit:
        unknown = sorted(set(explicit) - roster_set)
        if unknown:
            raise ValueError(f"tasks are not in {DATASET}: {unknown}")
        return list(dict.fromkeys(explicit))
    software = [
        name
        for name in roster
        if task_category(checkout / "tasks" / name / "task.md") == "software-engineering"
    ]
    if profile == "smoke":
        preferred = [name for name in SMOKE_TASKS if name in software]
        return preferred if len(preferred) == len(SMOKE_TASKS) else software[:3]
    if profile == "standard":
        if not software:
            raise RuntimeError("no software-engineering tasks were discovered")
        return software
    if profile == "full":
        return roster
    raise ValueError(profile)


def stage_practical_skill(output: Path) -> Path:
    skills_root = output / "staged-skills"
    destination = skills_root / "practical-coding"
    if destination.exists():
        shutil.rmtree(destination)
    destination.mkdir(parents=True)
    shutil.copy2(ROOT / "SKILL.md", destination / "SKILL.md")
    references = ROOT / "references"
    if references.is_dir():
        shutil.copytree(references, destination / "references")
    return skills_root


def bench_command(
    *,
    jobs_dir: Path,
    tasks: list[str],
    sandbox: str,
    workers: int,
    model: str,
    reasoning: str,
    skill_mode: str,
    skills_root: Path | None = None,
) -> list[str]:
    command = [
        *resolve_uvx(),
        "eval",
        "run",
        "-d",
        DATASET,
        "--agent",
        AGENT,
        "--model",
        model,
        "--reasoning-effort",
        reasoning,
        "--sandbox",
        sandbox,
        "--concurrency",
        str(workers),
        "--jobs-dir",
        str(jobs_dir),
        "--skill-mode",
        skill_mode,
        "--quiet",
    ]
    if skill_mode == "with-skill":
        if skills_root is None:
            raise ValueError("skills_root is required for with-skill")
        command += ["--skills-dir", str(skills_root)]
    for task in tasks:
        command += ["--include", task]
    return command


def oracle_command(*, jobs_dir: Path, tasks: list[str], sandbox: str, workers: int) -> list[str]:
    command = [
        *resolve_uvx(),
        "eval",
        "run",
        "-d",
        DATASET,
        "--agent",
        "oracle",
        "--sandbox",
        sandbox,
        "--concurrency",
        str(workers),
        "--jobs-dir",
        str(jobs_dir),
        "--skill-mode",
        "no-skill",
        "--quiet",
    ]
    for task in tasks:
        command += ["--include", task]
    return command


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def _reward(result: dict[str, Any]) -> float | None:
    rewards = result.get("rewards")
    if isinstance(rewards, dict):
        value = rewards.get("reward")
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return float(value)
    value = result.get("reward")
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)
    return None


def _task_id(result: dict[str, Any], rollout_dir: Path) -> str:
    direct = result.get("task_name") or result.get("task_id")
    if direct:
        return str(direct)
    task = result.get("task")
    if isinstance(task, dict) and task.get("id"):
        return str(task["id"])
    config = _read_json(rollout_dir / "config.json") or {}
    direct = config.get("task_name") or config.get("task_id")
    if direct:
        return str(direct)
    task = config.get("task")
    if isinstance(task, dict) and task.get("id"):
        return str(task["id"])
    return rollout_dir.name


def _excluded_reason(result: dict[str, Any], reward: float | None) -> str | None:
    if result.get("healthy") is False:
        return "unhealthy"
    if result.get("partial_trajectory") is True:
        return "partial_trajectory"
    if reward is not None:
        return None
    for field in ("error", "verifier_error", "export_error"):
        if result.get(field):
            return field
    return "unscored"


def load_job_rewards(job_dir: Path) -> dict[str, dict[str, Any]]:
    by_task: dict[str, dict[str, Any]] = {}
    duplicates: dict[str, list[str]] = defaultdict(list)
    for result_path in sorted(job_dir.rglob("result.json")):
        result = _read_json(result_path)
        if result is None:
            continue
        reward = _reward(result)
        task_id = _task_id(result, result_path.parent)
        row = {
            "task_id": task_id,
            "reward": reward,
            "passed": reward == 1.0,
            "excluded_reason": _excluded_reason(result, reward),
            "path": str(result_path),
        }
        if task_id in by_task:
            duplicates[task_id].extend([by_task[task_id]["path"], str(result_path)])
        else:
            by_task[task_id] = row
    if duplicates:
        details = "; ".join(f"{task}: {sorted(set(paths))}" for task, paths in sorted(duplicates.items()))
        raise RuntimeError(f"duplicate SkillsBench result.json files for a task: {details}")
    return by_task


def validate_oracle(job_dir: Path, tasks: list[str]) -> tuple[bool, dict[str, Any]]:
    rows = load_job_rewards(job_dir)
    missing = sorted(set(tasks) - set(rows))
    failed = sorted(task for task in tasks if task in rows and rows[task]["reward"] != 1.0)
    unhealthy = sorted(task for task in tasks if task in rows and rows[task]["excluded_reason"] is not None)
    return not missing and not failed and not unhealthy, {
        "expected": len(tasks),
        "observed": len(rows),
        "missing": missing,
        "failed": failed,
        "unhealthy": unhealthy,
    }


def collect_pairs(output: Path, tasks: list[str], runs: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    pairs: list[dict[str, Any]] = []
    gaps: list[dict[str, Any]] = []
    for repetition in range(1, runs + 1):
        rep = output / "runs" / f"r{repetition:03d}"
        base = load_job_rewards(rep / "no-skill") if (rep / "no-skill").exists() else {}
        practical = load_job_rewards(rep / "practical") if (rep / "practical").exists() else {}
        for task in tasks:
            left = base.get(task)
            right = practical.get(task)
            if not left or not right or left["excluded_reason"] or right["excluded_reason"]:
                gaps.append({
                    "task": task,
                    "repetition": repetition,
                    "baseline": left,
                    "practical": right,
                })
                continue
            pairs.append({
                "task": task,
                "repetition": repetition,
                "reward_base": left["reward"],
                "reward_practical": right["reward"],
                "passed_base": left["passed"],
                "passed_practical": right["passed"],
            })
    return pairs, gaps


def percentile(values: list[float], p: float) -> float | None:
    if not values:
        return None
    values = sorted(values)
    if len(values) == 1:
        return values[0]
    position = (len(values) - 1) * p
    lower = int(position)
    upper = min(lower + 1, len(values) - 1)
    fraction = position - lower
    return values[lower] * (1 - fraction) + values[upper] * fraction


def cluster_bootstrap(pairs: list[dict[str, Any]], samples: int = 5000, seed: int = 0) -> dict[str, list[float | None]]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for pair in pairs:
        groups[pair["task"]].append(pair)
    tasks = sorted(groups)
    if not tasks or samples <= 0:
        return {"pass_rate_delta": [None, None], "mean_reward_delta": [None, None]}
    rng = random.Random(seed)
    pass_deltas: list[float] = []
    reward_deltas: list[float] = []
    for _ in range(samples):
        sample_pairs: list[dict[str, Any]] = []
        for task in (rng.choice(tasks) for _ in tasks):
            sample_pairs.extend(groups[task])
        pass_deltas.append(
            statistics.mean(float(row["passed_practical"]) - float(row["passed_base"]) for row in sample_pairs)
        )
        reward_deltas.append(
            statistics.mean(float(row["reward_practical"]) - float(row["reward_base"]) for row in sample_pairs)
        )
    return {
        "pass_rate_delta": [percentile(pass_deltas, 0.025), percentile(pass_deltas, 0.975)],
        "mean_reward_delta": [percentile(reward_deltas, 0.025), percentile(reward_deltas, 0.975)],
    }


def summarize_pairs(pairs: list[dict[str, Any]], tasks: list[str], runs: int, gaps: list[dict[str, Any]], oracle_ok: bool) -> dict[str, Any]:
    if pairs:
        pass_base = statistics.mean(float(row["passed_base"]) for row in pairs)
        pass_practical = statistics.mean(float(row["passed_practical"]) for row in pairs)
        reward_base = statistics.mean(float(row["reward_base"]) for row in pairs)
        reward_practical = statistics.mean(float(row["reward_practical"]) for row in pairs)
    else:
        pass_base = pass_practical = reward_base = reward_practical = 0.0
    delta = pass_practical - pass_base
    normalized_gain = (delta / (1.0 - pass_base)) if delta > 0 and pass_base < 1.0 else delta
    by_task: list[dict[str, Any]] = []
    for task in tasks:
        rows = [row for row in pairs if row["task"] == task]
        if not rows:
            by_task.append({"task": task, "n": 0})
            continue
        by_task.append({
            "task": task,
            "n": len(rows),
            "pass_rate_base": statistics.mean(float(row["passed_base"]) for row in rows),
            "pass_rate_practical": statistics.mean(float(row["passed_practical"]) for row in rows),
            "mean_reward_base": statistics.mean(float(row["reward_base"]) for row in rows),
            "mean_reward_practical": statistics.mean(float(row["reward_practical"]) for row in rows),
        })
    expected_pairs = len(tasks) * runs
    stable = runs >= 3 and oracle_ok and len(pairs) == expected_pairs and not gaps and all(row["n"] == runs for row in by_task)
    return {
        "stable": stable,
        "expected_pairs": expected_pairs,
        "paired_rollouts": len(pairs),
        "gap_count": len(gaps),
        "pass_rate_base": pass_base,
        "pass_rate_practical": pass_practical,
        "pass_rate_delta": delta,
        "normalized_gain": normalized_gain,
        "mean_reward_base": reward_base,
        "mean_reward_practical": reward_practical,
        "mean_reward_delta": reward_practical - reward_base,
        "wins": sum((not row["passed_base"]) and row["passed_practical"] for row in pairs),
        "losses": sum(row["passed_base"] and (not row["passed_practical"]) for row in pairs),
        "ties": sum(row["passed_base"] == row["passed_practical"] for row in pairs),
        "ci95": cluster_bootstrap(pairs),
        "by_task": by_task,
    }


def _fmt_pct(value: float | None) -> str:
    return "—" if value is None else f"{100 * value:.1f}%"


def _fmt_signed_pp(value: float | None) -> str:
    return "—" if value is None else f"{100 * value:+.1f} pp"


def render_report(manifest: dict[str, Any], summary: dict[str, Any], gaps: list[dict[str, Any]]) -> str:
    ci = summary["ci95"]
    pass_ci = ci["pass_rate_delta"]
    reward_ci = ci["mean_reward_delta"]
    lines = [
        "# Practical Coding × SkillsBench external lift",
        "",
        f"- Dataset: `{manifest['dataset']}`",
        f"- Profile: `{manifest['profile']}` ({len(manifest['tasks'])} tasks)",
        f"- Agent/model: `{manifest['agent']}` / `{manifest['model']}` ({manifest['reasoning']})",
        f"- Runs per task/arm: `{manifest['runs']}`",
        f"- Evidence: **{'STABLE' if summary['stable'] else 'PROVISIONAL'}**",
        "- Treatment: baseline is `no-skill`; trained arm mounts only `practical-coding` as the custom Skill directory.",
        "- This is a Practical-owned ablation on the immutable SkillsBench dataset, not an official SkillsBench leaderboard submission using each task's curated Skill.",
        "",
        "## Overall",
        "",
        "| Metric | No Skill | + Practical | Delta | 95% cluster-bootstrap CI |",
        "|---|---:|---:|---:|---|",
        f"| Pass rate | {_fmt_pct(summary['pass_rate_base'])} | {_fmt_pct(summary['pass_rate_practical'])} | {_fmt_signed_pp(summary['pass_rate_delta'])} | {_fmt_signed_pp(pass_ci[0])} … {_fmt_signed_pp(pass_ci[1])} |",
        f"| Mean reward | {summary['mean_reward_base']:.3f} | {summary['mean_reward_practical']:.3f} | {summary['mean_reward_delta']:+.3f} | {(f'{reward_ci[0]:+.3f}' if reward_ci[0] is not None else '—')} … {(f'{reward_ci[1]:+.3f}' if reward_ci[1] is not None else '—')} |",
        "",
        f"Paired rollouts: **{summary['paired_rollouts']}/{summary['expected_pairs']}**. Pass flips: **{summary['wins']} wins / {summary['losses']} losses / {summary['ties']} ties**. Normalized gain: **{100 * summary['normalized_gain']:+.1f}%**.",
        "",
        "## Per task",
        "",
        "| Task | n | No Skill pass | Practical pass | No Skill reward | Practical reward |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in summary["by_task"]:
        if row["n"] == 0:
            lines.append(f"| {row['task']} | 0 | — | — | — | — |")
        else:
            lines.append(
                f"| {row['task']} | {row['n']} | {_fmt_pct(row['pass_rate_base'])} | {_fmt_pct(row['pass_rate_practical'])} | {row['mean_reward_base']:.3f} | {row['mean_reward_practical']:.3f} |"
            )
    if gaps:
        lines += ["", "## Missing / unhealthy pairs", ""]
        for gap in gaps:
            lines.append(f"- `{gap['task']}` r{gap['repetition']:03d}")
    lines += [
        "",
        "## Interpretation",
        "",
        "A positive delta means the same Codex/Luna setup solved more of the selected SkillsBench tasks when Practical Coding was mounted. The confidence interval resamples task IDs as clusters and keeps repeated trials for a task together. Public benchmark exposure still means this is external evidence, not a private holdout.",
        "",
    ]
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", choices=("smoke", "standard", "full"), default="standard")
    parser.add_argument("--task", action="append", default=[])
    parser.add_argument("--runs", type=int, default=0)
    parser.add_argument("--workers", type=int, default=3)
    parser.add_argument("--sandbox", choices=("docker", "daytona", "modal", "apple-container", "agentcore"), default="docker")
    parser.add_argument("--model", default=MODEL)
    parser.add_argument("--reasoning", default=REASONING)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--cache-root", type=Path)
    parser.add_argument("--skip-oracle", action="store_true")
    parser.add_argument("--require-stable-ranking", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def self_test() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        jobs = root / "jobs"
        for task, base, trained in (("a", 0.0, 1.0), ("b", 1.0, 1.0)):
            for arm, reward in (("base", base), ("trained", trained)):
                path = jobs / arm / task
                path.mkdir(parents=True, exist_ok=True)
                (path / "result.json").write_text(json.dumps({"task_name": task, "rewards": {"reward": reward}}), encoding="utf-8")
        assert load_job_rewards(jobs / "base")["a"]["reward"] == 0.0
        pairs = [
            {"task": "a", "repetition": 1, "reward_base": 0.0, "reward_practical": 1.0, "passed_base": False, "passed_practical": True},
            {"task": "b", "repetition": 1, "reward_base": 1.0, "reward_practical": 1.0, "passed_base": True, "passed_practical": True},
        ]
        summary = summarize_pairs(pairs, ["a", "b"], 1, [], True)
        assert summary["pass_rate_delta"] == 0.5
        assert not summary["stable"]
        stable_pairs = []
        for repetition in (1, 2, 3):
            for task in ("a", "b"):
                stable_pairs.append({"task": task, "repetition": repetition, "reward_base": 1.0, "reward_practical": 1.0, "passed_base": True, "passed_practical": True})
        assert summarize_pairs(stable_pairs, ["a", "b"], 3, [], True)["stable"]
    print("SkillsBench adapter self-test: PASS")


def main() -> int:
    args = parse_args()
    if args.self_test:
        self_test()
        return 0
    runs = args.runs or (1 if args.profile == "smoke" else 3)
    if runs < 1 or args.workers < 1:
        raise SystemExit("runs and workers must be positive")
    if args.require_stable_ranking and runs < 3:
        raise SystemExit("stable external ranking requires at least 3 runs")
    versions = check_prerequisites(args.sandbox)
    cache_root = (args.cache_root or Path(os.environ.get("LOCALAPPDATA") or tempfile.gettempdir()) / "practical-coding-benchmarks" / "external").resolve()
    checkout, source_commit = ensure_skillsbench_checkout(cache_root)
    tasks = discover_tasks(checkout, args.profile, args.task)
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    output = (args.output or ROOT / "benchmark-results" / "external" / f"skillsbench-{stamp}").resolve()
    output.mkdir(parents=True, exist_ok=False)
    staged_skills = stage_practical_skill(output)
    started = dt.datetime.now(dt.timezone.utc)
    manifest: dict[str, Any] = {
        "schema_version": 1,
        "started_at": started.isoformat(),
        "dataset": DATASET,
        "skillsbench_metadata_ref": SKILLSBENCH_REF,
        "skillsbench_metadata_commit": source_commit,
        "benchflow_version": BENCHFLOW_VERSION,
        "agent": AGENT,
        "model": args.model,
        "reasoning": args.reasoning,
        "sandbox": args.sandbox,
        "profile": args.profile,
        "runs": runs,
        "workers": args.workers,
        "tasks": tasks,
        "skill_bundle_sha256": skill_bundle_sha256(ROOT),
        "adapter_sha256": sha256_file(Path(__file__)),
        "environment": versions,
        "commands": [],
    }
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    oracle_ok = True
    oracle_summary: dict[str, Any] = {"skipped": True}
    if not args.skip_oracle:
        oracle_dir = output / "oracle"
        command = oracle_command(jobs_dir=oracle_dir, tasks=tasks, sandbox=args.sandbox, workers=args.workers)
        manifest["commands"].append({"kind": "oracle", "command": command})
        result = run_command(command, ROOT)
        (output / "oracle.log").write_text(result.stdout, encoding="utf-8")
        if result.returncode:
            raise RuntimeError(f"SkillsBench oracle command failed: {result.stdout[-4000:]}")
        oracle_ok, oracle_summary = validate_oracle(oracle_dir, tasks)
        if not oracle_ok:
            raise RuntimeError(f"SkillsBench oracle did not pass the selected task set: {oracle_summary}")

    for repetition in range(1, runs + 1):
        rep = output / "runs" / f"r{repetition:03d}"
        order = ("no-skill", "practical") if repetition % 2 else ("practical", "no-skill")
        for arm in order:
            jobs_dir = rep / arm
            mode = "no-skill" if arm == "no-skill" else "with-skill"
            command = bench_command(
                jobs_dir=jobs_dir,
                tasks=tasks,
                sandbox=args.sandbox,
                workers=args.workers,
                model=args.model,
                reasoning=args.reasoning,
                skill_mode=mode,
                skills_root=staged_skills if arm == "practical" else None,
            )
            manifest["commands"].append({"kind": arm, "repetition": repetition, "command": command})
            result = run_command(command, ROOT)
            rep.mkdir(parents=True, exist_ok=True)
            (rep / f"{arm}.log").write_text(result.stdout, encoding="utf-8")
            if result.returncode:
                manifest.setdefault("infrastructure_failures", []).append({"arm": arm, "repetition": repetition, "returncode": result.returncode})
                (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
                raise RuntimeError(f"SkillsBench {arm} r{repetition} failed: {result.stdout[-4000:]}")

    pairs, gaps = collect_pairs(output, tasks, runs)
    summary = summarize_pairs(pairs, tasks, runs, gaps, oracle_ok)
    manifest.update({
        "completed_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "oracle": oracle_summary,
        "paired_rollouts": len(pairs),
        "stable": summary["stable"],
    })
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    (output / "pairs.json").write_text(json.dumps(pairs, indent=2) + "\n", encoding="utf-8")
    (output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    (output / "report.md").write_text(render_report(manifest, summary, gaps), encoding="utf-8")
    print(f"wrote {output}")
    print(f"SkillsBench pass lift: {_fmt_signed_pp(summary['pass_rate_delta'])} ({'STABLE' if summary['stable'] else 'PROVISIONAL'})")
    if args.require_stable_ranking and not summary["stable"]:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

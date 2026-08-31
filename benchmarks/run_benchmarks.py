#!/usr/bin/env python3
"""Reproducible Practical Coding benchmark chain for Codex Luna."""

from __future__ import annotations

import argparse
import concurrent.futures
import datetime as dt
import gc
import hashlib
import importlib.util
import json
import math
import os
import re
import shutil
import statistics
import subprocess
import sys
import tempfile
import threading
import time
import platform
from collections import defaultdict
from pathlib import Path
from typing import Any, Callable


VERSION = "2.0"
MODEL = "gpt-5.6-luna"
REASONING = "medium"
ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent

COMPARATORS = {"delivery": "ponytail", "decision": "grilling", "debug": "superpowers"}
COMBO_COMPONENTS = ("practical-current", "ponytail", "superpowers", "grill-me")
PASS_NONINFERIORITY_MARGIN = 0.03
COST_WEIGHTS = {
    "uncached_input_tokens_median": 0.35,
    "output_tokens_median": 0.15,
    "duration_seconds_median": 0.35,
    "tool_calls_median": 0.15,
}
STRICT_SAFETY_CASES: set[str] = set()

SOURCES = {
    "ponytail": ("https://github.com/DietrichGebert/ponytail.git", "2ed6c52c9d7e5e56942508591085fd45dea277d3"),
    "mattpocock-skills": ("https://github.com/mattpocock/skills.git", "5b15a47f2d7150f545fbcacbfe381787fc0230dc"),
    "superpowers": ("https://github.com/obra/superpowers.git", "b36e0829c6d0140e93cfef2ca599b1b07d4a7797"),
    "full-stack-fastapi-template": ("https://github.com/fastapi/full-stack-fastapi-template.git", "cd83fc10ca20393e9ee50e3005e170c6929e047e"),
}

REASONING_ROUTES = ("NONE", "DECISION", "DEBUGGING", "IMPLEMENTATION")
RETRIEVAL_MODES = ("NONE", "TARGETED", "BOUNDED", "STRUCTURAL")

ROUTER_CASES = {
    "direct-known-local": ("NONE", "TARGETED", "Change the known label in src/Header.tsx and run its known component check."),
    "direct-artifact": ("NONE", "BOUNDED", "Add a DatePicker component beside existing UI primitives; their exact location is not given and no integration was requested."),
    "direct-default": ("NONE", "BOUNDED", "Add a local timestamp formatter; the repository already uses the platform default, but no target path or symbol is given."),
    "direct-multifile-known": ("NONE", "TARGETED", "Rename the known internal field in these two known private files and run the known focused test."),
    "decision-auth": ("DECISION", "NONE", "Choose API keys or OAuth for a public B2B API; customer compatibility needs are unresolved."),
    "decision-schema": ("DECISION", "NONE", "Choose rename versus alias for a public JSON field; client compatibility policy is unknown."),
    "decision-dependency": ("DECISION", "NONE", "Choose whether to adopt Redis or keep the installed database cache; operational ownership is unresolved."),
    "debug-symptom": ("DEBUGGING", "BOUNDED", "Invoice totals fail on comma-formatted amounts; the cause has not been traced."),
    "debug-named-function": ("DEBUGGING", "TARGETED", "Fix transfer(), which sometimes allows a negative balance; only the reported function is known."),
    "debug-over-decision": ("DEBUGGING", "BOUNDED", "A new queue client intermittently loses messages. Choose retry semantics and fix it, but no cause is diagnosed."),
    "implementation-contract": ("IMPLEMENTATION", "STRUCTURAL", "A versioned event contract must change across producers and consumers, but the coordinated surface is unknown."),
    "implementation-not-files": ("NONE", "TARGETED", "Update three already-known callers to the already-decided function signature."),
    "exploration-broad": ("NONE", "STRUCTURAL", "In this monorepo, map every service calling the billing client and where responses are transformed."),
    "exploration-cbm-off": ("NONE", "STRUCTURAL", "Map the complete call chain in this large repository; no structural index is available, so reconstruct the structural relationship from bounded source search."),
    "verification-risk": ("IMPLEMENTATION", "BOUNDED", "The change is complete, but its existing checks have not been identified; choose the cheapest sufficient evidence for a risky zero-downtime migration."),
    "verification-known": ("NONE", "BOUNDED", "The local change is complete and an existing focused unit test is sufficient, but its path or symbol is not given; locate and run it."),
}

DECISION_CASES = {
    "api-auth": {
        "prompt": "Choose API keys or OAuth 2.0 for a new public B2B API. Customers integrate backend systems and launch is in six weeks; identity, scopes, and lifecycle needs are unresolved.",
        "reply": "Backend-only integrations; customer-level identity; no delegated users or scopes; rotation and revocation are required. Resolve the decision now.",
        "expected": ("api key", "key"),
    },
    "service-boundary": {
        "prompt": "Decide whether invoicing and payments belong in our monolith or a microservice. Four engineers, three months; ownership, transactions, scale, and deployment constraints are unresolved.",
        "reply": "The same team owns it; it needs atomic transactions with monolith data; no distinct scale or isolation target; coordinated deployment is acceptable. Resolve the decision now.",
        "expected": ("monolith", "module"),
    },
    "event-delivery": {
        "prompt": "Choose at-most-once or at-least-once delivery for invoice events. Duplicate handling, loss tolerance, and consumer idempotency are unresolved.",
        "reply": "Losing an invoice event is unacceptable; duplicates are acceptable; consumers can use invoice_id as an idempotency key. Resolve the decision now.",
        "expected": ("at-least-once", "at least once"),
    },
    "api-migration": {
        "prompt": "Choose a breaking field rename or a compatibility alias for a public API used by unknown external clients. Migration window and removal policy are unresolved.",
        "reply": "Clients cannot all upgrade together; keep the old field for one documented release window with telemetry before removal. Resolve the decision now.",
        "expected": ("alias", "compatib"),
    },
}

CUSTOM_DEBUG = {
    "trace-config-bool": {
        "prompt": "feature_enabled() in config.py is wrong when FEATURE contains surrounding whitespace, such as ' false '. FEATURE and AUDIT use the same whitespace-tolerant boolean format; fix their shared parsing behavior without breaking other settings.",
        "files": {"config.py": """def parse_bool(value):\n    return value.lower() in {\"1\", \"true\", \"yes\"}\n\ndef feature_enabled(env):\n    return parse_bool(env.get(\"FEATURE\", \"false\"))\n\ndef audit_enabled(env):\n    return parse_bool(env.get(\"AUDIT\", \"false\"))\n"""},
        "score": "config",
    },
    "trace-url-join": {
        "prompt": "asset_url() in urls.py sometimes returns a URL with a double slash when the configured base ends in '/'. Fix it; callers share URL construction.",
        "files": {"urls.py": """def join_url(base, path):\n    return base + \"/\" + path\n\ndef asset_url(base, name):\n    return join_url(base, \"assets/\" + name)\n\ndef callback_url(base):\n    return join_url(base, \"oauth/callback\")\n"""},
        "score": "url",
    },
}

BEHAVIOR_CASES = {
    "native-direct": {
        "prompt": "Change the greeting in app.py from 'hello' to 'hello world' and run the file once.",
        "files": {"app.py": "print('hello')\n"},
        "reasoning_module": None,
        "retrieval": "TARGETED",
    },
    "native-direct-settled-choice": {
        "prompt": "Repository policy already requires Python's sqlite3 for durable command history. Implement save_history() in cli.py using that settled choice.",
        "files": {"cli.py": "import sqlite3\n\ndef save_history(connection, command):\n    pass\n"},
        "reasoning_module": None,
        "retrieval": "TARGETED",
    },
    "native-direct-diagnosed": {
        "prompt": "The failing test and trace already establish the cause: parse_bool() does not strip surrounding whitespace. Fix that shared function and run a focused check.",
        "files": {"config.py": "def parse_bool(value):\n    return value.lower() in {'1', 'true', 'yes'}\n\ndef feature_enabled(env):\n    return parse_bool(env.get('FEATURE', 'false'))\n"},
        "reasoning_module": None,
        "retrieval": "TARGETED",
    },
    "native-decision": {
        "prompt": "Choose SQLite or a JSON file for durable command history in this small public CLI. Compatibility and operational constraints are not specified. Make the decision only; do not implement it yet.",
        "files": {"cli.py": "def main():\n    pass\n"},
        "reasoning_module": "decision.md",
        "retrieval": "NONE",
    },
    "native-debugging": {
        "prompt": "feature_enabled() is wrong for FEATURE=' false '. Fix the reported bug without breaking other settings.",
        "files": {"config.py": "def parse_bool(value):\n    return value.lower() in {'1', 'true', 'yes'}\n\ndef feature_enabled(env):\n    return parse_bool(env.get('FEATURE', 'false'))\n\ndef audit_enabled(env):\n    return parse_bool(env.get('AUDIT', 'false'))\n"},
        "reasoning_module": "debugging.md",
        "retrieval": "TARGETED",
    },
    "native-debug-over-decision": {
        "prompt": "The new queue client intermittently loses messages. Choose retry semantics and fix it, but no cause has been diagnosed. Start with the unresolved event that must be handled first.",
        "files": {"queue.py": "def publish(client, message):\n    client.send(message)\n"},
        "reasoning_module": "debugging.md",
        "retrieval": "TARGETED",
    },
    "native-implementation": {
        "prompt": "Change the persisted account status field from integer codes 1/2 to public strings 'active'/'disabled' with a zero-downtime migration. Keep integer readers compatible for one release, then remove them; rollback restores integer writes. The producers and consumers are not mapped yet.",
        "files": {"models.py": "ACCOUNT_ACTIVE = 1\nACCOUNT_DISABLED = 2\n"},
        "reasoning_module": "implementation.md",
        "retrieval": "STRUCTURAL",
    },
    "native-implementation-security": {
        "prompt": "Add API-token rotation, but the permission boundary, durable secret storage, revocation invariant, and affected callers are not mapped. Determine the safe implementation surface before editing.",
        "files": {"tokens.py": "def issue_token(user_id):\n    raise NotImplementedError\n"},
        "reasoning_module": "implementation.md",
        "retrieval": "STRUCTURAL",
    },
    "native-exploration": {
        "prompt": "Map every service in this monorepo that calls the billing client and where each response is transformed. Report the complete call chain; do not change code.",
        "files": {"services/api.py": "from shared.billing import charge\n", "services/jobs.py": "from shared.billing import charge\n", "shared/billing.py": "def charge():\n    pass\n"},
        "reasoning_module": None,
        "retrieval": "STRUCTURAL",
        "backend": "source",
    },
    "native-structural-capability-fallback": {
        "prompt": "Map the complete call chain from API handlers through billing transformations in this repository. Use an already-available structural index only if the host actually exposes one; otherwise use bounded source search. Report only; do not edit code.",
        "files": {
            "api.py": "from billing import charge\n",
            "billing.py": "def charge():\n    pass\n",
        },
        "reasoning_module": None,
        "retrieval": "STRUCTURAL",
    },
}

PROFILE_CASES = {
    "smoke": {
        "delivery": ["safe-path", "reuse-slug", "tmpl-fe-datepicker"],
        "router": ["direct-artifact", "decision-auth", "debug-named-function", "verification-risk"],
        "decision": ["service-boundary"],
        "debug": ["trace-transfer"],
        "behavior": ["native-direct", "native-debugging", "native-implementation"],
        "runs": 1,
    },
    "standard": {
        "delivery": ["safe-path", "critic-email", "cache", "reuse-slug", "reuse-money", "tmpl-fe-datepicker", "tmpl-fe-dropzone", "tmpl-fe-command", "tmpl-be-count"],
        "router": list(ROUTER_CASES),
        "decision": list(DECISION_CASES),
        "debug": ["trace-transfer", "trace-amount", "trace-config-bool", "trace-url-join"],
        "behavior": list(BEHAVIOR_CASES),
        "runs": 3,
    },
    "full": {
        "delivery": ["safe-path", "critic-email", "rate-limit", "sql-user", "auth-token", "csv-sum", "cache", "reuse-slug", "reuse-money", "tmpl-fe-datepicker", "tmpl-fe-colorpicker", "tmpl-fe-dropzone", "tmpl-fe-rating", "tmpl-fe-command", "tmpl-fe-wizard", "tmpl-be-count", "tmpl-be-search", "tmpl-be-csv"],
        "router": list(ROUTER_CASES),
        "decision": list(DECISION_CASES),
        "debug": ["trace-transfer", "trace-amount", "trace-config-bool", "trace-url-join"],
        "behavior": list(BEHAVIOR_CASES),
        "runs": 3,
    },
}


def run_command(args: list[str], cwd: Path, timeout: float | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=str(cwd), text=True, encoding="utf-8", errors="replace", stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout, check=False)


def snapshot_workspace(workspace: Path) -> None:
    """Create the baseline commit used by upstream scoring, failing loudly on setup errors."""
    git = shutil.which("git") or "git"
    commands = [
        [git, "init", "-q"],
        [git, "config", "core.longpaths", "true"],
        [git, "add", "-A"],
        [git, "-c", "user.email=bench@local", "-c", "user.name=bench", "commit", "-q", "-m", "base", "--no-verify"],
    ]
    for command in commands:
        result = run_command(command, workspace)
        if result.returncode != 0:
            detail = (result.stderr or result.stdout).strip()
            raise RuntimeError(f"workspace snapshot failed ({' '.join(command[1:])}): {detail}")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def bundle_sha256(root: Path) -> str:
    digest = hashlib.sha256()
    paths = [root / "SKILL.md", *sorted((root / "references").glob("*.md"))]
    for path in paths:
        if path.is_file():
            digest.update(str(path.relative_to(root)).replace("\\", "/").encode())
            digest.update(b"\0")
            digest.update(path.read_bytes())
            digest.update(b"\0")
    return digest.hexdigest()


def materialize_git_skill(revision: str, destination: Path) -> Path:
    listed = run_command(["git", "ls-tree", "-r", "--name-only", revision, "--", "SKILL.md", "references"], ROOT)
    if listed.returncode:
        raise RuntimeError(f"cannot resolve baseline ref {revision}: {listed.stderr}")
    names = [line.strip() for line in listed.stdout.splitlines() if line.strip()]
    if "SKILL.md" not in names:
        raise RuntimeError(f"baseline ref {revision} has no SKILL.md")
    for name in names:
        if name != "SKILL.md" and not name.startswith("references/"):
            continue
        result = subprocess.run(["git", "show", f"{revision}:{name}"], cwd=str(ROOT), stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        if result.returncode:
            raise RuntimeError(result.stderr.decode("utf-8", errors="replace"))
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(result.stdout)
    return destination


def resolve_codex(value: str) -> str:
    resolved = shutil.which(value) or value
    path = Path(resolved)
    if os.name == "nt" and path.suffix.lower() in {".cmd", ".bat", ".ps1"}:
        candidates = sorted(path.parent.glob("node_modules/@openai/codex/node_modules/@openai/codex-win32-*/vendor/*/bin/codex.exe"))
        if candidates:
            return str(candidates[0])
    return resolved


def default_sources_root() -> Path:
    base = os.environ.get("LOCALAPPDATA") or tempfile.gettempdir()
    return Path(base) / "practical-coding-benchmarks" / "sources"


def ensure_checkout(root: Path, name: str) -> Path:
    url, commit = SOURCES[name]
    path = root / name
    head = run_command(["git", "rev-parse", "HEAD"], path) if path.exists() else None
    needs_materialize = head is None or head.returncode or head.stdout.strip() != commit
    if needs_materialize:
        if path.exists():
            shutil.rmtree(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        result = run_command(["git", "clone", "--filter=blob:none", "--no-checkout", url, str(path)], root.parent)
        if result.returncode:
            raise RuntimeError(result.stderr)
        fetch = run_command(["git", "fetch", "--depth", "1", "origin", commit], path)
        checkout = run_command(["git", "checkout", "--detach", commit], path)
        if fetch.returncode or checkout.returncode:
            raise RuntimeError(fetch.stderr + checkout.stderr)
    head = run_command(["git", "rev-parse", "HEAD"], path)
    if head.returncode or head.stdout.strip() != commit:
        raise RuntimeError(f"{name} must be pinned at {commit}; found {head.stdout.strip()}")
    return path


def load_ponytail(sources: dict[str, Path]) -> Any:
    template = sources["full-stack-fastapi-template"]
    os.environ["PONYTAIL_TMPL"] = str(template)
    agentic = sources["ponytail"] / "benchmarks" / "agentic"
    sys.path.insert(0, str(agentic))
    spec = importlib.util.spec_from_file_location("practical_ponytail_agentic", agentic / "run.py")
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load Ponytail agentic runner")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def prepare_eval_home(output: Path) -> Path:
    key = hashlib.sha256(str(output.resolve()).encode()).hexdigest()[:16]
    home = Path.home() / ".codex-evals" / "practical-coding-benchmarks" / key
    home.mkdir(parents=True, exist_ok=True)
    source = Path.home() / ".codex" / "auth.json"
    target = home / "auth.json"
    if not source.is_file():
        raise FileNotFoundError("Codex auth.json is unavailable")
    if not target.exists():
        os.link(source, target)
    return home


def install_native_skill(eval_home: Path, source: Path) -> Path:
    destination = eval_home / "skills" / "practical-coding"
    if destination.exists():
        shutil.rmtree(destination)
    destination.mkdir(parents=True)
    shutil.copy2(source / "SKILL.md", destination / "SKILL.md")
    references = source / "references"
    if references.is_dir():
        shutil.copytree(references, destination / "references")
    return destination


def disabled_skill_config() -> str:
    candidates = [Path.home() / ".agents/skills/practical-coding/SKILL.md", Path.home() / ".codex/skills/practical-coding/SKILL.md"]
    entries = ",".join(f'{{path="{path.as_posix()}",enabled=false}}' for path in candidates if path.is_file())
    return f"skills.config=[{entries}]"


def codex_command(codex: str, cwd: Path, *, resume: str | None = None) -> list[str]:
    command = [codex, "exec"]
    if resume:
        command += ["resume"]
    command += ["--json", "--ignore-user-config", "--disable", "plugins", "--disable", "skill_search", "--disable", "memories", "--disable", "apps", "--disable", "multi_agent", "--model", MODEL, "--config", f"model_reasoning_effort={REASONING}", "--config", disabled_skill_config(), "--dangerously-bypass-approvals-and-sandbox"]
    if resume:
        command += [resume, "-"]
    else:
        command += ["-C", str(cwd), "-"]
    return command


def run_codex(command: list[str], prompt: str, cwd: Path, env: dict[str, str], stdout: Path, stderr: Path, timeout: float) -> tuple[int, bool, bool, float]:
    deadline = time.monotonic() + timeout
    completed_at: float | None = None
    started = time.monotonic()
    with stdout.open("w", encoding="utf-8") as out, stderr.open("w", encoding="utf-8") as err:
        process = subprocess.Popen(command, cwd=str(cwd), stdin=subprocess.PIPE, text=True, encoding="utf-8", errors="replace", stdout=out, stderr=err, env=env)
        assert process.stdin is not None
        try:
            process.stdin.write(prompt)
            process.stdin.close()
        except (BrokenPipeError, OSError):
            # Preserve the CLI's exit code and stderr instead of losing the diagnostic
            # when Windows reports a closed stdin pipe as EINVAL.
            try:
                process.stdin.close()
            except OSError:
                pass
        timed_out = forced = False
        while process.poll() is None:
            now = time.monotonic()
            if completed_at is None and stdout.exists() and '"type":"turn.completed"' in stdout.read_text(encoding="utf-8", errors="replace"):
                completed_at = now
            if completed_at is not None and now - completed_at >= 10:
                forced = True
                process.terminate()
                break
            if now >= deadline:
                timed_out = True
                process.terminate()
                break
            time.sleep(0.25)
        try:
            code = process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            code = process.wait(timeout=10)
    return code, timed_out, forced, time.monotonic() - started


def parse_transcript(path: Path) -> dict[str, Any]:
    answer = ""
    thread_id = None
    usage = {"input_tokens": 0, "cached_input_tokens": 0, "output_tokens": 0, "reasoning_output_tokens": 0}
    tool_calls = 0
    tool_commands: list[str] = []
    tool_outputs: list[str] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if event.get("type") == "thread.started":
            thread_id = event.get("thread_id")
        if event.get("type") == "item.completed":
            item = event.get("item") or {}
            if item.get("type") == "agent_message":
                answer = item.get("text") or answer
            elif item.get("type") in {"command_execution", "mcp_tool_call", "file_change"}:
                tool_calls += 1
                command = item.get("command")
                if isinstance(command, str):
                    tool_commands.append(command)
                output = item.get("aggregated_output")
                if isinstance(output, str):
                    tool_outputs.append(output)
        if event.get("type") == "turn.completed":
            for key in usage:
                usage[key] += int((event.get("usage") or {}).get(key) or 0)
    usage["uncached_input_tokens"] = usage["input_tokens"] - usage["cached_input_tokens"]
    usage["total_tokens"] = usage["input_tokens"] + usage["output_tokens"]
    return {"answer": answer, "thread_id": thread_id, "usage": usage, "tool_calls": tool_calls, "tool_commands": tool_commands, "tool_outputs": tool_outputs}


def combo_arms() -> list[str]:
    """All non-empty co-install subsets of Practical, Ponytail, Superpowers, and grill-me."""
    from itertools import combinations

    arms: list[str] = []
    for width in range(1, len(COMBO_COMPONENTS) + 1):
        for combo in combinations(COMBO_COMPONENTS, width):
            arms.append("+".join(combo))
    return arms


def skill_text(arm: str, sources: dict[str, Path], previous: Path | None, suite: str | None = None) -> str:
    if "+" in arm:
        parts = [part for part in arm.split("+") if part]
        if not parts or any("+" in part for part in parts):
            raise ValueError(arm)
        return "\n\n".join(skill_text(part, sources, previous, suite) for part in parts)
    if arm in {"baseline", "practical-native", "practical-native-previous"}:
        return ""
    if arm in {"practical-current", "practical-previous"}:
        root = ROOT if arm == "practical-current" else previous
        if root is None:
            raise RuntimeError("previous skill unavailable")
        skill = (root / "SKILL.md").read_text(encoding="utf-8")
        loaded = f'Practical Coding is loaded below. Read only event-required references from {root / "references"}.\n<loaded-skill name="practical-coding">\n{skill}\n</loaded-skill>'
        if suite == "decision":
            decision = root / "references" / "decision.md"
            if decision.is_file():
                loaded += f'\n<loaded-skill-reference name="decision">\n{decision.read_text(encoding="utf-8")}\n</loaded-skill-reference>'
        return loaded
    if arm == "ponytail":
        value = (sources["ponytail"] / "skills/ponytail/SKILL.md").read_text(encoding="utf-8")
        return f'<loaded-skill name="ponytail">\n{value}\n</loaded-skill>'
    if arm == "grilling":
        value = (sources["mattpocock-skills"] / "skills/productivity/grilling/SKILL.md").read_text(encoding="utf-8")
        return f'<loaded-skill name="grilling">\n{value}\n</loaded-skill>'
    if arm == "grill-me":
        root = sources["mattpocock-skills"] / "skills/productivity"
        grill_me = (root / "grill-me/SKILL.md").read_text(encoding="utf-8")
        grilling = (root / "grilling/SKILL.md").read_text(encoding="utf-8")
        return (
            f'<loaded-skill name="grill-me">\n{grill_me}\n</loaded-skill>\n'
            f'<loaded-skill name="grilling">\n{grilling}\n</loaded-skill>'
        )
    if arm == "superpowers":
        root = sources["superpowers"] / "skills"
        value = (root / "using-superpowers/SKILL.md").read_text(encoding="utf-8")
        return f'Superpowers is loaded below. Read invoked skills under {root}.\n<loaded-skill name="using-superpowers">\n{value}\n</loaded-skill>'
    raise ValueError(arm)


def parse_router_answer(answer: str) -> tuple[str, str]:
    match = re.fullmatch(
        r"\s*`?\s*REASONING\s*=\s*(NONE|DECISION|DEBUGGING|IMPLEMENTATION)\s*;\s*"
        r"RETRIEVAL\s*=\s*(NONE|TARGETED|BOUNDED|STRUCTURAL)\s*`?\s*[.]?\s*",
        answer.upper(),
    )
    return match.groups() if match else ("", "")


def behavior_score(
    commands: list[str],
    expected_reasoning_module: str | None,
    outputs: list[str] | None = None,
    expected_retrieval: str = "TARGETED",
    expected_backend: str | None = None,
) -> dict[str, Any]:
    normalized = [command.replace("\\", "/").lower() for command in commands]
    combined_output = "\n".join(outputs or [])
    triggered = bool(re.search(r"(?m)^# Practical Coding\s*$", combined_output)) or any("practical-coding" in command and "skill.md" in command for command in normalized)
    module_headings = {
        "decision.md": "Decision",
        "debugging.md": "Debugging",
        "implementation.md": "Implementation",
        "navigation.md": "Navigation",
        "delegation.md": "Isolated Module Delegation",
    }
    batches: list[list[str]] = []
    if outputs:
        for output in outputs:
            matches = []
            for module, heading in module_headings.items():
                match = re.search(rf"(?m)^# {re.escape(heading)}\s*$", output)
                if match:
                    matches.append((match.start(), module))
            if matches:
                batches.append([module for _, module in sorted(matches)])
    else:
        for command in normalized:
            if "practical-coding" not in command or "references" not in command:
                continue
            batch = [module for module in module_headings if module in command]
            if batch:
                batches.append(batch)
    module_sequence = [module for batch in batches for module in batch]
    module_reads = sorted(set(module_sequence))
    reasoning_modules = {"decision.md", "debugging.md", "implementation.md"}
    reasoning_batches = [[module for module in batch if module in reasoning_modules] for batch in batches]
    reasoning_batches = [batch for batch in reasoning_batches if batch]
    reasoning_sequence = [module for batch in reasoning_batches for module in batch]
    reasoning_reads = sorted(set(reasoning_sequence))
    expected_reads = [] if expected_reasoning_module is None else [expected_reasoning_module]
    first_reasoning_batch = reasoning_batches[0] if reasoning_batches else []
    reasoning_ok = reasoning_reads == expected_reads and (
        not reasoning_batches if expected_reasoning_module is None else first_reasoning_batch == expected_reads
    )
    graph_used = any("codebase-memory-mcp" in command for command in normalized)
    source_search_used = any(
        re.search(r"(^|[\s;&|])(?:rg|grep|find|fd)(?:\.exe)?(?:[\s;&|]|$)", command)
        or "get-childitem" in command
        or "git grep" in command
        for command in normalized
    )
    navigation_used = "navigation.md" in module_reads
    if expected_retrieval == "STRUCTURAL":
        retrieval_ok = graph_used or source_search_used
    elif expected_retrieval == "BOUNDED":
        retrieval_ok = source_search_used and not navigation_used and not graph_used
    else:
        retrieval_ok = not navigation_used and not graph_used
    backend_ok = expected_backend is None or graph_used == (expected_backend == "graph")
    return {
        "triggered": triggered,
        "expected_reasoning_module": expected_reasoning_module,
        "reasoning_reads": reasoning_reads,
        "reasoning_sequence": reasoning_sequence,
        "first_reasoning_batch": first_reasoning_batch,
        "reasoning_ok": reasoning_ok,
        "expected_retrieval": expected_retrieval,
        "source_search_used": source_search_used,
        "navigation_used": navigation_used,
        "retrieval_ok": retrieval_ok,
        "module_reads": module_reads,
        "module_sequence": module_sequence,
        "expected_backend": expected_backend,
        "graph_backend_used": graph_used,
        "backend_ok": backend_ok,
        "passed": triggered and reasoning_ok and retrieval_ok and backend_ok,
    }


def prepare_upstream_workspace(task_id: str, workspace: Path, ponytail: Any) -> None:
    task = ponytail.TASKS[task_id]
    if task.get("fixture"):
        fixture = Path(task["fixture"])
        shutil.copytree(fixture, workspace, dirs_exist_ok=True, ignore=shutil.ignore_patterns("node_modules", ".git", "build", "dist", "dist-ssr", ".vite", "*.log", "__pycache__", "storage", ".venv", "venv", ".pytest_cache", "*.mp4", "*.mp3", "*.wav", "*.mov", "*service-account*.json", "nul", "con", "prn", "aux", "DatePicker*.tsx", "DatePicker*.jsx"))
        manifest = sorted(str(path.relative_to(workspace)).replace("\\", "/") for path in workspace.rglob("*") if path.is_file())
        (workspace / "_fixture_files.json").write_text(json.dumps(manifest), encoding="utf-8")
    for name, content in task.get("seed", {}).items():
        path = workspace / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    if task.get("fixture"):
        snapshot_workspace(workspace)


def custom_debug_score(case: str, workspace: Path) -> dict[str, Any]:
    if case == "trace-config-bool":
        spec = importlib.util.spec_from_file_location("debug_config", workspace / "config.py")
        try:
            assert spec and spec.loader
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            correct = module.feature_enabled({"FEATURE": " true "}) is True
            safe = module.audit_enabled({"AUDIT": " yes "}) is True
        except Exception as error:
            return {"correct": 0, "safe": 0, "reason": str(error)}
        return {"correct": int(correct), "safe": int(safe), "reason": "shared parse_bool" if safe else "patched only reported caller"}
    spec = importlib.util.spec_from_file_location("debug_urls", workspace / "urls.py")
    try:
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        correct = module.asset_url("https://x.test/", "a.png") == "https://x.test/assets/a.png"
        safe = module.callback_url("https://x.test/") == "https://x.test/oauth/callback"
    except Exception as error:
        return {"correct": 0, "safe": 0, "reason": str(error)}
    return {"correct": int(correct), "safe": int(safe), "reason": "shared join_url" if safe else "patched only asset_url"}


def decision_metrics(answer: str) -> dict[str, Any]:
    labels = re.findall(r"(?mi)^\s*(?:❓\s*)?\*{0,2}(?:Q|Question|问题)\s*\d+", answer)
    questions = len(labels) if labels else answer.count("?")
    recommendations = sum(
        1
        for line in answer.splitlines()
        if re.search(r"(?:➡️|Recommendation\s*:|Recommended\b|Recommend\b|建议\s*[:：])", line, re.I)
    )
    lower = answer.lower()
    return {
        "questions": questions,
        "recommendations": recommendations,
        "has_tradeoff": any(term in lower for term in ("trade-off", "tradeoff", "alternative", "overhead", "complexity", "coordination", "risk", "cost", "权衡", "代价", "成本", "复杂", "风险")),
        "attempted_implementation": any(term in lower for term in ("i implemented", "i have implemented", "已实现", "已经修改")),
    }


def post_build(task_id: str, workspace: Path, timeout: float) -> dict[str, Any] | None:
    if not task_id.startswith("tmpl-fe-"):
        return None
    frontend = workspace / "frontend"
    started = time.monotonic()
    bun = shutil.which("bun")
    if not bun:
        return {"passed": False, "duration_seconds": 0.0, "output_tail": "bun was not found", "infrastructure_error": "bun was not found"}
    launcher = [bun]
    if os.name == "nt" and Path(bun).suffix.lower() == ".ps1":
        launcher = [shutil.which("pwsh") or "pwsh", "-NoProfile", "-File", bun]
    elif os.name == "nt" and Path(bun).suffix.lower() in {".cmd", ".bat"}:
        launcher = [os.environ.get("COMSPEC", "cmd.exe"), "/d", "/c", bun]
    install = None if (frontend / "node_modules").is_dir() else run_command([*launcher, "install", "--frozen-lockfile"], frontend, timeout)
    build = run_command([*launcher, "run", "build"], frontend, timeout) if install is None or install.returncode == 0 else None
    output = ((install.stdout + install.stderr) if install else "") + ((build.stdout + build.stderr) if build else "")
    infrastructure_error = build_infrastructure_error(output)
    return {"passed": bool(build and build.returncode == 0), "duration_seconds": time.monotonic() - started, "output_tail": output[-4000:], "infrastructure_error": infrastructure_error}


def prepare_frontend_dependencies(task_id: str, workspace: Path, timeout: float) -> dict[str, Any] | None:
    """Make declared frontend dependencies available before the agent chooses its verification."""
    if not task_id.startswith("tmpl-fe-"):
        return None
    frontend = workspace / "frontend"
    bun = shutil.which("bun")
    if not bun:
        raise RuntimeError("bun was not found")
    launcher = [bun]
    if os.name == "nt" and Path(bun).suffix.lower() == ".ps1":
        launcher = [shutil.which("pwsh") or "pwsh", "-NoProfile", "-File", bun]
    elif os.name == "nt" and Path(bun).suffix.lower() in {".cmd", ".bat"}:
        launcher = [os.environ.get("COMSPEC", "cmd.exe"), "/d", "/c", bun]
    started = time.monotonic()
    install = run_command([*launcher, "install", "--frozen-lockfile"], frontend, timeout)
    output = install.stdout + install.stderr
    if install.returncode:
        raise RuntimeError(f"frontend dependency setup failed: {output[-2000:]}")
    return {"duration_seconds": time.monotonic() - started, "output_tail": output[-2000:]}


def build_infrastructure_error(output: str) -> str | None:
    lower = output.lower()
    if "out of memory" in lower or "memory allocation of" in lower or "allocation failed - process out of memory" in lower:
        return "frontend build exhausted memory"
    if "bun was not found" in lower:
        return "bun was not found"
    return None


def run_cell(spec: tuple[str, str, str, int], args: argparse.Namespace, sources: dict[str, Path], previous: Path | None, ponytail: Any, eval_homes: dict[str, Path], output: Path) -> dict[str, Any]:
    suite, case, arm, repetition = spec
    cell = output / "cells" / suite / case / arm / f"r{repetition:03d}"
    cell.mkdir(parents=True, exist_ok=False)
    workspace = cell / "workspace"
    workspace.mkdir()
    if suite in {"delivery", "debug"} and case in ponytail.TASKS:
        prepare_upstream_workspace(case, workspace, ponytail)
        request = ponytail.TASKS[case]["prompt"]
    elif suite == "debug":
        custom = CUSTOM_DEBUG[case]
        for name, content in custom["files"].items():
            (workspace / name).write_text(content, encoding="utf-8")
        snapshot_workspace(workspace)
        request = custom["prompt"]
    elif suite == "router":
        request = ROUTER_CASES[case][2]
    elif suite == "behavior":
        behavior = BEHAVIOR_CASES[case]
        for name, content in behavior["files"].items():
            path = workspace / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        snapshot_workspace(workspace)
        request = behavior["prompt"]
    else:
        request = DECISION_CASES[case]["prompt"]

    dependency_setup = None
    if suite == "delivery" and not args.no_builds:
        dependency_setup = prepare_frontend_dependencies(case, workspace, args.build_timeout)

    loaded = skill_text(arm, sources, previous, suite=suite)
    if suite == "router":
        prompt = (
            "Classify two independent dimensions. Return exactly: "
            "REASONING=<NONE|DECISION|DEBUGGING|IMPLEMENTATION>; "
            "RETRIEVAL=<NONE|TARGETED|BOUNDED|STRUCTURAL>. "
            "NONE means no reasoning module or no repository context is needed. "
            "TARGETED means a known path or symbol is enough; BOUNDED means location is unknown but bounded/ranked/text search is enough; "
            "STRUCTURAL means callers, callees, implementations, dependencies, or broad cross-file flow are the main retrieval need. "
            "Classify only; do not use tools or solve it.\n\nRequest: " + request + "\n\n" + loaded
        )
    elif suite == "decision":
        prompt = request + "\n\nReturn only the first decision round, then wait. Do not use tools or implement.\n" + loaded
    elif suite in {"delivery", "debug"}:
        prompt = request + "\n\nImplement the requested change in the current workspace. Do not start long-lived services.\n" + loaded
    else:
        prompt = request + "\n\nHandle this request in the current workspace. Do not start long-lived services.\n" + loaded
    (cell / "prompt.txt").write_text(prompt, encoding="utf-8")
    env = os.environ.copy()
    if arm == "practical-native":
        eval_home = eval_homes["native"]
    elif arm == "practical-native-previous":
        eval_home = eval_homes["native-previous"]
    else:
        eval_home = eval_homes["default"]
    env["CODEX_HOME"] = str(eval_home)
    codex = resolve_codex(args.codex)
    first_out, first_err = cell / "round1.jsonl", cell / "round1.stderr.txt"
    code, timed_out, forced, duration = run_codex(codex_command(codex, workspace), prompt, workspace, env, first_out, first_err, args.timeout)
    parsed = parse_transcript(first_out)
    rounds = [parsed]
    answers = [parsed["answer"]]
    if suite == "decision" and parsed["thread_id"] and not timed_out:
        second_prompt = DECISION_CASES[case]["reply"]
        (cell / "round2-prompt.txt").write_text(second_prompt, encoding="utf-8")
        second_out, second_err = cell / "round2.jsonl", cell / "round2.stderr.txt"
        code2, timed2, forced2, duration2 = run_codex(codex_command(codex, workspace, resume=parsed["thread_id"]), second_prompt, workspace, env, second_out, second_err, args.timeout)
        second = parse_transcript(second_out)
        rounds.append(second)
        answers.append(second["answer"])
        code = code2 if code2 else code
        timed_out = timed_out or timed2
        forced = forced or forced2
        duration += duration2

    usage = {key: sum(round_["usage"].get(key, 0) for round_ in rounds) for key in rounds[0]["usage"]}
    tool_calls = sum(round_["tool_calls"] for round_ in rounds)
    setup_duration = dependency_setup["duration_seconds"] if dependency_setup else 0.0
    record: dict[str, Any] = {"suite": suite, "case": case, "arm": arm, "repetition": repetition, "exit_status": code, "timed_out": timed_out, "forced_after_completion": forced, "duration_seconds": duration, "setup_duration_seconds": setup_duration, "dependency_setup": dependency_setup, "tool_calls": tool_calls, **usage, "workspace": str(workspace), "answers": answers}
    infrastructure_error = "timeout" if timed_out else (f"codex exit status {code}" if code and not forced else None)
    if infrastructure_error:
        record.update({"passed": None, "verdict": "indeterminate", "error": infrastructure_error})
        (cell / "answer.md").write_text("\n\n--- ROUND ---\n\n".join(answers) + "\n", encoding="utf-8")
        (cell / "result.json").write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return record
    if suite == "router":
        expected_reasoning, expected_retrieval, _ = ROUTER_CASES[case]
        actual_reasoning, actual_retrieval = parse_router_answer(answers[0])
        reasoning_ok = actual_reasoning == expected_reasoning
        retrieval_ok = actual_retrieval == expected_retrieval
        record.update({
            "expected_reasoning": expected_reasoning,
            "actual_reasoning": actual_reasoning,
            "reasoning_ok": reasoning_ok,
            "expected_retrieval": expected_retrieval,
            "actual_retrieval": actual_retrieval,
            "retrieval_ok": retrieval_ok,
            "passed": reasoning_ok and retrieval_ok,
        })
    elif suite == "decision":
        first = decision_metrics(answers[0])
        second = decision_metrics(answers[1]) if len(answers) > 1 else {"questions": 999, "recommendations": 0, "has_tradeoff": False, "attempted_implementation": False}
        expected_terms = DECISION_CASES[case]["expected"]
        converged = second["questions"] == 0 and any(term in answers[-1].lower() for term in expected_terms)
        passed = first["questions"] > 0 and first["recommendations"] >= first["questions"] and not first["attempted_implementation"] and converged and not second["attempted_implementation"]
        record.update({"first_round": first, "second_round": second, "converged": converged, "passed": passed})
    elif suite == "behavior":
        commands = [command for round_ in rounds for command in round_["tool_commands"]]
        outputs = [output for round_ in rounds for output in round_["tool_outputs"]]
        behavior = BEHAVIOR_CASES[case]
        record.update(behavior_score(commands, behavior["reasoning_module"], outputs, behavior["retrieval"], behavior.get("backend")))
    else:
        if case in ponytail.TASKS:
            scored = ponytail.score_workspace(case, arm, MODEL, workspace)
        else:
            scored = custom_debug_score(case, workspace)
            scored.update(ponytail.git_diff_stats(workspace))
        build = None if args.no_builds else post_build(case, workspace, args.build_timeout)
        build_indeterminate = bool(build and build.get("infrastructure_error"))
        passed = None if build_indeterminate else scored.get("correct") == 1 and scored.get("safe") == 1 and (build is None or build["passed"])
        record.update(scored)
        record.update({"build": build, "build_duration_seconds": build["duration_seconds"] if build else 0.0, "end_to_end_duration_seconds": setup_duration + duration + (build["duration_seconds"] if build else 0.0), "passed": passed})
        if build_indeterminate:
            record["indeterminate_reason"] = build["infrastructure_error"]
    record["verdict"] = "indeterminate" if record.get("passed") is None else ("pass" if record["passed"] else "fail")
    (cell / "answer.md").write_text("\n\n--- ROUND ---\n\n".join(answers) + "\n", encoding="utf-8")
    (cell / "result.json").write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return record


def aggregate(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        groups[(record["suite"], record["case"], record["arm"])].append(record)
    rows = []
    for (suite, case, arm), cells in sorted(groups.items()):
        determinate = [cell for cell in cells if cell.get("verdict") != "indeterminate"]
        row: dict[str, Any] = {
            "suite": suite,
            "case": case,
            "arm": arm,
            "n": len(cells),
            "determinate_n": len(determinate),
            "indeterminate_n": len(cells) - len(determinate),
            "pass_rate": (sum(bool(cell.get("passed")) for cell in determinate) / len(determinate)) if determinate else None,
        }
        for key in ("total_loc", "input_tokens", "cached_input_tokens", "uncached_input_tokens", "output_tokens", "reasoning_output_tokens", "total_tokens", "duration_seconds", "setup_duration_seconds", "build_duration_seconds", "end_to_end_duration_seconds", "tool_calls"):
            values = [float(cell[key]) for cell in determinate if cell.get(key) is not None]
            if values:
                row[f"{key}_median"] = statistics.median(values)
                row[f"{key}_mean"] = statistics.mean(values)
                row[f"{key}_stdev"] = statistics.stdev(values) if len(values) > 1 else 0.0
        if suite in {"delivery", "debug"}:
            row["correct_rate"] = (sum(cell.get("correct") == 1 for cell in determinate) / len(determinate)) if determinate else None
            row["safe_rate"] = (sum(cell.get("safe") == 1 for cell in determinate) / len(determinate)) if determinate else None
            builds = [cell["build"]["passed"] for cell in determinate if cell.get("build") is not None]
            row["build_rate"] = (sum(builds) / len(builds)) if builds else None
        rows.append(row)
    return rows


def _comparator_arms_for(summary: list[dict[str, Any]], suite: str, case: str | None = None) -> list[str]:
    arms = {
        row["arm"]
        for row in summary
        if row["suite"] == suite
        and row["arm"] not in {"practical-current", "practical-native", "practical-native-previous"}
        and (case is None or row["case"] == case)
    }
    preferred = [COMPARATORS.get(suite), "practical-previous", "grilling", "grill-me", "baseline"]
    ordered = [arm for arm in preferred if arm in arms]
    ordered.extend(sorted(arm for arm in arms if arm not in ordered))
    return ordered


def comparisons(summary: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_key = {(row["suite"], row["case"], row["arm"]): row for row in summary}
    rows = []
    for current in summary:
        if current["arm"] != "practical-current":
            continue
        for arm in _comparator_arms_for(summary, current["suite"], current["case"]):
            other = by_key.get((current["suite"], current["case"], arm))
            if not other:
                continue
            if current.get("indeterminate_n", 0) or other.get("indeterminate_n", 0):
                continue
            row = {"suite": current["suite"], "case": current["case"], "current": "practical-current", "comparator": arm}
            for key in ("pass_rate", "correct_rate", "safe_rate", "total_loc_median", "uncached_input_tokens_median", "output_tokens_median", "duration_seconds_median", "end_to_end_duration_seconds_median"):
                if key in current and key in other and current[key] is not None and other[key] is not None:
                    row[f"{key}_delta"] = current[key] - other[key]
            rows.append(row)
    return rows


def suite_rollups(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return aggregate([{**record, "case": "__all__"} for record in records])


def _geometric_ratio(
    current: dict[str, Any],
    comparator: dict[str, Any],
    weighted_metrics: dict[str, float],
) -> tuple[float | None, dict[str, float]]:
    ratios: dict[str, float] = {}
    available: list[tuple[float, float]] = []
    for metric, weight in weighted_metrics.items():
        current_value = current.get(metric)
        comparator_value = comparator.get(metric)
        if current_value is None or comparator_value is None:
            continue
        current_cost = float(current_value)
        comparator_cost = float(comparator_value)
        if current_cost <= 0 or comparator_cost <= 0:
            continue
        ratio = comparator_cost / current_cost
        ratios[metric] = ratio
        available.append((weight, ratio))
    if not available:
        return None, ratios
    weight_total = sum(weight for weight, _ in available)
    efficiency = math.exp(sum((weight / weight_total) * math.log(ratio) for weight, ratio in available))
    return efficiency, ratios


def _pareto_status(current: dict[str, Any], comparator: dict[str, Any]) -> str:
    quality_metrics = ("pass_rate", "correct_rate", "safe_rate", "build_rate")
    cost_metrics = (*COST_WEIGHTS, "total_loc_median")
    comparisons_: list[int] = []
    for metric in quality_metrics:
        if current.get(metric) is not None and comparator.get(metric) is not None:
            delta = float(current[metric]) - float(comparator[metric])
            comparisons_.append(1 if delta > 0 else -1 if delta < 0 else 0)
    for metric in cost_metrics:
        if current.get(metric) is not None and comparator.get(metric) is not None:
            delta = float(comparator[metric]) - float(current[metric])
            comparisons_.append(1 if delta > 0 else -1 if delta < 0 else 0)
    if comparisons_ and all(value >= 0 for value in comparisons_) and any(value > 0 for value in comparisons_):
        return "practical-dominates"
    if comparisons_ and all(value <= 0 for value in comparisons_) and any(value < 0 for value in comparisons_):
        return "comparator-dominates"
    return "tradeoff"


def scorecards(summary: list[dict[str, Any]], rollups: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Quality-gated relative efficiency; never trades safety for resource savings."""
    summary_by_key = {(row["suite"], row["case"], row["arm"]): row for row in summary}
    rollup_by_key = {(row["suite"], row["arm"]): row for row in rollups}
    cards: list[dict[str, Any]] = []
    suites = sorted({row["suite"] for row in rollups if row["arm"] == "practical-current"})
    for suite in suites:
        current = rollup_by_key.get((suite, "practical-current"))
        if not current:
            continue
        for comparator_arm in _comparator_arms_for(rollups, suite):
            comparator = rollup_by_key.get((suite, comparator_arm))
            if not comparator:
                continue
            case_names = sorted({case for row_suite, case, arm in summary_by_key if row_suite == suite and arm == "practical-current"})
            sample_reasons: list[str] = []
            quality_reasons: list[str] = []
            for case in case_names:
                current_case = summary_by_key[(suite, case, "practical-current")]
                comparator_case = summary_by_key.get((suite, case, comparator_arm))
                if not comparator_case:
                    sample_reasons.append(f"{case}: comparator cell missing")
                    continue
                for arm_name, case_row in (("practical", current_case), (comparator_arm, comparator_case)):
                    if case_row.get("n", 0) < 3:
                        sample_reasons.append(f"{case}/{arm_name}: n={case_row.get('n', 0)} < 3")
                    if case_row.get("indeterminate_n", 0):
                        sample_reasons.append(f"{case}/{arm_name}: indeterminate={case_row['indeterminate_n']}")
                if case in STRICT_SAFETY_CASES:
                    current_safe = current_case.get("safe_rate")
                    comparator_safe = comparator_case.get("safe_rate")
                    if current_safe is not None and comparator_safe is not None and current_safe < comparator_safe:
                        quality_reasons.append(f"{case}: safety {current_safe:.3f} < {comparator_safe:.3f}")

            current_pass = current.get("pass_rate")
            comparator_pass = comparator.get("pass_rate")
            if current_pass is None or comparator_pass is None:
                quality_reasons.append("suite pass rate unavailable")
            elif current_pass < comparator_pass - PASS_NONINFERIORITY_MARGIN:
                quality_reasons.append(
                    f"pass rate {current_pass:.3f} is more than {PASS_NONINFERIORITY_MARGIN:.3f} below {comparator_pass:.3f}"
                )
            for metric in ("safe_rate", "build_rate"):
                current_value = current.get(metric)
                comparator_value = comparator.get(metric)
                if current_value is not None and comparator_value is not None and current_value < comparator_value:
                    quality_reasons.append(f"{metric} {current_value:.3f} < {comparator_value:.3f}")

            efficiency, cost_ratios = _geometric_ratio(current, comparator, COST_WEIGHTS)
            quality_ratio = None
            utility = None
            if current_pass is not None and comparator_pass is not None:
                quality_ratio = (float(current_pass) + 0.01) / (float(comparator_pass) + 0.01)
                if not quality_reasons and efficiency is not None:
                    utility = (quality_ratio**2) * efficiency
            cards.append(
                {
                    "suite": suite,
                    "current": "practical-current",
                    "comparator": comparator_arm,
                    "sample_qualified": not sample_reasons,
                    "quality_qualified": not quality_reasons,
                    "status": "qualified" if not sample_reasons and not quality_reasons else "provisional" if not quality_reasons else "not-qualified",
                    "pareto": _pareto_status(current, comparator),
                    "pass_noninferiority_margin": PASS_NONINFERIORITY_MARGIN,
                    "quality_ratio": quality_ratio,
                    "cost_efficiency_index": efficiency,
                    "qualified_utility_index": utility,
                    "cost_ratios": cost_ratios,
                    "sample_reasons": sample_reasons,
                    "quality_reasons": quality_reasons,
                }
            )
    return cards


def rescore_run(run_dir: Path, ponytail: Any) -> None:
    results_path = run_dir / "results.json"
    manifest_path = run_dir / "manifest.json"
    records = json.loads(results_path.read_text(encoding="utf-8"))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for record in records:
        suite, case = record["suite"], record["case"]
        answers = record.get("answers") or []
        if suite == "router":
            expected_reasoning, expected_retrieval, _ = ROUTER_CASES[case]
            actual_reasoning, actual_retrieval = parse_router_answer(answers[0] if answers else "")
            reasoning_ok = actual_reasoning == expected_reasoning
            retrieval_ok = actual_retrieval == expected_retrieval
            record.update({
                "expected_reasoning": expected_reasoning,
                "actual_reasoning": actual_reasoning,
                "reasoning_ok": reasoning_ok,
                "expected_retrieval": expected_retrieval,
                "actual_retrieval": actual_retrieval,
                "retrieval_ok": retrieval_ok,
                "passed": reasoning_ok and retrieval_ok,
            })
        elif suite == "decision":
            first = decision_metrics(answers[0]) if answers else decision_metrics("")
            second = decision_metrics(answers[1]) if len(answers) > 1 else {"questions": 999, "recommendations": 0, "has_tradeoff": False, "attempted_implementation": False}
            converged = second["questions"] == 0 and any(term in (answers[-1].lower() if answers else "") for term in DECISION_CASES[case]["expected"])
            passed = first["questions"] > 0 and first["recommendations"] >= first["questions"] and not first["attempted_implementation"] and converged and not second["attempted_implementation"]
            record.update({"first_round": first, "second_round": second, "converged": converged, "passed": passed})
        elif suite == "behavior":
            commands = []
            outputs = []
            for transcript in sorted(Path(record["workspace"]).parent.glob("round*.jsonl")):
                parsed = parse_transcript(transcript)
                commands.extend(parsed["tool_commands"])
                outputs.extend(parsed["tool_outputs"])
            behavior = BEHAVIOR_CASES[case]
            record.update(behavior_score(commands, behavior["reasoning_module"], outputs, behavior["retrieval"], behavior.get("backend")))
        elif "workspace" in record:
            workspace = Path(record["workspace"])
            scored = ponytail.score_workspace(case, record["arm"], MODEL, workspace) if case in ponytail.TASKS else custom_debug_score(case, workspace)
            if case not in ponytail.TASKS:
                scored.update(ponytail.git_diff_stats(workspace))
            record.update(scored)
            build = record.get("build")
            if build is not None:
                build["infrastructure_error"] = build.get("infrastructure_error") or build_infrastructure_error(build.get("output_tail", ""))
            if build and build.get("infrastructure_error"):
                record["passed"] = None
                record["indeterminate_reason"] = build["infrastructure_error"]
            else:
                record["passed"] = scored.get("correct") == 1 and scored.get("safe") == 1 and (build is None or build.get("passed"))
        if record.get("error") or record.get("timed_out"):
            record["verdict"] = "indeterminate"
        else:
            record["verdict"] = "indeterminate" if record.get("passed") is None else ("pass" if record["passed"] else "fail")
    summary = aggregate(records)
    deltas = comparisons(summary)
    rollups = suite_rollups(records)
    rollup_deltas = comparisons(rollups)
    cards = scorecards(summary, rollups)
    results_path.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (run_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    (run_dir / "comparisons.json").write_text(json.dumps(deltas, indent=2) + "\n", encoding="utf-8")
    (run_dir / "rollups.json").write_text(json.dumps(rollups, indent=2) + "\n", encoding="utf-8")
    (run_dir / "rollup-comparisons.json").write_text(json.dumps(rollup_deltas, indent=2) + "\n", encoding="utf-8")
    (run_dir / "scorecards.json").write_text(json.dumps(cards, indent=2) + "\n", encoding="utf-8")
    manifest.update({"rescored_at": dt.datetime.now(dt.timezone.utc).isoformat(), "runner_version": VERSION, "runner_sha256": sha256(Path(__file__))})
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    write_report(run_dir / "report.md", manifest, summary, deltas, float(manifest.get("suite_elapsed_seconds", 0)), rollups, rollup_deltas, cards)
    print(f"rescored {len(records)} cells in {run_dir}")


def write_report(path: Path, manifest: dict[str, Any], summary: list[dict[str, Any]], deltas: list[dict[str, Any]], elapsed: float, rollups: list[dict[str, Any]], rollup_deltas: list[dict[str, Any]], cards: list[dict[str, Any]]) -> None:
    lines = ["# Practical Coding benchmark report", "", f"- Model: `{MODEL}` / `{REASONING}`", f"- Profile: `{manifest['profile']}`", f"- Runs: `{manifest['runs']}`", f"- Suite elapsed: `{elapsed:.1f}s`", "", "## Results", "", "| Suite | Case | Arm | n | Indeterminate | Pass | Correct | Safe | Build | LOC median | Tokens median | Uncached median | Time median |", "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for row in summary:
        def pct(value: Any) -> str:
            return "—" if value is None else f"{100 * value:.1f}%"
        lines.append("| {suite} | {case} | {arm} | {n} | {indeterminate} | {passed} | {correct} | {safe} | {build} | {loc} | {tokens} | {uncached} | {time} |".format(
            suite=row["suite"], case=row["case"], arm=row["arm"], n=row["n"], indeterminate=row.get("indeterminate_n", 0), passed=pct(row["pass_rate"]), correct=pct(row.get("correct_rate")), safe=pct(row.get("safe_rate")), build=pct(row.get("build_rate")), loc=f"{row.get('total_loc_median', 0):.0f}" if "total_loc_median" in row else "—", tokens=f"{row.get('total_tokens_median', 0):.0f}", uncached=f"{row.get('uncached_input_tokens_median', 0):.0f}", time=f"{row.get('duration_seconds_median', 0):.1f}s"))
    if deltas:
        lines += ["", "## Practical deltas", "", "Positive pass deltas favor Practical; negative LOC/token/time deltas mean Practical used less.", "", "| Suite | Case | Comparator | Pass pp | LOC | Uncached tokens | Output tokens | Model time |", "|---|---|---|---:|---:|---:|---:|---:|"]
        for row in deltas:
            pp = 100 * row.get("pass_rate_delta", 0)
            lines.append(f"| {row['suite']} | {row['case']} | {row['comparator']} | {pp:+.1f} | {row.get('total_loc_median_delta', 0):+.0f} | {row.get('uncached_input_tokens_median_delta', 0):+.0f} | {row.get('output_tokens_median_delta', 0):+.0f} | {row.get('duration_seconds_median_delta', 0):+.1f}s |")
    if rollups:
        lines += ["", "## Suite rollups", "", "| Suite | Arm | Cells | Indeterminate | Pass | Correct | Safe | Tokens median | Time median |", "|---|---|---:|---:|---:|---:|---:|---:|---:|"]
        for row in rollups:
            correct = "—" if row.get("correct_rate") is None else f"{100 * row['correct_rate']:.1f}%"
            safe = "—" if row.get("safe_rate") is None else f"{100 * row['safe_rate']:.1f}%"
            passed = "—" if row.get("pass_rate") is None else f"{100 * row['pass_rate']:.1f}%"
            lines.append(f"| {row['suite']} | {row['arm']} | {row['n']} | {row.get('indeterminate_n', 0)} | {passed} | {correct} | {safe} | {row.get('total_tokens_median', 0):.0f} | {row.get('duration_seconds_median', 0):.1f}s |")
    if rollup_deltas:
        lines += ["", "## Suite-level Practical deltas", "", "| Suite | Comparator | Pass pp | LOC | Uncached tokens | Output tokens | Model time |", "|---|---|---:|---:|---:|---:|---:|"]
        for row in rollup_deltas:
            lines.append(f"| {row['suite']} | {row['comparator']} | {100 * row.get('pass_rate_delta', 0):+.1f} | {row.get('total_loc_median_delta', 0):+.0f} | {row.get('uncached_input_tokens_median_delta', 0):+.0f} | {row.get('output_tokens_median_delta', 0):+.0f} | {row.get('duration_seconds_median_delta', 0):+.1f}s |")
    if cards:
        lines += ["", "## Quality-gated scorecards", "", "A score is emitted only after the quality gate passes. Efficiency above 1 favors Practical; the utility index squares the pass-rate ratio before applying efficiency. A qualified ranking also requires n>=3 with no indeterminate cells.", "", "| Suite | Comparator | Status | Pareto | Quality ratio | Efficiency | Qualified utility |", "|---|---|---|---|---:|---:|---:|"]
        for card in cards:
            quality = "—" if card["quality_ratio"] is None else f"{card['quality_ratio']:.3f}"
            efficiency = "—" if card["cost_efficiency_index"] is None else f"{card['cost_efficiency_index']:.3f}"
            utility = "—" if card["qualified_utility_index"] is None else f"{card['qualified_utility_index']:.3f}"
            lines.append(f"| {card['suite']} | {card['comparator']} | {card['status']} | {card['pareto']} | {quality} | {efficiency} | {utility} |")
    lines += ["", "## Interpretation", "", "Correctness, safety, and build pass before LOC/tokens/time. Infrastructure, timeout, and capture failures are indeterminate and excluded from pass-rate denominators. Token totals include cached input; use uncached and output columns to interpret cost. Repeated-run standard deviations are in `summary.json`. A smoke profile is not a stable ranking.", ""]
    path.write_text("\n".join(lines), encoding="utf-8")


def scorer_selftest(ponytail: Any) -> None:
    for profile_name, profile in PROFILE_CASES.items():
        missing = {
            "delivery": set(profile["delivery"]) - set(ponytail.TASKS),
            "router": set(profile["router"]) - set(ROUTER_CASES),
            "decision": set(profile["decision"]) - set(DECISION_CASES),
            "debug": set(profile["debug"]) - (set(ponytail.TASKS) | set(CUSTOM_DEBUG)),
            "behavior": set(profile["behavior"]) - set(BEHAVIOR_CASES),
        }
        if any(missing.values()):
            raise RuntimeError(f"unknown cases in profile {profile_name}: {missing}")
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        for task_id, task in ponytail.TASKS.items():
            if task.get("fixture") or task.get("open"):
                continue
            scores = {}
            for kind in ("good", "bad"):
                workspace = root / f"{task_id}-{kind}"
                workspace.mkdir()
                for name, content in task.get("seed", {}).items():
                    path = workspace / name
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text(content, encoding="utf-8")
                target = workspace / task["file"]
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(task[kind], encoding="utf-8")
                scores[kind] = task["score"](workspace)
            good, bad = scores["good"], scores["bad"]
            if good.get("correct") != 1 or good.get("safe") != 1:
                raise RuntimeError(f"Ponytail good fixture rejected: {task_id}: {good}")
            axis = task.get("axis", "safe")
            if bad.get(axis) != 0:
                raise RuntimeError(f"Ponytail bad fixture accepted: {task_id}: {bad}")
        for case, data in CUSTOM_DEBUG.items():
            workspace = root / case
            workspace.mkdir()
            for name, content in data["files"].items():
                (workspace / name).write_text(content, encoding="utf-8")
            bad = custom_debug_score(case, workspace)
            if bad["correct"] == 1 and bad["safe"] == 1:
                raise RuntimeError(f"custom debug bad fixture not caught: {case}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", choices=PROFILE_CASES, default="standard")
    parser.add_argument("--suite", action="append", choices=("delivery", "router", "decision", "debug", "behavior"), help="run only a suite; repeatable")
    parser.add_argument("--case", action="append", help="run only a case id; repeatable")
    parser.add_argument("--arm", action="append", help="run only an arm; repeatable")
    parser.add_argument("--runs", type=int, default=0)
    parser.add_argument("--workers", type=int, default=3)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--sources-root", type=Path)
    parser.add_argument("--baseline-skill", type=Path)
    parser.add_argument("--baseline-ref", help="materialize the previous Practical arm from a Git revision")
    parser.add_argument("--include-baseline", action="store_true")
    parser.add_argument("--combo-matrix", action="store_true", help="run all co-install subsets of practical/ponytail/superpowers/grill-me on delivery/decision/debug")
    parser.add_argument("--no-builds", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--rescore", type=Path, help="reapply current mechanical graders to an existing run without model calls")
    parser.add_argument("--fail-on-cell-failure", action="store_true")
    parser.add_argument("--codex", default=os.environ.get("CODEX_BIN", "codex"))
    parser.add_argument("--timeout", type=float, default=600)
    parser.add_argument("--build-timeout", type=float, default=600)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.runs < 0 or args.workers < 1:
        raise SystemExit("runs must be non-negative and workers positive")
    if args.baseline_skill and args.baseline_ref:
        raise SystemExit("use only one of --baseline-skill and --baseline-ref")
    sources_root = (args.sources_root or default_sources_root()).resolve()
    mapped = {}
    for name in SOURCES:
        candidate = sources_root / ("full-stack-fastapi-template-cd83fc1" if name == "full-stack-fastapi-template" and (sources_root / "full-stack-fastapi-template-cd83fc1").exists() else name)
        if candidate.exists():
            expected = SOURCES[name][1]
            head = run_command(["git", "rev-parse", "HEAD"], candidate)
            if head.returncode or head.stdout.strip() != expected:
                raise RuntimeError(f"{candidate} is not pinned at {expected}")
            mapped[name] = candidate
        else:
            mapped[name] = ensure_checkout(sources_root, name)
    sources = mapped
    ponytail = load_ponytail(sources)
    scorer_selftest(ponytail)
    if args.self_test:
        print("benchmark self-test: PASS")
        return 0
    if args.rescore:
        rescore_run(args.rescore.resolve(), ponytail)
        return 0
    profile = PROFILE_CASES[args.profile]
    runs = args.runs or profile["runs"]
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    default_output = ROOT / "benchmark-results" / stamp
    output = (args.output or default_output).resolve()
    output.mkdir(parents=True, exist_ok=False)
    previous = args.baseline_skill.resolve() if args.baseline_skill else None
    if args.baseline_ref:
        previous = materialize_git_skill(args.baseline_ref, output / "baseline-skill")
    if previous and not (previous / "SKILL.md").is_file():
        raise FileNotFoundError(f"baseline skill missing SKILL.md: {previous}")
    eval_homes = {
        "default": prepare_eval_home(output / "default"),
        "native": prepare_eval_home(output / "native"),
    }
    native_skill = install_native_skill(eval_homes["native"], ROOT)
    native_previous_skill = None
    if previous:
        eval_homes["native-previous"] = prepare_eval_home(output / "native-previous")
        native_previous_skill = install_native_skill(eval_homes["native-previous"], previous)
    codex_path = resolve_codex(args.codex)
    codex_version = run_command([codex_path, "--version"], ROOT)
    manifest = {"runner_version": VERSION, "runner_sha256": sha256(Path(__file__)), "model": MODEL, "reasoning": REASONING, "profile": args.profile, "runs": runs, "workers": args.workers, "started_at": dt.datetime.now(dt.timezone.utc).isoformat(), "environment": {"platform": platform.platform(), "python": sys.version, "codex": codex_version.stdout.strip(), "codex_path": codex_path}, "skill": {"current_entrypoint_sha256": sha256(ROOT / "SKILL.md"), "current_bundle_sha256": bundle_sha256(ROOT), "native_install": str(native_skill), "native_previous_install": str(native_previous_skill) if native_previous_skill else None, "previous_ref": args.baseline_ref, "previous_entrypoint_sha256": sha256(previous / "SKILL.md") if previous else None, "previous_bundle_sha256": bundle_sha256(previous) if previous else None}, "sources": {name: {"url": SOURCES[name][0], "commit": SOURCES[name][1], "path": str(sources[name])} for name in SOURCES}, "cases": profile}
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    specs = []
    previous_arm = ["practical-previous"] if previous else []
    if args.combo_matrix:
        matrix_arms = combo_arms()
        delivery_arms = [*matrix_arms, *previous_arm, *(["baseline"] if args.include_baseline else [])]
        decision_arms = [*matrix_arms, *previous_arm]
        debug_arms = [*matrix_arms, *previous_arm]
        manifest["combo_matrix"] = matrix_arms
        (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    else:
        delivery_arms = ["practical-current", "ponytail", *previous_arm, *(["baseline"] if args.include_baseline else [])]
        decision_arms = ["practical-current", "grilling", *previous_arm]
        debug_arms = ["practical-current", "superpowers", *previous_arm]
    for case in profile["delivery"]:
        for repetition in range(1, runs + 1):
            for arm in delivery_arms:
                specs.append(("delivery", case, arm, repetition))
    for case in profile["router"]:
        for repetition in range(1, runs + 1):
            for arm in ["practical-current", *previous_arm]:
                specs.append(("router", case, arm, repetition))
    for case in profile["decision"]:
        for repetition in range(1, runs + 1):
            for arm in decision_arms:
                specs.append(("decision", case, arm, repetition))
    for case in profile["debug"]:
        for repetition in range(1, runs + 1):
            for arm in debug_arms:
                specs.append(("debug", case, arm, repetition))
    for case in profile["behavior"]:
        for repetition in range(1, runs + 1):
            specs.append(("behavior", case, "practical-native", repetition))
            if previous:
                specs.append(("behavior", case, "practical-native-previous", repetition))
    if args.suite:
        specs = [spec for spec in specs if spec[0] in args.suite]
    if args.case:
        unknown = set(args.case) - {spec[1] for spec in specs}
        if unknown:
            raise ValueError(f"case not in selected profile/suite: {sorted(unknown)}")
        specs = [spec for spec in specs if spec[1] in args.case]
    if args.arm:
        unknown = set(args.arm) - {spec[2] for spec in specs}
        if unknown:
            raise ValueError(f"arm not available in selected cells: {sorted(unknown)}")
        specs = [spec for spec in specs if spec[2] in args.arm]
    if not specs:
        raise ValueError("selection produced no benchmark cells")
    records: list[dict[str, Any]] = []
    lock = threading.Lock()
    started = time.monotonic()
    print(f"running {len(specs)} Luna cells with {args.workers} workers", flush=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(run_cell, spec, args, sources, previous, ponytail, eval_homes, output): spec for spec in specs}
        for future in concurrent.futures.as_completed(futures):
            spec = futures[future]
            try:
                record = future.result()
            except Exception as error:
                record = {"suite": spec[0], "case": spec[1], "arm": spec[2], "repetition": spec[3], "passed": None, "verdict": "indeterminate", "error": repr(error)}
            with lock:
                records.append(record)
                records.sort(key=lambda item: (item["suite"], item["case"], item["arm"], item["repetition"]))
                (output / "results.json").write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            print(f"[{len(records)}/{len(specs)}] {record['suite']}/{record['case']}/{record['arm']}/r{record['repetition']} pass={record.get('passed')} error={record.get('error')}", flush=True)
    elapsed = time.monotonic() - started
    summary = aggregate(records)
    (output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    deltas = comparisons(summary)
    rollups = suite_rollups(records)
    rollup_deltas = comparisons(rollups)
    (output / "comparisons.json").write_text(json.dumps(deltas, indent=2) + "\n", encoding="utf-8")
    (output / "rollups.json").write_text(json.dumps(rollups, indent=2) + "\n", encoding="utf-8")
    (output / "rollup-comparisons.json").write_text(json.dumps(rollup_deltas, indent=2) + "\n", encoding="utf-8")
    cards = scorecards(summary, rollups)
    (output / "scorecards.json").write_text(json.dumps(cards, indent=2) + "\n", encoding="utf-8")
    write_report(output / "report.md", manifest, summary, deltas, elapsed, rollups, rollup_deltas, cards)
    manifest.update({"completed_at": dt.datetime.now(dt.timezone.utc).isoformat(), "suite_elapsed_seconds": elapsed, "cells": len(records)})
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {output}")
    infrastructure_failed = any(record.get("error") or record.get("verdict") == "indeterminate" for record in records)
    cells_failed = any(record.get("verdict") == "fail" for record in records)
    return 2 if infrastructure_failed or (args.fail_on_cell_failure and cells_failed) else 0


if __name__ == "__main__":
    raise SystemExit(main())

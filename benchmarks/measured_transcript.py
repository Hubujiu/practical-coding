"""Measured Codex JSONL evidence, without treating missing usage as zero.

The event stream is host evidence, not a security attestation. In particular,
unsupported shell programs cannot be credited as successful policy reads.
"""
from __future__ import annotations

import json
import re
import shlex
from collections import Counter
from pathlib import Path
from typing import Any, Mapping

VERSION = "1.0"
USAGE_KEYS = ("input_tokens", "cached_input_tokens", "output_tokens", "reasoning_output_tokens")
TOOLS = {"command_execution", "mcp_tool_call", "file_change", "web_search"}
REF_RE = re.compile(r"references[/\\][a-z0-9_. /\\-]+?\.md", re.I)
PROVIDERS = {"zg": "zvec-grep", "codebase-memory-mcp": "codebase-memory-mcp", "rtk": "rtk"}


def parse_transcript(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    errors: list[str] = []
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = raw.decode("utf-8-sig", errors="replace")
        errors.append("non-UTF8 transcript")
    answer = ""
    thread_id = None
    turns: list[Mapping[str, Any]] = []
    tools: dict[tuple[int, str], dict[str, Any]] = {}
    turn_index = 0
    closed = False
    failed = False
    for number, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except ValueError:
            errors.append(f"invalid JSON at line {number}")
            continue
        if not isinstance(event, dict):
            errors.append(f"non-object event at line {number}")
            continue
        kind = event.get("type")
        if kind == "thread.started":
            thread_id = event.get("thread_id")
        elif kind == "turn.started":
            turn_index += 1
            closed = False
        elif kind in {"turn.failed", "error"}:
            failed = True
        elif kind == "turn.completed":
            if closed:
                errors.append("duplicate turn completion")
            closed = True
            usage = event.get("usage")
            turns.append(usage if isinstance(usage, dict) else {})
        elif kind in {"item.started", "item.updated", "item.completed"}:
            item = event.get("item")
            if not isinstance(item, dict):
                errors.append(f"invalid item at line {number}")
                continue
            item_type = item.get("type")
            if item_type in {"agent_message", "assistant_message"} and kind == "item.completed":
                if isinstance(item.get("text"), str):
                    answer = item["text"] or answer
            if item_type not in TOOLS:
                continue
            identity = item.get("id")
            if not isinstance(identity, str) or not identity:
                errors.append(f"tool item without identity at line {number}")
                identity = f"unidentified-line-{number}"
            key = (turn_index, identity)
            previous = tools.get(key, {})
            if previous.get("_completed"):
                errors.append(f"event after tool completion: {identity}")
                continue
            tools[key] = {**previous, **item, "_completed": kind == "item.completed"}
    usage: dict[str, int | None] = {}
    for key in USAGE_KEYS:
        values = [turn.get(key) for turn in turns]
        usage[key] = (sum(values) if values and all(type(v) is int and v >= 0 for v in values) else None)
    for turn in turns:
        inputs, cached = turn.get("input_tokens"), turn.get("cached_input_tokens")
        if type(inputs) is int and type(cached) is int and cached > inputs:
            errors.append("cached input exceeds input tokens")
            usage["input_tokens"] = usage["cached_input_tokens"] = None
    usage["uncached_input_tokens"] = (
        usage["input_tokens"] - usage["cached_input_tokens"]
        if usage["input_tokens"] is not None and usage["cached_input_tokens"] is not None else None
    )
    usage["total_tokens"] = (
        usage["input_tokens"] + usage["output_tokens"]
        if usage["input_tokens"] is not None and usage["output_tokens"] is not None else None
    )
    complete = bool(turns) and closed and not failed and not errors and all(t["_completed"] for t in tools.values())
    if not complete:
        # A partial turn's unobserved consumption cannot be inferred from earlier turns.
        usage = {key: None for key in usage}
    tool_events = list(tools.values())
    outputs = [output_text(item) for item in tool_events if item.get("_completed")]
    return {
        "answer": answer, "thread_id": thread_id, "usage": usage,
        "tool_calls": len(tools), "tool_events": tool_events,
        "tool_commands": [item["command"] for item in tool_events if isinstance(item.get("command"), str)],
        "tool_outputs": outputs,
        "telemetry": {
            "schema_version": VERSION, "transcript_complete": complete,
            "usage_complete": complete and all(usage[k] is not None for k in USAGE_KEYS[:3]),
            "completed_turns": len(turns), "failed_turn": failed, "errors": errors,
        },
    }


def output_text(item: Mapping[str, Any]) -> str:
    value = item.get("aggregated_output")
    if isinstance(value, str):
        return value
    result = item.get("result")
    if isinstance(result, dict):
        content = result.get("content")
        if isinstance(content, list):
            return "\n".join(part["text"] for part in content
                             if isinstance(part, dict) and isinstance(part.get("text"), str))
    return ""


def succeeded(item: Mapping[str, Any]) -> bool:
    if item.get("_completed") is not True or item.get("status") != "completed":
        return False
    if item.get("type") == "command_execution":
        return type(item.get("exit_code")) is int and item["exit_code"] == 0
    if item.get("type") == "mcp_tool_call":
        result = item.get("result")
        return isinstance(result, dict) and not item.get("error") and result.get("isError") is not True
    return False


def command_parts(command: str, depth: int = 0) -> list[list[str]]:
    """Recognize simple shell invocations, not arbitrary shell program semantics."""
    if depth > 3:
        return []
    try:
        lexer = shlex.shlex(command, posix=False, punctuation_chars=";&|<>")
        lexer.whitespace_split = True
        lexer.commenters = "#"
        tokens = list(lexer)
    except ValueError:
        return []
    tokens = [token[1:-1] if len(token) > 1 and token[0] == token[-1] and token[0] in "\"'" else token for token in tokens]
    if tokens and tokens[0] == "&":  # PowerShell invocation operator, not an infix pipeline.
        tokens.pop(0)
    if not tokens:
        return []
    name = binary_name(tokens[0])
    if name in {"bash", "sh", "zsh", "pwsh", "powershell"}:
        for i, token in enumerate(tokens[1:], 1):
            if token.lower() in {"-c", "-lc", "-command"} and i + 1 < len(tokens):
                return command_parts(" ".join(tokens[i + 1:]), depth + 1)
        return []
    parts: list[list[str]] = [[]]
    for token in tokens:
        if token in {";", "&&", "||", "|", "&"}:
            if parts[-1]:
                parts.append([])
        elif token in {">", ">>", "<", "<<"}:
            return []  # Redirected/heredoc evidence needs a typed host adapter.
        else:
            parts[-1].append(token)
    return [part for part in parts if part]


def binary_name(value: str) -> str:
    return value.replace("\\", "/").rsplit("/", 1)[-1].lower().removesuffix(".exe").removesuffix(".cmd")


def provider_observations(events: list[dict[str, Any]]) -> dict[str, Any]:
    attempts = {name: False for name in PROVIDERS.values()}
    successes = dict(attempts)
    setup = False
    for event in events:
        invocations = command_parts(str(event.get("command", "")))
        if event.get("type") == "mcp_tool_call":
            server = binary_name(str(event.get("server", "")))
            if server == "codebase-memory-mcp":
                invocations.append([server, "cli", str(event.get("tool", ""))])
        for argv in invocations:
            name = binary_name(argv[0])
            provider = PROVIDERS.get(name)
            args = [arg.lower() for arg in argv[1:]]
            if provider:
                # Probe/init is not measured retrieval usage. Listing a project is a
                # provider invocation but does not establish that an edge was found.
                relevant = (name == "zg" and args[:1] in (["query"], ["search"])) or (
                    name == "codebase-memory-mcp" and args[:1] == ["cli"]
                ) or (name == "rtk" and bool(args) and not args[0].startswith("-"))
                if relevant:
                    attempts[provider] = True
                    successes[provider] |= succeeded(event) and len(invocations) == 1
            setup |= (name == "zg" and args[:1] == ["index"]
                      or name == "codebase-memory-mcp" and args[:2] == ["cli", "index_repository"]
                      or name == "rtk" and args[:1] == ["init"]
                      or name == "npm" and args[:1] in (["ci"], ["install"]))
    return {"attempted": attempts, "successful": successes, "setup_violation": setup}


def _lines(text: str) -> Counter[str]:
    # Permit line-number prefixes emitted by bounded readers, not arbitrary paraphrases.
    return Counter(re.sub(r"^\s*\d+[\t:|]\s?", "", line).strip()
                   for line in text.splitlines() if line.strip())


def observe_policy_reads(events: list[dict[str, Any]], root: Path) -> dict[str, Any]:
    sources = {path.relative_to(root).as_posix().lower(): _lines(path.read_text(encoding="utf-8"))
               for path in (root / "references").rglob("*.md")}
    coverage: dict[str, Counter[str]] = {}
    observed: list[str] = []
    unverified: set[str] = set()
    readers = {"cat", "sed", "head", "tail", "get-content", "type", "more", "nl"}
    transforms = {"sed", "head", "tail", "select-object", "nl"}
    for event in events:
        if not succeeded(event):
            continue
        parts = command_parts(str(event.get("command", "")))
        paths: list[str] = []
        if event.get("type") == "mcp_tool_call" and event.get("tool") in {"read_file", "read_text_file", "read_multiple_files"}:
            args = event.get("arguments")
            if isinstance(args, dict):
                paths = [str(args.get("path") or args.get("file_path") or "")]
                if isinstance(args.get("paths"), list):
                    paths += [value for value in args["paths"] if isinstance(value, str)]
        elif parts and binary_name(parts[0][0]) in readers and all(
            binary_name(part[0]) in readers | transforms for part in parts[1:]
        ):
            paths = [arg for part in parts for arg in part[1:]]
        if not paths:
            # Unknown readers cannot silently masquerade as "no policy loaded".
            # Echo/printf mentions are not reads; supported readers below need
            # content coverage, not just a path token.
            first = binary_name(parts[0][0]) if parts else ""
            if first not in {"echo", "printf", "write-output"}:
                text = str(event.get("command", "")) + json.dumps(event.get("arguments", {}))
                unverified.update(match.group(0).lower().replace("\\", "/") for match in REF_RE.finditer(text))
        refs = []
        for path in paths:
            refs.extend(match.group(0).lower().replace("\\", "/") for match in REF_RE.finditer(path))
        emitted = _lines(output_text(event))
        for ref in refs:
            expected = sources.get(ref)
            if not expected:
                unverified.add(ref)
                continue
            # Partial reads may collectively cover a file, but parent completion
            # must precede child completion in the observed sequence.
            coverage[ref] = coverage.get(ref, Counter()) | (emitted & expected)
            if not (expected - coverage[ref]) and ref not in observed:
                observed.append(ref)
            elif ref not in observed:
                unverified.add(ref)
    return {"references": observed, "unverified_references": sorted(unverified - set(observed)),
            "method": "completed-reader-and-source-content-coverage"}


def canonical_reference(raw: str) -> str:
    value = str(raw).strip().strip('<>\"\'').lower().replace('\\', '/')
    marker = 'references/'
    if marker in value:
        return marker + value.split(marker, 1)[1]
    if value.startswith('manual/') or ('/' not in value and value.endswith('.md')):
        return 'references/' + value
    return value


def verified_probe_commands(events: list[dict[str, Any]]) -> list[str]:
    """Successful executable probes, not echo/reader mentions of a command."""
    names = {'npm', 'npx', 'vitest', 'mvn', 'mvnw', 'python', 'python3', 'pytest', 'node'}
    result = []
    for event in events:
        if not succeeded(event) or event.get('type') != 'command_execution':
            continue
        parts = command_parts(str(event.get('command', '')))
        if len(parts) != 1:
            continue  # Compound command exit status does not establish each probe's status.
        argv = parts[0]
        if binary_name(argv[0]) == 'rtk' and len(argv) > 1:
            argv = argv[2:] if argv[1] == 'proxy' else argv[1:]
        if argv and binary_name(argv[0]) in names:
            result.append(' '.join(argv))
    return result

"""Observational retrieval metadata; never used by an answer scorer.

Bytes are UTF-8 bytes recorded in the transcript, not pre-truncation output or
an estimate of model-visible tokens. Mixed calls have overlapping category byte
upper bounds because their output cannot be separated retrospectively.
"""
from __future__ import annotations

import hashlib
import json
import re
import shlex
from pathlib import Path
from typing import Any, Iterable

VERSION = "1.1"
CATEGORIES = (
    "broad_inventory", "broad_search", "focused_search", "bounded_read",
    "whole_file_read", "dependency_source", "test_or_build", "other",
)
TOOL_TYPES = {"command_execution", "mcp_tool_call", "file_change"}
SOURCE_SUFFIXES = {".py", ".java", ".js", ".jsx", ".ts", ".tsx", ".go", ".rs",
                   ".c", ".cpp", ".h", ".cs", ".kt", ".swift", ".vue", ".rb"}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def normalized(command: str) -> str:
    command, _ = command_body(command)
    # Preserve quoted payloads: collapsing their whitespace changes queries.
    parts = re.split(r"('(?:[^']|'')*'|\"(?:\\.|[^\"])*\")", command.strip())
    return "".join(part if index % 2 else re.sub(r"\s+", " ", part)
                   for index, part in enumerate(parts))


def path_text(value: str) -> str:
    return re.sub(r"/+", "/", value.replace("\\", "/"))


def command_body(command: str) -> tuple[str, str]:
    """Decode CLI shell-word rendering, without executing the command.

    Raw scripts are already scripts, not argv. Only unwrap recognized shell
    executables; an argument that merely contains '-Command' is not a launcher.
    """
    launcher = re.match(r'^\s*[\'\"]?(?:[^\r\n]*[/\\])?(?:pwsh|powershell|bash|sh)(?:\.exe)?[\'\"]?\s', command, re.I)
    if not launcher:
        return command, "raw_script"
    try:
        args = shlex.split(command)
    except ValueError:
        return command, "invalid_shell_rendering"
    for index, arg in enumerate(args[1:], 1):
        if arg.lower() in {"-command", "-c", "-lc"}:
            if len(args) == index + 2:
                return args[index + 1], "decoded_shell_argv"
            return command, "unsupported_shell_arguments"
    return command, "unsupported_shell_arguments"


def classify(command: str, project_paths: Iterable[str] = ()) -> list[str]:
    """Conservative command-shape tags, including all observed mixed categories.

    A repository-wide glob is still broad. A pipe limiting returned lines does
    not make the underlying search scoped. Unrecognized commands remain other.
    """
    body, decoding = command_body(command)
    if decoding in {"invalid_shell_rendering", "unsupported_shell_arguments"}:
        return ["other"]
    text = path_text(body).lower()
    # Mask quoted payloads for command-position detection, retaining character
    # positions. Paths/scopes and read bounds still use the unmasked script.
    executable_text = re.sub(r"'(?:[^']|'')*'|\"(?:`.|[^\"])*\"", lambda m: " " * len(m[0]), text)
    # Command positions, not arbitrary words in search patterns or symbol names.
    position = r"(?:^|[;|({}\n]|=)\s*(?:&\s*)?"
    ending = r"(?=\s|[;|)}]|$)"
    def invokes(pattern: str) -> bool:
        return bool(re.search(position + r"(?:" + pattern + r")" + ending, executable_text))
    inventory_pattern = r"rg\s+--files|git\s+ls-files|get-childitem|gci|ls|dir|find"
    search_pattern = r"rg(?!\s+--files)|grep|select-string|search_code|search_files"
    read = invokes(r"get-content|gc|cat|type|read_file|readfile|sed|head|tail") or bool(re.search(r"\.(?:read_(?:text|bytes)|readtoend|readline|readalltext|readalllines)\(", executable_text))
    bounded = bool(re.search(r"-(?:head|tail|totalcount|first|last|skip)\b|\bselect-object\s+-index|\[\s*\d+\s*\.\.\s*\d+\s*\]|\b(head|tail)\s+-\w*\d+|\bsed\b|\bread_file\b.*\b(start_line|end_line|limit)\b|\$\w+\s+-[lg][et]\s+\d+", text))
    # Concrete source paths or literal directory operands (not glob patterns).
    paths = [path_text(p).lower() for p in project_paths]
    directories = {p.split("/", 1)[0] for p in paths if "/" in p}
    tags: set[str] = set()
    for pattern, broad_category in ((inventory_pattern, "broad_inventory"), (search_pattern, "broad_search")):
        for match in re.finditer(position + r"(?:" + pattern + r")" + ending, executable_text):
            delimiter = re.search(r"[;|}\n]", executable_text[match.end():])
            end = match.end() + delimiter.start() if delimiter else len(text)
            segment = text[match.start():end]
            # Resolve literal scope variables within this script only. Pipeline
            # filters consume their predecessor's output, not the repository.
            assignments = dict(re.findall(r"(\$[a-z_]\w*)\s*=\s*['\"]([^'\"\r\n]*)['\"]", text[:match.start()]))
            for variable, value in assignments.items():
                segment = re.sub(re.escape(variable) + r"\b", lambda _: value, segment)
            scoped = any(p in segment for p in paths if p)
            scoped |= any(re.search(r"(?:^|\s)['\"]?" + re.escape(p) + r"/?['\"]?(?=\s|$)", segment) for p in directories)
            scoped |= bool(re.search(r"(?<![\w*])(?:[\w.-]+/)+[\w.-]+(?![\w*])", segment))
            root_operand = bool(re.search(r"(?:^|\s)['\"]?\./?['\"]?(?=\s|$)", segment))
            if broad_category == "broad_search" and match[0].lstrip().startswith("|") and not root_operand:
                scoped = True
            tags.add(broad_category if root_operand or not scoped else "focused_search")
    if read:
        # A limit somewhere in a compound call cannot prove every read bounded.
        read_count = len(re.findall(position + r"(get-content|gc|cat|type|read_file|readfile)\b", executable_text))
        tags.add("bounded_read" if bounded and read_count <= 1 else "whole_file_read")
    if (read or invokes(search_pattern) or invokes("javap")) and re.search(r"(?:^|/|\s)(?:node_modules|site-packages|\.m2|\.gradle|vendor)(?:/|\b)|\bjavap\b|sources\.jar", text):
        tags.add("dependency_source")
    if invokes(r"pytest|python\s+-m\s+(?:pytest|unittest)|(?:\./)?mvnw?|(?:\./)?gradlew?|tsc|make|cmake|(?:npm|pnpm|yarn|bun)\s+(?:run\s+)?(?:test|build|check|lint|typecheck)|(?:cargo|go|dotnet)\s+(?:test|build|check)"):
        tags.add("test_or_build")
    return [category for category in CATEGORIES if category in tags] or ["other"]


def output_data(item: dict[str, Any]) -> tuple[bytes | None, str]:
    if isinstance(item.get("aggregated_output"), str):
        return item["aggregated_output"].encode("utf-8"), "aggregated_output"
    if item.get("type") == "mcp_tool_call" and item.get("result") is not None:
        result = item["result"]
        value = result if isinstance(result, str) else json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        return value.encode("utf-8"), "result_canonical_json" if not isinstance(result, str) else "result_text"
    return None, "unavailable"


def measure_transcript(path: Path, *, project_paths: Iterable[str] = ()) -> dict[str, Any]:
    paths = tuple(path_text(p) for p in project_paths)
    sources = {p for p in paths if Path(p).suffix.lower() in SOURCE_SUFFIXES}
    events: list[dict[str, Any]] = []
    seen: set[str] = set()
    candidate_seen = project_read_seen = False
    malformed = 0
    usage_seen = False
    usage_fields: set[str] = set()
    totals = {"tool_output_bytes": 0, "tool_output_lines": 0, "max_single_output_bytes": 0,
              "whole_file_read_bytes": 0, "dependency_source_bytes": 0, "test_or_build_bytes": 0,
              "duplicate_command_calls": 0, "broad_calls_after_first_project_read": 0,
              "broad_calls_after_first_project_candidate": 0, "outputs_over_16k": 0, "outputs_over_64k": 0}
    totals.update({f"{c}_calls": 0 for c in CATEGORIES})
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        try:
            event = json.loads(line)
        except ValueError:
            malformed += 1
            continue
        if not isinstance(event, dict):
            malformed += 1
            continue
        if event.get("type") == "turn.completed":
            usage_seen = True
            usage_fields.update((event.get("usage") or {}).keys())
        item = event.get("item") or {}
        if event.get("type") != "item.completed" or item.get("type") not in TOOL_TYPES:
            continue
        command = item.get("command")
        if not isinstance(command, str):
            command = ":".join(str(item.get(k, "")) for k in ("type", "server", "tool"))
            if "arguments" in item:
                command += " " + json.dumps(item["arguments"], sort_keys=True, ensure_ascii=False)
        tags = classify(command, paths)
        body, decoding = command_body(command)
        raw, representation = output_data(item)
        output = raw.decode("utf-8") if raw is not None else ""
        size = len(raw) if raw is not None else None
        lines = len(output.splitlines()) if raw is not None else None
        identity = normalized(command)
        duplicate = identity in seen
        seen.add(identity)
        # Only concrete source-content matches establish discovery; a file list
        # alone does not identify which of thousands of paths is a candidate.
        mentioned = [p for p in sources if p in path_text(body)]
        source_read = bool(mentioned and {"bounded_read", "whole_file_read"}.intersection(tags)
                           and "dependency_source" not in tags and item.get("exit_code", 0) == 0
                           and raw)
        output_paths = {m.group(1).removeprefix("./") for m in re.finditer(r"(?:^|\n)([^\r\n:]+):\d+[:\-]", path_text(output))}
        source_hit = bool({"focused_search", "broad_search"}.intersection(tags) and sources.intersection(output_paths))
        truncated = bool(raw and (len(raw) == 1048576 or re.search(r"output.{0,40}truncat|truncat.{0,40}output", output, re.I)))
        row = {
            "sequence": len(events) + 1, "transcript_line": line_number,
            "item_id": item.get("id"), "tool_type": item["type"], "command": command,
            "command_sha256": digest(identity.encode()), "category": tags[0], "categories": tags,
            "command_decoding": decoding,
            "output_bytes": size, "output_lines": lines, "output_sha256": digest(raw) if raw is not None else None,
            "output_representation": representation, "duplicate_command": duplicate,
            "large_output": size is not None and size > 16384,
            "after_project_candidate": candidate_seen, "after_first_project_read": project_read_seen,
            "project_source_read": source_read, "project_source_candidate": source_hit or source_read,
            "mixed_category_attribution": len(tags) > 1, "possible_truncation": truncated,
        }
        events.append(row)
        for tag in tags:
            totals[f"{tag}_calls"] += 1
            if f"{tag}_bytes" in totals:
                totals[f"{tag}_bytes"] += size or 0
        totals["tool_output_bytes"] += size or 0
        totals["tool_output_lines"] += lines or 0
        totals["max_single_output_bytes"] = max(totals["max_single_output_bytes"], size or 0)
        totals["duplicate_command_calls"] += int(duplicate)
        broad = bool({"broad_inventory", "broad_search"}.intersection(tags))
        totals["broad_calls_after_first_project_read"] += int(broad and project_read_seen)
        totals["broad_calls_after_first_project_candidate"] += int(broad and candidate_seen)
        totals["outputs_over_16k"] += int((size or 0) > 16384)
        totals["outputs_over_64k"] += int((size or 0) > 65536)
        candidate_seen |= source_hit or source_read
        project_read_seen |= source_read
    measured = sum(e["output_bytes"] is not None for e in events)
    missing_usage = sorted({"input_tokens", "cached_input_tokens", "output_tokens"} - usage_fields)
    return {
        "retrieval_metrics_version": VERSION, "retrieval_events": events, **totals,
        "measurement_coverage": {
            "completed_tool_events": len(events), "measured_output_events": measured,
            "output_event_ratio": measured / len(events) if events else None,
            "missing_output_events": len(events) - measured, "malformed_transcript_lines": malformed,
            "unknown_category_events": sum(e["categories"] == ["other"] for e in events),
            "shell_decode_failures": sum(e["command_decoding"] in {"invalid_shell_rendering", "unsupported_shell_arguments"} for e in events),
            "unclassified_output_bytes": sum(e["output_bytes"] or 0 for e in events if e["categories"] == ["other"]),
            "mixed_category_events": sum(e["mixed_category_attribution"] for e in events),
            "possible_truncation_events": sum(e["possible_truncation"] for e in events),
            "usage_seen": usage_seen, "missing_usage_fields": missing_usage,
            "project_path_count": len(paths), "project_source_path_count": len(sources),
            "byte_scope": "recorded UTF-8 output only; mixed category bytes overlap; semantic query equivalence requires audit",
        },
    }

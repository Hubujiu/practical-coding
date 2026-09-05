"""Canonical dependency-benchmark trace parser.

The historical tree runner accepted only alphabetic retrieval labels. Active
Retrieval stages contain digits (R0-R3), so dependency-enabled runners share
this parser instead of weakening their trace contract or rewriting old result
files.
"""

from __future__ import annotations

import re
from typing import Any


TRACE_RE = re.compile(
    r"TREE_TRACE\s+path=([^\s]+)\s+retrieval=([A-Z0-9_]+)\s+manual=([a-z_-]+)\s+refs=([^\r\n]+)",
    re.I,
)
RETRIEVAL_REF_RE = re.compile(
    r"references[/\\]retrieval[/\\](?:skill|direct|discovery|evidence|structural)\.md",
    re.I,
)


def parse_trace(answer: str) -> dict[str, Any]:
    matches = list(TRACE_RE.finditer(answer))
    if not matches:
        return {"path": [], "retrieval": None, "manual": None, "references_loaded": []}
    match = matches[-1]
    raw_path = match.group(1).strip().strip("<>")
    path = (
        []
        if raw_path.lower() in {"none", "-"}
        else [part.strip().lower() for part in raw_path.split(">") if part.strip()]
    )
    refs_raw = match.group(4).strip().strip("<>")
    refs = (
        []
        if refs_raw.lower() in {"none", "-"}
        else [part.strip().strip("<>") for part in refs_raw.split(",") if part.strip()]
    )
    return {
        "path": path,
        "retrieval": match.group(2).upper(),
        "manual": match.group(3).lower(),
        "references_loaded": refs,
    }


def observed_references(commands: list[str]) -> list[str]:
    """Return unique Retrieval references in actual command-observation order."""

    observed: list[str] = []
    seen: set[str] = set()
    for command in commands:
        normalized = str(command).replace("\\", "/")
        for match in RETRIEVAL_REF_RE.finditer(normalized):
            reference = match.group(0).lower().replace("\\", "/")
            if reference not in seen:
                seen.add(reference)
                observed.append(reference)
    return observed

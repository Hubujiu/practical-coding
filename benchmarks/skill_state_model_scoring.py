#!/usr/bin/env python3
"""General scoring helpers for execution-state model-gate results.

The helpers deliberately separate delivered-answer evidence from state-only
requirements.  Text evidence accepts harmless separator variation (for example,
``parser-transition`` versus ``parser transition``) without stemming, synonym
expansion, or case-specific aliases.  Immutable artifact integrity is required in
all arms, while the canonical-state history pointer is required only when an arm
actually owns a state object.
"""

from __future__ import annotations

import hashlib
import unicodedata
from pathlib import Path
from typing import Any, Mapping

SCORER_CONTRACT_VERSION = "2.0"


def normalize_evidence_text(value: str) -> str:
    """Return case-folded evidence text with separators normalized to one space.

    Letters and digits are preserved.  Punctuation, symbols, underscores, and
    whitespace are treated as equivalent separators.  This is intentionally less
    permissive than stemming or semantic matching: only surface separator
    variation is normalized.
    """

    if not isinstance(value, str):
        raise TypeError("evidence text must be a string")
    normalized = unicodedata.normalize("NFKC", value).casefold()
    parts: list[str] = []
    pending_separator = False
    for character in normalized:
        if character.isalnum():
            if pending_separator and parts:
                parts.append(" ")
            parts.append(character)
            pending_separator = False
        else:
            pending_separator = True
    return "".join(parts).strip()


def evidence_contains(haystack: str, needle: str) -> bool:
    """Match one normalized token phrase without prefix/stemming expansion."""

    if not isinstance(haystack, str) or not isinstance(needle, str):
        raise TypeError("evidence matching requires strings")
    normalized_needle = normalize_evidence_text(needle)
    normalized_haystack = normalize_evidence_text(haystack)
    if not normalized_needle:
        return False
    return f" {normalized_needle} " in f" {normalized_haystack} "


def score_answer(case: Any, answer: str) -> dict[str, Any]:
    """Score topology-neutral final-answer evidence for one frozen case."""

    if not isinstance(answer, str):
        raise TypeError("answer must be a string")
    missing = [
        list(group)
        for group in case.required_answer_groups
        if not any(evidence_contains(answer, term) for term in group)
    ]
    forbidden = [
        term
        for term in case.forbidden_answer_terms
        if evidence_contains(answer, term)
    ]
    return {
        "scorer_contract_version": SCORER_CONTRACT_VERSION,
        "answer_match_normalization": "NFKC+casefold+separator-equivalence",
        "answer_required_groups_missing": missing,
        "answer_forbidden_terms_present": forbidden,
        "answer_pass": not missing and not forbidden,
    }


def artifact_integrity(
    cell: Path,
    artifact: Mapping[str, Any] | None,
    state: Mapping[str, Any] | None,
) -> dict[str, Any]:
    """Validate immutable evidence and, only for state arms, its state pointer.

    Non-state comparison arms have no canonical ``state`` object.  They are still
    required to reference an existing artifact with the frozen digest in their
    answer, but they cannot satisfy or be failed by ``state.history`` fields that
    do not exist by design.
    """

    if artifact is None:
        return {
            "required": False,
            "artifact_pass": None,
            "state_pointer_required": False,
            "state_pointer_pass": None,
        }

    path = cell / str(artifact["path"])
    exists = path.is_file()
    observed_digest = hashlib.sha256(path.read_bytes()).hexdigest() if exists else None
    integrity_pass = bool(exists and observed_digest == artifact["sha256"])

    state_pointer_required = state is not None
    history_required: bool | None = None
    pointer_present: bool | None = None
    state_pointer_pass: bool | None = None
    if state_pointer_required:
        history_required = False
        pointer_present = False
        if isinstance(state, Mapping):
            history = state.get("history")
            if isinstance(history, Mapping):
                history_required = history.get("required") is True
                artifacts = history.get("artifacts")
                pointer_present = (
                    isinstance(artifacts, list)
                    and artifact["pointer"] in artifacts
                )
        state_pointer_pass = bool(history_required and pointer_present)

    artifact_pass = bool(
        integrity_pass
        and (state_pointer_pass is not False)
    )
    return {
        "required": True,
        "path": artifact["path"],
        "expected_sha256": artifact["sha256"],
        "observed_sha256": observed_digest,
        "exists": exists,
        "integrity_pass": integrity_pass,
        "state_pointer_required": state_pointer_required,
        "history_required": history_required,
        "pointer_present": pointer_present,
        "state_pointer_pass": state_pointer_pass,
        "artifact_pass": artifact_pass,
    }


__all__ = [
    "SCORER_CONTRACT_VERSION",
    "artifact_integrity",
    "evidence_contains",
    "normalize_evidence_text",
    "score_answer",
]

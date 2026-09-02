#!/usr/bin/env python3
"""Frozen long-horizon cases for the execution-state four-arm model gate.

The cases exercise state-retention mechanisms with a scripted observation stream.
They intentionally do not encode an automatic router node.  The ordinary tree
benchmark remains the authority for topology quality; this suite isolates whether
explicit state can replace replayed history without losing task-relevant facts.
"""

from __future__ import annotations

import argparse
import copy
import json
from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence

CASE_SCHEMA_VERSION = 1

STANDARD_PROFILE = "standard"
BOUNDED_PROFILE = "bounded"
SMOKE_PROFILE = "smoke"
PROFILES = (SMOKE_PROFILE, STANDARD_PROFILE, BOUNDED_PROFILE)

ARM_FULL_HISTORY = "full-history"
ARM_STATE_SHADOW = "state-shadow"
ARM_STATE_HISTORY_FREE = "state-history-free"
ARM_NO_SKILL_FULL_HISTORY = "no-skill-full-history"
ALL_ARMS = (
    ARM_FULL_HISTORY,
    ARM_STATE_SHADOW,
    ARM_STATE_HISTORY_FREE,
    ARM_NO_SKILL_FULL_HISTORY,
)
STATE_ARMS = frozenset({ARM_STATE_SHADOW, ARM_STATE_HISTORY_FREE})
HISTORY_FREE_ARMS = frozenset({ARM_STATE_HISTORY_FREE})

DEFAULT_ARMS_BY_PROFILE: Mapping[str, tuple[str, ...]] = {
    SMOKE_PROFILE: ALL_ARMS,
    STANDARD_PROFILE: ALL_ARMS,
    BOUNDED_PROFILE: (ARM_FULL_HISTORY, ARM_STATE_HISTORY_FREE),
}


@dataclass(frozen=True)
class StateCase:
    """One frozen observation schedule and topology-neutral delivered outcome."""

    case_id: str
    profile: str
    family: str
    repository: str
    repository_commit: str
    objective: str
    success: tuple[str, ...]
    observations: tuple[str, ...]
    required_answer_groups: tuple[tuple[str, ...], ...]
    forbidden_answer_terms: tuple[str, ...] = ()
    required_state_paths: tuple[tuple[str, Any], ...] = ()
    required_state_terms: tuple[str, ...] = ()
    forbidden_state_terms: tuple[str, ...] = ()
    history_required: bool = False
    artifact_payload: str | None = None
    horizon: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": CASE_SCHEMA_VERSION,
            "case_id": self.case_id,
            "profile": self.profile,
            "family": self.family,
            "repository": self.repository,
            "repository_commit": self.repository_commit,
            "objective": self.objective,
            "success": list(self.success),
            "observations": list(self.observations),
            "required_answer_groups": [list(group) for group in self.required_answer_groups],
            "forbidden_answer_terms": list(self.forbidden_answer_terms),
            "required_state_paths": [[path, value] for path, value in self.required_state_paths],
            "required_state_terms": list(self.required_state_terms),
            "forbidden_state_terms": list(self.forbidden_state_terms),
            "history_required": self.history_required,
            "artifact_payload": self.artifact_payload,
            "horizon": self.horizon,
        }


def _noise(label: str, count: int) -> tuple[str, ...]:
    return tuple(
        f"DISTRACTOR {label}-{index:02d}: detached worker cpu={(index * 17) % 100}%; "
        f"temporary cache key=noise-{index:02d}. This telemetry is unrelated to the task."
        for index in range(1, count + 1)
    )


def _standard_cases() -> tuple[StateCase, ...]:
    return (
        StateCase(
            case_id="delayed-release-identity",
            profile=STANDARD_PROFILE,
            family="delayed-dependency",
            repository="Hubujiu/practical-coding",
            repository_commit="ec9269d17abfc8c9e497a7fc69906e3df8ffe3b4",
            objective="Retain early release identity until the final verification handoff.",
            success=(
                "The final answer names the current branch and candidate commit.",
                "The final answer names the focused host test command.",
            ),
            observations=(
                "FACT: The candidate commit under review is d85c72cc5aa239da32352309e723ed1e6fc80429. "
                "For state arms, store it at facts.candidate_commit.",
                "FACT: The target branch is experiment/evolvable-router-tree. "
                "For state arms, store it at facts.branch.",
                *_noise("release", 4),
                "FACT: The focused non-model check is `python -m unittest tests.test_skill_state_host`. "
                "For state arms, store it at facts.focused_check.",
                "FINAL: Report the candidate commit, target branch, and focused check. Do not invent a benchmark result.",
            ),
            required_answer_groups=(
                ("d85c72cc5aa239da32352309e723ed1e6fc80429",),
                ("experiment/evolvable-router-tree",),
                ("python -m unittest tests.test_skill_state_host",),
            ),
            required_state_paths=(
                ("facts.candidate_commit", "d85c72cc5aa239da32352309e723ed1e6fc80429"),
                ("facts.branch", "experiment/evolvable-router-tree"),
                ("facts.focused_check", "python -m unittest tests.test_skill_state_host"),
            ),
            forbidden_state_terms=("detached worker", "temporary cache key"),
        ),
        StateCase(
            case_id="corrected-remote-head",
            profile=STANDARD_PROFILE,
            family="corrective-observation",
            repository="Hubujiu/practical-coding",
            repository_commit="ec9269d17abfc8c9e497a7fc69906e3df8ffe3b4",
            objective="Replace a stale remote-head fact immediately after an authoritative correction.",
            success=(
                "The final answer reports only the corrected remote head as current.",
                "The canonical current fact no longer points at the stale head.",
            ),
            observations=(
                "FACT: Initial observation says origin/experiment/evolvable-router-tree is at abc1230. "
                "For state arms, store the current value at facts.remote_head.",
                *_noise("remote", 2),
                "CORRECTION: A fresh `git fetch origin` proves the current remote head is def4560. "
                "The previous abc1230 value is stale. Replace facts.remote_head now; do not keep the stale value as current.",
                *_noise("remote-after-correction", 2),
                "FINAL: State the current remote head and explicitly say the earlier observation was superseded.",
            ),
            required_answer_groups=(("def4560",), ("superseded", "stale", "replaced", "更正", "失效")),
            forbidden_answer_terms=("current remote head is abc1230", "remote head: abc1230"),
            required_state_paths=(("facts.remote_head", "def4560"),),
        ),
        StateCase(
            case_id="noise-filtered-release-gate",
            profile=STANDARD_PROFILE,
            family="distractor-noise",
            repository="Hubujiu/practical-coding",
            repository_commit="ec9269d17abfc8c9e497a7fc69906e3df8ffe3b4",
            objective="Preserve one release-gate fact while excluding unrelated telemetry from canonical state.",
            success=(
                "The final answer reports the release quality gate and determinate cell count.",
                "Unrelated telemetry is not persisted as task state.",
            ),
            observations=(
                "FACT: The release_quality_gate is PASS. For state arms, store it at facts.release_quality_gate.",
                *_noise("telemetry", 6),
                "FACT: The completed tree run contains 252 determinate cells. "
                "For state arms, store it at facts.determinate_cells as the integer 252.",
                "FINAL: Report the release quality gate and determinate-cell count only; ignore the telemetry.",
            ),
            required_answer_groups=(("PASS", "pass"), ("252",)),
            required_state_paths=(
                ("facts.release_quality_gate", "PASS"),
                ("facts.determinate_cells", 252),
            ),
            forbidden_state_terms=("DISTRACTOR", "detached worker", "temporary cache key"),
        ),
        StateCase(
            case_id="rejected-cache-hypothesis",
            profile=STANDARD_PROFILE,
            family="repeated-hypothesis-pressure",
            repository="Hubujiu/personal-progress",
            repository_commit="515c2e2193c3d547e04e65687da6666dc877ab61",
            objective="Remember that a tempting hypothesis was rejected and avoid cycling back to it.",
            success=(
                "The final answer identifies the parser transition as the supported cause.",
                "The cache hypothesis is retained only as rejected evidence.",
            ),
            observations=(
                "HYPOTHESIS: h-cache says a stale cache leaves an operation RUNNING. "
                "For state arms, put h-cache in hypotheses.active.",
                "EVIDENCE: Cache invalidation completes before the failure and reproducing with cache disabled changes nothing.",
                "CORRECTION: Reject h-cache. Move it out of hypotheses.active and record it in hypotheses.rejected.",
                *_noise("hypothesis", 2),
                "EVIDENCE: The earliest incorrect transition is the exception path failing to complete the operation state. "
                "For state arms, record parser-transition as the supported active hypothesis.",
                "FINAL: Name the supported cause and the rejected hypothesis without reopening the rejected cause.",
            ),
            required_answer_groups=(
                ("exception path", "parser-transition", "complete the operation", "state transition"),
                ("cache",),
                ("rejected", "disproved", "排除", "否定"),
            ),
            required_state_terms=("h-cache", "parser-transition"),
        ),
        StateCase(
            case_id="coordinated-event-contract",
            profile=STANDARD_PROFILE,
            family="coordinated-implementation",
            repository="java-up-up/super-agent",
            repository_commit="d44edf063032a2d8797549411f11923aa4a83ec3",
            objective="Keep producer, consumer, invariant, and focused evidence synchronized across a long plan.",
            success=(
                "The final answer names the producer and consumer.",
                "The final answer states the v2 compatibility invariant and focused test.",
            ),
            observations=(
                "FACT: Producer symbol is EventPublisher. For state arms, store it at facts.contract.producer.",
                *_noise("contract-a", 2),
                "FACT: Consumer symbol is EventHandler. For state arms, store it at facts.contract.consumer.",
                "FACT: The target wire contract is v2, while v1 readers remain accepted for one release. "
                "For state arms, store the invariant at facts.contract.compatibility.",
                *_noise("contract-b", 2),
                "FACT: The cheapest focused evidence is EventContractTest. "
                "For state arms, store it at facts.contract.focused_test.",
                "FINAL: Give the coordinated change surface, compatibility invariant, and focused evidence.",
            ),
            required_answer_groups=(
                ("EventPublisher",),
                ("EventHandler",),
                ("v2",),
                ("v1", "one release", "compatib"),
                ("EventContractTest",),
            ),
            required_state_paths=(
                ("facts.contract.producer", "EventPublisher"),
                ("facts.contract.consumer", "EventHandler"),
                ("facts.contract.focused_test", "EventContractTest"),
            ),
        ),
        StateCase(
            case_id="history-required-audit-pointer",
            profile=STANDARD_PROFILE,
            family="history-required-control",
            repository="Hubujiu/practical-coding",
            repository_commit="ec9269d17abfc8c9e497a7fc69906e3df8ffe3b4",
            objective="Preserve an immutable evidence pointer when the task explicitly requires audit provenance.",
            success=(
                "The final answer reports the artifact path and digest.",
                "State arms set history.required and retain the exact immutable pointer.",
            ),
            observations=(
                "CONTROL: This is an audit/provenance task. For state arms, set history.required=true.",
                "ARTIFACT: The host created `{artifact_path}` with SHA-256 `{artifact_sha256}`. "
                "For state arms, add the exact pointer `{artifact_pointer}` to history.artifacts.",
                *_noise("audit", 3),
                "FINAL: Report the immutable artifact path and SHA-256. Do not replace it with a narrative transcript.",
            ),
            required_answer_groups=(("{artifact_path}",), ("{artifact_sha256}",)),
            required_state_paths=(("history.required", True),),
            required_state_terms=("{artifact_pointer}",),
            history_required=True,
            artifact_payload=(
                '{"case":"history-required-audit-pointer","event":"frozen-evidence",'
                '"candidate":"d85c72cc5aa239da32352309e723ed1e6fc80429"}\n'
            ),
        ),
    )


def _bounded_case(horizon: int) -> StateCase:
    if horizon < 4:
        raise ValueError("bounded horizon must be at least 4")
    ticket = f"HF-BOUND-{horizon}"
    observations: list[str] = [
        f"FACT: The stable ticket is {ticket}. For state arms, store it at facts.ticket.",
    ]
    correction_step = max(2, horizon // 2)
    for step in range(2, horizon):
        if step == correction_step:
            observations.append(
                "CORRECTION: current_generation is now 2 and supersedes generation 1. "
                "For state arms, set facts.current_generation to integer 2."
            )
        else:
            observations.append(
                f"DISTRACTOR bounded-{horizon}-{step:03d}: background shard={(step * 19) % 13}; "
                f"ephemeral marker=ignore-{step:03d}."
            )
    observations.append(
        f"FINAL: Report stable ticket {ticket} and current_generation 2. Ignore all bounded distractors."
    )
    return StateCase(
        case_id=f"bounded-horizon-{horizon}",
        profile=BOUNDED_PROFILE,
        family="bounded-context-horizon",
        repository="Hubujiu/practical-coding",
        repository_commit="ec9269d17abfc8c9e497a7fc69906e3df8ffe3b4",
        objective=f"Preserve a fixed state contract across {horizon} observations.",
        success=("The final answer retains the stable ticket and corrected generation.",),
        observations=tuple(observations),
        required_answer_groups=((ticket,), ("2", "generation 2")),
        required_state_paths=(("facts.ticket", ticket), ("facts.current_generation", 2)),
        forbidden_state_terms=("ephemeral marker", "DISTRACTOR bounded"),
        horizon=horizon,
    )


def all_cases() -> tuple[StateCase, ...]:
    return (*_standard_cases(), *(_bounded_case(h) for h in (10, 25, 50, 100)))


def cases_for_profile(profile: str) -> tuple[StateCase, ...]:
    if profile not in PROFILES:
        raise ValueError(f"unknown profile: {profile}")
    cases = all_cases()
    if profile == SMOKE_PROFILE:
        return tuple(case for case in cases if case.case_id in {"delayed-release-identity", "corrected-remote-head"})
    return tuple(case for case in cases if case.profile == profile)


def select_cases(profile: str, selected: Iterable[str] = ()) -> tuple[StateCase, ...]:
    available = cases_for_profile(profile)
    selected_set = {value for value in selected if value}
    if not selected_set:
        return available
    by_id = {case.case_id: case for case in available}
    unknown = selected_set - set(by_id)
    if unknown:
        raise ValueError(f"unknown cases for {profile}: {', '.join(sorted(unknown))}")
    return tuple(by_id[case_id] for case_id in sorted(selected_set))


def render_case(case: StateCase, replacements: Mapping[str, str] | None = None) -> StateCase:
    """Return an isolated case with host-generated artifact placeholders resolved."""

    mapping = dict(replacements or {})

    def render_text(value: str) -> str:
        rendered = value
        for key, replacement in mapping.items():
            rendered = rendered.replace("{" + key + "}", replacement)
        return rendered

    return StateCase(
        case_id=case.case_id,
        profile=case.profile,
        family=case.family,
        repository=case.repository,
        repository_commit=case.repository_commit,
        objective=render_text(case.objective),
        success=tuple(render_text(value) for value in case.success),
        observations=tuple(render_text(value) for value in case.observations),
        required_answer_groups=tuple(tuple(render_text(term) for term in group) for group in case.required_answer_groups),
        forbidden_answer_terms=tuple(render_text(term) for term in case.forbidden_answer_terms),
        required_state_paths=tuple((path, render_text(value) if isinstance(value, str) else copy.deepcopy(value)) for path, value in case.required_state_paths),
        required_state_terms=tuple(render_text(term) for term in case.required_state_terms),
        forbidden_state_terms=tuple(render_text(term) for term in case.forbidden_state_terms),
        history_required=case.history_required,
        artifact_payload=render_text(case.artifact_payload) if case.artifact_payload is not None else None,
        horizon=case.horizon,
    )


def validate_cases(cases: Sequence[StateCase] | None = None) -> None:
    selected = tuple(cases or all_cases())
    ids = [case.case_id for case in selected]
    if len(ids) != len(set(ids)):
        raise AssertionError("case IDs must be unique")
    for case in selected:
        if not case.observations or not case.observations[-1].startswith("FINAL:"):
            raise AssertionError(f"{case.case_id}: final observation must start with FINAL:")
        if not case.required_answer_groups:
            raise AssertionError(f"{case.case_id}: required answer groups are empty")
        if case.history_required and not case.artifact_payload:
            raise AssertionError(f"{case.case_id}: history-required case needs artifact payload")
        if case.profile == BOUNDED_PROFILE and case.horizon != len(case.observations):
            raise AssertionError(f"{case.case_id}: horizon does not match observation count")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", choices=PROFILES, default=STANDARD_PROFILE)
    parser.add_argument("--case", action="append", default=[])
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    validate_cases()
    if args.self_test:
        standard = cases_for_profile(STANDARD_PROFILE)
        bounded = cases_for_profile(BOUNDED_PROFILE)
        assert len(standard) == 6
        assert [case.horizon for case in bounded] == [10, 25, 50, 100]
        assert set(DEFAULT_ARMS_BY_PROFILE) == set(PROFILES)
        print("skill-state model cases: PASS")
        return 0
    selected = select_cases(args.profile, args.case)
    if args.json:
        print(json.dumps([case.to_dict() for case in selected], ensure_ascii=False, indent=2))
    else:
        for case in selected:
            print(f"{case.case_id}\t{case.family}\t{len(case.observations)} steps")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

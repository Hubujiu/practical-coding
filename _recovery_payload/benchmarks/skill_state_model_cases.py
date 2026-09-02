"""Frozen observation-stream cases for the execution-state four-arm model gate.

The cases exercise long-horizon state mechanisms without encoding an expected
router node. Every arm receives the same ordered observations for a case.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


STANDARD_HORIZONS = (8, 10, 12)
BOUNDED_HORIZONS = (10, 25, 50, 100)


@dataclass(frozen=True)
class StateModelCase:
    case_id: str
    family: str
    observations: tuple[str, ...]
    required_groups: tuple[tuple[str, ...], ...]
    forbidden_groups: tuple[tuple[str, ...], ...] = ()
    state_required_groups: tuple[tuple[str, ...], ...] = ()
    state_forbidden_groups: tuple[tuple[str, ...], ...] = ()
    history_required: bool = False

    @property
    def horizon(self) -> int:
        return len(self.observations)


def _finalize(observations: Iterable[str], instruction: str) -> tuple[str, ...]:
    rows = list(observations)
    if not rows:
        raise ValueError("a state-model case needs at least one observation")
    rows[-1] = rows[-1] + "\n\nFINAL STEP: " + instruction
    total = len(rows)
    return tuple(f"Step {index}/{total}. {value}" for index, value in enumerate(rows, 1))


def _noise(step: int) -> str:
    return (
        f"Unrelated telemetry: detached-worker-{step % 7} cpu={(step * 17) % 100}%; "
        f"cache-probe-{step % 5}=healthy. This is distractor data."
    )


def _standard_cases() -> tuple[StateModelCase, ...]:
    delayed = StateModelCase(
        case_id="delayed-dependency",
        family="delayed-dependency",
        observations=_finalize(
            (
                "Release invariant: public event schema_version must remain 3 until every consumer accepts version 4.",
                _noise(2),
                "Producer inventory is complete: api, worker, and retry publisher emit the event.",
                _noise(4),
                "Consumer inventory is complete: billing, analytics, and audit consume the event.",
                _noise(6),
                "Migration order is consumers first, then producers; rollback restores version-3 writes.",
                "The focused compatibility checks are producer_contract and consumer_compat.",
            ),
            "Report the safe migration order, retained version invariant, affected producers and consumers, rollback, and focused checks.",
        ),
        required_groups=(
            ("schema_version", "version 3", "version-3"),
            ("consumers first", "consumer-first"),
            ("api",),
            ("worker",),
            ("billing",),
            ("analytics",),
            ("rollback",),
            ("producer_contract",),
            ("consumer_compat",),
        ),
        state_required_groups=(("schema_version", "version 3"), ("consumers first", "consumer-first")),
    )

    corrective = StateModelCase(
        case_id="corrective-observation",
        family="corrective-observation",
        observations=_finalize(
            (
                "Remote release head is abc123; the pending check is release-abc123.",
                _noise(2),
                "The earlier remote-head observation is now stale: remote release head moved to def456.",
                "Do not run or cite release-abc123. The current focused check is release-def456.",
                _noise(5),
                "release-def456 passed on the current head.",
                "The release note must identify def456 as authoritative and abc123 as superseded.",
                "No other release check is required.",
            ),
            "Report the authoritative head, the passing current check, and the superseded stale value without treating it as current.",
        ),
        required_groups=(("def456",), ("release-def456",), ("abc123", "superseded", "stale")),
        forbidden_groups=(("abc123 is authoritative", "current head is abc123"), ("release-abc123 passed",)),
        state_required_groups=(("def456",), ("release-def456",)),
        state_forbidden_groups=(("\"remote_head\":\"abc123\"", "\"current_head\":\"abc123\""),),
    )

    distractor = StateModelCase(
        case_id="distractor-noise",
        family="distractor-noise",
        observations=_finalize(
            (
                "The target function is parse_bool in config.py; surrounding whitespace is the observed defect.",
                _noise(2),
                _noise(3),
                "FEATURE and AUDIT both call parse_bool and must preserve the same behavior.",
                _noise(5),
                _noise(6),
                "The smallest fix is to strip before lower-casing; focused evidence covers both callers.",
                "No detached-worker or cache telemetry is relevant to the code change.",
            ),
            "Report the shared root cause, smallest fix, affected callers, and focused evidence. Exclude telemetry from the conclusion.",
        ),
        required_groups=(("parse_bool",), ("strip", "whitespace"), ("FEATURE",), ("AUDIT",), ("focused", "test")),
        forbidden_groups=(("detached-worker",), ("cache-probe",)),
        state_forbidden_groups=(("detached-worker",), ("cache-probe",)),
    )

    hypotheses = StateModelCase(
        case_id="rejected-hypothesis",
        family="repeated-hypothesis-pressure",
        observations=_finalize(
            (
                "Symptom: cancelling export can still trigger download.",
                "Hypothesis h1: AbortController is not wired to the encoder.",
                "Evidence rejects h1: the signal reaches encodeAvif and abort is observed.",
                _noise(4),
                "Hypothesis h2: completion dispatch ignores signal.aborted after encode returns.",
                "Probe confirms h2 at exportCover immediately before download dispatch.",
                _noise(7),
                "The cheapest falsifying test cancels after encode resolution and asserts download is not called.",
            ),
            "Report the evidenced cause, the rejected hypothesis that must not be retried, the boundary, and the cheapest falsifying test.",
        ),
        required_groups=(("h1", "rejected"), ("h2",), ("signal.aborted",), ("exportCover",), ("download", "not called")),
        state_required_groups=(("h1", "rejected"), ("h2", "active", "confirmed")),
    )

    coordinated = StateModelCase(
        case_id="coordinated-implementation",
        family="coordinated-implementation",
        observations=_finalize(
            (
                "Change objective: add one-release alias new_status while preserving required public field status.",
                "Authoritative producer is PluginDispatchView.from; controller returns that view.",
                _noise(3),
                "Known consumers include old plugins reading status and new clients reading new_status.",
                "Serialization must emit both fields during the compatibility window.",
                "Removal requires telemetry showing no status reads for one documented release.",
                "Focused checks are PluginDispatchApiTest and PluginDispatchViewTest.",
                _noise(8),
                "Rollback removes new_status and leaves status unchanged.",
                "The implementation surface is view mapping, serialization contract, tests, and release documentation.",
            ),
            "Report the coordinated producer/consumer contract, compatibility window, removal signal, rollback, and focused checks.",
        ),
        required_groups=(
            ("PluginDispatchView",),
            ("status",),
            ("new_status",),
            ("one release", "one-release"),
            ("telemetry",),
            ("PluginDispatchApiTest",),
            ("PluginDispatchViewTest",),
            ("rollback",),
        ),
        state_required_groups=(("status",), ("new_status",), ("PluginDispatchView",)),
    )

    provenance = StateModelCase(
        case_id="history-required-provenance",
        family="history-required-control",
        observations=_finalize(
            (
                "This task requires an audit trail. The host artifact pointer is {{ARTIFACT_POINTER}}.",
                "The immutable artifact SHA-256 is {{ARTIFACT_SHA256}}.",
                _noise(3),
                "The audit artifact records the accepted release decision and exact source evidence.",
                "Do not copy the raw artifact into execution state; retain only its bounded pointer and digest.",
                _noise(6),
                "The final report must say history was required and name the immutable artifact pointer.",
                "No other provenance source is authoritative.",
            ),
            "Report why history is required and cite the immutable artifact pointer and digest.",
        ),
        required_groups=(("history", "audit", "provenance"), ("{{ARTIFACT_POINTER}}",), ("{{ARTIFACT_SHA256}}",)),
        state_required_groups=(("{{ARTIFACT_POINTER}}",), ("{{ARTIFACT_SHA256}}",), ("true", "required")),
        history_required=True,
    )
    return (delayed, corrective, distractor, hypotheses, coordinated, provenance)


def _bounded_case(horizon: int) -> StateModelCase:
    rows: list[str] = [
        "Bounded-context invariant: authoritative release train is amber and focused check is bounded-state-check."
    ]
    for step in range(2, horizon):
        rows.append(_noise(step))
    rows.append("The release train remains amber; bounded-state-check passed.")
    return StateModelCase(
        case_id=f"bounded-horizon-{horizon}",
        family="bounded-context",
        observations=_finalize(
            rows,
            "Report the authoritative release train and passing focused check.",
        ),
        required_groups=(("amber",), ("bounded-state-check",), ("pass", "passed")),
        forbidden_groups=(("detached-worker",), ("cache-probe",)),
        state_required_groups=(("amber",), ("bounded-state-check",)),
        state_forbidden_groups=(("detached-worker",), ("cache-probe",)),
    )


STANDARD_CASES = _standard_cases()
BOUNDED_CASES = tuple(_bounded_case(value) for value in BOUNDED_HORIZONS)
PROFILES = {"standard": STANDARD_CASES, "bounded": BOUNDED_CASES}


def cases_for_profile(profile: str, selected: Iterable[str] = ()) -> tuple[StateModelCase, ...]:
    if profile not in PROFILES:
        raise ValueError(f"unknown profile: {profile}")
    cases = PROFILES[profile]
    selected_ids = set(selected)
    unknown = selected_ids - {case.case_id for case in cases}
    if unknown:
        raise ValueError(f"unknown cases for {profile}: {', '.join(sorted(unknown))}")
    return tuple(case for case in cases if not selected_ids or case.case_id in selected_ids)


def replace_artifact_placeholders(case: StateModelCase, pointer: str, digest: str) -> StateModelCase:
    def replace(value: str) -> str:
        return value.replace("{{ARTIFACT_POINTER}}", pointer).replace("{{ARTIFACT_SHA256}}", digest)

    return StateModelCase(
        case_id=case.case_id,
        family=case.family,
        observations=tuple(replace(value) for value in case.observations),
        required_groups=tuple(tuple(replace(value) for value in group) for group in case.required_groups),
        forbidden_groups=tuple(tuple(replace(value) for value in group) for group in case.forbidden_groups),
        state_required_groups=tuple(tuple(replace(value) for value in group) for group in case.state_required_groups),
        state_forbidden_groups=tuple(tuple(replace(value) for value in group) for group in case.state_forbidden_groups),
        history_required=case.history_required,
    )


def self_test() -> None:
    assert {case.horizon for case in BOUNDED_CASES} == set(BOUNDED_HORIZONS)
    assert len({case.case_id for case in STANDARD_CASES}) == len(STANDARD_CASES)
    assert any(case.history_required for case in STANDARD_CASES)
    assert all("FINAL STEP:" in case.observations[-1] for case in STANDARD_CASES + BOUNDED_CASES)


if __name__ == "__main__":
    self_test()
    print("skill-state model cases: PASS")

---
name: practical-coding
description: "Use for implementing, fixing, refactoring, or reviewing code with the smallest correct change; routes only unresolved debugging, decision, or execution-boundary blockers, while retrieval expands independently."
license: MIT
metadata:
  author: Hubujiu
  version: "1.5"
---

# Practical Coding

Use the Core for every coding task. Load one reasoning reference only for a present unresolved event; expand retrieval independently.

Before the first diagnostic, decision-research, or change-mapping source command, apply the Event Router. If a condition matches, its reference is the next read. Otherwise stay Direct.

## Core

- Read the request and touched code; define the smallest observable success.
- Stop at the first rung that works: do nothing; reuse the nearest project primitive; standard library; platform feature; available dependency; one line; otherwise minimum local code.
- Reuse established APIs and established contracts. Build only behavior required by a current caller or requirement; nearby richness is not a requirement.
- Add no speculative options, wrappers, aliases, configuration, scaffolding, helper layers, or one-implementation interfaces.
- Make the smallest coherent reachable change. A standalone artifact needs no demo; a user-facing feature must be reachable. Preserve unrelated code and user changes.
- Prefer deletion. Remove each new dependency, file, option, wrapper, comment, fallback, retry, test, or document not required by behavior, project contract, or verification.
- Run the cheapest focused check once after the final edit. If no repository test exists, run one focused executable check, not a broad test runner. Prefer no-write check modes (for example Python `-B`). Never repeat an unchanged check or replace a required build gate with diff inspection. If disposable output remains, clean it once when safe; after a blocked or failed cleanup, stop and report it without another inspection or command. Install declared dependencies only as a bounded prerequisite in isolation; otherwise report the missing prerequisite.
- State only fresh evidence. Unless requested, finish with the outcome, changed surface, check, and remaining uncertainty—no process recap.

## Direct Path

When no Event Router condition matches, proceed with the Core alone. Targeted reads and searches are ordinary Direct work.

## Event Router

Route only a present unresolved blocker. Settled facts and choices are inputs, not events; risk or technology nouns do not route by themselves.

Use this first-match ladder:

1. An observed failure, regression, incorrect behavior, or failed check still lacks an evidenced cause: read `references/debugging.md`.
2. A material user-owned choice about architecture, dependency, implementation, API, data model, or compatibility remains unresolved and would change the next action: read `references/decision.md`.
3. Safe execution is blocked by an unknown contract or invariant; required producers and consumers must change together but their joint contract is unknown; a material security, irreversible-effect, persistence/migration, concurrency/transaction, or compatibility boundary remains unresolved; or evidence sufficient for a risky material claim is unknown: read `references/implementation.md`.

Read exactly that reference plus the Core. Resolve the blocker, then contract. Do not preload candidates. Reassess only for a different later blocker; handle a trivial one with the Core or isolate a substantial one when the saved context exceeds handoff cost.

Stay Direct when the cause, choice, governing boundary, affected surface, and sufficient check are already established. A named target with settled behavior remains Direct even when it concerns risk; a requested standalone artifact with no integration remains Direct. Unknown locations, file count, callers, consumers, and data flow are Retrieval questions, not Implementation events. Read-only source mapping is never an Implementation event. Choosing evidence sufficient to support a material risk or performance claim is an Implementation boundary, not a user-owned product Decision.

## Explicit-only requirements interview

Load `references/manual/clarification.md` only when the current instruction explicitly asks to be interviewed, grilled, or questioned before implementation. Ambiguity, importance, risk, or one unavoidable blocking question does not activate it. Decision resolves a genuinely open material choice; alternatives alone do not activate it.

## Retrieval Policy

Retrieval is orthogonal to execution. Stop at the first sufficient rung:

1. Read a known path or symbol directly. Do not inventory history, branches, or unrelated files, or search outside the project for an implementation unless the blocker or request requires it.
2. Otherwise use an available bounded/ranked source search, falling back to filename, text, or symbol search.
3. For unknown callers, dependencies, authoritative boundaries, or cross-file guarantees, prefer an available structural code index when it materially reduces exploration. Stay Bounded when known identifiers or a finite known consumer set can be located by text search; a known edit target alone is not Targeted when relationships are unknown.
4. For bounded exhaustive repository claims, use coverage-aware discovery and disclose gaps. For external contracts, use the smallest authoritative current source.
5. Fall back without installing retrieval tooling; verify material conclusions in current source. Use NONE when only user-owned policy is missing, and retrieve only facts needed to resolve it.

Routine lookup stays here; do not load `references/navigation.md`. Load it only for substantial broad structural mapping or bounded exhaustive discovery. Do not add Navigation beside a reasoning reference merely to search; use this policy or isolate the mapping when worthwhile.

## Isolation Gate

Direct work and one routed event in small context use no worker. Keep the root at Core plus one active reasoning reference.

When isolation saves more context than its handoff cost, dispatch one worker with `references/delegation.md` and one assigned reference. Navigation and Debugging workers are read-only. Decision is read-only unless the root authorizes settled implementation. Implementation writes only an assigned non-overlapping scope as sole writer. Never overlap writers or build worker pipelines.

## Evolution contract

Runtime agents do not read `evolution/`. Maintenance records benchmark and real-project receipts there, freezes experiments before changing runtime rules, and preserves rejected changes. Never add benchmark-specific nouns or keep a module for symmetry; each runtime module must earn quality-qualified net lift over its smaller parent.

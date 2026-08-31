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

- Read the request and touched code; define the smallest observable success before editing.
- Stop at the first rung that works: do nothing; reuse the nearest project primitive; use the standard library; use a native platform feature; use an available dependency; one line; otherwise write the minimum local code.
- Reuse established APIs and established contracts. Build only behavior required by a current caller or requirement; names, aesthetics, and rich siblings are not requirements.
- Add no speculative options, wrappers, aliases, configuration, scaffolding, helper layers, or one-implementation interfaces.
- Make the smallest coherent reachable change. A standalone artifact needs no demo unless requested; a user-facing feature must be reachable. Preserve unrelated code and user changes.
- Prefer deletion and boring code. Remove every new dependency, file, option, wrapper, comment, fallback, retry, test, or document not required by behavior, project contract, or the chosen check.
- Run the cheapest focused check once after the final edit. Do not repeat an unchanged check or replace a required compile/build gate with diff inspection. Install declared dependencies only as a bounded prerequisite in an isolated workspace; otherwise report the missing prerequisite.
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

1. Read a known path or symbol when current context identifies it.
2. Otherwise use an available bounded/ranked source search, falling back to filename, text, or symbol search.
3. For structural questions—callers, callees, imports, implementations, dependencies, authoritative boundaries, or cross-file guarantees—prefer an available structural code index when it materially reduces exploration. A known edit target does not make retrieval Targeted when those relationships are unknown.
4. For bounded exhaustive repository claims, use coverage-aware discovery and disclose gaps. For external contracts, use the smallest authoritative current source.
5. If a stronger capability is unavailable, fall back without installing or persisting retrieval tooling. Verify material conclusions against current source. Do not retrieve merely to decide an unresolved user-owned policy; retrieve only facts required to resolve it.

Routine lookup stays here; do not load `references/navigation.md`. Load it only for substantial broad structural mapping or bounded exhaustive discovery. Do not add Navigation beside a reasoning reference merely to search; use this policy or isolate the mapping when worthwhile.

## Isolation Gate

Direct work and one routed event in small context use no worker. Keep the root at Core plus one active reasoning reference.

When isolation clearly saves more context than its handoff costs, dispatch one worker with `references/delegation.md` and exactly one assigned reference. Navigation and Debugging workers are read-only. A Decision worker is read-only unless the root separately authorizes settled implementation. An Implementation worker writes only an explicitly assigned, non-overlapping scope as its sole writer. Never use overlapping writers or worker pipelines.

## Evolution contract

Runtime agents do not read `evolution/`. Maintenance records benchmark and real-project receipts there, freezes experiments before changing runtime rules, and preserves rejected changes. Never add benchmark-specific nouns or keep a module for symmetry; each runtime module must earn quality-qualified net lift over its smaller parent.

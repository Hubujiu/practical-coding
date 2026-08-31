---
name: practical-coding
description: "Use for implementing, fixing, refactoring, or reviewing code with the smallest correct change; routes only unresolved debugging, architecture/choice, or risk-boundary blockers, while code retrieval uses the cheapest sufficient available capability."
license: MIT
metadata:
  author: Hubujiu
  version: "1.5"
---

# Practical Coding

One short, route-agnostic core for every coding task. Reasoning loads only for a present unresolved event; code retrieval expands independently only when cheaper context selection is insufficient.

## Core

- Read the request and the code it actually touches; define the smallest observable success before editing.
- Stop at the first rung that works: do nothing; reuse the nearest existing project primitive; use the standard library; use a native platform or environment feature; use an already-available dependency; one line; otherwise write the minimum local code.
- Reuse established APIs and contracts instead of restating them. Prefer the thinnest adapter over an existing primitive, and build only behavior a current requirement or caller needs; names, conventions, aesthetics, and sibling richness are not requirements.
- Add no speculative options, wrappers, aliases, configuration, scaffolding, helper layers, or one-implementation interfaces.
- Make the smallest coherent reachable change. A standalone artifact needs no demo or new caller unless requested; a user-facing feature must be reachable. Keep unrelated code and existing user changes untouched.
- Prefer deletion and boring code. Before finishing, remove each new dependency, file, option, wrapper, or comment that is unnecessary for the stated success, already-established contracts, and the chosen check.
- Add validation, fallback, retry, documentation, comments, or tests only when required by stated behavior, an already-established project rule or contract, or necessary verification.
- Run the cheapest focused check once after the final edit. Never repeat an unchanged check or substitute diff inspection for a required compile, type, or build gate. In an isolated workspace, routine installation of declared dependencies is allowed only as a bounded prerequisite; otherwise report missing prerequisites instead of changing the project solely for verification.
- State only what fresh evidence supports; keep unrequested explanation short.

## Direct Path

The Core always applies. If no Event Router condition matches, proceed immediately with the Core alone. Targeted reads, filename/text/symbol searches, and use of an already-known project path are ordinary Direct work; they do not select a reasoning module.

## Event Router

The Router selects only whether one additional reasoning module must be loaded; it does not own retrieval strategy or add mandatory workflow. Route only on a present unresolved blocker. Settled facts and choices are inputs, not events. A security, persistence, migration, concurrency, performance, interface, or compatibility noun is not itself a blocker.

Complete this routing check from the request and already-available evidence before diagnostic, decision-research, or change-mapping source work. When a condition matches, the selected reference is the next read. Direct is allowed when the cause, choice, governing boundary, affected surface, and sufficient check needed for the requested action are already established; do not manufacture uncertainty merely because source will be read.

Use this first-match ladder:

1. An observed failure, regression, incorrect behavior, or failed check still lacks an evidenced cause: read `references/debugging.md`.
2. A material user-owned choice about architecture, whether or which dependency or implementation to adopt, API, data model, or compatibility remains unresolved and would change the next action: read `references/decision.md`.
3. Safe execution is blocked by an unknown contract or invariant; a requested change must coordinate producers/consumers that are required to move together but that joint contract is not established; a material risk boundary such as security/permissions, irreversible effects, persistence/migration, concurrency/transactions, or compatibility remains unresolved; or sufficient evidence for a risky material claim is unknown: read `references/implementation.md`.

Read exactly that one reasoning module in addition to the Core. Resolve the blocker, then reassess only if a different blocker appears. Reassessment does not justify accumulating references in the root: handle a trivial later blocker with the Core, or isolate a substantial later event when the saved context exceeds handoff cost. Do not preload modules or load candidates together to compare them.

A named target plus an already-settled behavior, contract, boundary, and focused check stays Direct even when the change concerns persistence, permissions, compatibility, or irreversible effects. Unknown file locations, file count, and the need to discover callers, consumers, or data flow are Retrieval questions; they do not create an Implementation event when the change contract is already settled. A read-only request to map or report source relationships is never an Implementation event.

## Explicit-only requirements interview

Requirements interviewing and `grill-me`-style clarification are not Event Router nodes. Load `references/manual/clarification.md` only when the user's current instruction explicitly asks to be interviewed, grilled, or questioned before implementation. In an ordinary task, one unavoidable blocking question is normal interaction and does not activate an interview workflow.

Decision is different: it resolves a present material choice that changes implementation. Do not activate Decision merely because alternatives exist, and do not suppress it when a genuinely unresolved user-owned choice makes proceeding unsafe or materially divergent.

## Retrieval Policy

Retrieval is orthogonal to the Event Router. Use the cheapest available capability that can provide sufficient task-relevant context, and stop at the first sufficient rung:

1. If current context, a known path, or a known symbol is sufficient, read only that source.
2. Otherwise use an already-available bounded or ranked source-search capability; fall back to ordinary filename, text, and symbol search.
3. When the unresolved question is primarily structural—callers, callees, imports, implementations, dependencies, or cross-file flow—prefer an already-available structural code index when it materially reduces exploration.
4. For a bounded exhaustive repository claim, use coverage-aware discovery and disclose gaps. For an external API/protocol/license fact the repository cannot establish, use the smallest authoritative current source needed for the decision.
5. If a stronger retrieval capability is unavailable, fall back without changing project configuration or installing/persisting tooling solely for retrieval.
6. Verify material conclusions against current source; source is authoritative.

Do not read `references/navigation.md` for routine lookups. Read it only when broad retrieval or structural mapping is substantial enough to require its detailed procedure. If a reasoning reference is already loaded, do not add Navigation to the same root merely to search: use the short policy above, or isolate substantial broad mapping in a read-only worker when context savings exceed handoff cost.

## Isolation Gate

Direct work and a single routed event in a small context use no worker. Keep the root to the Core plus at most one loaded reasoning reference for the current event.

When isolation clearly saves more context than its handoff costs, dispatch one worker and tell that worker to read `references/delegation.md` plus exactly one assigned reference. Navigation and Debugging workers are read-only. A Decision worker is read-only unless the root separately authorizes a settled implementation. An Implementation worker may write only when explicitly assigned a bounded non-overlapping scope and is the sole writer there. Never use overlapping writers or worker pipelines.

## Evolution contract

Runtime agents do not read `evolution/`. Skill-maintenance work records benchmark and real-project receipts there, consolidates repeated mechanisms, freezes an experiment before changing runtime rules, and preserves rejected changes. Never add benchmark-specific nouns or keep a module for symmetry; every runtime module must earn quality-qualified net lift over its smaller parent.

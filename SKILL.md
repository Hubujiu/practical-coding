---
name: practical-coding
description: "Use for implementing, fixing, refactoring, or reviewing code with the smallest correct change; routes only unresolved debugging, architecture/choice, or risk-boundary blockers, while code retrieval uses the cheapest sufficient available capability."
license: MIT
metadata:
  author: Hubujiu
  version: "1.2"
---

# Practical Coding

One short, route-agnostic core for every coding task. Reasoning escalates only for unresolved blockers; code retrieval escalates independently only when cheaper context selection is insufficient.

## Core

- Read the request and the code it actually touches; define the smallest observable success before editing.
- Stop at the first rung that works: do nothing; reuse the nearest existing project primitive; use the standard library; use a native platform or environment feature; use an already-available dependency; one line; otherwise write the minimum local code.
- Reuse established APIs and contracts instead of restating them. Prefer the thinnest adapter over an existing primitive, and build only behavior a current requirement or caller needs; names, conventions, aesthetics, and sibling richness are not requirements.
- Add no speculative options, wrappers, aliases, configuration, scaffolding, helper layers, or one-implementation interfaces.
- Make the smallest coherent reachable change. A standalone artifact needs no demo or new caller unless requested; a user-facing feature must be reachable. Keep unrelated code and existing user changes untouched.
- Prefer deletion and boring code. Before finishing, remove each new dependency, file, option, wrapper, or comment that is unnecessary for the stated success, already-established contracts, and the chosen check.
- Add validation, fallback, retry, documentation, comments, or tests only when required by stated behavior, an already-established project rule or contract, or necessary verification.
- Run the cheapest focused check once after the final edit. Never repeat an unchanged check or substitute diff inspection for a required compile, type, or build gate. In an isolated workspace, routine installation of declared dependencies is allowed only as a bounded prerequisite; otherwise report missing prerequisites instead of changing the project solely for verification. If the check creates unrelated generated churn, inspect at most one diff, then leave and report it.
- State only what fresh evidence supports; keep unrequested explanation short.

## Direct Path

The Core always applies. If no Event Router condition matches, proceed immediately with the Core alone. Targeted reads, filename/text/symbol searches, and use of an already-known project path are ordinary Direct work; they do not select a reasoning module.

## Event Router

The Router selects only whether one additional reasoning module must be loaded; it does not own retrieval strategy or add implementation rules. Route only on a present unresolved blocker. Settled facts and choices are inputs, not events. Use this first-match ladder:

1. An observed failure, regression, or incorrect behavior still lacks an evidenced cause: read `references/debugging.md`. A symptom or named failing function is not a diagnosed cause.
2. A material user-owned choice about architecture, whether or which external dependency or implementation to adopt, API, data model, or compatibility remains unresolved and would change the next action: read `references/decision.md`. A choice already specified and authorized by the user is settled input; research needed to resolve an open choice belongs inside Decision.
3. Safe execution requires mapping an unknown contract or invariant, a material risk boundary such as security/permissions, irreversible effects, persistence/migration, concurrency/transactions, or compatibility, or sufficient evidence for a risky material claim: read `references/implementation.md`.

Read exactly that one reasoning module in addition to the Core. Resolve the blocker, then route again only if a different blocker appears. Do not preload modules or load candidates together to compare them. Task nouns, file count, and the mere existence of an alternative library do not select a module.

## Retrieval Policy

Retrieval is orthogonal to the Event Router. Use the cheapest available capability that can provide sufficient task-relevant code context, and stop at the first sufficient rung:

1. If current context, a known path, or a known symbol is sufficient, read only that source.
2. Otherwise use an already-available bounded or ranked source-search capability; fall back to ordinary filename, text, and symbol search.
3. When the unresolved question is primarily structural — callers, callees, imports, implementations, dependencies, or cross-file flow — prefer an already-available structural code index when it materially reduces exploration.
4. If a stronger retrieval capability is unavailable, fall back without changing project configuration or installing/persisting tooling solely for retrieval.
5. Verify material conclusions against current source; source is authoritative.

Do not read `references/navigation.md` for routine lookups. Read it only when broad retrieval itself is substantial enough to require the detailed retrieval procedure. If a reasoning reference is already loaded, do not add Navigation to the same root context merely to search: use the short policy above, or isolate substantial broad mapping in a read-only worker when context savings exceed handoff cost.

## Isolation Gate

Direct work and a single routed event in a small context use no worker. The root never reads `references/delegation.md`. Prefer keeping the root to the Core plus at most one loaded reasoning reference; do not build a sequence of references that only accumulates context.

When isolation clearly saves more context than its handoff costs, dispatch one worker and tell that worker to read `references/delegation.md` plus exactly one assigned reference. Navigation workers are read-only. Decision and Debugging workers are read-only. An Implementation worker may write only when its assignment explicitly includes implementation, must have a bounded scope, and must be the sole writer there. Never use overlapping writers or worker pipelines.

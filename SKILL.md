---
name: practical-coding
description: "Use for implementing, fixing, refactoring, or reviewing code with the smallest correct change; routes only unresolved architecture, debugging, exploration, or risk-boundary blockers while ordinary well-specified work stays direct."
license: MIT
metadata:
  author: Hubujiu
  version: "1.3"
---

# Practical Coding

One short, route-agnostic core for every coding task, with optional modules loaded only for unresolved blockers.

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

If no Event Router condition matches, apply the Core immediately: read no reference and dispatch no worker.

## Event Router

The Router only selects whether one module must be loaded; it does not add implementation rules. Route only on a present unresolved blocker. Settled facts and choices are inputs, not events. Use this first-match ladder:

1. An observed failure, regression, or incorrect behavior still lacks an evidenced cause: read `references/debugging.md`. A symptom or named failing function is not a diagnosed cause.
2. A material user-owned choice about architecture, whether or which external dependency or implementation to adopt, API, data model, or compatibility remains unresolved and would change the next action: read `references/decision.md`. A choice already specified and authorized by the user is settled input; research needed to resolve an open choice belongs inside Decision.
3. Safe execution requires mapping an unknown contract or invariant, a material risk boundary such as security/permissions, irreversible effects, persistence/migration, concurrency/transactions, or compatibility, or sufficient evidence for a risky material claim: read `references/implementation.md`.
4. Broad structural mapping is itself necessary before another safe action is known: read `references/navigation.md`, which selects the configured backend.

Read exactly that one module. Resolve the blocker, then route again only if a different blocker appears. Do not preload modules or load candidates together to compare them. Task nouns, file count, and the mere existence of an alternative library do not select a module.

## Isolation Gate

Direct work and a single routed event in a small context use no worker. The root never reads `references/delegation.md`; when isolation clearly saves more context than its handoff costs, dispatch one worker and tell that worker to read it plus the one assigned module. Never use overlapping writers or worker pipelines.

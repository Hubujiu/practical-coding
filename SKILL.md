---
name: practical-coding
description: "Use for implementing, fixing, refactoring, or reviewing code with the smallest correct change; routes only unresolved architecture, debugging, exploration, or risk-boundary blockers while ordinary well-specified work stays direct."
license: MIT
metadata:
  author: Hubujiu
  version: "1.0"
---

# Practical Coding

One short core for every coding task, with optional modules only for unresolved blockers. Simple work does not enter a workflow.

## Core

- Read the request and the code it actually touches; define the smallest observable success before editing.
- Stop at the first rung that works: do nothing; reuse the nearest existing primitive; use the standard library; use a native platform feature; use an installed dependency; use one line; otherwise write the minimum custom code.
- Reuse current APIs as they are. When an artifact only specializes an existing primitive, make the thinnest adapter and inherit its contract; do not restate its styles, types, refs, events, or value semantics without a requirement.
- Build only behavior a current requirement or caller needs. Names and common conventions are not requirements; when the request is underspecified, preserve the platform representation and nearest existing contract instead of inventing a richer domain model.
- Add no speculative options, wrappers, aliases, configuration, scaffolding, or one-implementation interfaces.
- Make the smallest coherent reachable change. A standalone artifact needs no demo or new caller unless requested; a user-facing feature is incomplete until the existing application can reach it.
- Prefer deletion, boring code, repository defaults, and mature maintained implementations. Keep unrelated code and existing user changes untouched.
- Add validation, fallback, retry, documentation, comments, or tests only for a current contract, concrete boundary, observed risk, project rule, or necessary evidence.
- After the final edit, run the cheapest focused check once. Never repeat an unchanged check. If dependencies are absent, report that limitation instead of installing them solely to enable verification, unless installation is requested, part of the change, or needed for a high-risk claim.
- If a check creates unrelated generated churn, inspect at most one diff, then leave and report it. Never investigate its provenance or stage, restore, or rewrite unrelated files merely to clean status output.
- State only what fresh evidence supports; keep unrequested explanation short.

## Direct Path

When the next safe action is clear, apply the Core immediately: read no reference and dispatch no worker. A narrow lookup, reversible default, established project pattern, or known coherent multi-file edit remains Direct. File count and task nouns never select a module. A symptom or named failing function is not a cause; without prior evidence, read `references/debugging.md` before inspecting or editing.

## Event Router

Route only when a present unresolved event blocks the next safe action. If the request or repository already settles it, it is an input, not an event. Use this first-match ladder and stop at the first match:

1. An observed failure still lacks an evidenced cause: read `references/debugging.md`.
2. An open user-owned choice about architecture, dependency, API, data model, or compatibility would change the next action: read `references/decision.md`.
3. Safe execution requires mapping an unknown cross-boundary contract/invariant, or handling security, irreversible effects, persistence, concurrency, or compatibility risk: read `references/implementation.md`.
4. Broad structural navigation is necessary: read `references/navigation.md`, which selects the configured backend.

Read and apply exactly that one module before routing again. Never load candidates together to compare them; route again only if resolving the first event exposes a different blocker.

Do not preload modules. A named option, migration, dependency, or compatibility topic is not a Decision when its material policy is already fixed. Settled choices are inputs to Implementation or Direct execution. A reported symptom is not a diagnosed cause. Known coordinated edits are Direct; Implementation is not a mandatory stage.

Navigation needed to execute a risky change stays inside Implementation; use Navigation when the structural map itself is the current outcome or independently blocks another event.

## Isolation Gate

Direct work and a single routed event in a small context use no worker. The root never reads `references/delegation.md`; when isolation clearly saves more context than its handoff costs, dispatch one worker and tell that worker to read it plus the one assigned module. Never use overlapping writers or worker pipelines.

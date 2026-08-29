---
name: practical-coding
description: "Use for implementing, fixing, refactoring, or reviewing code with adaptive engineering rigor: start from the smallest Core, resolve blocking choices before execution, escalate only for an unexplained failure or unresolved material execution boundary, and retrieve only the minimum sufficient code context."
license: MIT
metadata:
  author: Hubujiu
  version: "1.3"
---

# Practical Coding

Use the smallest amount of engineering rigor and repository context that is sufficient for the current coding task. The Core always applies. Additional references are escalation profiles, not task categories or mandatory stages.

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

## Decision Gate

Before execution, ask one question:

> Does a material unresolved choice block or materially change the next safe action?

If no, continue immediately to Execution Escalation. If yes, read `references/decision.md` and resolve only that decision frontier.

A choice already settled by the request, repository, an authoritative constraint, or a cheap reversible default is input, not a Decision Gate. The existence of another library or implementation is not itself a blocker. Resolve discoverable facts before asking the user; ask only when a genuinely user-owned preference, compatibility policy, cost, scope, or risk tolerance still changes the next action.

When the choice is settled, return to the Core and reassess execution. Settling a Decision does not itself justify loading another reasoning reference in the same root context.

## Execution Escalation

Start Direct: use the Core alone and stop as soon as it is sufficient. Direct is the default execution state, not a route or module.

Escalate only for the blocker actually present:

- **Debugging rigor:** when an observed failure, regression, incorrect behavior, or failed check exists and its cause is not yet evidenced, read `references/debugging.md`.
- **Implementation rigor:** when safe execution is blocked by an unknown contract or invariant, an unresolved material risk boundary, or insufficient evidence for a risky material claim, read `references/implementation.md`. Material boundaries include security or permissions, irreversible effects, persistence or migration, concurrency or transactions, and compatibility.

These are not sequential stages. Do not pass through Debugging before Implementation, or Implementation after Debugging, unless a new blocker actually appears. A diagnosed bug can be fixed Direct. A risky-looking change stays Direct when its governing boundary, affected surface, and sufficient check are already established. File count, task nouns, and apparent code size are not escalation evidence.

If a loaded rigor profile resolves its blocker, continue with the Core. If a materially different blocker later requires another large reference, do not accumulate references in the root merely because the logical task continued; use the Isolation Gate when the saved context exceeds handoff cost.

## Retrieval Policy

Retrieval is independent from Decision and execution rigor. Use the cheapest available capability that can provide sufficient task-relevant code context, and stop at the first sufficient rung:

1. If current context, a known path, or a known symbol is sufficient, read only that source.
2. Otherwise use an already-available bounded or ranked source-search capability; fall back to ordinary filename, text, and symbol search.
3. When the unresolved question is primarily structural — callers, callees, imports, implementations, dependencies, or cross-file flow — prefer an already-available structural code index when it materially reduces exploration.
4. If a stronger retrieval capability is unavailable, fall back without changing project configuration or installing or persisting tooling solely for retrieval.
5. Verify material conclusions against current source; source is authoritative.

Retrieval levels are cost bounds, not semantic task classes. A slightly broader bounded search is acceptable when it remains cheap and avoids guessing; unnecessary structural exploration is not. Do not read `references/navigation.md` for routine lookups. Read it only when broad retrieval itself is substantial enough to require the detailed procedure. If another large reference is already resident, prefer the short policy above or isolate substantial broad mapping instead of adding Navigation to the same root context.

## Isolation Gate

Direct work and one small escalated blocker use no worker. The root never reads `references/delegation.md`. Keep the root to the Core plus at most one loaded reasoning reference at a time; textual instructions such as "return to Direct" do not remove already-loaded context.

When a later blocker or broad mapping task is substantial and isolation clearly saves more context than its handoff costs, dispatch one worker and tell that worker to read `references/delegation.md` plus exactly one assigned reference. Pass settled choices, verified facts, repository state, scope, and success conditions as a compact capsule rather than replaying prior reasoning.

Navigation workers are read-only. Decision and Debugging workers are read-only. An Implementation worker may write only when its assignment explicitly includes implementation, must have a bounded scope, and must be the sole writer there. Never use overlapping writers or worker pipelines.

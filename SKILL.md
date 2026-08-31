---
name: practical-coding
description: "Use for implementing, fixing, refactoring, or reviewing code with the smallest correct change; execution capabilities disclose through a local router tree while retrieval expands independently."
license: MIT
metadata:
  author: Hubujiu
  version: "1.6"
---

# Practical Coding

Use Core for every coding task. Core is the root of the automatic execution tree. A loaded node may disclose only its own immediate children; it must not know or select descendants owned by another node.

## Core

**Tree depth: 0**

- Read the request and touched code; define the smallest observable success.
- Stop at the first rung that works: do nothing; reuse the nearest project primitive; standard library; platform feature; available dependency; one line; otherwise minimum local code.
- Reuse established APIs and contracts. Build only behavior required by a current caller or requirement; nearby richness is not a requirement.
- When one established primitive owns shared behavior, repair it once instead of adding caller-specific branches or modes.
- Add no speculative options, wrappers, aliases, configuration, scaffolding, helper layers, or one-implementation interfaces.
- Make the smallest coherent reachable change. A standalone artifact needs no demo; a user-facing feature must be reachable. Preserve unrelated code and user changes.
- Prefer deletion. Remove each new dependency, file, option, wrapper, comment, fallback, retry, test, or document not required by behavior, project contract, or verification.
- Run the cheapest focused check once after the final edit. If no repository test exists, run one focused executable check, not a broad test runner. Prefer no-write check modes. Never repeat an unchanged check or replace a required build gate with diff inspection. Install declared dependencies only as a bounded prerequisite in isolation; otherwise report the missing prerequisite.
- State only fresh evidence. Unless requested, finish with the outcome, changed surface, check, and remaining uncertainty—no process recap.

## Root Router

Route only when Core cannot safely resolve the present blocker. These are the only automatic children known at depth 0:

1. An observed failure, regression, incorrect behavior, or failed check still lacks an evidenced cause: load `references/debugging.md`.
2. Safe execution is blocked by an unknown contract or invariant; required producers and consumers must change together but their joint contract is unknown; a material security, irreversible-effect, persistence/migration, concurrency/transaction, or compatibility boundary remains unresolved; or sufficient evidence for a risky material claim is unknown: load `references/implementation.md`.

Otherwise stay at Core. Unknown locations, callers, consumers, file count, or data flow are retrieval questions, not automatic execution children.

A routed node owns its next decision. Do not return to Core merely to discover a descendant. Do not preload siblings or descendants. If a node declares itself a leaf, resolve there unless the task becomes a genuinely different top-level blocker.

## Convergence Rule

Automatic routing may deepen execution only to resolve a current blocker. It must not reopen deliberation.

- Do not automatically load Decision from Core or from any execution node.
- When implementation exposes an ordinary technical choice, reuse the established project convention or choose the smallest sufficient reversible option and continue.
- When a genuinely user-owned choice blocks progress and no safe default exists, ask only the minimum blocking question in the current context. Do not activate the Decision workflow unless the user explicitly requested decision analysis.
- A failed check of the current candidate stays inside the active node when its cause is the candidate itself; correct it there instead of opening a fresh routing cycle.

## Manual Modes

Manual modes are outside the automatic execution tree and never appear in an automatic capability path.

- Load `references/manual/decision.md` only when the current user explicitly asks to compare options, make a technical choice, recommend an architecture/dependency/API/data-model approach, or otherwise perform decision analysis.
- Load `references/manual/clarification.md` only when the current user explicitly asks to be interviewed, grilled, questioned, or to clarify requirements before implementation.
- A manual mode must not automatically route to another manual mode or into an automatic descendant. After the requested manual work is resolved, return to Core with the settled result as input.

## Retrieval Policy

Retrieval is orthogonal to the execution tree. Expand only because current evidence is insufficient, not because execution depth increased.

1. Read a known path or symbol directly.
2. Otherwise use an available bounded or ranked source search, falling back to filename, text, or symbol search.
3. For unknown callers, dependencies, authoritative boundaries, or cross-file guarantees, prefer an available structural code index when it materially reduces exploration.
4. For bounded exhaustive repository claims, use coverage-aware discovery and disclose gaps. For external contracts, use the smallest authoritative current source.
5. Fall back without installing retrieval tooling; verify material conclusions in current source.

Routine lookup stays here. Load `references/navigation.md` only for substantial broad structural mapping or bounded exhaustive discovery. Retrieval does not become an execution-tree node merely because a reasoning node needs source evidence.

## Isolation Gate

Core and one small routed node use no worker. Use `references/delegation.md` only when isolation saves more context than the handoff costs. Navigation and Debugging workers are read-only. Implementation writes only an assigned non-overlapping scope as sole writer. Manual Decision is read-only unless the user separately authorizes implementation. Never overlap writers or build worker pipelines.

## Evolution Contract

Runtime agents do not read `evolution/`. The tree is not a fixed taxonomy.

- Every runtime node owns its behavior, current depth, and only its immediate-child router; a leaf says so explicitly.
- Add a child only when a repeatable pre-load signal exists and parent-versus-child ablation shows quality-qualified net lift across multiple tasks or repositories.
- Merge siblings when their boundary is persistently ambiguous and separation adds no net value.
- Promote a child into its parent when the child is needed for most parent tasks.
- Remove a child that does not independently improve qualified outcomes enough to justify context and routing cost.
- Split or deepen a node only when failures form a stable, observable task cluster that a narrower capability fixes.
- Benchmark evidence may change node names, boundaries, branching factor, or depth. Do not preserve symmetry, numeric levels, or historical route labels for compatibility.

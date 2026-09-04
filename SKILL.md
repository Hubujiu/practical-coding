---
name: practical-coding
description: "Use for implementing, fixing, refactoring, reviewing, or explaining code with the smallest correct change; execution and retrieval disclose through separate local trees while host capabilities remain replaceable infrastructure."
license: MIT
metadata:
  author: Hubujiu
  version: "2.0"
---

# Practical Coding

Use Core for every coding task. Core is the root of the automatic execution tree. Retrieval is a separate progressive tree that expands only when current source evidence is insufficient. Host tools are capabilities beneath those policies, not routing nodes.

A loaded node may disclose only its own immediate children. It must not know or select descendants owned by another node.

## Core

**Execution tree depth: 0**

- Read the request and touched code; define the smallest observable success.
- Stop at the first rung that works: do nothing; reuse the nearest project primitive; standard library; platform feature; available dependency; one line; otherwise minimum local code.
- Reuse established APIs and contracts. Build only behavior required by a current caller or requirement; nearby richness is not a requirement.
- When one established primitive owns shared behavior, repair it once instead of adding caller-specific branches or modes.
- Add no speculative options, wrappers, aliases, configuration, scaffolding, helper layers, or one-implementation interfaces.
- Make the smallest coherent reachable change. A standalone artifact needs no demo; a user-facing feature must be reachable. Preserve unrelated code and user changes.
- Prefer deletion. Remove each new dependency, file, option, wrapper, comment, fallback, retry, test, or document not required by behavior, project contract, or verification.
- Run the cheapest focused check once after the final edit. If no repository test exists, run one focused executable check, not a broad test runner. Prefer no-write check modes. Never repeat an unchanged check or replace a required build gate with diff inspection. Install declared project dependencies only as a bounded prerequisite in isolation; otherwise report the missing prerequisite.
- State only fresh evidence. Unless requested, finish with the outcome, changed surface, check, and remaining uncertainty—no process recap.

## Root Router

Route only when Core cannot safely resolve the present execution blocker. These are the only automatic execution children known at depth 0:

1. An observed failure, regression, incorrect behavior, or failed check still lacks an evidenced cause: load `references/debugging.md`.
2. Safe execution is blocked by an unknown contract or invariant; required producers and consumers must change together but their joint contract is unknown; a material security, irreversible-effect, persistence/migration, concurrency/transaction, or compatibility boundary remains unresolved; or sufficient evidence for a risky material claim is unknown: load `references/implementation.md`.

Otherwise stay at Core. Unknown locations, callers, consumers, file count, or data flow are retrieval questions, not automatic execution children.

A routed node owns its next decision. Do not return to Core merely to discover a descendant. Do not preload siblings or descendants. If a node declares itself a leaf, resolve there unless the task becomes a genuinely different top-level blocker.

## Convergence Rule

Automatic execution routing may deepen only to resolve a current blocker. It must not reopen deliberation.

- Do not automatically load Decision from Core or from any execution node.
- When implementation exposes an ordinary technical choice, reuse the established project convention or choose the smallest sufficient reversible option and continue.
- When a genuinely user-owned choice blocks progress and no safe default exists, ask only the minimum blocking question in the current context. Do not activate the Decision workflow unless the user explicitly requested decision analysis.
- A failed check of the current candidate stays inside the active node when its cause is the candidate itself; correct it there instead of opening a fresh routing cycle.

## Manual Modes

Manual modes are outside both automatic trees and never appear in an automatic capability path.

- Load `references/manual/decision.md` only when the current user explicitly asks to compare options, make a technical choice, recommend an architecture/dependency/API/data-model approach, or otherwise perform decision analysis.
- Load `references/manual/clarification.md` only when the current user explicitly asks to be interviewed, grilled, questioned, or to clarify requirements before implementation.
- A manual mode must not automatically route to another manual mode or into an automatic descendant. After the requested manual work is resolved, return to Core with the settled result as input.

## Retrieval Policy

Retrieval is orthogonal to execution. Its depth represents the unresolved information problem, not the strength or brand of an available tool.

When source evidence is needed, load `references/retrieval/SKILL.md`. Core knows only the Retrieval root; it does not know or select that root's descendants. Every retrieval node owns only its immediate child decision and returns as soon as the minimum evidence needed for the current claim has been established.

Do not choose a retrieval depth from Core in one global decision. Do not route by tool name. Do not preload deeper retrieval modules or copy the full benchmark topology into a runtime node.

Runtime retrieval uses the strongest already-available capability appropriate to the current node and falls back losslessly to bounded repository-native search. Material conclusions must be verified in current source. A benchmark profile may deliberately require concrete providers; that requirement belongs to the benchmark environment, not to the runtime tree.

Once candidate paths or symbols are known, stop inventory and switch to bounded line ranges or symbol reads; do not dump whole files or repeat broad discovery. Batch independent bounded reads only when each source is required by a current claim.

Use a structural code index only at R3, when the unresolved answer is a call, dependency, ownership, control/data-flow, or impact relationship. Provider output proposes evidence; current source establishes it.

## Navigation Boundary

Load `references/navigation.md` only when the unresolved question is which bounded repository area should be searched. Navigation returns a small topology map; it does not perform semantic evidence discovery, choose a search provider, or tour the repository.

After the area is bounded, use the Retrieval tree to identify the concrete evidence. If the target is already known, skip Navigation, load the Retrieval root, and let that root start at R0.

## Execution Output Layer

Shell, test, build, and Git output may pass through an already-configured output-compaction layer. This is cross-cutting infrastructure, not Navigation, Retrieval, Verification, or execution depth. A host adapter should make it transparent when the host supports command hooks; otherwise expose only the thinnest wrapper instruction needed to use it.

Compaction must preserve command semantics, exit status, failures, and enough evidence to verify the material claim. Never change the requested check merely to obtain shorter output. If compact output omits evidence needed for diagnosis, retrieve that bounded evidence without disabling compaction globally.

## Isolation Gate

Core and one small routed node use no worker. Use `references/delegation.md` only when isolation saves more context than the handoff costs. Navigation and Debugging workers are read-only. Implementation writes only an assigned non-overlapping scope as sole writer. Manual Decision is read-only unless the user separately authorizes implementation. Never overlap writers or build worker pipelines.

## Evolution Contract

Runtime agents do not read `evolution/`. Neither tree is a fixed taxonomy.

- Every runtime node owns its behavior, current depth, and only its immediate-child router; a leaf says so explicitly.
- Retrieval policy, capability providers, output transport, and maintenance workflows remain separate concerns. A provider must not become a tree node merely to expose a tool.
- On an `experiment/*` branch, a proposed child may be staged only to collect controlled parent-versus-child and adaptive-routing evidence. Staging is not promotion.
- Promote a staged child into a release topology only when a repeatable pre-load signal exists and parent-versus-child ablation shows quality-qualified net lift across multiple tasks or repositories.
- Merge siblings when their boundary is persistently ambiguous and separation adds no net value.
- Promote a child into its parent when the child is needed for most parent tasks.
- Remove a child that does not independently improve qualified outcomes enough to justify context and routing cost.
- Split or deepen a node only when failures form a stable, observable task cluster that a narrower capability fixes.
- Benchmark evidence may change node names, boundaries, branching factor, or depth. Do not preserve symmetry, numeric levels, or historical route labels for compatibility.

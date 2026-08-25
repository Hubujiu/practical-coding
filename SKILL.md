---
name: practical-coding
description: "Use for general coding work: implementing, modifying, or refactoring code, fixing bugs, regressions, or failed checks, choosing architectures, dependencies, APIs, or data models, reviewing changes, deciding how to verify work, and navigating large or structurally complex codebases. Also use when a task risks over-engineering, speculative abstraction, defensive bloat, unnecessary tests or documentation, or wasteful repeated exploration, or when the user asks for a lazier (low) or more thorough (high) mode."
argument-hint: "[low|smart|high]"
license: MIT
metadata:
  author: Hubujiu
  version: "2.0"
---

# Practical Coding

One coding skill: a lazy-by-default always-on core, three routing intensities, and independently loadable modules for events that genuinely block the next safe action. The best code is the code never written; the router does not replace ordinary coding judgment.

## Always-on Core

These rules apply on every path and in every mode:

- Read first, then be lazy. Understand the requested outcome and the code it actually touches, and turn them into a small acceptance set before editing. A familiar feature name implies only its named behavior, not every conventional extra.
- Stop at the first rung that holds: this does not need to exist at all; something in this codebase already does it (one narrow lookup for the nearest implementation and one likely shared primitive, then stop); the standard library does it; a native platform feature covers it — a native control over a widget library, CSS over JS, a framework prop over refs, effects, mirrored state, or custom event machinery; an already-installed dependency solves it; it fits in one line; only then the minimum custom code that works.
- Reuse an existing primitive through its current API. Do not copy or modify its implementation, translate its value types, or add convenience options without a pre-existing current caller that needs them, and do not create a caller merely to justify extra API or behavior.
- Build only behavior a current requirement or caller needs: no unrequested abstractions, optional modes, generic configuration, aliases, wrappers, scaffolding "for later", or interface with one implementation.
- Include the minimum wiring that makes the requested behavior reachable. A request to add or create a named component, helper, or library artifact is an artifact request: no demo, mount, registration, or new caller unless requested or required by an existing repository contract. A user-facing feature, endpoint, command, or integration is incomplete until the existing application can reach it. When a reversible, low-risk detail is unspecified, follow the repository's existing or platform default instead of expanding the API or blocking delivery.
- Deletion over addition; boring over clever; fewest files; the shortest working diff wins once the problem is understood. Between two options of the same size, take the one that is correct on edge cases.
- Validation, fallback, retry, documentation, or a test must trace to an actual trust boundary, project policy, observed risk, or the cheapest evidence this change needs. Never simplify away validation at a trust boundary, error handling that prevents data loss, or anything explicitly requested.
- For non-trivial capabilities, prefer integrating a mature maintained implementation over building a parallel one.
- Keep unrelated code and existing user changes untouched. Mark a deliberate simplification that cuts a real corner with a one-line comment naming the ceiling and the upgrade path.
- Before claiming completion, obtain the cheapest fresh evidence sufficient for the change; prefer one existing focused check and do not grow a redundant test suite. Deliver the change first, then at most three short lines of unrequested prose: what was skipped and when to add it. Explanation the user explicitly asked for is not debt.

## Modes

The default mode is smart. Switch only when the user names one ("low", "lazy mode", "high", "be thorough") or `.practical-coding.yaml` sets `mode:`. These levels are routing intensity, not a second copy of Ponytail's lite/full/ultra code intensity: the core above never relaxes in low and never grows extra standing duties in high.

| Mode | Routing | Delegation |
|---|---|---|
| **low** | Stay on Direct Path unless proceeding blind risks a wrong or irreversible result: an undiagnosed failure still loads Debugging; a material user-owned choice still loads Decision; an unmapped large codebase still loads Exploration (or Codebase Memory when enabled). Implementation is not loaded — wiring and evidence follow core defaults. | Never dispatch workers. |
| **smart** | The Direct Path rule and Event Router below, as written. | The Isolation Gate below. |
| **high** | Load the matching module for every triggered event, even a partially resolved one; map the change surface before multi-file edits and state an explicit evidence plan before the completion claim. | Prefer isolated workers for separable scopes. |

## Direct Path

Direct Path is the default. When no unresolved event below blocks the next action, read no reference and dispatch no worker; apply the core and proceed. Ordinary narrow source lookup, a reversible repository/platform default, and a known coherent multi-file edit remain Direct Path. Creating a named artifact beside existing primitives, without changing their contracts or adding callers, is Direct Path, not Implementation. Following an already-established repository or platform default is Direct Path, not Decision.

A reported symptom or named failing function is not a diagnosed cause. When a failure's earliest incorrect state is not already established by evidence, Direct Path does not apply: load `references/debugging.md` before editing.

## Event Router

Otherwise load only the module for the unresolved event that blocks the next safe action. Resolve it, then route again; task nouns and file counts do not select modules.

| Unresolved event | Read |
|---|---|
| a material choice about architecture, dependencies, APIs, data models, compatibility, or multiple plausible implementations remains unresolved | `references/decision.md` |
| understanding the task requires broad navigation of a large or structurally complex codebase | `references/exploration.md`, or `references/codebase-memory.md` only when the project explicitly enables it |
| an observed failure, regression, or failed check still lacks a diagnosed cause | `references/debugging.md` |
| a change must coordinate multiple files, contracts, or invariants and the change surface is unclear, or the sufficient evidence for a risky change is itself unresolved | `references/implementation.md` |

Do not preload modules. Missing or false configuration means Codebase Memory is off.

When events overlap, diagnose an unexplained failure first; otherwise resolve a material user-owned Decision before mapping or implementing its dependent surface. Use Exploration only when broad navigation is still needed, and Implementation only when a coordinated contract surface or the sufficient evidence for a change is still unclear. Choosing how to verify a change is Implementation, not Decision.

## Isolation Gate

Prefer one isolated worker when the context it avoids, or the parallel work it unblocks, clearly exceeds startup and handoff cost. Use multiple workers only for genuinely independent, non-overlapping scopes when parallelism clearly outweighs coordination cost. Each worker reads `references/delegation.md` plus its one assigned module; the root retains user intent, repository state, integration, and the final completion claim, and does not duplicate worker scope. No overlapping writers or worker pipelines.

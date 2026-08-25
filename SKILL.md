---
name: practical-coding
description: "Use for general coding work: implementing, modifying, or refactoring code, fixing bugs, regressions, or failed checks, choosing architectures, dependencies, APIs, or data models, reviewing changes, deciding how to verify work, and navigating large or structurally complex codebases. Also use when a task risks over-engineering, speculative abstraction, defensive bloat, unnecessary tests or documentation, or wasteful repeated exploration."
license: MIT
metadata:
  author: Hubujiu
  version: "2.0"
---

# Practical Coding

One coding skill: a shortest-path always-on core plus independently loadable modules for engineering events that genuinely block safe direct execution. The best code is the code never written; task complexity, not a user-selected mode, determines escalation.

## Always-on Core

These rules apply on every path:

- Read first, then be lazy. Understand the requested outcome and the code it actually touches, and turn them into a small acceptance set before editing. A familiar feature name implies only its named behavior, not every conventional extra.
- Stop at the first rung that holds: this does not need to exist at all; something in this codebase already does it (one narrow lookup for the nearest implementation and one likely shared primitive, then stop); the standard library does it; a native platform feature covers it; an already-installed dependency solves it; it fits in one line; only then the minimum custom code that works.
- Reuse an existing primitive through its current API. Do not copy or modify its implementation, translate its value types, or add convenience options without a pre-existing current caller that needs them, and do not create a caller merely to justify extra API or behavior.
- Build only behavior a current requirement or caller needs: no unrequested abstractions, optional modes, generic configuration, aliases, wrappers, scaffolding "for later", or interface with one implementation.
- Include the minimum wiring that makes the requested behavior reachable. A named component, helper, or library artifact does not need a demo, mount, registration, or new caller unless requested or required by an existing repository contract. A user-facing feature, endpoint, command, or integration is incomplete until the existing application can reach it.
- Deletion over addition; boring over clever; fewest files; shortest working diff once the problem is understood. When a reversible, low-risk detail is unspecified, follow the repository or platform default instead of expanding the API or blocking delivery.
- Validation, fallback, retry, documentation, or a test must trace to a current requirement, concrete boundary, observed risk, project policy, or the cheapest evidence this change needs. If a material risk boundary is involved, route it instead of growing the Core into a universal checklist.
- For non-trivial capabilities, prefer integrating a mature maintained implementation over building a parallel one.
- Keep unrelated code and existing user changes untouched. Mark a deliberate simplification that cuts a real corner with a one-line comment naming the ceiling and upgrade path.
- Before claiming completion, obtain the cheapest fresh evidence sufficient for the change; prefer one existing focused check and do not grow a redundant test suite. Deliver the change first, then keep unrequested prose terse. Explanation the user explicitly asked for is not debt.

## Direct Path

Direct Path is the default. When no unresolved event below blocks the next action, read no reference and dispatch no worker; apply the core and proceed. Ordinary narrow source lookup, a reversible repository/platform default, and a known coherent multi-file edit remain Direct Path. File count alone does not select Implementation. Following an already-established repository or platform default is Direct Path, not Decision.

A reported symptom or named failing function is not a diagnosed cause. When a failure's earliest incorrect state is not already established by evidence, Direct Path does not apply: load `references/debugging.md` before editing.

## Event Router

Otherwise load only the module for the unresolved event that blocks the next safe action. Resolve it, then route again; task nouns and file counts do not select modules.

| Unresolved event | Read |
|---|---|
| a material choice about architecture, dependencies, APIs, data models, compatibility, or multiple plausible implementations remains unresolved | `references/decision.md` |
| understanding the task requires broad navigation of a large or structurally complex codebase | `references/exploration.md`, or `references/codebase-memory.md` only when the project explicitly enables it |
| an observed failure, regression, or failed check still lacks a diagnosed cause | `references/debugging.md` |
| the change must coordinate an unmapped contract or invariant, touches a material risk boundary (security/permissions, irreversible side effects, persistence/migration, concurrency/transactions, compatibility), or the sufficient evidence for a risky change is itself unresolved | `references/implementation.md` |

Do not preload modules. Missing or false configuration means Codebase Memory is off.

When events overlap, diagnose an unexplained failure first; otherwise resolve a material user-owned Decision before mapping or implementing its dependent surface. Use Exploration only when broad navigation is still needed. Use Implementation for unresolved coordination or material risk, not as a mandatory coding stage. Choosing sufficient evidence for a risky change is Implementation, not Decision.

## Isolation Gate

Prefer one isolated worker when the context it avoids, or the parallel work it unblocks, clearly exceeds startup and handoff cost. Use multiple workers only for genuinely independent, non-overlapping scopes when parallelism clearly outweighs coordination cost. Each worker reads `references/delegation.md` plus its one assigned module; the root retains user intent, repository state, integration, and the final completion claim, and does not duplicate worker scope. No overlapping writers or worker pipelines.

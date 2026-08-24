---
name: practical-coding
description: "Use for general coding work: implementing, modifying, or refactoring code, fixing bugs, regressions, or failed checks, choosing architectures, dependencies, APIs, or data models, reviewing changes, deciding how to verify work, and navigating large or structurally complex codebases. Also use when a task risks over-engineering, speculative abstraction, defensive bloat, unnecessary tests or documentation, or wasteful repeated exploration."
license: MIT
metadata:
  author: Hubujiu
  version: "1.10"
---

# Practical Coding

One coding skill: a small always-on core plus independently loadable modules. Start with a narrow inspection and expand only when routing evidence is insufficient; this router does not replace ordinary coding judgment.

## Always-on Core

These rules apply on every path, including work that loads no module:

- Turn the requested outcome and current repository contract into a small acceptance set before editing. A familiar feature name implies only its named behavior, not every conventional extra.
- Deliver the smallest complete, usable change. Before creating a helper or component, use one narrow lookup for the nearest implementation and one likely shared primitive, then stop once the fit is clear. Prefer, in order: reuse or composition; the standard library or a native platform feature; an already-installed dependency; only then the minimum custom code.
- Reuse an existing primitive through its current API when composition is enough. Do not copy its implementation, modify it, translate its value types, or add convenience options without a pre-existing current caller that needs them. Do not create a caller merely to justify extra API or behavior.
- Prefer native or declarative behavior already available through an element, framework, or component prop over refs, effects, mirrored state, manual synchronization, or custom event machinery.
- Build only behavior a current requirement or caller needs. Do not add optional modes, generic configuration, extensibility, aliases, wrappers, or scaffolding for hypothetical reuse.
- Include the minimum wiring that makes the requested behavior reachable. Treat a request to add or create a named component, helper, or library artifact as an artifact request: do not add a demo, mount, registration, or new caller unless requested or required by an existing repository contract. A user-facing feature, endpoint, command, or integration is incomplete until the existing application can reach it. When a reversible, low-risk detail is unspecified, follow the repository's existing or platform default instead of expanding the API or blocking delivery.
- Everything else you add — validation, fallback, retry, documentation, or a test — must trace to an actual boundary, project policy, observed risk, or the cheapest evidence needed for this change.
- Non-trivial new logic — a branch, loop, parser, state transition, or money/security path — ships with exactly one smallest runnable check unless an existing focused test already covers it or the user forbids tests. Trivial native wiring needs none.
- For non-trivial capabilities, prefer integrating a mature maintained implementation over building a parallel one.
- Preserve required security, permissions, data integrity, accessibility, compatibility, and explicit project constraints.
- Keep unrelated code and existing user changes untouched.
- Before claiming completion, obtain the cheapest fresh evidence sufficient for the change. Prefer one existing focused check and do not grow a redundant test suite.

## Direct Path

Direct Path is the default. When no unresolved event below blocks the next action, read no reference and dispatch no worker; apply the core and proceed. Ordinary narrow source lookup, a reversible repository/platform default, and a known coherent multi-file edit remain Direct Path.

A reported symptom or named failing function is not a diagnosed cause. When a failure's earliest incorrect state is not already established by evidence, Direct Path does not apply: load `references/debugging.md` before editing.

## Event Router

Otherwise load only the module for the unresolved event that blocks the next safe action. Resolve it, then route again; task nouns and file counts do not select modules.

| Unresolved event | Read |
|---|---|
| a material choice about architecture, dependencies, APIs, data models, compatibility, or multiple plausible implementations remains unresolved | `references/decision.md` |
| understanding the task requires broad navigation of a large or structurally complex codebase | `references/exploration.md`, or `references/codebase-memory.md` only when the project explicitly enables it |
| an observed failure, regression, or failed check still lacks a diagnosed cause | `references/debugging.md` |
| a change must coordinate multiple files, contracts, or invariants and the change surface is unclear | `references/implementation.md` |
| risk or uncertainty makes the verification strategy itself a meaningful decision | `references/verification.md` |

Do not preload modules. Missing or false configuration means Codebase Memory is off.

When events overlap, diagnose an unexplained failure first; otherwise resolve a material user-owned Decision before mapping or implementing its dependent surface. Use Exploration only when broad navigation is still needed, Implementation only when a coordinated contract surface is still unclear, and Verification only when choosing evidence is itself unresolved.

## Isolation Gate

Prefer one isolated worker when the context it avoids, or the parallel work it unblocks, clearly exceeds startup and handoff cost. Use multiple workers only for genuinely independent, non-overlapping scopes when parallelism clearly outweighs coordination cost. Each worker reads `references/delegation.md` plus its one assigned module; the root retains user intent, repository state, integration, and the final completion claim, and does not duplicate worker scope. No overlapping writers or worker pipelines.

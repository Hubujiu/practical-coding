---
name: practical-coding
description: "Use for general coding work: implementing, modifying, or refactoring code, fixing bugs, regressions, or failed checks, choosing architectures, dependencies, APIs, or data models, reviewing changes, deciding how to verify work, and navigating large or structurally complex codebases. Also use when a task risks over-engineering, speculative abstraction, defensive bloat, unnecessary tests or documentation, or wasteful repeated exploration."
license: MIT
metadata:
  author: Hubujiu
  version: "1.7"
---

# Practical Coding

One coding skill: a small always-on core plus independently loadable modules. Start with a narrow inspection and expand only when routing evidence is insufficient; this router does not replace ordinary coding judgment.

## Always-on Core

These rules apply on every path, including work that loads no module:

- Understand the requested outcome and inspect the smallest relevant context before changing anything.
- Everything you add — capability, abstraction, dependency, validation, fallback, retry, configuration, documentation, or test — must trace to a concrete requirement, an actual boundary, project policy, or observed risk.
- For non-trivial capabilities, prefer integrating a mature maintained implementation over building a parallel one.
- Preserve required security, permissions, data integrity, accessibility, compatibility, and explicit project constraints.
- Keep unrelated code and existing user changes untouched.
- Before claiming completion, obtain the cheapest fresh evidence sufficient for the change.

## Direct Path

When the behavior, the relevant paths, and a sufficient focused check are already known, read no reference and dispatch no worker; apply the core rules and proceed normally.

## Event Router

Otherwise load only the module whose event is unresolved.

| Unresolved event | Read |
|---|---|
| a material choice about architecture, dependencies, APIs, data models, compatibility, or multiple plausible implementations | `references/decision.md` |
| understanding the task requires broad navigation of a large or structurally complex codebase | `references/exploration.md`, or `references/codebase-memory.md` only when the project explicitly enables it |
| an observed failure, regression, or failed check still lacks a diagnosed cause | `references/debugging.md` |
| a change must coordinate multiple files, contracts, or invariants and the change surface is unclear | `references/implementation.md` |
| risk or uncertainty makes the verification strategy itself a meaningful decision | `references/verification.md` |

Do not preload modules. Missing or false configuration means Codebase Memory is off.

## Isolation Gate

Prefer one isolated worker when the context it avoids, or the parallel work it unblocks, clearly exceeds startup and handoff cost. Use multiple workers only for genuinely independent, non-overlapping scopes when parallelism clearly outweighs coordination cost. Each worker reads `references/delegation.md` plus its one assigned module; the root retains user intent, repository state, integration, and the final completion claim, and does not duplicate worker scope. No overlapping writers or worker pipelines.

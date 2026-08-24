---
name: practical-coding
description: "Use for general coding work: implementation, modification, debugging, refactoring, review, verification, architecture and dependency choices, and structurally complex codebase navigation. Routes known work directly, loads focused guidance only for unresolved events, and isolates unusually large module context when a subagent is cheaper."
license: MIT
metadata:
  author: Hubujiu
  version: "1.6"
---

# Practical Coding

Classify coding work after at most one narrow inspection. This router does not replace ordinary coding judgment.

## Direct Path

When the behavior, relevant path, and focused check are known, stop. Read no reference, dispatch no worker, and proceed normally. Explicit cross-layer work stays direct when coordination is resolved.

## Event Router

Otherwise load only the unresolved event.

| Event | Read |
|---|---|
| viable choices materially differ | `references/decision.md` |
| broad scanning is otherwise necessary | `references/exploration.md`, or `codebase-memory.md` only when explicitly enabled |
| an observed failure still lacks a cause | `references/debugging.md` |
| an impact map still leaves contract/invariant coordination unresolved | `references/implementation.md` |
| project gates and focused checks still leave sufficient evidence unresolved | `references/verification.md` |

Do not preload modules. Missing or false config means Codebase Memory is off.

## Isolation Gate

Use one worker only when avoided context or parallel critical-path work clearly exceeds startup and handoff. It reads `delegation.md` plus one module; the root waits and does not duplicate its scope. No overlapping writers or worker pipelines.

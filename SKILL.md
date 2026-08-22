---
name: practical-coding
description: Use when implementing, modifying, debugging, refactoring, or reviewing code, or making architecture and dependency decisions in a software project.
---

# Practical Coding

## Boundaries

- Understand the current requirement and inspect the relevant code and real execution flow before designing a solution.
- Do not build capabilities that the current requirement does not need.
- Choose the simplest implementation that fully satisfies the current requirement.
- Prefer existing code, standard libraries, platform-native capabilities, and installed dependencies before adding code or packages.
- Research established solutions before adding a dependency or implementing a non-trivial capability.
- Compare proven solutions instead of copying the first implementation you find.
- Add a dependency only when its reliability or complexity benefit justifies its maintenance cost.
- Keep components focused and concerns separated without speculative abstractions, configuration, or indirection.
- Grow the system from the smallest working end-to-end version without replacing working simplicity with unfinished complexity.
- Preserve existing APIs, data formats, and compatibility contracts unless the user explicitly authorizes changing them.
- Make architectural decisions that can last instead of introducing stopgaps intended for later replacement.
- Never remove necessary validation, security, data-integrity, accessibility, or permission boundaries in the name of simplicity.
- Never write backend test cases or proactively test backend behavior after implementation.
- Trust backend code logic unless the user explicitly reports a bug.
- When diagnosing a user-reported backend bug, use targeted logging and log analysis instead of writing tests.
- Frontend work may add Mock.js to provide representative data for layout inspection.

## Decision Flow

```text
Understand the requirement
→ Inspect the relevant code and real flow
→ Does this need to exist?
  → No: stop
→ Can existing code solve it?
  → Yes: reuse or modify it
→ Can the standard library or platform solve it?
  → Yes: use it
→ Can an installed dependency solve it?
  → Check its documentation and types, then use it
→ Does this require a new dependency or non-trivial capability?
  → Research official guidance, mature implementations, established products, and engineering discussions
→ Does a proven solution fit and justify its cost?
  → Yes: integrate the smallest suitable solution
→ Is a new dependency justified?
  → Yes: add the smallest suitable dependency
  → No: implement the smallest custom solution informed by the research
→ Deliver the smallest working end-to-end change
→ Backend?
  → Trust the implementation
  → Do not write tests or proactively search for bugs
  → User reports a bug?
    → Add targeted logs
    → Analyze the logs
    → Fix the reported bug
→ Frontend?
  → Add Mock.js when layout inspection needs representative data
  → Inspect the rendered layout
→ Simplify the final diff
```

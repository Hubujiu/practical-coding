---
name: practical-coding
description: Use for software implementation, modification, debugging, refactoring, review, architecture, dependency, and verification tasks. Routes each task to only the minimum Practical Coding modules it actually needs.
---

# Practical Coding

Practical Coding is one coding skill with independently loadable modules. Do not run a fixed workflow. Load only the rules that materially help the current task.

## Goal

Produce the smallest durable change with enough evidence to justify confidence while minimizing unnecessary code, tests, documentation, dependencies, defensive handling, process, and context usage.

## Always-on Core

- Understand the requested outcome and inspect the smallest relevant code or project context before changing anything.
- Expand context only when current evidence is insufficient.
- Do not add capabilities, abstractions, dependencies, validation, fallbacks, retries, configuration, documentation, or tests without a concrete reason from the requirement, an actual boundary, project policy, or observed risk.
- Preserve required security, permissions, data integrity, accessibility, compatibility, and explicit project constraints.
- Keep unrelated code and user changes untouched.
- Treat existing code, project instructions, documentation, and Git history as evidence when useful, not as mandatory ceremony.
- Obtain the cheapest fresh evidence sufficient for the change before claiming completion.

## Module Router

Read only the references whose trigger matches the current task. Modules are independent and do not imply an execution order.

### Decision

Read `references/decision.md` when the task requires a material choice about architecture, dependencies, APIs, data models, compatibility, a new capability, or multiple plausible implementations.

Skip it for direct, well-specified local edits such as copy changes, simple layout movement, renames, obvious style changes, or mechanical modifications with no material design choice.

### Implementation

Read `references/implementation.md` when modifying project files or code.

This is the normal module for direct implementation. If implementation exposes a new material design choice, load Decision at that point rather than preloading it.

### Debugging

Read `references/debugging.md` only when a failure, regression, incorrect behavior, or failed verification needs diagnosis.

Do not load it for ordinary implementation and do not proactively turn a successful task into an open-ended bug hunt.

### Verification

For trivial, low-risk changes, use direct evidence such as inspecting the diff, rendering the changed UI, compiling the touched target, or another obvious focused check without loading an additional module.

Read `references/verification.md` when risk, uncertainty, project gates, public behavior, security, permissions, concurrency, persistence, migration, integration, or a non-trivial behavioral change makes verification strategy itself a meaningful decision.

### Structured Codebase Memory

Structured codebase memory is an optional future extension and is not bundled by this version. Do not install, initialize, or assume a code graph. When an integration is added later, it must remain optional and should be queried only when its indexing and context cost is justified by codebase size or navigation complexity.

## Routing Examples

```text
Change button copy
→ Implementation
→ direct visual/diff evidence

Move a button with an obvious CSS change
→ Implementation
→ direct render evidence

Add a new authentication provider
→ Decision + Implementation + Verification

Fix a reported production bug
→ Debugging + Implementation
→ Verification only if the risk or fix warrants the full module

Review an architecture proposal without changing code
→ Decision only
```

## Escalation

- A module may load another module only when work reveals that module's trigger.
- Do not create plans, execution documents, test suites, review stages, commits, branches, or extra artifacts merely because a generic coding workflow usually does so.
- If the project or user explicitly requires one of those artifacts or gates, follow that requirement with the smallest sufficient implementation.
- Record a durable technical decision only when the reason cannot be cheaply reconstructed from code, existing documentation, or history and is likely to matter later.

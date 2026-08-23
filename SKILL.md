---
name: practical-coding
description: Use when implementing, modifying, or refactoring code, fixing a bug, regression, error, or failed check, choosing an architecture, dependency, API, or data model, reviewing changes, deciding how to verify a change, or navigating a large or structurally complex codebase. Also use when a task risks over-engineering, speculative abstraction, defensive bloat, unnecessary tests or documentation, process overhead, or wasteful repeated code exploration.
license: MIT
metadata:
  author: Hubujiu
  version: "1.5"
---

# Practical Coding

Practical Coding is one coding skill with independently loadable modules. Do not run a fixed workflow. Load only the rules that materially help the current task.

## Goal

Produce the smallest durable change with enough evidence to justify confidence while minimizing unnecessary code, tests, documentation, dependencies, defensive handling, process, and context usage.

## Always-on Core

- Understand the requested outcome and inspect the smallest relevant code or project context before changing anything.
- Expand context only when current evidence is insufficient.
- Every capability, abstraction, dependency, validation, fallback, retry, configuration item, document, or test you add must trace to a concrete requirement, an actual boundary, project policy, or observed risk.
- For non-trivial capabilities, prefer integrating a mature, maintained implementation over building a parallel implementation. Add custom code only for requirements, integration gaps, or confirmed defects the mature implementation does not cover.
- Preserve required security, permissions, data integrity, accessibility, compatibility, and explicit project constraints.
- Keep unrelated code and user changes untouched.
- Treat existing code, project instructions, documentation, structured code intelligence, and Git history as evidence when useful, not as mandatory ceremony.
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

Read `references/codebase-memory.md` only when structured code navigation would materially reduce repeated source scanning: large or multi-module repositories, call-chain analysis, impact analysis, cross-service relationships, architecture discovery, exact coverage questions, or repeated multi-agent exploration.

Codebase Memory uses the mature MIT-licensed `DeusData/codebase-memory-mcp` implementation as its only graph backend. Do not maintain or fall back to a lower-accuracy Practical Coding parser.

Project preference lives in `.practical-coding.yaml` and is persistent:

```yaml
version: 1
codebase_memory:
  enabled: true
```

If no project configuration exists:

- for a small project or a local edit that targeted search can handle cheaply, skip Codebase Memory without asking;
- when the repository or task would materially benefit from structured code intelligence, ask once whether the user wants Codebase Memory enabled for this project;
- persist the answer as `enabled: true` or `enabled: false`, preserving unrelated project configuration, so later sessions do not repeat the project-level question.

When enabled, prefer an existing `codebase-memory-mcp` executable. If none is available and `npx` is usable, invoke the official npm wrapper lazily with `npx --yes codebase-memory-mcp@latest ...`; this downloads/caches the upstream native runtime without installing its MCP/Skill integration into the agent.

Do not automatically run `codebase-memory-mcp install`, because that mutates agent/editor configuration and can add a second Codebase Memory Skill/MCP surface. Practical Coding normally uses upstream CLI mode only.

If neither the upstream executable nor an official lazy launcher can be used, do not change the persisted preference. Continue with ordinary source search and explicitly report that Codebase Memory was not used for this task.

Enabling Codebase Memory means the upstream engine may be used when useful, not that every task must query it. Use upstream indexing, coverage, search, trace, architecture, impact, semantic, and source-snippet capabilities rather than recreating them locally.

## Routing Examples

```text
Change button copy
→ Implementation
→ direct visual/diff evidence

Add a new authentication provider
→ Decision + Implementation + Verification

Fix a reported production bug
→ Debugging + Implementation
→ Verification only if the risk or fix warrants the full module

Trace a request across a large monorepo with Codebase Memory enabled
→ resolve upstream CLI
→ index/refresh with upstream engine
→ structured discovery + coverage checks
→ decisive source verification

Codebase Memory enabled but upstream CLI cannot be launched
→ keep persistent preference unchanged
→ use normal source search for this task
→ report that Codebase Memory was not used

Review an architecture proposal without changing code
→ Decision only
```

## Escalation

- A module may load another module only when work reveals that module's trigger.
- Create plans, execution documents, test suites, review stages, commits, branches, or other process artifacts only when the user, the project, or the task itself requires them; a generic workflow habit is not a requirement.
- If the project or user explicitly requires one of those artifacts or gates, follow that requirement with the smallest sufficient implementation.
- Record a durable technical decision only when the reason cannot be cheaply reconstructed from code, existing documentation, structured code intelligence, or history and is likely to matter later.

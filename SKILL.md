---
name: practical-coding
description: Use when implementing, modifying, or refactoring code, fixing a bug, regression, error, or failed check, choosing an architecture, dependency, API, or data model, reviewing changes, deciding how to verify a change, or navigating a large or structurally complex codebase. Also use when a task risks over-engineering, speculative abstraction, defensive bloat, unnecessary tests or documentation, process overhead, or wasteful repeated code exploration.
license: MIT
metadata:
  author: Hubujiu
  version: "1.4"
---

# Practical Coding

Practical Coding is one coding skill with independently loadable modules. Do not run a fixed workflow. Load only the rules that materially help the current task.

## Goal

Produce the smallest durable change with enough evidence to justify confidence while minimizing unnecessary code, tests, documentation, dependencies, defensive handling, process, and context usage.

## Always-on Core

- Understand the requested outcome and inspect the smallest relevant code or project context before changing anything.
- Expand context only when current evidence is insufficient.
- Every capability, abstraction, dependency, validation, fallback, retry, configuration item, document, or test you add must trace to a concrete requirement, an actual boundary, project policy, or observed risk.
- Preserve required security, permissions, data integrity, accessibility, compatibility, and explicit project constraints.
- Keep unrelated code and user changes untouched.
- Treat existing code, project instructions, documentation, the embedded code graph, and Git history as evidence when useful, not as mandatory ceremony.
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

Read `references/codebase-memory.md` only when structured code navigation would materially reduce repeated source scanning: large or multi-module repositories, call-chain analysis, impact analysis, cross-service relationships, architecture discovery, or repeated multi-agent exploration.

The graph helper is bundled with this skill at `runtime/codebase_memory.py`. It is not a second agent runtime: the Skill is the instructions the agent loads, while this Python helper is only invoked by the agent when those instructions route a task to Codebase Memory. Do not require or install `codebase-memory-mcp`; MCP, WebUI, daemon, watcher, semantic model, and upstream installation machinery are not required.

Project preference lives in `.practical-coding.yaml` and is persistent:

```yaml
version: 1
codebase_memory:
  enabled: true
```

If no project configuration exists:

- for a small project or a local edit that targeted search can handle cheaply, skip codebase memory without asking;
- when the repository or task would materially benefit from a graph, ask once whether the user wants codebase memory enabled for this project;
- persist the user's answer as `enabled: true` or `enabled: false`, preserving unrelated project configuration, so later sessions do not ask the same project-level preference again.

`.practical-coding.yaml` is a Skill routing preference, not a safety gate inside the helper program. Read it before deciding whether to invoke the graph. A user manually running `runtime/codebase_memory.py` directly is outside this routing gate by design.

When codebase memory is enabled, resolve a usable Python 3 command before invoking the helper. Prefer `python`, then `python3`, then Windows `py -3` when available.

If no usable Python 3 environment is available:

- do not change the persisted `codebase_memory.enabled` preference;
- continue the current task with normal source search and direct reads instead of blocking;
- explicitly report that Codebase Memory was not used because no usable Python 3 environment was available;
- do not automatically install Python or repeatedly retry within the same task/session.

A later task or another machine may try again when the persistent project preference remains `enabled: true`.

Enabling codebase memory means the bundled helper may be used when useful, not that every task must query it. Index on demand and refresh incrementally before structural claims when source may have changed.

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

Trace a request across a large monorepo with codebase memory enabled
→ resolve Python
→ Codebase Memory for discovery
→ Implementation only if code changes are requested

Codebase Memory enabled but Python unavailable
→ keep the persistent preference unchanged
→ use normal source search for this task
→ report that Codebase Memory was not used

Review an architecture proposal without changing code
→ Decision only
```

## Escalation

- A module may load another module only when work reveals that module's trigger.
- Create plans, execution documents, test suites, review stages, commits, branches, or other process artifacts only when the user, the project, or the task itself requires them; a generic workflow habit is not a requirement.
- If the project or user explicitly requires one of those artifacts or gates, follow that requirement with the smallest sufficient implementation.
- Record a durable technical decision only when the reason cannot be cheaply reconstructed from code, existing documentation, the code graph, or history and is likely to matter later.

# Practical Coding

This repository is an Agent Skill. If you are a coding agent reading this file from a checkout, apply the skill as follows.

Read [`SKILL.md`](SKILL.md) for the always-on core, modes, and event router. The default mode is smart; an explicit user request or `.practical-coding.yaml` `mode:` selects low (lazier routing — Debugging, Decision, and Exploration/Codebase Memory only when proceeding blind is risky; no workers) or high (eager routing, prefer workers) as defined in `SKILL.md`. Local, well-specified tasks use the Direct Path with no reference and no worker. For a substantial triggered event, prefer an isolated no-history worker when its context savings exceed handoff cost; use multiple workers only for genuinely independent, non-overlapping scopes when parallelism clearly wins; otherwise load only that reference in the root agent:

| Trigger | Module |
|---|---|
| A material choice about architecture, dependencies, APIs, data models, compatibility, or multiple plausible implementations | [`references/decision.md`](references/decision.md) |
| A change must coordinate multiple files, contracts, or invariants and the change surface is unclear, or the sufficient evidence for a risky change is itself unresolved | [`references/implementation.md`](references/implementation.md) |
| An observed failure, regression, incorrect behavior, or failed verification needs diagnosis | [`references/debugging.md`](references/debugging.md) |
| Broad navigation of a large or structurally complex codebase with ordinary source search (the default) | [`references/exploration.md`](references/exploration.md) |
| The same structural event when `.practical-coding.yaml` explicitly enables Codebase Memory | [`references/codebase-memory.md`](references/codebase-memory.md) |

Modules are independent and imply no execution order.

The root agent owns user intent, authorization, repository state, routing, integration, and the final completion claim. A selected module worker reads [`references/delegation.md`](references/delegation.md) plus exactly one assigned module and returns a compact capsule. Workers are read-only by default; an implementation worker must have explicit scope and be the sole writer there. Treat a capsule as stale after relevant repository changes.

For non-trivial capabilities, prefer mature maintained implementations over parallel reimplementation. Custom code should close a concrete gap or confirmed defect, not duplicate an existing production-grade solution.

Structured Codebase Memory is a Skill-routed opt-in capability backed directly by the mature `DeusData/codebase-memory-mcp` implementation. It is used only when `.practical-coding.yaml` explicitly sets `codebase_memory.enabled: true`; false or missing configuration uses ordinary Exploration without prompting.

When enabled, prefer an existing `codebase-memory-mcp` executable. Otherwise, when `npx` is available, the Skill may use `npx --yes codebase-memory-mcp@latest` as a lazy official launcher. Use upstream CLI mode; do not automatically run its `install` command or add a duplicate MCP/Skill integration. If the upstream engine cannot be launched, keep the project preference unchanged, continue with ordinary source search, and explicitly report that Codebase Memory was not used for the task.

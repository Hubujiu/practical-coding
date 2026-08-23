# Practical Coding

This repository is an Agent Skill. If you are a coding agent reading this file from a checkout, apply the skill as follows.

Read [`SKILL.md`](SKILL.md) for the always-on core rules, then load only the reference modules whose trigger matches the current task:

| Trigger | Module |
|---|---|
| A material choice about architecture, dependencies, APIs, data models, compatibility, or multiple plausible implementations | [`references/decision.md`](references/decision.md) |
| Modifying code or project files | [`references/implementation.md`](references/implementation.md) |
| An observed failure, regression, incorrect behavior, or failed verification needs diagnosis | [`references/debugging.md`](references/debugging.md) |
| Risk or uncertainty makes the verification strategy itself a meaningful decision | [`references/verification.md`](references/verification.md) |
| Large or structurally complex codebase navigation, call-chain analysis, impact analysis, architecture discovery, exact coverage questions, or repeated exploration where structured code intelligence reduces source scanning | [`references/codebase-memory.md`](references/codebase-memory.md) |

Modules are independent and imply no execution order.

For non-trivial capabilities, prefer mature maintained implementations over parallel reimplementation. Custom code should close a concrete gap or confirmed defect, not duplicate an existing production-grade solution.

Structured Codebase Memory is a Skill-routed optional capability backed directly by the mature `DeusData/codebase-memory-mcp` implementation. The project preference is persisted in `.practical-coding.yaml`; when the file is missing and structured code intelligence would materially help, ask once and persist the user's `enabled: true` or `enabled: false` choice.

When enabled, prefer an existing `codebase-memory-mcp` executable. Otherwise, when `npx` is available, the Skill may use `npx --yes codebase-memory-mcp@latest` as a lazy official launcher. Use upstream CLI mode; do not automatically run its `install` command or add a duplicate MCP/Skill integration. If the upstream engine cannot be launched, keep the project preference unchanged, continue with ordinary source search, and explicitly report that Codebase Memory was not used for the task.

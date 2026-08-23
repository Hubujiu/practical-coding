# Practical Coding

This repository is an Agent Skill. If you are a coding agent reading this file from a checkout, apply the skill as follows.

Read [`SKILL.md`](SKILL.md) for the always-on core rules, then load only the reference modules whose trigger matches the current task:

| Trigger | Module |
|---|---|
| A material choice about architecture, dependencies, APIs, data models, compatibility, or multiple plausible implementations | [`references/decision.md`](references/decision.md) |
| Modifying code or project files | [`references/implementation.md`](references/implementation.md) |
| An observed failure, regression, incorrect behavior, or failed verification needs diagnosis | [`references/debugging.md`](references/debugging.md) |
| Risk or uncertainty makes the verification strategy itself a meaningful decision | [`references/verification.md`](references/verification.md) |
| Large or structurally complex codebase navigation, call-chain analysis, impact analysis, architecture discovery, or repeated exploration where a graph reduces source scanning | [`references/codebase-memory.md`](references/codebase-memory.md) |

Modules are independent and imply no execution order. Structured codebase memory is bundled at `runtime/codebase_memory.py` but remains optional per project/task. Respect `.practical-coding.yaml` when present. When enabled, resolve Python 3 before using the runtime; if Python is unavailable, explain the requirement, persist `codebase_memory.enabled: false`, and continue with ordinary source search instead of blocking.

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

Modules are independent and imply no execution order.

Structured Codebase Memory is a Skill-routed optional capability. The project preference is persisted in `.practical-coding.yaml`; when the file is missing and a graph would materially help, ask once and persist the user's `enabled: true` or `enabled: false` choice. The bundled `runtime/codebase_memory.py` file is only a helper program invoked after the Skill chooses the graph path; it is not a separate agent runtime and does not enforce the project preference itself.

When Codebase Memory is enabled, resolve Python 3 before invoking the helper. If no usable Python 3 environment exists, keep the persistent preference unchanged, continue with ordinary source search, and explicitly report that Codebase Memory was not used for this task. Do not auto-install Python or repeatedly retry within the same task/session.

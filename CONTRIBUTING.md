# Contributing

Contributions should preserve Practical Coding as one compact skill with independently loadable modules.

- Keep `SKILL.md` as a small router plus rules that genuinely apply to almost every coding task.
- Put conditional behavior in focused files under `references/` and state an exact trigger for loading each file.
- Keep modules independent; do not create a mandatory chain where loading one module automatically requires the others.
- Prefer strengthening an existing module over adding a new module.
- Add a new module only when it represents a distinct, reusable decision surface that would otherwise pollute unrelated tasks.
- Do not introduce mandatory plans, execution documents, Git workflows, tests, reviews, documentation, or tool-specific ceremony as universal gates.
- Preserve the solution priority of reuse before invention, risk-proportional verification, evidence-driven debugging, and resistance to speculative code and defensive bloat.
- Keep optional heavy capabilities such as structured codebase memory outside the default context and default runtime cost.
- Avoid scripts, dependencies, configuration, and generated project files unless they solve a demonstrated need.

## Codebase Memory changes

Before extending the embedded graph helper, inspect the mature upstream [`DeusData/codebase-memory-mcp`](https://github.com/DeusData/codebase-memory-mcp) implementation for the same problem.

- If upstream already has a proven mechanism that can be adapted without importing its large runtime stack, prefer adapting that mechanism over inventing a parallel design here.
- Keep attribution and license notices when upstream code or substantial implementation material is reused; see `THIRD_PARTY_NOTICES.md`.
- Do not chase upstream parser parity by continually adding regex heuristics. Upstream's multi-language quality depends on its Tree-sitter and Hybrid LSP stack. If a requirement truly needs that level of accuracy, reconsider the backend boundary rather than pretending a lightweight parser is equivalent.
- Preserve the embedded helper's role as a zero-third-party-dependency discovery accelerator. Exact, negative, and exhaustive conclusions still return to decisive source code.

A change is moving in the wrong direction if a trivial local edit must load or execute more process after the change than before it.

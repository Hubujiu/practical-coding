# Practical Coding

Practical Coding is an Agent Skill for producing the smallest reliable coding change without turning every task into a heavyweight workflow.

It uses one compact Core, three evidence-triggered reasoning modules, and an orthogonal retrieval policy:

```text
Core / Direct
├─ unresolved observed failure            → Debugging
├─ unresolved material implementation choice → Decision
└─ unresolved contract, invariant, or risk boundary → Implementation

Retrieval (independent):
known target → bounded/ranked search → structural or authoritative evidence → bounded exhaustive coverage
```

## Runtime contract

The Core applies to every task:

- define the smallest observable success;
- reuse established project primitives;
- add no speculative abstractions, dependencies, configuration, validation, tests, or documentation;
- preserve unrelated behavior and user changes;
- verify with the cheapest check that can falsify the material claim.

If no unresolved Event Router condition matches, stay Direct. A risk-related noun, multiple files, unknown paths, or caller discovery does not itself justify a reasoning module.

When an event is present, load exactly one reference:

- [`references/debugging.md`](references/debugging.md) — an observed failure still lacks an evidenced cause;
- [`references/decision.md`](references/decision.md) — a material user-owned implementation choice remains open;
- [`references/implementation.md`](references/implementation.md) — safe execution is blocked by an unresolved contract, coordinated invariant, material risk boundary, or evidence plan.

Requirements interviewing and `grill-me` behavior are explicit-only through [`references/manual/clarification.md`](references/manual/clarification.md). One unavoidable blocking question in an ordinary task is normal interaction, not an interview mode.

## Retrieval policy

Retrieval is separate from reasoning. Use the cheapest available capability that supplies enough current context:

1. read a known path or symbol;
2. use bounded/ranked filename, text, or symbol search;
3. use an already-available structural index for relationship questions when it saves work;
4. use bounded exhaustive coverage only for explicit exhaustive claims, and authoritative external sources only for contracts the repository cannot establish;
5. verify material conclusions against current source.

[`references/navigation.md`](references/navigation.md) is the optional detailed procedure for substantial retrieval. Codebase Memory, LSP/AST, ranked search, and ordinary search are capabilities, not required dependencies.

## Evolution discipline

Runtime agents do not read `evolution/`. Maintainers record experiences, consolidate repeated mechanisms, freeze experiments before changing runtime rules, and preserve rejected changes.

The rejected E/R depth and specialist-leaf experiment is retained under [`evolution/rejected/`](evolution/rejected/) with its n=3 evidence in [`benchmarks/results/progressive-tree/`](benchmarks/results/progressive-tree/). The replacement event-router experiment is documented in [`evolution/experiments/event-router-restoration.md`](evolution/experiments/event-router-restoration.md).

The accepted v1.5 release evidence is published under [`benchmarks/results/v1.5/`](benchmarks/results/v1.5/). Its frozen current-only n=3 matrix had zero indeterminate cells: Delivery 54/54, Debug 40/42, Decision 29/30, Native Behavior 52/54, and 61/66 held-out quality cells across 22 real tasks. Event reasoning was 113/114; after correcting three retrieval expectations that contradicted the current structural-mapping contract, the public Router result was 107/114 (reasoning 113/114, retrieval 108/114). These are non-paired release results; they do not claim superiority over other skills.

## Validation

Public regression and real-repository held-out validation use `gpt-5.6-luna` at medium reasoning. Iteration runs use `n=1`; release claims require the complete current-only matrix at `n=3`.

```powershell
pwsh -NoProfile -File benchmarks/run.ps1 -SelfTest
pwsh -NoProfile -File benchmarks/run.ps1 -ProgressiveSelfTest

python benchmarks/run_catalog.py --profile full --runs 3 --workers 3 `
  --arm practical-current --arm practical-native --output benchmark-results/public-final

python benchmarks/progressive_validation.py --phase all --current-only --runs 3 --workers 3 `
  --output benchmark-results/heldout-final
```

Historical published evidence remains version-specific and non-paired unless its arms are rerun in one frozen matrix.

MIT License. See `THIRD_PARTY_NOTICES.md` for attribution.

# Contributing

Contributions to the progressive-ladders experiment should preserve one invariant:

> Practical Coding should use the **lowest quality-sufficient execution process and retrieval scope**, then escalate only from evidence and contract again after localization.

## Runtime architecture

- Keep `SKILL.md` as the compact control policy and Core.
- Decision is a gate, not an execution level.
- Execution currently tests `E0 Direct → E1 Guided → E2 Structured → E3 Assurance`.
- Retrieval currently tests `R0 Target → R1 Local → R2 Structural → R3 Repository → R4 External`.
- Debugging and Implementation are capabilities loaded at structured/assurance depth, not sequential levels.
- Navigation is retrieval, not another reasoning branch.
- E3 must deepen the already-selected capability rather than load a second reasoning module.
- Keep the root to Core plus at most one reasoning reference; use isolation only when it saves net context.
- Do not introduce mandatory plans, reviews, Git workflows, tests, documents, workers, or other ceremony as universal stages.

The level names/counts are hypotheses. A contribution may merge, remove, split, or rename them if benchmark evidence supports the change.

## Escalation changes require evidence

Do not retune boundaries from one failed public cell.

A good escalation change identifies:

1. a repeated mechanism rather than a task noun;
2. whether the current behavior is over-escalation or under-escalation;
3. the lower/higher capped result showing which rung is actually sufficient;
4. the expected quality and cost effect;
5. held-out validation when making a general claim.

A change is moving in the wrong direction if trivial local work pays more process/context after the change without a quality benefit.

## Retrieval discipline

Tool choice is subordinate to scope:

1. known target/current context first;
2. bounded local discovery;
3. structural relationship retrieval when that is the unresolved question;
4. repo-wide only when narrower scopes cannot localize or a bounded exhaustive claim is required;
5. external authoritative evidence only for facts the repository cannot establish.

FFF-style ranked retrieval, ordinary search, LSP/AST, and Codebase Memory-style graph tools are optional capabilities. Do not make an optional backend a hard dependency or install/persist tooling solely for retrieval.

Always contract scope after localization. A broad search that identifies two relevant files should not justify continued broad exploration.

## Evolution records

Runtime agents must not read `evolution/` for ordinary coding tasks.

For Skill maintenance:

- repeated evidence-supported mechanisms go to `evolution/patterns/`;
- proposed changes are frozen under `evolution/experiments/` before validation;
- rejected/regressive changes remain under `evolution/rejected/` so the project does not repeat them later.

Do not copy large raw transcripts into evolution records. Keep task/run IDs and compact evidence.

## Benchmark requirements

Use `benchmarks/LADDER_EVOLUTION.md` for boundary/level changes. Correctness, safety, and build/reachability always gate efficiency.

Public cases that influenced wording are regression evidence. Strong generalization claims require held-out tasks and repeated determinate runs.

Do not preserve four execution levels or five retrieval levels for symmetry. If a rung is almost never the minimum sufficient rung, test removing or merging it. If one rung contains separable repeated under/over-escalation clusters, test moving or splitting the boundary.

## Mature implementation first

For non-trivial capability work with credible prior art:

1. inspect maintained mature implementations first;
2. prefer supported public integration surfaces over copying internals;
3. verify fit, maintenance state, known issues, operational constraints, and license;
4. add local code only for concrete gaps;
5. keep patches narrow and removable.

Prefer strengthening the control policy or an existing capability over adding another permanent module.

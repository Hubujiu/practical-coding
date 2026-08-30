# Contributing

Contributions to the progressive-capability-tree experiment should preserve one invariant:

> Practical Coding should use the **lowest quality-sufficient engineering depth and retrieval scope**, then load only the capability needed by the concrete unresolved event.

## Runtime architecture

- Keep `SKILL.md` as the compact control policy and Core.
- Decision is a gate, not an execution level.
- Execution depth currently tests `E0 Direct → E1 Focused → E2 Root → E3 Leaf`.
- E2 selects one root: `diagnosis` or `engineering`.
- E3 may add one evidence-triggered specialist leaf, not a global checklist.
- Retrieval currently tests `R0 Target → R1 Local`, then branches to `R2 Structural`, `R2 External contract`, or `R3 bounded exhaustive repository`.
- External evidence is not downstream of repository-wide search.
- Navigation is retrieval, not another execution branch.
- Keep normal root context to Core + at most one capability root + one leaf.
- Do not introduce mandatory plans, reviews, Git workflows, tests, documents, workers, or lifecycle ceremony as universal stages.

The depth count, root set, leaf set, and trigger boundaries are all hypotheses.

## Node changes require evidence

Do not add or retune a node from one failed public case.

A good tree change identifies:

1. a repeated mechanism rather than a task noun;
2. the observable trigger available before action;
3. whether current behavior is over-escalation, under-escalation, unnecessary leaf load, missed leaf, or branch confusion;
4. parent-vs-leaf or depth-cap evidence showing what is sufficient;
5. expected quality and context/process effect;
6. held-out validation for general claims.

A specialist node that does not show stable net lift over its parent on its claimed task family should be tightened, merged, replaced, or removed.

## Retrieval discipline

Tool choice is subordinate to the unresolved question:

1. known target/current context first;
2. bounded/ranked local discovery;
3. structural relationship retrieval when relationships are the blocker;
4. authoritative external evidence when the repository cannot establish a needed contract;
5. repo-wide discovery only when narrower retrieval cannot localize or an explicit bounded exhaustive claim is required.

FFF-style ranked retrieval, ordinary search, LSP/AST, and Codebase Memory-style graphs are optional capabilities. Do not make an optional backend a hard dependency.

Always contract after localization.

## Evolution records

Runtime agents must not read `evolution/` for ordinary coding tasks.

For Skill maintenance:

- record benchmark/real-project observations with `evolution/EXPERIENCE_SCHEMA.md`;
- consolidate repeated mechanisms under `evolution/wiki/`;
- freeze proposed changes under `evolution/experiments/` before validation;
- preserve rejected/regressive changes under `evolution/rejected/`.

Existing `evolution/patterns/` is historical evidence; new mechanisms should prefer the wiki layer so evidence can compound across experiments.

Do not copy large raw transcripts, private code, or sensitive content into evolution records.

## Benchmark requirements

Use `benchmarks/LADDER_EVOLUTION.md` for depth/tree changes. Quality gates always precede efficiency.

Compare no-skill, accepted prior Practical Coding, and the candidate adaptive tree. Use external expert skills only as family-specific comparators where their scope actually matches.

Do not preserve four execution depths, four retrieval depths, two roots, or six leaves for symmetry. Remove/merge nodes that do not earn their cost; split only when a stable observable condition separates repeated failure clusters.

## Mature implementation first

For non-trivial capability work with credible prior art:

1. inspect maintained mature implementations first;
2. extract principles and supported public integration surfaces rather than copying whole workflows;
3. verify fit, maintenance state, known constraints, and license;
4. add local guidance only for concrete gaps;
5. keep every new node narrow and removable.

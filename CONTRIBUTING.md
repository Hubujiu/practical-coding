# Contributing

Contributions to the progressive-capability-tree experiment should preserve one invariant:

> Practical Coding should use the **lowest quality-sufficient engineering depth and retrieval scope**, then load only the adaptive capability needed by the concrete unresolved event.

## Runtime architecture

- Keep `SKILL.md` as the compact control policy and Core.
- Default runtime begins at Core/E0; there is no automatic Clarification or Decision gate.
- Execution depth currently tests `E0 Direct → E1 Probe → E2 Root → E3 Leaf`.
- E1 is only a cheap executable observation/falsification step. **Source discovery never raises execution depth by itself.**
- E2 selects one root: `diagnosis` or `engineering`.
- E3 may add one evidence-triggered specialist leaf, not a global checklist.
- Retrieval starts `R0 Target → R1 Local`, then branches to `R2 Structural`, `R2 External contract`, or `R3 bounded exhaustive repository`.
- Retrieval is the only adaptive axis for acquiring code/source/context. `references/navigation.md` is an R2 Structural/R3 coverage procedure, not a third capability axis.
- Keep normal root context to Core + at most one capability root + one leaf.
- Do not introduce mandatory plans, reviews, interviews, Git workflows, tests, documents, workers, or lifecycle ceremony as universal stages.

## Manual-only boundary

Interaction-heavy modes such as `grill-me`/requirements interviewing and Decision/option selection must remain outside adaptive routing.

A manual mode may be activated only by an explicit user request for that interaction. Do not create automatic triggers from vague requirements, multiple plausible solutions, risk level, or task complexity. Do not let one manual mode route into another without a second explicit request or an original request that explicitly asked for both behaviors.

A specialist may ask one minimum blocking user-owned question when execution is otherwise impossible. That is normal interaction and must not be reframed as entering manual Decision or Clarification mode.

Benchmark these modes separately: explicit activation should add value; spontaneous activation on ordinary tasks should be zero.

## Node changes require evidence

The adaptive depth count, root set, leaf set, and trigger boundaries are hypotheses. Do not add or retune a node from one failed public case.

A good tree change identifies a repeated mechanism, an observable pre-action trigger, the current routing error, parent-vs-leaf/depth-cap evidence, expected quality/context effect, and held-out validation for general claims.

A specialist node that does not show stable net lift over its parent on its claimed task family should be tightened, merged, replaced, or removed.

## Execution / Retrieval orthogonality

When labeling a task or designing a benchmark case, ask two separate questions:

1. **Retrieval:** how much source/context must be acquired before the next material decision is supported?
2. **Execution:** once relevant evidence is available, how much structured engineering reasoning is still required?

Finding a caller, sibling, contract, implementation, or configuration belongs to R0–R3. It does not justify E1. E1 requires an executable probe such as reproducing behavior, exercising one path, or falsifying one concrete hypothesis.

Valid combinations include `E0/R0`, `E0/R2`, `E3/R0`, and `E3/R2`.

## Retrieval discipline

Tool choice is subordinate to the unresolved question: known target → bounded/ranked local discovery → structural or authoritative external evidence when that is the blocker → repo-wide only when narrower retrieval cannot localize or an explicit bounded exhaustive claim is required.

FFF-style ranked retrieval, ordinary search, LSP/AST, and Codebase Memory-style graphs are optional capabilities. Always contract after localization.

## Evolution records

Runtime agents must not read `evolution/` for ordinary coding tasks.

For Skill maintenance, record benchmark/real-project observations with `evolution/EXPERIENCE_SCHEMA.md`, consolidate repeated mechanisms under `evolution/wiki/`, freeze proposed changes under `evolution/experiments/`, and preserve rejected changes under `evolution/rejected/`.

Do not copy large raw transcripts, private code, or sensitive content into evolution records.

## Benchmark requirements

Use `benchmarks/LADDER_EVOLUTION.md` for adaptive depth/tree changes. Quality gates always precede efficiency.

Compare no-skill, accepted prior Practical Coding, and the candidate adaptive tree. Use external expert skills only as family-specific comparators where their scope actually matches.

Do not preserve four execution depths, four retrieval depths, two roots, or six leaves for symmetry. Remove/merge nodes that do not earn their cost; split only when a stable observable condition separates repeated failure clusters.

## Mature implementation first

For non-trivial capability work with credible prior art, inspect maintained implementations first, extract principles/public surfaces rather than copying whole workflows, verify fit/maintenance/license, add local guidance only for concrete gaps, and keep every new node narrow and removable.
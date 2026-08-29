# Next validation protocol

This document freezes the evidence requirements for the **Practical Coding v1.3 adaptive-rigor candidate** before new v1.3 model results are inspected. Its purpose is to prevent post-hoc metric selection, public-regression overfitting, and marketing claims stronger than the evidence.

Version status is intentionally explicit:

- latest tagged GitHub Release: `v1.0.0`;
- last committed validated architecture baseline: **v1.2**, with compact evidence in [`results/v1.2/`](results/v1.2/);
- current candidate architecture: **v1.3**, using Decision Gate + Execution Escalation + Retrieval cost bounds;
- v1.0/v1.1/v1.2 result directories remain immutable historical evidence for their tested schemas.

## 1. Freeze before running

Before any release-quality v1.3 model run:

1. commit the candidate and use a clean working tree;
2. record the exact candidate commit, previous-baseline commit, runner bundle hash, Skill entrypoint hash, and complete Skill-bundle hash;
3. freeze the v1.3 classification contract before inspecting model results: `DECISION`, `EXECUTION`, and Retrieval minimum/maximum bounds;
4. do not change Skill text, tasks, scorers, retrieval bounds, or acceptance thresholds after seeing partial results from the same cycle;
5. if an instrument bug is found, invalidate the affected run, fix the instrument, document why, and rerun the complete affected matrix;
6. preserve the complete candidate Skill bundle and comparator pins.

Documentation-only changes do not justify retuning against already-inspected public cells. New behavioral evidence should come from held-out tasks, stack/interference tests, transition tests, or repeated independent failures.

## 2. Required gate order

### Gate A — harness self-test

```powershell
pwsh -NoProfile -File benchmarks/run.ps1 -SelfTest
```

A failing self-test blocks all benchmark claims.

### Gate B — adaptive-rigor and native-behavior regression

Because v1.3 changes the control model itself, rerun the affected classifier and native behavior suites before interpreting delivery comparisons:

```powershell
pwsh -NoProfile -File benchmarks/run.ps1 `
  -Profile full `
  -Suite router `
  -Suite behavior `
  -Runs 3 `
  -Workers 3 `
  -RequireStableRanking
```

The legacy suite id remains `router` for CLI compatibility, but its v1.3 contract is not an Event Router. It scores:

- `DECISION=CLEAR|REQUIRED`;
- `EXECUTION=BLOCKED|DIRECT|DEBUGGING|IMPLEMENTATION`;
- Retrieval as a **minimum sufficient to maximum reasonable** cost interval.

Required state invariant:

```text
DECISION=REQUIRED  => EXECUTION=BLOCKED
DECISION=CLEAR     => EXECUTION in DIRECT | DEBUGGING | IMPLEMENTATION
```

The matrix must include the explicit transition boundaries:

- Decision → Direct;
- Decision → Implementation;
- Debugging → Direct after diagnosis;
- Debugging → Implementation only when a material execution boundary remains unresolved.

### Gate C — public regression/current-vs-v1.2 gate

Run whenever `SKILL.md` or `references/` behavior changes:

```powershell
pwsh -NoProfile -File benchmarks/run.ps1 `
  -Profile full `
  -Runs 3 `
  -Workers 3 `
  -BaselineRef 88382d2b0c00fa278067a5933bbcacc86f46b56e `
  -IncludeBaseline `
  -RequireStableRanking
```

This compares the candidate against the accepted v1.2 baseline while preserving the fact that v1.2 and v1.3 classification schemas are not score-comparable. Delivery/Decision/Debug behavior, build/reachability, safety, and efficiency can still be compared where the underlying task/scorer contract is unchanged.

Acceptance order remains correctness/safety → build/reachability → efficiency.

### Gate D — private held-out evidence

The strongest generalization claim requires a task set that was not consulted while editing the Skill or its public regression corpus.

Minimum first held-out target:

- at least 20 real coding tasks;
- include simple/direct tasks, diagnosed and undiagnosed bugs, risky changes, unresolved choices, multi-file low-risk changes, and relationship-heavy retrieval tasks;
- executable verification whenever possible;
- seed state fails and oracle/reference state passes before model calls where applicable;
- same fixed model/harness for `no-skill` and Practical arms;
- at least three paired repetitions for publication-quality claims;
- report unnecessary escalation, missed escalation, and retrieval-cost overshoot in addition to task success.

## 3. Required combined-stack benchmark

Before claiming that Practical Coding is experimentally better than installing Ponytail and Superpowers together, include this arm:

```text
no-skill
Ponytail
Superpowers
Ponytail + Superpowers
Practical Coding
```

The combined arm must install the **actual pinned/current Skills simultaneously** in the same harness rather than concatenate their text manually.

Measure at minimum:

- task success, safety, and build;
- total/uncached input tokens, output tokens, reasoning tokens;
- model time and tool calls;
- number of Skill/reference files loaded;
- unnecessary rigor/profile loads;
- missed escalations;
- Decision blocking when no choice actually blocks execution;
- Debugging reload after the cause is already diagnosed;
- Implementation escalation after the governing boundary is already established;
- retrieval below the minimum sufficient bound or above the maximum reasonable bound;
- worker/subagent dispatches;
- final production/test LOC.

The task set must include at least:

1. trivial/local direct edits;
2. clear multi-file but low-risk changes;
3. unknown root-cause bugs;
4. already-diagnosed bugs;
5. security/persistence/concurrency boundaries, both mapped and unmapped;
6. unresolved architecture/dependency decisions;
7. settled decisions followed by Direct work;
8. settled decisions followed by unresolved execution boundaries.

### Hypothesis being tested

The architectural hypothesis is not "Ponytail is bad" or "Superpowers is bad." It is:

> Broad specialist Skills may provide useful capabilities but leave activation and interaction to the host/model. Practical's adaptive-rigor control policy should preserve specialist rigor when a real blocker exists while avoiding unnecessary process, reference loading, and repository context when the Core is already sufficient.

This remains a hypothesis until the combined arm is measured.

## 4. Rigor and interference ablation

To attribute any gain to adaptive activation rather than prompt wording, test:

```text
no-skill
Core only
Core + Decision
Core + Debugging
Core + Implementation
Full Practical
Ponytail + Superpowers
```

Record:

- unnecessary reference loads;
- missed escalations;
- references loaded and bytes/tokens injected;
- Decision Gate false positives/negatives;
- Execution state errors;
- retrieval minimum/maximum violations;
- time/tokens before the sufficient rigor level is reached;
- worker/subagent dispatches;
- whether a second large reference is accumulated in the root instead of isolated when isolation would be cheaper.

## 5. Retrieval scoring discipline

Do not retune Skill wording to force one exact retrieval label when multiple low-cost paths are reasonable.

The v1.3 classifier scores two retrieval failures separately:

- **insufficient retrieval:** actual level is below the declared minimum needed to act safely;
- **excessive retrieval:** actual level exceeds the declared maximum reasonable cost.

A task may therefore accept a range such as `TARGETED..BOUNDED`. Change a range only before inspecting a new validation cycle, or after an independently justified benchmark-instrument defect is documented. Do not widen a range merely to turn an observed failure green.

## 6. Statistical language

`n=3` is a stability gate, not proof that small differences are statistically resolved. For small deltas use language such as `numerically ahead`, `numerically behind`, or `tied on this matrix` and report task counts separately from repeated trials.

Future confidence intervals should bootstrap by task/case ID so repetitions of one task are not treated as independent tasks.

## 7. Failure discipline

When a failure appears:

1. save the complete run first;
2. classify infrastructure vs scorer/oracle defect vs stochastic behavior vs genuine Skill behavior;
3. distinguish control failure (Decision/Execution), retrieval insufficiency, retrieval overshoot, and delivered-code failure;
4. do not add case-specific nouns merely to turn a public cell green;
5. prefer a general invariant only after the same mechanism appears independently;
6. rerun the complete affected gate after a behavior change.

## 8. Claim ladder

| Evidence completed | Allowed claim |
|---|---|
| v1.3 public regression only | Stable on the fixed adaptive-rigor regression matrix |
| + current-vs-v1.2 behavioral comparison | Bounded before/after claims on unchanged Delivery/Decision/Debug task contracts |
| + combined Ponytail/Superpowers arm | Bounded claims about integrated-stack efficiency/quality on that task population |
| + private held-out paired run | Bounded generalization claims for the held-out population |

Never collapse Delivery vs Ponytail, Decision vs grilling, Debug vs Superpowers, adaptive-rigor classification, and the combined-stack comparison into a single universal score.

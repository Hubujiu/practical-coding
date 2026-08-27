# Next validation protocol

This document freezes the evidence requirements for the next Practical Coding validation cycle before new results are inspected. Its purpose is to prevent post-hoc metric selection, public-regression overfitting, and marketing claims stronger than the evidence.

The current public release is **Practical Coding v1.0**. The published evaluation is [`../docs/evaluations/2026-08-26-practical-v1-release.md`](../docs/evaluations/2026-08-26-practical-v1-release.md), with compact aggregates in [`results/v1.0/`](results/v1.0/).

## 1. Freeze before running

Before any release-quality model run:

1. commit the candidate and use a clean working tree;
2. record the exact candidate commit and benchmark manifest hashes;
3. do not change Skill text, tasks, scorers, or acceptance thresholds after seeing partial results from the same cycle;
4. if an instrument bug is found, invalidate the affected run, fix the instrument, document why, and rerun the complete affected matrix;
5. preserve the complete candidate Skill bundle and comparator pins.

Documentation-only changes do not justify retuning against already-inspected public cells. New evidence should come from held-out tasks, stack/interference tests, or repeated independent failures.

## 2. Required gate order

### Gate A — harness self-test

```powershell
pwsh -NoProfile -File benchmarks/run.ps1 -SelfTest
```

A failing self-test blocks all benchmark claims.

### Gate B — public regression/current-vs-previous gate

Run whenever `SKILL.md` or `references/` behavior changes:

```powershell
pwsh -NoProfile -File benchmarks/run.ps1 `
  -Profile full `
  -Runs 3 `
  -Workers 3 `
  -BaselineRef <accepted-v1.0-or-later-commit> `
  -IncludeBaseline `
  -RequireStableRanking
```

Acceptance order remains correctness/safety → build/reachability → efficiency.

### Gate C — private held-out evidence

The strongest generalization claim requires a task set that was not consulted while editing the Skill.

Minimum first held-out target:

- at least 20 real coding tasks;
- include simple/direct tasks, root-cause bugs, risky multi-file changes, and architecture/navigation tasks;
- executable verification whenever possible;
- seed state fails and oracle/reference state passes before model calls;
- same fixed model/harness for `no-skill` and Practical arms;
- at least three paired repetitions for publication-quality claims.

## 3. Required combined-stack benchmark

Before claiming that Practical Coding is experimentally better than installing Ponytail and Superpowers together, add this arm:

```text
no-skill
Ponytail
Superpowers
Ponytail + Superpowers
Practical Coding
```

The combined arm must install the **actual current Skills simultaneously** in the same harness rather than concatenate their text manually.

Measure at minimum:

- task success, safety, and build;
- total/uncached input tokens, output tokens, reasoning tokens;
- model time and tool calls;
- number of Skill/reference files loaded;
- unnecessary process/module loads;
- missed escalations;
- number of planning/debugging/delegation phases entered;
- final production/test LOC;
- whether both broad coding/process policies are invoked on simple tasks.

The task set must include at least:

1. trivial/local direct edits;
2. clear multi-file but low-risk changes;
3. unknown root-cause bugs;
4. security/persistence/concurrency boundaries;
5. unresolved architecture/dependency decisions.

### Hypothesis being tested

The architectural hypothesis is not "Ponytail is bad" or "Superpowers is bad." It is:

> Two independently broad Skills may provide useful capabilities but incur duplicated routing/process context and leave their interaction to the host/model, while Practical's single event router should preserve similar specialist rigor with less unnecessary process on tasks that do not need it.

This remains a hypothesis until the combined arm is measured.

## 4. Routing and interference ablation

To attribute any gain to adaptive routing rather than prompt wording, test:

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

- unnecessary module loads;
- missed escalations;
- references loaded and bytes/tokens injected;
- route changes per task;
- time/tokens before the correct route is reached;
- worker/subagent dispatches.

## 5. Statistical language

`n=3` is a stability gate, not proof that small differences are statistically resolved. For small deltas use language such as `numerically ahead`, `numerically behind`, or `tied on this matrix` and report task counts separately from repeated trials.

Future confidence intervals should bootstrap by task/case ID so repetitions of one task are not treated as independent tasks.

## 6. Failure discipline

When a failure appears:

1. save the complete run first;
2. classify infrastructure vs scorer/oracle defect vs stochastic behavior vs genuine Skill behavior;
3. do not add case-specific nouns merely to turn a public cell green;
4. prefer a general invariant only after the same mechanism appears independently;
5. rerun the complete affected gate after a behavior change.

## 7. Claim ladder

| Evidence completed | Allowed claim |
|---|---|
| Public regression only | Stable / numerically competitive on the fixed public matrix |
| + combined Ponytail/Superpowers arm | Bounded claims about integrated-stack efficiency/quality on that task population |
| + private held-out paired run | Bounded generalization claims for the held-out population |

Never collapse Delivery vs Ponytail, Decision vs grilling, Debug vs Superpowers, and the combined-stack comparison into a single universal score.

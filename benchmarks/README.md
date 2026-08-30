# Practical Coding benchmark chain

This experimental branch keeps the existing v1.2 public regression harness and adds a second evaluation layer for **progressive execution/retrieval boundaries**.

Historical v1.0–v1.2 results remain evidence for the Skill versions that produced them. They are not evidence that the new E0–E3 / R0–R4 architecture is better until fresh runs are completed.

## Two benchmark questions

The project now separates:

1. **Does the Skill produce a correct, safe, reachable result?**
2. **Did it pay for more process or context than that result required?**

The existing Delivery, Decision, Debug, Router, Native Behavior, and Navigation ablation suites answer the first question and preserve regression coverage. The new ladder calibration protocol answers the second.

## Existing suites

| Suite | Purpose |
|---|---|
| Delivery | Correctness, safety, build reachability, LOC, tokens, time, tool calls |
| Decision | Material-choice behavior and convergence without premature implementation |
| Debug | Root-cause repair, sibling callers, delivered invariant, safety, efficiency |
| Router / classification | Whether the Skill recognizes the intended reasoning/retrieval situation |
| Native behavior | Real Skill/reference discovery and context isolation without prompt injection |
| Navigation ablation | Whether stronger structural retrieval pays for itself on real repositories |

The v1.2 runner and historical result directories remain intact.

## Progressive ladder calibration

See [`LADDER_EVOLUTION.md`](LADDER_EVOLUTION.md).

Execution candidates:

```text
E0 Direct
E1 Guided
E2 Structured
E3 Assurance
```

Retrieval candidates:

```text
R0 Target
R1 Local
R2 Structural
R3 Repository
R4 External
```

For each task/axis, run frozen capped variants and identify the **lowest quality-qualified rung**. Then compare the normal adaptive Skill with that empirical minimum.

Primary new metrics:

- `over_escalation`: adaptive level is higher than the minimum sufficient level;
- `under_escalation`: adaptive level is lower and fails while a higher cap passes;
- `minimum_sufficient_counts`: how often each rung is actually necessary;
- cost at each quality-qualified cap.

The number of levels is itself under test. A rung that is rarely/never minimum sufficient becomes a merge/removal candidate; a rung with separable repeated under/over-escalation clusters becomes a boundary/split candidate.

## Analyze aggregated calibration observations

After repeated cells have been reduced to one qualified/not-qualified observation per task/axis/arm/level:

```bash
python benchmarks/ladder_analysis.py observations.jsonl
```

or:

```bash
python benchmarks/ladder_analysis.py observations.jsonl --output ladder-report.json
```

The input format and interpretation rules are documented in `LADDER_EVOLUTION.md`.

## Existing harness commands

Self-test:

```powershell
pwsh -NoProfile -File benchmarks/run.ps1 -SelfTest
```

Normal public regression matrix:

```powershell
pwsh -NoProfile -File benchmarks/run.ps1 -Profile standard -Runs 3 -Workers 3 -RequireStableRanking
```

Complete public regression matrix:

```powershell
pwsh -NoProfile -File benchmarks/run.ps1 -Profile full -Runs 3 -Workers 3 -RequireStableRanking
```

Candidate before/after gate:

```powershell
pwsh -NoProfile -File benchmarks/run.ps1 `
  -Profile full `
  -Runs 3 `
  -Workers 3 `
  -BaselineRef <accepted-previous-commit> `
  -IncludeBaseline `
  -RequireStableRanking
```

## Acceptance order

Always interpret results in this order:

1. correctness and safety;
2. build/reachability;
3. then routing/retrieval sufficiency;
4. only then tokens, model time, tool calls, LOC, and reference/context cost.

A cheap failure cannot beat a correct result. Likewise, a lower rung is not "better" merely because it is cheaper; it must first quality-qualify.

## Regression versus evolution evidence

Public tasks that influenced Skill wording are regression tests. They can show that a new boundary did not break known behavior, but they cannot prove generalization of that boundary.

For boundary or level-count claims, require held-out tasks plus repeated runs. Store the durable maintenance lesson under `evolution/`, not inside runtime Skill text until the experiment passes the acceptance gate.

## Output discipline

Keep raw transcripts/workspaces in normal local benchmark artifacts. Commit compact aggregates and evolution records that identify evidence without duplicating large raw context.

If an instrumentation or oracle defect is found, invalidate the affected run, fix the instrument, document the reason, and rerun the full affected matrix. Do not tune a boundary from a corrupted partial result.

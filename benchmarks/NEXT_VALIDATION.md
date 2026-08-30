# Next validation protocol — progressive ladders experiment

This document freezes the next validation cycle for `experiment/progressive-ladders` before its results are inspected.

The objective is not to prove that four execution levels or five retrieval levels are correct. The objective is to test whether progressive constraint/retrieval beats the accepted baseline without quality regression, and to learn the smallest useful number and boundary of levels.

## 1. Freeze before running

Before release-quality model calls:

1. commit the candidate and use a clean working tree;
2. record candidate commit, accepted baseline commit, task manifest hashes, scorer/oracle versions, model/harness configuration, and comparator pins;
3. freeze every capped ladder variant before looking at any partial result;
4. do not change Skill text, tasks, scorers, cap definitions, or acceptance thresholds after partial results from the same cycle are visible;
5. if instrumentation is defective, invalidate and rerun the complete affected matrix.

## 2. Gate A — harness self-test

```powershell
pwsh -NoProfile -File benchmarks/run.ps1 -SelfTest
```

Also run the ladder analyzer unit tests:

```bash
python -m unittest benchmarks.test_ladder_analysis
```

A failing self-test blocks benchmark claims.

## 3. Gate B — public regression against accepted baseline

Because `SKILL.md` and `references/` behavior changed, run the complete existing matrix:

```powershell
pwsh -NoProfile -File benchmarks/run.ps1 `
  -Profile full `
  -Runs 3 `
  -Workers 3 `
  -BaselineRef <accepted-v1.2-commit> `
  -IncludeBaseline `
  -RequireStableRanking
```

Acceptance order:

1. correctness/safety non-regression;
2. build/reachability non-regression;
3. only then efficiency.

Historical public cases are regression evidence only.

## 4. Gate C — ladder boundary calibration

Follow [`LADDER_EVOLUTION.md`](LADDER_EVOLUTION.md).

### Execution axis

Freeze and run caps:

```text
E0
E1
E2
E3
adaptive
```

Allow normal retrieval so retrieval is not the intentional bottleneck.

### Retrieval axis

Freeze and run caps:

```text
R0
R1
R2
R3
R4
adaptive
```

Allow normal execution so execution is not the intentional bottleneck.

Use at least `n=3` determinate repetitions for a claimed minimum-sufficient rung. Do not force a minimum for unstable/indeterminate cells.

Required output per task/axis:

- minimum sufficient level;
- adaptive level;
- adaptive quality result;
- exact / over-escalation / under-escalation / quality-failure / inconsistent classification;
- tokens, model time, tool calls, references loaded when available.

Aggregate with:

```bash
python benchmarks/ladder_analysis.py observations.jsonl --output ladder-report.json
```

## 5. Gate D — held-out boundary evidence

The strongest architecture claim requires tasks not consulted while writing the new Skill.

Minimum first held-out target:

- at least 20 real coding tasks;
- include trivial known-target edits;
- local uncertainty that should stop at E1/R1;
- unknown-root-cause bugs;
- risky implementation boundaries;
- relationship-heavy cross-file navigation;
- cases where repo-wide or external evidence is genuinely necessary;
- executable verification whenever possible;
- same fixed model/harness for baseline and candidate;
- at least three paired repetitions for publication-quality claims.

## 6. Boundary acceptance criteria

Do not accept a new escalation rule because classification accuracy improved alone. It must preserve delivered quality on real tasks.

### Tighten a boundary when

- repeated over-escalation occurs;
- the lower rung quality-qualifies on the same mechanism;
- the higher rung adds material tokens/time/context/process;
- tightening does not create a held-out quality regression.

### Relax a boundary when

- repeated under-escalation occurs;
- a higher capped rung quality-qualifies;
- the blocker can be recognized from evidence available before failure;
- the new trigger generalizes beyond task nouns.

### Merge/remove a level when

- it is rarely or never minimum sufficient across a varied held-out set;
- bypassing it does not create a material quality cliff;
- its existence adds routing/context/process cost or confusion.

### Split a level when

- repeated failures form two stable behavior clusters;
- an observable pre-action condition separates the clusters;
- the split reduces both under- and over-escalation on held-out tasks.

## 7. Combined-stack benchmark remains required

Before claiming Practical Coding is experimentally superior to installing Ponytail and Superpowers together, keep the arm:

```text
no-skill
Ponytail
Superpowers
Ponytail + Superpowers
Practical Coding
```

Measure quality first, then total/uncached input, output/reasoning tokens, model time, tool calls, module/reference loads, unnecessary process, missed escalation, LOC, and build/reachability.

The hypothesis remains about integrated control cost, not about either upstream project being intrinsically bad.

## 8. Failure discipline

When a failure appears:

1. save the complete run first;
2. classify infrastructure vs scorer/oracle defect vs stochastic behavior vs genuine Skill behavior;
3. record repeated mechanisms under `evolution/patterns/` only after independent evidence;
4. create the proposed change under `evolution/experiments/` before rerunning validation;
5. never add case-specific nouns merely to turn a public cell green;
6. preserve a rejected experiment and its lesson under `evolution/rejected/`.

## 9. Merge gate for this exploration branch

Do not merge the progressive architecture into `main` until:

- existing regression harness passes the quality gate;
- ladder analyzer/tests pass;
- execution and retrieval over/under-escalation are reported separately;
- a held-out task population has tested the boundaries;
- any proposed level merge/split is evidence-backed;
- README claims are rewritten to match the new evidence rather than carrying forward v1.2 numbers as v1.3 proof.

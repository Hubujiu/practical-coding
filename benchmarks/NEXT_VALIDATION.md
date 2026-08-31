# Next validation protocol — progressive capability tree

This document freezes the next validation cycle for `experiment/progressive-ladders` before results are inspected.

The objective is to test whether the tree improves quality-qualified routing and context cost—not to prove that the current number of depths or leaves is correct.

## 1. Freeze before running

Record candidate commit, accepted baseline commit, no-skill configuration, task manifest hashes, scorer/oracle versions, model/harness configuration, comparator pins, depth caps, capability-path ablations, and repetition count before inspecting partial results.

If instrumentation is defective, invalidate and rerun the complete affected matrix.

## 2. Gate A — harness self-test

```powershell
pwsh -NoProfile -File benchmarks/run.ps1 -SelfTest
```

Also run:

```bash
python -m unittest benchmarks.test_ladder_analysis
```

A failing self-test blocks benchmark claims.

## 3. Gate B — public regression

Run the complete existing matrix against the accepted baseline and retain a no-skill reference point.

```powershell
pwsh -NoProfile -File benchmarks/run.ps1 `
  -Profile full `
  -Runs 3 `
  -Workers 3 `
  -BaselineRef <accepted-commit> `
  -IncludeBaseline `
  -RequireStableRanking
```

Interpret in order: correctness/safety → build/reachability → routing sufficiency → efficiency.

Historical public cases are regression evidence only.

## 4. Gate C — depth calibration

Execution caps:

```text
E0 Direct
E1 Probe
E2 Root
E3 Leaf
adaptive
```

Retrieval caps:

```text
R0 Target
R1 Local
R2 Specialized
R3 Bounded exhaustive
adaptive
```

R2 permits the appropriate specialized branch (Structural or External); R3 permits bounded exhaustive repository discovery. External evidence is not an R4 successor.

### Axis-labeling rule

Retrieval and execution must be calibrated independently:

- finding/reading source, caller, reference, sibling, contract, implementation, or configuration changes R-depth only;
- E1 requires a cheap executable probe: reproduce one behavior, exercise one path, falsify one concrete hypothesis, or run one focused check that determines the next action.

A case that needs structural discovery but no extra execution reasoning should be allowed to settle at `E0/R2`. Do not manufacture an E1 step merely because retrieval expanded.

Use at least `n=3` determinate repetitions for a claimed minimum-sufficient depth.

Aggregate depth observations with:

```bash
python benchmarks/ladder_analysis.py observations.jsonl --output ladder-report.json
```

Adaptive rows should record benchmark-only `capability_path` and `references_loaded` when instrumentation can do so mechanically.

## 5. Gate D — capability-path ablation

For each specialist family being claimed, freeze a minimal matrix before running:

```text
parent-only
parent + claimed leaf
candidate adaptive tree
```

Optionally include one plausible sibling as a routing-confusion control; do not brute-force every leaf.

Initial families:

- diagnosis with security/state/compatibility/performance causes;
- engineering with security/state/compatibility/performance guarantees;
- structural review/refactor for `quality`;
- material visual/interface delivery for `interface`.

Required path metrics:

- unnecessary root load;
- unnecessary leaf load;
- missed root/leaf;
- branch confusion;
- path exactness;
- quality and cost delta of claimed leaf vs parent-only.

A leaf is not accepted because its prose is plausible. It must earn its cost on the population it claims to cover.

## 6. Gate E — held-out evidence

Minimum first held-out target:

- at least 20 real coding tasks across multiple repositories;
- trivial known-target edits expected to stop at `E0/R0`;
- retrieval-only local discovery expected to stop at `E0/R1`;
- retrieval-only structural mapping expected to permit `E0/R2` when execution remains simple;
- one-probe execution uncertainty expected to require E1 without automatically requiring deeper retrieval;
- unexplained failures;
- unresolved contract/invariant changes;
- specialist security/state/compatibility/performance cases;
- substantive quality/refactor and interface cases where those leaves are actually material;
- structural and external retrieval cases;
- at least one bounded exhaustive repository claim;
- executable verification whenever possible;
- at least three paired repetitions for publication-quality claims.

## 7. Real-project experience gate

Record routing mistakes, repeated user corrections, and expensive dead ends using `evolution/EXPERIENCE_SCHEMA.md`.

Do not convert one real-project anecdote directly into Skill wording. Consolidate repeated mechanisms into `evolution/wiki/`, then freeze a new experiment.

## 8. Combined-stack and specialist comparisons

Keep the broad historical arm when testing the integrated-control hypothesis:

```text
no-skill
Ponytail
Superpowers
Ponytail + Superpowers
Practical Coding
```

For specialist leaves, also consider narrower expert comparators when relevant (for example focused security/review/design skills). Do not interpret a specialist win as a universal architecture win.

## 9. Failure discipline

1. save the complete run first;
2. classify infrastructure, scorer/oracle, stochastic, routing, or genuine capability failure;
3. create/attach an experience receipt;
4. consolidate repeated mechanisms in the evolution wiki;
5. freeze the proposed change under `evolution/experiments/` before rerunning;
6. never add benchmark-specific nouns merely to turn public cells green;
7. preserve rejected experiments and lessons.

## 10. Merge gate

Do not merge this experiment into `main` until:

- existing regression harness passes quality gates;
- ladder analyzer/tests pass;
- execution/retrieval over- and under-escalation are reported separately;
- E1 Probe is demonstrably separated from R1/R2 source discovery in case labeling and adaptive traces;
- specialist parent-vs-leaf ablations exist for claimed nodes;
- unnecessary/missed leaf and branch-confusion rates are reported;
- held-out tasks test changed boundaries;
- README claims are rewritten to match fresh evidence rather than historical numbers.
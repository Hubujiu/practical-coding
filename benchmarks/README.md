# Practical Coding benchmark chain

This experimental branch keeps the existing public regression harness and adds evaluation for **progressive execution/retrieval depth plus capability-path routing**.

Historical v1.0–v1.2 results remain evidence for the Skill versions that produced them. They are not evidence that the new capability tree is better until fresh runs are completed.

## Three benchmark questions

1. **Does the Skill produce a correct, safe, reachable result?**
2. **Did it pay for more process/context than the result required?**
3. **When it went deep, did it load the right capability root/leaf?**

Existing Delivery, Decision, Debug, Router, Native Behavior, and Navigation ablation suites preserve regression coverage. The new protocol calibrates depth and tree routing.

## Candidate depth model

Execution:

```text
E0 Direct
E1 Focused
E2 Capability root
E3 Specialist leaf
```

Retrieval:

```text
R0 Target
R1 Local
├─ R2 Structural
├─ R2 External contract
└─ R3 Bounded exhaustive repository
```

For each task/axis, run frozen depth caps and identify the **lowest quality-qualified depth**. For deep task families, also run parent-vs-leaf ablations before claiming that a specialist node earns its context cost.

## Primary metrics

Depth metrics:

- `over_escalation`;
- `under_escalation`;
- `minimum_sufficient_counts`;
- cost at each quality-qualified cap.

Tree metrics from benchmark instrumentation:

- selected `capability_path`;
- references loaded;
- unnecessary root/leaf loads;
- missed root/leaf;
- branch confusion;
- path exactness on frozen ablation sets.

The node count is itself under test.

## Baselines

Every release-quality cycle should retain:

```text
no-skill
accepted prior Practical Coding
candidate Practical Coding tree
```

Add Ponytail, Superpowers, Addy-style expert skills, or other specialist skills only where the comparison answers a real family-specific question. A universal pack is not automatically a meaningful comparator for every task.

## Analyze aggregated depth observations

```bash
python benchmarks/ladder_analysis.py observations.jsonl
```

or:

```bash
python benchmarks/ladder_analysis.py observations.jsonl --output ladder-report.json
```

Adaptive rows may include `capability_path` and `references_loaded`; the analyzer summarizes them alongside depth errors. Parent-vs-leaf qualification still follows the frozen ablation protocol in `LADDER_EVOLUTION.md`.

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

1. correctness and safety;
2. build/reachability;
3. depth/path sufficiency;
4. then tokens, model time, tool calls, LOC, and context/reference cost.

A cheap failure cannot beat a correct result, and a specialist leaf is not useful merely because it sounds expert.

## Regression versus evolution evidence

Public tasks that influenced Skill wording are regression tests. Strong boundary/node claims require held-out tasks and repeated determinate runs.

Real-project experience is valuable calibration evidence but is recorded separately under `evolution/` rather than treated as hidden benchmark proof.

# Practical Coding benchmark chain

This experimental branch keeps the existing public regression harness and adds evaluation for **progressive execution/retrieval depth plus adaptive capability-path routing**.

Historical v1.0–v1.2 results remain evidence for the Skill versions that produced them. They are not evidence that the new capability tree is better until fresh runs are completed.

## Three adaptive benchmark questions

1. **Does the Skill produce a correct, safe, reachable result?**
2. **Did it pay for more process/context than the result required?**
3. **When it went deep, did it load the right capability root/leaf?**

Existing Delivery, Debug, Router, Native Behavior, and Navigation suites preserve adaptive regression coverage. Historical Decision cases may remain for compatibility, but Decision/requirements-interview behavior is now **manual-only** and must not be interpreted as an adaptive routing target.

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

## Primary adaptive metrics

- `over_escalation`, `under_escalation`, `minimum_sufficient_counts`;
- selected `capability_path` and references loaded;
- unnecessary/missed root or leaf;
- branch confusion and path exactness;
- cost at each quality-qualified cap.

## Manual-mode metrics

Manual-only Clarification/Decision are not eligible `capability_path` values. Test them in explicit opt-in cases and add a negative control over ordinary tasks:

- explicit-activation quality/cost delta;
- spontaneous manual-mode activation rate — target **0**.

Do not loosen an adaptive trigger to make a manual-mode benchmark pass.

## Baselines

Every release-quality cycle should retain `no-skill`, accepted prior Practical Coding, and the candidate Practical Coding tree. Add Ponytail, Superpowers, Addy-style expert skills, or other specialist skills only where the comparison answers a real family-specific question.

## Analyze aggregated depth observations

```bash
python benchmarks/ladder_analysis.py observations.jsonl
python benchmarks/ladder_analysis.py observations.jsonl --output ladder-report.json
```

Adaptive rows may include `capability_path` and `references_loaded`; parent-vs-leaf qualification follows `LADDER_EVOLUTION.md`.

## Existing harness commands

```powershell
pwsh -NoProfile -File benchmarks/run.ps1 -SelfTest
pwsh -NoProfile -File benchmarks/run.ps1 -Profile standard -Runs 3 -Workers 3 -RequireStableRanking
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
3. adaptive depth/path sufficiency;
4. then tokens, model time, tool calls, LOC, and context/reference cost.

Public tasks that influenced Skill wording are regression tests. Strong boundary/node claims require held-out tasks and repeated determinate runs. Real-project experience is calibration evidence recorded separately under `evolution/`.
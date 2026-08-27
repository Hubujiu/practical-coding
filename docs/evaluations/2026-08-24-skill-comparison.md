# Practical Coding specialist comparison notes

Date: 2026-08-24

Status: controlled calibration/regression evidence, not a universal leaderboard.

## Purpose

Practical Coding is a generalist integration Skill. Its public benchmark therefore compares individual capabilities with relevant specialists instead of combining unrelated tasks into one score:

- Delivery / minimal implementation: Ponytail;
- Debugging and explicit security: Superpowers;
- Decision convergence: Matt Pocock `grilling`;
- Routing/native loading: Practical-owned integration regressions.

The current public release is **v1.0**. Compact release aggregates are in [`../../benchmarks/results/v1.0/`](../../benchmarks/results/v1.0/).

## Current headline results

| Capability | Practical | Comparator | Interpretation |
|---|---:|---:|---|
| Delivery | 96.3% | Ponytail 100% | Ponytail retains build/LOC advantage; Practical is cheaper but not quality-gate qualified |
| Debug | 90.0% | Superpowers 83.3% | Practical quality-qualified and materially more efficient in this harness |
| Explicit security | 100% safe | Superpowers 100% safe | Equal observed safety; Practical uses less measured compute/process cost |
| Decision | 100% | grilling 94.4% | Practical leads quality; cost is a trade-off |
| Router | 95.2% | expected route | Public regression evidence |
| Native behavior | 96.7% | route/load contract | Confirms selective reference loading in real Skill execution |

## Why individual specialist comparisons are not enough

These results answer whether Practical can retain useful specialist behavior. They do not by themselves prove the project's integration hypothesis.

The missing comparison is:

```text
Ponytail + Superpowers installed simultaneously
```

This matters because both Skills have broad activation semantics. The question is not whether either project is good in isolation; the question is whether two independent general coding/process policies create extra context/process cost or ambiguous arbitration compared with Practical's single event router.

The combined arm is explicitly required by [`../../benchmarks/NEXT_VALIDATION.md`](../../benchmarks/NEXT_VALIDATION.md). Until that run exists, statements about Practical versus the combined stack must be presented as architecture/hypothesis, not measured superiority.

## Evidence discipline

Use these rules when citing the results:

- do not call Decision/Debug results official upstream benchmarks;
- do not turn a one-cell difference into a universal claim;
- report correctness/safety/build before efficiency;
- public regression cases that influenced Skill wording are not held-out generalization evidence;
- never merge specialist suites into one universal score.

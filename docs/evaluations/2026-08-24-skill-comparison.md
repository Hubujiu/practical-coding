# Practical Coding specialist comparison notes

Date: 2026-08-24

Status: controlled calibration/regression evidence, not a universal leaderboard.

## Purpose

Practical Coding is a generalist integration Skill. Its public benchmark therefore compares individual capabilities with relevant specialists instead of combining unrelated tasks into one score:

- Delivery / minimal implementation: Ponytail;
- Debugging and explicit security: Superpowers;
- Decision convergence: Matt Pocock `grilling`;
- Routing/native loading: Practical-owned integration regressions.

The current public release is **v1.1**. Compact release aggregates and the updated comprehensive report are in [`../../benchmarks/results/v1.1/`](../../benchmarks/results/v1.1/). The v1.0 directory remains historical evidence.

## Current headline results

| Capability | Practical | Comparator | Interpretation |
|---|---:|---:|---|
| Delivery | 100% (27/27) | Ponytail 96.3% historical arm | Current Practical passed correctness, safety, and build; cross-run rather than a new paired scorecard |
| Debug | 96.7% (29/30) | Ponytail 93.3% historical arm | Correctness 100%; one localized repair missed a sibling caller |
| Decision | 100% (18/18) | role-dependent | Current two-turn convergence regression passed |
| Router | 100% (114/114) | expected route | Expanded five-route public regression evidence |
| Native behavior | 100% (54/54) | route/load contract | Confirms exact selective loading in real Skill execution |
| Applicable total | 99.6% (242/243) | — | Three affected-surface reruns, not one atomic manifest |

## Combined-Skill evidence

The historical Cursor matrix ran all 15 non-empty prompt-inlined subsets of Practical, Ponytail, Superpowers, and grill-me. It found useful interference signals: Practical + Ponytail reached 100% Delivery, adding Superpowers often hurt Delivery, and all four reached 100% Debug at higher cost. Current v1.1 Practical figures supersede that matrix's Practical-current rows.

This still does not prove universal behavior for actual plugin installation. The comparator arms used runner v1.6, current Practical used v1.8/v1.9, and prompt inlining is not every host's plugin lifecycle. The exact real-install comparison remains in [`../../benchmarks/NEXT_VALIDATION.md`](../../benchmarks/NEXT_VALIDATION.md).

## Evidence discipline

Use these rules when citing the results:

- do not call Decision/Debug results official upstream benchmarks;
- do not turn a one-cell difference into a universal claim;
- report correctness/safety/build before efficiency;
- public regression cases that influenced Skill wording are not held-out generalization evidence;
- never merge specialist suites into one universal score;
- do not turn the cross-run comparator rows into a paired v1.9 scorecard.

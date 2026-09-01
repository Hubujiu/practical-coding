# EXP-20260902 — Manual-boundary discriminator

Status: **rejected after paired n=1**

## Observation

The complete paired leaf artifact `benchmark-results/tree-final-ad2987c-20260902` put adaptive and frozen v1.5 at 45/45. Existing tasks did not exercise the architectural difference between v1.5 automatic Decision routing and the candidate's explicit-only Decision mode, so strict quality superiority was unmeasurable at the ceiling.

## Hypothesis

A real compatibility-boundary task that explicitly asks for only the minimum blocking question, while forbidding option comparison/recommendation/implementation planning, should distinguish the contracts:

- current Skill asks one question in Core without loading manual Decision;
- v1.5 may automatically load `references/decision.md`, which itself requires recommendation/trade-off analysis;
- no-skill remains a neutral comparator.

Score both visible decision-analysis leakage and observed v1.5 Decision-reference loading. Apply legacy manual-reference discipline symmetrically: explicit Decision tasks may load it; automatic tasks may not.

## Acceptance

Positive/negative deterministic tests must pass. Then run only the new case as a paired n=1 discriminator. Keep the case only if adaptive passes and the result exposes a real contract difference rather than a lexical accident. If retained, rerun the complete current-only suite at n=1 before any final n=3.

## Result

`benchmark-results/tree-discriminator-minimum-question-n1-20260902` completed 6/6 determinate cells. Adaptive, frozen v1.5, and no-skill all passed, and v1.5 did not load Decision. The case therefore did not distinguish the contracts. The case and its provisional scorer expansion were removed; the artifact and this rejection remain as evidence.

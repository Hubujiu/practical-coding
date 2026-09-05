# EXP-20260901 — Recommendation inflection normalization

Status: **frozen before scorer edit**

## Observation

The complete leaf-topology n=1 run at `benchmark-results/tree-delivery-n1-leaves-retry-20260901` was 58/58 determinate. All three capability ceilings passed every automatic task, all traces/manual contracts passed, and the sole adaptive failure began `Recommend a one-release compatibility alias` before comparing both options and stating the strongest trade-off.

The recommendation evidence group accepted `Recommendation` but not the ordinary verb `Recommend`.

## Hypothesis

Recommendation evidence is an act, not a required part of speech. Adding the verb stem `recommend` preserves the independent requirements for both options, a chosen option, and its strongest downside while eliminating a lexical false negative.

## Acceptance

Add a positive verb-form test and retain the existing missing-trade-off negative. Then rerun the complete leaf-topology current-only matrix at n=1 in a fresh directory.

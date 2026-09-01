# EXP-20260902 — Retired reference isolation

Status: **frozen before runtime-surface edit**

## Observation

The paired n=3 artifact `benchmark-results/tree-final-67f2f5c-20260901` and the n=1 artifact `benchmark-results/tree-delivery-n1-observed-trace-20260902` each contained an adaptive run that loaded a depth-2 reference removed from the active topology. Parent router text and the topology manifest both declared Debugging/Implementation leaves, but the retired files remained discoverable under the runtime `references/` directory.

## Hypothesis

A rejected automatic node must leave the runtime discovery surface, not merely the manifest. Remove the four unearned depth-2 documents from `references/`; preserve their content through Git history, experiments, raw receipts, and benchmark artifacts. Do not merge their specialist prose back into Core or the leaf parents.

## Acceptance

- no retired depth-2 document remains under runtime `references/`;
- topology and parent nodes still define Debugging/Implementation as leaves;
- deterministic tests prove unknown/retired reference observations are invalid;
- a fresh complete current-only n=1 has all cells determinate, adaptive 15/15, trace 15/15, manual 2/2, and zero spontaneous manual activation.

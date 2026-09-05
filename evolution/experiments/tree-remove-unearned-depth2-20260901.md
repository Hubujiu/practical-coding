# EXP-20260901 — Remove unearned depth-2 nodes

Status: **frozen before topology/runtime edit**

## Observation

The complete paired n=3 artifact at `benchmark-results/tree-final-eca9a09-20260901` found no depth-2 staged node in any minimum-sufficient set. After the general oracle correction, the fresh current-only n=1 artifact at `benchmark-results/tree-delivery-n1-outcome-semantics-20260901` passed every one of 106 cells and again found zero marginal lift and zero minimum-sufficient tasks for all four staged depth-2 nodes.

The paired artifact still showed `Debugging` or `Implementation` as the minimum-sufficient depth for `ca-avif-stall-evidence`, so the seed root children remain. Only their unearned staged descendants are in scope.

## Hypothesis

Removing `dynamic-evidence`, `security-boundary`, `migration-compatibility`, and `state-concurrency` from the active topology, and keeping Debugging/Implementation as leaves, will preserve delivered quality and manual-mode discipline while reducing unnecessary disclosure and capability cells.

The specialist documents remain historical experiment artifacts in Git history; no sibling is merged into Core and no task-specific wording is added.

## Acceptance

- topology contains only Core, Debugging, and Implementation;
- Debugging and Implementation contain no active descendant routes;
- complete current-only n=1 is determinate and passes 15/15 adaptive tasks, all traces, both explicit manual tasks, and zero spontaneous manual activations;
- only after that candidate freezes may a fresh paired n=3 run be used for delivery comparison.

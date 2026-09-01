# EXP-20260902 — Collapse unearned automatic leaves into Core

Status: **frozen before runtime/topology edit**

## Observation

The complete paired n=3 artifact `benchmark-results/tree-final-ad2987c-20260902` passed every adaptive and frozen-v1.5 quality cell (45/45 each), all adaptive traces/manual contracts, and beat no-skill at 45/45 versus 44/45. It did not establish strict quality superiority because both Skill versions hit the benchmark ceiling.

Capability ablation was nevertheless stable: Core passed 39/39 automatic cells. Neither Debugging nor Implementation was minimum-sufficient for any task, and adaptive selected a non-minimum child in 13/39 automatic cells. Adaptive used fewer tools than v1.5 (7.60 versus 8.27 mean), but used more tokens and time.

## Hypothesis

Collapse Debugging and Implementation into the already-sufficient Core by removing both automatic child routes and their runtime reference files. Preserve explicit manual Decision/Clarification and orthogonal retrieval. Do not copy leaf prose into Core.

At equal delivered quality, the smaller automatic surface should reduce routing/context/tool cost enough to produce a better comparable report than frozen v1.5. If quality drops or costs do not improve coherently, reject the collapse.

## Acceptance

- Core is the only automatic node in runtime docs and topology;
- all deterministic gates pass;
- complete current-only n=1 is fully determinate with adaptive 15/15, Core ceiling 13/13, trace/manual discipline perfect;
- only then run paired n=3;
- delivery requires adaptive quality no worse than v1.5 and a clear net efficiency improvement at equal quality; the previously frozen strict-quality rule is reported as ceiling-blocked rather than silently rewritten.

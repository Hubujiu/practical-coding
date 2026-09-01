# EXP-20260902 — Observed trace fallback

Status: **frozen before harness edit**

## Observation

The complete n=1 artifact at `benchmark-results/tree-delivery-n1-evidence-identity-outcome-20260902` had all three capability ceilings at 13/13. Its sole adaptive failure was a complete, evidence-backed manual Decision answer that actually read `references/manual/decision.md` but omitted the benchmark-only `TREE_TRACE` footer.

The footer is instrumentation, not delivered task behavior. A stochastic formatting omission should not erase observed reference-use evidence, but recovery must not permit inactive or retired references.

## Hypothesis

When and only when the reported trace is absent, derive a fallback trace from actual tool-command reference reads:

- active automatic references determine the deepest valid local path;
- a uniquely observed manual reference determines manual mode;
- repository commands imply targeted retrieval;
- any observed Practical Coding reference outside the active automatic/manual/navigation surface invalidates the recovered trace.

Explicit reported traces remain authoritative and are not rewritten. This makes instrumentation robust while preserving detection of the known retired-node leak.

## Acceptance

Unit tests must prove correct automatic/manual recovery and rejection of a retired reference. Then rerun the complete current-only n=1 matrix in a fresh directory. Retired file removal remains a separate runtime-isolation iteration.

# EXP-20260831 — Restore event routing and policy-based retrieval

## Evidence / pattern

The progressive-tree experiment did not justify E2, R2/R3 runtime labels, or specialist leaves. Its supported mechanisms can be expressed with fewer runtime concepts. Accepted v1.2 evidence already demonstrated a small Debugging/Decision/Implementation router with retrieval kept orthogonal.

## Hypothesis

Replacing numeric depth/path tracking with three observable unresolved events will restore routing compatibility and improve delivered quality while reducing context and branch confusion. Keeping retrieval as a cheapest-sufficient capability policy will preserve structural/exhaustive retrieval without forcing the agent to classify a numeric depth. Requirements interviewing remains explicit-only; genuinely open material implementation choices return to Decision.

## Change

- Remove E0-E3 and R0-R3 as runtime states and emitted benchmark contracts.
- Route exactly one of Debugging, Decision, or Implementation only for a present unresolved event.
- Restore top-level `references/decision.md` and `references/implementation.md`.
- Fold shared specialist guarantees into the owning general module; remove specialist runtime leaves.
- Keep `references/navigation.md` as the optional detailed retrieval procedure, with Codebase Memory opt-in and source verification.
- Keep `references/manual/clarification.md` explicit-only.

## Expected result

Quality gates first:

- no Delivery correctness/safety/build regression;
- restore Debug shared-boundary behavior;
- Router and Native Behavior use the same three reasoning events and orthogonal retrieval contract as the runtime;
- held-out real-task quality remains at least 18/22 stable at final n=3;
- zero spontaneous clarification/interview activation;
- lower branch/path confusion and no requirement to emit numeric depth labels.

Cost should be unchanged or lower because at most one general reasoning reference is loaded and specialist leaves disappear.

## Frozen validation

- Iteration model/harness: `gpt-5.6-luna`, medium, n=1.
- Fast gates: public Router/Native Behavior plus focused Delivery/Debug; current-only held-out quality and manual negative control.
- Final gate only after n=1 acceptance: full current-only public profile and at least 20 held-out real tasks at n=3.
- Historical comparator: accepted v1.2 reports only, non-paired unless a later explicit scope change authorizes rerunning prior arms.
- Do not change runtime wording from individual failing case nouns; new tests must encode a reusable mechanism and be frozen before inspecting candidate output.

## Result

### Iteration 1 — `67aad6c`, n=1

- Public full current-only: Delivery 18/18, Debug 13/14, Decision 7/10, Router 30/38, Native Behavior 17/18.
- Held-out current-only: 21/22 mechanical passes, 22/22 determinate, 0 spontaneous requirements-interview activation, 22/22 valid traces, 10/22 exact reasoning+retrieval traces.
- The held-out miss was a tokenization defect: the answer proved the model-interceptor boundary but the evidence group accepted only unspaced `ModelInterceptor`.
- The Debug miss exposed a contradictory oracle: the prompt required preserving sibling cache semantics while the scorer required changing them. The candidate preserved the stated sibling contract.
- Four Router misses were Direct tasks incorrectly escalated to Implementation despite already-settled target/boundary/check evidence.
- Native Debugging delivered a correct shared-boundary fix but did not load the required module before diagnostic source work.
- Decision outputs converged but lacked the stable `Recommendation:` structure required for compact user-visible comparison.

Iteration 2 changes are limited to these reusable mechanisms: pre-source event routing, explicit Direct settled-boundary protection, stable Decision output structure, retrieval instrumentation definitions, and scorer/oracle corrections. No benchmark case noun is added to runtime text.

### Iteration 2 — `bacb34e`, n=1

- Public focused full-profile surfaces: Debug 14/14, Decision 10/10, Native Behavior 18/18, Router 33/38.
- Router reasoning was correct in 36/38; two read-only/source-discovery tasks still over-routed to Implementation. Three remaining failures were retrieval granularity disagreements, not reasoning-module or delivered-quality failures.
- Held-out: 19/22 mechanical passes, 0 spontaneous requirements interviewing, 21/22 valid traces, 18/22 exact event+retrieval traces.
- Two held-out failures were executable-command oracle defects: the scorer required both `mvn` and `mvnw`, or both `npm` and `vitest`, rather than accepting equivalent project runner entrypoints.
- The remaining security answer again established the rejection boundary; the redundant exact type-name evidence group was not material to the task contract.
- One interface planning task was mechanically inherited as Implementation from the rejected leaf tree, although no code change or unresolved implementation boundary was requested. The event-router oracle is corrected to Direct before final validation.

Iteration 3 therefore changes only the general Direct/source-discovery distinction plus benchmark command/evidence-group semantics. The broad quality modules already pass their n=1 gates.

### Iteration 3 focused result — `313e2bb`, n=1

Both source-discovery controls still over-routed to Implementation. The cause was a contradictory candidate rule: `unmapped coherent change surface` appeared as an Implementation trigger even though the Direct and Retrieval sections said unknown paths/callers alone are retrieval. The earlier phrase won the first-match routing check.

This phrase is an incorrect improvement and is removed. Implementation now requires an unresolved governing contract/risk/evidence boundary, or a coordinated change whose required joint contract is not established. Read-only mapping is explicitly Direct plus Retrieval.

### Final n=1 gate — `8669827`

- The two repeated retrieval-only controls both routed Direct with the expected retrieval scope.
- Five affected held-out controls passed 5/5 quality, 5/5 valid traces, 5/5 exact reasoning+retrieval, and zero spontaneous requirements interviewing.
- Combined with Iteration 2, all Delivery, Debug, Decision, and Native Behavior n=1 quality surfaces passed; Router residuals were retrieval-granularity differences rather than module-selection or delivered-quality regressions.

The runtime wording is frozen. Documentation and dead rejected-runner paths are being cleaned before the complete n=3 release matrix; no further runtime tuning is allowed without returning to a new n=1 experiment.

## Decision

Pending.

## Follow-up

If this fails, preserve the failure mechanism here or under `evolution/rejected/` before starting another runtime change.

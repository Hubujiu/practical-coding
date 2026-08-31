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

Pending.

## Decision

Pending.

## Follow-up

If this fails, preserve the failure mechanism here or under `evolution/rejected/` before starting another runtime change.


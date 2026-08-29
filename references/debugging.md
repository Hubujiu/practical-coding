# Debugging Rigor

Load this module only when an observed or reported failure, regression, incorrect behavior, or failed verification exists and its cause is not yet evidenced. Debugging is an execution escalation profile, not a task category or a mandatory stage for every bug report.

If the cause is already established by fresh evidence and the safe fix is known, stay Direct with the Core.

## Evidence First

- Reproduce the symptom when practical, or collect the smallest useful evidence when reproduction is unavailable.
- Trace the real execution path backward from the symptom to the earliest incorrect state.
- Distinguish observed facts from hypotheses.
- Test one meaningful hypothesis at a time instead of changing several possible causes together.

## Fix the Cause

- Prefer the narrowest fix that corrects the root cause and preserves existing contracts.
- Do not patch a downstream symptom when an earlier incorrect state is identifiable and fixable.
- Treat universal wording such as "never," "every," or "no X can" as one contract across current mutation paths. Before editing a reported caller, inspect its delegated helper and nearest sibling caller; if both can violate that contract, fix the invariant once in their common state-mutation or parsing helper. Patch only the reported adapter when evidence shows the helper intentionally owns a different lower-level contract. For a shared invariant, the smallest coherent fix means that common boundary, not the fewest edited lines or the named caller.
- Do not use broad retries, catches, fallbacks, default values, or defensive branches to hide an unexplained failure.
- Add temporary logging or instrumentation only when it produces evidence needed to distinguish hypotheses.

Judge a fix by the delivered code, not by whether it followed a named debugging or TDD ritual. A successful fix:

- removes the earliest incorrect state that explains the symptom;
- preserves the intended behavior of the reported path and other callers of the repaired boundary;
- restores a violated security, permission, integrity, accessibility, compatibility, or explicit project constraint when that constraint is the diagnosed cause, at the shared boundary every affected caller passes through;
- changes no unrelated behavior and introduces no speculative fallback, extra validation, accessibility chrome, or refactor;
- is no larger than the diagnosed cause requires.

## Stay in Scope

- Do not expand beyond the diagnosed contract into a repo-wide search for unrelated defects.
- Do not write tests merely because debugging occurred or because the repaired logic is non-trivial. Use the cheapest reproduction or focused check that can falsify the fix; add a durable targeted test only when regression risk, project requirements, or a still-unresolved evidence boundary justifies its lasting value.
- If diagnosis exposes a material choice that changes the next action or an unresolved execution boundary that makes the fix unsafe, return that blocker to the root. Do not load another Practical Coding reference from this module.

## Exit

- Verify that the original symptom is resolved with fresh evidence appropriate to the failure.
- Exercise the nearest shared caller or boundary when the root cause could affect more than the named symptom.
- Remove temporary diagnostic instrumentation unless it has durable operational value.
- Report remaining uncertainty rather than hiding it behind additional defensive code.
- Return to the Core. Do not escalate to Implementation merely because Debugging occurred; escalate only if an unresolved material execution boundary still blocks safe action.

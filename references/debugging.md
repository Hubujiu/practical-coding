# Debugging

Load this module only for an observed or reported failure, regression, incorrect behavior, or failed verification.

## Evidence First

- Reproduce the symptom when practical, or collect the smallest useful evidence when reproduction is unavailable.
- Trace the real execution path backward from the symptom to the earliest incorrect state.
- Distinguish observed facts from hypotheses.
- Test one meaningful hypothesis at a time instead of changing several possible causes together.

## Fix the Cause

- Prefer the narrowest fix that corrects the root cause and preserves existing contracts.
- Do not patch a downstream symptom when an earlier incorrect state is identifiable and fixable.
- Place an invariant at the narrowest shared state-mutation or parsing boundary that every affected caller passes through. Before editing a named failing caller, inspect the helper it delegates to and the helper's nearest sibling caller; if both can produce the invalid state, repair the shared boundary.
- Do not use broad retries, catches, fallbacks, default values, or defensive branches to hide an unexplained failure.
- Add temporary logging or instrumentation only when it produces evidence needed to distinguish hypotheses.

Judge a fix by the delivered code, not by whether it followed a named debugging or TDD ritual. A successful fix:

- removes the earliest incorrect state that explains the symptom;
- preserves the intended behavior of the reported path and other callers of the repaired boundary;
- restores a violated security, permission, integrity, accessibility, compatibility, or explicit project constraint when that constraint is the diagnosed cause, at the shared boundary every affected caller passes through;
- changes no unrelated behavior and introduces no speculative fallback, extra validation, accessibility chrome, or refactor;
- is no larger than the diagnosed cause requires.

## Stay in Scope

- Scope the fix by the violated contract or invariant, not merely by the function named in the report. If the requirement is universal across a resource or state (for example, it must never enter an invalid state), inspect every current mutation path through the nearest shared boundary; a sibling caller that can violate the same invariant is part of the reported defect.
- Do not expand beyond that contract into a repo-wide search for unrelated defects.
- Do not write tests merely because debugging occurred or because the repaired logic is non-trivial. Use the cheapest reproduction or focused check that can falsify the fix; add a durable targeted test only when `verification.md`, regression risk, or project requirements justify its lasting value.
- If diagnosis reveals a material design or dependency decision, load `decision.md` before making that choice.

## Exit

- Verify that the original symptom is resolved with fresh evidence appropriate to the failure.
- Exercise the nearest shared caller or boundary when the root cause could affect more than the named symptom.
- Remove temporary diagnostic instrumentation unless it has durable operational value.
- Report remaining uncertainty rather than hiding it behind additional defensive code.

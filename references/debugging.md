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
- Do not use broad retries, catches, fallbacks, default values, or defensive branches to hide an unexplained failure.
- Add temporary logging or instrumentation only when it produces evidence needed to distinguish hypotheses.

## Stay in Scope

- Diagnose the reported or observed failure; do not turn debugging into a repo-wide search for unrelated defects.
- Do not write tests merely because debugging occurred. Add a targeted test only when `verification.md` or project requirements justify its lasting value.
- If diagnosis reveals a material design or dependency decision, load `decision.md` before making that choice.

## Exit

- Verify that the original symptom is resolved with fresh evidence appropriate to the failure.
- Remove temporary diagnostic instrumentation unless it has durable operational value.
- Report remaining uncertainty rather than hiding it behind additional defensive code.

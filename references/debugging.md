# Debugging

**Tree depth: 1**

Load this node only from its parent when an observed or reported failure, regression, incorrect behavior, or failed verification still lacks an evidenced cause.

## Evidence First

- Reproduce the symptom when practical, or collect the smallest useful evidence when reproduction is unavailable.
- Trace the real execution path backward from the symptom to the earliest incorrect state.
- Distinguish observed facts from hypotheses.
- Test one meaningful hypothesis at a time instead of changing several possible causes together.

## Fix the Cause

- Prefer the narrowest fix that corrects the root cause and preserves existing contracts.
- Do not patch a downstream symptom when an earlier incorrect state is identifiable and fixable.
- Treat universal wording such as "never," "every," or "no X can" as one contract across current mutation paths. Before editing a reported caller, inspect its delegated helper and nearest sibling caller; if both can violate that contract, fix the invariant once in their common state-mutation or parsing helper.
- When the request names shared behavior, repair the authoritative shared primitive for all current callers. Do not preserve the same defect behind a new per-caller flag or branch unless an established caller contract requires different behavior.
- Do not use broad retries, catches, fallbacks, default values, or defensive branches to hide an unexplained failure.
- Add temporary logging or instrumentation only when it produces evidence needed to distinguish hypotheses.

Judge a fix by delivered behavior. It should remove the earliest incorrect state, preserve other callers of the repaired boundary, restore any violated security, permission, integrity, accessibility, compatibility, or explicit project constraint, and change no unrelated behavior.

## Local Router

**Current status: leaf.** No child capability has yet earned stable parent-versus-child lift across the benchmark evidence.

Resolve debugging work here. Do not route to Decision when diagnosis exposes alternatives. Reuse the established project contract or smallest sufficient reversible option. If a genuinely user-owned choice blocks progress with no safe default, ask the minimum blocking question without loading a Decision module.

A future child may be added here only when repeated debugging failures form an observable pre-load cluster and the child demonstrates stable quality-qualified net lift over this node. Core must not be updated to know that descendant.

## Stay in Scope

- Diagnose the reported failure; do not turn debugging into a repository-wide search for unrelated defects.
- Do not write tests merely because debugging occurred. Use the cheapest reproduction or focused check that can falsify the fix; add a durable test only when regression risk or project requirements justify it.
- If work exposes a genuinely different top-level execution blocker rather than a descendant of Debugging, return that blocker to Core.

## Exit

- Verify the original symptom with fresh evidence.
- Exercise the nearest shared caller or boundary when the repaired invariant serves more than the named symptom.
- Remove temporary diagnostic instrumentation unless it has durable operational value.
- Report remaining uncertainty instead of hiding it behind defensive code.

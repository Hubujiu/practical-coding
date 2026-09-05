# Debugging

**Tree depth: 1**

Enter only when an observed failure has no evidenced cause. A supplied, verified cause needs a fix, not a new investigation.

## Work

1. Reproduce the symptom or collect the smallest discriminating evidence when reproduction is unavailable. Separate observations from hypotheses.
2. Trace the actual path to the earliest incorrect state. Change one causal hypothesis at a time; compare against a nearby working case when useful.
3. Repair the authoritative owner. For a shared invariant, inspect its helper and nearest material caller before editing; do not fix one caller while preserving the same defect behind a flag elsewhere.
4. Verify the original symptom and affected shared boundary. For intermittent failures, use a bounded repeat/race check justified by the failure mechanism. Keep required safety and compatibility guarantees.

Do not hide an unexplained failure with retries, catches, defaults, or unrelated hardening. Remove temporary instrumentation after it has served its purpose. Add durable regression coverage only when the mechanism or project contract requires it; report an unavailable check as unavailable.

## Local Router

This node is a leaf. Timing, async ordering, worker/browser/network and CI evidence stay in this loop. Candidate-caused failures do not reopen routing. Never activate Decision automatically; use settled conventions or ask the minimum blocking user-owned question. Return to Core only for a genuinely different top-level blocker.

## Exit

Return the cause, narrow fix or diagnosis, fresh falsifying check, and remaining uncertainty. Diagnose-only requests authorize no edits. Stop after the requested failure is resolved; do not audit unrelated code.

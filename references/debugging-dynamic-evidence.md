# Dynamic Evidence

**Tree depth: 2**

Load only from Debugging when a live runtime discriminator is required to isolate an otherwise unexplained failure. This is not a generic "debug harder" stage.

## Smallest Feedback Loop

- Reproduce the narrowest version of the symptom with the minimum input and state that still fails.
- Record the exact observable boundary: request/response, event, state transition, worker message, browser action, process exit, timing interval, or CI step.
- Compare one known-good and one known-bad run when available. Change one explanatory variable at a time.

## Instrument the Boundary

- Instrument only the smallest boundary that distinguishes the current hypotheses. Prefer structured values, timestamps, correlation IDs, state/version identifiers, and before/after observations over blanket logging.
- For async behavior, wait for the relevant condition or event rather than adding a fixed sleep. A longer timeout is evidence only when timeout behavior itself is the contract.
- For browser/worker/network/process failures, separate producer time, queue/transport time, consumer time, cancellation, and resource pressure before changing code.
- For environment-only failures, compare only material runtime facts—dependency/runtime version, configuration, process model, filesystem/network capability, or CI command—not the whole environment.

## Fix After Evidence

Do not add retries, caches, fallbacks, sleeps, locks, or larger timeouts until evidence identifies the failure mode they address. Fix the earliest incorrect state or violated boundary with the smallest change.

## Exit

- Re-run the original reproducer and the nearest non-failing neighbor with fresh evidence.
- Remove diagnostic instrumentation unless it is intentionally useful in production.
- Add a durable regression test only when the failure can be reproduced deterministically enough for the test to provide signal.
- Report any runtime dimension that remains unobserved.

## Local Router

**Current status: leaf.** A deeper child requires a new stable failure cluster and parent-versus-child evidence.

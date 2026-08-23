# Verification

Load this module when choosing verification is itself non-trivial. Tests are one form of evidence, not a default deliverable.

## Principle

Choose the cheapest evidence that is strong enough for the change's risk, uncertainty, blast radius, project gates, and user request.

Do not expand verification into open-ended bug hunting or generate tests mechanically for every changed function.

## Evidence Ladder

Prefer the lowest-cost level that provides sufficient confidence:

1. Inspect the focused diff or resulting file for trivial textual or mechanical changes.
2. Render or directly exercise the changed behavior for local UI or behavior changes.
3. Compile, type-check, lint, or run an existing focused check when static evidence is appropriate.
4. Run existing targeted tests covering the changed behavior.
5. Add the smallest targeted automated test when the behavior is important enough that direct evidence is insufficient and the test will provide durable value.
6. Use focused integration or end-to-end verification for cross-boundary behavior where lower levels cannot establish correctness.
7. Run a broad or full suite only when the change surface, project gate, or regression risk justifies it.

## Risk Signals

Stronger evidence is usually justified for changes involving:

- authentication, authorization, secrets, or permissions;
- payments, billing, or irreversible side effects;
- concurrency, locking, ordering, retries, or distributed coordination;
- persistence, migrations, serialization, or data integrity;
- public APIs, compatibility contracts, or shared libraries;
- cross-service or third-party integrations;
- complex algorithms where plausible edge cases are difficult to inspect directly.

These signals raise the verification requirement; they do not automatically require every possible test type.

## Test Quality

When adding a test:

- test externally meaningful behavior or a durable invariant rather than private implementation details;
- keep it focused on the risk or regression being addressed;
- prefer existing test infrastructure and conventions;
- do not add a new testing framework for a small change unless its long-term value clearly justifies the dependency and maintenance cost;
- avoid duplicating the same assertion across multiple test layers without a distinct reason.

## Completion

Claim only what fresh evidence supports. If an appropriate check cannot run because of environment, credentials, unavailable services, or another blocker, state the limitation and the remaining uncertainty.

Red flags before claiming completion:

| Rationalization | Reality |
|---|---|
| "Too simple to verify" | Simple changes still get one direct check: read the diff or render the result. |
| "It compiled / worked before this last edit" | Stale evidence. Re-check the final state with the cheapest sufficient check. |
| "The tests probably still pass" | A guess is not evidence. Run the targeted check or report that you could not. |
| "Verification here would be over-engineering" | This skill trims speculative work, never the evidence for work actually done. |

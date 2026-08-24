# Verification

Load only for `evidence.uncertain`. Produce a bounded evidence plan, then execute it.

## Principle

Map each material claim or risk to the cheapest check that can falsify it. Prefer project gates and existing focused tests; add one durable test only when direct evidence is insufficient. Do not expand into open-ended bug hunting.

Use the lowest sufficient level: diff inspection; direct exercise/render; compile/type/lint; existing focused test; one new focused test; boundary integration test; full suite only for broad surface or a required gate.

For persistence or concurrency, exercise restart/rollback/race behavior and close files, connections, threads, and handles before cleanup. For compatibility, run both old and new callers. For security boundaries, include a valid case and the smallest representative rejection cases, and verify rejection happens before side effects.

## Test Quality

Test externally meaningful behavior or a durable invariant, use existing infrastructure, and avoid duplicate assertions across layers without a distinct reason.

## Completion

Claim only what fresh evidence supports. Re-check after the final edit. If environment, credentials, or services block an appropriate check, report the limitation and remaining uncertainty.

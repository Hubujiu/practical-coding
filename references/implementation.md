# Implementation Rigor

Load this module only when safe execution is blocked by an unknown contract or invariant, an unresolved material risk boundary, or insufficient evidence for a risky material claim. Implementation is an execution escalation profile, not a synonym for "coding" and not a mandatory stage after Debugging.

Material risk boundaries include security or permissions, irreversible side effects, persistence or migration, concurrency or transactions, and compatibility. A risk-related noun does not trigger this profile when the governing boundary, affected surface, and sufficient check are already established; in that case stay Direct with the Core.

Produce only the change map and evidence plan the blocker requires.

## Work Locally

- Identify the authoritative contract or invariant and the minimum producers, consumers, adapters, data, and checks that must move together.
- Read only those paths and their material callers or dependencies; leave nearby cleanup opportunities and unrelated code alone.
- For a risk boundary, identify the smallest authoritative point that owns the guarantee before editing. A single-file change can still need Implementation rigor when the unresolved boundary is material.
- Preserve public compatibility unless the requirement authorizes a break. When migration is required, choose one authoritative internal representation and keep compatibility at the narrowest boundary.
- Match project conventions and make the smallest coherent end-to-end diff.

## Keep Code Small

Reuse existing helpers and patterns. Add an interface, adapter, wrapper, switch, or generic utility only for a demonstrated current boundary. Comments explain intent or constraints code cannot express.

## Match Error Handling to Real Boundaries

Put validation once at the narrowest authoritative boundary. Add retries, fallbacks, broad catches, compatibility layers, or recovery only for a concrete failure mode. Preserve required safety, permission, integrity, and compatibility guarantees in the touched boundary without expanding into unrelated hardening.

## Prove the Change

Map each material claim or risk to the cheapest check that can falsify it, at the lowest sufficient level: diff inspection; direct exercise or render; compile/type/lint; an existing focused test; one new focused test; a boundary integration test; the full suite only for a broad surface or a required gate. Prefer project gates and existing focused tests; add one durable test only when direct evidence is insufficient, and do not expand into open-ended bug hunting or duplicate assertions across layers.

For persistence or concurrency, exercise restart, rollback, or race behavior when relevant and close files, connections, threads, and handles before cleanup. For compatibility, exercise the materially affected old and new callers. For a security or permission boundary, include one valid case and the smallest representative rejection cases, and verify rejection happens before side effects.

Claim only what fresh evidence supports, re-checked after the final edit. "Too simple to verify", "it worked before this last edit", and "the tests probably still pass" are rationalizations, not evidence: run the cheapest sufficient check, or report the limitation and remaining uncertainty when environment, credentials, or services block it.

## Exit

When the governing boundary, affected surface, and sufficient evidence are established, return to the Core and execute the smallest coherent change. Do not keep expanding rigor after its blocker is resolved.

If work exposes a materially different unresolved choice or unexplained failure, return that blocker to the root. Do not automatically load another Practical Coding reference from this module; isolate substantial follow-up when adding another large reference would cost more context than a handoff.

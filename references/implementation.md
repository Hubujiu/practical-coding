# Implementation

Load this module only when a change must coordinate multiple files, contracts, or invariants and the change surface is still unclear, or when the sufficient evidence for a risky change is itself unresolved. Produce a small change map and a bounded evidence plan, then implement; do not narrate a workflow.

## Work Locally

- Identify the authoritative contract or invariant and the minimum producers, consumers, adapters, data, and checks that must move together.
- Read only those paths and their material callers/dependencies; leave nearby cleanup opportunities and unrelated code alone.
- Preserve public compatibility unless the requirement authorizes a break. When migration is required, choose one authoritative internal representation and keep compatibility at the narrowest boundary.
- Match project conventions and make the smallest coherent end-to-end diff.

## Keep Code Small

Reuse existing helpers and patterns. Add an interface, adapter, wrapper, switch, or generic utility only for a demonstrated current boundary. Comments explain intent or constraints code cannot express.

## Match Error Handling to Real Boundaries

Put validation once at the narrowest authoritative boundary. Add retries, fallbacks, broad catches, compatibility layers, or recovery only for a concrete failure mode. Preserve required safety and integrity checks.

## Prove the Change

Map each material claim or risk to the cheapest check that can falsify it, at the lowest sufficient level: diff inspection; direct exercise or render; compile/type/lint; an existing focused test; one new focused test; a boundary integration test; the full suite only for a broad surface or a required gate. Prefer project gates and existing focused tests; add one durable test only when direct evidence is insufficient, and do not expand into open-ended bug hunting or duplicate assertions across layers.

For persistence or concurrency, exercise restart/rollback/race behavior and close files, connections, threads, and handles before cleanup. For compatibility, run both old and new callers. For a security boundary, include one valid case and the smallest representative rejection cases, and verify rejection happens before side effects.

Claim only what fresh evidence supports, re-checked after the final edit. "Too simple to verify", "it worked before this last edit", and "the tests probably still pass" are rationalizations, not evidence: run the cheapest sufficient check, or report the limitation and remaining uncertainty when environment, credentials, or services block it.

If implementation exposes another event, return it to the router; do not automatically load another module.

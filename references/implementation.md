# Implementation

**Tree depth: 1**

Load this node only from its parent when a change must coordinate an unmapped contract or invariant, touches a material risk boundary where direct execution would be unsafe, or when sufficient evidence for a risky material change is unresolved. Produce only the change map, implementation, and evidence the task needs; this is not a mandatory coding stage.

## Work Locally

- Identify the authoritative contract or invariant and the minimum producers, consumers, adapters, data, and checks that must move together.
- Read only those paths and their material callers or dependencies; leave nearby cleanup opportunities and unrelated code alone.
- For a risk boundary, identify the narrowest authoritative point that owns the guarantee before editing.
- Preserve public compatibility unless the requirement authorizes a break. When migration is required, choose one authoritative internal representation and keep compatibility at the narrowest boundary.
- Match project conventions and make the smallest coherent end-to-end diff.

## Keep Code Small

Reuse existing helpers and patterns. Add an interface, adapter, wrapper, switch, or generic utility only for a demonstrated current boundary. Comments explain intent or constraints code cannot express.

## Match Error Handling to Real Boundaries

Put validation once at the narrowest authoritative boundary. Add retries, fallbacks, broad catches, compatibility layers, or recovery only for a concrete failure mode. Preserve required safety, permission, integrity, and compatibility guarantees without expanding into unrelated hardening.

## Prove the Change

Map each material claim or risk to the cheapest check that can falsify it: direct exercise or render; compile/type/lint; an existing focused test; one new focused test; a boundary integration test; the full suite only for a broad surface or required gate.

For persistence or concurrency, exercise restart/rollback/race behavior when relevant. For compatibility, exercise materially affected old and new callers. For security or permissions, include one valid case and the smallest representative rejection cases, and verify rejection happens before side effects.

Claim only what fresh evidence supports. If the environment blocks an appropriate check, report the limitation and remaining uncertainty.

## Local Router

The following depth-2 children are staged candidates. Choose at most one for the present blocker; do not load siblings merely because their nouns also appear in the task.

1. If the primary invariant is who/what may cross a trust boundary—authentication, authorization, untrusted input, secrets, permission checks, or a sensitive side effect that must be rejected before execution—load `references/implementation-security-boundary.md`.
2. If an existing persisted representation, public/shared API, serialized format, schema, or configuration contract must change while old data/callers/versions may coexist or rollback must remain possible, load `references/implementation-migration-compatibility.md`.
3. If correctness primarily depends on ordering, atomicity, idempotency, transactions, retries/duplicate delivery, concurrent mutation, or restart-visible state ownership, load `references/implementation-state-concurrency.md`.

Stay in this parent when the risk is ordinary, the authoritative boundary is already clear, or the specialist would only restate this node. Security takes precedence only when allow/deny or secret-handling is the primary guarantee; migration takes precedence for version/representation coexistence; state/concurrency takes precedence for ordering/atomicity. If no single specialist owns the blocker cleanly, stay here rather than loading multiple siblings.

These children are experimental. Retain them only when each earns independent minimum-sufficient cases, quality-qualified lift over this parent, and acceptable Trigger/Boundary behavior.

Resolve ordinary implementation choices locally by established project convention, platform default, or the smallest sufficient reversible choice. Never route automatically to Decision. If a genuinely user-owned choice blocks safe execution and no default is justified, ask the minimum blocking question without opening a Decision workflow.

If work exposes a genuinely different top-level unexplained failure rather than an Implementation descendant, return that blocker to Core.

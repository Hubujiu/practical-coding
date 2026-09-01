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

This node is a leaf. Handle security/permission boundaries, migration/compatibility, and state/concurrency invariants with the shared implementation rules above; repeated capability ablation did not show stable minimum-sufficient lift for separate children.

Resolve ordinary implementation choices locally by established project convention, platform default, or the smallest sufficient reversible choice. Never route automatically to Decision. If a genuinely user-owned choice blocks safe execution and no default is justified, ask the minimum blocking question without opening a Decision workflow.

If work exposes a genuinely different top-level unexplained failure rather than an Implementation descendant, return that blocker to Core.

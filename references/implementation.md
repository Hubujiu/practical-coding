# Implementation

Load only for `change.context-heavy`. Produce a small change map, then implement; do not narrate a workflow.

## Work Locally

- Identify the authoritative contract or invariant and the minimum producers, consumers, adapters, data, and checks that must move together.
- Read only those paths and their material callers/dependencies; ignore nearby cleanup and decoys.
- Preserve public compatibility unless the requirement authorizes a break. When migration is required, choose one authoritative internal representation and keep compatibility at the narrowest boundary.
- Match project conventions and make the smallest coherent end-to-end diff.

## Keep Code Small

Reuse existing helpers and patterns. Add an interface, adapter, wrapper, switch, or generic utility only for a demonstrated current boundary. Comments explain intent or constraints code cannot express.

## Match Error Handling to Real Boundaries

Put validation once at the narrowest authoritative boundary. Add retries, fallbacks, broad catches, compatibility layers, or recovery only for a concrete failure mode. Preserve required safety and integrity checks.

If implementation exposes another event, return it to the router; do not automatically load another module.

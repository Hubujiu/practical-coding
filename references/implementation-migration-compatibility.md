# Migration & Compatibility

**Tree depth: 2**

Load only from Implementation when a persisted or public/shared contract must change while old data, callers, versions, or rollback may coexist. This is not for a new local type with no compatibility surface.

## One Authoritative Destination

- Define the target representation or contract and the exact compatibility window.
- Keep one authoritative semantic meaning. Compatibility adapters translate at the narrowest boundary; do not let old and new representations become independent sources of truth.
- Prefer additive/expand changes before destructive/contract changes when coexistence is required.
- Backfill or migrate existing state before removing the path that can read it.

## Phase the Change

Use only phases the real system needs:

1. introduce a compatible target surface;
2. migrate/backfill or begin target-format writes;
3. switch authoritative reads/callers;
4. verify mixed old/new operation;
5. remove compatibility only after the stated window or evidence permits it.

Do not dual-write by default. If dual-write is necessary, define failure ordering and reconciliation explicitly.

## Rollback

Keep rollback possible until the destructive step. A rollback plan must say which representation becomes authoritative again and what happens to data written during the migration window; "revert the deploy" is insufficient when durable state changed.

## Evidence

Exercise the smallest material matrix: old state with new code, new state with new code, old caller with compatibility when required, restart/reload for durable state, and rollback before cleanup. Test removal only when the compatibility window actually ends.

## Local Router

**Current status: leaf.**

# State & Concurrency

**Tree depth: 2**

Load only from Implementation when the unresolved guarantee depends primarily on ordering, atomicity, idempotency, transaction boundaries, duplicate delivery/retry behavior, concurrent mutation, or restart-visible state ownership.

## Find the State Owner

- Name the authoritative state and the component/transaction that owns each transition.
- Write the invariant in terms of observable states before choosing a lock, queue, transaction, retry, or cache.
- Separate in-memory coordination from durable state. Restart semantics must follow the actual source of truth.

## Make Ordering Explicit

- Identify check-then-act windows and transitions that must be atomic.
- Decide whether an operation is safely repeatable, idempotent with a key/version, at-most-once, or allowed to duplicate. Do not add retries before this is known.
- Use the narrowest existing transaction/locking/version primitive that preserves the invariant. Do not invent distributed coordination for a local invariant.
- Keep critical sections and transactions limited to state that must move together.

## Evidence

Prefer one deterministic interleaving or barrier-controlled test over many timing-sensitive loops. When relevant, exercise duplicate delivery/retry, concurrent reset/update, stale version rejection, transaction rollback, and restart/reload. Fixed sleeps are not concurrency evidence.

## Local Router

**Current status: leaf.**

# State, Persistence, and Concurrency

Load only when correctness materially depends on persistence, migration state, transactions, ordering, retries, idempotency, rollback, restart, duplicate delivery, or concurrent actors.

## Procedure

- Name the state invariant and the operation that owns it.
- Identify the atomicity/ordering boundary and which failures can happen before, during, or after it.
- Distinguish in-memory success from durable success.
- Reuse existing transaction, lock, lease, idempotency, or migration mechanisms before introducing new ones.
- Exercise only the material failure modes: duplicate, race, rollback, restart, partial write, or mixed state.

Do not add locks, retries, transactions, or recovery machinery without a concrete failure mode.

## Exit evidence

The invariant holds for the normal path and the smallest representative material failure/interleaving path; ownership and recovery semantics are explicit enough to contract back to Core.

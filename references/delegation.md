# Isolated Module Delegation

Load this protocol only inside a worker selected by the Isolation Gate. Also read exactly the one Decision, Exploration, Codebase Memory, Debugging, Implementation, or Verification module assigned by the root.

## Worker contract

- Use the requirement, project constraints, known evidence, repository state, and allowed scope supplied by the root. Do not reconstruct the full conversation or rescan unrelated areas.
- The root must not inspect or modify the delegated scope while this worker runs. If that happens, stop and return `stale`; do not spend more calls reconstructing a moving target.
- Do only the assigned module's work. Report a newly exposed event to the root instead of loading another Practical Coding module or spawning another worker.
- Decision, Exploration, Codebase Memory, and Debugging workers are read-only.
- Verification workers may run checks but do not modify product code.
- An Implementation worker writes only within its assigned file or subsystem scope and is the sole writer there.
- Record the starting HEAD and relevant dirty paths. Mark the result stale if the repository or assigned scope changes underneath the work.
- Never commit, reset, checkout, clean, or overwrite pre-existing user changes unless the root explicitly authorizes that operation.

## Compact return capsule

Return conclusions and evidence, not a transcript, raw graph dump, copied source, full logs, or full diff:

```yaml
event: decision | exploration | codebase-memory | debugging | implementation | verification
status: complete | provisional | blocked | stale | needs-root
repo_state: { head: "<commit-or-null>", dirty_paths: [] }
scope: { paths: [], symbols: [] }
findings: []
changes: []
checks: []
unresolved: []
next_event: null
```

Evidence pointers should identify an exact path, symbol, command result, or coverage limitation. `next_event` is a suggestion; only the root decides whether to route it. Do not persist the capsule in the repository unless the user requested an artifact.

## Module-specific result

- Decision: material constraints, viable options, recommendation, and tradeoffs.
- Exploration: exact paths/symbols, relevant edges, compatibility boundaries, likely change surface, decoys, and gaps.
- Codebase Memory: project/generation, queries and pagination, symbols and paths, call edges, coverage and source fallbacks.
- Debugging: reproduction, earliest incorrect state, supported root cause or current hypothesis, and remaining uncertainty.
- Implementation: changed paths, implementation decisions that are not evident from the diff, and fresh focused checks.
- Verification: evaluated repository state, checks and results, freshness, limitations, and unverified risks.

# Isolated Module Delegation

Load this protocol only inside a worker selected by the Isolation Gate. Also read exactly the one Decision, Navigation, Debugging, or Implementation module assigned by the root.

## Worker contract

- Use the requirement, project constraints, known evidence, repository state, and allowed scope supplied by the root. Do not reconstruct the full conversation or rescan unrelated areas.
- The root must not inspect or modify the delegated scope while this worker runs. If that happens, stop and return `stale`; do not spend more calls reconstructing a moving target.
- Do only the assigned module's work. Report a newly exposed event to the root instead of loading another Practical Coding module or spawning another worker.
- Decision, Navigation, and Debugging workers are read-only.
- An Implementation worker is read-only when assigned only mapping or evidence work. When explicitly assigned implementation, it writes only within its assigned file or subsystem scope, is the sole writer there, and may run the checks its evidence plan requires.
- Record the starting HEAD and relevant dirty paths. Mark the result stale if the repository or assigned scope changes underneath the work.
- Never commit, reset, checkout, clean, or overwrite pre-existing user changes unless the root explicitly authorizes that operation.

## Compact return

Return conclusions and evidence, not a transcript, raw graph dump, copied source, full logs, or full diff. A useful return states:

- which module's work was done and whether it is complete, provisional, blocked, or stale;
- the repository state it evaluated: starting commit and relevant dirty paths;
- the paths and symbols in scope;
- findings, changes, and checks, each backed by an exact path, symbol, command result, or coverage limitation;
- unresolved items, and any newly exposed event as a suggestion that only the root decides whether to route.

Do not persist the return in the repository unless the user requested an artifact.

## Module-specific result

- Decision: material constraints, viable options, recommendation, and tradeoffs.
- Navigation: selected backend; exact paths/symbols and relevant edges; when graph-backed, project/generation, queries, pagination, coverage, and source fallbacks.
- Debugging: reproduction, earliest incorrect state, supported root cause or current hypothesis, and remaining uncertainty.
- Implementation: mapped boundaries, changed paths when writes were authorized, implementation decisions not evident from the diff, fresh focused checks with results and freshness, and unverified risks.

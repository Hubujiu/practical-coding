# Isolated Reference Delegation

Load this protocol only inside a worker selected by the Isolation Gate. Also read exactly one assigned automatic reference (`Debugging`, `Implementation`, or `Navigation`) or one explicitly requested manual reference.

## Worker contract

- Use the requirement, project constraints, known evidence, repository state, and allowed scope supplied by the root. Do not reconstruct the full conversation or rescan unrelated areas.
- The root must not inspect or modify the delegated scope while this worker runs. If it changes, return `stale`.
- Do only the assigned reference's work. Report a newly exposed blocker to the owner of the active tree node instead of discovering arbitrary descendants or spawning another worker.
- Debugging and Navigation workers are read-only.
- A manual Decision worker is always outside the automatic execution tree and is read-only unless the user separately authorizes implementation after the choice is settled.
- An Implementation worker is read-only when assigned mapping/evidence only. When explicitly assigned implementation, it writes only within its bounded non-overlapping scope and is the sole writer there.
- Record starting HEAD and relevant dirty paths. Never commit, reset, checkout, clean, or overwrite user changes unless explicitly authorized.

## Compact return

Return conclusions and evidence, not transcripts or raw search dumps:

- assigned reference and status: complete, provisional, blocked, or stale;
- active node and current tree depth when the work belongs to the automatic tree;
- starting repository state and exact paths/symbols in scope;
- findings or changes backed by current source/tool evidence;
- checks run and their freshness;
- coverage limitations, unresolved items, and any newly exposed top-level blocker.

Do not persist the capsule unless the user requested an artifact.

# Isolated Reference Delegation

Load this protocol only inside a worker selected by the Isolation Gate. Also read exactly one assigned reference: Decision, Debugging, Implementation, or Navigation retrieval.

## Worker contract

- Use the requirement, project constraints, known evidence, repository state, and allowed scope supplied by the root. Do not reconstruct the full conversation or rescan unrelated areas.
- The root must not inspect or modify the delegated scope while this worker runs. If it changes, return `stale`.
- Do only the assigned reference's work. Report a newly exposed blocker to the root instead of loading another reference or spawning another worker.
- Decision, Debugging, and Navigation workers are read-only.
- An Implementation worker is read-only when assigned mapping/evidence only. When explicitly assigned implementation, it writes only within its bounded non-overlapping scope and is the sole writer there.
- Record starting HEAD and relevant dirty paths. Never commit, reset, checkout, clean, or overwrite user changes unless explicitly authorized.

## Compact return

Return conclusions and evidence, not transcripts or raw search dumps:

- assigned reference and status: complete, provisional, blocked, or stale;
- starting repository state and exact paths/symbols in scope;
- findings or changes backed by current source/tool evidence;
- checks run and their freshness;
- coverage limitations, unresolved items, and any newly exposed event for root routing.

Do not persist the capsule unless the user requested an artifact.

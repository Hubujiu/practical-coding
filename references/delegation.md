# Isolated Reference Delegation

Load only inside a worker selected by the Isolation Gate. The root assigns one bounded adaptive event and the minimum references needed for it: one capability root, optionally one specialist leaf, or the structural-retrieval procedure from `references/navigation.md`.

The structural-retrieval procedure belongs to the Retrieval axis; it is not an independent Navigation capability. Manual-only interaction modes are never selected or delegated by the adaptive Isolation Gate.

## Worker contract

- Use the requirement, known evidence, repository state, and allowed scope supplied by the root. Do not reconstruct the whole conversation or rescan unrelated areas.
- Do only the assigned event. If a different material blocker appears, return it to the root instead of loading sibling leaves or spawning another worker.
- Read-only workers do not modify repository state.
- A writing Engineering worker may modify only an explicitly assigned non-overlapping scope and must be the sole writer there.
- Record starting HEAD and relevant dirty paths. Return `stale` if the assigned scope changes underneath the work.
- Never commit, reset, checkout, clean, or overwrite user changes unless explicitly authorized.

## Compact evidence capsule

Return conclusions and evidence, not a transcript or raw dump:

- capability path used and status: complete / provisional / blocked / stale;
- starting repository state and paths/symbols in scope;
- findings or changes backed by exact source/tool evidence;
- checks run and their freshness;
- unresolved items and any newly exposed event for root routing.

Do not persist the capsule unless the user requested an artifact.
# Isolated Reference Delegation

Use only when isolation saves more context than the handoff costs. Read one assigned automatic reference or an explicitly requested manual reference; do not reconstruct the entire conversation or spawn another worker.

The handoff supplies the requested outcome, active node/depth, known evidence, repository state, and bounded scope. Record starting HEAD and relevant dirty paths. Navigation/Debugging workers are read-only. Implementation writes only its assigned non-overlapping scope as sole writer; mapping-only assignments remain read-only. Manual Decision authorizes no implementation by itself.

No overlapping writers. The owner must not change delegated inputs while work runs; if those inputs changed, return `stale`. Never commit, reset, checkout, clean, or overwrite user changes without authorization.

Return status (complete/provisional/blocked/stale), starting state, concrete findings or changes, fresh checks, and coverage gaps. Return new blockers to the active node's owner. Do not return raw transcripts or persist a capsule unless requested.

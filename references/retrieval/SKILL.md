# Retrieval

**Retrieval depth:** root  
**Purpose:** locate the minimum current-source evidence required for the task  
**Immediate child:** [`direct.md`](direct.md)

Retrieval is independent of the automatic execution tree. It progresses according to the information problem that remains unresolved, not according to task risk, execution depth, repository size, or provider strength.

Start at Direct Locate. Do not preload any node beyond this immediate child and do not select a deeper stage from the root.

## Evidence and stopping contract

- Keep the current claim and the smallest evidence gap in working context; do not create a new state file or mandatory report.
- Request bounded candidates, then read only the source ranges needed for that gap. Once locations are known, stop discovery rather than repeating inventories.
- Stop when current authoritative source supports the claim and its material boundary. More matches or available tools are not reasons to continue.
- A failed search is not proof of absence: distinguish a wrong scope, an unavailable provider, and a genuinely unsupported claim. After an unproductive query, change a justified scope or follow the active node's immediate child; do not repeat the same search without new evidence.
- After an edit, generated-source refresh, or index change, recheck only affected evidence before relying on it. An index proposes locations; it does not override current source.
- Return the supported conclusion and any unresolved gap. Never turn missing evidence into certainty or trim away a required failure or counterexample to meet an output budget.

A capability provider implements a stage; it is not the stage itself. The same policy must continue to work when providers change or when runtime fallback is necessary.

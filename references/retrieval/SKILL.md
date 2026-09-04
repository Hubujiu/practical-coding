# Retrieval

**Retrieval depth:** root  
**Purpose:** locate the minimum current-source evidence required for the task  
**Immediate child:** [`direct.md`](direct.md)

Retrieval is independent of the automatic execution tree. It progresses according to the information problem that remains unresolved, not according to task risk, execution depth, repository size, or provider strength.

Start at Direct Locate. Do not preload any node beyond this immediate child and do not select a deeper stage from the root.

A capability provider implements a stage; it is not the stage itself. The same policy must continue to work when providers change or when runtime fallback is necessary.

# Structural Retrieval Procedure

This file is **not a separate Navigation axis or execution phase**. It is the deeper procedure inside the Retrieval tree for substantial **R2 Structural** mapping and, when needed, disciplined **R3 bounded exhaustive repository** coverage.

Routine R0/R1 target reading, caller/reference lookup, sibling inspection, and nearby contract discovery do not need this file.

## Retrieval tree position

`R0 Target → R1 Local`, then branch only as needed:

- **R2 Structural relation** for callers/callees/imports/implementations/dependencies/data/config flow.
- **R2 External contract** is handled by the root with authoritative external sources; it does not require this file unless local structural mapping is also substantial.
- **R3 Bounded exhaustive repository claim** only when the requested claim is explicitly repository-wide or lower-depth retrieval cannot localize the boundary.

External retrieval is not downstream of repository-wide search.

## Structural retrieval

1. Start from the best anchor already known: symbol, error, route, test, config key, type, or file.
2. Ask one relationship question at a time.
3. Prefer an already-available structural index/graph when it reduces source exploration; otherwise use bounded source search.
4. Rank candidates before reading source. Read only enough to confirm or reject each relationship.
5. Return exact paths/symbols and material edges, not raw search output.

Graph/index output is navigation evidence, not repository truth. Confirm material behavior in current source before editing.

## Bounded exhaustive claims

State the boundary being exhausted, search it systematically with pagination/coverage tracking, and report gaps. Do not call a partial search exhaustive.

## Contract

Once the relevant relationship or boundary is known, stop retrieval expansion and contract to that surface. Do not keep searching merely because a broad tool remains available.

Finding source may change R-depth without changing E-depth. Raise execution only if the retrieved evidence exposes an unresolved execution problem that requires Probe, Diagnosis, Engineering, or a specialist leaf.
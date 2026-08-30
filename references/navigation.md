# Navigation

Load this module only when structural or repository-wide retrieval is itself a substantial unresolved event. Produce the smallest bounded map that answers the task; do not tour the repository.

## Retrieval tree

`R0 Target → R1 Local`, then branch only as needed:

- **R2 Structural relation** for callers/callees/imports/implementations/dependencies/data/config flow.
- **R2 External contract** is handled by the root with authoritative external sources; it does not require this module unless local structural mapping is also substantial.
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

Once the relevant relationship or boundary is known, stop navigation and contract retrieval to that surface. Do not keep searching merely because a broad tool remains available.

# Navigation

Navigation is the detailed retrieval procedure, not an Event Router branch. Load it only when broad code discovery, structural mapping, external contract lookup, or bounded exhaustive coverage is substantial enough that the short Retrieval Policy in `SKILL.md` is insufficient.

Use already-available capabilities only. Do not install a backend, add a persistent integration, or change project configuration solely to obtain retrieval for the current task.

## Retrieval ladder

### Known target

Read the identified file, symbol, route, test, error, or configuration directly. Follow only material definitions, callers, consumers, transformations, and compatibility boundaries. Stop when the requested behavior and minimum coherent surface are established.

### Bounded or ranked source discovery

When location is unknown, prefer an already-available bounded/ranked primitive. Otherwise use ordinary filename, text, and symbol search.

- Batch narrow queries rather than dumping the repository.
- Use top-k, limits, pagination, and narrow scopes where available.
- Confirm relevance through imports, calls, tests, or runtime flow rather than name similarity.
- Read definitions first, then only the material neighbors.

### Structural retrieval

Use an already-available structural code index when the unresolved question is primarily relational and lexical reconstruction would be expensive: callers, callees, imports, implementations, inheritance, dependencies, or cross-file flow.

When Codebase Memory is available, confirm project identity/freshness, use the smallest graph query set, check index coverage once candidate paths are known, and read current source for material claims and every partial/stale/excluded range. If unavailable or insufficient, continue with bounded source discovery.

### External and exhaustive evidence

For a repository-wide claim, state the bounded scope, search systematically with pagination/coverage tracking, and disclose gaps. For an external API/protocol/license contract, use the smallest authoritative maintained source needed for the code decision.

## Contract

Search and graph output are evidence, not repository truth. Verify material conclusions in current source. Once the relevant relationship or boundary is known, stop expanding and contract to that surface.

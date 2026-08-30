# Navigation

Navigation is the detailed procedure for substantial retrieval. It is not an execution branch. Load it only when R2/R3 work is broad enough that the short Retrieval Ladder in `SKILL.md` is insufficient.

The invariant is **expand only to answer the next unresolved question; contract as soon as the relevant boundary is found**.

Use already-available capabilities only. Do not install a backend, add persistent integration, or change project configuration solely for retrieval. Missing capabilities fall back to bounded source search.

## R0 — Target

If current evidence identifies the relevant file, symbol, route, test, error, or configuration, read it directly. Follow only material definitions, callers, consumers, transformations, and compatibility boundaries needed for the next decision.

Stop when the minimum coherent surface is explained.

## R1 — Local discovery

When location is uncertain, search the nearest plausible scope first.

- Prefer bounded/ranked host-native retrieval when available.
- Otherwise use filename, text, symbol, reference, `rg`, `grep`, `find`, or host equivalents.
- Batch narrow queries; use top-k, limits, pagination, or scoped directories when supported.
- Read definitions before neighbors.
- Confirm relevance through imports, calls, tests, or runtime flow rather than name similarity.
- Do not copy large result sets into context when a narrower follow-up can select candidates.

If R1 identifies the boundary, contract to those targets and stop broad discovery.

## R2 — Structural discovery

Use R2 when the unresolved question is primarily relational: callers, callees, imports, implementations, inheritance, dependencies, or cross-file execution flow.

Prefer an already-available structural index only when it materially reduces exploration. `DeusData/codebase-memory-mcp` is one supported example when already integrated; it is not required.

For any structural backend:

1. confirm project identity/freshness when the capability exposes that state;
2. ask the smallest relationship query that can answer the current question;
3. inspect current source for material snippets and any partial/stale/unknown coverage;
4. treat index output as evidence, not authority.

If no structural backend exists, reconstruct only the required relationship with bounded source search. Do not install one solely for the task.

## R3 — Repository discovery

Expand repository-wide only when narrower retrieval cannot localize the relevant boundary or the task requires a bounded exhaustive repository claim.

Use scoped exclusions, pagination, ranking, and staged narrowing. A repo-wide search is a candidate generator, not permission to read every result. For negative or exhaustive claims, disclose coverage limits and verify representative/current source.

As soon as the relevant subsystem or symbol set is identified, contract back to that scope.

## R4 — External evidence

Use authoritative external evidence only when the repository cannot establish the required fact: current framework/API behavior, compatibility, license, maintained implementation, or another external contract.

Prefer primary maintained documentation, upstream source, standards, or official release information. Retrieve only the facts that affect the current decision. External search is not a substitute for reading the repository's actual integration.

## Evidence depth

- **Scout:** narrow positive lookup; provisional.
- **Verify — default:** material relationships and snippets plus current-source verification.
- **Auditor:** only for a bounded exhaustive request; require relevant pagination/coverage and disclose limitations.

A clean index or search result is not proof of semantic completeness.

## Context discipline

Returning to a narrower rung does not unload already-read text. It means stop widening and keep subsequent reads within the localized boundary.

When another reasoning reference is already resident and substantial R2/R3 work would create large context, prefer a read-only isolated Navigation worker only when the context saved exceeds handoff cost. The worker returns paths, symbols, relationships, constraints, gaps, and evidence limits—not raw search transcripts.

# R0 Direct Locate

**Retrieval stage:** R0  
**Goal:** resolve the current claim through an already-known or narrowly identifiable target  
**Immediate child:** [`discovery.md`](discovery.md)

## Enter when

The target can be identified by a known file, exact symbol, exact identifier, route, test, configuration key, error location, or a very narrow literal search.

## Work

- Read the target and only the minimum surrounding context needed to interpret it.
- Follow a directly referenced definition or caller only when the current claim requires it.
- Prefer bounded line or symbol reads over whole-file dumps.
- Return concrete source locations and the evidence they establish.

## Stop or escalate

Return as soon as the target plus minimum context answers the current question.

If the target cannot be located confidently from exact or narrow evidence, load **R1 Ranked Discovery**. Do not jump to later stages and do not broaden into a repository tour.

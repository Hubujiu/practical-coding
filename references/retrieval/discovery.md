# R1 Ranked Discovery

**Retrieval stage:** R1

**Goal:** locate the implementation for known intent

**Immediate child:** [`evidence.md`](evidence.md)

When location is unknown, issue a bounded intent query with lexical anchors using an available ranked capability; otherwise use exact/regular-expression source search. Read the strongest candidates in current source. Ranking is not proof, and unrelated matches are not progress.

When the target is already located, do not run another discovery query merely to satisfy this stage. Reuse that location. Return if its bounded evidence resolves the claim; otherwise load R2 Evidence Expansion for the missing caller, test, configuration, interface, schema, or other material boundary.

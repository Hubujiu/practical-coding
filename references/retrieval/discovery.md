# R1 Ranked Discovery

**Retrieval stage:** R1  
**Goal:** find likely implementation locations when the target is unknown but the intended behavior or concept is known  
**Immediate child:** [`evidence.md`](evidence.md)

## Work

Use the strongest available bounded retrieval capability in this order:

1. hybrid semantic intent plus lexical anchors;
2. ranked lexical or symbol search;
3. exact or regular-expression repository search as a lossless fallback.

Return only the strongest candidates. Confirm candidate relevance in current source through definitions, imports, calls, tests, configuration, or runtime flow; ranking is not proof.

Do not search merely related concepts, dump unbounded matches, or treat provider output as repository truth.

## Stop or escalate

Return when one candidate and its bounded source evidence answer the current question.

If the answer still depends on evidence distributed across nearby implementations, callers, configuration, tests, interfaces, or schemas, load **R2 Evidence Expansion**. Do not skip this immediate child.

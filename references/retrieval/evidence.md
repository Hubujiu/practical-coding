# R2 Evidence Expansion

**Retrieval stage:** R2

**Goal:** the smallest cross-file evidence set for unresolved claims

**Immediate child:** [`structural.md`](structural.md)

Start from known candidates. For each remaining claim, read the smallest source that could prove or falsify it: an authoritative implementation, material caller/callee, focused test, configuration, interface, schema, or state owner. Add a source because evidence is missing, not because the file is nearby. Batch independent reads; stop once the material claims are supported.

If the remaining answer depends on a relationship such as call/dependency path, ownership, control/data flow, or impact coverage, load R3 Structural Trace. Do not first reconstruct an entire graph manually just to qualify for the child.

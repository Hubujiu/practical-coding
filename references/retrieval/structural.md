# R3 Structural Trace

**Retrieval stage:** R3

**Leaf:** yes

Resolve the smallest relationship needed: caller/callee, dependency, implementation, ownership, control/data flow, or change impact. Use an available structural capability after checking repository identity, index freshness, and coverage. Verify material edges in current source; an index does not prove dynamic dispatch, excluded code, or missing edges cannot exist.

Without that capability, trace bounded references: find the next unresolved edge, read its authoritative source, and stop when the required path is established. Report coverage gaps instead of claiming completeness. There is no deeper stage and no whole-repository escalation.

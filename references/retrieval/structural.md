# R3 Structural Trace

**Retrieval stage:** R3  
**Leaf:** yes

## Goal

Resolve questions whose answer depends on relationships between code entities rather than isolated matching text.

## Work

Use an available graph-aware structural capability for the smallest query set that can establish the required relationship. Appropriate relationships include:

- callers and callees;
- imports, implementations, inheritance, and dependencies;
- ownership and authoritative state boundaries;
- control flow and data flow;
- change impact and cross-service paths.

Check project identity, index freshness, and coverage before relying on a structural result. Verify every material path, symbol, and partial, stale, or excluded range in current source.

If no graph-aware capability is available at runtime, fall back to bounded reference tracing:

`find references -> read material callers/callees -> follow the next unresolved edge -> stop`.

Stop once the relationship required by the task is established. There is no deeper retrieval stage and no whole-repository escalation.

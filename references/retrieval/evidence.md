# R2 Evidence Expansion

**Retrieval stage:** R2  
**Goal:** expand located candidates into the smallest cross-file evidence set required by unresolved claims  
**Immediate child:** [`structural.md`](structural.md)

## Work

Start from the strongest R1 candidate. For each unresolved claim, identify the smallest additional source that can prove or falsify it. Possible evidence includes:

- the primary implementation;
- one material caller or callee;
- authoritative configuration;
- focused tests;
- an interface, schema, state owner, or compatibility boundary;
- adjacent behavior only when it changes the answer.

Expand because a named claim lacks evidence, not because a file is related. Keep an explicit bounded evidence set and stop adding sources once every material claim is supported.

## Stop or escalate

Return when the required distributed evidence is complete.

If the unresolved answer is fundamentally a relationship—call path, dependency path, ownership, control flow, data flow, or impact surface—and bounded source expansion would reconstruct a graph manually, load **R3 Structural Trace**.

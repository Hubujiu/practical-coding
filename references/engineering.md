# Engineering

Load this capability root only when the desired behavior is known but sufficient bounded Retrieval still cannot safely localize the authoritative contract, invariant, ownership boundary, or coherent change surface. An E1 probe may precede this root only when one cheap executable observation could settle that execution uncertainty.

Engineering is not a synonym for implementation. Most implementation remains E0 with whatever R-depth is needed to find the target. Source discovery by itself does not justify Engineering.

## Structured mapping

1. State the material behavior that must remain true after the change.
2. Identify the narrowest owner of that behavior: producer, consumer, adapter, state boundary, public contract, or side-effect boundary.
3. Map only the paths that must move together for that owner to remain coherent.
4. Reuse existing project primitives and keep one authoritative representation where possible.
5. Map each material claim to the cheapest check that can falsify it.
6. Once the boundary is known, stop mapping and implement the smallest coherent diff.

Do not create abstractions because the mapped surface is large. Create one only when a current demonstrated boundary needs it.

## Specialist leaf trigger

Load one child under `references/specialists/` only when this root cannot support a material guarantee without domain-specific reasoning. The guarantee must be concrete, not inferred from a noun in the task.

- trust/rejection boundary → `security.md`
- persistence/concurrency/transaction boundary → `state.md`
- old/new or public contract boundary → `compatibility.md`
- measured resource or speed boundary → `performance.md`
- structural review/refactor boundary → `quality.md`
- material visual/interface direction → `interface.md`

Do not load multiple leaves as a checklist. Resolve the active guarantee, contract, then route a newly exposed orthogonal event separately.

## Exit

Exit Engineering when the authoritative owner, affected paths, and sufficient evidence are known. Return to Core behavior for the edit and focused verification.
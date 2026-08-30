# Compatibility and Migration

Load only when a material requirement spans old/new callers, public APIs, schemas, protocols, serialized data, configuration formats, versions, or migration windows.

## Procedure

- Identify the exact compatibility contract and who depends on it.
- Choose one authoritative internal representation where possible.
- Keep compatibility adaptation at the narrowest boundary instead of spreading dual representations through the system.
- Distinguish required coexistence from speculative backward compatibility.
- For migration, identify start state, end state, rollback/restart expectations, and the shortest supported transition window.

Do not preserve undocumented behavior merely because it exists. Do not create permanent aliases or shims without an active dependent contract.

## Exit evidence

Representative required old and new paths work, unauthorized breaks are absent, and any temporary migration/compatibility surface has explicit ownership and scope.

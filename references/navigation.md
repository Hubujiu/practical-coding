# Navigation

**Concern:** repository topology only  
**Output:** the smallest bounded map that identifies where Retrieval should begin

Load Navigation only when the current unresolved question is **which repository area should be searched**. Do not load it merely because a file path is unknown; R1 Ranked Discovery handles unknown locations when the intended behavior or concept is already known.

## Goal

Reduce a broad or unfamiliar repository to a bounded scope such as one package, module, service, layer, or directory group.

A useful result looks like:

```text
platform API
  -> progress-core lifecycle package
  -> operation executor and state package
```

not a file inventory, semantic-search transcript, or repository tour.

## Procedure

1. Read the repository's own map first: root manifests, workspace/module declarations, package metadata, build files, and maintained architecture notes.
2. Identify only the regions that can own the requested behavior or relationship.
3. Exclude unrelated generated, vendored, fixture, example, and historical areas unless the task explicitly includes them.
4. Return the bounded scope and the evidence that establishes the boundary.
5. Continue with `references/retrieval/SKILL.md` at Direct Locate inside that scope.

## Boundary

Navigation does not:

- choose between search tools;
- perform semantic or ranked discovery;
- expand callers, tests, configuration, or related implementations;
- trace call graphs, dependencies, control flow, or data flow;
- claim exhaustive coverage unless the user explicitly requested it and coverage can be demonstrated.

When a concrete path, symbol, identifier, or sufficiently narrow scope is already known, skip Navigation.

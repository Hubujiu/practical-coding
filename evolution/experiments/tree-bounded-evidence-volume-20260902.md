# EXP-20260902 — Bound evidence volume after discovery

Status: **n=1 qualified; frozen for paired n=3**

## Observation

The isolated leaf candidate's complete paired n=3 reached 45/45 quality against frozen v1.5 at 45/45 and reduced mean tool calls from 8.27 to 7.60, but increased mean total tokens from 211,758.69 to 242,910.84 and duration from 72.94s to 75.60s. The later Core-only collapse regressed every cost metric.

## Hypothesis

The topology is not the remaining cost problem. Once discovery identifies candidate paths or symbols, explicitly stopping broad inventory and using bounded reads should reduce tool-output/context volume without changing evidence quality, routing, or verification scope.

## Change boundary

Add only a general retrieval-volume rule to Core/Retrieval Policy: stop discovery after candidates are known, read relevant symbols or bounded ranges, avoid whole-file/repeated inventory, and batch independent bounded reads only while output remains focused. Do not change cases, scorer, topology, nodes, or repositories.

## Acceptance

Deterministic tests must pass, followed by a fresh complete current-only n=1 with every quality/trace/manual cell passing. Only that frozen candidate may run paired n=3. Accept delivery only if quality remains at least equal and the comparable cost report shows a genuine net improvement rather than relying on repetition variance.

## n=1 qualification

`benchmark-results/tree-bounded-evidence-n1-20260902` completed 58/58 determinate cells. Adaptive passed 15/15; Core, Debugging, and Implementation capability ceilings each passed 13/13; adaptive trace/manual discipline was perfect. The runtime/scorer/cases are frozen for paired n=3.

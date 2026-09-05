# EXP-20260901 — Tree oracle outcome semantics

Status: **frozen before scorer edit**

## Observation

The complete paired n=3 run at `benchmark-results/tree-final-eca9a09-20260901` was determinate in all 408 cells, but five adaptive cells failed. All three explicit compatibility Decision answers made a choice and described its strongest downside, one focused test answer reported an exact blocked outcome, and one cancellation diagnosis identified the authoritative `exportCover` side-effect boundary without naming its UI caller.

## Hypothesis

The deterministic oracle should score the semantic acts required by the prompt rather than preferred headings, successful-only outcomes, or a neighboring caller that is not necessary to establish the boundary:

- an explicit `Decision: choose ...` is a recommendation act;
- `cost` can state a trade-off when the competing benefit is also present;
- an exact blocked/failed test outcome is still an outcome report;
- an authoritative cancellation boundary does not require repeating `EditorShell` when `exportCover`, cancellation, focused evidence, and a falsifying test are all present.

Independent groups still require the actual choice, downside, compared alternatives, cancellation mechanism, authoritative boundary, focused evidence, and concrete falsifying test.

## Acceptance

Add positive tests for each equivalent form and preserve negative tests for a missing trade-off and missing concrete test evidence. Rerun the full current-only matrix at n=1 in a fresh directory. Do not use this correction as paired comparison evidence.

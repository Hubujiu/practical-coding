# Experiment: progressive capability tree

Status: **candidate implemented; validation pending**

## Observation

The previous experimental branch separated execution depth from retrieval depth, but E2 routed only to Debugging or Implementation and E3 merely deepened the same module. External retrieval was also modeled as a rung after repository-wide retrieval.

Those shapes can create two avoidable errors:

1. a broad Implementation module accumulates unrelated specialist guidance;
2. routing can imply a false sequence where specialist domains or external evidence appear only after traversing unrelated steps.

## Hypothesis

A sparse tree will preserve the small Core while improving expert behavior on genuinely deep tasks:

- depth remains `E0–E3`;
- E2 selects one event root (`diagnosis` or `engineering`);
- E3 loads one evidence-triggered specialist leaf;
- retrieval keeps depth but branches at R2 into structural or external evidence, with R3 reserved for bounded exhaustive repository claims.

Expected effect: lower unnecessary reference loading on ordinary tasks, better specialist precision on deep tasks, and fewer false routing sequences.

## Candidate change

Implemented in this commit:

- replace `implementation.md` with `engineering.md`;
- add specialist leaves for security, state, compatibility, performance, quality, and interface;
- make root + leaf the maximum normal root-context capability path;
- remove R4 and model external retrieval as an R2 branch;
- add capability-path benchmark instrumentation;
- add WikiSkill-style experience → wiki → frozen experiment separation.

## Validation matrix

Freeze before running:

- no-skill;
- accepted prior Practical Coding;
- candidate adaptive tree;
- E0/E1/E2/E3 caps;
- R0/R1/R2/R3 caps;
- parent-only vs parent+leaf ablations for claimed specialist families.

Use at least n=3 for boundary claims and include held-out repositories/tasks before accepting structural changes.

## Acceptance signals

- no stable correctness/safety/build regression;
- lower or unchanged ordinary-task context cost;
- specialist leaves show net lift over parent-only on their claimed families;
- unnecessary/missed leaf and branch-confusion rates are bounded and interpretable;
- no removed depth/node was empirically necessary often enough to restore it.

## Result

Pending fresh benchmark and real-project evidence. Do not publish comparative claims from this experiment yet.

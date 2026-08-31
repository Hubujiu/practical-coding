# Experiment: progressive capability tree

Status: **candidate implemented; validation pending**

## Observation

The previous experimental branch separated execution depth from retrieval depth, but E2 routed only to Debugging or Implementation and E3 merely deepened the same module. External retrieval was also modeled as a rung after repository-wide retrieval.

A later review found another boundary problem: E1 mixed local source inspection with execution evidence, even though source acquisition already had an independent Retrieval axis. The historical Navigation name could also be misread as a third runtime capability.

Those shapes can create avoidable errors:

1. a broad Implementation module accumulates unrelated specialist guidance;
2. routing can imply a false sequence where specialist domains or external evidence appear only after traversing unrelated steps;
3. the same caller/contract lookup can be counted as both E1 execution and R1 retrieval, making minimum-sufficient depth ambiguous;
4. Navigation can be mistaken for a peer of Retrieval rather than a structural-retrieval procedure inside it.

## Hypothesis

A sparse, orthogonal tree will preserve the small Core while improving expert behavior on genuinely deep tasks:

- execution remains `E0–E3`, with **E1 = Probe** only for one cheap executable observation/falsification step;
- source discovery belongs exclusively to retrieval depth and may produce combinations such as `E0/R2`;
- E2 selects one event root (`diagnosis` or `engineering`);
- E3 loads one evidence-triggered specialist leaf;
- retrieval keeps depth but branches at R2 into structural or external evidence, with R3 reserved for bounded exhaustive repository claims;
- `references/navigation.md` remains a compatibility filename for the deeper R2 Structural/R3 procedure, not a third runtime axis.

Expected effect: lower unnecessary reference loading on ordinary tasks, cleaner execution/retrieval calibration, better specialist precision on deep tasks, and fewer false routing sequences.

## Candidate change

Implemented on this branch:

- replace `implementation.md` with `engineering.md`;
- add specialist leaves for security, state, compatibility, performance, quality, and interface;
- make root + leaf the maximum normal root-context capability path;
- remove R4 and model external retrieval as an R2 branch;
- redefine E1 from broad focused inspection to **Probe** and move caller/reference/sibling/contract discovery fully into Retrieval;
- define Navigation as a Retrieval-internal structural/coverage procedure rather than an independent capability;
- keep manual Clarification/Decision outside adaptive routing;
- add capability-path benchmark instrumentation and explicit axis-labeling rules;
- add WikiSkill-style experience → wiki → frozen experiment separation.

## Validation matrix

Freeze before running:

- no-skill;
- accepted prior Practical Coding;
- candidate adaptive tree;
- E0/E1/E2/E3 caps;
- R0/R1/R2/R3 caps;
- explicit retrieval-only `E0/R1` and `E0/R2` controls;
- explicit one-probe E1 controls;
- parent-only vs parent+leaf ablations for claimed specialist families.

Use at least n=3 for boundary claims and include held-out repositories/tasks before accepting structural changes.

## Acceptance signals

- no stable correctness/safety/build regression;
- lower or unchanged ordinary-task context cost;
- E1 is not used to label source discovery that belongs to R1/R2;
- specialist leaves show net lift over parent-only on their claimed families;
- unnecessary/missed leaf and branch-confusion rates are bounded and interpretable;
- no removed depth/node was empirically necessary often enough to restore it.

## Result

Pending fresh benchmark and real-project evidence. Do not publish comparative claims from this experiment yet.
# Progressive depth and capability-tree evolution protocol

This protocol evaluates whether Practical Coding chooses the **lowest quality-qualified depth and the smallest useful capability path**.

The current architecture is an experiment:

- execution depth: `E0 E1 E2 E3` where E1 is **Probe**;
- retrieval depth: `R0 R1 R2 R3`;
- E2 roots: `diagnosis`, `engineering`;
- E3 specialist leaves: `security`, `state`, `compatibility`, `performance`, `quality`, `interface` where valid under the active root.

No level or node is permanent.

## 1. Quality before cost

A variant is sufficient only after correctness/safety and build/reachability gates pass. Only then compare tokens, time, tool calls, LOC, and loaded references.

A cheaper failure is not a win.

## 2. Always keep real baselines

For every candidate architecture, retain at least:

1. **no-skill**;
2. **accepted prior Practical Coding**;
3. **candidate adaptive tree**.

Use expert skills such as debugging, review, security, or design-oriented skills as informative specialist comparators on task families they actually claim to cover, not as universal baselines.

This distinguishes net skill lift from merely moving work between prompt layers.

## 3. Freeze before observing

Freeze candidate commit, task manifest, scorer/oracle, model/harness, depth-capped bundles, capability-path ablations, and repetition count before the first result is inspected.

Do not create a per-case prompt after seeing the answer.

## 4. Keep execution and retrieval orthogonal

The axes answer different questions and must not be inferred from the same action:

- **Retrieval:** how much source/context had to be acquired before the next material decision was supported?
- **Execution:** after relevant evidence was available, how much structured engineering reasoning was required?

Source discovery alone never raises execution depth. Finding/reading callers, references, siblings, contracts, implementations, or configuration belongs to R0–R3. A task may legitimately be `E0/R1` or `E0/R2`.

E1 requires a **cheap executable probe**: reproduce one behavior, exercise one path, falsify one concrete hypothesis, or run one focused check whose result determines the next action. If a case definition cannot point to such a probe, do not label retrieval activity as E1.

This boundary is part of the experiment. If E1 rarely earns a distinct minimum-sufficient role after retrieval is separated, test merging/removing it rather than broadening it back into source inspection.

## 5. Calibrate depth independently

### Execution

Run caps at `E0`, `E1`, `E2`, `E3` with retrieval permissive enough not to be the bottleneck. The first stable quality-qualified cap is the minimum sufficient execution depth.

For E1-specific cases, freeze the executable probe allowed by the cap. Retrieval-only expansion must remain available independently and must not be counted as E1 behavior.

### Retrieval

Run caps at `R0`, `R1`, `R2`, `R3` with execution permissive enough not to be the bottleneck. R2 permits the appropriate specialized branch (structural or external); R3 permits bounded exhaustive repository discovery.

External evidence is not an `R4` successor to repository search.

Use at least `n=3` determinate repetitions for boundary claims. Mark unstable cells indeterminate.

## 6. Calibrate tree nodes by ablation

Depth alone cannot tell whether a specialist node earns its context cost.

For tasks whose adaptive run selects a capability path, freeze the smallest relevant ablation set before running:

```text
parent-only
parent + claimed leaf
candidate adaptive tree
```

When useful, add one plausible sibling as a branch-confusion control. Do not test every leaf on every task.

A leaf is justified only when, on the population it claims to cover, it produces stable net quality lift over its parent or preserves quality while materially lowering cost/routing error elsewhere.

Track:

- **unnecessary root load** — E0/E1 was quality-sufficient but adaptive loaded a root;
- **unnecessary leaf load** — parent was quality-sufficient but adaptive loaded a leaf;
- **missed root/leaf** — adaptive failed at a shallower path while the frozen deeper path succeeds;
- **branch confusion** — the selected sibling fails or costs materially more while another pre-frozen path succeeds;
- **path exactness** — adaptive selects the lowest quality-qualified frozen path.

Do not infer leaf value from task nouns alone.

## 7. Observation format

`benchmarks/ladder_analysis.py` consumes aggregated JSONL after repetitions are classified.

Capped depth row:

```json
{"task_id":"bug-017","axis":"execution","arm":"cap","level":"E2","qualified":true,"tokens":4200,"duration_seconds":31.2,"tool_calls":8}
```

Adaptive row with routing instrumentation:

```json
{"task_id":"bug-017","axis":"execution","arm":"adaptive","level":"E3","qualified":true,"capability_path":["diagnosis","state"],"references_loaded":["references/debugging.md","references/specialists/state.md"],"tokens":6100,"duration_seconds":45.1,"tool_calls":12}
```

The routing fields are benchmark-only instrumentation; runtime answers need not expose labels.

## 8. Family-level analysis

Report over/under-escalation and path behavior by task family and repository, not only globally. A boundary that looks good in aggregate can systematically fail on one mechanism.

Useful families include known-target edits, retrieval-only local/structural discovery, one-probe execution uncertainty, observed-failure diagnosis, unresolved contract/invariant changes, security boundary, state/concurrency, compatibility/migration, measured performance, structural review/refactor, and material interface work.

Use mechanism labels only for analysis; do not paste benchmark-specific nouns into runtime triggers.

## 9. Retrieval-specific calibration

Measure more than tool choice:

- candidate results inspected before localization;
- source lines/files read;
- structural index/graph use when available;
- pagination/coverage for exhaustive claims;
- contraction point after localization;
- unnecessary external lookup and unnecessary repository-wide expansion.

A better retrieval path is one that reaches authoritative evidence with less irrelevant context, not one that uses a particular tool.

`references/navigation.md` is evaluated as the deeper R2 Structural/R3 coverage procedure inside this axis; do not score Navigation as a third independent depth.

## 10. Real-project experience

Benchmark tasks are necessary but not sufficient. Record real-project successes, routing mistakes, repeated user corrections, and expensive dead ends as **experience receipts** using `evolution/EXPERIENCE_SCHEMA.md`.

Do not promote one anecdote directly into `SKILL.md`. Consolidate repeated mechanisms into persistent evolution knowledge first.

## 11. Evolution loop

```text
benchmark runs + real-project receipts
                ↓
      evolution wiki knowledge
                ↓
     frozen candidate hypothesis
                ↓
 depth caps + path ablations + baselines
                ↓
       held-out validation
          ↙             ↘
       accept           reject
         ↓                ↓
 runtime Skill      retain lesson only
```

This mirrors the useful separation from WikiSkill: raw experience, accumulated maintenance knowledge, and executable Skill wording remain distinct.

## 12. Acceptance gate for this branch

Before proposing merge to `main`:

1. existing harness self-tests pass;
2. no stable correctness/safety/build regression versus accepted Practical Coding and no-skill reference points;
3. claimed depth boundaries have at least three determinate repetitions;
4. execution/retrieval labeling demonstrates the E1 Probe vs R-depth boundary rather than conflating source inspection with execution;
5. changed boundaries are tested on held-out tasks;
6. new specialist leaves have parent-vs-leaf ablation evidence on their claimed families;
7. over/under-escalation and unnecessary/missed leaf rates are reported;
8. real-project evidence is treated as calibration input, not hidden held-out proof;
9. no node survives only because the tree looks conceptually neat.
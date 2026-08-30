# Progressive ladder evolution protocol

This protocol evaluates whether Practical Coding's execution and retrieval ladders choose the **lowest level that still produces a quality-qualified result**. It is specifically for tuning escalation boundaries and deciding whether levels should be merged, removed, or split.

The current level names are hypotheses:

- Execution: `E0 E1 E2 E3`
- Retrieval: `R0 R1 R2 R3 R4`

Do not optimize for preserving these names or counts.

## 1. Quality before cost

A rung is sufficient only if it passes the same hard gates used by the main harness:

1. correctness and safety;
2. build/reachability when applicable;
3. only then efficiency.

A cheaper failure is never a sufficient lower rung.

## 2. Freeze variants before observing results

For a calibration cycle, freeze:

- candidate Skill commit;
- task manifest;
- scorer/oracle versions;
- model and harness configuration;
- capped Skill bundles for every level being tested.

Do not create a per-case cap after looking at that case's result. Caps must be mechanically generated or otherwise fixed for the complete matrix before the first model run.

## 3. Calibrate the axes independently

Execution and retrieval interact, so estimate each boundary while keeping the other axis permissive enough not to be the bottleneck.

### Execution calibration

Run variants capped at `E0`, `E1`, `E2`, and `E3` while allowing normal retrieval. For each task, the first level that quality-qualifies is its **minimum sufficient execution level**.

### Retrieval calibration

Run variants capped at `R0`, `R1`, `R2`, `R3`, and `R4` while allowing normal execution. For each task, the first level that quality-qualifies is its **minimum sufficient retrieval level**.

A cap means stronger behavior cannot be used, not that the model is told which answer is expected.

## 4. Repetitions

Use at least `n=3` determinate repetitions for boundary claims. A capped cell is quality-qualified only when its hard-gate result is stable under the project's current stability policy. If stochastic disagreement prevents a stable judgment, mark the task/axis indeterminate rather than forcing a minimum rung.

Held-out tasks are required before treating a tuned boundary as general rather than regression-specific.

## 5. Adaptive run

After the capped matrix is frozen and run, execute the normal adaptive Skill on the same tasks.

Record its selected execution/retrieval level through benchmark-only instrumentation. Do not require runtime user-facing answers to expose ladder labels.

For native behavior, use mechanical evidence where possible: references loaded, retrieval scope/tool traces, files/results inspected, and worker dispatches. If E0 versus E1 cannot be inferred mechanically, use a dedicated classification probe in the benchmark rather than changing production output format.

## 6. Required observation format

`benchmarks/ladder_analysis.py` consumes aggregated JSONL observations after repeated cells have already been classified as quality-qualified or not.

Capped row:

```json
{"task_id":"bug-017","axis":"execution","arm":"cap","level":"E2","qualified":true,"tokens":4200,"duration_seconds":31.2,"tool_calls":8}
```

Adaptive row:

```json
{"task_id":"bug-017","axis":"execution","arm":"adaptive","level":"E3","qualified":true,"tokens":6100,"duration_seconds":45.1,"tool_calls":12}
```

Use one aggregated row per task/axis/arm/level. Keep raw repetitions in the normal benchmark artifacts.

## 7. Boundary metrics

For every scorable task/axis:

- **minimum sufficient level:** lowest capped level that quality-qualifies;
- **exact:** adaptive level equals the minimum sufficient level and qualifies;
- **over-escalation:** adaptive qualifies but selects a higher level than minimum sufficient;
- **under-escalation:** adaptive selects below the minimum sufficient level and does not qualify while a higher capped level does;
- **quality failure:** adaptive fails even though it selected at or above a known sufficient cap;
- **inconsistent:** adaptive qualifies below the observed minimum capped level; investigate stochasticity/instrumentation before changing the Skill.

Report rates by task family, not only globally. A boundary can be correct overall and still systematically wrong for one family.

## 8. Tune boundaries before prose

When a pattern appears, classify it before editing:

- **Over-escalation cluster:** tighten the escalation condition or improve de-escalation/contraction.
- **Under-escalation cluster:** relax the escalation condition or expose the blocker earlier.
- **Retrieval over-expansion:** tighten scope transition or contraction conditions.
- **Retrieval under-expansion:** allow the next scope when the current information test fails.

Do not add task nouns or benchmark-specific phrases merely to turn public cells green.

## 9. Tune the number of levels

A level is a merge/removal candidate when, across a sufficiently varied held-out population:

- it is rarely or never the minimum sufficient level;
- moving directly from its lower neighbor to upper neighbor does not create a material quality cliff;
- its presence adds measurable context/process cost or routing error.

A level is a split candidate when it repeatedly contains two separable clusters with different minimum sufficient behavior and a stable observable condition can distinguish them before execution.

Do not split a level merely because task descriptions look different.

## 10. Persistent evolution record

Every structural change should create an experiment record under `evolution/experiments/` with:

- observed pattern and evidence IDs;
- hypothesis;
- exact boundary/level change;
- expected quality and cost effect;
- frozen benchmark manifest;
- result;
- accept/reject decision.

Rejected changes move or are summarized under `evolution/rejected/`. Their lessons remain available to future maintainers even though runtime Skill text rolls back.

## 11. Acceptance for this experimental branch

Before proposing merge to `main`:

1. existing harness self-tests pass;
2. no public correctness/safety/build regression against the accepted baseline;
3. ladder calibration has at least three determinate repetitions per claimed cell;
4. at least one held-out task population tests the new boundaries;
5. over/under-escalation is reported separately for execution and retrieval;
6. no level-count change is justified only by prompt aesthetics.

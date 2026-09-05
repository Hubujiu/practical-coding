# Execution-state gate-role correction after the first remediated n=1 run

Status: `candidate-pending-fresh-rerun`

## Evidence

The remediated standard `n=1`, `workers=1` matrix produced 24 determinate cells:

- `full-history`: 6/6;
- `state-history-free`: 6/6;
- `no-skill-full-history`: 6/6;
- `state-shadow`: 5/6.

The history-free arm also passed the final client transport audit and the history-pointer check. The published analyzer nevertheless returned:

- `quality_gate = FAIL`;
- `state_semantic_gate = FAIL`;
- `execution_state_model_gate = FAIL`.

Inspection of the analysis implementation showed that both blocking gates pooled `state-shadow` with `state-history-free`. This conflicts with the frozen protocol: history-free is the release candidate, full-history is its ablation baseline, and state-shadow is a reconstruction diagnostic that cannot establish bounded context.

The same run reported a negative short-horizon cost signal for history-free relative to full-history:

- uncached input tokens: 78,118 versus 50,736;
- cell-duration sum: 172.60 seconds versus 154.57 seconds.

These `n=1` values are diagnostic only. They do not justify a token/latency claim or an immediate Skill/schema/tree change, and the bounded 10/25/50/100 profile has not yet run.

## Causal claim

The overall FAIL is not evidence that the history-free candidate regressed: its six candidate cells passed. It is caused by a gate-role error that lets a non-blocking diagnostic arm veto the candidate and by a formal-status rule that does not enforce the protocol's `n>=3` release requirement.

## Atomic proposal

Change only the analysis/reporting contract:

1. compare `state-history-free` with `full-history` in the blocking quality gate;
2. evaluate blocking state semantics and history pointers only for `state-history-free`;
3. report `state-shadow` quality/state/pointer outcomes under a separate non-blocking diagnostic gate;
4. require a complete paired, determinate standard four-arm matrix at `n>=3` before formal cost claims;
5. keep `execution_state_model_gate` pending until candidate quality/transport, repeated evidence, token, latency, and bounded-context gates are all resolved;
6. expose the exact shadow semantic failure details in generated reports.

Do not change:

- `SKILL.md` or any reference node;
- automatic tree topology;
- execution-state schema or canonical validators;
- case prompts or required evidence;
- scorer normalization or artifact rules;
- raw benchmark results.

## Expected benefit

The report will distinguish three independent questions:

- does history-free preserve quality and state semantics?;
- does shadow reveal a state-update problem while history remains available?;
- after `n>=3` and horizon runs, does history-free reduce token/time cost while keeping the client request bounded?

This prevents a diagnostic shadow failure from being misreported as a history-free release failure while preserving the failure as evidence.

## Falsifier

Reject this change if the frozen protocol explicitly defines state-shadow as a release-blocking candidate, or if the revised analysis can hide a failure in `state-history-free`, an indeterminate required cell, a missing four-arm repetition, a transport failure, or an invalid history pointer.

## Validation plan

Before any new model call:

- add deterministic tests showing a shadow-only failure remains visible but non-blocking;
- add tests showing a history-free failure remains blocking;
- add tests showing `n=1` cannot produce a formal pass or cost claim;
- add tests for paired/determinate `n>=3` completeness;
- run existing execution-state and benchmark unit tests plus all deterministic self-tests.

After the patch is frozen:

1. re-analyze the old `n=1` result only as historical diagnostic evidence; do not relabel it as a formal pass;
2. run a fresh complete standard `n=1` matrix under the new analysis identity;
3. run bounded `n=1` at horizons 10/25/50/100 to locate request growth and any cost crossover;
4. proceed to standard `n>=3` only if the candidate gates remain clean and the bounded run justifies the expense;
5. modify activation/schema/Skill only from repeated mechanism-level evidence. Do not modify the router tree unless failures independently cluster on an observable execution-boundary signal.

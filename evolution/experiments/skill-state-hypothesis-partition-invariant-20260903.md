# Execution-state hypothesis partition invariant

Status: `hypothesis-frozen-before-runtime-patch`

## Evidence

The standard four-arm `n=1`, `workers=1`, `codex-sse-v1` report against
`e6cc9caa456767b3e05dbff59474aa7014146cbf` contains one state-shadow semantic
failure in `rejected-cache-hypothesis`: the final state retained `h-cache` in
`hypotheses.active` after also classifying it as rejected. The history-free arm
completed the same case correctly. The report otherwise records 24/24
determinate cells, a passing history-free quality/state/history-pointer/transport
candidate gate, and no tree-boundary failure.

The raw benchmark artifacts remain local and are not rewritten by this change.
This receipt records only the reported mechanism and the exact candidate ref.

## Causal claim

`runtime/skill_state.py` validates `hypotheses.active` and
`hypotheses.rejected` as independent string maps, so the same hypothesis ID can
legally appear in both partitions. JSON Merge Patch then permits a model to add a
rejected entry while accidentally omitting the `null` deletion of the active
entry. The resulting state is structurally valid but semantically contradictory.

## Observable signal

Before a successor state is accepted, compute the exact-key intersection of
`hypotheses.active` and `hypotheses.rejected`. A non-empty intersection is a
deterministic invalid-state signal available without inspecting task wording or
benchmark labels.

## Exact target

- `runtime/skill_state.py`: canonical state validation only.
- `tests/test_skill_state_hardening.py`: ordinary deterministic regression tests.
- `docs/SKILL_STATE.md`: schema invariant and retry behavior.

No change is proposed to `SKILL.md`, router topology, state shape/schema version,
benchmark cases, scorer, runner, thresholds, or stored benchmark results.

## Proposed patch

Require `set(hypotheses.active).isdisjoint(hypotheses.rejected)`. Reject the
complete successor with a stable error listing the overlapping IDs. Because
`apply_transition()` validates the full successor before exposing its action, the
existing host retry path will keep the original canonical state and request a
corrected patch.

## Expected benefit

- A hypothesis has one current lifecycle classification, never both live and
  rejected.
- An omitted merge-patch deletion fails closed instead of becoming durable state.
- The rule applies to every task and does not encode the observed case ID or its
  answer terms.

## Falsifier

Reject or revise this intervention if any supported workflow intentionally needs
one exact hypothesis ID in both partitions, if deterministic state/host tests
regress, or if a fresh model matrix shows a quality regression that cannot be
attributed to infrastructure. Additional retry cost must remain visible; semantic
correctness is not permission to hide token or latency regressions.

## Baseline and validation plan

Baseline ref: `e6cc9caa456767b3e05dbff59474aa7014146cbf`.

Before model work:

```text
python -m py_compile runtime/skill_state.py tests/test_skill_state_hardening.py
python -m unittest tests.test_skill_state_hardening tests.test_skill_state_host
python -m unittest benchmarks.test_skill_state_runtime
python benchmarks/skill_state_validation.py --self-test
```

After the patch is frozen, rerun a new standard four-arm `n=1` matrix from an
empty output directory. Do not resume or relabel the previous matrix. The minimum
iteration acceptance conditions are:

- all 24 cells determinate;
- history-free quality, state semantics, history pointer, and client transport
  remain `PASS`;
- no accepted state contains overlapping active/rejected hypothesis IDs;
- the shadow diagnostic either passes or records only a different independently
  diagnosed mechanism;
- token, latency, and bounded-context claims remain separate and are not promoted
  from this deterministic invariant.

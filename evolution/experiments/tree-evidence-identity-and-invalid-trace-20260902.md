# EXP-20260902 — Evidence identity and invalid-trace robustness

Status: **frozen before scorer/analyzer edit**

## Observation

The complete paired n=3 artifact at `benchmark-results/tree-final-67f2f5c-20260901` produced all 252 cells but failed delivery. Three of four adaptive quality failures were contract-equivalent evidence forms:

- `avifEncoder.ts` plus the full worker call boundary was rejected because only the exact function token `encodeAvif` was accepted;
- the authoritative `runCommand` transition and focused executor test were rejected because only the concrete class token `DefaultPluginOperationExecutor` was accepted;
- an explicit Decision run loaded the correct `references/manual/decision.md` command and declared `manual=decision`, but the trace shortened the identity to `manual/decision.md`.

The fourth failure selected a retired node. Trace validation rejected it correctly, but `tree_analysis.py` crashed with `KeyError` instead of recording an invalid trace.

## Hypothesis

Score authoritative boundary identities and observed reference reads rather than a single spelling, while preserving independent evidence groups and applying the same observed-read rule to detect forbidden spontaneous manual loads. Treat any selected node absent from the active topology as `invalid_trace` in analysis.

This iteration changes only scorer/analyzer contracts. Retired runtime-reference isolation is a separate subsequent hypothesis.

## Acceptance

- positive tests cover `avifEncoder`, `runCommand`, root-elided manual identity, and an observed correct manual-reference read;
- a negative test proves an automatic task that actually reads a manual reference is still rejected;
- analyzer test proves an unknown retired node produces `invalid_trace` without crashing;
- all deterministic gates pass, followed by a fresh complete current-only n=1 run.

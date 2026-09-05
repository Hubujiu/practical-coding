# EXP-20260901 — Tree oracle semantic equivalence

Status: **frozen before second scorer patch**

## Evidence pointers

- `benchmark-results/tree-delivery-n1-oraclefix-20260901-111838/results.jsonl`
- `benchmark-results/tree-delivery-n1-oraclefix-20260901-111838/analysis.json`
- `evolution/experiments/tree-oracle-alignment-20260901.md`
- `evolution/wiki/benchmark-oracle-contracts.md`

## Causal claim

The first punctuation/file-list correction remained too lexical. The deterministic scorer still rejects semantically complete evidence when a model names the cancellation operation and observed test behavior without repeating an implementation type/file token, or answers a manual Decision request in Chinese using the equivalent labels “推荐” and “权衡”.

## Observable signal

`missing_evidence_groups` contains only a language-specific heading or an implementation identifier even though the answer contains the requested semantic act, concrete side-effect boundary, existing-test observation, falsifying test, valid manual trace, and clean workspace.

## Exact target and patch shape

- Target only evidence alternatives in `benchmarks/tree_cases.py` plus deterministic regression tests and wiki evidence.
- Accept Chinese recommendation/trade-off equivalents for manual tasks.
- Accept concrete cancellation-operation and existing/focused-test evidence without requiring one exact class or filename.
- Retain independent required groups for the controller/UI caller, `exportCover`, a falsifying probe/test, and both compared manual alternatives.
- Do not change prompts, runtime Skill files, topology, repositories, model, or trace enforcement.

## Expected benefit and falsifier

Expected benefit: language- and formatting-equivalent answers pass without weakening the requirement for a concrete diagnosis, test, recommendation, comparison, and strongest trade-off.

Falsifier: an answer missing the cancellation operation, focused-test evidence, recommendation, or trade-off passes; or any deterministic contract test regresses.

## Baseline and benchmark plan

- baseline ref: current scorer patch working tree based on `31ba37c9c324ff5863ee237a8c89203f4405fbe9`
- invalidated artifact: `benchmark-results/tree-delivery-n1-oraclefix-20260901-111838`
- add positive semantic-equivalence tests and retain negative evidence tests;
- run all deterministic tree/evolution tests;
- rerun the full 15-task, 106-cell current-only n=1 matrix in a fresh directory.

## Acceptance criteria

1. The two observed semantically complete answers have no missing evidence groups under the corrected oracle.
2. Negative answers without a concrete test or trade-off still fail.
3. All deterministic checks pass and runtime Skill/tree files remain unchanged.
4. The new full n=1 artifact has zero indeterminate cells before any delivery/final-run decision.

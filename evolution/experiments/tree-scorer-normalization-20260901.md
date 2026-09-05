# EXP-20260901 — Tree scorer normalization

Status: **frozen before third scorer patch**

## Evidence pointers

- `benchmark-results/tree-delivery-n1-semantic-20260901-120715/results.jsonl`
- `benchmark-results/tree-delivery-n1-semantic-20260901-120715/analysis.json`
- `evolution/wiki/benchmark-oracle-contracts.md`

## Causal claim

Two scorer boundaries remain incorrectly platform- or identifier-specific: manual-reference enforcement compares only POSIX separators even though the Windows harness emits backslashes, and focused-test evidence requires repository filenames even when the answer reports the focused suite and its uncovered boundary.

## Observable signal

- A manual answer has no missing evidence groups, emits `manual=decision`, and loads the correct absolute Windows path, but `manual_contract_ok` is false.
- A diagnosis states focused-suite outcome and the missing falsifying test while only the filename evidence group remains missing.

## Exact target and patch shape

- Normalize reference paths to forward slashes before manual reference checks in `tree_validation.py`.
- Make the cancellation focused-test group require generic focused/suite/test evidence instead of a specific filename.
- Add deterministic positive and negative regression tests.
- Do not change runtime Skill files, topology, prompts, repositories, or model settings.

## Expected benefit and falsifier

Expected benefit: equivalent Windows/POSIX reference paths enforce the same manual contract, and focused-test evidence is scored by the requested act rather than one filename.

Falsifier: a trace loading a non-manual reference passes, or a cancellation answer without any focused test/suite evidence passes.

## Baseline and benchmark plan

- baseline ref: current scorer working tree based on `31ba37c9c324ff5863ee237a8c89203f4405fbe9`
- invalidated artifact: `benchmark-results/tree-delivery-n1-semantic-20260901-120715`
- run all deterministic tree/evolution tests;
- rerun the complete 15-task, 106-cell current-only n=1 matrix in a fresh directory.

## Acceptance criteria

1. Absolute Windows and POSIX manual reference paths both satisfy the same requested manual contract.
2. A focused-suite diagnosis with a concrete falsifying test passes; a no-test diagnosis fails.
3. All deterministic checks pass, no runtime file changes, and the full rerun has zero indeterminate cells.

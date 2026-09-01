# EXP-20260901 — Tree benchmark oracle alignment

Status: **frozen before scorer patch**

## Evidence pointers

- `benchmark-results/tree-delivery-n1-20260901-103036/results.jsonl`
- `benchmark-results/tree-delivery-n1-20260901-103036/analysis.json`
- frozen cover-atelier commit `fc3b12b3a944f45b5a1d19963e29307d95b120fb`
- `evolution/wiki/benchmark-oracle-contracts.md`

## Causal claim

The first tree n=1 run contains three false failures because the deterministic oracle is narrower than the frozen task contract: two manual Decision answers state the strongest trade-off without the exact punctuation token `Trade-off:`, and the cancellation diagnosis cites the repository's existing cancellation test plus the correct download-side-effect boundary while the oracle requires unrelated UI/progress test filenames.

## Observable signal

An answer satisfies the prompt's semantic evidence and manual-mode trace contract, but `missing_evidence_groups` contains only formatting punctuation or a non-authoritative test filename that the prompt never required.

## Exact target and patch shape

- Target only `benchmarks/tree_cases.py` and its deterministic tests.
- Accept the semantic `trade-off` term independently of punctuation.
- Accept the frozen repository's existing cancellation-focused `avifEncoder.test.ts` as a valid focused-test evidence path alongside the existing progress tests.
- Add regression assertions that representative semantically valid answers score successfully.
- Do not change `SKILL.md`, router references, topology, prompts, repositories, or model settings.

## Expected benefit and falsifier

Expected benefit: semantically compliant answers cease to fail for punctuation or an unjustified file-name oracle while truly missing recommendation, trade-off, cancellation-path, or test evidence still fails.

Falsifier: the relaxed groups allow an answer without a real trade-off or without a concrete focused cancellation test, or any existing deterministic tree test regresses.

## Baseline and benchmark plan

- baseline ref: `31ba37c9c324ff5863ee237a8c89203f4405fbe9`
- invalidated exploratory artifact: `benchmark-results/tree-delivery-n1-20260901-103036`
- run focused deterministic scorer tests after the patch;
- then rerun the full frozen current-only tree matrix at n=1 in a fresh directory;
- accept the scorer patch only if all deterministic tests pass and the rerun has zero indeterminate cells with no new contract regression.

## Acceptance criteria

1. Representative colon-free strongest-trade-off answers pass the manual evidence group while manual trace enforcement remains unchanged.
2. A cancellation answer naming `avifEncoder.test.ts`, the download boundary, and a falsifying test passes; an answer with no test evidence still fails.
3. No runtime Skill/tree file changes.
4. The full n=1 rerun is completed before any runtime optimization decision.

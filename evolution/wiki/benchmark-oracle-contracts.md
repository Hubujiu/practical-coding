# Mechanism: benchmark prompts and deterministic oracles must encode the same contract

## Claim

A deterministic scorer is invalid when it rewards behavior forbidden by the task prompt or rejects semantically equivalent evidence solely because of formatting/tokenization.

## Observable trigger

- The delivered answer or code satisfies the explicit task contract, but the scorer's safety/correctness predicate requires a contradictory sibling change.
- An evidence group represents a concept but accepts only one punctuation/casing/spacing form without a semantic reason.

## Supporting receipts

- `trace-ttl-zero` explicitly required no change to sibling cache semantics, while the scorer required cache TTL zero to change from the seeded default behavior to zero.
- `sa-sensitive-security` described the model interceptor chain and proved rejection-before-model-call, but the scorer accepted only the unspaced token `ModelInterceptor`.

## Affected nodes/boundaries

Benchmark scorer/oracle contract only. These observations do not justify runtime wording changes.

## Candidate experiments

- Add unit assertions that the canonical oracle preserves every explicit sibling/non-goal contract in the prompt.
- Evidence groups may include semantically equivalent lexical forms when formatting is not part of the requirement.

## Current status

Applied to the n=1 iteration harness before the second candidate run.

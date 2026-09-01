# Mechanism: benchmark prompts and deterministic oracles must encode the same contract

## Claim

A deterministic scorer is invalid when it rewards behavior forbidden by the task prompt or rejects semantically equivalent evidence solely because of formatting/tokenization.

## Observable trigger

- The delivered answer or code satisfies the explicit task contract, but the scorer's safety/correctness predicate requires a contradictory sibling change.
- An evidence group represents a concept but accepts only one punctuation/casing/spacing form without a semantic reason.

## Supporting receipts

- `trace-ttl-zero` explicitly required no change to sibling cache semantics, while the scorer required cache TTL zero to change from the seeded default behavior to zero.
- `sa-sensitive-security` described the model interceptor chain and proved rejection-before-model-call, but the scorer accepted only the unspaced token `ModelInterceptor`.
- `evolution/raw/sessions/2026-09-01-tree-n1-oracle-defects.md`: two explicit Decision answers satisfied the manual trace and strongest-trade-off contract but failed only because the evidence group required `Trade-off:` with exact punctuation.
- The same receipt records a cancellation diagnosis that identified the real download side-effect boundary and existing cancellation test, while the scorer required UI/progress filenames not required by the prompt.
- `evolution/raw/sessions/2026-09-01-tree-n1-semantic-oracle.md`: the first correction still rejected a Chinese recommendation/strongest-trade-off answer and a cancellation answer that named `abort()`, existing test coverage, and the exact side-effect boundary without repeating the scorer's preferred identifiers.
- `evolution/raw/sessions/2026-09-01-tree-n1-path-normalization.md`: Windows backslashes caused a correctly loaded manual reference to fail enforcement, and a focused-suite result still failed an identifier-specific test-file group.

## Affected nodes/boundaries

Benchmark scorer/oracle contract only. These observations do not justify runtime wording changes.

## Candidate experiments

- Add unit assertions that the canonical oracle preserves every explicit sibling/non-goal contract in the prompt.
- Evidence groups may include semantically equivalent lexical forms when formatting is not part of the requirement.
- Test-file evidence groups should enumerate authoritative frozen-repository tests relevant to the requested boundary, not force a neighboring layer whose filename happens to look related.
- When response language is not part of the task contract, evidence groups should admit equivalent recommendation/trade-off labels in supported response languages; independent negative groups must still require both acts.
- When identifiers are not themselves the contract, accept the concrete operation and observed test behavior while retaining separate groups for the caller, authoritative function, side effect, and falsifying test.
- Normalize platform-dependent path separators at the scorer boundary before enforcing reference ownership.
- Score “inspected focused tests” as an evidence act (`focused`/`suite`/test path), leaving the separate falsifying-test group to require a concrete test proposal.

## Current status

Applied to the earlier progressive-tree harness and refined through three falsifying n=1 runs during the 2026-09-01 evolvable-tree iteration. Artifacts produced before the latest scorer-normalization correction are invalid for delivery comparison and remain only diagnostic evidence.

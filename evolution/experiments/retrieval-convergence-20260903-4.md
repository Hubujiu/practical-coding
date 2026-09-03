# Retrieval convergence — iteration 4: select the source corpus before content search

Status: **candidate-not-applied**

## Frozen hypothesis

- Baseline SHA: `205f5fe76ee88b951f9a6690d2a7bfbe0bfe0d15`; runtime matches the original accepted `d7c4a93a9d50b1305407d323b718b45e19b0f2fe`. The preceding source-reuse candidate was rejected and fully rolled back before this independent hypothesis.
- Evidence: complete iteration 3 attempt2 baseline/candidate artifacts and semantic audits, summarized in `benchmarks/results/retrieval-convergence/20260903-iteration-3.json`. Memory reset baseline event 1 and candidate event 1 each return 1,048,576 bytes: mixed relevant project declarations and irrelevant minified vendored webviewer implementation. Sensitive rejection baseline event 2 and candidate event 2 likewise enter a broad content corpus and return large unrelated source. These are different contract questions; previous frozen iteration 2 evidence also recorded early discovery output of 190,711–214,709 bytes on a separate repository's token-rotation boundary. Do not infer a global rule from one exceptional cell.
- Causal mechanism: a repository root is a physical container, not the relevant source corpus. Content search over every tracked/generated/vendor file emits irrelevant implementation before the agent has a chance to narrow. Selecting project-owned scope from known request clues reduces this first output without inserting the rejected mandatory filename-discovery round. This differs from source reuse (iteration 3) and post-discovery bounded evidence (already accepted runtime).
- Observable trigger: about to emit source-content matches, using any available paths, symbols, or language clues from the current request. Scope can be a known source root or a file-type/path filter in the same query; no separate tool round is required.
- Exact runtime surface: `SKILL.md`, Retrieval Policy only, one paragraph immediately before the existing paragraph beginning “Once candidate paths or symbols are known”.
- Exact proposed paragraph: **Before emitting content matches, use available path, symbol, or language cues to choose an initial project-owned scope; exclude generated, minified, and vendored files, dependency caches, and build outputs unless the task targets them or an unresolved contract requires that specific boundary.**
- Ordinary project-owned contracts, callers, tests, configuration and documentation remain eligible; the rule does not permit skipping authoritative evidence or necessary dependency implementation. A request explicitly about generated/vendor code itself supplies the relevant boundary. Unknown scope may still use existing bounded/ranked discovery. No mandatory extra locating stage or universal file-extension restriction is introduced.
- Unchanged: all other Skill text/references, Router/topology/automatic/manual modes, cases, scorer, model/reasoning, fixtures, verification requirements and frozen sharded runner/observer. Execution-state/history-free remains retired. No retrieval framework, tool installation, helper runtime, special case ID or gold-answer keyword.
- Expected effect: prevent unrelated source dumps at the first query, reduce cumulative input and output while preserving sufficient evidence and quality. Later whole-file and dependency reads may remain unchanged; this transfer limit can fail the cost gate. No benefit is assumed.
- Falsifiers: required callers/configuration/documentation or external contracts are missed; content filtering becomes a mandatory extra round; dump output is only moved to another tool; a generated/vendor owner is ignored; or any fixed quality/cost gate fails. Once candidate results are observed, do not reword this hypothesis.

## Frozen evaluation

- Use the same repaired harness and observation 1.3 frozen at `ffa6b655aa683bb891cc50e0cdb7efa7ae333cd8`: model `gpt-5.6-luna`, medium reasoning, Codex CLI 0.145.0, Python 3.13.14, timeout 600 seconds, eight concurrent shards, at most five cells per shard. Identical case assignment, dependencies/build conditions and measurement code in both arms. Fresh outputs; no retry/resume or selective result replacement.
- Fresh complete current-only n=1: 54 cells (15 adaptive, three ceilings for each of 13 ordinary cases). Baseline directory `benchmark-results/retrieval-iteration-4-baseline-n1`; candidate directory `benchmark-results/retrieval-iteration-4-candidate-n1`. Run baseline before applying the paragraph. Freeze its three highest-output ordinary adaptive task IDs, result hash, audit hashes and unchanged gate arithmetic before candidate execution. Do not replace tail cases based on candidate outcomes.
- Require complete determinate comparable identities; zero timeouts/scorer crashes/usage or shell decoding gaps, at least 99% completed output coverage and audit of material unknown output. Preserve automatic estimates; resolve tail event attribution using the same semantic audit contract in `retrieval-continuation-20260903.md`.
- Apply the already frozen manual quality requirement: necessary authoritative owner/caller/contract/test evidence must survive. For the executor task, recognize the intended Error/crash marker and startup recovery contract rather than misdiagnosing every nonterminal state as a defect. Machine passes alone are insufficient. No case/scorer edits.
- Whole-file/dependency audits use actual executed operations/output: explicit file reads proven to return a full file count conservatively even under a generous cap; filtered content searches remain searches. Full unfiltered bytecode implementation dumps count as whole/dependency; source materialized internally but emitted only as bounded matches is bounded/focused. Policy-rejected operations do not count as executed source reads. Mixed event category totals retain full event bytes, without invented output apportionment. Apply the same definitions to both arms.

## Required non-time n=1 gates

1. Infrastructure and audit completeness above.
2. No paired machine quality regression; all traces legal, explicit manual correct, spontaneous manual zero, clean fixtures, and candidate manual tail quality passes.
3. Frozen-tail paired median tool-output ratio <=0.70. Audited broad-after-first-project-source total <=50% of baseline; zero baseline requires zero candidate, with no positive reduction claim. Tail totals of duplicate commands, whole-file bytes, dependency-source bytes and >64 KiB output events do not increase.
4. Tail paired median input-token ratio <=0.90; tail uncached-input total does not increase; all 54 paired input-token median ratio <=1.02 and tool-call median ratio <=1.00. Zero-to-positive regressions are never omitted.

Duration is telemetry only; no latency gate or separate serial latency rerun. Cache differences cannot substitute for input work reduction.

## Frozen n=3 gate and disposition

Only complete n=1 passage permits committing the exact candidate and running the full paired n=3 matrix (252 cells, same conditions, 51 shards with at most eight active and five cells each). The immediate baseline ref above is authoritative even under a legacy variant label. All cells must be determinate; adaptive quality must not decrease against immediate baseline or no-skill, with legal traces, correct explicit manual and no spontaneous manual, clean fixtures and sufficient caller/contract/test evidence. Compare all 45 adaptive/baseline pairs for fixed overhead and nine frozen-tail pairs for cost. Apply the same output/input/tool thresholds and non-increase counters; improvement must hold in at least two repetitions and more than one tail task. No threshold or oracle change.

On failure preserve evidence, reject and restore the entire paragraph before an independently justified new iteration. On full passage update wiki/impact/log, sanitize evidence, commit, push and verify, then stop successfully. The user's until-success continuation overrides the old iteration count stop, not any acceptance gate.

## Results (outside the frozen hypothesis)

Pre-freeze independent review confirmed the mechanism is source-corpus selection rather than an added locating stage. The exact paragraph incorporates explicit task-target and insufficient-clue/initial-scope boundaries to preserve required generated/dependency and cross-language evidence. Pending fresh baseline. Candidate not applied.

# Skill impact tracker

Record every maintenance-time Skill proposal after validation. Rejected proposals remain here so later iterations do not repeat them without new evidence.

Each entry should include:

- date / iteration;
- hypothesis or experiment path;
- target Skill/node;
- baseline ref and benchmark artifact;
- candidate ref or unified diff;
- baseline and candidate required quality scores;
- relevant cost metrics;
- decision: `Accepted` or `Rejected`;
- rejection reason or acceptance rationale.

## Historical note

Experiments before this tracker was introduced remain authoritative in their existing benchmark artifacts and `evolution/rejected/` records; do not invent missing scores retroactively.

## 2026-09-03 — retrieval output instrumentation

- hypothesis: `evolution/experiments/retrieval-convergence-20260903-1.md`
- baseline: `d7c4a93a9d50b1305407d323b718b45e19b0f2fe`; branch `experiment/retrieval-convergence`
- target: benchmark metadata only; runtime prompts, topology, cases and answer scorers unchanged
- deterministic evidence: 41 tests pass, tree self-test passes; replay of 252 historical records preserves every original field
- artifact: `benchmark-results/retrieval-iteration-1-instrumentation-replay/`; original results SHA-256 `fdba2d83ef600fb5e541f2e302b0a9ee7dc063e6a249cf740cba4949fb07776c`
- coverage: recorded output available for 1,844/1,845 tool events; mixed category bytes overlap and possible truncation is flagged
- initial deterministic decision: `Accepted` for observation only; subsequently **Inconclusive / infrastructure_indeterminate** for gate readiness
- frozen instrumentation: `6475c33cca967ffafadf09ee484ed84e2feb49a7`
- fresh artifact: `benchmark-results/retrieval-iteration-1-baseline-n1/`; 4/54 cells complete, all four quality/trace passes, 50 missing; explicit manual boundary untested
- failure: current CLI mixed-quote command rendering hides two source reads; 5/5 output events measured but 3/5 classified `other`. Byte coverage alone cannot establish convergence metrics.
- runtime outcome: no Skill candidate, no frozen tail, no paired comparison, no n=3, no cost claim; instrumentation and raw artifacts retained, runtime identical to the original baseline
- termination: insufficient n=1 measurement coverage and incomplete baseline; loop stopped after one instrumentation iteration, with no candidate repair or second iteration
- record: `evolution/rejected/retrieval-instrumentation-20260903.md`; require independently validated general command classification before future cost acceptance

### User-directed repair and continuation

- repair hypothesis: `evolution/experiments/retrieval-instrumentation-repair-20260903.md`
- decoder 1.1 uses standard shell-word argv decoding, with separate command scope and pipeline-filter handling; archive stream reads are recognized as source retrieval
- verification: 45 tests and tree self-test pass; final replay 252 records preserves original fields, shell decode failures 0, original missed source reads recovered
- artifact: `benchmark-results/retrieval-iteration-1-repair-frozen-replay/`; unclassified bytes 0.68%, with coverage limits retained
- decision: `Accepted` for repaired instrumentation; iteration 1 closed, no runtime patch or cost claim. The original interrupted-run report remains an invalid diagnostic, not a reused baseline.

## 2026-09-03 — path-only retrieval discovery rejected

- hypothesis: `evolution/experiments/retrieval-convergence-20260903-2.md`; rejection: `evolution/rejected/retrieval-path-only-discovery-20260903.md`
- target: one `SKILL.md` Retrieval Policy line; baseline `9d742b22fadda8bdd78f84bc58b955cf628a1cc0`; candidate uncommitted on `af7dc97fd16ebad90052280819cc0c6a0008bb02`, exact rejected patch retained
- artifacts: fresh `benchmark-results/retrieval-iteration-2-baseline-n1/` and `benchmark-results/retrieval-iteration-2-candidate-n1/`; 54/54 determinate quality passes each, all traces valid, explicit manual 2/2 each, spontaneous manual zero, clean fixtures
- tail paired medians: recorded output -58.4%, input tokens +67.4%, tool calls +41.2%; tail uncached input total +2.9%; all-cell input paired median +6.4%, tool-call paired median unchanged
- mechanism: dependency output and duplicate commands increase; whole-file output and >64 KiB events decrease. Output savings do not establish context savings.
- decision: **Rejected**, runtime patch fully rolled back, no n=3 or third runtime candidate. Cost-ineffective termination applies; duration is telemetry only per the user's later instruction and does not determine the final decision.
- observation closeout: 48 tests and tree self-test pass; metrics 1.2 fixes platform build wrappers and literal source-path interpolation. Offline replay of all 108 transcripts preserves every non-observation field and direct cost; original frozen 1.1 artifacts remain unchanged. Corrected tail broad-after-read estimates 1 -> 3 still fail; compound-command partial-success limitations remain disclosed.
- durable lesson: `evolution/wiki/retrieval-output-and-context-cost.md`; sanitized report: `benchmarks/results/retrieval-convergence/20260903-iteration-2.json`

## 2026-09-01 — explicit maintenance skills

- hypothesis: `evolution/wiki/maintenance-trigger-isolation.md`
- target: maintenance orchestration only; no runtime Skill/tree node changed
- baseline ref: `118acd81cb0e26f4f8087555c3bd89cbf45c9d30`
- benchmark: `benchmarks/results/evolution-workflow/2026-09-01.json`
- baseline runtime surface: unchanged by candidate
- candidate maintenance-contract score: `28/28 = 1.000`
- decision: `Accepted`
- rationale: the new maintenance skills are isolated from automatic topology and the deterministic contract gate passes perfectly; runtime model-backed inputs remain byte-identical in this iteration.

## 2026-09-01 — tree scorer contract normalization

- hypotheses: `evolution/experiments/tree-oracle-alignment-20260901.md`, `tree-oracle-semantic-equivalence-20260901.md`, `tree-scorer-normalization-20260901.md`
- target: deterministic benchmark evidence matching and Windows reference enforcement; no runtime Skill/tree file changed
- baseline ref: `31ba37c9c324ff5863ee237a8c89203f4405fbe9`
- invalidated artifacts: `tree-delivery-n1-20260901-103036`, `tree-delivery-n1-oraclefix-20260901-111838`, `tree-delivery-n1-semantic-20260901-120715`
- accepted artifact: `benchmark-results/tree-delivery-n1-normalized-20260901-125524`
- baseline adaptive score: invalid for acceptance because each preceding artifact used a superseded scorer contract
- candidate required quality: 106/106 determinate; adaptive 15/15; trace 15/15; explicit manual 2/2; spontaneous manual 0/13
- deterministic gate: 22 tree/discriminator/evolution tests passed; maintenance workflow 28/28
- decision: `Accepted`
- rationale: prompt/scorer alignment, semantic and language equivalence, and Windows path normalization are covered by positive and negative tests; runtime inputs remain unchanged. Stable topology and prior-version claims remain pending paired n=3 evidence.

## 2026-09-02 — evolvable leaf tree delivery

- hypothesis: `evolution/experiments/tree-bounded-evidence-volume-20260902.md`
- target: Core retrieval-volume rule on the isolated Debugging/Implementation leaf topology
- frozen baseline: v1.5 at `ba4058b4ef47a42bf79c9963b25678a2389897c1`
- candidate ref: `b202f7a165ae3ea4404d404bb1235ebf4270cbfb`
- artifact: `benchmark-results/tree-final-b202f7a-20260902` (252/252 determinate, n=3)
- required quality: adaptive 45/45; v1.5 44/45; no-skill 44/45
- discipline: trace 45/45; explicit manual 6/6; spontaneous manual 0/39
- adaptive versus v1.5 cost: tokens 258,061.64 vs 217,460.96; duration 76.82s vs 72.20s; tools 8.42 vs 7.24
- decision: `Accepted`
- rationale: the frozen primary release gate requires strict paired delivered-quality superiority and no regression against no-skill; both comparators were exceeded by one cell with perfect discipline. The proposed cost mechanism was not confirmed and the regression remains an explicit limitation, not an acceptance claim.

## 2026-09-03 — execution-state/history-free experiment

- experiments: archived under `evolution/rejected/execution-state/`
- target: cross-cutting explicit execution-state runtime, history-free host/transport, and four-arm model gate
- final measured candidate baseline: `e6cc9caa456767b3e05dbff59474aa7014146cbf`; final pre-retirement branch head: `215334db7bb914bd9f0346a2b09654fc89accc96`
- standard n=1 matrix: 24/24 determinate; full-history 6/6; state-history-free 6/6; state-shadow 5/6; no-skill-full-history 6/6
- transport: captured state-history-free client transport gate passed
- state semantic diagnostic: shadow retained `h-cache` in both active and rejected lifecycle partitions; later deterministic hardening was not model-rerun before retirement
- cost versus full-history: uncached input tokens 78,118 vs 50,736 (`+54.0%`); duration 172.60s vs 154.57s (`+11.7%`)
- incomplete claims: formal n>=3, token, latency, and bounded-horizon gates remained pending
- decision: `Rejected`
- rationale: the mechanism produced no delivered-quality lift, materially increased cost in the completed matrix, and added substantial runtime/transport/benchmark complexity while not addressing the observed retrieval-output long tail. Active code and contracts were removed; historical records remain archived.
- reconsideration: only through a new frozen experiment with independent evidence for a substantially simpler mechanism that solves a demonstrated long-horizon failure, preserves n>=3 quality, and reduces both uncached tokens and time.

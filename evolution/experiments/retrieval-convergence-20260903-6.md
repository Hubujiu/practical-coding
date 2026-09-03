# Retrieval convergence — iteration 6: preserve discriminating search anchors

Status: **Rejected and rolled back**

## Frozen hypothesis

- Baseline SHA: `72d6d138228664c7ec2efc1fc8e12e3dba9b87a6`; runtime remains original accepted `d7c4a93a9d50b1305407d323b718b45e19b0f2fe`. Iteration5 was rejected and completely rolled back; no rejected paragraph is retained.
- Evidence: complete iteration5 baseline/candidate and audited output metadata, especially initial queries on memory-map and sensitive rejection. Baseline memory-map expands named controller/service anchors into `NoMemory|Sliding|Summary|summary|window`; baseline sensitive expands its domain into `sensitive|interceptor|reject|rejection|model`. Both return1,048,576 recorded bytes. Their largest recorded source fragments (up to528,232 bytes) come from unrelated bundled webviewer implementation, contain generic model/filter/window occurrences, and contain none of the relevant named controller/service/interceptor anchors. Candidate memory-map still broadens named anchors into generic terms and returns84,710 Java-source bytes. These different source questions support a query-specificity mechanism rather than another blanket corpus exclusion or response formatter.
- Causal mechanism: OR-expanding a discriminating clue with generic topic words destroys selectivity before source context is available. Preserve specific literal anchors first, and relax only when needed for the current evidence gap. Literal matching also avoids accidental regex interpretation of exact error text/symbol punctuation. Existing routing/retrieval rules still determine source authority and completeness.
- Observable trigger: constructing a source-content query with an available filename, symbol, error text or distinctive domain clue. Return source content directly if useful; there is no mandatory filename-only stage, scope inventory, source reuse registry or output-formatting helper.
- Exact runtime surface: one paragraph in `SKILL.md` Retrieval Policy, immediately before the existing “Once candidate paths or symbols are known” paragraph.
- Exact proposed paragraph: **When searching source, start with the most discriminating available anchor or required set of anchors; keep exact symbols, stable error fragments, and distinctive terms literal, using path constraints for filenames and regex only for known variations or required patterns. Add generic alternatives only when the specific search leaves needed evidence unresolved.**
- Unchanged: all other runtime text/references, topology/automatic/manual nodes, cases, scorer, model, fixture commits, verification and retirement boundaries. No case identifiers, gold-answer symbol list, helper implementation, required extra round or fixed numeric output cap is introduced.
- Required coverage: multiple requested symbols/callers remain required; unrelated missing paths cannot be declared absent from one exact query. Different spelling, casing, generated names or nonliteral structural questions may require a justified broader query under existing retrieval policy. Known broad/exhaustive tasks retain their coverage obligations. A literal miss is evidence of a miss for that spelling, not proof of absence.
- Expected effect: less unrelated initial output and less cumulative input without repeated formatting/pagination machinery. Additional queries caused by over-specific spelling can regress tools/input or miss necessary evidence; all existing gates remain mandatory. Benefit is not presumed.
- Falsifiers: query remains a generic OR under different syntax; narrow matching misses a required owner/caller/contract; fallback causes excessive extra rounds; a requested item is omitted from the final artifact; or any frozen gate fails. No rewording after candidate outputs.

## Frozen evaluation

- Same frozen observation1.3 and repaired shard harness, unchanged scorer/cases/fixtures: `gpt-5.6-luna`, medium, Codex CLI0.145.0, Python3.13.14, timeout600,8concurrent shards with<=5cells each. Both arms identical conditions/assignments and fresh output; no retry/resume/selective replacement.
- Fresh current-only n=1 all54cells: baseline `benchmark-results/retrieval-iteration-6-baseline-n1`, candidate `benchmark-results/retrieval-iteration-6-candidate-n1`. Run baseline first; freeze its3highest-output ordinary adaptive IDs using CASES manual_request flags, result/audit hashes and unchanged gate arithmetic before candidate application.
- Use exactly the audit and non-time gate definitions in iteration5 and `retrieval-continuation-20260903.md`: actual output/operation semantics, full mixed-event attribution, source versus names, later-completed broad events, explicit whole-file versus filtered/bounded reads, and direct verification of actual vendor content even outside conventional dependency directories. Preserve raw counters and unavailable/null outputs. Audit unknown material output; unresolved attribution blocks qualification. No observation-definition change in this iteration.
- Quality still requires accurate requested paths/symbols/filename/caller/contract and verification evidence. Intentional Error/crash-marker/startup recovery cannot be misdiagnosed as a bug; machine required-symbol matches alone are insufficient. Preserve any baseline lexical-oracle limitations without edits or selective reruns.

## Mandatory acceptance

1. Complete/determinate comparable54-cell matrices; no cell timeout/scorer crash/usage/decode gap; each cell>=99% measured completed outputs; resolved semantic attribution. Null-output events remain unmeasured rather than becoming fabricated empty outputs.
2. No paired machine-quality regression in adaptive or required ceilings; all traces legal, explicit manual correct, spontaneous manual0, clean final fixtures; candidate manual tail quality passes.
3. Tail paired median output ratio<=0.70; audited broad-after-source total<=0.5baseline (zero baseline requires candidate0 and earns no positive reduction claim); tail duplicate commands, whole-file bytes, dependency-source bytes and>64KiB events do not increase.
4. Tail paired median input ratio<=0.90; tail uncached input total no increase; all54 input median<=1.02 and tool-call median<=1.00. Preserve zero-to-positive regressions. Duration telemetry only, no serial latency gate and no cached-token substitution.

Only full n=1 passage qualifies the exact committed candidate for the complete252-cell paired n=3,51shards under the same conditions. Compare adaptive quality to the immediate baseline and no-skill without regression; all cells determinate, valid traces/manual discipline, clean fixtures and required source/contract/test evidence. All45 adaptive/baseline pairs govern fixed overhead,9frozen-tail pairs govern cost under the same thresholds and non-increase counters. Improvement must persist in>=2repetitions and>1tail task. No threshold, scorer, case, Router or retirement change.

On failure preserve evidence and restore the entire paragraph before another independent hypothesis. On full passage update wiki/impact/log, sanitize, commit/push/verify and stop successfully. Until-success authorization removes the old count stop, not these gates.

## Results (outside the frozen hypothesis)

Pre-freeze independent review preserved required multi-symbol sets, known spelling/casing variants, stable error fragments, path constraints and necessary regex patterns. This remains one query-specificity mechanism with no mandatory failed preliminary query. Pending fresh baseline; candidate not applied.

### Baseline receipt

Fresh54/54 cells complete,53 machine passes,54 valid routing/manual contracts, no spontaneous manual activation or dirty fixtures. All424 outputs measured with no decode/usage gaps. The failed cap:debugging executor cell omits required Error-test evidence and misreads the intended Error/RUNNING/startup-recovery boundary; raw fail and source audit are retained.

Frozen tail (before candidate): pp-running-after-throw371,153 bytes; sa-sensitive-rejection-boundary283,531; pp-token-rotation-boundary186,855. Audited whole-file total174,396 bytes, dependency-source94,225, broad-after-source1. Manual quality is false/true/false respectively: executor misses startup INTERRUPTED recovery; token assumes stateless authentication makes this explicitly single-node application safe for a rolling multi-instance replacement. These are known quality failures, not unresolved attribution. All tail output hashes verified; no unresolved audit items. The tracked baseline JSON freezes result, audit and pre-existing gate-script hashes.

### Complete candidate: rejected

Both54-cell arms complete and comparable; baseline53/candidate54 machine passes, no paired machine regression. Candidate411/411 outputs measured, no decode/malformed/usage gaps; all routing/manual contracts valid and fixtures clean. Exact candidate Skill hash `491ae7780bbf86654bea8d044d379778d363004a899e52561137fcb1a40b91e7`, run HEAD `a5f02d0a4253e16eaf060e093a0c63c0211d52a6` plus only the frozen paragraph. No n=3.

| Tail metric | Baseline total | Candidate total | Paired median ratio |
|---|---:|---:|---:|
| tool_output_bytes | 841539 | 659448 | 0.6042386832384489 |
| input_tokens | 2286242 | 1392532 | 0.9342233511533804 |
| uncached_input_tokens | 187810 | 163220 | 0.8415560315696629 |
| tool_calls | 53 | 39 | 0.9130434782608695 |
| broad_calls_after_first_project_read | 1 | 1 | 1.0 |
| duplicate_command_calls | 0 | 1 | 1.0 |
| whole_file_read_bytes | 174396 | 90770 | 0.7220171293561725 |
| dependency_source_bytes | 94225 | 76431 | 1.0 |
| outputs_over_64k | 3 | 2 | 0.5 |

Output0.604239 passes, input0.934223 fails0.90. Broad-after-source1 does not halve baseline1; duplicate commands increase. Whole-file/dependency/uncached totals improve. All-cell input0.936193 and tools1.0 pass; duration remains telemetry. Formal decision: Rejected.

Manual tail quality remains false/true/false. Executor misdiagnoses intended Error/RUNNING and omits startup INTERRUPTED recovery, while naming an unsubstantiated test; actual class suite25/0 is preserved. Token correctly acknowledges a single instance cannot restart without interruption but still bases the proposed guarantee on existing multi-instance deployment without resolving the explicit single-node lifecycle contract. Sensitive passes with a minor non-substantive link-format defect. All audit hashes and raw answers are retained.

The proposed query-specificity mechanism was not consistently followed: token initial search still ORs11 general terms,188,987bytes (63.1%of its output); executor root+module searches emit183,901bytes (82%). A later executor read repeats137 lines already returned. Lower tool count or source-file bytes does not ensure sufficient input reduction or correct use of the contract.

Material unknown output outside the tail (sensitive cap:core event9) is a successful source-JAR read with two full classes plus a partial class:18,583bytes conservatively whole/dependency, verified from raw output and archive lengths. Its separate audit preserves automatic estimates. Sensitive adaptive initial source includes vendored UID implementation even with Java/XML filtering; full mixed-event attribution is retained.

Sanitized results: `benchmarks/results/retrieval-convergence/20260903-iteration-6.json`. Full matrices/audits and exact candidate snapshot/patch remain under benchmark-results. Rollback: `git restore --source=72d6d138228664c7ec2efc1fc8e12e3dba9b87a6 -- SKILL.md`; original runtime restored. No threshold/scorer/case/Router change.

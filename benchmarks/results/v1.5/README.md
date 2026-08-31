# Practical Coding v1.5 benchmark evidence

This directory publishes the compact evidence for the accepted event-router restoration. The final candidate was commit `30ac7e70b425b3f02f7bf4e21cb4809f0e4d6c2c`, evaluated current-only with `gpt-5.6-luna` at medium reasoning and three determinate repetitions per case.

## Final results

| Surface | Result | Interpretation |
|---|---:|---|
| Delivery | 54/54 | All correctness, safety, and frontend build cells passed. |
| Debug | 40/42 | All reported bugs were corrected; two fixes preserved an ambiguous sibling behavior instead of changing the shared helper. |
| Decision | 29/30 | One second-round answer used a different recommendation label while retaining the decision and trade-off. |
| Native Behavior | 52/54 | One correct fix skipped the Debugging module read; one irreversible change was safely refused but missed the Retrieval instrumentation. |
| Event reasoning | 113/114 | Reasoning-module selection was stable; one Direct artifact cell selected Implementation. |
| Retrieval | 108/114 | Contract-adjudicated result after three stale relationship-mapping expectations were corrected. |
| Router exact | 107/114 | Exact reasoning plus Retrieval; v1.2's non-paired historical result was 106/114. |
| Held-out quality | 61/66 | 18/22 tasks passed all three repetitions across three frozen real repositories. |
| Manual false activation | 0/66 | Requirements interviewing remained explicit-only. |

All 294 public cells and 66 held-out cells were determinate. The raw Router report recorded 99/114 and held-out exact routing recorded 37/66. The active-contract adjudication changed no model output: it corrected public Retrieval expectations that contradicted STRUCTURAL relationship mapping and removed rejected capability-tree inference from held-out reasoning expectations. The adjudicated held-out exact result is 48/66.

## Evidence boundary

- This cycle ran only the current version. v1.2 is an offline historical reference, not an atomic paired arm.
- No no-skill, Ponytail, combined-skill, or prior-version arm was run.
- Raw transcripts and workspaces remain local because they contain machine-specific paths; hashes are published in `release-summary.json`.
- Held-out exact routing is diagnostic. Delivered quality, clean workspaces, valid traces, and zero manual false activation are reported separately.
- The two public Debug misses and all five held-out quality misses are preserved in the Chinese report; no case-specific runtime wording was added after n=3.

See [`REPORT_ZH.md`](REPORT_ZH.md) for the release decision and failure adjudication, and [`release-summary.json`](release-summary.json) for machine-readable identities and scores.

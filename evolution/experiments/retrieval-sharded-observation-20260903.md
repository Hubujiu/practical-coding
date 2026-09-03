# Frozen observation and sharding support for the resumed loop

Status: **Accepted — benchmark infrastructure only**

Baseline before this maintenance change: `ed522d538e618c0e7f2804304939732a5ff6280f`. No runtime Skill, reference, topology, case, scorer or model prompt was changed.

- Observation 1.3 retains all existing cost/count values and adds explicit per-event convergence attribution uncertainty and aggregate manual-audit requirements. Compound partial failures, dynamic search scopes, mixed project/dependency reads, and same-event ordering cannot silently establish complete convergence coverage.
- `tree_shards.py` launches the original runner in isolated fresh subprocess shards, at most five cells each and at most eight concurrent shards. There is no retry/resume or selective replacement. Current-only n=1 has 54 cells / 11 shards; paired n=3 has 252 cells / 51 shards.
- The aggregate validates exact unique expected coverage, complete raw artifacts, equality with each raw result, matching common manifests, baseline runtime hashes, frozen model/runner/fixture identities and original full matrix specifications. It adds only `shard_index` and `cell_directory` to result rows. Timing is not a gate.
- Verification: **61 deterministic tests pass**, plus tree self-test. Mock subprocess tests cover concurrency, bounded allocation, missing/duplicate/tampered/incompatible results and no-retry behavior. Actual model subprocess execution remains to be verified by the first fresh baseline.
- AST comparison with the starting commit confirms unchanged `build_specs`, `task_prompt`, `score_answer`, `run_cell`, `instrumentation`, `ceiling_instruction`, `parse_trace`, and `validate_trace`.
- Offline observation replay: `benchmark-results/retrieval-observation13-replay/`, all 108 prior model records / 851 tool events. Every pre-existing 1.2 observation field remains identical; only new uncertainty metadata/version differs. Original results hashes are unchanged. 52/54 baseline and 51/54 candidate records require some manual audit, often because harmless status commands are unclassified; this is not a direct-cost failure. Tail gate attribution must be explicitly audited before qualification.
- Raw model artifacts were not rewritten. Commit/freeze this support before a new baseline and preserve identical support files for both arms.

The user's reopened-loop authorization and non-time gates are recorded in `retrieval-continuation-20260903.md`.

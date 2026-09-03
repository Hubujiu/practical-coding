# Retrieval instrumentation repair after user-directed continuation

Status: **Accepted — repaired instrumentation only**

The user explicitly requested repair and continuation of the existing loop. This
is remediation of iteration 1's observational implementation, not a new runtime
candidate or a reset of the maximum three iterations. The interrupted artifact
and original termination record remain unchanged. No runtime candidate has yet
been evaluated.

- Starting SHA: `678c67c153206f86b73ac3bc2c06af8b91e3a3b6`, clean and matching origin after fetch.
- Root cause: the CLI serializes an argv vector using shell-word escaping; a single script argument may concatenate single-quoted, double-quoted and escaped fragments. Stripping only matching outer quotes is not argument decoding.
- General repair: decode recognized shell launcher argv using Python's standard `shlex`, extract its script argument, then classify the decoded script. Preserve raw command text for audit. Report malformed/unsupported launcher decoding as a measurement gap. Canonical duplicate identity uses the decoded command, preserving quoted payload whitespace.
- Tests: generated quote/escape variants, payloads containing command words, malformed launchers, duplicate wrapper equivalence, and convergence after wrapped source reads. Existing prompt/scorer noninterference and tree tests remain required.
- Scope: retrieval metrics/tests and this repair record; metadata-only manifest/analysis improvements if necessary to make coverage and identity auditable. No runtime, topology, case, answer scorer or frozen-artifact change.
- Validation: deterministic tests; remeasure old transcripts into a new repair directory, including the aborted baseline's commands. Commit and freeze before fresh model runs. Old cost statistics never form a pair with repaired statistics.
- Next: close iteration 1 as accepted instrumentation when the measurement contract passes; freeze an atomic iteration 2 hypothesis from relevant accepted historical retrieval metadata before a fresh baseline; freeze its top-three ordinary adaptive output cases before applying runtime wording.
- All original n=1/n=3 quality, mechanism, token, tool-call and latency thresholds remain unchanged. No selective retry or case replacement.

## Results

- 45 deterministic tests and the tree self-test pass. Added tests cover shell argument round trips, quoted command text, malformed launchers, pipeline filtering, per-command scopes, literal scope variables, archive stream reads, and duplicate/convergence identity.
- Final replay: `benchmark-results/retrieval-iteration-1-repair-frozen-replay/`; 252 records retain every original result field; 1,844/1,845 events have output; shell decoding failures 0. Unclassified bytes are 531,601/78,011,482 (0.68%). Other includes legitimate status/metadata calls and is not silently treated as a retrieval pass.
- Every nonempty source-read output in the interrupted four-cell baseline is now recognized. Original artifacts remain untouched.
- Frozen metrics version 1.1 SHA-256: `f07b0fc4f61af3b2d6ed1126a23dba7fe757d536bab7fc9e04209741ebc44adf`.
- General measurement limits remain explicit: bytes are recorded UTF-8 output, possible truncation is flagged, and mixed-category byte attributions overlap. Inspect high-output unknown events and tail command classifications before interpreting any gate.
- Iteration 1 is closed as accepted observation infrastructure after the user-authorized repair. It does not establish runtime quality or cost benefits. Continue to an independently frozen iteration 2, retaining the original three-iteration limit.

# EXP-state-20260902 — Bounded execution state as a runtime substrate

## Evidence / pattern

The current evolvable tree controls **which execution capability is disclosed**, and the WikiSkill-inspired maintenance loop controls **how experience compounds across sessions**. Neither mechanism makes the current state of one long-running coding task explicit. A long task can therefore still reconstruct current branch/check/hypothesis/change status from an append-only conversation even when routing itself is minimal.

Badhe, Tiwari, and Chung's *SKILL.state: Scalable Long-Horizon Agent Skills* (arXiv:2608.26263v2) isolates this problem. Its runtime invokes the model with immutable procedure `P`, structured current state `Σ`, and only the latest observation `O`; a deterministic runtime validates a merge patch, applies null-deletion semantics, executes the action only after accepting the transition, and does not replay the transient reasoning trace on the next step.

The branch's last complete release comparison (`b202f7a165ae3ea4404d404bb1235ebf4270cbfb`) passed delivered quality but reported higher average token, duration, and tool-call cost than frozen v1.5. That result does not prove history growth caused the overhead, but it makes bounded long-horizon state a testable cost mechanism rather than a new task taxonomy.

## Hypothesis

When a coding task spans enough tool rounds that the next action depends on facts produced earlier, a compact validated coding-domain execution state will reduce reconstruction, stale-fact drift, repeated hypotheses, and irrelevant-tool-output carryover without changing the automatic route.

The useful preload/activation signal is **state pressure**, not a domain noun:

- the next action depends on current facts from at least two earlier observations;
- a latest observation can invalidate a previously stored branch/check/contract fact;
- repeated hypotheses or checks must be remembered to avoid cycling; or
- replaying raw tool output would otherwise be required to recover the current work surface.

Short tasks remain stateless. State projection is cross-cutting runtime infrastructure, not `Core -> State`, not a retrieval level, and not a manual mode.

## Change

Freeze a deterministic contract benchmark first, then add one zero-dependency runtime adapter and the minimum Skill wording needed to activate it:

1. one coding-domain schema for objective/success, route, working set, facts, hypotheses, change surface, verification, next action, and bounded history artifacts;
2. JSON Merge Patch behavior where omitted keys survive and `null` deletes obsolete keys;
3. strict schema/type/size validation before canonical mutation;
4. rollback on invalid patch and no execution of its proposed action;
5. prompt construction from procedure + current state + latest observation only;
6. explicit refusal to persist reasoning traces, transcripts, or raw tool output;
7. a history escape hatch for audit/provenance tasks, dynamic-schema discovery, and observations whose future relevance is still uncertain;
8. a JSON runtime-input envelope and explicit observation/control ownership so delimiter-like or instruction-like tool data cannot become a new prompt section or mutate host-owned task/route fields.

Do not add an automatic tree node or change the Debugging/Implementation boundary.

## Expected result

Required correctness gates:

- nested partial updates preserve omitted siblings;
- explicit `null` removes obsolete entries;
- invalid patches never mutate canonical state or release their action;
- state cannot contain transcript/reasoning/raw-tool-output fields;
- irrelevant telemetry does not enter later state;
- a corrective observation can replace a stale fact in the same transition;
- the state remains within a fixed byte budget across horizons 10, 50, and 200;
- runtime input with Markdown fences, fake headings, or JSON-looking text round-trips as JSON data without escaping the prompt boundary;
- the prompt declares model-owned versus host-owned fields, while runtime validation remains authoritative;
- manual Decision/Clarification isolation and current automatic topology remain unchanged.

Cost expectations are secondary: the deterministic history baseline should grow with horizon while the state prompt remains bounded by schema and latest-observation size. This does **not** establish the paper's LLM accuracy/token results and does not justify an `O(1)` claim for hosts that continue appending prior messages underneath the Skill.

## Frozen validation

- Immediate parent / baseline ref: `13c8a252121d92ab47548016ae1ee39bcafcd149`.
- Original deterministic benchmark: `benchmarks/skill_state_validation.py` plus `benchmarks/test_skill_state_runtime.py`, committed before the initial runtime implementation.
- Review hardening: prompt-envelope/control-ownership tests were added before the corresponding runtime change.
- Deterministic horizons: 10, 50, 200; 20 irrelevant telemetry events per turn; fixed four-slot coding state.
- Existing regression gate: repository unit-test suite, tree topology self-test, manual-only layout check, and explicit evolution workflow contract.
- Model-backed mechanism iteration: current tree benchmark at `n=1`, compared with the immediate parent on identical tasks/scorer/model/harness.
- Release gate after wording/topology freeze: complete `n=3` adaptive/baseline/no-skill and dedicated full-history/state-shadow/state-history-free state matrix; required delivered quality and manual-mode discipline cannot regress. Cost may only break a quality tie.

## Result

The deterministic implementation and repository contract gates passed on the candidate lineage: the CI validation job completed successfully with 107 repository tests plus the tree, evolution-workflow, execution-state, manual-only, prompt-reference, and legacy-runtime checks. The review then found one uncovered adapter boundary: a Markdown-fenced state block did not clearly separate untrusted observation text from control text, and the prompt did not state the same host/model ownership rule enforced by the validator.

The candidate now serializes all runtime input as one compact JSON value, declares observation trust and field ownership, withholds action until the successor state validates, and extends the deterministic benchmark with delimiter/control-boundary round-trip tests. The local focused suite passes all 19 execution-state tests and the expanded deterministic contract.

No model-backed long-horizon state comparison has completed after this runtime-prompt change. The earlier evolvable-tree n=3 result is historical non-regression evidence for the tree, not proof that execution-state projection improves quality or cost.

## Decision

`accept-experimental`: retain execution state as an experimental cross-cutting substrate because its deterministic contract and topology/manual-mode isolation pass. Do not promote its efficiency claims into the release contract until the frozen model-backed state gate completes without quality regression.

## Follow-up

Run the protocol in `benchmarks/SKILL_STATE_MODEL_GATE.md`. Reject or revise the candidate if the coding schema repeatedly needs ad-hoc fields, if state pressure cannot be detected before history reconstruction, if valid-but-premature overwrite/deletion loses future-relevant facts, if explicit state causes quality/manual-routing regression, or if a host cannot actually exclude prior messages and the projection adds cost without reducing reconstruction.

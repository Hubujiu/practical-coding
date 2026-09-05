# EXP-state-host-20260902 — Audited history-free transport boundary

## Status

`candidate-pending-model-gate`

This hypothesis is frozen before any model-backed result for the host adapter is observed. The implementation may pass deterministic checks without earning a quality, token, latency, or topology claim.

## Evidence / unresolved mechanism

The execution-state schema and merge runtime can construct `P + Σ + O`, but `build_prompt()` alone cannot establish what an SDK, proxy, or product actually sends. A surrounding host may still append prior messages, use `previous_response_id`, attach a conversation or prompt reference, rebuild the request, or put accumulated history into a field labeled as the latest observation. In that situation the state is only a shadow aid; it is not evidence for history-free execution or a horizon-independent per-step client request.

The paired tree report at `f65bcd3dac2eac1f8e47ec435c7499c953ec0c96` establishes quality non-regression for the reviewed tree/runtime wording, but adaptive cost remained above frozen v1.5. It does not isolate execution state and does not establish a state-related token or latency benefit.

## Atomic hypothesis

A transport-facing host that freezes request identity, constructs exactly one current request from immutable procedure plus validated state and the latest bounded observation, rejects all explicit history-import channels, and audits the exact serialized request body will make the `state history-free` arm mechanically testable without changing the automatic router topology.

The observable activation signal remains state pressure. The host boundary is a cross-cutting substrate and must not become an automatic node, a manual mode, or a retrieval mode.

## Candidate change

Add only the host substrate and its runtime contract:

1. `runtime/skill_state_host.py` freezes model, procedure, tools, options, limits, and request-shape identity in a self-digested manifest;
2. the current procedure and transition contract are placed in top-level `instructions`;
3. exactly one current user input contains canonical JSON for `Σ`, current `O`, and optional bounded deterministic validation feedback;
4. prior-response, conversation, prompt-reference, context-management, old assistant/tool input, and equivalent configured history handles are rejected;
5. procedure, state, observation, feedback, tools, options, response, attempts, and the final serialized body have hard bounds;
6. each retry starts from the unchanged original state and does not append a rejected response;
7. a valid successor must be durably persisted before its still-untrusted action proposal is returned;
8. request/response identity, component sizes, provider usage when present, and transport timing are exposed as audit records;
9. offline build/audit commands never call a model;
10. AGENTS, SKILL, README, detailed architecture, and OpenAI agent metadata distinguish state shadow, client-body boundedness, and model-backed benefit.

Do not alter `benchmarks/`, `benchmarks/results/`, automatic topology, Debugging/Implementation boundaries, or manual-mode eligibility in this candidate.

## Deterministic falsifiers

Reject the implementation before model testing if any of the following occurs:

- a prepared request can contain more than one input item or any explicit prior-response/conversation/prompt/context handle;
- a manifest-free one-request audit is reported as a frozen trajectory claim;
- manifest, procedure, tools, options, limits, or request contract can drift without rejection;
- a retry contains a prior response or starts from a mutated candidate state;
- invalid output, retry exhaustion, or persistence failure can release an action;
- a native model tool call can be mistaken for the required JSON transition;
- final serialized request or response bytes can exceed the frozen limits;
- direct script invocation does not work from the repository root.

## Model-backed falsifiers

Use the already frozen protocol in `benchmarks/SKILL_STATE_MODEL_GATE.md`. Reject or revise the candidate if:

- the final outbound body, contextual headers/cookies, proxy/session state, or observation provenance cannot be audited;
- the history-free arm regresses delivered quality, safety, required checks, route validity, or manual-mode discipline against full history;
- valid state repeatedly loses future-relevant evidence, fails to replace stale facts, or increases repeated actions/hypotheses;
- invalid-transition retries or state maintenance erase the expected token benefit;
- provider-reported cumulative uncached input tokens do not satisfy the pre-frozen paired threshold after quality passes;
- end-to-end latency does not satisfy its independently frozen paired threshold;
- history-required cases silently discard provenance instead of retaining bounded immutable pointers or exiting history-free mode.

## Claim boundary before results

Before the model gate, the maximum supported statement is:

> Under one validated frozen manifest, the captured client-visible request body has one current input, contains no explicit body-level history channel, and is bounded in bytes independently of prior task-step count.

This does not prove that an HTTP transport added no contextual state, that the provider used no internal context, that the observation injector supplied only the latest observation, that model quality is preserved, or that tokens or latency improve. Even after a per-step bound is established, cumulative input across `T` steps remains proportional to the number of steps rather than constant.

## Frozen non-benchmark validation

- Python syntax compilation for the state runtime, host adapter, and ordinary tests;
- `tests.test_skill_state_hardening`;
- `tests.test_skill_state_host`;
- direct offline CLI build and manifest-matched re-audit;
- YAML parsing and whitespace checks;
- no benchmark case, scorer, runner, topology manifest, or result-data modification.

## Pending decision

Do not modify the Skill activation rule or router tree from this candidate alone. After the paired report is published, classify failures by mechanism first: host integration, observation provenance, state schema/update policy, activation timing, delivery quality, or cost. Only repeated topology-specific evidence may justify a tree mutation.

# Audited history-free host boundary

`runtime/skill_state_host.py` is the transport-facing companion to
`runtime/skill_state.py`. The state runtime validates `Σ` and transitions; the
host boundary constructs one bounded request from `P + Σ + O`, audits the exact
serialized request, and releases a proposed action only after the successor state
has been persisted.

The module is deliberately transport-agnostic and zero-dependency. It does not
call a model, execute tools, persist credentials, or define benchmark cases. A
benchmark or product host supplies the byte transport and its normal action-policy
boundary.

## Claim boundary

A request is eligible for a **client-visible history-free request** claim only
when all of the following are true:

- the immutable procedure and transition contract are carried by the current
  top-level `instructions` field;
- the body contains exactly one current `user` input item with one `input_text`
  block whose complete text is the state/observation JSON data object;
- `previous_response_id`, `conversation`, prompt references,
  `context_management`, prior assistant/tool items, and equivalent nested history
  handles are absent;
- `store=false`, `stream=false`, `background=false`, and
  `truncation="disabled"` are explicit;
- the procedure, tools, options, limits, and request-shape contract match one
  frozen manifest;
- procedure, state, latest observation, validation feedback, tools, options, and
  the complete serialized request remain within hard byte limits;
- the exact audited bytes are the request-body bytes delivered to the HTTP transport;
- the transport does not attach a context-bearing cookie, session/conversation
  header, proxy memory handle, or another out-of-band history channel. This last
  property must be established by the integration or captured outbound request,
  not inferred from the body audit.

The caller must also establish that `latest_observation` is the current bounded
observation supplied by the frozen observation injector, not a relabeled transcript
or concatenation of prior turns. The byte boundary can cap that field but cannot
classify its semantic provenance.

Passing this audit does not prove provider-internal behavior, privacy, zero data
retention, semantic resistance to prompt injection, delivered task quality, or a
token/time improvement. It establishes only the composition and fixed byte bound
of the captured client request. If an SDK reconstructs the body, attaches session
state, or converts it into another request, audit that final serialized body
instead.

## Frozen request contract

`HistoryFreeHost` freezes:

- model identifier;
- immutable procedure hash;
- canonical tools hash;
- canonical options hash;
- all configurable limits and fixed component hard limits;
- the current-instructions/one-current-input/no-history request contract.

`manifest()` returns this data plus a self-digest. Every prepared request records
the manifest digest and hashes for the complete request, procedure, state,
observation, tools, and options. `audit_wire_request_against_manifest()` rejects
identity or limit drift.

The runtime hard caps are:

| Surface | Hard cap |
|---|---:|
| Model identifier | 256 bytes |
| Current instructions | 80 KiB |
| Canonical execution state | 16 KiB |
| Procedure | 64 KiB |
| Latest observation | 64 KiB |
| Validation feedback | 2 KiB |
| Frozen options | 16 KiB |
| Frozen tools | 96 KiB |
| Complete request body | 320 KiB |
| Raw response body | 4 MiB |
| Transition attempts | 3 |

A `HistoryFreeLimits` instance may tighten these caps for a frozen run; it cannot
raise them.

## Request construction

```python
from runtime.skill_state import initial_state
from runtime.skill_state_host import HistoryFreeHost

state = initial_state(
    "Repair the release check",
    ["The focused release check passes"],
)

host = HistoryFreeHost(
    model="gpt-5.6-luna",
    procedure="<exact loaded Practical Coding procedure>",
    options={
        "max_output_tokens": 4096,
        "reasoning": {"effort": "medium"},
    },
)

manifest = host.manifest()
prepared = host.prepare_request(
    state,
    "The latest focused check failed at release.py:41.",
    step_id="case-01/step-03",
)

# Send prepared.wire_bytes unchanged. Do not rebuild the request through an SDK.
request_sha256 = prepared.audit["request_sha256"]
```

The request uses the Responses-compatible JSON shape but does not require the
OpenAI SDK. The procedure is serialized into the current `instructions` field,
while the single user input contains only canonical JSON for `state`,
`latest_observation`, and optional bounded `validation_error`. This gives the
procedure an instruction-level boundary instead of placing trusted procedure and
untrusted observation in the same user message.

Avoid rebuilding the prepared body through an SDK: SDK-managed conversation or
prior-response state would make the history-free claim un-auditable unless the
final outbound body is intercepted and rechecked.

## Transition loop

`run_transition()` accepts a caller-supplied byte transport:

```python
from pathlib import Path

from runtime.skill_state_host import TransportResponse


def transport(body: bytes) -> TransportResponse:
    # The integration must send exactly `body` and retain the final outbound
    # bytes plus raw response in its benchmark artifact store.
    ...


def persist_successor(successor: dict) -> None:
    # Use one durable atomic write, revision/CAS, or a single-writer store.
    ...


result = host.run_transition(
    state,
    "The latest focused check failed at release.py:41.",
    transport=transport,
    persist_successor=persist_successor,
    step_id="case-01/step-03",
    max_attempts=2,
)

# `result.action` remains untrusted. Apply the product's normal tool,
# argument, permission, working-directory, side-effect, and user-consent policy.
```

Each retry starts from the same original canonical state and receives only the
same `P + Σ + O` plus one bounded host-generated validation error. A rejected
transition never persists state or releases its action. A valid successor is
passed to `persist_successor` before its action is returned. If persistence
fails, the action is withheld. The persistence callback itself must not report
success before the new snapshot is durable; the runtime cannot roll back an
external store that commits and then raises.

The returned attempt records include:

- request/response hashes and byte sizes;
- manifest, procedure, state, observation, tools, and options hashes;
- request ID when supplied by the transport;
- input, cached input, uncached input, output, and total token usage when present;
- transport elapsed time;
- transition status and bounded validation feedback;
- accepted successor-state and action hashes.

Raw request and response bodies are intentionally not retained by the runtime.
The benchmark transport must store them in its own access-controlled artifact
location before publishing only redacted summaries.

## Offline build and audit

The CLI builds requests but never sends them:

```powershell
python runtime/skill_state_host.py build `
  --model "gpt-5.6-luna" `
  --procedure procedure.txt `
  --state state.json `
  --observation observation.txt `
  --options options.json `
  --tools tools.json `
  --request-output request.json `
  --audit-output request-audit.json `
  --manifest-output host-manifest.json

python runtime/skill_state_host.py audit request.json `
  --manifest host-manifest.json `
  --output request-reaudit.json
```

An `audit` run without `--manifest` validates only one request body and reports
`bounded_context_eligible=false`. Supplying the self-validating manifest proves
that the saved body matches the frozen client contract and reports eligibility for
the limited client-body bound. The model benchmark still has to show that the same
bytes reached its actual transport boundary, that no contextual headers or proxy
session state were added, and that provider-reported token usage was captured.

## Non-benchmark validation

```powershell
python -m py_compile runtime/skill_state.py runtime/skill_state_host.py
python -m unittest tests.test_skill_state_hardening tests.test_skill_state_host
```

These checks cover request shape, manifest identity, hard limits, no-history
controls, retry rollback, persistence-before-release, token metadata, and CLI
round trips. They do not run a model and cannot establish quality, token, or
latency benefit.

## Benchmark handoff

The remaining work is the model-backed protocol in
`../benchmarks/SKILL_STATE_MODEL_GATE.md`. The harness should use this host for the
`state history-free` arm, record every exact request/response at the transport
boundary, and compare it with frozen full-history, state-shadow, and no-skill
arms. Do not change Skill wording or router topology in response to a single
result. First publish the paired report; then treat quality loss, state loss,
retry rate, token reduction, and latency as separate mechanisms when deciding
whether to keep, revise, or reject the substrate.

# EXP-state-20260903 — Scorer-contract and Codex SSE transport remediation

## Status

`infrastructure-fixed-pending-fresh-n1`

This record follows the first complete `standard / n=1 / workers=1` four-arm run at
`ea8580f169154cab01914f4c76e369f1a26f91f8`. It is an infrastructure remediation,
not a Skill or router candidate. No historical result is rewritten or promoted.

## Frozen evidence

The original atomic matrix contained 24 cells: 19 pass, 4 fail, and 1
indeterminate. A connection-failure case was rerun independently under the same
configuration and all four arms passed; those retry cells remain separate rather
than being spliced into the original matrix.

Run identity:

- model `gpt-5.6-luna`, reasoning `medium`;
- standard profile, `n=1`, one worker, 90-second request timeout, at most two
  transition attempts;
- original manifest SHA-256
  `c4408f852c39f4caa15ff0a39271a830772b48461676d2962f848b368945af18`;
- local compatibility adapter SHA-256
  `ece048d7836c6f50fe1f6074a51df9f6cecc8e8ecbe7bce49f01cc124adaee0f`;
- independent retry manifest SHA-256
  `5f088e168d58bac3be036e9bbb76323605c748497e41633b26617da6903cf8c3`.

The raw artifacts remain ignored local benchmark evidence. This repository record
contains only the mechanism-level findings needed to freeze the repair.

## Confirmed defects

### 1. Separator-sensitive answer evidence

The answer scorer used case-folded literal substring matching. Therefore the
semantically and lexically equivalent surface forms `parser-transition` and
`parser transition` received different scores even though the case success
contract itself uses the spaced form.

The repair is general: normalize Unicode with NFKC, case-fold, and treat
punctuation, symbols, underscores, and whitespace as equivalent separators. It
does not add case-specific aliases, stemming, synonyms, or semantic judging.

### 2. State-only artifact requirement leaked into control arms

The immutable artifact file and digest are required in every arm. A canonical
`state.history.required` flag and state artifact pointer exist only in state arms.
The old scorer required those state fields from full-history and no-skill arms,
which made two otherwise correct control cells structurally impossible to pass.

The repair separates:

- immutable file existence and digest integrity — every arm;
- `state.history.required` and exact pointer retention — state arms only.

### 3. The observed Codex wire request was not the frozen source request

The API-key/non-streaming request profile was not accepted by the ChatGPT-backed
Codex endpoint. The successful local compatibility run changed exactly four
fields: set `stream=true` and removed `background`, `max_output_tokens`, and
`truncation`. It retained the current instructions, input, model, reasoning,
`store=false`, and all task data. The response was an SSE stream.

Because the canonical host manifest described the source body rather than the
final transformed body, that run cannot establish the final outbound transport
gate. Source-body audit success is retained as source evidence only.

## Frozen remediation

1. Keep the original implementation available under private compatibility module
   names so the patch is reviewable and does not duplicate unrelated runner code.
2. Give the scorer an explicit version and reject mixed old/new result sets.
3. Apply only the two general scoring-contract repairs above; do not edit frozen
   case wording or manually rescore historical rows.
4. Add a named `codex-sse-v1` wire profile with a self-digesting contract manifest.
5. Audit the canonical history-free source request before transformation.
6. Permit exactly the four observed field changes and prove all other JSON fields
   remain identical.
7. Send the transformed bytes directly, with `store=false`, no previous response,
   no conversation/thread/session field, no cookie jar, no environment proxy, and
   no replayed response context header.
8. Preserve both source and final request hashes, raw SSE, normalized response,
   redacted final headers, profile manifest, and profile audit per request.
9. Treat the final output-token limit as provider-managed for this profile; do not
   claim the removed `max_output_tokens=2048` remains enforced.
10. Parse a run only after exactly one `response.completed` event. A missing or
    conflicting completion remains an infrastructure failure.

## Falsifiers before model rerun

Reject this infrastructure patch before another model run if any deterministic
check shows that:

- answer normalization accepts stemming or unrelated semantic variants;
- a non-state arm can pass with a missing or wrong artifact digest;
- a state arm can pass the history-required case without its exact pointer;
- `codex-sse-v1` changes any field beyond the four frozen changes;
- a final request imports old response, conversation, thread, session, cookie, or
  proxy state;
- the final wire/profile manifest cannot be reproduced from committed code;
- an incomplete SSE stream is normalized as a completed response;
- old scorer rows can be mixed into a new formal analysis.

## Required rerun

The original n=1 matrix and independent retry remain historical diagnostic
evidence. After deterministic checks pass, start a fresh output directory and run
the complete four-arm standard n=1 matrix with the new scorer and frozen final
wire profile. Do not merge old cells, hand-correct old verdicts, or use the
independent retry as an atomic replacement.

Only after the fresh n=1 matrix is determinate may the project decide whether to
freeze an n>=3 release comparison and the 10/25/50/100 bounded profile. Until then:

- execution-state model gate: `PENDING`;
- token gate: `PENDING`;
- latency gate: `PENDING`;
- bounded-context gate: `PENDING`;
- Skill wording and automatic tree topology: unchanged.

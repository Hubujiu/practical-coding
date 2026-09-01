---
name: session-to-wiki
description: "Explicit maintenance skill for compiling the current visible session into sanitized persistent evolution knowledge. Never activate automatically during ordinary coding work."
license: MIT
metadata:
  author: Hubujiu
  version: "1.0"
---

# Session to Wiki

Activate this maintenance skill only when the user explicitly asks to preserve, distill, consolidate, or write the current session into the Practical Coding evolution wiki. It is outside the automatic runtime router tree.

## Scope

The goal is not to archive chat. Convert useful execution experience into durable, auditable maintenance knowledge while keeping raw experience, wiki knowledge, and runtime Skill text separate.

Use only visible session content and observable tool/results evidence. Do not reconstruct or store private chain-of-thought.

## Procedure

1. **Select evidence.** Keep only session events that reveal a reusable success strategy, failure mechanism, routing boundary, benchmark defect, or user correction relevant to Practical Coding evolution.
2. **Sanitize before persistence.** Remove secrets, credentials, private code, personal identifiers, and unrelated conversation. Replace sensitive specifics with coarse mechanism-level descriptions. Never copy the full transcript into the repository.
3. **Write one immutable receipt first.** Create a new file under `evolution/raw/sessions/` using `evolution/EXPERIENCE_SCHEMA.md`. Include the source pointer, outcome, affected capability/boundary, mechanism, supporting evidence, contradictions, and candidate lesson. Do not rewrite an older receipt to make a later hypothesis look stronger.
4. **Read the current wiki before consolidating.** Start with `evolution/wiki/index.md`, then inspect the few relevant pattern pages. Update an existing mechanism when possible; create a new page only for a distinct generalizable mechanism.
5. **Consolidate causally.** A wiki page must state the claim, observable pre-action trigger, supporting receipts, contradicting receipts, affected nodes/boundaries, candidate experiments, and current status. Prefer root cause and action pattern over surface wording.
6. **Update navigation and chronology.** Update `evolution/wiki/index.md` and append a concise entry to `evolution/wiki/log.md`, even when no new reusable pattern is created.
7. **Stop before runtime mutation.** This skill must not edit `SKILL.md`, automatic router references, or executable runtime behavior. If the accumulated wiki suggests a Skill change, report the candidate hypothesis and leave mutation to the explicit `evolve-skill` maintenance skill.

## Quality Gate

Before finishing, verify:

- no raw transcript or secret was persisted;
- the receipt is immutable evidence, not a rewritten conclusion;
- wiki claims cite receipts or benchmark artifacts;
- supporting and contradicting evidence are both represented when present;
- no runtime Skill/router file changed.

Finish with the receipt path, wiki pages changed, and whether a follow-up evolution hypothesis now has enough evidence to test.

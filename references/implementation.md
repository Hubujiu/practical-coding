# Implementation

Load this module only when Core-only work cannot safely proceed because an authoritative contract or invariant is unknown, a material risk boundary is unresolved, or the sufficient evidence for a risky material claim is itself unknown.

Implementation is an execution capability. It normally starts at E2 and escalates to E3 only when the guarantee spans a materially wider boundary.

## E2 — Structured implementation

- Identify the authoritative contract or invariant and the minimum producers, consumers, adapters, data, and checks that must move together.
- Read only those paths and their material callers/dependencies.
- For a risk boundary, identify the smallest point that owns the guarantee before editing.
- Preserve public compatibility unless the requirement authorizes a break. When migration is required, choose one authoritative internal representation and keep compatibility at the narrowest boundary.
- Reuse existing helpers and patterns. Add an interface, adapter, wrapper, switch, generic utility, or configuration surface only for a demonstrated current boundary.
- Map each material claim to the cheapest check that can falsify it.

Validation belongs once at the narrowest authoritative boundary. Add retries, fallbacks, broad catches, compatibility layers, or recovery only for a concrete failure mode.

## Escalate to E3 only when needed

Use Assurance depth only when E2 cannot support a material guarantee without exercising a wider state or caller space, for example:

- security/permission decisions where rejection must occur before side effects across more than one entry path;
- persistence or migration where restart, rollback, mixed-version, or old/new representation behavior matters;
- concurrency/transactions where ordering, race, duplicate delivery, or atomicity is material;
- compatibility where materially different old and new callers or versions must coexist;
- irreversible side effects where partial failure or recovery semantics determine correctness.

At E3, expand evidence only to those representative modes. Do not add generalized hardening unrelated to the touched guarantee.

## Evidence ladder inside the capability

Choose the lowest sufficient check: diff inspection; direct exercise/render; compile/type/lint; an existing focused test; one new focused test; a boundary integration test; full suite only for a broad surface or required gate.

For persistence/concurrency, exercise restart/rollback/race behavior only when material. For compatibility, exercise the materially affected old and new callers. For a security or permission boundary, include a valid case and the smallest representative rejection cases and verify rejection precedes side effects.

## De-escalate after mapping

Once the governing boundary, affected surface, and sufficient evidence are known, stop assurance mapping. Contract to the minimum coherent diff, implement, and run the planned focused checks after the final edit.

If implementation exposes a different event, return it to the root; do not automatically load another module.

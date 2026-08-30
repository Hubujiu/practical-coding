# Debugging

Load this module only after an observed or reported failure, regression, incorrect behavior, or failed verification still lacks an evidenced cause and bounded Core-only inspection was insufficient.

Debugging is an execution capability. It normally starts at E2 and escalates to E3 only when the evidence boundary itself is materially wider.

## E2 — Structured diagnosis

1. Reproduce the symptom when practical, or collect the smallest evidence that distinguishes plausible causes.
2. Trace the real execution path backward from the symptom to the earliest incorrect state.
3. Separate observed facts from hypotheses.
4. Test one meaningful hypothesis at a time.
5. Fix the narrowest authoritative cause, not a downstream symptom.
6. Verify the original symptom with fresh focused evidence.

For universal wording such as "never", "every", or "no X can", inspect the delegated helper and nearest sibling caller before editing the reported adapter. If multiple current paths can violate the same invariant, the smallest coherent fix is the common authoritative boundary, not necessarily the fewest changed lines.

Do not use broad retries, catches, fallbacks, default values, or defensive branches to hide an unexplained failure. Temporary instrumentation is justified only when it distinguishes hypotheses.

## Escalate to E3 only when needed

Use Assurance depth only when E2 cannot support the material claim because one of these remains unresolved:

- nondeterministic or timing-sensitive behavior;
- concurrency, transaction, retry, or ordering interactions;
- multiple state transitions or persistence/restart behavior;
- a shared security, permission, integrity, compatibility, or public-contract boundary across materially different callers;
- the failure appears only across environments, modes, or versions and bounded evidence cannot isolate the cause.

At E3, expand only the evidence needed to resolve that guarantee: representative sibling paths, relevant state transitions, controlled race/rollback conditions, or materially affected compatibility modes. Do not turn Assurance into repo-wide bug hunting.

## De-escalate after localization

Once the earliest incorrect state and authoritative repair boundary are known, stop diagnosis. Contract to the affected surface, make the smallest coherent fix, and run the cheapest sufficient final checks.

A successful fix:

- removes the earliest incorrect state that explains the symptom;
- preserves intended behavior for the reported path and materially affected sibling callers;
- restores any diagnosed security, permission, integrity, accessibility, compatibility, or project invariant at the boundary that owns it;
- changes no unrelated behavior;
- adds no speculative fallback, validation, test, or refactor.

Add a durable targeted test only when regression risk, project requirements, or the evidence plan gives it lasting value. Otherwise use the cheapest reproduction or focused check that can falsify the fix.

If diagnosis exposes a different material blocker, return it to the root. Do not load another Practical Coding reasoning reference from this module.

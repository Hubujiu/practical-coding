# Diagnosis

Load this capability root only after an observed or reported failure, regression, incorrect behavior, or failed verification still lacks an evidenced cause and one bounded Core-only inspection was insufficient.

## Structured diagnosis

1. Reproduce the symptom when practical, or collect the smallest evidence that distinguishes plausible causes.
2. Trace the real execution path backward from the symptom to the earliest incorrect state.
3. Keep observed facts separate from hypotheses.
4. Test one meaningful hypothesis at a time.
5. Fix the narrowest authoritative cause, not a downstream symptom.
6. Verify the original symptom with fresh focused evidence.

Do not use broad retries, catches, fallbacks, defaults, or defensive branches to hide an unexplained failure. Temporary instrumentation is justified only when it distinguishes hypotheses.

## Specialist leaf trigger

Load one child only when the remaining causal uncertainty is specifically inside a material specialist boundary:

- trust/permission/rejection behavior → `specialists/security.md`
- persistence/order/race/transaction/restart behavior → `specialists/state.md`
- version/public-contract/environment coexistence → `specialists/compatibility.md`
- measured hot path/resource behavior → `specialists/performance.md`

`quality.md` and `interface.md` are not diagnosis leaves by default. Use them only if the task itself changes from diagnosis into a substantive structural or interface-quality event and the root reroutes it.

## Exit

As soon as the earliest incorrect state and authoritative repair boundary are known, stop diagnosis. Contract to the affected surface, make the smallest coherent fix, and run the cheapest check that can falsify the fix.

Add a durable regression test only when project rules, regression risk, or the evidence plan gives it lasting value.

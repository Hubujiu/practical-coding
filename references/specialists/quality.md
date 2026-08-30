# Structural Quality

Load only when the task is a substantive code review/refactor or when structural complexity itself blocks a safe material change. Do not load for routine implementation cleanup.

## Review axes

Inspect only axes material to the requested change:

1. correctness and explicit invariants;
2. simplicity/readability and unnecessary concepts;
3. ownership/module boundaries and dependency direction;
4. security or performance only when evidence triggers those specialist leaves separately.

Prefer findings that remove concepts, branches, indirection, duplication, or misplaced ownership. A few high-confidence structural findings are better than a long list of style nits.

For refactors, require an observable simplification: fewer concepts, branches, duplicated policies, or ownership leaks. Moving complexity without reducing it is not improvement.

Do not impose arbitrary LOC limits or personal style. Existing project conventions beat generic preferences unless they are the source of the material problem.

## Exit evidence

The proposed or completed change improves the requested structural property without changing unrelated behavior, and any remaining concern is clearly optional rather than disguised as a blocker.

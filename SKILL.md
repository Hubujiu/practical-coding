---
name: practical-coding
description: "Use for implementing, fixing, refactoring, or reviewing code with the least engineering process and repository context that can still produce a reliable result; execution and retrieval escalate independently only when current evidence is insufficient."
license: MIT
metadata:
  author: Hubujiu
  version: "1.3"
---

# Practical Coding

Use the least process and the least context that can still produce a reliable coding result.

Two independent ladders control cost:

- **Execution:** how much engineering structure and assurance the task needs.
- **Retrieval:** how much repository or external context the next decision needs.

Start at the lowest rung. Escalate only when fresh evidence shows the current rung is insufficient. As soon as the blocking uncertainty is resolved or the relevant boundary is localized, contract the work again. Escalation changes behavior; it does not imply that already-read context can be unloaded.

## Core

The Core applies at every execution level.

- Define the smallest observable success before editing.
- Prefer the smallest coherent reachable change that satisfies the current requirement and established contracts.
- Stop at the first implementation rung that works: do nothing; reuse the nearest project primitive; use the standard library; use a native platform feature; use an already-available dependency; one line; otherwise write the minimum local code.
- Add no speculative options, wrappers, aliases, configuration, scaffolding, helper layers, extension points, or one-implementation interfaces.
- Prefer deletion and boring code. Keep unrelated code and existing user changes untouched.
- Add validation, fallback, retry, documentation, comments, or tests only when required by stated behavior, an established project rule or contract, or necessary verification.
- Verify the final state with the cheapest focused check that can falsify the material claim. Do not repeat an unchanged check.
- State only what fresh evidence supports.
- Do not escalate because a task sounds complex, touches many files, or contains a risk-related noun. Escalate because the current rung cannot answer the next material question or support the required claim.

## Decision Gate

Decision is a gate before or during execution, not an execution level.

Load `references/decision.md` only when a material choice remains genuinely open, would change the next action, and cannot be settled from the request, repository, established contracts, or cheap reversible defaults. A choice already specified or authorized by the user is settled input.

Resolve the choice, then continue at the lowest execution and retrieval rungs consistent with the new facts. If a substantial Decision context would otherwise remain resident while later specialist work is likely, prefer an isolated Decision worker when the context saved exceeds handoff cost.

## Execution Ladder

### E0 — Direct

Default here.

Use E0 when the target behavior, governing contract, and sufficient focused check are already clear enough to make the smallest coherent change.

Do not load a reasoning reference.

### E1 — Guided

Stay Core-only, but spend one bounded local step to remove a specific uncertainty that blocks Direct work.

Examples:

- inspect the nearest caller, contract, sibling pattern, or focused test;
- confirm one assumption about current behavior;
- identify the smallest check that can falsify the change.

Escalate beyond E1 only when that bounded step fails to resolve the blocker. Do not turn ordinary local inspection into a workflow.

### E2 — Structured

Load exactly one specialist reasoning capability when evidence shows Core-only work is insufficient:

- **Debugging:** an observed failure, regression, incorrect behavior, or failed verification still lacks an evidenced cause → read `references/debugging.md`.
- **Implementation:** safe execution is blocked by an unknown contract or invariant, an unresolved material risk boundary, or insufficient evidence for a risky material claim → read `references/implementation.md`.

Use that module at its structured depth. Do not load both in the same root context merely because both could be relevant.

### E3 — Assurance

E3 is deeper use of the already-selected specialist capability, not another module.

Escalate from E2 only when a material claim still cannot be supported because the relevant boundary spans multiple callers, states, compatibility modes, side-effect phases, or high-impact rejection/rollback/race behavior. Expand evidence only as far as the unresolved guarantee requires.

Security/permissions, irreversible side effects, persistence/migration, concurrency/transactions, and compatibility often justify E3 **only when their material guarantee remains unresolved**. Their presence alone does not.

### De-escalation

When the cause, contract, invariant, or evidence boundary becomes clear:

1. stop broad diagnosis or assurance work;
2. contract to the smallest affected surface;
3. implement the smallest coherent fix/change;
4. run the cheapest sufficient final check.

Do not continue a higher-level ritual after its blocker is gone.

## Retrieval Ladder

Retrieval is independent of the Execution Ladder. A simple edit may need broad discovery; a difficult bug may already have a known target.

### R0 — Target

Use current context, a known path, symbol, error, route, test, or configuration. Read only the source needed for the next decision.

### R1 — Local

When the target is unknown or one local relation is missing, use bounded/ranked filename, text, symbol, reference, or host-native source search within the nearest plausible scope. Prefer limits, top-k, pagination, and batched narrow queries.

### R2 — Structural

When the unresolved question is primarily relational—callers, callees, imports, implementations, inheritance, dependencies, or cross-file flow—use an already-available structural capability when it materially reduces exploration. Otherwise reconstruct only the needed relationship with bounded source search.

### R3 — Repository

Expand to repository-wide discovery only when R0–R2 cannot localize the relevant boundary or when the task requires a bounded exhaustive repository claim. Do not dump broad result sets into context; narrow candidates before reading source.

### R4 — External

Use authoritative external evidence only when the task depends on behavior not established by the repository itself, such as a current framework/API contract, compatibility fact, license, or maintained external implementation. Prefer primary maintained sources.

### Retrieval contraction

After any expansion identifies the relevant files, symbols, relationships, or external contract, contract back to that bounded surface. Do not keep searching at the widest scope merely because it was once necessary.

Current source remains authoritative for repository behavior.

Read `references/navigation.md` only when R2/R3 retrieval itself becomes substantial enough to benefit from its detailed procedure. Routine R0/R1 work does not need it.

## Isolation Gate

Direct work and small E1/E2 work use no worker. Keep the root to the Core plus at most one loaded reasoning reference.

When a second substantial event or broad Navigation effort would accumulate more context than a handoff costs, dispatch one worker. The worker reads `references/delegation.md` plus exactly one assigned reference and returns a compact evidence capsule.

- Decision, Debugging, and Navigation workers are read-only.
- An Implementation worker may write only when explicitly assigned implementation, with a bounded non-overlapping scope and no competing writer.
- Do not build worker pipelines or overlap writers.

## Benchmark Contract

The ladder names are operational hypotheses, not permanent architecture. Benchmark them.

Measure at least:

- correctness, safety, build/reachability;
- tokens, time, tool calls, LOC, and references loaded;
- **over-escalation:** the adaptive run uses a higher rung than the lowest quality-qualified rung;
- **under-escalation:** a lower selected rung fails while a higher capped rung quality-qualifies;
- minimum-sufficient rung distribution for both axes.

If a rung is rarely or never the minimum sufficient rung, test merging or removing it. If one rung repeatedly contains both under- and over-escalation clusters, test splitting or moving its boundary. Do not preserve the number or names of levels for aesthetic symmetry.

Runtime agents do not read `evolution/`. Benchmark and Skill-maintenance work may use it to retain patterns, accepted experiments, and rejected changes across iterations.

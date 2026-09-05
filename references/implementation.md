# Implementation

**Tree depth: 1**

Enter only when an unresolved governing contract, coordinated guarantee, or material risk/evidence boundary blocks safe change. Settled local changes stay at Core.

## Establish the Boundary

Identify the authoritative invariant and minimum producers, consumers, adapters, state, and checks that must move together. Read only their material paths. Mapping/report-only requests authorize no implementation.

Preserve public compatibility unless a break is authorized. For migrations, choose one internal representation and keep temporary compatibility at the narrowest required boundary. Put validation where the guarantee is owned, before side effects.

## Implement and Falsify

Make the smallest reachable end-to-end change using existing primitives. Add retries, wrappers, fallbacks, or dependencies only for a demonstrated boundary; nearby extensibility is not a requirement.

Choose evidence that could falsify each material claim, not just the easiest green test. Preserve required build gates. Exercise old/new callers for compatibility, rollback/restart for persistence, race behavior for concurrency, and valid plus representative rejected inputs for permissions. Confirm rejection before side effects. Use broader integration checks only when the changed guarantee spans that boundary.

Report checks actually executed and any missing prerequisites. Never infer behavioral correctness from a diff or a passing format check alone.

## Local Router

This node is a leaf. Resolve ordinary technical choices with project convention or the smallest sufficient reversible option; do not automatically open Decision. Ask only a blocking user-owned choice with no safe default. Correct failures introduced by this candidate here. Return a genuinely different unexplained top-level failure to Core.

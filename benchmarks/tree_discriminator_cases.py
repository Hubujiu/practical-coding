"""Parent-local discriminator cases for staged router children.

These are cheap trigger/boundary diagnostics, not release-quality task verifiers.
They intentionally expose only the parent router text; child bodies are not loaded.
"""

from __future__ import annotations


CASES = [
    {
        "case_id": "debug-dynamic-browser-worker",
        "parent": "debugging",
        "expected": "dynamic-evidence",
        "prompt": (
            "A browser export occasionally completes after cancellation. The static call path is known, "
            "but the failure only appears under worker/message timing and no current trace distinguishes "
            "whether cancellation, progress delivery, or worker completion wins the race."
        ),
    },
    {
        "case_id": "debug-dynamic-ci-environment",
        "parent": "debugging",
        "expected": "dynamic-evidence",
        "prompt": (
            "A test passes locally and fails only in CI. The same source revision is used; the next useful "
            "step is to compare runtime/config/process facts and capture evidence at the failing process boundary."
        ),
    },
    {
        "case_id": "debug-parent-deterministic-trace",
        "parent": "debugging",
        "expected": "parent",
        "prompt": (
            "A focused unit test deterministically fails. The stack trace and source show parse_bool does not "
            "strip whitespace before lowercasing, and the shared caller path is already identified."
        ),
    },
    {
        "case_id": "debug-parent-simple-exception",
        "parent": "debugging",
        "expected": "parent",
        "prompt": (
            "A deterministic exception points at a single invalid index calculation. Reproduction, earliest "
            "incorrect state, and the focused falsifying test are already available from the local trace."
        ),
    },
    {
        "case_id": "impl-security-authz-side-effect",
        "parent": "implementation",
        "expected": "security-boundary",
        "prompt": (
            "Add a privileged delete endpoint. The unresolved invariant is that authenticated users without "
            "the resource permission must be rejected before any durable deletion or external notification."
        ),
    },
    {
        "case_id": "impl-security-secret-rotation",
        "parent": "implementation",
        "expected": "security-boundary",
        "prompt": (
            "Rotate an API credential. The unresolved work is the authoritative authentication/revocation "
            "boundary and proving invalid or revoked credentials cannot reach the protected side effect."
        ),
    },
    {
        "case_id": "impl-migration-public-field",
        "parent": "implementation",
        "expected": "migration-compatibility",
        "prompt": (
            "Rename a required public response field while old clients must keep working for one release. "
            "New and old versions will coexist, and rollback must remain possible before the compatibility window ends."
        ),
    },
    {
        "case_id": "impl-migration-persisted-enum",
        "parent": "implementation",
        "expected": "migration-compatibility",
        "prompt": (
            "Change a persisted integer status to strings. Existing rows and an older reader can coexist during "
            "deployment, and the migration must define backfill, mixed-version behavior, cleanup, and rollback."
        ),
    },
    {
        "case_id": "impl-state-idempotent-retry",
        "parent": "implementation",
        "expected": "state-concurrency",
        "prompt": (
            "A webhook may be delivered more than once and the handler can retry after a timeout. The unresolved "
            "guarantee is whether the durable state transition is idempotent and atomic across duplicate delivery."
        ),
    },
    {
        "case_id": "impl-state-reset-race",
        "parent": "implementation",
        "expected": "state-concurrency",
        "prompt": (
            "Concurrent session reset and update can interleave. The unresolved invariant is the authoritative "
            "state owner, transition ordering, atomicity, and what survives restart."
        ),
    },
    {
        "case_id": "impl-negative-new-local-validation",
        "parent": "implementation",
        "expected": "parent",
        "prompt": (
            "Add validation for a new internal configuration value. There are no old versions, no untrusted "
            "external caller, no privilege boundary, and no concurrent mutation; the owning parser is already known."
        ),
    },
    {
        "case_id": "impl-negative-known-compatible-addition",
        "parent": "implementation",
        "expected": "parent",
        "prompt": (
            "Add a new optional JSON response field using the repository's established serializer. It is additive, "
            "old clients ignore unknown fields, no persisted data changes, and rollback is a normal code revert."
        ),
    },
    {
        "case_id": "impl-hard-negative-security-not-migration",
        "parent": "implementation",
        "expected": "security-boundary",
        "prompt": (
            "The token string format remains unchanged and no old/new representation coexistence is needed. "
            "The blocker is ensuring revoked tokens are denied before a privileged mutation."
        ),
    },
    {
        "case_id": "impl-hard-negative-migration-not-state",
        "parent": "implementation",
        "expected": "migration-compatibility",
        "prompt": (
            "There is no concurrent writer and no retry behavior. The blocker is moving persisted rows to a new "
            "representation while the previous application version can still read during rolling deployment."
        ),
    },
    {
        "case_id": "impl-hard-negative-state-not-security",
        "parent": "implementation",
        "expected": "state-concurrency",
        "prompt": (
            "Authorization is already settled and inputs are trusted. The blocker is preventing two concurrent "
            "workers from both applying the same durable transition after duplicate queue delivery."
        ),
    },
]


CASE_IDS = {case["case_id"] for case in CASES}

"""Frozen real-repository cases for evolvable router-tree experiments.

These cases score delivered evidence and manual-mode discipline. They intentionally
contain no expected automatic node, depth, or capability path. Automatic topology
is inferred by parent-versus-child capability ceilings and adaptive traces.
"""

from __future__ import annotations


REPOSITORIES = {
    "personal-progress": {
        "url": "https://github.com/Hubujiu/personal-progress.git",
        "commit": "515c2e2193c3d547e04e65687da6666dc877ab61",
        "local_name": "personal-progress",
    },
    "cover-atelier": {
        "url": "https://github.com/Hubujiu/cover-atelier.git",
        "commit": "fc3b12b3a944f45b5a1d19963e29307d95b120fb",
        "local_name": "cover-atelier",
    },
    "super-agent": {
        "url": "https://github.com/java-up-up/super-agent.git",
        "commit": "d44edf063032a2d8797549411f11923aa4a83ec3",
        "local_name": "super-agent",
    },
}


def _case(
    task_id: str,
    repository: str,
    family: str,
    prompt: str,
    required: list[list[str]],
    *,
    probe_terms: list[list[str]] | None = None,
    manual_request: str | None = None,
) -> dict[str, object]:
    return {
        "task_id": task_id,
        "repository": repository,
        "family": family,
        "prompt": prompt,
        "required": required,
        "probe_terms": probe_terms or [],
        "manual_request": manual_request,
    }


CASES = [
    _case(
        "pp-known-contract",
        "personal-progress",
        "known-target",
        "Read progress-core/src/main/java/com/hubujiu/progress/core/database/PluginDatabaseNames.java only. Report the schema and role naming invariants and why long plugin IDs cannot collide. Do not edit files.",
        [["63", "max_identifier_bytes"], ["sha-256", "digest"], ["plugin_", "plugin_role_"]],
    ),
    _case(
        "pp-lifecycle-map",
        "personal-progress",
        "structural-read",
        "Trace install/start/stop from the platform API into lifecycle execution. Identify the controller, lifecycle service, operation executor, and state machine with source paths. Report only; do not edit files.",
        [["PluginManagementController"], ["PluginLifecycleService"], ["PluginOperationExecutor", "DefaultPluginOperationExecutor"], ["PluginStateMachine"]],
    ),
    _case(
        "pp-running-after-throw",
        "personal-progress",
        "unexplained-failure",
        "An operation sometimes remains RUNNING after its worker throws. The cause is not established. Inspect the operation executor and focused tests, identify the earliest incorrect state transition, and name the cheapest falsifying test. Diagnose only; do not edit files.",
        [["DefaultPluginOperationExecutor", "runCommand"], ["PluginOperationExecutorTest", "errorIsNotSwallowedAsOperationFailure", "commandErrorDoesNotLeaveOperationRunning"], ["RUNNING"], ["fail", "exception", "complete"]],
    ),
    _case(
        "pp-token-rotation-boundary",
        "personal-progress",
        "risk-boundary",
        "Plan a zero-downtime rotation of the bootstrap admin token. Map the authoritative filter/configuration boundary, protected platform entry points, rejection-before-side-effect behavior, and focused evidence. Use existing project boundaries rather than opening a technology-selection discussion. Report only; do not edit files.",
        [["BootstrapAdminTokenFilter"], ["PlatformSecurityConfiguration"], ["401", "unauthorized", "reject"], ["PlatformManagementApiTest", "PluginDispatchApiTest"]],
    ),
    _case(
        "pp-compatibility-manual-decision",
        "personal-progress",
        "manual-decision",
        "Explicit decision request: compare a breaking rename versus a one-release compatibility alias for a required public plugin-dispatch response field while old plugins and clients coexist. Inspect the current HTTP/view contract as needed and recommend one option with its strongest trade-off. Do not implement.",
        [["Recommendation:", "recommendation", "recommend", "Decision:", "choose", "推荐", "建议", "决定", "选择"], ["trade-off", "tradeoff", "cost", "权衡", "代价"], ["alias", "compatib"], ["one release", "one-release", "release window"]],
        manual_request="decision",
    ),
    _case(
        "ca-export-format-known",
        "cover-atelier",
        "known-target",
        "Read src/lib/exportFormat.ts only and report each export format's MIME type, extension, and explicit quality value when present. Do not edit files.",
        [["image/jpeg", "jpeg"], ["image/webp", "webp"], ["image/avif", "avif"], ["image/png", "png"]],
    ),
    _case(
        "ca-cancel-download",
        "cover-atelier",
        "unexplained-failure",
        "Users report that cancelling an export sometimes still downloads a file. The cause is not established. Inspect the cancellation path and focused tests, identify the earliest observable boundary to probe, and name the single cheapest falsifying test. Diagnose only; do not edit files.",
        [["AbortController", "AbortSignal", "signal", "abort()", "abort"], ["exportCover"], ["focused", "suite", "existing test", ".test."], ["probe", "test"]],
    ),
    _case(
        "ca-new-format-existing-pattern",
        "cover-atelier",
        "settled-local-choice",
        "Plan the smallest coherent change to add one more image format by following the repository's existing export-format configuration and encoder boundary. Do not ask the user to choose an architecture or abstraction if the repository already settles it. Map the affected config, filename, orchestration, encoder boundary, and focused tests. Report only; do not edit files.",
        [["exportFormat"], ["exportFilename"], ["exportCover"], ["encoder", "avifEncoder"], ["test"]],
    ),
    _case(
        "ca-avif-stall-evidence",
        "cover-atelier",
        "uncertain-performance",
        "Large AVIF exports are reported to stall the UI, but no timing evidence exists. Map the main-thread/worker boundary and propose one bounded measurement that separates encode latency, progress delivery, memory pressure, and cancellation. Diagnose and report only; do not edit files.",
        [["avifEncoder.worker.ts"], ["encodeAvif", "avifEncoder"], ["performance", "duration", "latency", "measure"], ["memory"], ["cancel", "Abort"]],
    ),
    _case(
        "ca-export-filename-probe",
        "cover-atelier",
        "focused-verification",
        "Run the focused exportFilename test once to establish the current filename contract, then report the exact command and outcome. Do not edit files or run the full test suite.",
        [["exportFilename"], ["Outcome:", "pass", "passed", "blocked", "failed", "error", "could not", "unable", "无法", "未运行", "tests"]],
        probe_terms=[["exportfilename"], ["npm", "vitest"]],
    ),
    _case(
        "sa-memory-map",
        "super-agent",
        "structural-read",
        "Trace the memory comparison HTTP path from MemoryDemoController through MemoryComparisonService to the no-memory, sliding-window, and summary-compression implementations. Report paths and symbols only; do not edit files.",
        [["MemoryDemoController"], ["MemoryComparisonService"], ["NoMemoryChatService"], ["SlidingWindowMemoryChatService"], ["SummaryCompressionMemoryChatService"]],
    ),
    _case(
        "sa-sensitive-rejection-boundary",
        "super-agent",
        "risk-boundary",
        "Review where sensitive-word rejection occurs in the Spring AI Alibaba request path. Map interceptor registration and callers, define rejection-before-model-side-effect behavior, and identify the narrowest security tests needed. Use the existing request architecture rather than opening a framework choice. Report only; do not edit files.",
        [["SensitiveWordInterceptor"], ["SpringAiAlibabaAgentService"], ["reject", "before"], ["test"]],
    ),
    _case(
        "sa-memory-reset-concurrency",
        "super-agent",
        "state-boundary",
        "Review ResettableMemorySaver and its use by SpringAiAlibabaAgentService for concurrent sessions, reset ordering, and restart semantics. Identify the authoritative state owner and the smallest concurrency evidence. Resolve ordinary implementation choices from the existing code. Report only; do not edit files.",
        [["ResettableMemorySaver"], ["SpringAiAlibabaAgentService"], ["concurrent", "thread"], ["reset", "clear"], ["restart", "durable", "memory"]],
    ),
    _case(
        "sa-memory-strategy-manual-decision",
        "super-agent",
        "manual-decision",
        "Explicit decision request: for this repository's conversational memory example, compare the existing sliding-window and summary-compression approaches for a long-running support chat where bounded context cost matters more than exact verbatim recall. Inspect the current implementations as needed, then recommend one with its strongest trade-off. Do not implement.",
        [["Recommendation:", "recommendation", "recommend", "Decision:", "choose", "推荐", "建议", "决定", "选择"], ["trade-off", "tradeoff", "cost", "权衡", "代价"], ["SlidingWindowMemoryChatService", "sliding-window"], ["SummaryCompressionMemoryChatService", "summary-compression"]],
        manual_request="decision",
    ),
    _case(
        "sa-module-compile-probe",
        "super-agent",
        "focused-verification",
        "Compile the ai-example-spring-ai-memory module once with its required reactor dependencies to establish current reachability. Report the exact Maven command and outcome; do not edit files or run unrelated modules.",
        [["ai-example-spring-ai-memory"], ["build success", "success", "compiled"]],
        probe_terms=[["mvn", "mvnw"], ["ai-example-spring-ai-memory"], ["-pl"]],
    ),
]


TASK_IDS = {case["task_id"] for case in CASES}
MANUAL_IDS = {case["task_id"] for case in CASES if case["manual_request"]}
AUTOMATIC_IDS = TASK_IDS - MANUAL_IDS

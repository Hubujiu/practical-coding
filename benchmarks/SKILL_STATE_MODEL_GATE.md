# Model-backed gate for execution-state projection

This protocol evaluates the SKILL.state-inspired runtime substrate without changing the automatic router topology. It is separate from the deterministic schema/merge contract and from the capability-ceiling analysis that evolves Core, Debugging, and Implementation.

## Question

For genuinely long coding tasks, can a compact validated current-state projection preserve or improve delivered quality while reducing reconstruction, stale-fact drift, repeated work, and accumulated context?

The benchmark must not assume the paper's reported accuracy or token results transfer to this repository.

## Frozen arms

Run identical tasks, repository snapshots, model settings, tools, timeouts, scorer, and observation sequence under these arms:

1. **Full history** — current tree and normal accumulated conversation; no execution-state projection.
2. **State shadow** — current tree plus validated state, while the host still retains history. This measures whether explicit state helps reconstruction, but it cannot support a bounded-context claim.
3. **State history-free** — current tree; every model step receives only immutable loaded procedure `P`, validated current state `Σ`, latest observation `O`, and a bounded validation error on retry. Prior messages are omitted by the host.
4. **No skill full history** — absolute-quality reference using the same task and repository evidence, not an execution-state ablation substitute.

The automatic route, retrieval policy, available tools, and manual-mode rules remain identical in arms 1–3. Execution state must never appear in `TREE_TRACE`.

## Case families

Use real repositories and tasks long enough to create state pressure. The frozen suite should include multiple examples of each mechanism:

- delayed dependency: a fact observed early becomes necessary many actions later;
- corrective observation: branch head, check status, contract, or environment fact changes and must replace stale state immediately;
- distractor noise: unrelated logs or repository events appear between relevant observations;
- repeated hypothesis pressure: the agent must remember rejected causes or checks without replaying raw output;
- coordinated implementation: current producers, consumers, change surface, and verification must stay synchronized;
- history-required control: audit/provenance or intentionally evolving-schema tasks where the state arm must preserve bounded artifact pointers or decline history-free execution.

Do not encode a gold automatic node. Reuse the tree benchmark's delivered-quality scorer and topology-neutral route analysis.

## Freeze discipline

During iteration, run `n=1` only. Before a release comparison, freeze:

- case prompts and repository commits;
- observation injector and noise schedule;
- model, reasoning level, tools, harness, timeout, and worker count;
- state schema, prompt adapter, retry cap, scorer, and all acceptance thresholds;
- baseline/candidate refs and complete artifact manifest.

Then run the complete paired matrix at `n>=3`. A scorer fix invalidates all affected arms and requires rerunning them on identical evidence.

## Required artifacts

Retain per cell:

- initial prompt, every actual model request, response, validation error, and accepted transition;
- canonical state snapshots and patches;
- actions/tool calls, tool outputs, final answer, workspace diff, and focused/full checks;
- prompt/input/output token counts, duration, retry count, and infrastructure status;
- route trace, manual-mode trace, and repository/model/harness provenance.

Published summaries may redact machine paths or secrets, but the local audit trail must remain complete.

## Metrics

Quality gates cost:

1. delivered correctness, required build/checks, safety, compatibility, and user constraints;
2. zero spontaneous Decision/Clarification activation and valid automatic parent-child paths;
3. no quality-affecting premature overwrite/deletion, stale control fact, or execution of a rejected transition;
4. invalid-patch rate, validation retries, repeated actions/checks/hypotheses, and stale-fact recovery steps;
5. per-step and cumulative prompt/input/output tokens, duration, and tool calls.

Also report state JSON size and activation/exit timing, but do not optimize those proxies at the expense of delivered behavior.

## Acceptance

The state candidate is release-eligible only when the complete paired `n>=3` run has no infrastructure failure and:

- state history-free does not regress delivered quality, safety, required checks, manual-mode discipline, or topology validity against full history;
- the deterministic state contract remains 100% passing;
- no rejected transition action is executed;
- any history-required case retains bounded immutable evidence pointers rather than silently discarding required provenance;
- cost is used only after the quality gate. At equal quality, prefer lower cumulative input tokens, then lower duration/tool cost;
- a bounded or horizon-independent prompt claim is made only for the history-free arm and only from the actual captured requests, not from a synthetic byte model.

State shadow can be accepted as a reconstruction aid without making a bounded-context claim. A failed history-free arm is evidence to revise activation, schema, host integration, or the history escape hatch—not evidence to add execution state as a router child.

## Interpretation

Keep semantic state failures distinct from format failures:

- format/schema/type/size error: deterministic validator or constrained generation issue;
- premature overwrite/deletion: schema or state-update-policy issue;
- stale fact not replaced: transition or observation-authority issue;
- repeated action/hypothesis: missing future-relevant state;
- quality loss with valid state: projection may be omitting information whose relevance was not predictable;
- no cost reduction while history remains attached: expected host-boundary limitation, not proof against the mechanism.

Record rejected variants and mechanism-level lessons in `evolution/`; do not patch the router boundary merely to force a favorable state result.

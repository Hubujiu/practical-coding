# Retired execution-state / history-free experiment

Status: **Rejected and removed from the active runtime**

Decision date: 2026-09-03
Last active branch head before retirement: `215334db7bb914bd9f0346a2b09654fc89accc96`

## What was tried

The experiment added a bounded explicit coding state, merge-patch transitions, a history-free host boundary, exact outbound transport auditing, and a four-arm model gate:

- full history;
- state shadow;
- state history-free;
- no-skill full history.

The proposal was intentionally kept outside the Router tree.

## Evidence

The final complete standard `n=1`, `workers=1` matrix contained 24 determinate cells:

| Arm | Passed | Uncached input tokens | Duration |
|---|---:|---:|---:|
| full-history | 6/6 | 50,736 | 154.57s |
| no-skill-full-history | 6/6 | 19,722 | 123.61s |
| state-history-free | 6/6 | 78,118 | 172.60s |
| state-shadow | 5/6 | 56,611 | 156.83s |

The history-free candidate preserved delivered quality and its captured client transport contract passed. It did not establish a cost benefit:

- uncached input tokens were approximately **54.0% higher** than full history;
- total duration was approximately **11.7% higher** than full history;
- state shadow retained a rejected cache hypothesis as active in one case;
- formal `n>=3`, token, latency, and 10/25/50/100 bounded-horizon gates remained incomplete.

A later deterministic invariant rejected overlapping active/rejected hypothesis IDs, but that hardening was not rerun through the model matrix before retirement.

Separate tree evidence found the Core fixed cost on simple work acceptable, while the remaining cost problem was concentrated in retrieval over-expansion and oversized evidence. Execution state did not address that upstream cause and introduced a large runtime, transport, test, and benchmark maintenance surface.

## Decision

Reject the execution-state/history-free architecture for Practical Coding and remove it from:

- `SKILL.md`, `AGENTS.md`, README files, and the agent default prompt;
- active runtime and host/transport code;
- active deterministic and four-arm benchmark code;
- active topology metadata and CI gates.

The old experiment records are retained in this directory. Historical commits and locally preserved raw benchmark artifacts remain the authoritative detailed evidence; old results are not rewritten.

## Follow-up direction

Cost work returns to retrieval convergence:

- bound each search/read output;
- stop broad inventory once candidate paths or symbols are known;
- require explicit evidence before reading dependency internals;
- isolate large logs and test output instead of carrying them through later turns.

This is a retrieval-policy problem, not a reason to alter the current Core → Debugging / Implementation topology.

## Reconsideration condition

Do not restore the removed code. A future proposal must start as a new frozen experiment and provide independent evidence that a substantially simpler host-native mechanism:

1. solves a demonstrated long-horizon failure not addressed by retrieval/output bounds;
2. preserves required quality across a complete paired `n>=3` matrix;
3. reduces both quality-qualified uncached input tokens and end-to-end time;
4. passes bounded-horizon and final transport audits without reintroducing comparable maintenance cost.

## Preserved records

The original experiment and contract documents are archived under:

- [`experiments/`](experiments/)
- [`reference/`](reference/)

Key historical commits include:

- `d85c72cc5aa239da32352309e723ed1e6fc80429` — audited history-free host;
- `ea8580f169154cab01914f4c76e369f1a26f91f8` — four-arm runner;
- `0499fd15d3f2f6de65ec0681e96956ca4964113d` — scorer and Codex SSE hardening;
- `e6cc9caa456767b3e05dbff59474aa7014146cbf` — gate-role separation;
- `e6b5aab8e85777644f56737ec335c46beb0f9986` — hypothesis partition invariant;
- `215334db7bb914bd9f0346a2b09654fc89accc96` — final pre-retirement branch head.

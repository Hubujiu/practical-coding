# Local benchmark runner (no Codex)

Use this path when Codex CLI/auth is unavailable—for example in Cursor Cloud Agent pods.

## Flow

1. **Prepare** isolated cells (workspace + prompt + skill injection).
2. **Execute** each cell with any agent that can edit the workspace (Cursor subagents, manual work, or your own driver).
3. **Score** with the same deterministic graders as `run_benchmarks.py`.

## Commands

```bash
export PATH="$HOME/.bun/bin:$PATH"

# 1) Prepare smoke delivery comparison: practical vs ponytail vs no-skill
python3 benchmarks/local_runner.py prepare \
  --profile smoke \
  --suite delivery \
  --include-baseline \
  --arm practical-current \
  --arm ponytail \
  --arm baseline \
  --output benchmark-results/local-smoke-compare

# 2) For each cell under benchmark-results/local-smoke-compare/cells/...:
#    - read prompt.txt
#    - implement inside workspace/
#    - write answer.md and duration.json (seconds or {"elapsed_seconds": N})

# 3) Score and emit report.md
python3 benchmarks/local_runner.py score \
  --output benchmark-results/local-smoke-compare \
  --model cursor-default
```

## Arms

| Arm | Meaning |
|---|---|
| `practical-current` | This repo's `SKILL.md` (+ decision inline on decision suite) |
| `ponytail` | Pinned Ponytail `SKILL.md` |
| `baseline` | No skill text (no-skill control) |

## Evidence limits

- `n=1` smoke runs are sanity checks, not stable rankings.
- Token columns stay at 0 unless the executor records usage.
- The official Codex Luna harness remains in `run_catalog.py` / `run.ps1`.

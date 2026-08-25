# Practical Coding

<p align="center">
  <a href="https://github.com/Hubujiu/practical-coding/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT"></a>
  <a href="https://agentskills.io"><img src="https://img.shields.io/badge/Agent_Skills-Compliant-success.svg" alt="Agent Skills Compliant"></a>
  <img src="https://img.shields.io/badge/Version-2.0-blue.svg" alt="Version 2.0">
  <img src="https://img.shields.io/badge/Supports-Claude_Code_|_Cursor_|_Copilot_|_Gemini_|_Antigravity_|_Codex_|_Goose-purple.svg" alt="Compatible Agents">
  <a href="https://github.com/Hubujiu/practical-coding/pulls"><img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg" alt="PRs Welcome"></a>
</p>

<p align="center">
  🌐 <b>English</b> | <a href="README_zh.md">简体中文</a>
</p>

---

> **One coding skill, load only what the task needs.**  
> Practical Coding is a lean, event-driven coding skill for AI agents. It eliminates LLM over-engineering, skips bureaucratic process ceremony, and delivers surgical, production-ready code with fresh evidence.

---

## 📑 Table of Contents

- [The Problems We Solve](#-the-problems-we-solve)
- [Inspirations & Lineage (The Synthesis of Giants)](#-inspirations--lineage-the-synthesis-of-giants)
- [Architecture & How It Works](#-architecture--how-it-works)
- [The Always-On Core](#-the-always-on-core)
- [The 5 Modular Pillars](#-the-5-modular-pillars)
- [Subagent Delegation & Isolation Gate](#-subagent-delegation--isolation-gate)
- [Optional Codebase Memory (AST & LSP Intelligence)](#-optional-codebase-memory-ast--lsp-intelligence)
- [Quick Start & Installation](#-quick-start--installation)
- [Configuration](#-configuration)
- [Repository Structure](#-repository-structure)
- [Luna Benchmarks](#-luna-benchmarks)
- [Contributing & License](#-contributing--license)

---

## ⚡ The Problems We Solve

AI coding assistants are prone to two major failure modes:
1. **The AI Bloat Trap (Over-Engineering)**: Writing speculative abstractions, nested wrappers, unrequested fallback/retry logic, defensive catch-alls, and bloated boilerplate tests for simple 2-line edits.
2. **The "Process Ceremony" Tax**: Heavy multi-stage agent frameworks force *every* task (even fixing a typo or CSS color) through rigid 5-stage sequential pipelines (*Brainstorm → Plan → TDD → Review → Git Ceremony*), burning massive token budgets and causing developer fatigue.

Conversely, unconstrained single-prompt agents fail when facing complex multi-file refactors or tricky bug diagnoses due to lack of engineering discipline.

### How Practical Coding Compares

| Dimension / Task | Rigid Agent Frameworks | Naive / Unconstrained LLMs | 🚀 Practical Coding |
|---|---|---|---|
| **Simple / Local Edits** *(e.g. fix CSS, rename var)* | Heavy multi-step ceremony; burns tokens on unneeded plans & tests | Fast, but risks touching unrelated code | **Direct Path**: Zero references loaded, zero subagent overhead, executes immediately |
| **Complex / Risky Features** | Rigid pipeline overhead across every single step | Hallucinates architecture or misses critical boundaries | **Event-Driven Router**: Loads `decision.md` or `implementation.md` only when an unresolved choice, contract, or material risk requires it |
| **Bug Diagnosis** | Often writes boilerplate test suites before finding the bug | Patches downstream symptoms with `try/catch` & fallback hacks | **Evidence-First**: Reproduce → Earliest broken state → Single hypothesis → Root cause fix |
| **Subagent Workers** | Arbitrary subagent proliferation & pipeline chains | Single-context overload | **Economic Isolation Gate**: Dispatches workers only when avoided context clearly exceeds handoff cost |
| **Reusing Solutions** | Reinvents wheels or creates complex custom wrappers | Generates subpar custom code for solved problems | **Mature Implementation First**: Prefers stdlib → native platform → installed deps → mature upstream |
| **Code Intelligence** | Dumps full repo scans into context | Repeated slow grep/find across huge repos | **Non-Intrusive CLI Mode**: Direct AST/LSP graph via `codebase-memory-mcp` with zero permanent context pollution |

---

## 💡 Inspirations & Lineage (The Synthesis of Giants)

Practical Coding merges the best design paradigms from leading open-source agent methodologies:

```text
               ┌─────────────────────────────────────────────────────────┐
               │              DietrichGebert/ponytail                    │
               │   "Laziest Senior Dev" Pragmatism, YAGNI, Stdlib-First  │
               └────────────────────────────┬────────────────────────────┘
                                            │ (Pragmatic Philosophy)
                                            ▼
┌───────────────────────────┐      ┌─────────────────┐      ┌─────────────────────────────┐
│      obra/superpowers     │      │                 │      │      Agent Skills Spec      │
│  Engineering Rigor, TDD,  │─────►│ PRACTICAL CODING│◄─────│    (mattpocock / Anthropic) │
│  Delegation & Verification│      │                 │      │    Progressive Disclosure   │
└───────────────────────────┘      └────────┬────────┘      └─────────────────────────────┘
  (Decoupled from rigid pipeline)           │ (Structured Graph)
                                            ▼
               ┌─────────────────────────────────────────────────────────┐
               │             DeusData/codebase-memory-mcp                │
               │    Tree-sitter AST, Hybrid LSP, CLI-mode Intelligence   │
               └─────────────────────────────────────────────────────────┘
```

### 1. 🦄 [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) — *The Pragmatic Senior Dev Mindset*
- **What we adopted**: The ruthless **YAGNI** principle, the **ladder** (does this need to exist → already in this codebase → stdlib → native platform feature → installed dependency → one line → minimum custom code), deletion over addition, shortest working diff, and terse unrequested delivery prose.
- **How Practical differs**: Ponytail's runtime supports explicit intensity modes through host-specific plugins/hooks. Practical Coding stays a portable Agent Skill: it does not ask the model to infer a mode and does not duplicate host runtimes. Task events alone decide whether Direct Path or an engineering module is needed.

### 2. ⚡ [obra/superpowers](https://github.com/obra/superpowers) — *Disciplined Engineering Capabilities*
- **What we adopted**: Systematic root-cause debugging, verification gates, and isolated subagent task contracts.
- **How we evolved it**: We **unchained** these powerful tools from mandatory linear pipelines. You no longer suffer through mandatory brainstorming or TDD ceremony for trivial changes; capabilities are triggered **only when an unresolved event occurs**.

### 3. 📦 [mattpocock/skills](https://github.com/mattpocock/skills) & [Agent Skills Spec](https://agentskills.io) — *Progressive Disclosure*
- **What we adopted**: Ultra-lean entry footprint. [`SKILL.md`](SKILL.md) remains a compact resident router; deep reference modules are read only when routed.

### 4. 🧠 [DeusData/codebase-memory-mcp](https://github.com/DeusData/codebase-memory-mcp) — *Zero-Bloat Code Intelligence*
- **What we adopted**: Industrial-grade Tree-sitter AST parsing, Hybrid LSP semantic resolution, and persistent code graphs.
- **How we evolved it**: Instead of permanently injecting a heavy MCP server and tool definitions into the agent's system prompt, Practical Coding invokes upstream in **one-shot CLI mode** only when navigation value justifies it.

---

## 🏗️ Architecture & How It Works

Practical Coding is an **Event-Driven Router** backed by an **Always-On Core**. There is no routing-intensity mode: simple work is naturally Direct Path, while unresolved complexity or risk naturally escalates.

```mermaid
flowchart TB
    Task["🎯 User Task / Coding Request"] --> Core["⚡ SKILL.md<br/>Shortest-path Core & Event Router"]

    Core -->|"Local & Well-Understood"| Direct["🚀 Direct Path<br/>Root agent executes immediately<br/>(No modules, no subagents)"]
    Core -->|"Unresolved Material Choice"| D["🧭 Decision Module<br/>(references/decision.md)"]
    Core -->|"Unmapped Contract or Material Risk"| I["🏗️ Implementation Module<br/>(references/implementation.md)"]
    Core -->|"Observed Bug / Cause Unknown"| G["🔍 Debugging Module<br/>(references/debugging.md)"]
    Core -->|"Broad Codebase Navigation"| E["🗺️ Exploration Module<br/>(references/exploration.md)"]
    E -->|"codebase_memory.enabled: true"| M["🧠 Codebase Memory (CLI Mode)<br/>(references/codebase-memory.md)"]

    subgraph IsolationGate["⚖️ Economic Isolation Gate"]
        IG{"Avoided Context & Parallelism<br/>>> Startup + Handoff Cost?"}
        IG -->|"Yes"| Worker["🤖 Isolated Worker Subagent<br/>(Reads references/delegation.md + 1 module)"]
        IG -->|"No"| RootExec["👤 Root Agent Loads Module Locally"]
    end

    D -.-> IG
    I -.-> IG
    G -.-> IG
    E -.-> IG
    M -.-> IG

    Worker -->|"Returns compact evidence capsule"| Done["✅ Fresh Evidence Check & Completion"]
    RootExec --> Done
    Direct --> Done
```

---

## 🛡️ The Always-On Core

The Core is deliberately the shortest useful path for ordinary coding work, not a compressed checklist of every engineering concern:

1. **Read First, Then Be Lazy**: Understand the requested outcome and the code it actually touches; a familiar feature name implies only its named behavior, never every conventional extra.
2. **The Ladder**: Stop at the first rung that holds — doesn't need to exist → already in this codebase → stdlib → native platform feature → installed dependency → one line → minimum custom code.
3. **Traceable Value**: Validation, fallback, retry, config, tests, or docs must trace to a current requirement, concrete boundary, observed risk, project policy, or the cheapest evidence needed. Material risk routes to Implementation instead of bloating Core.
4. **Smallest Complete Change**: Deletion over addition, boring over clever, fewest files, shortest working diff once the problem is understood. Follow repository or platform defaults for reversible unspecified details.
5. **Untouched Scope**: Keep unrelated code and existing user modifications untouched; mark a deliberate corner cut with a one-line comment naming the ceiling.
6. **Fresh Evidence, Lean Output**: Obtain the cheapest fresh evidence before claiming completion and keep unrequested delivery prose terse.

---

## 🧩 The 5 Modular Pillars

When a task encounters an unresolved engineering event, only the matching module is loaded. **Verification is not a sixth module**: choosing sufficient evidence for a risky change is part of Implementation. Implementation is an escalation for unresolved coordination or material risk, not a mandatory stage for writing code.

| Module | Loaded When | Core Deliverable |
|---|---|---|
| 🧭 [`references/decision.md`](references/decision.md) | A material choice about architecture, dependencies, APIs, or data models remains open | Evaluates $\le 3$ viable options (stdlib/native first); chooses the smallest fitting solution. |
| 🏗️ [`references/implementation.md`](references/implementation.md) | An unmapped contract/invariant, a material risk boundary (security/permissions, irreversible side effects, persistence/migration, concurrency/transactions, compatibility), or the evidence plan for a risky change remains unresolved | Bounded change map; authoritative boundary handling; cheapest falsification ladder. |
| 🔍 [`references/debugging.md`](references/debugging.md) | An observed failure, regression, or failed verification lacks a diagnosed cause | Evidence-first: symptom → earliest broken state → single hypothesis → root cause fix. |
| 🗺️ [`references/exploration.md`](references/exploration.md) | Broad navigation of a large codebase is necessary with standard text/symbol tools | Bounded impact map (exact paths, symbols, edges) without full file dumps. |
| 🧠 [`references/codebase-memory.md`](references/codebase-memory.md) | Broad structural navigation in a project with `codebase_memory.enabled: true` | AST/LSP graph intelligence via upstream CLI across Scout, Verify, and Auditor tiers. |

---

## 🤖 Subagent Delegation & Isolation Gate

Practical Coding prevents runaway subagent proliferation through a strict **Economic Isolation Gate**:

> **The Isolation Rule:**  
> Spawn an isolated worker **only** when the context it avoids, or the parallel work it unblocks, **clearly exceeds** the startup and handoff overhead. Otherwise, keep the task in the root agent.

### Worker Protocol ([`references/delegation.md`](references/delegation.md))
- **Focused Scope**: Worker reads `delegation.md` + exactly **one** assigned module.
- **Read-Only by Default**: Decision, Exploration, Codebase Memory, Debugging, and mapping/evidence-only Implementation workers cannot modify code.
- **Sole Writer When Authorized**: An Implementation worker may write only when explicitly assigned implementation, only within its assigned directory/files, and must be the sole writer there.
- **Compact Evidence Capsule**: Workers return structured summaries (paths, symbols, diff summaries, test outputs), never raw transcripts or full file contents.

---

## 🧠 Optional Codebase Memory (AST & LSP Intelligence)

Practical Coding integrates directly with [`DeusData/codebase-memory-mcp`](https://github.com/DeusData/codebase-memory-mcp) as its structured code intelligence backend.

### Why One-Shot CLI Mode?
Instead of permanently loading upstream MCP server tools into the agent's system prompt (which wastes 1,000+ tokens on every conversation turn), Practical Coding executes upstream via one-shot CLI commands:

```bash
# Search symbols & call graphs
codebase-memory-mcp cli search_graph '{"name_pattern":".*Handler.*","label":"Function"}'
codebase-memory-mcp cli trace_call_path '{"function_name":"main","direction":"both"}'

# Check architecture & index coverage
codebase-memory-mcp cli get_architecture '{}'
codebase-memory-mcp cli check_index_coverage '{"paths":["src/core.ts"]}'
```

### CLI Resolution Order
1. Existing `codebase-memory-mcp` binary on `PATH`.
2. Official lazy npm launcher (if `npx` is available):
   ```bash
   npx --yes codebase-memory-mcp@latest cli <tool> '<json-arguments>'
   ```
3. **Graceful Fallback**: If upstream cannot be launched, the agent falls back to standard text exploration and reports that Codebase Memory was not used.

### Evidence Tiers
- 🔭 **Scout**: Rapid positive discovery. Small limits, shallow traces, marked provisional.
- 🎯 **Verify (Default)**: Normal development. Exact snippets + `check_index_coverage` validation.
- 🔬 **Auditor**: Bounded exhaustive audits. Scope coverage, pagination completion, and fallback source checking for any reported coverage gaps.

---

## 🚀 Quick Start & Installation

### One-Command Install (Recommended)

Using the standard [`skills`](https://github.com/mattpocock/skills) CLI:

```bash
npx skills@latest add Hubujiu/practical-coding
```

---

### Manual Installation by Agent Platform

#### 🟣 Claude Code
```bash
git clone https://github.com/Hubujiu/practical-coding.git ~/.claude/skills/practical-coding
```

#### 🔵 Cursor / Codex / Copilot CLI / Gemini CLI / Antigravity / Goose

**macOS & Linux:**
```bash
git clone https://github.com/Hubujiu/practical-coding.git ~/.agents/skills/practical-coding
```

**Windows (PowerShell 7):**
```powershell
git clone https://github.com/Hubujiu/practical-coding.git "$env:USERPROFILE\.agents\skills\practical-coding"
```

#### 📁 Project-Level Installation
To install Practical Coding for a specific workspace/repository:
```bash
# For Agent Skills compatible tools
git clone https://github.com/Hubujiu/practical-coding.git .github/skills/practical-coding
```

---

## ⚙️ Configuration

Enable optional Codebase Memory by adding `.practical-coding.yaml` to your project root:

```yaml
version: 1
codebase_memory:
  enabled: true
```

- `enabled: false` (or missing file): Codebase Memory is disabled; standard exploration is used without prompting.
- `enabled: true`: Upstream AST/LSP graph intelligence is enabled for large-scale navigation.

---

## 📂 Repository Structure

```text
practical-coding/
├── SKILL.md                 # Lean entry point: shortest-path Core & Event Router
├── AGENTS.md                # Agent instructions & module routing index
├── README.md                # English documentation (this file)
├── README_zh.md             # Simplified Chinese documentation
├── CONTRIBUTING.md          # Contribution guidelines
├── LICENSE                  # MIT License
├── THIRD_PARTY_NOTICES.md   # Attribution for upstream Codebase Memory MCP
├── agents/
│   └── openai.yaml          # Agent configuration profile
├── benchmarks/
│   ├── run.ps1              # PowerShell entry point
│   ├── run_benchmarks.py    # Luna isolation, grading, and aggregation
│   ├── test_benchmarks.py   # Harness regression tests
│   └── REPRODUCING.md       # Exact reproduction protocol and evidence boundaries
├── examples/
│   ├── README.md            # Example configuration instructions
│   └── practical-coding.yaml# Sample project-level configuration
├── references/              # On-demand engineering modules
│   ├── decision.md          # Architecture & dependency decisions
│   ├── implementation.md    # Risk boundaries, change maps & falsification ladder
│   ├── debugging.md         # Evidence-first root-cause diagnosis
│   ├── delegation.md        # Worker subagent protocol & capsule return
│   ├── exploration.md       # Standard source navigation & impact maps
│   └── codebase-memory.md   # Upstream AST/LSP graph intelligence & coverage
└── .github/
    └── workflows/
        └── validate.yml     # Skill validation workflow
```

---

## 🧪 Luna Benchmarks

`benchmarks/run.ps1` invokes the fixed `gpt-5.6-luna` model in isolated sessions for Ponytail delivery tasks, event routing, multi-round grilling decisions, and Superpowers debugging comparisons. Standard and full profiles default to three runs per cell, while `-BaselineRef HEAD` adds the pre-change Git version to the same paired run. See [`benchmarks/README.md`](benchmarks/README.md) and [`benchmarks/REPRODUCING.md`](benchmarks/REPRODUCING.md) for evidence boundaries, artifacts, graders, and exact commands.

---

## 🤝 Contributing & License

Contributions are welcome! Please review our [Contributing Guidelines](CONTRIBUTING.md) before submitting pull requests.

- **License**: [MIT License](LICENSE) © 2026 Hubujiu
- **Third-Party Attribution**: See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for details on [`DeusData/codebase-memory-mcp`](https://github.com/DeusData/codebase-memory-mcp).
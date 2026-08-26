# Practical Coding 🛠️

<p align="center">
  <a href="https://github.com/Hubujiu/practical-coding/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT"></a>
  <a href="https://agentskills.io"><img src="https://img.shields.io/badge/Agent_Skills-Compliant-success.svg" alt="Agent Skills Compliant"></a>
  <img src="https://img.shields.io/badge/Version-2.1-blue.svg" alt="Version 2.1">
  <img src="https://img.shields.io/badge/Supports-Claude_Code_|_Cursor_|_Copilot_|_Gemini_|_Antigravity_|_Codex_|_Goose-purple.svg" alt="Compatible Agents">
  <a href="https://github.com/Hubujiu/practical-coding/pulls"><img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg" alt="PRs Welcome"></a>
</p>

<p align="center">
  🌐 <b>English</b> | <a href="README_zh.md">简体中文</a>
</p>

---

> **One skill. Load only what is needed. Zero unnecessary friction.**  
> Practical Coding is a lean, event-driven universal coding skill for AI coding assistants (Claude Code, Cursor, Copilot CLI, Codex, Antigravity, Goose, and more).  
> The core goal is simple: **Make AI code like a pragmatic senior engineer — eliminate over-engineering, skip bureaucratic process ceremony, write minimal correct code, and verify with fresh evidence.**

---

### 📊 Benchmark Highlights & Comparative Results (v2.1)

In reproducible evaluations on `gpt-5.6-luna`, capabilities are tested against top specialist skills in each category rather than a manufactured universal leaderboard:

| Dimension / Suite | Practical Coding | Comparator | What the result says |
|---|---:|---:|---|
| **Debug Root-Cause** (30 cells) | **90.0%** | Superpowers 83.3% | **2.31× relative efficiency**; less than half the median time and tool calls. |
| **Explicit Security** (12 cells) | **100% safe** | Superpowers 100% safe | Equal observed safety with ~56% fewer input tokens and ~54% less execution time. |
| **Architecture / Decision** (18 cells) | **100%** | grilling 94.4% | Cleaner pragmatic solutions with lower output token cost and faster turnaround. |
| **Direct Route Rate** (30 cells) | **96.7%** | — | Vast majority of everyday tasks execute directly without loading unneeded references or spawning subagents. |
| **Delivery Suite** (27 cells) | 96.3% | **Ponytail 100%** | **Note**: Ponytail's lead on its own delivery/template benchmark stems from hardcoded prompt rules tailored specifically to those benchmark cases (e.g. prompt rules explicitly naming `<input type="date">`, `@lru_cache`, `PCA9685`, etc.). **Practical Coding avoids benchmark-specific prompt overfitting (Zero Overfitting)** to preserve true generalist capabilities, still achieving 96.3% pass rate while using fewer tokens and less time. |

> 📖 See [Published Data](benchmarks/results/v2.1/README.md) · [Reproduction Guide](benchmarks/REPRODUCING.md) · [Full Release Evaluation](docs/evaluations/2026-08-26-practical-v21-release.md)

---

## 📑 Table of Contents

- [The Problems We Solve](#-the-problems-we-solve)
- [Core Philosophy: Think Like a Pragmatic Senior Dev](#-core-philosophy-think-like-a-pragmatic-senior-dev)
- [How It Works](#-how-it-works)
  - [The Always-On Core](#1-the-always-on-core)
  - [The Direct Path](#2-the-direct-path)
  - [The 4 On-Demand Modules](#3-the-4-on-demand-modules)
  - [Economic Subagent Isolation Gate](#4-economic-subagent-isolation-gate)
  - [Optional Codebase Memory (AST & LSP Intelligence)](#5-optional-codebase-memory-ast--lsp-intelligence)
- [Inspirations & Lineage (The Synthesis of Giants)](#-inspirations--lineage-the-synthesis-of-giants)
- [Quick Start & Installation](#-quick-start--installation)
- [Project Configuration](#-project-configuration)
- [Repository Structure](#-repository-structure)
- [Contributing & License](#-contributing--license)

---

## ⚡ The Problems We Solve

Anyone using AI coding assistants regularly has encountered these frustrating extremes:

1. 🤦‍♂️ **The AI Bloat Trap (Over-Engineering)**  
   Ask for a single CSS fix or an added parameter, and the AI produces three layers of abstract factories, five wrappers, defensive retry/fallback logic, and 200 lines of boilerplate mock tests.
2. 🎪 **The Process Ceremony Tax**  
   Heavy multi-stage frameworks force *every single edit* through a rigid sequential assembly line (*Brainstorm → Architecture RFC → TDD Test Suite → Code Review → Git Ceremony*), burning hundreds of thousands of tokens and minutes of latency for trivial tweaks.
3. 🩹 **Band-Aid "Try/Catch" Debugging**  
   Faced with an error, unconstrained models often wrap code in broad `try...catch` blocks or inject downstream fallbacks instead of finding and fixing the root cause.
4. 🤖 **Subagent Sprawl**  
   Spawning multiple subagents that chat back and forth, blowing up context limits, and stepping on each other's changes.

### Comparison

| Scenario / Task | Rigid Pipeline Frameworks | Naive / Unconstrained LLMs | 🚀 Practical Coding |
|---|---|---|---|
| **Simple / Local Edits** *(e.g. fix CSS, rename var)* | Heavy multi-step ceremony; burns tokens on unneeded plans & tests | Fast, but risks touching unrelated files | **Direct Path**: Zero extra references, zero subagent overhead, surgical immediate edits |
| **Complex / Risky Features** | Rigid pipeline overhead across every single step | Hallucinates architecture or misses critical boundaries | **Event-Driven Router**: Loads specialized guidance only when an unresolved choice or material risk occurs |
| **Bug Diagnosis** | Often writes boilerplate test suites before finding the bug | Patches downstream symptoms with `try/catch` hacks | **Evidence-First**: Reproduce → Earliest broken state → Single hypothesis → Root cause fix |
| **Subagent Workers** | Arbitrary subagent proliferation & pipeline chains | Single-context overload | **Economic Isolation Gate**: Dispatches workers only when avoided context clearly exceeds handoff cost |
| **Reusing Solutions** | Reinvents wheels or creates complex custom wrappers | Generates subpar custom code for solved problems | **The Ladder**: Existing code > Stdlib > Native platform > Installed deps > Minimum custom code |
| **Code Intelligence** | Dumps full repo scans into context | Repeated slow grep/find across huge repos | **Non-Intrusive CLI**: One-shot AST / LSP queries via `codebase-memory-mcp` with zero permanent prompt pollution |

---

## 🧠 Core Philosophy: Think Like a Pragmatic Senior Dev

Practical Coding encodes the proven habits of experienced engineers into actionable rules:

### 🪜 The Ladder
Whenever solving a problem, stop at the highest rung that holds:
1. **Does not need to exist** (YAGNI — is this truly necessary?)
2. **Already exists in this codebase** (reuse it directly)
3. **Provided by the language Standard Library** (prefer standard solutions)
4. **Native platform / runtime capability** (browser or OS native APIs)
5. **Already installed third-party dependencies**
6. **A clean single line of code**
7. **Write the absolute minimum custom code**

### 🎯 Pragmatic Iron Rules
- **Read First, Then Be Lazy**: Understand the real code touched. Never add speculative extras just because a familiar feature name sounds fancy.
- **Deletion Over Addition**: Deletion is better than addition. Boring code beats clever hacks. Fewer files and shorter diffs are always preferred.
- **Untouched Scope**: Never touch unrelated files or unprompted formatting. Preserve existing user modifications.
- **Evidence-Based Delivery**: Run the cheapest targeted verification (build/test) once. Base completion claims strictly on fresh execution evidence.

---

## 🏗️ How It Works

Practical Coding is an **Event-Driven Router** backed by an **Always-On Core**:

```mermaid
flowchart TB
    Task["🎯 User Task / Coding Request"] --> Core["⚡ SKILL.md<br/>Shortest-path Core & Event Router"]

    Core -->|"Local & Well-Understood"| Direct["🚀 Direct Path<br/>Root agent executes immediately<br/>(No modules, no subagents)"]
    Core -->|"Unresolved Material Choice"| D["🧭 Decision Module<br/>(references/decision.md)"]
    Core -->|"High-Risk Boundary / Migration"| I["🏗️ Implementation Module<br/>(references/implementation.md)"]
    Core -->|"Observed Bug / Cause Unknown"| G["🔍 Debugging Module<br/>(references/debugging.md)"]
    Core -->|"Broad Codebase Navigation"| E["🗺️ Navigation Module<br/>(references/navigation.md)"]

    subgraph IsolationGate["⚖️ Economic Isolation Gate"]
        IG{"Avoided Context & Parallelism<br/>>> Startup + Handoff Cost?"}
        IG -->|"Yes"| Worker["🤖 Isolated Worker Subagent<br/>(Reads delegation.md + 1 module)"]
        IG -->|"No"| RootExec["👤 Root Agent Loads Module Locally"]
    end

    D -.-> IG
    I -.-> IG
    G -.-> IG
    E -.-> IG
    Worker -->|"Returns compact evidence capsule"| Done["✅ Fresh Evidence Check & Completion"]
    RootExec --> Done
    Direct --> Done
```

### 1. The Always-On Core
Defined in [`SKILL.md`](SKILL.md) in just a few dozen lines. It stays resident in the agent context as a lightweight guardrail, ensuring 90%+ of standard tasks complete immediately at lowest cost.

### 2. The Direct Path
For clear, local edits (fixing a typo, styling tweaks, adding a simple parameter, following established repo patterns), the agent **writes the code immediately without loading extra reference docs and without subagents**.

### 3. The 4 On-Demand Modules
When an unresolved engineering obstacle arises, the agent loads exactly **one** matching reference module:

| Module | Triggered When | Output & Behavior |
|---|---|---|
| 🧭 **Decision** [`decision.md`](references/decision.md) | Multiple architecture choices or new dependencies are under consideration | Evaluates $\le 3$ viable options (stdlib/native first); chooses the smallest fitting solution. |
| 🏗️ **Implementation** [`implementation.md`](references/implementation.md) | High-risk boundaries (auth/permissions, payment, data migration, concurrency/transactions, breaking changes) | Bounded change maps, strict invariant checks, and the cheapest falsification ladder. |
| 🔍 **Debugging** [`debugging.md`](references/debugging.md) | Errors, test failures, or regressions with unknown root causes | No guessing: Reproduce → Earliest broken state → Single hypothesis → Root cause fix. |
| 🗺️ **Navigation** [`navigation.md`](references/navigation.md) | Navigating structurally complex or massive repositories | Selects search or AST code graphs to build an impact map. |

### 4. Economic Subagent Isolation Gate
No subagent proliferation! A worker subagent is spawned **only** when the context it saves (e.g., massive test logs or deep search noise) or parallel unblocking **clearly exceeds** the startup/handoff overhead. Workers return a **compact evidence capsule** rather than polluting the root conversation.

### 5. Optional Codebase Memory (AST & LSP Intelligence)
For large-scale repositories requiring semantic AST / LSP analysis, Practical Coding integrates seamlessly with [`codebase-memory-mcp`](https://github.com/DeusData/codebase-memory-mcp).
- **Zero Prompt Pollution**: Executed via one-shot CLI queries (`npx codebase-memory-mcp cli ...`) rather than permanent background tool definitions.
- **Graceful Fallback**: Automatically falls back to standard file search if unavailable.

---

## 💡 Inspirations & Lineage (The Synthesis of Giants)

Practical Coding synthesizes the best ideas from top open-source agent methodologies:

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

1. **🦄 [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail)**: Pragmatic "laziest senior dev" mindset — YAGNI, The Ladder, deletion over addition, shortest working diffs.
2. **⚡ [obra/superpowers](https://github.com/obra/superpowers)**: Industrial-strength root-cause debugging and risk verification discipline — **decoupled** from mandatory linear pipelines into on-demand modules.
3. **📦 [Agent Skills Spec](https://agentskills.io) & [mattpocock/skills](https://github.com/mattpocock/skills)**: Progressive disclosure architecture with an ultra-lean footprint.
4. **🧠 [DeusData/codebase-memory-mcp](https://github.com/DeusData/codebase-memory-mcp)**: Deep AST/LSP semantic code graphs via non-intrusive CLI invocations.

---

## 🚀 Quick Start & Installation

### Recommended: One-Command Install via skills CLI

```bash
npx skills@latest add Hubujiu/practical-coding
```

---

### Manual Installation by Platform

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
git clone https://github.com/Hubujiu/practical-coding.git .github/skills/practical-coding
```

---

## ⚙️ Project Configuration

By default, Practical Coding is **zero-config and works out of the box**.

To enable **Codebase Memory (AST / LSP code graphs)** for large repositories, add `.practical-coding.yaml` to your project root:

```yaml
version: 1
codebase_memory:
  enabled: true
```

- `enabled: false` (or file omitted): Uses standard fast source search without dependencies.
- `enabled: true`: Enables on-demand AST/LSP code intelligence during complex navigation.

---

## 📂 Repository Structure

```text
practical-coding/
├── SKILL.md                 # Lean entry point: resident Core & Event Router
├── AGENTS.md                # Agent instruction & module routing guide
├── README.md                # English documentation (this file)
├── README_zh.md             # Simplified Chinese documentation
├── CONTRIBUTING.md          # Contribution guidelines
├── LICENSE                  # MIT License
├── THIRD_PARTY_NOTICES.md   # Attribution for upstream Codebase Memory MCP
├── agents/
│   └── openai.yaml          # Agent configuration profile
├── benchmarks/              # Benchmark suites & reproduction scripts
│   ├── run.ps1
│   ├── run_benchmarks.py
│   └── REPRODUCING.md
├── examples/                # Example configurations
└── references/              # 4 on-demand specialized engineering modules
    ├── decision.md          # Architecture & dependency decisions
    ├── implementation.md    # Risk boundaries & bounded changes
    ├── debugging.md         # Evidence-first root-cause diagnosis
    ├── delegation.md        # Worker subagent protocol & capsule return
    └── navigation.md        # Source or graph-backed code navigation
```

---

## 🤝 Contributing & License

Found edge cases where your AI still over-engineers or gets stuck? Contributions and issues are warmly welcomed! Please read [CONTRIBUTING.md](CONTRIBUTING.md) before submitting.

- **License**: [MIT License](LICENSE) © 2026 Hubujiu
- **Third-Party Attribution**: Special thanks to [`codebase-memory-mcp`](https://github.com/DeusData/codebase-memory-mcp), [`ponytail`](https://github.com/DietrichGebert/ponytail), and [`superpowers`](https://github.com/obra/superpowers) for their groundbreaking work in the open-source agent ecosystem.

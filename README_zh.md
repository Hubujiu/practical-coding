# Practical Coding 🛠️

<p align="center">
  <a href="https://github.com/Hubujiu/practical-coding/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT"></a>
  <a href="https://agentskills.io"><img src="https://img.shields.io/badge/Agent_Skills-Compliant-success.svg" alt="Agent Skills 规范兼容"></a>
  <img src="https://img.shields.io/badge/Version-2.1-blue.svg" alt="Version 2.1">
  <img src="https://img.shields.io/badge/Supports-Claude_Code_|_Cursor_|_Copilot_|_Gemini_|_Antigravity_|_Codex_|_Goose-purple.svg" alt="支持的 Agent 平台">
  <a href="https://github.com/Hubujiu/practical-coding/pulls"><img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg" alt="欢迎 PR"></a>
</p>

<p align="center">
  🌐 <a href="README.md">English</a> | <b>简体中文</b>
</p>

---

> **一个 Skill，按需加载，绝不瞎折腾。**  
> Practical Coding 是一个面向 AI 编程助手（Claude Code / Cursor / Copilot / Codex / Antigravity / Goose 等）的极简、事件驱动型通用编程 Skill。  
> 它的目标很简单：**让 AI 像一个务实的资深程序员一样写代码 —— 拒绝过度设计、拒绝流程内耗、能不写的代码坚决不写、只做最小且正确的修改，并用真实运行结果说话。**

---

### 📊 实测表现对比（v2.1）

在基于 `gpt-5.6-luna` 的真实测试中，我们不搞虚标的“万能大榜”，而是将各项能力与对应领域最顶尖的专项方案进行严格的同台竞技：

| 评测维度与场景 | Practical Coding | 对照组方案 | 实测结论与深度说明 |
|---|---:|---:|---|
| **Debug 根因排查** (30 cells) | **90.0%** | Superpowers 83.3% | **综合效率提升 2.31×**；耗时与工具调用中位数不到 Superpowers 的一半。 |
| **显式安全边界** (12 cells) | **100% 安全** | Superpowers 100% 安全 | 同样做到 100% 零越界，但输入 Token 减少 ~56%，耗时减少 ~54%。 |
| **架构与方案决策** (18 cells) | **100%** | grilling 94.4% | 方案更克制实用，输出 Token 消耗更低、响应更快。 |
| **日常直通路由率** (30 cells) | **96.7%** | — | 绝大多数日常需求直接由主 Agent 一步改完，不加载多余文档，不盲目派发子 Agent。 |
| **Delivery 专项交付** (27 cells) | 96.3% | **Ponytail 100%** | **注**：Ponytail 在该项测试中领先，主因是其 Prompt 针对自身的测试用例存在明显的硬编码提示（如在提示词中显式写入 `<input type="date">`、`@lru_cache`、`PCA9685` 等针对样例编程的规则）。**Practical Coding 拒绝针对测试集做 Prompt 拟合（Zero Overfitting）**，保持真正的通用泛化能力，在此前提下依然取得了 96.3% 的通过率，且在 Token 与耗时成本上更低。 |

> 📖 查看 [完整测试数据](benchmarks/results/v2.1/README.md) · [复现指南](benchmarks/REPRODUCING.md) · [版本评估报告](docs/evaluations/2026-08-26-practical-v21-release.md)

---

## 📑 目录

- [我们解决什么痛点？](#-我们解决什么痛点)
- [核心设计理念：像资深老程序员一样思考](#-核心设计理念像资深老程序员一样思考)
- [它是如何工作的？](#-它是如何工作的)
  - [常驻核心（Always-On Core）](#1-常驻核心always-on-core)
  - [直通路径（Direct Path）](#2-直通路径direct-path)
  - [4 个按需触发的工程模块](#3-4-个按需触发的工程模块)
  - [子 Agent 派发门禁](#4-子-agent-派发门禁)
  - [可选的代码图谱智能（Codebase Memory）](#5-可选的代码图谱智能codebase-memory)
- [站在巨人的肩膀上（灵感与传承）](#-站在巨人的肩膀上灵感与传承)
- [快速开始与安装](#-快速开始与安装)
- [项目配置](#-项目配置)
- [目录结构](#-目录结构)
- [参与贡献与开源协议](#-参与贡献与开源协议)

---

## ⚡ 我们解决什么痛点？

用过 AI 编程助手的开发者，通常都会被下面这两种极端的表现折磨过：

1. 🤦‍♂️ **“过度设计”综合征（AI Bloat Trap）**  
   你只是让它改个按钮颜色或加一个字段，它顺手写了三层抽象工厂、封装了五层 Wrapper、自作主张加了一堆带重试/降级逻辑的防腐层，最后还给你附赠了 200 行 Mock 测试。
2. 🎪 **“流程形式主义”内耗（Process Ceremony Tax）**  
   某些重型 Agent 框架把所有任务都硬塞进固定流水线：不管多小的改动，都必须强行走一遍「头脑风暴 → 写 RFC 架构设计 → 写 TDD 测试 → Review → Git 仪式」。改个错别字都要烧掉几十万 Token 和几分钟时间。
3. 🩹 **“创可贴式”无脑 Debug**  
   报错了不去找根本原因，反手套个 `try ... catch` 把异常吞掉，或者在下游写各种奇怪的默认值兜底，代码越改越乱。
4. 🤖 **“子 Agent 军团”乱飞**  
   动不动就派生出 5 个子 Agent 在那里互相问候聊天，上下文爆炸，还经常把彼此的代码改坏。

### 核心对比

| 场景 / 需求 | 传统重型流水线 Agent | 朴素 / 无约束的裸 Prompt | 🚀 Practical Coding |
|---|---|---|---|
| **改个样式 / 修个小改动** | 强行走完一套设计+测试流程，浪费 Token | 速度快，但经常误碰无关文件 | **直通路径 (Direct Path)**：不加载额外文档，不派子 Agent，直奔主题修改 |
| **复杂/高风险功能** | 步骤僵化繁琐，执行缓慢 | 容易架构幻觉，遗漏关键安全边界 | **事件路由**：仅在遇到未决方案或安全/事务风险时按需加载专精指南 |
| **排查定位 Bug** | 容易先写一堆无关测试再盲猜 | 各种 try/catch 乱盖或者下游打补丁 | **根因定位**：复现 → 找到最早出错点 → 验证假说 → 直击根因修复 |
| **子 Agent 委派** | 随意泛滥，多层嵌套 | 单一上下文容易超载爆炸 | **经济门禁**：仅当节省的 Context 显著大于交接成本时才派发独立 Worker |
| **复用既有方案** | 喜欢造轮子或封装重型库 | 随手手写劣质临时实现 | **梯子法则**：已有代码 > 标准库 > 平台原生 > 已装依赖 > 最少手写 |
| **大工程代码检索** | 把整个项目几万行代码硬塞进上下文 | 反复用 grep/find 盲目翻找 | **非侵入式图谱**：按需调用 Tree-sitter AST / LSP，不污染常驻 Prompt |

---

## 🧠 核心设计理念：像资深老程序员一样思考

Practical Coding 把资深工程师在实际工作中最推崇的习惯提炼成了几条核心铁律：

### 🪜 梯子法则（The Ladder）
遇到任何需求，按以下顺序从上往下找解法，停在第一个能解决问题的阶梯上：
1. **根本不需要存在**（YAGNI，这真的是需求吗？能不能不加？）
2. **当前仓库已有类似实现**（直接复用）
3. **语言标准库自带**（优先使用）
4. **平台原生能力**（如浏览器/操作系统自带 API）
5. **项目中已安装的第三方依赖**
6. **一行简洁代码**
7. **最后才写最小化的自定义实现**

### 🎯 务实铁律
- **先看懂，再动手，然后尽量“偷懒”**：先看懂真正要改的代码，不要自作聪明去联想一堆附加需求。
- **删代码比加代码好**：能删就删，代码越朴实越好，涉及的文件越少越好，改动的 Diff 越短越好。
- **不碰无关代码**：保护用户的现有修改，不搞大范围代码格式化，不在一次修改里掺杂无关私货。
- **用事实与证据说话**：改完后跑一次最轻量的验证（测试用例或构建），绝不盲目吹嘘“我已经完美修复”。

---

## 🏗️ 它是如何工作的？

Practical Coding 不是一套复杂的软件程序，而是一套**结构精巧、渐进式披露的 Agent 规范**：

```mermaid
flowchart TB
    Task["🎯 用户任务 / 编码需求"] --> Core["⚡ SKILL.md<br/>常驻核心与事件路由器"]

    Core -->|"局部改动、需求明确"| Direct["🚀 直通路径 (Direct Path)<br/>主 Agent 立即执行，零额外开销<br/>（不加载模块，不派发子代理）"]
    Core -->|"存在未决的技术/架构选型"| D["🧭 方案决策模块<br/>(references/decision.md)"]
    Core -->|"涉及高危边界、数据迁移、并发风险"| I["🏗️ 有界实现模块<br/>(references/implementation.md)"]
    Core -->|"发现 Bug 但原因不明"| G["🔍 根因调试模块<br/>(references/debugging.md)"]
    Core -->|"需大范围梳理大型代码库"| E["🗺️ 代码导航模块<br/>(references/navigation.md)"]

    subgraph IsolationGate["⚖️ 经济隔离门禁 (Economic Isolation Gate)"]
        IG{"节省的上下文与并行收益<br/>>> 启动与交接成本？"}
        IG -->|"是"| Worker["🤖 派发单任务 Worker<br/>（只读 delegation.md + 对应模块）"]
        IG -->|"否"| RootExec["👤 主 Agent 本地直接加载处理"]
    end

    D -.-> IG
    I -.-> IG
    G -.-> IG
    E -.-> IG
    Worker -->|"返回精简证据胶囊"| Done["✅ 获取新鲜证据 & 交付完成"]
    RootExec --> Done
    Direct --> Done
```

### 1. 常驻核心（Always-On Core）
放在 [`SKILL.md`](SKILL.md) 中，体积非常小（仅几十行）。它常驻在 Agent 上下文中，充当“守门员”和“交通警察”，确保日常 90% 的简单任务能以最低成本极速完成。

### 2. 直通路径（Direct Path）
当需求明确、改动局部时（例如修个 CSS、加个参数、改个接口字段、按既有模式改写），Agent **直接上手写代码，不加载任何外置文档，不派发子 Agent**，直接交活。

### 3. 4 个按需触发的工程模块
只有在真正遇到阻碍时，才单次加载对应的一篇说明文档（用完即止，不混着加载）：

| 模块 | 触发时机 | 产出物与行为 |
|---|---|---|
| 🧭 **方案决策** [`decision.md`](references/decision.md) | 面临多种架构、技术选型或依赖库选择时 | 评估不超过 3 个候选方案（优先考虑原生/现有方案），选出满足需求的最小方案。 |
| 🏗️ **有界实现** [`implementation.md`](references/implementation.md) | 涉及高危风险（鉴权/安全性、支付、数据迁移、并发事务、破坏性变更）时 | 明确风险边界，梳理不变量，制定最低成本验证阶梯。 |
| 🔍 **根因调试** [`debugging.md`](references/debugging.md) | 遇到报错、测试失败或行为异常，且原因不明时 | 坚决不猜：复现 → 找到最早的出错状态 → 验证单一假设 → 根治 Bug。 |
| 🗺️ **代码导航** [`navigation.md`](references/navigation.md) | 需要搞清楚超大代码库的复杂调用关系时 | 选择源码搜索或 AST 图谱，快速理清影响范围。 |

### 4. 子 Agent 派发门禁
严禁无意义的子 Agent 套娃！只有在**为了隔离海量日志/搜索结果，或者独立并行任务确实能省下一大笔上下文**时，才派发 1 个专职 Worker。Worker 完成后只返回**精炼的结论与证据胶囊**，不把整段废话灌回主对话。

### 5. 可选的代码图谱智能（Codebase Memory）
如果你在大型项目中需要精确的 AST 和 LSP 跨文件分析，Practical Coding 支持无缝联动 [`codebase-memory-mcp`](https://github.com/DeusData/codebase-memory-mcp)。
- **无需常驻后台吃内存**：采用按需 CLI 单次调用方式（`npx codebase-memory-mcp cli ...`），不污染主 Prompt。
- **自动降级**：没安装或不支持时，自动切换为普通源码搜索，绝不报错卡死。

---

## 💡 站在巨人的肩膀上（灵感与传承）

Practical Coding 并非凭空捏造，而是提炼和升华了社区中多款优秀项目的智慧结晶：

```text
               ┌─────────────────────────────────────────────────────────┐
               │              DietrichGebert/ponytail                    │
               │        “最懒资深工程师”哲学、YAGNI、标准库优先          │
               └────────────────────────────┬────────────────────────────┘
                                            │（极简务实设计理念）
                                            ▼
┌───────────────────────────┐      ┌─────────────────┐      ┌─────────────────────────────┐
│      obra/superpowers     │      │                 │      │      Agent Skills 规范      │
│  工程严谨性、调试、委派与验证│─────►│ PRACTICAL CODING│◄─────│    (mattpocock / Anthropic) │
│  （剥离僵化流水线，按需触发）│      │                 │      │        渐进式披露机制       │
└───────────────────────────┘      └────────┬────────┘      └─────────────────────────────┘
                                            │（代码图谱智能）
                                            ▼
               ┌─────────────────────────────────────────────────────────┐
               │             DeusData/codebase-memory-mcp                │
               │      Tree-sitter AST、Hybrid LSP、CLI 单次调用图谱智能    │
               └─────────────────────────────────────────────────────────┘
```

1. **🦄 [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail)**：继承了它“最懒资深工程师”的务实作风 —— 极简主义、YAGNI、删代码优先、最短可用 Diff。
2. **⚡ [obra/superpowers](https://github.com/obra/superpowers)**：吸纳了其工业级的根因调试与风险验证纪律，但**打破了其强制性的冗长流水线**，将其改造成只在出问题时才触发的按需插件。
3. **📦 [Agent Skills 规范](https://agentskills.io) & [mattpocock/skills](https://github.com/mattpocock/skills)**：遵循渐进式披露标准，保持极小的入口体积。
4. **🧠 [DeusData/codebase-memory-mcp](https://github.com/DeusData/codebase-memory-mcp)**：提供强大的代码语义图谱能力，并创新地改为非侵入式 CLI 模式调用。

---

## 🚀 快速开始与安装

### 推荐：使用 skills CLI 一键安装

```bash
npx skills@latest add Hubujiu/practical-coding
```

---

### 手动安装（按你的工具选择）

#### 🟣 Claude Code
```bash
git clone https://github.com/Hubujiu/practical-coding.git ~/.claude/skills/practical-coding
```

#### 🔵 Cursor / Codex / Copilot CLI / Gemini CLI / Antigravity / Goose

**macOS / Linux:**
```bash
git clone https://github.com/Hubujiu/practical-coding.git ~/.agents/skills/practical-coding
```

**Windows (PowerShell 7):**
```powershell
git clone https://github.com/Hubujiu/practical-coding.git "$env:USERPROFILE\.agents\skills\practical-coding"
```

#### 📁 仅为单个项目安装
如果你只想在某个特定的代码仓库中启用：
```bash
git clone https://github.com/Hubujiu/practical-coding.git .github/skills/practical-coding
```

---

## ⚙️ 项目配置

默认情况下，Practical Coding **开箱即用，无需任何配置文件**。

如果你想为大型代码库开启 **Codebase Memory（AST / LSP 代码图谱）**，可以在项目根目录新建 `.practical-coding.yaml`：

```yaml
version: 1
codebase_memory:
  enabled: true
```

- `enabled: false`（或不创建此文件）：使用普通源码检索，极简无依赖。
- `enabled: true`：遇到大范围代码梳理时，允许按需调用图谱智能。

---

## 📂 目录结构

```text
practical-coding/
├── SKILL.md                 # 核心入口：常驻 Core 与事件路由器
├── AGENTS.md                # 统一 Agent 引导说明
├── README.md                # 英文文档
├── README_zh.md             # 中文文档（本文件）
├── CONTRIBUTING.md          # 贡献指南
├── LICENSE                  # MIT 开源协议
├── THIRD_PARTY_NOTICES.md   # 第三方开源声明
├── agents/
│   └── openai.yaml          # Agent 配置文件
├── benchmarks/              # 基准测试运行工具与复现脚本
│   ├── run.ps1
│   ├── run_benchmarks.py
│   └── REPRODUCING.md
├── examples/                # 配置示例
└── references/              # 4 个按需加载的专精模块
    ├── decision.md          # 架构与技术选型决策
    ├── implementation.md    # 风险边界与有界实现
    ├── debugging.md         # 证据驱动的根因调试
    ├── delegation.md        # Worker 契约与胶囊回报
    └── navigation.md        # 源码与图谱导航
```

---

## 🤝 参与贡献与开源协议

如果你有更好的点子，或者发现了某些 AI 依然容易“发癫”的边界 case，非常欢迎提交 PR 或 Issue！提交前请查阅 [贡献指南](CONTRIBUTING.md)。

- **开源协议**：[MIT License](LICENSE) © 2026 Hubujiu
- **致谢**：特别感谢 [`codebase-memory-mcp`](https://github.com/DeusData/codebase-memory-mcp)、[`ponytail`](https://github.com/DietrichGebert/ponytail) 与 [`superpowers`](https://github.com/obra/superpowers) 项目为社区带来的卓越启发。

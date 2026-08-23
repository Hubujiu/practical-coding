# Practical Coding

> **一个 Skill，按需加载。**  
> **One skill, load only what the task needs.**

Practical Coding 是一个面向 Coding Agent 的轻量通用编码 Skill。它不把 Brainstorming、Planning、TDD、Debugging、Review 和 Git Workflow 串成固定流水线，而是让主 `SKILL.md` 作为轻量 Router，只在任务真正需要时读取对应模块。

目标很直接：**减少多余代码、测试、文档、防御性编程、重复源码扫描和流程成本，同时保持或提高代码质量。**

[中文](#中文) · [English](#english)

---

## 中文

### 它是什么

Practical Coding 不是“少做工程”，而是：

```text
理解当前任务
→ 判断真正需要哪些工程能力
→ 只加载对应模块
→ 用最小相关上下文完成最小且持久的修改
→ 用最低成本的充分证据确认结果
```

它默认反对没有明确收益的工程工作：

- 为假想未来需求增加抽象、配置、扩展点和兼容层；
- 为简单能力重复造轮子；
- 每改一个功能就机械新增测试；
- 把代码或 Git 能廉价重建的事实重复写成文档；
- 为从未观察到的失败增加大量 retry、fallback、guard、宽泛 catch 和重复校验；
- 仅因为“标准流程如此”就强制写计划、建分支、提交 checkpoint 或多轮 Review；
- 小改动也机械索引整个仓库、查询代码图谱或反复扫描无关源码。

但必要的安全、权限、数据完整性、兼容性、项目门禁和真实外部边界不属于“多余工作”，不能以精简为理由移除。

### 架构：四个工程模块 + 一个可选代码图谱模块

```text
                         SKILL.md
                      lightweight router
                             │
       ┌──────────────┬──────┼──────┬──────────────┐
       ↓              ↓      ↓      ↓              ↓
   Decision    Implementation Debugging Verification Codebase Memory
                                                      optional
```

它们不是五阶段流水线。模块之间**不强制耦合，也没有固定顺序**：一个任务可以只加载一个模块，也可以在执行过程中因为出现新的条件再加载另一个。

| 模块 | 加载条件 | 通常不需要加载的情况 |
|---|---|---|
| `references/decision.md` | 新能力、架构、依赖、API、数据模型、兼容性，或存在多个会实质影响结果的方案 | 改文案、移动按钮、简单 CSS、rename、机械修改 |
| `references/implementation.md` | 需要修改代码或项目文件 | 纯讨论、只读分析 |
| `references/debugging.md` | 已观察到 bug、回归、错误行为或验证失败 | 正常实现；不会主动扩大成 bug hunting |
| `references/verification.md` | 风险或不确定性使“如何验证”本身成为工程问题 | trivial 修改可以直接通过 diff、render、compile 等确认 |
| `references/codebase-memory.md` | 大型/多模块代码库、调用链、影响分析、跨服务导航、架构发现、重复多 Agent 探索 | 小型 Demo、局部改动、已知文件路径、普通搜索更便宜的任务 |

### 典型任务

```text
“把按钮文字改成保存”
→ Implementation
→ 看 diff / 页面

“把这个按钮移动到右侧”
→ Implementation
→ 页面检查

“给 Spring 项目接入新的 OAuth Provider”
→ Decision
→ Implementation
→ Verification

“这个接口线上返回 500”
→ Debugging
→ 找到根因后加载 Implementation
→ 风险较高时再加载 Verification

“这个大型 monorepo 里谁调用了 ProcessOrder，改它会影响什么？”
→ Codebase Memory（如果项目已启用）
→ 必要时回源读取关键代码
```

简单任务不会因为安装了 Practical Coding 就承担复杂任务的流程成本。更多 before/after 对比见 [examples/](examples/README.md)。

### Decision：先复用，再发明

只有出现真实技术决策时才加载 Decision。默认方案优先级：

```text
现有代码
→ 标准库
→ 平台 / 框架原生能力
→ 已安装依赖
→ 调研成熟方案
→ 新依赖
→ 最小自研
```

增加依赖或实现非简单能力前，优先查看官方资料、成熟实现、维护中的项目和可信工程讨论，而不是复制第一个搜索结果，也不是无依据自研。

同时避免：

- speculative abstraction；
- 没有当前需求支撑的 future-proofing；
- 临时架构以后再“重写”的承诺；
- 为了代码看起来更“高级”而增加层级和间接性。

### Implementation：最小 coherent change

Practical Coding 追求的不是最少字符，而是**最小完整修改**：

- 从最小相关上下文开始，只在证据不足时扩大读取范围；
- 优先修改现有代码，不创建平行实现；
- 不顺手重构无关区域；
- 不增加当前需求不需要的配置、wrapper、adapter 或扩展点；
- 保持项目已有 API、数据格式和明确兼容约束，除非当前任务要求改变它们。

#### 减少防御性编程

真实边界和不变量必须正确处理，但不会因为“也许会出问题”就默认加入：

```text
retry
fallback
重复 validation
宽泛 catch
null guard everywhere
兼容层
多层 wrapper
额外 feature flag
```

防御代码需要对应真实风险、真实边界、已有失败或明确契约，而不是想象中的可能性。

### Debugging：证据 → 根因 → 最小修复

Debugging 只在真实故障出现时加载：

```text
复现或收集证据
→ 沿真实执行路径向前/向后追踪
→ 找到最早错误状态
→ 一次验证一个假设
→ 修复根因
→ 确认原始症状消失
→ 移除临时诊断代码
```

不会因为进入 Debug 就自动生成测试，也不会把一个已知问题扩展成全仓库主动找 bug。

### Verification：测试是证据，不是默认产物

核心规则：

> **Risk → cheapest sufficient evidence.**

不同修改需要不同证据：

| 修改 | 可能足够的证据 |
|---|---|
| 文案、CSS、小型 UI 调整 | diff / render / visual inspection |
| 小型类型或配置修改 | compile / type check / targeted command |
| 普通业务逻辑 | targeted behavior check / existing tests |
| 权限、支付、并发、迁移、公共 API、跨服务集成 | 更强的定向验证，必要时增加最小且长期有价值的自动化测试 |

Practical Coding 不默认新增测试，也不机械执行全部测试；但没有与风险匹配的新证据时，也不会宣称任务已经完成。

### Git 和文档

#### Git 是证据源，不是门槛

有 Git 时，`diff`、`log`、`blame` 和历史决策可以帮助理解项目；没有 Git 时仍然可以执行普通编码任务。

除非用户或项目明确要求，否则不强制：

```text
初始化 Git
创建 branch
创建 worktree
固定 checkpoint commit
execution document
PR / review 流程
```

#### 文档记录“原因”，不是重复事实

不要记录可以廉价重建的信息：

```text
某个类在哪里
谁调用某个方法
这次改了哪些文件
当前任务完成了几步
```

这些信息通常可以从代码、AST、结构化代码索引、搜索或 Git 获得。

真正值得持久记录的是代码本身表达不了、以后很可能再次影响决策的信息，例如：

```text
为什么这里不能改成 async
为什么选择 Redis 而不是数据库锁
为什么一个看似多余的 workaround 不能删除
为什么某个兼容约束必须继续保留
```

### Structured Codebase Memory：已经接入，但完全可选

Practical Coding 现在正式加入 `references/codebase-memory.md`，默认 provider 是 [DeusData/codebase-memory-mcp](https://github.com/DeusData/codebase-memory-mcp)。上游项目使用 MIT License。

这里**没有把 Codebase Memory 的整个 C 运行时复制进来**。Practical Coding 只复用它最有价值的结构：持久化代码图谱、结构化查询、调用链/影响分析、增量索引，以及“图谱负责发现、关键结论回源确认”的使用方式。底层解析器、SQLite 存储、daemon、watcher、UI 和语义模型继续由 upstream provider 负责。

```text
小型 Demo / 一次性脚本 / 局部修改
→ 直接搜索代码通常更便宜

大型生产项目 / 多模块 / 微服务 / 多 Agent 协作
→ 结构化代码图谱可能减少重复扫描源码和上下文 Token
```

项目根目录可以保存最小配置：

```yaml
version: 1
codebase_memory:
  enabled: true
  provider: codebase-memory-mcp
```

模板见 [`examples/practical-coding.yaml`](examples/practical-coding.yaml)。

规则：

- 项目级可选，而不是安装 Skill 后全局强制开启；
- 没有配置时，小型/局部任务直接跳过，不打扰用户；
- 当代码库或任务明显会受益于图谱时，才询问用户是否为该项目启用；
- `enabled: true` 只代表“需要时可以用”，不代表每个任务都查询；
- 不会因为启用而自动安装 provider、打开 watcher、提交图谱快照；这些行为仍需用户同意；
- provider 不可用时退回普通源码搜索，不阻塞任务。

Codebase Memory 提供的 `get_architecture`、`search_graph`、`trace_path`、`detect_changes`、`query_graph` 等能力只在对应结构问题出现时调用。精确修改和“没有其他调用者”这类负面/穷尽结论仍应检查索引范围，并直接读取决定性源码。

### 为什么不是 Superpowers 式固定流程

Practical Coding 会参考 Brainstorming、Planning、Debugging、Testing、Review 等成熟工程方法，但不会因为这些能力有价值就让所有任务依次执行全部流程。

区别在于：

```text
固定流程：任务 → A → B → C → D → E

Practical Coding：任务 → Router → 当前真正需要的能力
```

这也是 Agent Skills progressive disclosure 的核心思路：主 Skill 保持短小，条件性知识放入独立 reference，并明确什么时候才读取。

### 安装

#### 一键安装

[skills.sh](https://skills.sh) 的通用安装器可以交互式选择要安装到哪些 agent：

```bash
npx skills@latest add Hubujiu/practical-coding
```

#### 手动安装（git clone）

**Codex / Cursor / Copilot CLI / Gemini CLI** —— 共享的跨工具用户级路径 `~/.agents/skills/`，装一次全部生效：

```bash
# macOS / Linux
git clone https://github.com/Hubujiu/practical-coding.git ~/.agents/skills/practical-coding
```

```powershell
# Windows PowerShell
git clone https://github.com/Hubujiu/practical-coding.git "$env:USERPROFILE\.agents\skills\practical-coding"
```

**Claude Code** —— 用户级路径 `~/.claude/skills/`：

```bash
# macOS / Linux
git clone https://github.com/Hubujiu/practical-coding.git ~/.claude/skills/practical-coding
```

```powershell
# Windows PowerShell
git clone https://github.com/Hubujiu/practical-coding.git "$env:USERPROFILE\.claude\skills\practical-coding"
```

**项目级安装** —— 把本仓库放进项目的 `.agents/skills/practical-coding`，与项目一起提交、团队共享（Cursor 也识别 `.cursor/skills/`，Claude Code 识别 `.claude/skills/`，Codex 识别 `.codex/skills/`）。

其他支持 Agent Skills 的工具可以直接使用仓库中的 `SKILL.md`；自动读取 `AGENTS.md` 的工具（OpenCode、Amp、Jules 等）从仓库根目录的 `AGENTS.md` 获得同样的路由规则。

> Codebase Memory provider 是独立可选依赖，不会随 Practical Coding 自动安装。需要时按 upstream 文档安装并配置 MCP 即可。

### 与其他 Skills 共存

Practical Coding 不替代领域能力。前端设计、Playwright、数据库、平台文档、图像、PDF、部署、安全专项检查等 Skill 可以继续保留。

真正需要避免的是：**同一个编码任务自动套入多套相互重叠的通用流程。**

如果已有 Skill 强制所有任务执行 Brainstorming、完整 Planning、TDD、多轮 Review 或固定 Git 流程，建议关闭其中冲突的自动触发，或保留为显式手动调用。

### 项目结构

```text
practical-coding/
├── SKILL.md
├── AGENTS.md
├── README.md
├── CONTRIBUTING.md
├── LICENSE
├── agents/
│   └── openai.yaml
├── examples/
│   ├── README.md
│   └── practical-coding.yaml
├── references/
│   ├── decision.md
│   ├── implementation.md
│   ├── debugging.md
│   ├── verification.md
│   └── codebase-memory.md
└── .github/
    └── workflows/
        └── validate.yml
```

### 思想来源

- [Ponytail](https://github.com/DietrichGebert/ponytail)：YAGNI、reuse-first、stdlib/native-first 和极小实现。
- [Matt Pocock / skills](https://github.com/mattpocock/skills)：面向 Agent 写作和 progressive disclosure。
- [Superpowers](https://github.com/obra/superpowers)：完整 Coding Workflow 的参考，以及 Practical Coding 有意避免的强制流程耦合。
- [Codebase Memory](https://github.com/DeusData/codebase-memory-mcp)：可持久化结构化代码图谱、调用链/影响分析，以及图谱发现与源码验证的分层使用方式。
- [Agent Skills specification](https://agentskills.io/specification)：Skill 结构与 progressive disclosure。

---

## English

Practical Coding is a compact general-purpose coding skill for coding agents. Instead of forcing every task through Brainstorming, Planning, TDD, Debugging, Review, and Git workflow stages, `SKILL.md` acts as a lightweight router and reads only the modules whose triggers match the task.

Its goal is simple: **less unnecessary code, testing, documentation, defensive programming, repeated source scanning, and process while preserving or improving software quality.**

### Architecture

```text
                         SKILL.md
                      lightweight router
                             │
       ┌──────────────┬──────┼──────┬──────────────┐
       ↓              ↓      ↓      ↓              ↓
   Decision    Implementation Debugging Verification Codebase Memory
                                                      optional
```

These are independent capabilities, not mandatory stages.

| Module | Load when |
|---|---|
| `references/decision.md` | A material architecture, dependency, API, data, compatibility, or solution choice exists. |
| `references/implementation.md` | Code or project files need to change. |
| `references/debugging.md` | An observed failure, regression, incorrect behavior, or failed verification needs diagnosis. |
| `references/verification.md` | Risk or uncertainty makes verification strategy non-trivial. |
| `references/codebase-memory.md` | Large/complex repository navigation, call chains, impact analysis, cross-service tracing, architecture discovery, or repeated multi-agent exploration would benefit from a structural graph. |

A text or button-position change may need only Implementation plus a direct visual check. A new authentication provider may need Decision, Implementation, and Verification. A production failure may start with Debugging and load other modules only when their triggers appear. See [examples/](examples/README.md) for before/after comparisons.

### Principles

- **Reuse before invention:** existing code → standard library → native platform/framework → installed dependency → research proven solutions → new dependency → minimal custom implementation.
- **Smallest coherent change:** avoid speculative abstractions, unrelated cleanup, unnecessary configuration, wrappers, and future-proofing.
- **No defensive bloat:** handle real boundaries, contracts, and observed risks rather than imagined failure modes.
- **Evidence-driven debugging:** evidence → earliest incorrect state → one hypothesis at a time → root cause → minimal fix.
- **Risk-proportional verification:** tests are evidence, not a default deliverable; use the cheapest sufficient fresh evidence.
- **Document decisions, not reconstructable facts:** avoid duplicating information already recoverable from code, structured indexes, search, ASTs, or Git.
- **Git is evidence, not ceremony:** repositories, branches, commits, plans, and checkpoints are not universal prerequisites.
- **Progressive disclosure:** keep default context small and load specialized guidance only when its trigger appears.

### Optional structured codebase memory

Structured Codebase Memory is now an actual optional module rather than a future placeholder. The default provider is [DeusData/codebase-memory-mcp](https://github.com/DeusData/codebase-memory-mcp), which is MIT-licensed.

Practical Coding does not vendor the provider's C runtime. It reuses the useful contract: persistent structural indexing, architecture/symbol queries, call-chain and impact analysis, incremental refresh, and a discovery-first / source-verification discipline. Parsing, SQLite storage, the daemon, watcher, UI, and semantic model remain upstream responsibilities.

A project may persist the smallest possible choice in `.practical-coding.yaml`:

```yaml
version: 1
codebase_memory:
  enabled: true
  provider: codebase-memory-mcp
```

See [`examples/practical-coding.yaml`](examples/practical-coding.yaml).

Small demos, one-off scripts, known local edits, and tasks where targeted search is cheaper skip the graph. Large production codebases, multi-module systems, microservices, and multi-agent workflows may opt in when structural navigation saves repeated exploration.

`enabled: true` means “available when useful,” not “query it on every task.” Practical Coding does not auto-install the provider, enable watchers, or commit shared graph snapshots. If the provider is unavailable, normal source search remains the fallback.

### Installation

#### One-command install

The universal [skills.sh](https://skills.sh) installer lets you pick the agents to install into:

```bash
npx skills@latest add Hubujiu/practical-coding
```

#### Manual install (git clone)

**Codex / Cursor / Copilot CLI / Gemini CLI** — one clone into the shared cross-tool user path `~/.agents/skills/` covers all of them:

```bash
# macOS / Linux
git clone https://github.com/Hubujiu/practical-coding.git ~/.agents/skills/practical-coding
```

```powershell
# Windows PowerShell
git clone https://github.com/Hubujiu/practical-coding.git "$env:USERPROFILE\.agents\skills\practical-coding"
```

**Claude Code** — user-level path `~/.claude/skills/`:

```bash
# macOS / Linux
git clone https://github.com/Hubujiu/practical-coding.git ~/.claude/skills/practical-coding
```

```powershell
# Windows PowerShell
git clone https://github.com/Hubujiu/practical-coding.git "$env:USERPROFILE\.claude\skills\practical-coding"
```

**Project-level** — commit the repo into your project's `.agents/skills/practical-coding` to share it with the team (Cursor also reads `.cursor/skills/`, Claude Code reads `.claude/skills/`, Codex reads `.codex/skills/`).

Other Agent Skills-compatible tools can use `SKILL.md` directly; tools that auto-load `AGENTS.md` (OpenCode, Amp, Jules, and others) pick up the same routing rules from the repository root `AGENTS.md`.

The Codebase Memory provider is a separate optional dependency and is never installed automatically by this skill.

### Sources

Practical Coding draws on Ponytail's implementation restraint, Matt Pocock's agent-writing and progressive-disclosure guidance, the engineering coverage of Superpowers without its mandatory workflow coupling, Codebase Memory's persistent structural graph and graph-to-source verification model, and the Agent Skills specification.

### License

See [LICENSE](LICENSE). Codebase Memory remains a separate MIT-licensed upstream provider; no upstream runtime source is vendored here.

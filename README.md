# Practical Coding

> **你只需要这一个 Coding Skill。**
> **The only general-purpose coding skill you need.**

**约 20–50% 更少 Token · 约 30–100% 更高交付效率 · 测试膨胀场景最高约 7× 更快**

**Target 20–50% fewer tokens · 30–100% faster delivery · up to 7× faster when backend test churn dominates**

[中文](#中文) · [English](#english)

## 中文

Practical Coding 是一个默认应用于编码任务的 Agent Skill。它把 Ponytail 的实现克制、Marcos Hernanz 的工程边界、grill-me 的必要澄清，以及“先寻找成熟实现、去掉多余后端测试”的实践合并成一个可恢复、可交接的编码决策流程。

它不是另一个需要与 Brainstorming、TDD、Writing Plans、Executing Plans 和多轮 Review 叠加使用的流程。它替代这些彼此重叠或冲突的通用 Coding Skills，只保留代码库检索、浏览器、设计、文档和其他领域工具。

### 一句话安装

把下面整句话复制给你的 Coding Agent：

```text
请帮我安装并启用这个 Skill：https://github.com/Hubujiu/practical-coding；先识别当前 Agent 和它的用户级 Skills 目录，阅读仓库 README，检测所有已安装的冲突 Coding Skills，把冲突项安全、可恢复地禁用而不是删除，保留不冲突的领域 Skills，然后安装 Practical Coding、验证它能被发现，并告诉我安装位置和具体禁用了哪些 Skill。
```

这条指令适用于 Codex、Cursor、Claude Code，以及其他支持 Agent Skills 的编码工具。Agent 应优先使用平台提供的 Skill 管理界面或命令；需要移动本地目录时，应先确认精确路径，并移动到平台不会扫描的备份目录。

### 它解决什么问题

Coding Agent 经常把写代码变成制造代码：为简单需求增加抽象和依赖，为每个后端功能生成测试类，功能修改后继续维护已经失效的测试，甚至围绕测试基础设施产生更多测试与修改。

这个 Skill 针对一种真实但低效的体验：功能实现只需约 10 分钟，自动生成和反复修正测试却可能耗费约 1 小时。这里的时间比例描述的是本项目要解决的使用体验，不是通用性能统计。

### 能节省多少

Practical Coding 的宣传目标是：

- 减少约 **20–50%** 的总 Token 消耗。
- 提升约 **30–100%** 的端到端交付效率。
- 在“实现 10 分钟、测试生成与维护 60 分钟”的后端任务中，把约 70 分钟的流程压缩到约 10 分钟，最高约 **7×** 更快，并减少约 **86%** 的非必要工作时间。
- 减少因上下文耗尽、重复规划、过度抽象、重复调研和 Agent 交接失败造成的返工。

这些区间是产品定位和经验性估算，不是 Practical Coding 自己的正式 Benchmark；任务已经足够精简时，收益可能接近零。作为可比较的公开参考，[Ponytail 的 Agentic Benchmark](https://github.com/DietrichGebert/ponytail/blob/main/benchmarks/results/2026-06-18-agentic.md)报告平均减少 **54% LOC、22% Token、20% 成本和 27% 时间**。Practical Coding 继承其实现克制，同时进一步移除后端测试膨胀、重复规划和多轮强制审查，因此以更宽的效率目标进行宣传。

Practical Coding 要求 Agent：

- 只澄清会改变产品、范围、风险或实现的实质性问题。
- 能从代码、文档和现有上下文查明的事情不询问用户。
- 按“现有代码 → 标准库 → 平台原生能力 → 已有依赖 → 调研成熟实现 → 新依赖 → 最小自研”选择方案。
- 在增加依赖或实现非简单能力前，比较官方资料、成熟项目、现有产品和工程讨论。
- 后端默认相信实现逻辑，不新增测试类，也不在完成后主动寻找 bug。
- 只有用户明确报告后端 bug 时，才通过定向日志和日志分析定位问题。
- 前端需要代表性数据检查布局时，可以加入 Mock.js。
- 在 Git 环境中工作，并在每个完整阶段创建本地 commit。
- 为大型、长期或可能交接的任务维护执行文档，避免上下文耗尽、项目过大或更换 Agent 后凭记忆继续。

### 核心工作流

```text
必要澄清
→ 检查代码和真实流程
→ 复用与调研决策
→ 选择最小方案
→ 检查 Git 环境
→ 必要时创建或恢复执行文档
→ 把执行方案和当前状态发给用户
→ 用户确认？
  → 否：返回必要澄清并重新提交方案
  → 是：提交批准后的执行文档
→ 分阶段执行
→ 实时更新进度、决定、文件、阻塞和下一步
→ Git checkpoint
→ 完成或安全交接
```

执行文档保存在目标仓库的 `.practical-coding/execution/<task-slug>.md`。恢复任务时，Agent 必须先读取仓库指令、执行文档、`git status`、近期提交和当前 diff，再把恢复后的方案发给用户确认。用户没有确认前不能修改产品代码。

简单单步任务不创建执行文档，但仍然需要 Git 环境和本地提交。如果当前目录不是 Git 仓库，Agent 必须提示用户创建或选择 Git 环境，不能擅自初始化仓库。

### 为什么去掉后端测试编写

本项目有意移除 Agent 默认的后端测试编写行为。目标不是声称测试没有价值，而是阻止测试成为与业务代码平行增长的第二套实现：每增加一个功能就增加一个测试类，每修改一个功能又要同步修改测试，最终维护测试的时间超过实现本身。

这是一个明确且有取舍的工作方式。受法规、团队流程或 CI 门禁约束而必须新增测试的项目不适合直接使用这条默认规则。

### 冲突的通用 Coding Skills

安装 Practical Coding 前，禁用或卸载下列 Skill；否则同一个任务可能同时进入多套互相矛盾的工作流。

| 冲突 Skill | Practical Coding 已替代的内容 |
|---|---|
| `brainstorming` | 必要澄清、用户确认和方案循环。 |
| `writing-plans` | 最小执行文档和阶段拆分。 |
| `executing-plans` | 按阶段执行、持续进度和阻塞恢复。 |
| `test-driven-development` | 与“后端不写测试”直接冲突。 |
| `verification-before-completion` | 与“后端不主动测试或寻找 bug”直接冲突。 |
| `systematic-debugging` | 用户报告 bug 后的日志定位流程。 |
| `requesting-code-review` | 不再自动增加强制审查阶段。 |
| `subagent-driven-development` | 不再为每个任务增加 Agent 和两轮审查。 |
| `finishing-a-development-branch` | 不再引入测试门禁和额外收尾流程。 |
| `writing-skills` | Skill 创建继续使用平台的 `skill-creator`，不强制压力测试。 |

以下能力不冲突，可以继续保留：代码库检索、Codebase Memory、并行 Agent、Git worktree、接收外部 Code Review、显式只读 Review、Playwright、前端设计、ImageGen、PDF、OpenAI Docs、Skill Creator、Plugin Creator 及其他领域 Skill。

### Codex

Codex 版本和已安装插件不同，[OpenAI 官方 Codex 文档](https://developers.openai.com/codex/use-cases)没有承诺一份长期固定的预装 Skill 名单。Codex 自带或由 OpenAI 提供的 ImageGen、OpenAI Docs、Skill Creator、Plugin Creator、Skill Installer 等领域 Skill 与 Practical Coding 不冲突，无需删除。

真正需要处理的通常是用户另外安装的通用编码工作流，例如 Superpowers 或同名个人 Skill。打开 **Customize → Skills**，如果发现上表中的冲突 Skill，请禁用它们。

安装到 Codex 用户 Skill 目录：

```powershell
git clone https://github.com/Hubujiu/practical-coding.git "$env:USERPROFILE\.codex\skills\practical-coding"
```

重新启动 Codex 或新建任务。Skill 会自动应用于编码任务，也可以显式调用：

```text
$practical-coding
```

### Cursor

[Cursor 官方 Agent Skills 文档](https://cursor.com/docs/skills)说明 Cursor 会自动发现 `.agents/skills/`、`.cursor/skills/`、`.claude/skills/` 和 `.codex/skills/` 中的 Skill。如果已经在同一台机器为 Codex 安装了 Practical Coding，Cursor 通常可以直接发现它；Cursor-only 安装建议使用通用目录：

```powershell
git clone https://github.com/Hubujiu/practical-coding.git "$env:USERPROFILE\.agents\skills\practical-coding"
```

Cursor 当前内置 `/automate`、`/babysit`、`/canvas`、`/create-hook`、`/create-rule`、`/create-skill`、`/create-subagent`、`/cursor-blame`、`/loop`、`/migrate-to-skills`、`/review`、`/review-bugbot`、`/review-security`、`/sdk`、`/shell`、`/split-to-prs`、`/statusline`、`/update-cli-config` 和 `/update-cursor-settings` 等 Skill。

这些 Cursor 内置项由 Cursor 管理，不需要全部卸载。为避免与 Practical Coding 的“不主动测试和审查”冲突，请在 **Customize → Skills** 中把 `/babysit`、`/review`、`/review-bugbot` 和 `/review-security` 保持为手动调用，不要加入自动编码流程。同时删除或禁用项目规则、用户规则及外部 Skill 中任何强制 Brainstorming、TDD、Writing Plans、测试、主动 Review 或完成验证的规则。

在 Cursor 中可以直接输入：

```text
/practical-coding
```

### Claude Code

[Claude Code 官方 Skills 文档](https://code.claude.com/docs/en/skills)说明 Claude Code 当前在每个会话提供 `/simplify`、`/batch`、`/debug`、`/loop` 和 `/claude-api` 等 bundled skills。它们是平台能力，不需要全部卸载；Practical Coding 已包含简化和日志调试逻辑，因此不要把 `/simplify` 或 `/debug` 再加入同一自动编码流程。

如果安装了 Superpowers 或其他提供上表冲突 Skill 的 Claude Code 插件，请先卸载该插件，或者禁用其中的冲突 Skill，再安装 Practical Coding。

安装到 Claude Code 用户 Skill 目录：

```powershell
git clone https://github.com/Hubujiu/practical-coding.git "$env:USERPROFILE\.claude\skills\practical-coding"
```

重新启动 Claude Code 后，它可以根据描述自动加载，也可以显式调用：

```text
/practical-coding
```

### 其他 Agent 和精简提示词

支持 Agent Skills 标准的工具可以直接使用仓库中的 `SKILL.md`。更换到 Hermes 或其他 Agent 接手时，应让它先读取执行文档和 Git 状态。

不支持 Skill 的 Agent 可以使用：

```text
务实编码：先澄清、复用和调研，再提交最小方案给我确认；后端不写测试，只有我报告 bug 后才用日志调试；大型任务实时维护执行文档并分阶段 Git 提交。
```

### 思想来源

- [Ponytail](https://github.com/DietrichGebert/ponytail)：参考其“先判断是否需要存在，再依次复用现有代码、标准库、平台能力和已有依赖，最后才写最小实现”的决策梯子。
- [Marcos Hernanz 的 AGENTS.md](https://x.com/marcoshernanz/status/2083954734487212511?s=46)：参考其简单实现、分层成长、模块化、依赖复用、成熟产品调研和长期架构边界。
- [grill-me](https://github.com/RobMitt/grill-me-skill)：参考其共同理解、一次处理一个关键问题，以及能从代码中调查就不询问用户的思想；没有采用穷尽式访谈，也没有复制其未声明许可证的文本。

Practical Coding 是独立融合与扩展。它额外强化了实现前调研、后端无测试、日志调试、用户审批、执行文档、可恢复交接和 Git checkpoint。

### 项目结构

```text
practical-coding/
├─ SKILL.md
├─ agents/
│  └─ openai.yaml
├─ references/
│  └─ execution-document.md
├─ CONTRIBUTING.md
├─ LICENSE
└─ README.md
```

## English

Practical Coding is the only general-purpose coding skill you need. It combines Ponytail's implementation restraint, Marcos Hernanz's engineering boundaries, grill-me's focused clarification, research-before-reinvention, no default backend tests, user-approved execution documents, resumable handoffs, and coherent Git checkpoints.

It addresses speculative abstractions, unnecessary dependencies, test classes that become a parallel implementation, stale tests after behavior changes, oversized plans, lost progress after context exhaustion, and hallucinated status during handoff.

### Expected impact

Practical Coding is positioned to deliver:

- Roughly **20–50% fewer total tokens**.
- Roughly **30–100% faster end-to-end delivery**.
- Up to **7× faster completion** and about **86% less unnecessary work** in the motivating backend case where implementation takes ten minutes and generated test maintenance takes sixty.
- Less rework from context exhaustion, repeated planning, speculative architecture, duplicate research, and failed agent handoffs.

These ranges are marketing targets and experience-based estimates, not a formal Practical Coding benchmark; already-minimal tasks may see little or no improvement. As a public reference point, [Ponytail's agentic benchmark](https://github.com/DietrichGebert/ponytail/blob/main/benchmarks/results/2026-06-18-agentic.md) reports **54% less LOC, 22% fewer tokens, 20% lower cost, and 27% less time** on average. Practical Coding adopts that implementation restraint and additionally removes backend test churn, repeated planning, and mandatory review loops.

### One-line installation

Copy this entire instruction to your coding agent:

```text
Install and enable this Skill for me: https://github.com/Hubujiu/practical-coding; first identify the current agent and its user-level Skills directory, read the repository README, detect every installed conflicting coding workflow skill, disable conflicts safely and reversibly instead of deleting them, preserve non-conflicting domain skills, install Practical Coding, verify that the agent discovers it, and report the install path and every skill you disabled.
```

This instruction works with Codex, Cursor, Claude Code, and other tools that support Agent Skills. The agent should prefer the platform's Skill-management UI or commands and verify exact paths before moving local directories into a backup location the platform does not scan.

### Workflow

```text
Clarify only material uncertainty
→ Inspect the code and real flow
→ Reuse and research before implementing
→ Choose the smallest solution
→ Require a Git environment
→ Create or restore an execution document when needed
→ Present it to the user
→ Confirmed?
  → No: return to clarification and revise
  → Yes: commit the approved document
→ Execute one bounded phase
→ Update live progress and commit the checkpoint
→ Complete or hand off safely
```

The execution document lives at `.practical-coding/execution/<task-slug>.md`. Product code cannot be changed until the user approves a newly created or restored execution document. Material scope, architecture, dependency, permission, or risk changes return to the approval loop.

### Conflicts

Disable or uninstall these overlapping workflow skills before using Practical Coding:

`brainstorming`, `writing-plans`, `executing-plans`, `test-driven-development`, `verification-before-completion`, `systematic-debugging`, `requesting-code-review`, `subagent-driven-development`, `finishing-a-development-branch`, and `writing-skills`.

Repository navigation, Codebase Memory, parallel agents, Git worktrees, receiving external review, explicit read-only review, Playwright, frontend design, image, PDF, documentation, plugin, and skill-management capabilities can remain installed.

### Platform notes

- **Codex:** install under `~/.codex/skills/practical-coding`; disable conflicting user-installed workflow skills in Customize; invoke with `$practical-coding`.
- **Cursor:** install under `~/.agents/skills/practical-coding` or another discovered Skill directory; keep built-in review skills manual; invoke with `/practical-coding`.
- **Claude Code:** install under `~/.claude/skills/practical-coding`; remove overlapping workflow plugins such as Superpowers or disable their conflicting skills; invoke with `/practical-coding`.

### Backend testing stance

Practical Coding intentionally removes backend test authoring and proactive backend testing from the agent's default workflow. It trusts the implementation unless the user reports a bug, then diagnoses that bug through focused logging and log analysis. Projects with mandatory regulatory, team-policy, or CI test requirements should not adopt this rule unchanged.

### Prompt-only use

```text
Use practical coding: clarify, reuse, and research first, then present the smallest plan for my approval; write no backend tests, debug only user-reported bugs through logs, and maintain a live execution document with phased Git commits for large work.
```

### Influences

- [Ponytail](https://github.com/DietrichGebert/ponytail)
- [Marcos Hernanz's AGENTS.md](https://x.com/marcoshernanz/status/2083954734487212511?s=46)
- [grill-me](https://github.com/RobMitt/grill-me-skill)

Practical Coding is an independent synthesis and extension. No text was copied from grill-me, whose repository did not declare a license when this project reviewed it.

## License

[MIT](LICENSE)

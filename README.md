# Practical Coding

> **一个 Skill，按需加载。**  
> **One skill, load only what the task needs.**

Practical Coding 是一个面向 Coding Agent 的轻量工程方法。目标不是让 Agent 少思考，而是让它减少无收益的工程工作：**更少代码、更少测试、更少文档、更少防御性编程、更少流程，同时用与风险匹配的证据提高交付质量。**

它不把 Brainstorming、Planning、TDD、Debugging、Review、Git Workflow 强制串成固定流水线。主 `SKILL.md` 只负责最小规则和路由，真正的规则按任务需要从 `references/` 加载。

[中文](#中文) · [English](#english)

## 中文

### 核心思想

```text
理解当前需求
→ 只加载当前任务需要的模块
→ 用最小上下文完成最小且持久的修改
→ 用最低成本的充分证据验证结果
```

Practical Coding 默认反对以下无明确收益的工作：

- 为假想未来需求增加抽象、配置和扩展点；
- 为简单能力重复造轮子；
- 为每次修改机械新增测试；
- 把能从代码或 Git 重建的事实重复写成文档；
- 为未观察到的失败增加大量 fallback、retry、guard 和重复校验；
- 因为“标准流程如此”就强制写计划、开分支、提交 checkpoint 或多轮 Review。

必要的安全、权限、数据完整性、兼容性和项目门禁不属于“多余工作”，不能以精简为理由移除。

### 按需模块

| 模块 | 什么时候加载 | 什么时候不加载 |
|---|---|---|
| `decision.md` | 新能力、架构、依赖、API、数据模型、兼容性或存在多个实质方案 | 改文案、移动按钮、简单 CSS、rename、机械修改 |
| `implementation.md` | 需要修改代码或项目文件 | 纯讨论或只读架构分析 |
| `debugging.md` | 已观察到 bug、回归、错误行为或验证失败 | 正常实现，不主动找 bug |
| `verification.md` | 风险或不确定性使“怎么验证”本身成为一个问题 | trivial 修改直接 diff/render/compile 即可 |

这些模块**不是四个阶段**，也没有固定顺序。任务可以只加载一个，也可以在执行过程中发现新的触发条件后再加载另一个。

例如：

```text
“把按钮文字改成保存”
→ implementation
→ 看 diff / 页面

“把登录系统接入新的 OAuth Provider”
→ decision + implementation + verification

“这个接口线上返回 500”
→ debugging + implementation
→ 只有风险需要时才加载 verification
```

### 决策：先复用，再发明

需要技术决策时采用以下优先级：

```text
现有代码
→ 标准库
→ 平台 / 框架原生能力
→ 已安装依赖
→ 调研成熟方案
→ 新依赖
→ 最小自研
```

增加依赖或实现非简单能力前先查官方资料、成熟库、维护中的实现和可信工程讨论；简单本地修改不为了流程去做无意义调研。

### 实现：减少代码，也减少防御性代码

Practical Coding 追求最小 coherent diff，而不是最少字符。真实外部边界、安全规则、权限、数据完整性和已观察到的失败必须正确处理；但不会因为“也许未来会失败”就默认增加 retry、fallback、重复校验、兼容层、宽泛 catch、null guard 或多层包装。

### Debug：证据 → 根因 → 最小修复

只有出现实际故障才加载 Debugging：先复现或收集证据，沿真实执行路径找到最早错误状态，一次验证一个假设，修复根因并确认原症状消失。Debug 不自动触发新增测试，也不会扩大成全仓库 bug hunting。

### Verification：测试是证据，不是默认产物

低风险修改通常只需要 diff、页面渲染、编译、类型检查或已有定向测试。支付、权限、并发、数据迁移、公共 API、跨服务集成等高风险修改才需要更强证据，并可能值得增加最小且有长期价值的自动化测试。

核心规则是：

> **Risk → cheapest sufficient evidence.**

不因为“完成前必须测试”就机械运行完整测试套件，也不因为“不默认写测试”就跳过必要验证。

### Git 和文档

Git 是证据源，不是前置条件。存在 Git 时可以用 diff、log、blame 理解修改与历史；没有 Git 仍然可以完成普通编码任务。除非用户或项目要求，否则 Practical Coding 不强制创建仓库、分支、commit、execution document 或 checkpoint。

文档同理：只记录代码本身无法廉价重建、未来又很可能被重新讨论的重要技术决策。文件位置、调用关系、改了哪些文件、任务进度等事实不重复写文档。

### Structured Codebase Memory

结构化代码图谱是计划中的**可选扩展**，本版本不包含 Codebase Memory，也不会自动安装或初始化代码图谱。

后续接入时仍遵循同一个原则：小型 Demo 默认不承担索引和上下文成本；大型生产项目、多模块项目或频繁做影响分析的代码库可以开启，以结构化查询减少反复扫描源码的 Token 成本。Codebase Memory 会作为可选能力接入，而不是让所有任务强制依赖它。

### 为什么不采用 Superpowers 式固定流程

Superpowers 的优势是流程完整和强约束，但它会把 brainstorming、planning、TDD、review 等流程技能按规则串联。Practical Coding 选择另一条路线：保留这些工程问题背后的必要原则，但把它们拆成条件模块，只在当前任务真正需要时加载。

这种结构也符合 Agent Skills 的 progressive disclosure：主 Skill 保持短小，条件性规则放入独立 reference，并由明确触发条件决定是否读取。

### 安装

Codex：

```powershell
git clone https://github.com/Hubujiu/practical-coding.git "$env:USERPROFILE\.codex\skills\practical-coding"
```

Cursor：

```powershell
git clone https://github.com/Hubujiu/practical-coding.git "$env:USERPROFILE\.agents\skills\practical-coding"
```

Claude Code：

```powershell
git clone https://github.com/Hubujiu/practical-coding.git "$env:USERPROFILE\.claude\skills\practical-coding"
```

支持 Agent Skills 标准的其他工具可以直接使用仓库中的 `SKILL.md`。

### 与其他 Skills 共存

不需要为了安装 Practical Coding 删除领域 Skill，例如前端设计、Playwright、PDF、文档、图像、数据库或平台专用 Skill。

需要避免的是**同一个任务同时自动运行多套通用编码流程**。如果已有 Skill 强制所有任务执行 brainstorming、完整计划、TDD、多轮 review 或固定 Git 流程，应将其中冲突的自动流程关闭或改为手动调用。

### 思想来源

- [Ponytail](https://github.com/DietrichGebert/ponytail)：YAGNI、reuse-first、stdlib/native-first 和极小实现。
- [Matt Pocock / skills](https://github.com/mattpocock/skills)：面向 Agent 写作与 progressive disclosure 的结构原则。
- [Superpowers](https://github.com/obra/superpowers)：完整工程工作流的参考，以及 Practical Coding 有意避免的强制流程耦合。
- [Agent Skills specification](https://agentskills.io/specification)：Skill 目录结构与 progressive disclosure。

---

## English

Practical Coding is one compact coding skill with independently loadable modules. It aims for **less code, fewer low-value tests, less redundant documentation, less defensive bloat, and less process while preserving enough evidence to justify confidence.**

### Architecture

`SKILL.md` is a lightweight router. It loads only the reference modules whose triggers match the current task:

| Module | Load when |
|---|---|
| `decision.md` | A material architecture, dependency, API, data, compatibility, or implementation choice exists. |
| `implementation.md` | Code or project files need to change. |
| `debugging.md` | An observed failure, regression, incorrect behavior, or failed verification needs diagnosis. |
| `verification.md` | Risk or uncertainty makes verification strategy non-trivial. |

The modules are not mandatory stages and do not form a fixed chain. A copy change may need only Implementation and a direct visual check. A new authentication provider may need Decision, Implementation, and Verification. A production failure may start with Debugging and load other modules only when their triggers appear.

### Principles

- **Reuse before invention:** existing code → stdlib → native platform → installed dependency → research proven solutions → new dependency → minimal custom implementation.
- **Smallest coherent change:** avoid speculative abstractions, configuration, wrappers, unrelated cleanup, and future-proofing without a present need.
- **No defensive bloat:** handle real boundaries and invariants, not imagined failures; never remove necessary security or integrity checks.
- **Evidence-driven debugging:** observed evidence → earliest incorrect state → one hypothesis at a time → root cause → minimal fix.
- **Risk-proportional verification:** tests are evidence, not a default deliverable; use the cheapest sufficient fresh evidence.
- **Document decisions, not reconstructable facts:** do not duplicate information already recoverable from code or Git.
- **Git is evidence, not ceremony:** repositories, branches, commits, plans, and checkpoints are not universal prerequisites.

### Optional structured codebase memory

Codebase Memory is intentionally not bundled in this version. A future integration will remain optional and should only be enabled when the savings from structured navigation and impact analysis justify indexing and context cost, especially for large production codebases.

### Sources

Practical Coding draws on Ponytail's implementation restraint, Matt Pocock's agent-writing and progressive-disclosure guidance, the engineering coverage of Superpowers without its mandatory workflow coupling, and the Agent Skills specification.

### License

See [LICENSE](LICENSE).

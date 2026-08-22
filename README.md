# Practical Coding

[中文](#中文) · [English](#english)

## 中文

Practical Coding 是一个默认应用于编码任务的 Agent Skill，它把 Ponytail 的实现克制、Marcos Hernanz 的工程边界，以及“先寻找成熟实现、减少无收益测试维护”的实践合并成一个决策流程。

### 它解决什么问题

Coding Agent 经常把写代码变成制造代码：为简单需求增加抽象和依赖，为每个后端功能生成测试类，功能修改后继续维护已失效的测试，甚至围绕测试基础设施产生更多测试与修改。

这个 Skill 针对一种常见但低效的工作模式：功能实现只需约 10 分钟，自动生成和反复修正测试却可能耗费约 1 小时。这里的时间比例描述的是本项目要解决的实际体验，不是通用性能统计。

它要求 Agent：

- 先确认真实需求和代码边界，再决定是否需要新增代码。
- 按“现有代码 → 标准库 → 平台原生能力 → 已有依赖 → 调研成熟实现 → 新依赖 → 最小自研”选择方案。
- 在增加依赖或实现非简单能力前，先阅读官方资料并比较成熟项目、现有产品和工程讨论。
- 避免预测式抽象、无必要配置、重复造轮子和临时架构。
- 后端默认相信实现逻辑，不新增测试类，也不在完成后主动寻找 bug。
- 只有用户明确报告后端 bug 时，才通过定向日志和日志分析定位问题。
- 前端需要代表性数据检查布局时，可以加入 Mock.js。

### 为什么去掉后端测试编写

本项目有意移除 Agent 默认的后端测试编写行为。目标不是声称测试没有价值，而是阻止测试成为与业务代码平行增长的第二套实现：每增加一个功能就增加一个测试类，每修改一个功能又要同步修改测试，最终维护测试的时间超过实现本身。

这是一个明确且有取舍的工作方式。受法规、团队流程或 CI 门禁约束而必须新增测试的项目不适合直接使用这条默认规则。

### 安装

在 PowerShell 中执行：

```powershell
git clone https://github.com/Hubujiu/practical-coding.git "$env:USERPROFILE\.codex\skills\practical-coding"
```

然后重新启动 Codex 或新建任务。

### 调用

Skill 默认应用于编码任务，也可以显式调用：

```text
$practical-coding
```

最短自然提示词：

```text
务实编码
```

不支持 Skill 的 Agent 可以使用这段精简提示词：

```text
务实编码：先复用和调研，再做最小实现；后端不写测试，只有我报告 bug 后才用日志调试；前端可用 Mock.js 检查布局。
```

### 思想来源

- [Ponytail](https://github.com/DietrichGebert/ponytail)：参考其“先判断是否需要存在，再依次复用现有代码、标准库、平台能力和已有依赖，最后才写最小实现”的决策梯子。
- [Marcos Hernanz 的 AGENTS.md](https://x.com/marcoshernanz/status/2083954734487212511?s=46)：参考其简单实现、分层成长、模块化、依赖复用、成熟产品调研和长期架构边界。

Practical Coding 是独立融合与扩展，不是上述项目的复制版本；它额外强化了实现前调研，并加入了由本项目作者确定的后端测试与日志调试规则。

### 项目结构

```text
practical-coding/
├─ SKILL.md
├─ agents/
│  └─ openai.yaml
├─ CONTRIBUTING.md
├─ LICENSE
└─ README.md
```

## English

Practical Coding is an always-on coding-agent skill that combines Ponytail's implementation restraint, Marcos Hernanz's engineering boundaries, and an explicit preference for researching proven solutions while avoiding low-value backend test maintenance.

### The problem it addresses

Coding agents often turn implementation into code production: speculative abstractions, unnecessary dependencies, a new backend test class for every feature, stale tests after each behavior change, and still more work to maintain the testing machinery itself.

This skill targets a recurring experience where implementation takes roughly ten minutes while generated tests and their repairs consume an hour. That ratio describes the motivating experience behind this project, not a universal benchmark.

The skill directs an agent to:

- Establish the real requirement and code boundary before adding anything.
- Prefer existing code, the standard library, native platform capabilities, and installed dependencies.
- Research official guidance and multiple mature implementations before adding a dependency or building a non-trivial capability.
- Deliver the smallest complete change without speculative abstractions or temporary architecture.
- Trust backend implementation logic by default and create no backend tests.
- Diagnose only user-reported backend bugs, using focused logging and log analysis.
- Use Mock.js when representative frontend data is needed for layout inspection.

### Backend testing stance

This project intentionally removes backend test authoring from the agent's default workflow. It does not claim that testing has no value; it rejects test code becoming a parallel implementation whose maintenance costs exceed the feature itself.

This is an opinionated trade-off. Projects that require new tests for regulatory, team-policy, or CI-gate reasons should not adopt this rule unchanged.

### Installation

Run in PowerShell:

```powershell
git clone https://github.com/Hubujiu/practical-coding.git "$env:USERPROFILE\.codex\skills\practical-coding"
```

Restart Codex or start a new task.

### Invocation

The skill is eligible for automatic invocation on coding tasks and can also be called explicitly:

```text
$practical-coding
```

Short natural-language prompt:

```text
Practical coding.
```

For agents without Skill support:

```text
Use practical coding: reuse and research first, then make the smallest implementation; write no backend tests, debug only user-reported bugs through logs, and use Mock.js for frontend layout checks when useful.
```

### Influences

- [Ponytail](https://github.com/DietrichGebert/ponytail): the decision ladder that asks whether a capability needs to exist and prefers reuse, standard libraries, native features, and installed dependencies before custom code.
- [Marcos Hernanz's AGENTS.md](https://x.com/marcoshernanz/status/2083954734487212511?s=46): simple implementations, layered growth, modularity, dependency reuse, studying established products, and durable architecture decisions.

Practical Coding is an independent synthesis and extension rather than a copy of either source. It strengthens research-before-implementation and adds its own backend testing and logging policy.

## License

[MIT](LICENSE)

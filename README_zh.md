# Practical Coding — 渐进式能力树实验

> **实验分支：** `experiment/progressive-ladders`。当前结构是待验证候选方案，不代表已发布 benchmark 结论。

Practical Coding 默认只回答一个问题：

> **下一步可靠行动，最少需要多少工程化深度和多少上下文？**

默认运行时继续保持 Ponytail 式最小化。**需求访谈、grill-me、Decision 这类交互流程不属于自动路由树。**

## 默认结构

```text
用户任务
  ↓
Core / E0 Direct
  ↓  仍存在执行不确定性且一个便宜实验可判定
E1 Probe
  ├─ E2 diagnosis
  │   └─ E3 security / state / compatibility / performance
  └─ E2 engineering
      └─ E3 security / state / compatibility / performance / quality / interface

检索独立：
R0 Target → R1 Local
             ├─ R2 Structural
             ├─ R2 External contract
             └─ R3 Bounded exhaustive repo
```

模型默认直接从 Core/E0 开始，不再先判断“要不要澄清”“要不要 Decision”。

**Execution 和 Retrieval 是两个真正独立的轴。** 找文件、caller、reference、sibling、contract、implementation、configuration 都属于 Retrieval，本身不会让执行从 E0 升到 E1。因此简单修改也可能是 `E0/R2`，而目标已知的复杂 bug 也可能是 `E3/R0`。

## 仅手动激活的交互模式

`grill-me` 式需求澄清和 Decision/方案选择被移出自动能力树。**需求模糊、存在多个方案、任务重要、高风险、模型觉得多问一点更好，都不能成为自动 trigger。**

只有用户当前指令明确要求相应行为时才允许加载：

- [`references/manual/clarification.md`](references/manual/clarification.md)：例如“grill me”“先采访我需求”“先只问需求不要写代码”；
- [`references/manual/decision.md`](references/manual/decision.md)：例如“进入 Decision 模式”“先把方案列出来让我选再实现”。

显式描述这个行为也算手动激活，不要求用户必须知道文件名。但一个 manual mode **不能自动跳转到另一个 manual mode**。

普通编码任务如果缺少一个导致完全无法安全执行的必要信息，可以只问那个最小阻塞问题；这只是正常交互，不等于进入 grill-me/Decision 工作流。

## Core：保持最小

大多数任务应该保持 Core + 浅执行深度：

- 最小可观察成功；
- 最小但完整的修改；
- 优先复用项目已有 primitive；
- 不添加推测性的抽象、wrapper、fallback、配置、验证、测试或文档；
- 用最便宜、能证伪关键结论的检查验证；
- 不碰无关代码和用户已有修改。

## 执行深度与能力树

| 深度 | 含义 | 加载 |
|---|---|---|
| **E0 Direct** | 行为、契约、验证已由当前/检索到的证据确定 | 仅 Core |
| **E1 Probe** | 一个便宜的可执行观察就能解决一个执行不确定性 | 仅 Core |
| **E2 Root** | 真实执行问题需要结构化处理 | diagnosis 或 engineering 二选一 |
| **E3 Leaf** | 仍存在明确领域保证 | 根能力 + 一个专家叶子 |

E1 被刻意限制得很窄：复现一个行为、执行一条路径、证伪一个具体假设，或者跑一个能直接决定下一步的 focused check。**搜索/阅读源码不属于 E1。**

`Debugging` 是 diagnosis 根能力；只有已经观察到错误、在足够的 bounded retrieval 和必要的 Probe 后原因仍未知时才加载。`engineering` 只在目标行为已知，但 authoritative contract、不变量、所有权边界或协同修改面仍无法定位时加载。

E3 专家叶子保持窄边界：`security / state / compatibility / performance / quality / interface`。它们吸收专家 Skill 的 trigger、procedure、exit、verification，但不会成为全局 checklist。

## Retrieval：唯一的源码/上下文获取轴

```text
R0 Target
└─ R1 Local
   ├─ R2 Structural
   ├─ R2 External contract
   └─ R3 Bounded exhaustive repo
```

- `R0`：目标已经知道；
- `R1`：局部、排序后的搜索，也包括普通 caller/reference/sibling/附近 contract 检索；
- `R2 Structural`：调用、依赖、数据流、配置流等结构关系；
- `R2 External`：仓库无法确定的官方 API/协议/许可证契约；
- `R3`：明确要求 repository-wide exhaustive claim，或低层检索始终无法定位边界。

仍然遵循 **expand → localize → contract**。Codebase Memory、LSP/AST、FFF 风格 ranked retrieval 等只是可选加速器，不是依赖。

`references/navigation.md` 暂时保留文件名以减少迁移，但它在概念上只是 **Retrieval 内部较深的 R2 Structural / R3 coverage 操作方法**，不再是第三个轴，也不是独立阶段。

## Benchmark 反向优化

自动能力树继续通过 no-skill、上一个已接受 Practical Coding、depth caps、parent-vs-leaf ablation 和真实项目体验来调优：正确性/安全/build 优先，然后才比较路由、token、时间、tool calls、LOC。

两个轴的 benchmark 必须保持可解释：如果任务只是需要多找一个 caller，它可以是 `E0/R1`；只有真正做了可执行 Probe 才能记为 E1。

手动模式单独测两件事：

1. 用户明确激活时是否真的有收益；
2. 普通任务的 **spontaneous manual activation 必须为 0**。

因此 Clarification/Decision 不再参与 adaptive minimum-sufficient path，也不能靠 benchmark 调成自动 Gate。

## WikiSkill 式演化闭环

运行时不读取 `evolution/`。维护阶段把 benchmark/真实项目体验、持久 wiki 知识、冻结实验、runtime 规则分开，只有重复机制经过验证后才修改能力树边界。

## Runtime references

```text
references/
├── debugging.md
├── engineering.md
├── navigation.md         # Retrieval 内部：较深 R2 Structural / R3 coverage
├── delegation.md
├── specialists/          # 自动路由可选择
│   ├── security.md
│   ├── state.md
│   ├── compatibility.md
│   ├── performance.md
│   ├── quality.md
│   └── interface.md
└── manual/               # 只能由用户明确激活
    ├── clarification.md
    └── decision.md
```

详见 [`benchmarks/LADDER_EVOLUTION.md`](benchmarks/LADDER_EVOLUTION.md)、[`evolution/README.md`](evolution/README.md) 与 [`evolution/EXPERIENCE_SCHEMA.md`](evolution/EXPERIENCE_SCHEMA.md)。
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
  ↓  当前证据不足才加深
E1 Focused
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

## 仅手动激活的交互模式

`grill-me` 式需求澄清和 Decision/方案选择被移出自动能力树。**需求模糊、存在多个方案、任务重要、高风险、模型觉得多问一点更好，都不能成为自动 trigger。**

只有用户当前指令明确要求相应行为时才允许加载：

- [`references/manual/clarification.md`](references/manual/clarification.md)：例如“grill me”“先采访我需求”“先只问需求不要写代码”；
- [`references/manual/decision.md`](references/manual/decision.md)：例如“进入 Decision 模式”“先把方案列出来让我选再实现”。

显式描述这个行为也算手动激活，不要求用户必须知道文件名。但一个 manual mode **不能自动跳转到另一个 manual mode**。

普通编码任务如果缺少一个导致完全无法安全执行的必要信息，可以只问那个最小阻塞问题；这只是正常交互，不等于进入 grill-me/Decision 工作流。

## Core：保持最小

大多数任务应该停在 E0/E1：

- 最小可观察成功；
- 最小但完整的修改；
- 优先复用项目已有 primitive；
- 不添加推测性的抽象、wrapper、fallback、配置、验证、测试或文档；
- 用最便宜、能证伪关键结论的检查验证；
- 不碰无关代码和用户已有修改。

## 执行深度与能力树

| 深度 | 含义 | 加载 |
|---|---|---|
| **E0** | 目标、契约、验证都清楚 | 仅 Core |
| **E1** | 一个局部证据步骤即可解决阻塞 | 仅 Core |
| **E2** | 真实执行问题需要结构化处理 | diagnosis 或 engineering 二选一 |
| **E3** | 仍存在明确领域保证 | 根能力 + 一个专家叶子 |

`Debugging` 是 diagnosis 根能力；只有已经观察到错误、但原因仍未知时才加载。`engineering` 只在契约、不变量、所有权边界或协同修改面无法由 E1 定位时加载。

E3 专家叶子保持窄边界：`security / state / compatibility / performance / quality / interface`。它们吸收专家 Skill 的 trigger、procedure、exit、verification，但不会成为全局 checklist。

## 检索树

```text
R0 Target
└─ R1 Local
   ├─ R2 Structural
   ├─ R2 External contract
   └─ R3 Bounded exhaustive repo
```

仍然遵循 **expand → localize → contract**。Codebase Memory 等结构化工具只是可选加速器，不是依赖。

## Benchmark 反向优化

自动能力树继续通过 no-skill、上一个已接受 Practical Coding、depth caps、parent-vs-leaf ablation 和真实项目体验来调优：正确性/安全/build 优先，然后才比较路由、token、时间、tool calls、LOC。

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
├── navigation.md
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
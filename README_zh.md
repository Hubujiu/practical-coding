# Practical Coding

Practical Coding 是一个 Agent Skill：目标是交付最小、可靠的代码修改，同时避免把所有任务都变成重量级流程。

运行时只有一个 Core、三个由证据触发的推理模块，以及一条独立的检索策略：

```text
Core / Direct
├─ 已观察失败但原因未证实            → Debugging
├─ 会改变实现方向的重大选择尚未解决    → Decision
└─ 契约、不变量、风险边界或证据计划未解决 → Implementation

检索独立：
已知目标 → 有界/排序搜索 → 结构或权威证据 → 有界穷举覆盖
```

## 运行时契约

Core 始终适用：

- 先定义最小可观察成功；
- 复用项目已经存在的 primitive；
- 不添加推测性的抽象、依赖、配置、验证、测试或文档；
- 保留无关行为和用户已有修改；
- 用能证伪关键结论的最便宜检查验证。

没有 Event Router 条件时保持 Direct。风险名词、文件数量、路径未知或需要找 caller，本身都不是推理升级理由。

存在未解决事件时只加载一个 reference：

- [`references/debugging.md`](references/debugging.md)：已观察失败仍没有证据化原因；
- [`references/decision.md`](references/decision.md)：会改变实现方向的重大用户选择尚未解决；
- [`references/implementation.md`](references/implementation.md)：安全执行被未知契约、协同不变量、重大风险边界或证据计划阻塞。

需求采访和 `grill-me` 只能由用户显式激活 [`references/manual/clarification.md`](references/manual/clarification.md)。普通任务里一个不可避免的阻塞问题不算进入采访模式。

## 检索策略

检索与推理正交，始终使用能提供充分当前上下文的最便宜能力：

1. 读取已知路径或 symbol；
2. 使用有界/排序的文件名、文本或 symbol 搜索；
3. 关系问题在确实节省探索成本时使用已经可用的结构索引；
4. 只有明确穷举结论才做有界覆盖，仓库无法建立的外部契约才查询权威来源；
5. 重要结论必须回到当前源码验证。

[`references/navigation.md`](references/navigation.md) 只用于较重的检索过程。Codebase Memory、LSP/AST、排序搜索和普通搜索都是可选能力，不是依赖。

## 演化纪律

普通运行时不读取 `evolution/`。维护阶段才记录体验、合并重复机制、先冻结实验再修改运行时规则，并保留失败改进。

被拒绝的 E/R 深度与专家叶子实验保存在 [`evolution/rejected/`](evolution/rejected/)，其 n=3 证据位于 [`benchmarks/results/progressive-tree/`](benchmarks/results/progressive-tree/)。替代实验记录在 [`evolution/experiments/event-router-restoration.md`](evolution/experiments/event-router-restoration.md)。

## 验证

公共回归与真实仓库 held-out 使用 `gpt-5.6-luna`、medium reasoning。迭代阶段使用 `n=1`；发布结论必须完成 current-only 全矩阵 `n=3`。

```powershell
pwsh -NoProfile -File benchmarks/run.ps1 -SelfTest
pwsh -NoProfile -File benchmarks/run.ps1 -ProgressiveSelfTest

python benchmarks/run_catalog.py --profile full --runs 3 --workers 3 `
  --arm practical-current --arm practical-native --output benchmark-results/public-final

python benchmarks/progressive_validation.py --phase all --current-only --runs 3 --workers 3 `
  --output benchmark-results/heldout-final
```

历史报告只证明生成它的版本；除非在同一冻结矩阵中重跑，否则只能做非配对参照。

MIT License。第三方归属见 `THIRD_PARTY_NOTICES.md`。

# Practical Coding

Practical Coding 是一个 Agent Skill：目标是交付最小、可靠的代码修改，同时避免把所有任务都变成重量级流程。

当前实验把渐进式披露实现为**可演化的局部 Router 树**，而不是扁平的全局 Router，也不是预先写死的 E0-E3 线性等级。

```text
自动执行树

Core（depth 0）
├─ 已观察失败但原因未证实            → Debugging（depth 1，当前为叶子）
└─ 执行契约/风险边界尚未解决          → Implementation（depth 1，当前为叶子）

手动模式——只能由用户显式请求
├─ Decision
└─ Clarification / grill-me

检索——与执行深度独立
已知目标 → 有界/排序搜索 → 结构/权威证据 → 有界穷举覆盖
```

## 运行时契约

Core 始终适用：

- 先定义最小可观察成功；
- 复用项目已经存在的 primitive 和 contract；
- 不添加推测性的抽象、依赖、配置、验证、测试或文档；
- 保留无关行为和用户已有修改；
- 用能证伪关键结论的最便宜检查验证。

Core 是树根，只知道自己的直接子节点。一个模块被加载后，只负责描述自己的下一层 Router；Core 不知道未来的孙节点。没有通过 benchmark 证明有价值的下一层时，模块必须明确声明自己是叶子节点。

当前自动节点：

- [`references/debugging.md`](references/debugging.md)：已观察失败仍没有证据化原因；
- [`references/implementation.md`](references/implementation.md)：安全执行被未知契约、协同不变量、重大风险边界或证据要求阻塞。

自动路由必须保持收敛：可以为了当前 blocker 继续向更深的执行能力披露，但不能重新打开 deliberation。执行途中出现普通技术选择时，优先复用项目惯例、平台默认或最小充分且可逆的方案。如果确实存在只能由用户决定、且没有安全默认值的 blocker，只问最小阻塞问题，不自动进入 Decision。

## 手动模式

Decision 不再属于自动 Router。

- [`references/manual/decision.md`](references/manual/decision.md) 只有在用户当前明确要求“比较方案、技术选型、推荐架构/依赖/API/数据模型”等决策分析时才加载；
- [`references/manual/clarification.md`](references/manual/clarification.md) 只有在用户明确要求先采访、grill、提问或澄清需求时才加载。

手动模式不属于自动 capability path。任何自动节点都不能路由到 Decision 或 Clarification。手动模式完成后，把已经确定的结果作为输入返回 Core。

## 检索策略

检索与执行树正交，始终使用能提供充分当前证据的最便宜能力：

1. 读取已知路径或 symbol；
2. 使用有界/排序的文件名、文本或 symbol 搜索；
3. 关系问题在确实节省探索成本时使用已经可用的结构索引；
4. 只有明确穷举结论才做有界覆盖，仓库无法建立的外部契约才查询权威来源；
5. 重要结论必须回到当前源码验证。

[`references/navigation.md`](references/navigation.md) 只用于较重的检索过程。Codebase Memory、LSP/AST、排序搜索和普通搜索都是可选能力，不是依赖。

## Benchmark 驱动树演化

Benchmark 不再用于证明一棵预先写死的树“路由正确”，而是用于决定树应该如何生长、拆分、合并、提升、折叠或删除节点。

当前拓扑放在 [`benchmarks/tree_topology.json`](benchmarks/tree_topology.json)。新的 [`benchmarks/tree_cases.py`](benchmarks/tree_cases.py) 不再保存 expected automatic route、E0-E3 或固定 capability path。

[`benchmarks/tree_validation.py`](benchmarks/tree_validation.py) 会让普通任务分别在 Core 和每个 root-to-node capability ceiling 下运行，再运行 adaptive candidate。随后 [`benchmarks/tree_analysis.py`](benchmarks/tree_analysis.py) 根据稳定通过的 ceiling 推导任务的 **minimum-sufficient node set**。Adaptive Router 与这个集合不一致时，首先视为 topology 证据，而不是直接判模型失败。

树的修改规则：

- **新增/加深**：存在可观察的 pre-load signal，而且 child 相比 parent 在多个任务或仓库上稳定增加质量收益；
- **合并/移动边界**：兄弟节点频繁同时成为 minimum-sufficient，或长期难区分而没有净收益；
- **提升/折叠**：child 在 parent 的绝大部分有效任务上都必须加载；
- **删除**：节点没有独立的 minimum-sufficient 案例，也没有相对 parent 的稳定增益；
- **拆分**：某个叶子节点出现重复失败簇，并且能在加载前识别出稳定边界。

Depth 只表示渐进披露深度，不代表固定的任务复杂度等级。不同分支完全可以有不同深度。

## 验证

修改 runtime、topology、case 或 scorer 时只跑 `n=1`；冻结候选后再跑 `n=3`。

```powershell
pwsh -NoProfile -File benchmarks/run.ps1 -TreeSelfTest

python benchmarks/tree_validation.py --current-only --runs 1 --workers 3 `
  --output benchmark-results/tree-n1
python benchmarks/tree_analysis.py benchmark-results/tree-n1/results.jsonl `
  --output benchmark-results/tree-n1/analysis.json
```

最终冻结比较：

```powershell
python benchmarks/tree_validation.py --runs 3 --workers 3 `
  --output benchmark-results/tree-final
python benchmarks/tree_analysis.py benchmark-results/tree-final/results.jsonl `
  --output benchmark-results/tree-final/analysis.json
```

已接受的 v1.5 扁平 Debugging/Decision/Implementation Event Router 继续作为历史 baseline，保存在 [`benchmarks/results/v1.5/`](benchmarks/results/v1.5/) 和 [`evolution/experiments/event-router-restoration.md`](evolution/experiments/event-router-restoration.md)。被拒绝的固定 E/R 深度与专家叶子实验继续保存在 [`evolution/rejected/`](evolution/rejected/) 和 [`benchmarks/results/progressive-tree/`](benchmarks/results/progressive-tree/)。历史结果不会为了适配新树而重写。

MIT License。第三方归属见 `THIRD_PARTY_NOTICES.md`。

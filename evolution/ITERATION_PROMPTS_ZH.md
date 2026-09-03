# Practical Coding 演化迭代提示词

本文件用于显式启动维护态迭代。普通编码任务不得自动读取 `evolution/`，也不得因为一次任务表现不佳就直接修改运行时 Skill。

推荐把“沉淀经验”和“修改 Skill”拆成两次独立请求：先将当前会话写入 wiki，再在后续请求中基于累计证据做一次原子迭代。这样可以减少单次会话对候选方案和评测标准的同时污染。

## 1. 单次原子迭代：推荐主提示词

```text
你现在维护仓库 Hubujiu/practical-coding 的 experiment/evolvable-router-tree 分支。

显式启用 evolution/skills/evolve-skill/SKILL.md，只执行一次可归因的 Skill 演化迭代。目标不是增加更多流程或节点，而是在不降低交付质量的前提下，用已有证据验证一个最小候选修改；没有足够证据时返回 no_action。

执行要求：

1. 先读取并遵守 AGENTS.md、SKILL.md、evolution/skills/evolve-skill/SKILL.md。
2. 读取 evolution/wiki/index.md、evolution/wiki/skill-impact.md，以及与本次机制直接相关的少量 wiki、receipt、experiment 和 benchmark 结果。不要把整个 evolution/ 塞进上下文。
3. 读取 benchmarks/tree_topology.json、benchmarks/TREE_EVOLUTION.md 和当前相关 benchmark 契约。
4. 记录当前分支 HEAD、工作树状态、模型、reasoning 配置、harness、case 集、scorer 版本和重复次数。只在 experiment/evolvable-router-tree 上工作，不合并 PR。
5. 从累计证据中只选择一个原子假设；目标只能是一个节点、一个父子边界、一个检索边界或一个评测缺陷。多个相互独立的问题必须拆成后续迭代。
6. 在看到候选结果之前，先在 evolution/experiments/ 写下冻结假设：证据指针、因果机制、可观察的预加载/激活信号、准确目标、候选补丁形状、预期收益、明确反证条件、baseline ref、评测方案和接受门槛。
7. 在修改运行时 Skill 之前冻结或新增 benchmark。新增能力至少要有正例和边界/负例；case 不得写入“正确自动路由节点”，scorer 不得奖励候选措辞，也不得在看到候选结果后偷偷改变门槛。
8. 先在冻结 benchmark 上运行 baseline n=1 并保存完整 artifact；再应用最小候选补丁，并使用完全相同的模型、工具、case、scorer、超时和环境运行 candidate n=1。
9. 同时运行所有相关确定性测试和现有回归。确定性测试通过只能证明结构或解析契约成立，不能代替真实模型任务质量。
10. 若 n=1 暴露候选缺陷，可以回到一个新的假设重新开始；不得连续修补同一候选直到迎合 held-out。只有冻结候选才运行配对 n>=3 的 baseline/candidate/no-skill 发布矩阵。
11. 接受顺序必须是：交付正确性、安全性、兼容性、可达性和必要检查不下降；自动路径仍是有效父子路径；Decision 与 Clarification 仍为零自发触发；新增 benchmark 不下降；所有必须门禁可判定。只有质量打平后才比较输入 token、时长、工具调用和平均加载深度。
12. 若任一必要质量门禁下降或证据不完整，回滚运行时候选。保留冻结 benchmark、原始 artifact 和机制知识，并将拒绝原因写入 evolution/rejected/ 与 evolution/wiki/skill-impact.md。
13. 若候选通过门禁，更新 evolution/wiki/skill-impact.md、evolution/wiki/log.md 和相关机制状态，再提交一个边界清晰的 commit。
14. 最终必须报告：假设文件、benchmark 变化、baseline 结果、candidate 结果、配对重复次数、接受/拒绝决定、是否已回滚、最终 commit SHA、仍缺少的证据。不得把 pending 描述成 accepted。

结构不变量：

- Core 只拥有直接子节点；加载节点只知道自己的直接子节点，不允许 Core 跨级选择后代。
- Decision 和 Clarification 永远只能由当前用户显式请求触发，不得学习为自动 fallback。
- Retrieval 与执行树正交；不要为了让路由更好看而扩大检索。
- 不保留对称层级、固定深度或历史节点名；add/split/merge/promote/collapse/remove 都必须由质量合格后的净收益决定。
- 不得用 token 节省补偿正确性或安全性下降。
- 已记录在 evolution/rejected/ 的方案不得在没有新独立证据直接解决其失败机制时复活。
```

## 2. 先把当前会话沉淀到 wiki

这一步只提取证据，不修改 `SKILL.md`、自动 Router、参考模块或运行时代码。

```text
在 Hubujiu/practical-coding 的 experiment/evolvable-router-tree 分支上，显式启用 evolution/skills/session-to-wiki/SKILL.md。

只使用当前可见会话与可验证工具结果，把具有复用价值的成功机制、失败机制、路由边界、benchmark 缺陷或用户纠正沉淀到 evolution/。先按照 evolution/EXPERIENCE_SCHEMA.md 创建一份新的、经过脱敏的不可变 receipt，再读取少量相关 wiki 页面进行因果合并，最后更新 wiki/index.md 与 wiki/log.md。

不得复制完整聊天，不得保存私有推理，不得写入秘密、个人标识或私有代码，不得为了形成结论改写旧 receipt，不得修改任何运行时 Skill/Router 文件。结束时报告 receipt 路径、wiki 变化、支持与反例证据，以及是否已形成足以进入 evolve-skill 的候选假设。
```

## 3. 连续迭代，但必须逐轮门禁

不要使用“持续优化直到最好”这类无边界提示词。它会诱导模型连续堆叠未经验证的修改、反复查看 held-out 失败并调整 scorer。

需要连续探索时，使用下面的有界版本：

```text
按照 evolution/skills/evolve-skill/SKILL.md 最多执行 3 次独立迭代。

每一轮都必须完整经历：独立冻结假设 → 冻结 benchmark → baseline → 单一候选 → 相同证据 candidate → 回归门禁 → 接受并提交，或拒绝并回滚。上一轮没有完成“接受并提交”或“拒绝、回滚并记录”的闭环，不得开始下一轮；被拒绝后若继续，下一轮必须使用新的独立假设，不能继续修补同一候选。不同轮次不得共享未冻结的候选结果。出现 no_action、基础设施结果不可判定、预算耗尽或连续两轮拒绝时立即停止；任一轮出现必要质量门禁下降时，必须先回滚并记录，再由停止条件决定是否还能开启新的独立轮次。

最终按轮次列出假设、证据、结果、决定和 commit，不得把多轮修改压成一个无法归因的补丁。
```

## 推荐调用顺序

1. 会话产生了可复用经验时，先单独运行“session-to-wiki”。
2. 累计证据足够时，在新请求中运行“一次原子迭代”。
3. 只有冻结候选通过完整配对门禁后，才把它称为已接受的 Skill 改进。

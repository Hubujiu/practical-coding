# 渐进式能力树实验报告

## 结论

候选提交 `eefb3b79c688ced94273daea6a0af22b74d47022` **未通过合并门槛**。这次实验完成了当前版本的全量公共回归、E/R 双轴最低充分深度、E2 Root → E3 Leaf 消融，以及 22 个 held-out 真实任务；结果不支持按现状发布该能力树。

## 正式运行

| 运行 | 单元 | n | 结果 |
|---|---:|---:|---|
| 当前版本公共 full profile | 294 | 3 | 0 indeterminate；Delivery 54/54，Debug 34/42 |
| 当前版本 progressive current-only | 378 | 3 | 0 indeterminate；包含 66 held-out、240 axis caps、72 ablation |

没有同时运行 no-skill、Ponytail、旧版本或组合 arm。旧版本只读取 `benchmarks/results/v1.2/` 的既有正式报告，因此不是原子配对对比。

## P0 结果

### E/R 最低充分深度

- Execution：E0=6，E1=1，E2=0，E3=1。E2 没有一次成为最低充分深度。
- Retrieval：R0=1，R1=7，R2=0，R3=0。R2/R3 没有一次成为最低充分深度。
- Adaptive 的端到端精确率：Execution 4/8，Retrieval 1/8；Execution 有 3 个质量失败和 1 个不一致，Retrieval 有 5 个质量失败、2 个过度升级。

这说明当前样本支持 Core/E0、Probe/E1 和局部检索 R1 的存在，但没有为独立 E2、R2、R3 层级提供充分经验依据。单个 E3 最低充分结果也不能抵消下面的 leaf 消融结论。

### E2 Root → E3 Leaf 消融

8 个冻结任务、每个 parent-only / parent+leaf / adaptive 各 n=3：

- 质量提升：0；
- 质量持平：7；
- 质量回退：1（compatibility leaf 2/3，parent-only 3/3）；
- adaptive path exact：6/8；
- 多数 leaf 明显增加 token、时长或 tool calls。

因此专家叶子没有赚回上下文成本，不能按现状接受。

### Held-out 真实任务

- 22 个任务，来自 3 个冻结真实仓库；66/66 determinate。
- 单元通过 58/66（87.9%）；18/22 任务达到三次稳定通过。
- routing trace valid 40/66（60.6%）；routing exact 21/66（31.8%）。
- manual-only spontaneous activation 0/66，通过零误触发要求。

4 个不稳定/失败任务中，`ca-filename-probe` 的三次失败来自冻结 checkout 未安装 Vitest，属于环境可执行性不足；另外三个任务包含真实证据覆盖缺口或执行层级与 root/leaf 路径不一致。即使剔除该环境受限任务，路由精确性和 leaf 消融仍不足以接受架构。

## 公共回归与历史报告

当前 full profile：Delivery 54/54，Debug 34/42，Decision 5/30，Router 53/114，Native Behavior 24/54。

- Delivery 是有效的当前质量证据。
- Debug 的 8 个失败是 shared-boundary / sibling-safety 范围不足，属于真实回归风险。
- Decision、Router、Native Behavior 仍按旧架构标签和旧文件名评分，不能用来衡量 E0-E3/R0-R3 或 manual-only 新边界。
- v1.2 既有报告为 Router retrieval 106/114、Native Behavior 54/54、capability regression 75/75。由于没有本轮配对重跑，不能宣称候选优于或劣于 v1.2、no-skill、Ponytail 或组合 arm。

## 决策

保留实验、runner 和冻结证据，拒绝当前树作为 release 架构。PR 用于审阅实验工具与失败证据，不应合并候选 runtime 结构。下一轮应先缩减或重定义没有获得最低充分/消融支持的节点，再冻结新实验；不得针对这 22 个任务改写触发词来刷分。


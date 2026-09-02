# Evolvable local router tree 发布验证报告

## 结论

候选提交 `d85c72c` 的树质量 n=1 迭代和冻结 n=3 非回归均通过。最终 n=3 使用两个独立 work（8 case + 7 case），每个 work 使用 8 个并行 worker，单个 work 不超过 10 个 case。

合并后的结果为 15 个 case、252/252 个 determinate cell；adaptive、frozen baseline 和 no-skill 均为 45/45 通过，`release_quality_gate` 为 `PASS`。

## 配对结果

| arm | 质量 | 稳定任务 | 平均 tokens | 平均时长 | 平均工具调用 |
|---|---:|---:|---:|---:|---:|
| adaptive | 45/45 | 15/15 | 253,543.13 | 84.15s | 8.82 |
| frozen baseline | 45/45 | 15/15 | 222,598.13 | 80.31s | 8.02 |
| no-skill | 45/45 | 15/15 | 245,342.04 | 81.66s | 6.33 |

adaptive 相对两个比较 arm 均通过质量非劣性门禁（margin 0.03）。本轮不宣称成本优势；adaptive 的平均 tokens、时长和工具调用高于 frozen baseline。

## 纪律与边界

- adaptive trace failures：0；spontaneous manual：0；explicit manual contract failures：0。
- Core、Debugging、Implementation capability ceiling 均为 39/39。
- 一个初始不确定 cell `pp-running-after-throw / cap:debugging / repetition 1` 已独立重跑；该 case 的 18 个 cell 全部通过，随后完成 252 cell 合并分析。
- tree topology 未改变；execution-state 仍是 cross-cutting substrate，不是 Router 节点。

## 未完成项

本报告只证明树质量 n=3 非回归。execution-state 四臂模型 benchmark（full history、state shadow、state history-free、no-skill full history）以及最终 outbound transport/header/cookie/proxy 审计仍为 `pending`，因为当前仓库没有实现该四臂 transport runner；不能用普通 tree runner 代替。

## 可复现边界

- 候选：`d85c72cc5aa239da32352309e723ed1e6fc80429`。
- 冻结 baseline：`ba4058b4ef47a42bf79c9963b25678a2389897c1`。
- 模型：`gpt-5.6-luna`，reasoning `medium`。
- 原始 transcript、cell JSON 和机器路径保留在 ignored local artifacts；本目录只包含脱敏汇总。

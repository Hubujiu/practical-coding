# Evolvable local router tree 发布验证报告

## 结论

候选提交 `b82b38d` 通过完整发布质量门槛。两个独立 work 合计覆盖 15 个 case、252 个 n=3 cell；adaptive、冻结 v1.5 baseline 和 no-skill 均为 45/45 通过，非劣性门禁通过。

## 配对结果

| arm | 质量 | 稳定任务 | 平均 tokens | 平均时长 | 平均工具调用 |
|---|---:|---:|---:|---:|---:|
| adaptive | 45/45 | 15/15 | 253,543.13 | 84.15s | 8.82 |
| frozen v1.5 | 45/45 | 15/15 | 222,598.13 | 80.31s | 8.02 |
| no-skill | 45/45 | 15/15 | 245,342.04 | 81.66s | 6.33 |

adaptive 相对两个比较 arm 均满足质量非劣性门禁（margin 0.03）。质量相同的情况下，adaptive 的平均 tokens、时长和工具调用仍高于 frozen v1.5；本轮不把成本改善作为结论。

## 纪律与能力消融

- adaptive trace failure 为 0；spontaneous manual 为 0；explicit manual contract failure 为 0。
- Core、Debugging、Implementation capability ceiling 均为 39/39。
- analyzer 发现 29 个 exact-minimum 关系和 10 个 over-disclosure 关系；没有任务出现多个 minimum 节点或未通过 capability ceiling。
- 两个叶子没有获得稳定的独立 lift；这只作为诊断，不自动修改已冻结拓扑。

## 可复现边界

- 模型：`gpt-5.6-luna`，reasoning `medium`。
- 冻结 baseline：`ba4058b4ef47a42bf79c9963b25678a2389897c1`。
- 15 个任务、3 个仓库、每个 arm/capability 单元 n=3。
- 两个 work 分别为 8 case/135 cell 和 7 case/117 cell，每个 work 使用 8 个并行 worker，单个 work 不超过 10 个 case。
- 原始 transcript、cell JSON 和机器路径保留在 ignored local artifacts；本目录只包含脱敏汇总。

## 限制

该结果证明当前冻结候选在本 suite 上通过 n=3 质量与纪律门禁，不证明成本优势，也不将确定性 runtime contract 等同于模型质量证据。runtime hardening 的非 benchmark 回归另由 `tests.test_skill_state_hardening` 和 `benchmarks.test_skill_state_runtime` 覆盖。

# Evolvable local router tree 发布验证报告

## 结论

候选提交 `b202f7a165ae3ea4404d404bb1235ebf4270cbfb` 通过发布质量门槛。完整原子配对 n=3 共 252/252 个单元可判定；adaptive 为 45/45，冻结 v1.5 为 44/45，no-skill 为 44/45。候选在同一 runner、scorer、任务、仓库快照和模型下取得严格质量优势。

## 配对结果

| arm | 质量 | 稳定任务 | 平均 tokens | 平均时长 | 平均工具调用 |
|---|---:|---:|---:|---:|---:|
| adaptive | 45/45 | 15/15 | 258,061.64 | 76.82s | 8.42 |
| frozen v1.5 | 44/45 | 14/15 | 217,460.96 | 72.20s | 7.24 |
| no-skill | 44/45 | 14/15 | 258,750.62 | 76.55s | 6.31 |

adaptive 相对 v1.5 的质量高 1/45；v1.5 的单次失败来自 Decision 回答遗漏 SlidingWindow 对比项。no-skill 的单次失败来自取消诊断遗漏 focused-test 证据。adaptive 全部通过。

## 纪律与能力消融

- adaptive trace 45/45 有效；显式 manual contract 6/6；39 个自动任务单元中 spontaneous manual 为 0。
- Core、Debugging、Implementation capability ceiling 均为 39/39。
- analyzer 将 23 个自动单元判为 exact-minimum、16 个判为 over-disclosure。两个叶子没有获得独立的 minimum-sufficient lift；但此前 Core-only 完整 n=3 已在质量持平时回退全部成本指标，因此本轮不依据单次 analyzer 建议再次折叠拓扑。

## 成本限制

质量优势不等于成本优势。adaptive 相对 v1.5 的平均 tokens 高 18.67%，时长高 6.40%，工具调用高 16.26%。本轮加入的 bounded-evidence wording 没有证明成本改善；该子假设明确记为未确认。后续成本优化必须从新冻结假设和 n=1 开始，不能通过重复相同 n=3 寻找有利波动。

## 可复现边界

- 模型：`gpt-5.6-luna`，reasoning `medium`。
- 冻结 baseline：`ba4058b4ef47a42bf79c9963b25678a2389897c1`。
- 三个仓库、15 个任务、每个 arm/capability 单元 n=3。
- 原始 transcript、cell JSON 和机器路径保留在本地 ignored artifact；发布目录只包含脱敏汇总。

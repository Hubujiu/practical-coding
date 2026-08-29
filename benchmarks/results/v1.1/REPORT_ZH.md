# Practical Coding v1.1 全面评测报告

日期：2026-08-27

更新：2026-08-28（加入当前 Practical 补测；原 1239-cell combo 矩阵保持历史冻结）

性质：当前 Practical 受影响面补测覆盖旧 Cursor 报告中的 Practical 数据；历史 15-arm 共装矩阵保留作干扰对照。两者不是同一 paired run，也不是通用万能排行榜。

## 1. 结论

### 1.1 Practical Coding v1.1 当前结果

当前 Practical 补测在相同模型 `gpt-5.6-luna` / `medium` 下得到：

1. Delivery **27/27（100%）**，correct / safe / build 均为 100%；Decision **18/18（100%）**。
2. 最新 Debug v1.9 为 **29/30（96.7%）**，correct 100%、safe 96.7%；唯一失败是 `trace-page-window` 一次漏修 sibling caller。
3. 扩展后的 Router **114/114（100%）**，Native Behavior **54/54（100%）**；新增的风险名词、单文件高风险、迁移决策与故障优先级极端边界全部通过。
4. 与 Cursor 原矩阵的独立 `ponytail` arm 做跨运行观察：Delivery 100% 对 96.3%，Debug 96.7% 对 93.3%，Decision 100% 对 0%；但当前 Practical 使用 runner v1.8/v1.9，Ponytail 是 v1.6，不能把该差异当成新的 paired scorecard。
5. 当前 Practical 的通过率提升伴随成本：相对 Ponytail-only，Delivery 时间中位数约 +35.8%，Debug uncached input +37.6%、时间 +26.1%。Ponytail 仍是更轻、更快的编码 Skill。

当前适用套件合计为 **242/243（99.6%）**：Delivery 27/27、Decision 18/18、Debug 29/30、Router 114/114、Behavior 54/54。这些来自按受影响表面拆分的补测，不是单一 manifest 的 243-cell 原子运行。

详细的独立 Practical vs Ponytail-only 报告见 [`PRACTICAL_VS_PONYTAIL_ONLY_ZH.md`](PRACTICAL_VS_PONYTAIL_ONLY_ZH.md)。

### 1.2 历史 Cursor combo 矩阵结论

以下结论仍只描述固定模型、隔离 Codex 会话、15 种 Skill 排列组合的原始同轮矩阵：

1. **单独使用时**，Practical Coding 在编码交付与调试上明显优于 grill-me，数值上不低于或优于 Superpowers；与 Ponytail 在 Delivery 上同为 96.3%，但 Ponytail 交付代码更小。
2. **Decision（决策访谈）** 上，单独 Practical 与「含 grill-me / grilling 能力」的共装组合均为 100%；单独 Ponytail / Superpowers 接近 0%，说明它们不是决策访谈 Skill。
3. **共装干扰**：把 Superpowers 叠进 Delivery 往往会拉低通过率；把 grill-me 叠进编码任务，alone 很差，但与 Practical 共装时多数仍可维持高通过率。
4. **最佳共装信号**：`practical-current+ponytail` 在 Delivery 达到 100% 通过且 build 100%；四技能全装在 Debug 也达到 100%，但成本明显高于单独 Practical。
5. **Router / Behavior**（仅当时 Practical）分别为 96.4% 与 100%；已被 2026-08-28 的 114/114 与 54/54 扩展补测取代。

本结果支持有限结论：在本矩阵上，单独 Practical 是稳健默认；与 Ponytail 共装可提升 Delivery 天花板；与 Superpowers 共装通常更贵且不一定更好；grill-me 适合决策访谈，不适合单独承担编码。

## 2. 历史 Cursor combo 试验设置

| 项 | 值 |
|---|---|
| 仓库 HEAD | `792a74cfacd18824be12b994ff5e3ab0e4fe00c1`（拉取 GitHub 最新后） |
| Profile | `standard` + `--combo-matrix` |
| Cells | 1239（全部 determinate，0 indeterminate） |
| Runs / Workers | 3 / 3 |
| 墙钟 | 5.16 h |
| 稳定性门控 | `check_stability.py`：**STABLE** |
| Ponytail | `2ed6c52c…` |
| Matt Pocock skills（grill-me + grilling） | `5b15a47f…` |
| Superpowers | `b36e0829…` |

共装子集（15 arms）：四种组件 `{practical-current, ponytail, superpowers, grill-me}` 的全部非空子集。`grill-me` arm 同时注入 `grill-me` 与 `grilling` 原始 Skill。

套件覆盖：

- Delivery / Decision / Debug：全部 15 种共装 arm
- Router / Behavior：仅 Practical（项目路由与原生发现回归）

补测证据并未重跑 15-arm combo：

| 补测 | Runner | Cells | 用途 |
|---|---|---:|---|
| `practical-extreme-quality-v2-final-20260828` | v1.8 | 75 | Practical-only Delivery / Decision / Debug |
| `practical-debug-v19-final2-20260828` | v1.9 | 30 | 最新 Debug 与共享契约提示修复 |
| `practical-extreme-regression-v2-final-20260828` | v1.8 | 168 | 扩展 Router / Native Behavior |

## 3. 原始 combo 套件总表（suite rollups，历史冻结）

通过率与成本均为 determinate 中位数汇总。本节所有数值仍来自 2026-08-27 runner v1.6 同轮矩阵；不要把其中旧 `practical-current` 行与 2026-08-28 补测混为一次 paired run。

### 3.1 Delivery（9 cases × 15 arms × 3 = 405 cells）

| Arm | Pass | Correct | Safe | Build | Uncached median | Time median | LOC median |
|---|---:|---:|---:|---:|---:|---:|---:|
| practical-current | 96.3% | 100% | 100% | 88.9% | 16424 | 49.9s | 21 |
| ponytail | 96.3% | 100% | 100% | 88.9% | 15672 | 47.9s | 12 |
| superpowers | 51.9% | 51.9% | 96.3% | 100% | 18372 | 39.4s | 9 |
| grill-me | 18.5% | 18.5% | 63.0% | 100% | 10554 | 29.4s | 3 |
| practical+ponytail | **100%** | 100% | 100% | **100%** | 15394 | 48.1s | 16 |
| practical+superpowers | 85.2% | 92.6% | 100% | 77.8% | 13254 | 44.5s | 13 |
| practical+grill-me | 96.3% | 100% | 100% | 88.9% | 18445 | 59.1s | 21 |
| ponytail+superpowers | 63.0% | 66.7% | 100% | 88.9% | 20778 | 42.8s | 9 |
| ponytail+grill-me | 96.3% | 96.3% | 96.3% | 100% | 18252 | 45.5s | 11 |
| superpowers+grill-me | 48.1% | 48.1% | 92.6% | 100% | 18082 | 46.3s | 9 |
| practical+ponytail+superpowers | 88.9% | 92.6% | 100% | 88.9% | 18552 | 49.4s | 11 |
| practical+ponytail+grill-me | 96.3% | 100% | 100% | 88.9% | 12473 | 53.9s | 13 |
| practical+superpowers+grill-me | 92.6% | 100% | 100% | 77.8% | 19639 | 49.6s | 16 |
| ponytail+superpowers+grill-me | 70.4% | 70.4% | 88.9% | 100% | 21745 | 49.6s | 9 |
| all four | 92.6% | 100% | 100% | 77.8% | 21143 | 54.6s | 11 |

解读：单独编码 Skill 中 Practical ≈ Ponytail ≫ Superpowers ≫ grill-me。与 Ponytail 共装是本轮 Delivery 唯一 100%/100% build 组合。叠 Superpowers 常损伤 build 或正确率。

### 3.2 Decision（6 cases × 15 arms × 3 = 270 cells）

| Arm | Pass | Uncached median | Time median |
|---|---:|---:|---:|
| practical-current | **100%** | 9042 | 19.7s |
| grill-me | 83.3% | 6708 | 23.2s |
| ponytail | 0.0% | 8848 | 18.9s |
| superpowers | 0.0% | 7422 | 20.8s |
| 任意含 practical 的共装 | **100%** | 9526–14840 | 20.8–22.5s |
| ponytail+grill-me / superpowers+grill-me / 三技能含 grill-me（无 practical） | **100%** | 7938–11812 | 20.3–21.7s |
| ponytail+superpowers（无 grill-me） | 5.6% | 10238 | 18.7s |

解读：决策访谈契约依赖 grilling/grill-me 或 Practical Decision 模块。纯编码 Skill 几乎全部失败；一旦装上 grill-me 或 Practical，通过率回到 100%。

### 3.3 Debug（10 cases × 15 arms × 3 = 450 cells）

| Arm | Pass | Safe | Uncached median | Time median | Tools median |
|---|---:|---:|---:|---:|---:|
| practical-current | 96.7% | 96.7% | 8368 | 37.8s | 6.0 |
| ponytail | 93.3% | 93.3% | 7120 | 33.3s | 5.0 |
| superpowers | 80.0% | 80.0% | 23454 | 77.9s | 14.0 |
| grill-me | 26.7% | 26.7% | 7552 | 29.7s | 2.0 |
| practical+ponytail | 96.7% | 96.7% | 11204 | 38.2s | 6.0 |
| practical+superpowers | 93.3% | 93.3% | 12226 | 43.0s | 6.0 |
| practical+grill-me | 96.7% | 96.7% | 9942 | 38.5s | 6.0 |
| ponytail+grill-me | **100%** | 100% | 11362 | 37.9s | 5.0 |
| all four | **100%** | 100% | 15173 | 45.2s | 7.0 |
| 其他含 Superpowers 的组合 | 90–96.7% | 同左 | 更高 | 更高 | 更高 |

相对效率（quality-qualified）：Practical 对 Superpowers `E≈2.42`，Pareto **practical-dominates**。

### 3.4 Router / Behavior（仅 Practical）

| Suite | Arm | n | Pass |
|---|---|---:|---:|
| Router | practical-current | 84 | 96.4% |
| Behavior | practical-native | 30 | 100% |

## 4. 与当前项目的质量门控对比（scorecards）

规则：先要求 suite 通过率非劣（−3pp）、安全/build 不退步；再算相对效率 `E`（>1 表示 Practical 更省）。

### 单技能头对头

| Suite | Comparator | Status | Pareto | E |
|---|---|---|---|---:|
| Delivery | ponytail | qualified | comparator-dominates | 0.96 |
| Delivery | superpowers | not-qualified（build） | tradeoff | — |
| Delivery | grill-me | not-qualified（build） | tradeoff | — |
| Decision | grill-me | qualified | tradeoff | 1.01 |
| Decision | ponytail / superpowers | qualified | — | 质量碾压 |
| Debug | superpowers | qualified | practical-dominates | 2.42 |
| Debug | ponytail | qualified | tradeoff | 0.88 |
| Debug | grill-me | qualified | tradeoff | 0.73（质量碾压） |

### 关键共装

| 组合 | Delivery | Decision | Debug |
|---|---|---|---|
| practical+ponytail | 100% 且 build 100%；单独 Practical 对该组合 not-qualified（自身非劣失败） | 100%，Practical 成本更低并支配 | 96.7% 平手级 |
| practical+superpowers | 85.2%，差于单独 Practical | 100% | 93.3%，Practical 单独支配 |
| practical+grill-me | 96.3% 持平，成本更高 | 100% | 96.7% 持平 |
| 四技能全装 | 92.6% | 100% | **100%**，但更贵 |

## 5. 干扰效应摘要

1. **Superpowers 干扰 Delivery**：单独 51.9%；与 Ponytail 共装 63.0%；与 Practical 共装 85.2–92.6%，仍低于单独 Practical/Ponytail。
2. **grill-me 单独编码失效**：Delivery 18.5%、Debug 26.7%；但叠到 Practical 上大多不破坏通过率，只增加 token/时间。
3. **grill-me 修复 Decision**：任何含 grill-me 或 Practical 的 Decision arm 均为 100%；无访谈能力的编码 Skill 组合失败。
4. **全装并非全面最优**：四技能在 Debug 拉满通过率，在 Delivery 却因 build 掉到 77.8%。

## 6. 证据边界

- 公开回归矩阵，不是 held-out 泛化证明。
- Delivery 复用 Ponytail 任务与 scorer（Codex/Luna 适配），不代表 Claude 原版上游结果。
- Decision/Debug 是受控行为对比，不是 Matt Pocock / Superpowers 官方榜。
- Luna 采样有噪声；本轮 n=3 且稳定性门控通过，小差距应表述为「数值上领先/落后」。
- 共装通过 prompt 内联多 Skill，与真实插件生命周期不完全相同。
- 2026-08-28 Practical 与 Ponytail-only 对照跨 runner/跨运行，只能描述观察差异；严格头对头需在 v1.9 下重跑两个 arm。
- `STABLE` 只表示每个 cell n≥3 且无基础设施错误，不表示模型输出没有方差；共享 helper 压力测试仍观察到低频局部修复。

## 7. 发布产物

- 当前 Practical Delivery / Decision：[`delivery-decision-summary.json`](delivery-decision-summary.json)
- 当前 Practical Debug：[`debug-summary.json`](debug-summary.json)
- 当前 Practical Router / Behavior：[`router-behavior-summary.json`](router-behavior-summary.json)
- transfer 高压补测：[`transfer-stress-summary.json`](transfer-stress-summary.json)
- Practical vs Ponytail-only 详细报告：[`PRACTICAL_VS_PONYTAIL_ONLY_ZH.md`](PRACTICAL_VS_PONYTAIL_ONLY_ZH.md)
- 原始 transcripts、workspaces 与含本机路径的 manifest 保持本地，不进入公开仓库。

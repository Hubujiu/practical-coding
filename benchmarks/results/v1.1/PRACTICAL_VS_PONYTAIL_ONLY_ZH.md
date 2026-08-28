# Practical Coding v1.1 与 Ponytail-only 详细对比

日期：2026-08-28

模型：`gpt-5.6-luna` / `medium`，每个 case 运行 3 次。

## 1. 对比口径

本报告比较两个独立 Skill arm：

- **当前 Practical**：Delivery / Decision 来自 `practical-extreme-quality-v2-final-20260828`，Debug 来自 `practical-debug-v19-final2-20260828`。
- **Ponytail-only**：来自 Cursor 原始 `combo-standard-20260827-132513` 矩阵中的独立 `ponytail` arm，不含 Practical、Superpowers 或 grill-me。

两边使用相同模型、reasoning、case 名和 n=3，但不是严格 paired rerun：Ponytail 使用 runner v1.6；当前 Practical 的 Delivery / Decision 使用 v1.8，Debug 使用 v1.9。v1.8 起，前端模板在 agent 开始前准备锁文件依赖，使 agent 与最终 build 处于同一可执行环境；v1.9 还明确了 `trace-config-bool` 的共享配置格式。因此下列结果是**跨运行观察对比**，不能直接生成新的 qualified scorecard、Pareto 或因果结论。

## 2. 总表

| Suite | 当前 Practical | Ponytail-only | 观察差值 |
|---|---:|---:|---:|
| Delivery pass | **27/27（100%）** | 26/27（96.3%） | Practical +3.7pp |
| Delivery build | **9/9 build cells（100%）** | 8/9 build cells（88.9%） | Practical +11.1pp |
| Decision pass | **18/18（100%）** | 0/18（0%） | Practical +100pp |
| Debug pass | **29/30（96.7%）** | 28/30（93.3%） | Practical +3.3pp |
| Debug correct | 30/30（100%） | 30/30（100%） | 持平 |
| Debug safe | **29/30（96.7%）** | 28/30（93.3%） | Practical +3.3pp |

共同的 75 个 Delivery / Decision / Debug cell 中，当前 Practical 为 **74/75（98.7%）**，Ponytail-only 为 **54/75（72.0%）**。这个总差主要由 Decision 角色错配贡献；若只看两者都面向编码的 Delivery + Debug，当前 Practical 为 **56/57（98.2%）**，Ponytail-only 为 **54/57（94.7%）**。

## 3. 成本与产物

| Suite | Arm | Uncached median | Output median | Time median | Tools median | LOC median |
|---|---|---:|---:|---:|---:|---:|
| Delivery | 当前 Practical | 15,638 | 2,082 | 65.0s | 6 | 12 |
| Delivery | Ponytail-only | 15,672 | **1,786** | **47.9s** | 6 | 12 |
| Decision | 当前 Practical | **8,520** | 774 | 19.5s | 0 | — |
| Decision | Ponytail-only | 8,848 | **632.5** | **18.9s** | 0 | — |
| Debug | 当前 Practical | 9,795.5 | 1,459.5 | 41.9s | 6 | 1 |
| Debug | Ponytail-only | **7,120** | **1,204.5** | **33.3s** | **5** | 1 |

相对 Ponytail-only，当前 Practical：

- Delivery 的 uncached input 基本持平（−0.2%），output +16.6%，耗时 +35.8%，LOC 持平。
- Decision 的 uncached input −3.7%，output +22.4%，耗时 +3.4%。
- Debug 的 uncached input +37.6%，output +21.2%，耗时 +26.1%，工具调用 +20%，LOC 持平。

所以当前结果不是“Practical 全面支配 Ponytail”：Practical 的观察通过率更高，但 Ponytail-only 明显更快、更省输出，尤其在 Debug 中。

## 4. Delivery 逐 case

| Case | 当前 Practical | Ponytail-only | 解释 |
|---|---:|---:|---|
| safe-path | 3/3 | 3/3 | 持平 |
| critic-email | 3/3 | 3/3 | 持平 |
| cache | 3/3 | 3/3 | 持平 |
| reuse-slug | 3/3 | 3/3 | 持平 |
| reuse-money | 3/3 | 3/3 | 持平 |
| tmpl-fe-datepicker | 3/3，build 3/3 | 3/3，build 3/3 | 持平 |
| tmpl-fe-dropzone | 3/3，build 3/3 | 3/3，build 3/3 | 持平 |
| tmpl-fe-command | **3/3，build 3/3** | 2/3，build 2/3 | 唯一 Delivery 差异 |
| tmpl-be-count | 3/3 | 3/3 | 持平 |

Ponytail-only 唯一失败是 `tmpl-fe-command/r3`：行为 scorer 的 correct/safe 均通过，但 TypeScript build 因路由 path 类型与 React/DOM `KeyboardEvent` 类型错误失败。当前 Practical 在修复后的前置依赖环境中 3/3 build 通过。由于环境版本不同，这说明“当前 Practical + 当前 harness 已解决原失败”，但不能单独证明若把 Ponytail 放进 v1.9 它仍会失败。

## 5. Decision 逐 case

| Case | 当前 Practical | Ponytail-only |
|---|---:|---:|
| api-auth | 3/3 | 0/3 |
| service-boundary | 3/3 | 0/3 |
| event-delivery | 3/3 | 0/3 |
| api-migration | 3/3 | 0/3 |
| pagination-contract | 3/3 | 0/3 |
| file-storage | 3/3 | 0/3 |

这不是通用编码能力排名。Decision scorer 要求先识别未决约束、逐项收敛并在第二轮给出决定；Practical 有专门 Decision 路由，Ponytail 是编码交付 Skill，没有声明这一访谈契约。因此 100% 对 0% 主要表示**角色覆盖不同**。

## 6. Debug 逐 case

| Case | 当前 Practical | Ponytail-only | 差异机制 |
|---|---:|---:|---|
| security-path-containment | 3/3 | 3/3 | 持平 |
| security-tenant-authorization | 3/3 | 3/3 | 持平 |
| trace-amount | 3/3 | 3/3 | 持平 |
| trace-cache-tenant | 3/3 | 3/3 | 持平 |
| trace-config-bool | 3/3 | 3/3 | 持平；当前 runner 明确共享格式 |
| trace-duration-units | 3/3 | 3/3 | 持平 |
| trace-header-normalize | 3/3 | 3/3 | 持平 |
| trace-url-join | 3/3 | 3/3 | 持平 |
| trace-page-window | 2/3 | **3/3** | Practical 一次只修局部 caller，漏 sibling |
| trace-transfer | **3/3** | 1/3 | Ponytail 两次只修 `transfer()`，未修共享 `_debit()` |

两者都达到 correct 100%，差异全部来自 sibling caller 的安全轴。当前 Practical 在 `trace-transfer` 上明显更稳，但在最新 `trace-page-window` 中仍有一次同类低频局部修复。额外压力测试中，当前 Practical 的 transfer 为 9/10；因此应表述为“共享不变量命中率较高但仍有 Luna-medium 方差”，而不是宣称已彻底消除该错误。

## 7. 结论

1. **编码质量**：当前观察中 Practical 在 Delivery + Debug 为 56/57，Ponytail-only 为 54/57；Practical 数值领先 3.5pp。
2. **效率**：Ponytail-only 更快、更省 output，Debug 成本优势尤其明显。
3. **代码大小**：两边当前 Delivery LOC 中位数同为 12，旧报告中“Ponytail 代码更小”的结论不再适用于这次跨运行当前值。
4. **Decision**：Practical 完整覆盖，Ponytail-only 不覆盖；不应把这部分当成 Ponytail 编码质量缺陷。
5. **严格结论所需下一步**：在 runner v1.9 下同时运行 `practical-current` 与 `ponytail`，保持 case 顺序随机化或交替、n≥3，并重新生成 paired scorecard。未完成该步前，不能声称当前 Practical 严格统计支配 Ponytail。

## 8. 公开证据

- 当前 Practical Delivery / Decision：[`delivery-decision-summary.json`](delivery-decision-summary.json)
- 当前 Practical Debug v1.9：[`debug-summary.json`](debug-summary.json)
- 当前 Practical Router / Behavior：[`router-behavior-summary.json`](router-behavior-summary.json)
- Ponytail-only 数字保留自 2026-08-27 历史 combo 矩阵；完整解释见 [`REPORT_ZH.md`](REPORT_ZH.md)。

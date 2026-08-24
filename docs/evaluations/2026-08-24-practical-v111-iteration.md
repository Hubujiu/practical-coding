# Practical Coding v1.11 分析与前后对比

日期：2026-08-24（Asia/Shanghai）

## 结论

保留三处，撤销一处。

**保留**

1. Direct Path 两条路由负例：旁路 named artifact 不是 Implementation；已有仓库/平台默认不是 Decision。
2. `references/decision.md` 的 grilling 对齐：同一轮拆开独立前提；frontier 清空后停止，不再追问确认。
3. Decision 评测把对应 arm 的 `decision.md` 注入提示。grilling 全文内联，原先 `Do not use tools` 会让 Practical 的 Decision 模块根本进不了上下文。该修正对 v1.10 快照与 v1.11 同等生效。

**撤销**

Always-on Core 的 native-wrap 加句。它让 DatePicker/Command 变肥，并使 Rating 构建失败。按 v1.10 纪律，只撤回这一句。

相对 v1.10 快照，最终 v1.11 在本仓库 `run.ps1` 上：

- 路由 `48/48`，与 v1.10 打平（本 harness 已触顶，未能证明更高准确率，也没有回退）。
- Decision `12/12`，与 v1.10 打平，高于 grilling `10/12`；首轮问题覆盖略增，尤其 event-delivery 从 `1,1,2` 升到 `2,2,2`；第二轮全部 `q=0` 收敛。
- Debug `12/12`，与 v1.10 打平，高于 Superpowers `10/12`（config-bool 与 transfer 的 sibling/safe 失败）。
- 交付在撤回 Core 句后：正确/安全 `6/6`，通过率与 Ponytail、v1.10 同为 `5/6`（Command 构建在 n=1 上不稳定）。未宣称更接近 Ponytail 的 LOC。

因此 v1.11 被接受为：**Decision 行为更接近 grilling，且在本 runner 上超过 grilling 的收敛门禁；代码质量（debug 共享边界）继续超过 Superpowers；Core 没有新的 Ponytail 逼近。** 路由负例作为对 v1.10 论文失败模式的显式编码保留，但本 harness 给不出准确率增益。

## 基线与剩余缺口

v1.10 论文口径：路由 `27/30`、六个交付 `6/6`、LOC `380` vs Ponytail 历史 `306`、Decision 开始出现 whole-frontier。本仓库 `benchmarks/run.ps1` 与那套自定义 runner 不是同一套提示，所以本轮只拿 **冻结的 v1.10 Skill 快照** 做配对，不把论文里的 `27/30` 直接当本 runner 的前测。

| 目标 | 本 runner 上的 v1.10 快照 | 本轮要打的缺口 |
|---|---|---|
| 路由更准 | `48/48` | 论文里的 artifact→Implementation、default→Decision；本 harness 已触顶 |
| Core 逼近 Ponytail | 交付 n=1 总通过 `5/6` | DatePicker/Rating/Command 仍肥 |
| Decision 接近 grilling | `12/12` 机械通过 | API auth 问题偏少；要保证第二轮清空 frontier |
| 质量超过 Superpowers | Debug `12/12` | 保持共享边界修复，不引入 TDD 仪式 |

## 研究依据与假设

- [When Instructions Multiply](https://aclanthology.org/2025.findings-emnlp.896/)：不往 Core 堆新条目。路由负例写进 Direct Path；Core 只尝试给已有 native 规则加一句 stop condition。
- [What Prompts Don't Say](https://aclanthology.org/2026.findings-acl.441/)：DatePicker/Rating 变肥，假设是模型把“控件”理解成重建外观/键盘/状态。
- [Modeling Future Conversation Turns](https://arxiv.org/abs/2410.13788/)：用户答完当前 frontier 后再问确认，既偏离 grilling，也会让本仓库 scorer（第二轮 `questions == 0`）失败。

对照提交未改：Ponytail `2ed6c52c`，grilling `5b15a47f`，Superpowers `b36e0829`。

## 接受规则

1. 路由准确率不得下降。
2. 六个区分交付不得出现 correct/safe 回归；Core 若让 LOC 上升或构建变差，只撤 Core。
3. Decision：首轮每问有推荐、无提前实现；第二轮问题数为 0。相对 grilling 至少不在收敛上落后。
4. Debug：不得低于 v1.10，也不得低于 Superpowers。

## 环境

- Windows 11 `10.0.22621`；Python 3.13.14；Codex CLI `0.145.0`
- 模型 `gpt-5.6-luna`，reasoning `medium`
- Practical current：工作树 v1.11（Core wrap 句已撤）
- Practical previous：`docs/evaluations/snapshots/practical-v1.10`
- 命令入口：`benchmarks/run.ps1`（多 suite 时因 PowerShell `ValidateSet` 无法把 `decision,debug` 当数组，改用同等的 `python benchmarks/run_benchmarks.py --suite ...`）

产物：

```text
benchmark-results/v111-router-n3
benchmark-results/v111-decision-debug-n3
benchmark-results/v111-delivery-n1          # 含已撤销的 Core wrap
benchmark-results/v111-delivery-n1-core-reverted
```

## 1. 路由

16 个 case × 2 arm × 3 runs = 96 格。分类任务，不用工具。

| Arm | 通过 | 准确率 |
|---|---:|---:|
| v1.10 快照 | 48/48 | 100% |
| v1.11 | 48/48 | 100% |

`direct-artifact` 与 `direct-default` 两边都是 `3/3`。本 harness 的分类提示比 v1.10 论文自定义 runner 更干净，v1.10 快照已经触顶，所以 **负例没有测出准确率增益**。它们没有造成任何误判，作为对已知失败模式的显式约束保留。

## 2. Decision vs grilling

4 case × 3 arm × 3 runs = 36 格；每格两轮。Practical 两臂都注入各自的 `decision.md`。

| Arm | 机械通过 | 备注 |
|---|---:|---|
| grilling | 10/12 | `api-migration` 两次第二轮继续提问（q2=3, 2） |
| v1.10 快照 | 12/12 | 每问有推荐；全员 trade-off；第二轮 q=0 |
| v1.11 | 12/12 | 同上，且首轮覆盖略增 |

首轮实际问题数（人工按 `Q<n>` 标签，不是问号计数）：

| Case | grilling | v1.10 | v1.11 |
|---|---|---|---|
| api-auth | 5, 4, 5 | 2, 1, 3 | 2, 2, 3 |
| api-migration | 2, 2, 1 | 1, 2, 2 | 2, 1, 2 |
| event-delivery | 2, 1, 2 | 1, 1, 2 | **2, 2, 2** |
| service-boundary | 4, 5, 6 | 3, 3, 3 | 4, 3, 3 |

v1.11 仍比 grilling 克制（不会把整个设计树一次问完），但：

- 不再把 event-delivery 压成单问；
- 每问都有 Recommendation 和显式 trade-off（grilling 有几格 `has_tradeoff=False`）；
- 用户答完后停止，grilling 在 api-migration 上两次没有清空 frontier。

这是本轮对 “更接近 grill-me” 的可保留证据：不是复制 grilling 的提问量，而是复制 **whole-frontier + 每问推荐 + 空 frontier 即停**。Decision 评测时 SKILL.md 里仍带着后来撤销的 Core wrap 句；两臂机械通过率都是 100%，不把 Core 记成 Decision 的原因。

## 3. Debug vs Superpowers

4 case × 3 arm × 3 runs = 36 格。未改 `debugging.md`。

| Case | v1.11 根因+旁路 | v1.10 | Superpowers | v1.11 LOC 中位 |
|---|---:|---:|---:|---:|
| trace-amount | 3/3 | 3/3 | 3/3 | 10 |
| trace-config-bool | 3/3 | 3/3 | 2/3 | 1 |
| trace-transfer | 3/3 | 3/3 | 2/3 | 21 |
| trace-url-join | 3/3 | 3/3 | 3/3 | 1 |
| **合计** | **12/12** | **12/12** | **10/12** | — |

套件中位时间：v1.11 `39.1s`，v1.10 `44.5s`，Superpowers `78.8s`。套件中位 tokens：`80940` vs `88053` vs `245966`。

Superpowers 的两次失败是只修了被点名的 caller，sibling 路径仍错（`safe=0`）。Practical 继续把不变量放在共享 `parse_*` / `_debit` / `join_url` 边界。这是 “代码质量超过 Superpowers” 的本轮证据，不是 TDD 流程分。

## 4. Always-on Core vs Ponytail

六个区分任务，`n=1`。Ponytail scorer 的 `correct=1` 对 open task 主要表示写出了文件，所以 **构建通过率优先**。

### 4.1 含 Core wrap 句（已否决）

| Task | Ponytail LOC | v1.10 | v1.11+wrap | 构建 |
|---|---:|---:|---:|---|
| DatePicker | 9 | 18 | 30 | 三臂通过 |
| ColorPicker | 30 | 25 | 23 | 三臂通过 |
| Dropzone | 105 | 91 | 84 | 三臂通过 |
| Rating | 61 | 71 | 66 | **仅 v1.11 构建失败** |
| Command | 133 | 132 | 187 | 三臂都失败 |
| Count | 8 | 25 | 11 | 无前端构建 |
| 通过率 | 5/6 | 5/6 | **4/6** | |

通过率下降，DatePicker/Command 变肥。Core wrap 句撤销。

### 4.2 撤回 Core 句后的配对

| Task | Ponytail LOC | v1.10 | v1.11 最终 | 构建 |
|---|---:|---:|---:|---|
| DatePicker | 9 | 16 | 25 | 三臂通过 |
| ColorPicker | 23 | 25 | 21 | 三臂通过 |
| Dropzone | 80 | 76 | 82 | 三臂通过 |
| Rating | 80 | 67 | 72 | v1.10 失败；Ponytail 与 v1.11 通过 |
| Command | 142 | 154 | 163 | v1.11 与 Ponytail 失败；v1.10 通过 |
| Count | 9 | 25 | 13 | 无前端构建 |
| 通过率 | 5/6 | 5/6 | 5/6 | |
| 总 LOC | 343 | 363 | 376 | n=1 |

套件通过率打平。总 LOC 仍高于 Ponytail，也略高于这次 v1.10 重跑。Command 构建在两次 n=1 之间对调失败臂，不能当成稳定的 Skill 回归，也不能当成稳定的 Skill 胜利。

**不接受 “Core 更接近 Ponytail” 的宣称。** 下一次若还要打 DatePicker `25 vs 9`，需要比 “wrap native control” 更具体的失败样本（实际多写了哪些 props/类型/键盘层），而不是再给 Core 加一句抽象 stop condition。

## 去留决定

| 改动 | 数据 | 决定 |
|---|---|---|
| Direct Path：artifact ≠ Implementation，default ≠ Decision | 路由无回退，也无增益 | 保留 |
| Core：native wrap stop | 构建 4/6，DatePicker/Command 变肥 | **撤销** |
| decision.md：拆前提 + 空 frontier 即停 | 12/12，覆盖略增，grilling 10/12 | 保留 |
| harness：Decision 格注入 `decision.md` | 两臂同等；否则模块不可见 | 保留 |
| debugging.md | 未改；12/12 vs Superpowers 10/12 | 保持 |

## 下一轮（v1.12）只在有新失败样本时做

1. DatePicker：对着 v1.11 最终 `25 LOC` 与 Ponytail `9 LOC` 做 diff，只禁那一类多余层，不再写抽象 native 句。
2. Command：先把构建失败做成稳定回归（同一 TypeScript 错误），再谈 LOC。
3. 路由若还要超过 100%，需要比当前 16 格更难的负例，而不是继续改 SKILL.md。
4. Decision 若还要更接近 grilling 的提问量，只扩 `api-auth` 的独立前提清单，并继续用第二轮 `q=0` 卡住“问完不收敛”。

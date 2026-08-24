# Practical Coding v1.9 分层能力与交付物评测

日期：2026-08-24（Asia/Shanghai）

## 目标结构

Practical v1.9 明确分成三类可独立验收的能力：

1. Always-on core：吸收 Ponytail 的最小完整交付思想，所有编码任务默认生效；
2. Decision route：只在架构、API、依赖、数据模型或兼容性选择仍未解决时加载，目标是达到 Matt Pocock `grilling` 的事实先查、关键问题、逐项推荐与收敛能力；
3. Debug route：对已观察到但未诊断根因的故障加载，目标是用更小、更直接的根因修复获得更好的代码交付，不以 TDD/red-green 流程完整度计分。

三类 benchmark 分开计分，避免某个工作流的流程遵循率掩盖实际代码结果。

## 统一判据

按以下顺序评价：

1. 真实功能、build 或机械行为 scorer；
2. 安全、共享不变量、旁路调用和必要可达性；
3. 是否修改根因、是否引入回归或重复配置；
4. 源文件数、LOC、tokens 和 wall time。

不因写了测试、先红后绿、使用了某个 skill 名称、阶段是否齐全而加分。测试只作为能够证伪交付声明的证据。

环境延续同日 Codex 复现：Windows 11、Codex CLI 0.145.0、`gpt-5.6-luna`、reasoning `medium`，每格隔离 `CODEX_HOME`；Ponytail 固定提交 `2ed6c52c9d7e5e56942508591085fd45dea277d3`，Superpowers 固定提交 `b36e0829c6d0140e93cfef2ca599b1b07d4a7797`。

## 1. 基础能力 vs Ponytail

最终 v1.9 增加了一个通用约束：已有 element/framework/component prop 能声明式完成的行为，不用 ref、effect、镜像状态、手工同步或自定义事件 machinery 重写。

六个区分任务的 `n=1` 实际交付结果如下。ColorPicker 首轮因 fixture Git snapshot 未产生基线提交而被 scorer 错记为 0；文件实际存在且生产 build 通过，隔离重跑为 25 LOC、`correct=1`，下表使用有效重跑。Command 使用声明式规则后的定向重跑结果。

| Task | Practical v1.9 LOC | Ponytail LOC | 交付结果 |
|---|---:|---:|---|
| DatePicker | 18 | 11 | 两者交付；差异主要是类型与 JSX 展开格式 |
| ColorPicker | 25 | 24 | Practical 生产 build PASS；规模持平 |
| Dropzone | 103 | 83 | 两者交付；Practical 对直接拖放也执行 `accept` 过滤 |
| Rating | 76 | 65 | 两者交付 |
| Command Palette | 130 | 113 | 两者生产 build PASS |
| Count endpoint | 14 | 10 | 两者交付并留下 focused check |
| **合计** | **366** | **306** | Practical 多 19.6% |

Command Palette 的 17 LOC 差距不能直接解释为代码质量更差。Practical 的组件本体为 108 LOC，并将 Sidebar 原有导航提取为共享 `navigation.ts`，供 Sidebar 和 Palette 共用；Ponytail 在 Palette 中复制一份 Dashboard/Items/Settings/Admin 配置。Practical 修改 4 个源文件、总计 130 LOC，但消除了两份导航配置漂移风险。Ponytail 更短，Practical 的维护边界更一致。

合并有效定向重跑后，Practical 六任务约 1,858,702 tokens、625.4 秒；Ponytail约 1,274,055 tokens、446.2 秒。Practical 产物规模已接近，但推理/验证成本仍明显更高。这里是不同 `n=1` 定向单元的校准合并，不是正式统计值。

结论：基础交付物已从 v1.7 的 750 LOC 和初版 v1.8 的 503 LOC 收敛到 366 LOC，接近 Ponytail 的 306 LOC；在 ColorPicker 基本持平，在 Dropzone 语义和 Command 导航复用上有可说明的质量收益。仍不能声称 tokens/time 持平。

## 2. Decision route vs Matt Pocock `grilling`

Decision route 新增：

- 先从仓库/权威来源解决可发现事实；
- 维护 verified facts、constraints、assumptions、decisions 和 unresolved choices 的小账本；
- 只处理依赖已满足的 decision frontier；
- 只问会改变实现的 user-owned 决策；
- 每个问题必须明确给出 `Recommendation`、理由和 `Trade-off`；
- 已足够明确时不提问；便宜可逆的不确定性采用项目/平台默认；
- 无矛盾、重大选择已解决且剩余不确定性可逆时收敛。

两个第一轮案例：B2B API authentication 与 monolith/microservice service boundary。`n=1` 机械结果：

| Arm | 每案例问题数 | 每案例推荐数 | 显式 trade-off | 尝试实现 |
|---|---:|---:|---:|---:|
| Practical v1.9 | 1 / 1 | 1 / 1 | 2/2 | 0/2 |
| Matt `grilling` | 4 / 5 | 4 / 5 | 1/2（机械词面） | 0/2 |

人工核查：Practical 两例都先问最高影响的上游问题，并给出单一推荐、适用条件和最强替代；Matt 一轮展开整个当前 frontier 并逐项推荐。Practical 已达到核心推荐能力，同时更适合日常 coding 路由的低打扰需求。当前只验证第一轮，尚未验证多轮矛盾重开和最终 decision brief，不能称为完整替代专门 `grilling` skill。

## 3. Debug route vs Superpowers

任务使用 Ponytail 上游已有的确定性 shared-root-cause scorer：

- `trace-amount`：报告只点名 `invoice_total()`，真正根因在共享 `parse_amount()`；旁路 `tax_due()` 必须同时恢复；
- `trace-transfer`：报告点名 `transfer()`，但“不允许账户为负数”是共享状态不变量；`withdraw()` 也必须通过共享 `_debit()` 被保护。

同模型、同 prompt、同 seed、每臂 3 次。评分只看正确调用、旁路调用、LOC、tokens 和时间，不给测试文件或 TDD 流程加分。

### 金额解析

| Arm | 根因与旁路成功 | LOC 中位数 | tokens 中位数 | 时间中位数 | 写测试率 |
|---|---:|---:|---:|---:|---:|
| Practical v1.9 | 3/3 | 10 | 78,939 | 34.6s | 0/3 |
| Superpowers | 3/3 | 10 | 169,595 | 63.7s | 3/3 |

代码正确性和规模相同；Practical 用约 53.5% 更少 tokens、45.7% 更少时间完成。Superpowers 写测试不计加分，也没有因此得到更高功能分。

### 账户不变量

最初 Practical 只在 1/3 中修到共享 `_debit()`，Superpowers 为 0/3；两者多数运行都只给 `transfer()` 加 guard，未保护 `withdraw()`。轨迹揭示两个 Practical 路由问题：

1. 把“已知出错函数”误当成已知根因，跳过 debugging route；
2. 即使识别共享 helper，仍按报告中的函数名缩小范围，而没有按“账户绝不能为负数”的不变量划定范围。

v1.9 因此补充：报告症状不等于已诊断根因；修复范围按被破坏的 contract/invariant 确定；通用不变量应放在所有相关调用者经过的最窄共享 mutation/parsing boundary，并检查最近 sibling caller。

最终定向 `n=3`：

| Arm | 根因与旁路成功 | LOC 中位数 | tokens 中位数 | 时间中位数 |
|---|---:|---:|---:|---:|
| Practical v1.9 最终 | 3/3 | 22 | 123,593 | 67.7s |
| Superpowers 固定对照 | 0/3 | 19 | 233,262 | 84.6s |

Practical 多 3 LOC，但三个交付都把 guard 放在 `_debit()`，并保护 `withdraw()`；部分运行还保护负 deposit。Superpowers 三次都只修改 `transfer()`。因此按实际代码正确性，Practical 明显更有效；按资源也少 47.0% tokens、少 20.0% 时间。最终 Practical 是规则迭代后的定向重跑，Superpowers 来自同日同模型同 harness 的固定对照，不是重新随机配对的一轮，正式发布数字仍应重新做 paired repeated run。

## 当前结论

- Always-on core 已具备 Ponytail 式基础能力，六个区分任务 LOC 差距收窄到 19.6%；部分额外代码对应真实语义或消除重复配置，不应机械删除。
- Decision route 在两个第一轮案例中达到“关键问题 + 每问推荐 + trade-off”的核心效果，并比 Matt `grilling` 更克制；完整多轮能力尚未证明。
- Debug route 在两个共享根因任务上最终为 6/6，Superpowers 为 3/6；Practical 的优势来自正确修复共享边界和更低 tokens/time，而不是 TDD 流程缺失或齐全。
- 仍需扩大题集：基础层至少 3 次配对；decision 增加多轮矛盾/收敛；debug 增加构建、并发、配置传播、跨组件和回归任务。只有这些完成后才能声称跨类别稳定优于对应专项 Skill。

## 原始证据

```text
D:\Workspace\AiProjects\practical-coding-competitor-benchmark-20260824\
├── decision_route_compare.py
├── decision-practical-v19-vs-grilling-n1-template\
└── ponytail-codex-repro\
    ├── practical-v19-vs-ponytail-delivery-n1\
    ├── practical-v19-colorpicker-rerun-n1\
    ├── practical-v19-command-declarative-n1\
    ├── debug-practical-v19-vs-superpowers-n3\
    ├── debug-practical-v19-routefix-n3\
    ├── debug-practical-v19-shared-boundary-n3\
    └── debug-practical-v19-invariant-scope-n3\
```

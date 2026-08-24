# Practical Coding、Ponytail、Superpowers 与 Grill Me 同环境对比

日期：2026-08-24

性质：校准级评测，不是统计充分的通用排行榜

## 1. 结论

在本次固定环境、固定模型、相同任务与相同隐藏验收器下，Practical Coding 的通用编码综合表现最好：

- 两类编码任务共 6 次，Practical Coding 通过 5 次，与无 Skill 基线的 5/6 并列第一；
- Ponytail 与 Superpowers 均为 4/6；
- 简单任务中，Practical Coding 3/3 通过，耗时中位数最低，且每次都保持 Direct Path、零 reference、零 worker；
- 高风险 SQLite 任务中，Practical Coding 为 2/3，与 baseline 和 Ponytail 持平，高于 Superpowers 的 1/3；
- Practical Coding 在高风险任务中仍出现过一次 Windows SQLite 句柄未关闭，不能声称风险已经消除；
- Matt Pocock 的 `grill-me` 在专业需求访谈场景明显更强，但它解决的是“穷尽决策树并逐题推荐”，不是通用编码执行，因此不构成 Practical Coding 的编码退化。

本次结果支持以下有限结论：

> 在所测的 Codex/Luna 编码场景中，Practical Coding 没有使整体效果变差，并在成功率、简单任务速度和相对资源成本之间取得了三个 Coding Skill 中最好的平衡。

本次结果不支持“Practical Coding 在所有模型、仓库和任务上都优于其他 Skill”的外推。

## 2. 被测版本

| 项目 | 版本或提交 | 角色 |
|---|---|---|
| Practical Coding | `75d501380bc4c9c26de8b81f8e4fc320717b0141` | 被测项目 |
| [Ponytail](https://github.com/DietrichGebert/ponytail) | `4.9.0` / `2ed6c52c9d7e5e56942508591085fd45dea277d3` | Coding Skill 对照 |
| [Superpowers](https://github.com/obra/superpowers) | `6.3.0` / `b36e0829c6d0140e93cfef2ca599b1b07d4a7797` | Coding Skill 对照 |
| [Matt Pocock skills](https://github.com/mattpocock/skills) | `1.2.3` / `5b15a47f2d7150f545fbcacbfe381787fc0230dc` | `grill-me` 专项对照 |
| [liq22/grill-me](https://github.com/liq22/grill-me) | `2.0.0` / `a4023fff80e76bb43da3f6a2c6a7c8c797172d58` | 同名项目旁证，不进入主比较 |

选择 Matt Pocock 版本作为 `grill-me` 主对照，是因为本项目 README 明确致谢的是 Matt Pocock 的 Skill 集合。`liq22/grill-me` 虽然带有 eval JSON，但不能与 Matt 版本混为同一实现。

## 3. 测试环境

| 项目 | 固定值 |
|---|---|
| 操作系统 | Microsoft Windows NT `10.0.22621.0` |
| Shell | PowerShell `7.6.4` |
| Codex CLI | `0.145.0` |
| 模型 | `gpt-5.6-luna` |
| Reasoning effort | `medium` |
| Git | `2.45.1.windows.1` |
| Node.js | `22.23.1` |
| npm | `10.9.8` |
| Python | `3.13.14` |
| pandas | `2.3.0` |
| Bun | `1.3.10` |
| 编排 Shell | 原生 PowerShell；需要 Bash 的上游脚本使用 Git Bash `5.2.26` |

每个被测 agent 使用相同设置：

- `--ignore-user-config`；
- 禁用 plugins、skill search、memories 和 apps；
- 相同模型、reasoning effort、权限、超时和依赖缓存；
- 每次从相同 fixture 创建新的 Git 仓库；
- fixture 内显式关闭 Codebase Memory；
- 同一次 repetition 内相邻执行 `baseline → practical → ponytail → superpowers`，降低服务状态、缓存和时间漂移造成的伪差异；
- 使用相同隐藏行为与安全验收器；
- 保存原始 JSONL、stderr、Skill 快照、最终 diff、线程 telemetry 和验收结果。

Practical Coding 工作区原有的 `README.md`、`agents/openai.yaml` 未提交修改没有进入被测行为提示；实际被测的是固定提交对应的根 Skill、AGENTS 约束和按需 reference。

## 4. 对照组注入方式

| Arm | 注入方式 |
|---|---|
| baseline | 不注入任何被测 Skill，使用普通 coding judgment |
| practical | 在初始提示中注入 Practical Coding 根 `SKILL.md`，reference 只允许按事件读取 |
| ponytail | 在初始提示中注入 Ponytail 的 `skills/ponytail/SKILL.md` |
| superpowers | 注入 `using-superpowers`，并把完整 skills 目录作为只读文件暴露给 headless Codex |

Superpowers 的 Skill tool 语义在 headless adapter 中映射为读取对应目录下的 `SKILL.md`。四个 arm 都禁用了真实插件生命周期，因此没有单独让某一组享受插件注入、hook 或用户全局配置。

## 5. 编码任务与验收

### 5.1 Direct feature flag

任务要求在一个小型 Python 模块中增加 `new_dashboard` feature flag：

- 默认值为 `False`；
- 读取匹配的全大写环境变量；
- 接受常用真假字符串；
- 大小写不敏感；
- 输入两侧空格不影响解析；
- 未知值回落到默认值；
- 不引入 dependency 或 framework。

该任务用于检查 Direct Path、过度工程、字符串边界和简单任务成本。

### 5.2 Durable idempotency

任务要求实现 SQLite 支持的持久幂等事件处理，隐藏验收覆盖：

- 首次调用执行 action，重复 event id 返回持久结果；
- 失败后可以重试；
- 进程重建后仍保持幂等；
- 多实例并发不能重复执行 action；
- 结果可持久化；
- Windows 临时目录清理成功，不能遗留 SQLite 文件句柄。

该任务用于检查重大实现选择、并发、事务、持久化和资源生命周期。

## 6. 汇总结果

中位数包含失败尝试，因为失败同样消耗时间和 tokens。

| 任务 | Arm | 通过率 | 耗时中位数 | Tokens 中位数 | Tool calls 中位数 | 新增 LOC 中位数 |
|---|---:|---:|---:|---:|---:|---:|
| Direct feature flag | baseline | 3/3 | 41.6s | 58,794 | 4 | 18 |
| Direct feature flag | **Practical** | **3/3** | **38.8s** | 63,322 | **4** | 16 |
| Direct feature flag | Ponytail | 2/3 | 64.4s | 128,387 | 8 | **8** |
| Direct feature flag | Superpowers | 3/3 | 48.4s | 86,869 | 5 | 17 |
| Durable idempotency | baseline | 2/3 | **82.4s** | **99,655** | **6** | 49 |
| Durable idempotency | **Practical** | **2/3** | 90.6s | 103,815 | **6** | 39 |
| Durable idempotency | Ponytail | **2/3** | **90.0s** | 122,810 | 7 | **35** |
| Durable idempotency | Superpowers | 1/3 | 91.6s | 131,270 | 7 | 43 |

跨两个任务的总成功率：

| Arm | 成功 | 失败 | 成功率 |
|---|---:|---:|---:|
| baseline | 5 | 1 | 83.3% |
| **Practical** | **5** | **1** | **83.3%** |
| Ponytail | 4 | 2 | 66.7% |
| Superpowers | 4 | 2 | 66.7% |

### 6.1 结果解读

- Practical 在简单任务成功率与 baseline、Superpowers 相同，并且耗时最低；
- Practical 简单任务比 baseline 多约 7.7% tokens，但明显少于 Ponytail 和 Superpowers；
- Practical 复杂任务与 baseline、Ponytail 成功率相同，高于 Superpowers；
- Practical 复杂任务比 baseline 慢约 10%，tokens 多约 4%，因此不是每个单项都第一；
- Practical 复杂任务比 Ponytail、Superpowers 使用更少 tokens 和 tool calls；
- Ponytail 的新增代码最少，但最小 diff 没有保证最好的行为或资源安全；
- 综合正确性、速度、资源和流程克制，本次编码对比中 Practical 最好，但证据仍是小样本校准。

## 7. 24 条逐次记录

### 7.1 Direct feature flag

| Rep | Arm | Pass | Seconds | Tokens | Calls | Files | +LOC | -LOC | Error | Refs | Workers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|
| 1 | baseline | yes | 53.7 | 85,128 | 6 | 1 | 23 | 3 | — | 0 | 0 |
| 1 | practical | yes | 43.1 | 76,398 | 5 | 1 | 15 | 3 | — | 0 | 0 |
| 1 | ponytail | yes | 64.4 | 128,387 | 8 | 1 | 9 | 3 | — | 3 | 0 |
| 1 | superpowers | yes | 47.6 | 86,869 | 5 | 1 | 17 | 3 | — | 3 | 0 |
| 2 | baseline | yes | 41.6 | 58,794 | 4 | 1 | 18 | 3 | — | 0 | 0 |
| 2 | practical | yes | 38.8 | 63,322 | 4 | 1 | 16 | 5 | — | 1 | 0 |
| 2 | ponytail | **no** | 72.5 | 159,227 | 10 | 1 | 8 | 3 | `AssertionError` | 2 | 0 |
| 2 | superpowers | yes | 48.4 | 85,242 | 5 | 1 | 16 | 5 | — | 3 | 0 |
| 3 | baseline | yes | 35.0 | 58,523 | 4 | 1 | 18 | 3 | — | 0 | 0 |
| 3 | practical | yes | 36.8 | 62,945 | 4 | 1 | 19 | 3 | — | 0 | 0 |
| 3 | ponytail | yes | 59.3 | 111,205 | 7 | 1 | 5 | 3 | — | 1 | 0 |
| 3 | superpowers | yes | 60.6 | 117,439 | 7 | 1 | 18 | 3 | — | 3 | 0 |

### 7.2 Durable idempotency

| Rep | Arm | Pass | Seconds | Tokens | Calls | Files | +LOC | -LOC | Error | Refs | Workers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|
| 1 | baseline | yes | 66.0 | 77,374 | 5 | 1 | 49 | 7 | — | 0 | 0 |
| 1 | practical | yes | 90.6 | 88,021 | 5 | 2 | 41 | 7 | — | 2 | 0 |
| 1 | ponytail | **no** | 90.0 | 119,419 | 7 | 2 | 35 | 7 | `PermissionError` | 1 | 0 |
| 1 | superpowers | yes | 102.9 | 167,799 | 9 | 2 | 39 | 7 | — | 2 | 0 |
| 2 | baseline | **no** | 97.3 | 110,090 | 7 | 1 | 49 | 7 | `PermissionError` | 0 | 0 |
| 2 | practical | yes | 85.6 | 103,815 | 6 | 1 | 38 | 7 | — | 2 | 0 |
| 2 | ponytail | yes | 73.8 | 122,810 | 7 | 2 | 25 | 7 | — | 1 | 0 |
| 2 | superpowers | **no** | 91.6 | 131,270 | 7 | 1 | 43 | 7 | `PermissionError` | 2 | 0 |
| 3 | baseline | yes | 82.4 | 99,655 | 6 | 1 | 78 | 6 | — | 0 | 0 |
| 3 | practical | **no** | 104.3 | 139,800 | 8 | 1 | 39 | 7 | `PermissionError` | 3 | 0 |
| 3 | ponytail | yes | 93.6 | 194,644 | 11 | 2 | 37 | 7 | — | 1 | 0 |
| 3 | superpowers | **no** | 75.3 | 89,162 | 5 | 1 | 52 | 7 | `PermissionError` | 2 | 0 |

`Refs` 表示最终报告中声明读取的 instruction/reference 文件数量，不是源码文件读取次数。`Workers` 为实际派发的子代理数。

## 8. 失败分析

### 8.1 Ponytail 简单任务

失败实现对值调用了 `lower()`，但没有先 `strip()`。因此：

- `"TRUE"` 可以通过；
- `" yes "` 被解析为 `" yes "`，不在真值集合中；
- 隐藏验收以 `AssertionError` 失败。

这说明最少 LOC 不是充分质量指标。

### 8.2 SQLite 句柄泄漏

失败样本分别来自 baseline、Practical、Ponytail 和 Superpowers。共同模式是：

- 构造函数创建并持有 `sqlite3.Connection`；
- 类提供 `close()`，但调用契约没有要求使用者必须显式关闭；
- 测试创建临时数据库后直接释放临时目录；
- Windows 不允许删除仍被进程持有的 SQLite 文件；
- `TemporaryDirectory` 清理产生 `PermissionError / WinError 32`。

通过样本通常在单次 `process()` 内创建连接，并在 `finally` 或 context manager 中关闭。该差异属于外部可观察的资源生命周期正确性，不只是风格偏好。

Practical 只在 1/3 复杂样本出现该失败，因此当前 Skill 降低了但没有消除模型选择长连接实现的概率。由于其他 arm 同样出现，证据不支持“Practical 引入了独有回归”。

## 9. 上游声明测试与本机结果

### 9.1 Ponytail

声明的静态/基础设施门禁：

```powershell
npm test --prefix D:\Workspace\AiProjects\practical-coding-competitor-benchmark-20260824\sources\ponytail
```

结果：

- root：84/84；
- Pi extension：23/23；
- Ponytail MCP：3/3；
- 合计：110/110，通过。

Ponytail 还声明了两类效果基准：

- Promptfoo single-shot：多模型、多任务、多 repetition，测量 LOC、tokens、成本与延迟；
- Agentic benchmark：真实 Claude Code session、固定 FastAPI + React 仓库、12 个功能任务和安全任务。

本机条件满足 Node、Python 和 pandas，但完整 agentic 方法是 Claude 专属。离线 completion self-test 通过；native Windows self-test 在临时目录清理时触发 WinError。没有把未运行的付费 Claude benchmark 记为通过。

### 9.2 Superpowers

本机已执行的主要门禁：

| 检查 | 结果 |
|---|---|
| Pi extension | 6/6 passed |
| Hermes pytest | 19/19 passed |
| Brainstorm server | 120 passed、2 skipped、1 failed |
| Session-start hooks | passed |
| Systematic-debugging polluter test | passed |
| Codex marketplace manifest | passed |
| Devin manifest | passed |
| Kimi manifest | passed |
| Antigravity mapping | passed |
| Shell-lint self-test | passed |

Brainstorm server 剩余失败为 Windows 主机上的 IPv6 startup URL lifecycle 检查。两个 skipped 是当前 Windows 权限不允许创建测试所需 symlink。

未通过或未能忠实执行的其他 shell 门禁：

- writing-skills graph render：缺少 Graphviz；
- version bump：缺少 `jq`；
- Codex packaging：Git Bash/MSYS 将绝对路径转换成 Python 无法识别的 `/d/...`；
- OpenCode plugin loading：Windows/Git Bash symlink 行为不符合测试假设；
- Codex sync：同类 POSIX/路径依赖导致断言失败。

Superpowers 当前的完整行为评测位于外部 `prime-radiant-inc/superpowers-evals`。本机没有忠实运行，原因是：

- Bun `1.3.10` 低于其声明的 `>=1.3.13`；
- checkout 遇到 Windows 最大路径限制；
- 文档化的完整 appliance 路径面向 Linux/KVM，而不是 native PowerShell。

### 9.3 Matt Pocock `grill-me`

Matt 当前实现中：

- `grill-me` 只是别名；
- 实际行为在 `grilling`；
- package/plugin 版本一致性检查通过；
- 仓库没有声明 grill-specific 行为测试、benchmark 或 smoke runner。

因此新增两个相同 Luna 环境的一轮 smoke，而没有把自定义 smoke 冒充上游测试。

### 9.4 liq22 同名实现

`liq22/grill-me` 自带 `evals/evals.json` 与 `eval_queries.json`，并声明一致性 validator。本机运行结果：

```text
Validation passed: Grill Me skill v2.0.0 is internally consistent.
```

它没有进入主 grill 对比，因为它不是本项目致谢的 Matt Pocock 实现。

## 10. Grill Me 专项 smoke

固定模型与禁用项与编码对比相同。每个 arm 只生成第一轮问题，不调用工具、不修改文件。

### 10.1 任务

1. 付费 AI 研究助手：为研究生总结论文并构建个人知识图谱；
2. 一个季度把 monolith 替换为六个 microservices，并在访谈后自动重写仓库。

### 10.2 结果

| Case | Arm | 问题数 | 每题推荐 | 是否执行代码/改文件 |
|---|---|---:|---:|---:|
| Startup | baseline | 8 | no | no |
| Startup | Practical | 7 | no | no |
| Startup | Matt grill-me | 6 | **yes** | no |
| Migration | baseline | 10 | no | no |
| Migration | Practical | 7 | no | no |
| Migration | Matt grill-me | 8 | **yes** | no |

三组都能提出有意义的问题。Practical 并不“缺少澄清”，更不是“完全不澄清”。差异是：

- Practical 的目标是获得足够信息，以便安全、适量地完成编码任务；
- 它当前没有 `grill` 或穷尽式访谈路由事件；
- 没有专门 Skill 时，普通模型能力仍会提出澄清问题；
- Matt `grilling` 明确要求构建 design tree、计算当前 frontier、整轮提出所有已解锁问题，并为每个问题附上推荐答案；
- 因而 Matt 在专业 grilling 输出结构上明显更强，这是预期的领域专长。

不应把完整 grilling 流程加入 Practical 的默认路径。否则普通编码任务可能增加不必要的提问和前置流程。更合理的共存方式是：用户明确要求 “grill me” 时由专门的 `grill-me` 接管，Practical 继续负责后续编码决策与执行。

本次只测试独立 arm，没有测试 Practical 与 Matt `grill-me` 同时加载时的交互，因此不能据此声称 Practical 会增强或抑制另一个 Skill。

## 11. 复现命令

编码对比：

```powershell
python D:\Workspace\AiProjects\practical-coding-competitor-benchmark-20260824\compare.py `
  --task direct-feature-flag `
  --task decision-durable-idempotency `
  --repetitions 3 `
  --output D:\Workspace\AiProjects\practical-coding-competitor-benchmark-20260824\runs-reproduction `
  --timeout 900
```

本次原始执行分为 `runs-v1` 的一次 repetition 和 `runs-v2` 的两次 repetition；表格把它们顺序合并为 Rep 1–3。

Grill smoke：

```powershell
python D:\Workspace\AiProjects\practical-coding-competitor-benchmark-20260824\grill_compare.py
```

注意：`grill_compare.py` 的默认输出目录是固定的；重复运行前应选择新的输出目录或复制 runner 后修改输出路径，不能覆盖原始证据。

## 12. 原始产物

评测产物位于：

```text
D:\Workspace\AiProjects\practical-coding-competitor-benchmark-20260824\
├── RESULTS.md
├── compare.py
├── grill_compare.py
├── runs-v1\
├── runs-v2\
├── grill-runs-v1\
└── sources\
```

其中：

- `runs-v1/`、`runs-v2/`：编码任务原始 JSONL、stderr、prompt、Skill snapshot、workspace、diff、telemetry 和 evaluator 结果；
- `grill-runs-v1/`：访谈 prompt、原始 JSONL 与最终回答；
- `sources/`：固定提交的上游 checkout；
- 外部 `RESULTS.md`：较短的执行摘要；
- 本文档：仓库内的完整、可审阅记录。

## 13. 证据边界

- 每格只有 3 次，属于校准证据，不是统计充分的结论；
- 编码对比只覆盖一个简单任务和一个高风险持久化任务；
- 后续已经在 Codex/Luna 环境移植并运行 Ponytail 的 7 个安全任务、12 个 template 任务、两个 LLM judge 和 3 个行为 gate；详见 `2026-08-24-upstream-benchmarks-codex-reproduction.md`；
- 没有完整运行 Superpowers 外部 Quorum suite；
- Superpowers 使用 headless Codex adapter，不包含其真实插件 hook 生命周期；
- Grill 只检查第一轮，没有运行到 design tree frontier 清空；
- 没有测试多个 Skill 同时激活的交互；
- 时间和 token 会受到模型服务与缓存波动影响，因此优先看隐藏验收成功率，再看资源指标；
- 结果只直接适用于本·文固定的 Codex/Luna/Windows 环境。

后续若要形成更强结论，应至少：

1. 增加不同任务类别；
2. 每个随机单元运行至少 5 次，正式主张按项目现有政策使用至少 3 个有效配对并计算置信区间；
3. 加入 Practical + Ponytail、Practical + Superpowers、Practical + grill-me 的共存 arm；
4. 在 Linux 上忠实运行 Superpowers Quorum；
5. 在其声明的 Claude 环境复现 Ponytail agentic benchmark；
6. 把 SQLite 资源生命周期作为独立回归任务继续验证。

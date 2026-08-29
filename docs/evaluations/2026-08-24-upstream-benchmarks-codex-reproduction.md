# 上游 Benchmarks 的 Codex 环境复现

日期：2026-08-24（Asia/Shanghai）

本文回答两个问题：

1. Ponytail 仓库中的 `benchmarks/` 能否在 Codex 环境复现；
2. Practical Coding 融合或致谢的其他项目，有哪些声明评测可在同一环境复跑，哪些只能验证基础设施，哪些当前没有行为 benchmark。

结论先行：Ponytail 的主要 agentic 任务、确定性 scorer、完整度 judge、过度实现 judge 和行为 gate 均已移植到 Codex 并实际运行。它不是原 Claude 数字的复刻，而是保留任务、fixture、arms、rubric 和评分逻辑，仅替换 agent/judge backend 后得到的 Codex 复现。Superpowers 的官方 Codex adapter 测试通过，但 live Quorum 场景被当前 Windows 宿主的 Linux/Gauntlet 前置条件阻塞。Matt Pocock `grilling` 没有声明行为 benchmark；Codebase Memory 当前文档是未完成的评测计划，不存在可直接运行的 159-language runner。

## 1. 固定版本

| 项目 | 提交 / 版本 |
|---|---|
| Practical Coding | `75d501380bc4c9c26de8b81f8e4fc320717b0141` |
| DietrichGebert/ponytail | `2ed6c52c9d7e5e56942508591085fd45dea277d3`, v4.9.0 |
| full-stack-fastapi-template fixture | `cd83fc10ca20393e9ee50e3005e170c6929e047e` |
| obra/superpowers | `b36e0829c6d0140e93cfef2ca599b1b07d4a7797`, v6.3.0 |
| prime-radiant-inc/superpowers-evals | `339779f179d69ac468326d281a9e54f198aabf8d` |
| mattpocock/skills | `5b15a47f2d7150f545fbcacbfe381787fc0230dc`, v1.2.3 |
| DeusData/codebase-memory-mcp | `010569fa6ce1bc5d6430f858129243ea1a2e3fd5` |
| agentskills/agentskills | `69ef37e9424c0a7ea9dd2293b559e43ec8176379` |

上述外部 checkout 在取证时均为 clean；上游 HEAD 在 2026-08-24 通过 `git ls-remote` 复核一致。

## 2. Codex 测试环境

| 项 | 值 |
|---|---|
| OS | Windows 11 Pro `10.0.22621`, x64 |
| CPU / RAM | Intel Core i9-12900HX；16 核 / 24 逻辑处理器；约 34 GB RAM |
| Shell | PowerShell 7.6.4 |
| Codex CLI | 0.145.0 |
| Agent / judge model | `gpt-5.6-luna` |
| Reasoning | `medium` |
| Node / npm | 22.23.1 / 10.9.8 |
| Python | 3.13.14；默认 locale encoding `cp936` |
| Git | 2.45.1.windows.1 |

每个模型单元使用隔离的 `CODEX_HOME`，并禁用用户配置中的 plugins、skill search、memories、apps 和 multi-agent。Agentic 单元保留文件与 shell 工具；单次行为与 LLM judge 单元禁用 shell 工具。所有 arm 使用同一模型、reasoning、权限、任务、fixture 和超时。

本次是 `n=1` 的完整任务面复习，不是统计充分的正式发布数字。原 Ponytail agentic 报告使用 Claude Haiku、每格 4 次；single-shot 报告使用每格 10 次。两者不能与本次数值直接横比。

## 3. Ponytail agentic benchmark：移植边界

直接复用上游：

- `TASKS`、seed、public-repo fixture 和固定提交；
- 7 个确定性安全任务；
- 12 个 FastAPI template LOC 任务；
- Baseline、Caveman、Ponytail、YAGNI one-liner 四个原 arm；
- `score_workspace()`、LOC / files / tests 统计和 aggregate；
- over-engineering 与 completeness 的原始 rubric、参考对、自测排序门和 JSON parser。

新增两个对比 arm：Practical、Superpowers。

替换项：

- Claude Code launcher → Codex CLI launcher；
- Claude telemetry → Codex JSONL 与 `state_5.sqlite` telemetry adapter；
- Claude Sonnet judge → tool-free Codex/Luna judge；
- skill plugin 注入 → 固定提交 `SKILL.md` 的显式 headless 注入。

Windows 兼容修正：上游 scorer selftest 在 native Windows 上会因 SQLite 连接尚未释放而让临时目录清理报 `WinError 32`。Codex adapter 使用持久自测目录并在单元间 `gc.collect()`；没有改 scorer 判断。

Judge 输入修正：上游 `source_text()` 注释称只发送“agent 写的 source files”，实际却遍历整个复制的 FastAPI fixture。单个 workspace 达约 210 万字符，Codex 无法返回答案。由于上游 runner 在执行前已建立 Git snapshot，Codex adapter 改用 `git status --porcelain -z`，只发送代理新增或修改的非测试源文件。示例输入从 2,102,421 字符降至 4,387 字符并恢复有效 JSON。rubric、任务与解析未改，但这是明确的方法偏差，也暴露了上游 judge plumbing 的上下文缺陷。

## 4. 确定性 scorer 自测

Codex adapter 对上游所有非 open task 的 good/bad 参考对运行了 24 个判定：

```text
24/24 passed
```

覆盖 `todo-null`、7 个安全任务、两个 reuse 和两个 trace 质量任务。每个 good 必须 `correct=1, safe=1`，每个 bad 必须在声明的主轴上失败。

Ponytail single-shot 的本地 scorer 测试：

```text
benchmarks/correctness.test.js  4/4 passed
benchmarks/loc.test.js          6/6 passed
tests/behavior.test.js          8/8 passed
```

## 5. 7 个安全任务结果

任务：`safe-path`、`critic-email`、`rate-limit`、`sql-user`、`auth-token`、`csv-sum`、`cache`。

| Arm | correct | safe | LOC 总和 | tokens 总和 | wall time 总和 | 写测试的任务数 |
|---|---:|---:|---:|---:|---:|---:|
| Baseline | 7/7 | 7/7 | 135 | 389,710 | 282.8s | 1 |
| Caveman | 7/7 | 7/7 | 151 | 416,628 | 273.3s | 0 |
| Ponytail | 7/7 | 7/7 | 91 | 376,361 | 234.1s | 0 |
| Practical | 7/7 | 7/7 | 110 | 388,283 | 252.4s | 0 |
| Superpowers | 6/7 | 6/7 | 98 | 684,904 | 321.6s | 2 |
| YAGNI one-liner | 7/7 | 7/7 | 54 | 315,372 | 220.7s | 0 |

相对 Baseline，Ponytail LOC 减少 32.6%，Practical 减少 18.5%；两者都保持本轮 7/7。YAGNI 更短且本轮也 7/7，但 `n=1` 不足以推翻上游多次运行中“一行提示可能丢 guard”的风险结论。

Superpowers 的唯一失败是 `csv-sum`。它没有实现函数，而是按 `brainstorming` 的 bounded path 提出设计并等待用户批准：

```python
def sum_amount(path):
    """Read the CSV at path and return the sum of its 'amount' column."""
    raise NotImplementedError
```

这是一次明确的任务协议冲突：单轮 autonomous benchmark 没有后续批准回合，而 Superpowers 工作流把批准当成实现前硬门。不能据此说它不会实现 CSV；可以说它在这种单轮协议下没有完成任务。

## 6. 12 个 FastAPI template 任务

前端：datepicker、colorpicker、command palette、dropzone、wizard、rating。

后端：duplicate、search、count、archive、bulk delete、CSV export。

上游 open-task 的 `correct=1` 主要表示成功写入，不等于功能已完整；因此必须与 completeness judge 一起看。

| Arm | 上游交付检查 | LOC 总和 | tokens 总和 | wall time 总和 | 写测试任务数 |
|---|---:|---:|---:|---:|---:|
| Baseline | 12/12 | 1,296 | 2,551,739 | 1,097.7s | 7 |
| Caveman | 12/12 | 1,442 | 2,103,176 | 1,071.7s | 6 |
| Ponytail | 12/12 | 682 | 1,991,243 | 892.7s | 7 |
| Practical | 12/12 | 1,116 | 2,234,813 | 1,127.8s | 7 |
| Superpowers | 0/12 | 0 | 1,244,750 | 490.5s | 0 |
| YAGNI one-liner | 12/12 | 423 | 1,883,145 | 817.4s | 7 |

相对 Baseline：

| Arm | LOC 变化 | tokens 变化 | wall time 变化 |
|---|---:|---:|---:|
| Ponytail | -47.4% | -22.0% | -18.7% |
| Practical | -13.9% | -12.4% | +2.7% |
| YAGNI one-liner | -67.4% | -26.2% | -25.5% |
| Caveman | +11.3% | -17.6% | -2.4% |

Superpowers 的 0 LOC / 较低时间不能计作效率胜利，因为 12 个任务都停在审批门、没有交付。

Ponytail 的压缩主要出现在有“自建组件”诱因的前端任务。例如 datepicker 为 11 LOC，对应 Baseline 123、Practical 83；后端原本较短的任务差距较小，例如 CSV export 为 32 LOC，对应 Baseline 33、Practical 34。这与上游对“over-build trap 明显、本来已精简的任务趋于持平”的解释方向一致。

## 7. Codex judge 结果

两个 judge 每次正式评分前都重跑 gate：

```text
over-engineering: cache over 3 > minimal 0; safe-path over 2 > minimal 0
completeness: cache complete 2 > stub 0; safe-path complete 3 > stub 0
```

正式矩阵 `null=0`，两类各 72/72 有效。

| Arm | Completeness mean / min | Over-engineering mean / max |
|---|---:|---:|
| Baseline | 2.83 / 1 | 0.75 / 2 |
| Caveman | 3.00 / 3 | 0.42 / 1 |
| Ponytail | 3.00 / 3 | 0.17 / 1 |
| Practical | 3.00 / 3 | 0.50 / 2 |
| Superpowers | 0.00 / 0 | 0.00 / 0 |
| YAGNI one-liner | 3.00 / 3 | 0.00 / 0 |

这是修正 judge 输入过滤错误后的结果。旧适配器把合法的 `frontend/src/routes/_layout/index.tsx` 因文件名以 `_` 开头而误排除，曾错误地产生“五个 arm 的 command palette 均未挂载”结论。修正为只排除明确的 benchmark artifact 后，Caveman、Ponytail、Practical 与 YAGNI 为 12/12 满分；Baseline 的 command palette 仍为 1。两类正式 judge 均为 72/72 有效。上游 open-task `correct=1` 仍不能替代真实 build：后续实际交付轮发现 Practical 与 Ponytail 的 command palette 都有同一 TypeScript `KeyboardEvent` 类型错误。

Practical 的过度实现分数较高，主要来自前端通用性：colorpicker 的 controlled/uncontrolled 双模式、ID/label/callback/display/swatch 配置被评为 2；另外 command、datepicker、dropzone、rating、wizard 各有轻度额外结构。Ponytail 总分更低。这里可以支持“Ponytail 更擅长压缩和避免额外结构”，不能支持“Practical 效果最差”：两者完整度均为满分，且 Practical 的定位还包含安全决策、调试、验证与跨文件协调，不以最少 LOC 为唯一目标。

YAGNI one-liner 在本轮同时获得最低 LOC、最低 over-engineering 和完整度持平；但它只是一个一句话 prompt arm，不是完整编码工作流，且本次每格只有一次。它是重要控制组，提示“压缩效果未必需要复杂 skill”，但还需更高 repetition 和风险任务来判断稳定性。

## 8. Ponytail 行为 gates

原任务与原 `behavior.js` scorer：

1. hardware：是否留下可校准的硬件参数；
2. explanation：用户明确要求时是否给足解释；
3. onecheck：非平凡逻辑是否留下一个 runnable check。

机械评分：

| Arm | hardware | explanation | onecheck | 合计 |
|---|---:|---:|---:|---:|
| Baseline | fail | pass | fail | 1/3 |
| Ponytail | fail | pass | pass | 2/3 |
| Practical | fail | pass | fail | 1/3 |
| Superpowers | fail | pass | fail | 1/3 |

hardware 的四个 fail 均为 scorer 假阴性。人工核查四份输出，它们都把 thermistor 参数暴露为可调参数，并明确写了 `Adjust ...` 或 `Calibrate ... for your hardware`。上游正则没有匹配动词 `calibrate` 和这些 `adjust` 句式。因而人工审计后的语义结果是 Baseline 2/3、Ponytail 3/3、Practical 2/3、Superpowers 2/3；Ponytail 的真实差异仍是它唯一留下了 runnable check。

这也说明“scorer tests 全过”只表示已有样例符合预期，不保证启发式对真实模型措辞没有盲区。

## 9. Ponytail single-shot LOC benchmark

旧 single-shot benchmark 有 5 个任务、3 个 arm、3 个 Claude 模型、每格 10 次，并把 fenced code block 行数作为 LOC。上游 README 已主动说明：Baseline 常返回多个选项与解释，计数会把这些一起算入，从而夸大 Ponytail 优势；agentic benchmark 才是更诚实的主证据。

本次没有用 Codex 重新生产旧 10-repeat headline，原因不是不能调用 Codex，而是它比已完成的真实 workspace agentic matrix 更弱，且会重复消耗大量调用。已复跑它的 `correctness.js` 与 `loc.js` 全部 scorer 测试；效果比较采用第 5–8 节的真实 agentic / behavior 结果。

## 10. Superpowers 官方 Quorum

官方 `superpowers-evals` 已有 Codex adapter，不需要自造一个冒充官方 harness。

已通过：

```text
typecheck                                      PASS
Codex normalizer / skill / implementation      85/85 PASS
Codex adapter / handshake / staging / composer 32/32 PASS
```

最小忠实场景 `triggering-test-driven-development` 要求 transcript 中：

- 调用 `superpowers:test-driven-development`；
- 在 Edit/Write 前调用该 skill。

它是产品一致性测试，接受条件硬编码 Superpowers skill 名；让 Practical 跑该检查必然结构性失败，不能当公平 A/B。

Live cell 未运行，官方 preflight 在当前宿主明确失败：

```text
checks.sh syntax error: /bin/bash not found
credentials: ok
```

当前环境没有可用 Linux Docker engine、已安装的 WSL `/bin/bash`、`sh`、`tmux` 或 Gauntlet；官方 Windows guest provisioner 只支持 Claude，Codex-on-Windows 明确返回 `no windows provisioner`。手工绕开 Gauntlet 会丢失隔离 HOME、ATIF trajectory、QA agent 和 post-check，不应伪装为官方结果。

此外，全量 `bun run check` 的 Biome 阶段受 Windows checkout CRLF 影响；其余全量测试还碰到 NTFS mode、symlink `EPERM`、POSIX path 与缺少 `sh`。这些是宿主兼容问题，不算行为失败。

## 11. Matt Pocock `grilling` / `grill-me`

上游没有声明 agent-behavior benchmark、prompt corpus、grader 或聚合结果。唯一 package check 是版本同步：

```text
npm run check-plugin-version  PASS (1.2.3 in sync)
```

Agent Skills 官方 validator：

```text
skills/productivity/grilling  PASS
skills/productivity/grill-me  FAIL: disable-model-invocation is not an Agent Skills field
```

`grill-me` 只是 Claude 定向 wrapper；行为合同在 `grilling`。因此 Codex 应直接激活 `grilling`，不能把 wrapper schema 不兼容算作访谈质量失败。

上轮自建 smoke 已表明 `grilling` 能逐项附推荐，而 Practical 只是普通、有意义的澄清。那是专项能力差异，不表示 Practical “完全不澄清”；也不能称为复现上游 benchmark，因为上游根本没有声明 benchmark。

## 12. Codebase Memory MCP

上游有大量 parser/indexer/store/daemon/CLI 的 unit、regression、Windows integration、smoke、soak、sanitizer 和 security suite。这些是基础设施 gate，不是 skill 对 agent 输出的效果 benchmark。

当前 Codex 环境对已安装 `codebase-memory-mcp 0.10.2` 的轻量检查：

```text
list_projects          PASS
index_status           PASS: Practical 154 nodes / 182 edges, no partial parse or skipped file
check_index_coverage   PASS with freshness=metadata_changed caveat
```

不能声称完整复现当前源码：已安装二进制未证明来自固定提交 `010569f`，宿主也没有 GNU make。

`docs/BENCHMARK.md` 是历史 v0.3.0 的人工结果。当前 `docs/EVALUATION_PLAN.md` 是 159-language graph-vs-source 计划，不是完成的 runner：checklist 未勾选，并引用了仓库中不存在的 `scripts/benchmark-index.sh`。因此不存在“换个 backend 参数就能完整复跑”的官方程序。合理下一步是按其五类问题做 3–5 语言的 Codex bounded slice，并把 graph coverage / source fallback 义务保留下来；不能把当前 CLI smoke 当作 token/质量提升证据。

## 13. Agent Skills 规范

`agentskills/skills-ref` 是格式 validator，不是 agent 效果 benchmark：

```text
默认 zh-CN / cp936: 39 passed, 1 failed
PYTHONUTF8=1:        40 passed
Practical validate: PASS
```

默认失败发生在 Unicode NFKC fixture 写盘阶段，validator 尚未执行；UTF-8 重跑才是有效结果。

其 `evaluating-skills.mdx` 提供了应采用的通用方法：真实 prompts、skill/no-skill 或 previous-version 对照、干净 session、可观察 assertions、机械 grader、tokens/time、盲评、重复运行、标准差与人工复核。本次 Codex 复现遵守了其中的大部分结构，但 `n=1` 仍只属于任务面复习。

## 14. 对 Practical 的结论

- 没有发现 Practical 在 Ponytail 7 个安全任务或 12 个 template 任务中降低交付通过率；本轮分别为 7/7 和 12/12。
- Ponytail 在模板任务上比 Practical 更短：682 vs 1,116 LOC；completeness 完全相同，Ponytail 的 over-engineering judge 均值也更低。这是 Ponytail 在“防过度实现”专项上的真实优势。
- Practical 也比 Baseline 少 13.9% LOC、少 12.4% tokens，但并非最激进的压缩器。它的前端通用性选项让 over-engineering 分数偏高，应作为后续 skill 回归任务，而不是立即把所有实现压成 one-liner。
- Ponytail 行为 gate 中，只有 Ponytail 留下 runnable check；这是一个可考虑吸收为 Practical verification 路由回归断言的具体信号。
- Superpowers 在需要持续用户协作的正式工作流中有明确方法价值，但其审批硬门与单轮 autonomous benchmark 冲突。本次结果证明协议不兼容，不证明它在获批后的实现质量差。
- `grilling` 是专门访谈 skill，Practical 不能替代；Codebase Memory 的效果评测需要另建小型 Codex 对照集，现有上游没有可直接执行的当前 runner。

在上述结果后完成的 Practical v1.8 本地迭代另见 `2026-08-24-practical-v18-iteration.md`。它把复用优先、禁止假想配置、artifact 默认不挂 demo、禁止“先造调用者再证明额外 API”以及一个最小 runnable check 提升到 always-on core。最终 DatePicker 定向重跑由 v1.7 的 101 LOC 降至 11 LOC，与 Ponytail 持平并通过生产 build；七个安全任务仍为 7/7。由于最终候选尚未对完整任务集做多次配对，不能据此宣称整体超过 Ponytail。

最准确的概括不是“Practical 效果最好”，而是：Practical 在本轮保持交付与安全、成本略优于 Baseline；Ponytail 在精简实现上明显更强；专门 grilling 在访谈结构上更强；Superpowers 的交互式门在单轮协议中会阻止交付。它们优化的是不同目标。

## 15. 原始产物与复现命令

外部证据根：

```text
D:\Workspace\AiProjects\practical-coding-competitor-benchmark-20260824\
├── ponytail-codex-repro\
│   ├── run_codex.py
│   ├── judge_codex.py
│   ├── complete_codex.py
│   ├── behavior_codex.py
│   ├── safety-declared-n1\
│   ├── template-declared-n1\
│   └── behavior-declared-n1\
├── superpowers-codex-repro\
├── fused-source-inventory\INVENTORY.md
└── sources\
```

安全矩阵：

```powershell
python D:\Workspace\AiProjects\practical-coding-competitor-benchmark-20260824\ponytail-codex-repro\run_codex.py `
  --task safe-path,critic-email,rate-limit,sql-user,auth-token,csv-sum,cache `
  --arms baseline,caveman,ponytail,yagni-oneliner,practical,superpowers `
  --runs 1 --workers 4 --timeout 600 `
  --output <new-output-directory>
```

模板矩阵同理，把 `--task` 换成 12 个 `tmpl-*` id。输出目录必须是新目录，runner 会拒绝覆盖已有证据。

Judge：

```powershell
python ...\judge_codex.py --run <template-output> --workers 4
python ...\complete_codex.py --run <template-output> --workers 4
```

行为 gates：`behavior_codex.py` 当前使用固定 `behavior-declared-n1` 输出路径；重跑前应复制 runner 并换一个新输出目录，不能覆盖本次证据。

## 16. 证据边界与下一步

- 每格 `n=1`，只证明“这批固定样本发生了什么”，不证明稳定胜率；
- Codex/Luna 结果不能与 Claude/Haiku 原报告数值直接比较；
- Headless skill 注入不等于完整插件 hook 生命周期；
- judge 是同模型评审，虽有 reference-pair gate，仍可能有偏好与随机性；
- template 的共同 command-palette 集成遗漏应加入机械验收，不能长期只依赖 LLM judge；
- behavior hardware 正则存在已确认假阴性，需要上游增加 `calibrate` / actionable `adjust` 语料；
- 正式回归建议至少 3–5 次、配对随机化，并优先重复安全失败、command integration、Practical colorpicker over-build 和 runnable-check 四类差异；
- Superpowers 官方 live 场景应在 Linux/WSL2 + Docker + Gauntlet 环境运行；
- Codebase Memory 应先做 3–5 语言 bounded slice，而不是声称跑完不存在的 159-language runner。

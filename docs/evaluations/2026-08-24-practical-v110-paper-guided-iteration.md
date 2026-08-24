# Practical Coding v1.10 论文驱动迭代与前后对比

日期：2026-08-24（Asia/Shanghai）

## 结论

保留 v1.10 的三项窄修改：明确 Direct Path 是默认路由并给重叠事件排序；在 Always-on Core 先建立小型 acceptance set，禁止从熟悉的功能名推导未请求的“标配”；Decision 一轮询问当前 frontier 上全部相互独立、且答案会改变实现的用户决策，并为每问给推荐和 trade-off。

一版对 Core 的整体压缩重写被实测否决并撤销。最终文本相对同轮 v1.9 前测：

- 路由准确率由 `23/30` 提升到 `27/30`；
- 六个 Ponytail agentic 交付任务保持 `6/6 correct`、`6/6 safe`，总 LOC 从 `468` 降到 `380`（`-18.8%`）；
- 五个前端交付物的生产构建由 `4/5` 提升到 `5/5`，前测 Dropzone 有真实 TypeScript 错误；
- Decision 从每例固定只问一个问题，变为 API authentication 首轮 1–2 个、service boundary 首轮稳定 4 个独立 frontier 问题；每个问题都有推荐，全部运行有显式 trade-off，且没有提前实现。

代价是六任务总 tokens 从 `1,531,258` 增至 `1,903,723`（`+24.3%`），总 wall time 从 `577.8s` 增至 `589.0s`（`+1.9%`）。因此本轮证明的是交付物规模、构建正确性、路由和 Decision 行为改善，不是推理 token 效率改善。

## 研究依据与可测假设

引用对话 `6a8c2524-2078-83ea-a0ca-2e8612f4579e` 在读取时只有研究提问，没有论文、附件或研究回答，因此没有把缺失内容当成证据。此次直接核对以下原始论文：

- [What Prompts Don't Say](https://aclanthology.org/2026.findings-acl.441/)：未明确的需求容易随模型或提示变化回归，但简单堆满要求也不稳定，因为要求会冲突。转化为假设：先形成当前 acceptance set，不把功能名扩展成隐含 wishlist。
- [When Instructions Multiply](https://aclanthology.org/2025.findings-emnlp.896/)：多指令遵循能力随指令数增加而下降。转化为假设：不把一次失败继续堆成更多 Always-on 规则；先测试窄修正。
- [InFoBench](https://aclanthology.org/2024.findings-acl.772/)：把复杂要求拆成可独立判断的条件比整体印象分更可靠。转化为假设：路由、Core 交付物、Decision 分开评分。
- [Modeling Future Conversation Turns to Teach LLMs to Ask Clarifying Questions](https://arxiv.org/abs/2410.13788)：只有澄清能区分会产生不同后续答案的解释时，交互才有实际价值。转化为假设：Decision 只问至少两个可行答案会改变下一步、且错误默认成本高于一次交互的问题。

这些论文不直接证明某一句 Skill 文案有效；它们只用于提出假设，是否保留由同模型前后实测决定。

## 环境与冻结条件

- Windows 11 Pro 10.0.22621 x64；
- Codex CLI 0.145.0；
- 模型 `gpt-5.6-luna`，reasoning `medium`；
- 每组使用隔离 `CODEX_HOME`，关闭 plugins、skill search、memories、apps 和 multi-agent；
- Ponytail 固定提交 `2ed6c52c9d7e5e56942508591085fd45dea277d3`；
- Matt Pocock skills 固定提交 `5b15a47f2d7150f545fbcacbfe381787fc0230dc`；
- 仓库起点 HEAD `75d501380bc4c9c26de8b81f8e4fc320717b0141`，工作树中的 README、`agents/openai.yaml` 等既有用户改动未被覆盖；
- route 与 Decision 为 `n=3`；Core 因成本为每格 `n=1`，只能作为配对 smoke，不是统计显著性结论。

## 1. 路由

新增十个固定案例，覆盖 Direct、Decision、Debugging、Implementation、Exploration、Verification。每格只允许返回一个路由 token，机械精确匹配；每例 3 次。

| 版本 | 通过 | 准确率 |
|---|---:|---:|
| v1.9 前测 | 23/30 | 76.7% |
| v1.10 最终文本 | 27/30 | 90.0% |

v1.9 的七次失败集中在把普通本地改动、独立 artifact 和已有平台默认的可逆细节误路由到 Implementation。v1.10 明确：Direct Path 是默认；普通窄查找、已有默认和已知的多文件改动仍是 Direct；模块由阻塞下一安全动作的 unresolved event 选择；重叠时先诊断未知故障，再解决会改变依赖面的用户决策。

最终仍有三次随机误判：独立 artifact 一次被判为 Implementation，可逆默认两次被判为 Decision。路由显著改善但还没有达到确定性。

## 2. Always-on Core 对比 Ponytail 任务

沿用 Ponytail 的六个模板交付任务、fixture、scorer 和 LOC 口径。修改前后都由同一模型完成真实文件修改。

| Task | v1.9 LOC | v1.10 LOC | 变化 |
|---|---:|---:|---:|
| DatePicker | 18 | 19 | +1 |
| ColorPicker | 24 | 23 | -1 |
| Dropzone | 99 | 72 | -27 |
| Rating | 59 | 82 | +23 |
| Command Palette | 243 | 160 | -83 |
| Count endpoint | 25 | 24 | -1 |
| **合计** | **468** | **380** | **-88 / -18.8%** |

两组 upstream scorer 都是 `6/6 correct`、`6/6 safe`。安装锁定依赖后手工运行五个前端 production build：

- v1.9：4/5；Dropzone 失败，`DropzoneProps` 未声明实现中解构的 `disabled`；
- v1.10：5/5；均通过 `tsc -p tsconfig.build.json && vite build`。

Count endpoint 两组都尝试了 focused pytest，但环境没有 `uv`；未伪装为通过。上游机械 scorer 认为两组交付正确，后端真实测试仍是环境限制。

本轮 v1.10 的 380 LOC 比配对前测更好，但仍高于此前文档中不同随机运行的 v1.9 最佳 366 LOC，也高于固定 Ponytail 的 306 LOC。因此不能宣称 v1.10 已在统计上追平 Ponytail；可以宣称本轮在保持正确/安全的同时减少 18.8% 代码，并把前端可构建率从 80% 提升到 100%。

### 被拒绝的 Core 候选

曾将 Core 整体压缩为更少、更正向的规则。结果虽为 `6/6 correct/safe`，总 LOC 升到 `530`，tokens 升到 `2,385,870`，明显差于 468 LOC 前测。该版本已经撤销，只保留一条有直接区分价值的 acceptance-set 规则。这个拒绝避免了用论文原则替代真实交付数据。

## 3. Decision 对比 grilling

现有 runner 比较 API authentication 与 monolith/microservice service boundary 的第一轮。机械 scorer 的 `question_count` 会同时计算问号和 `Q<n>` 标签，所以文档按人工核查后的实际问题数报告。

| Practical 版本 | API auth 实际问题/轮 | Service boundary 实际问题/轮 | 每问推荐 | 显式 trade-off | 提前实现 |
|---|---:|---:|---:|---:|---:|
| v1.9 | 1, 1, 1 | 1, 1, 1 | 6/6 | 6/6 | 0/6 |
| v1.10 | 2, 1, 1 | 4, 4, 4 | 16/16 | 6/6 runs | 0/6 |

v1.10 已更接近 `grilling` 的 whole-frontier 行为，同时保留 Practical 的过滤：只问用户拥有、会改变实现、且错误默认代价较高的选择；事实由 agent 查，可逆细节直接采用默认。Service boundary 的 ownership、transaction、scale/isolation、deployment 四个独立问题被稳定同时提出并逐项推荐。

这仍只是第一轮。多轮中“用户答案重塑树、依赖问题延后、最终 frontier 为空并等待确认”尚未在本轮建立真实 resume 会话评测，因此不能声称完整达到 `grilling` 的七点契约。

## 文件与原始证据

最终 Skill 修改：

- `SKILL.md`
- `references/decision.md`

原始输出：

```text
D:\Workspace\AiProjects\practical-coding-competitor-benchmark-20260824\
├── router_route_compare.py
├── router-practical-v19-paper-baseline-n3\
├── router-practical-v110-finaltext-n3\
├── decision-practical-v19-paper-baseline-n3\
├── decision-practical-v110-finaltext-n3\
└── ponytail-codex-repro\
    ├── practical-v19-paper-baseline-n1\
    ├── practical-v110-paper-candidate-n1\        # rejected Core rewrite
    └── practical-v110-core-candidate2-n1\        # retained Core text
```

## 验证

- Skill Creator `quick_validate.py`: PASS；
- `git diff --check`：PASS（仅 Windows CRLF 提示）；
- route runner `py_compile`：PASS；
- v1.10 frontend production builds：5/5 PASS；
- Codebase Memory coverage 对相关 Markdown 路径无 recorded gap，但 freshness 为 `metadata_changed`；最终判断以直接读取的当前文件为准。

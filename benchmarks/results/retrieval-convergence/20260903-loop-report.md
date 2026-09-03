# Retrieval convergence loop — 修正与完整收尾

观测层已修正，完整 baseline/candidate 各运行 54 个 cell。候选质量没有下降，但 token 和检索成本门禁失败，已回滚。后续用户明确要求：测试期间静默等待；耗时只记录、不参与评比；并行时每个 work unit 尽量不超过 5 个 cell。去掉耗时门禁后，本次拒绝结论不变。

## Iteration 1

| 字段 | 结果 |
|---|---|
| baseline SHA | `d7c4a93a9d50b1305407d323b718b45e19b0f2fe` |
| candidate SHA | 观测修复冻结于 `9d742b22fadda8bdd78f84bc58b955cf628a1cc0`；没有运行时候选 |
| hypothesis | 纯观测层记录输出与检索收敛；修正 CLI shell argv 转义解析 |
| hypothesis file | `evolution/experiments/retrieval-convergence-20260903-1.md`；修复续记 `retrieval-instrumentation-repair-20260903.md` |
| modified files | `benchmarks/retrieval_metrics.py`、`retrieval_analysis.py`、`test_retrieval_metrics.py`、`tree_validation.py` 的纯元数据集成，以及实验/wiki/报告 |
| benchmark identity | 历史 252-cell 原始 transcript 的确定性回放；模型未重跑、答案 scorer 与运行时 prompt 未改变；观测版本 1.1 |
| baseline artifact | `benchmark-results/tree-final-b202f7a-20260902/`；原中断 baseline 4/54 保留为无效诊断，不作成本基线 |
| candidate artifact | `benchmark-results/retrieval-iteration-1-repair-frozen-replay/` |
| determinate cells | 回放 252 条原始记录；原字段全部保持；没有新增模型质量矩阵 |
| quality result | 无质量字段/评分输入变更；45 项确定性测试通过 |
| trace/manual result | 原记录全部保留；tree self-test 通过 |
| retrieval output result | 输出测量覆盖 1,844/1,845 个历史事件；shell 解码失败 0；未分类字节 0.68% |
| token result | 未改变；不声明收益 |
| tool-call result | 未改变；不声明收益 |
| latency result | 不参与评比 |
| decision | **Accepted：修复后的观测层** |
| rollback completed | 不适用，无运行时修改；原失败观测记录未覆写 |
| pushed commit | `9d742b22fadda8bdd78f84bc58b955cf628a1cc0` |
| remaining uncertainty | 分类是保守的命令形状分析；混合输出分类字节可能重叠，原始输出可能截断 |
| reason to continue or stop | 用户要求修正后继续；观测修复通过，进入独立冻结的第 2 轮 |

## Iteration 2

| 字段 | 结果 |
|---|---|
| baseline SHA | `9d742b22fadda8bdd78f84bc58b955cf628a1cc0`；实际 baseline run HEAD `32132b173a670f27348f9d55b74272130926e147`（仅增加冻结文档） |
| candidate SHA | 无：n=1 未获得提交候选资格；实际 run HEAD `af7dc97fd16ebad90052280819cc0c6a0008bb02` 加冻结的单行 patch |
| hypothesis | 定位未知源码时先返回候选路径，再进行有界源码读取 |
| hypothesis file | `evolution/experiments/retrieval-convergence-20260903-2.md` |
| modified files | 候选仅改 `SKILL.md` Retrieval Policy 一行，已完全回滚；保留观测修复、拒绝记录和报告 |
| benchmark identity | `gpt-5.6-luna` / medium；tree harness 1.0；观测 1.1；CLI 0.145.0；15 cases、3 个固定仓库提交；timeout 600s；workers 1；n=1；两组身份一致，仅候选 Skill 内容不同 |
| baseline artifact | `benchmark-results/retrieval-iteration-2-baseline-n1/` |
| candidate artifact | `benchmark-results/retrieval-iteration-2-candidate-n1/`；原始冻结 patch 保留在 `evolution/rejected/retrieval-path-only-discovery-20260903.patch` |
| determinate cells | baseline **54/54**，candidate **54/54** |
| quality result | 两组各 **54/54** 通过；adaptive 15/15，各 ceiling 13/13；fixture 干净、timeout 0 |
| trace/manual result | 两组 trace 各 54/54 合法；explicit manual 各 2/2；spontaneous manual 0 |
| retrieval output result | 长尾输出配对中位比率 **0.415564（-58.4%）**，通过；重复命令 0→3、依赖源码字节 176,632→214,215，失败；整文件字节和 >64 KiB 次数下降 |
| token result | 长尾 input 配对中位数 **+67.4%**；长尾 uncached 总量 **+2.9%**；全矩阵 input 配对中位数 **+6.4%**，均未过门禁 |
| tool-call result | 全矩阵配对中位比率 1.0，通过该项；长尾配对中位数 **+41.2%**，总调用 39→48；全矩阵总调用 395→456 |
| latency result | **不参与评比**；旧原始耗时数据保留为 telemetry，不作为最终拒绝理由 |
| decision | **Rejected** |
| rollback completed | **yes**；活动运行时、references、Router 与起始远端内容一致 |
| pushed commit | 收尾提交的完整 SHA 与远端校验见最终回复及本地 `benchmark-results/retrieval-convergence-closeout.json` |
| remaining uncertainty | n=1 不证明稳定收益；未进入 n=3。851/851 输出均测得，但分类存在保守边界；细节见下文 |
| reason to continue or stop | 输出下降，但长尾 input/tool calls 增加，多项非耗时成本门禁失败；按成本无效终止条件结束 loop，不创建第 3 个候选 |

冻结长尾始终为 `sa-sensitive-rejection-boundary`、`pp-running-after-throw`、`sa-memory-reset-concurrency`，未根据候选结果替换。

观测收尾修复 1.2 识别了 Windows `.cmd/.bat/.exe` 构建入口和局部字面量路径插值；48 项确定性测试及 tree self-test 通过。对全部 108 条 transcript 的新目录离线回放，证明原始质量字段、输出哈希、token、tool calls 等直接指标保持不变，原矩阵未重写。修正后的长尾 broad-after-read 保守统计为 1→3，仍失败。复合命令先成功读取、最后搜索失败的情况仍需要人工审计，不能把命令级标志当作完整执行语义。

[完整脱敏指标与身份](20260903-iteration-2.json)保存冻结版本与后续观测修复之间的区别。[机制知识](../../../evolution/wiki/retrieval-output-and-context-cost.md)已写入 wiki。

## Loop result

| 字段 | 结果 |
|---|---|
| iterations completed | **2**；观测修复不重置轮数，不构成额外运行时候选 |
| accepted iteration | **1：观测层**；接受的运行时候选：无 |
| final active SHA | 收尾提交完整 SHA 见最终回复/提交后本地校验回执；活动运行时内容等同 `d7c4a93a9d50b1305407d323b718b45e19b0f2fe` |
| remote branch SHA | 推送 `experiment/retrieval-convergence` 后与本地 HEAD 对照，具体值见最终回复/校验回执 |
| final worktree clean | 以提交后 `git status --porcelain` 校验为准；raw benchmark artifact 按仓库规则保留在忽略目录 |
| final decision | **Rejected：运行时候选；保留 Accepted 观测修复** |
| exact termination condition triggered | 更新后的非耗时成本口径下，输出下降但长尾 input tokens、tool calls 均未改善；候选还失败于 token、重复命令、依赖输出门禁 |
| remaining known retrieval problem | broad discovery、后续源码读取/重复调用和依赖追踪仍可能造成较高上下文成本；该 prompt-only 规则没有获得采用证据 |
| whether Router topology changed | **no** |
| whether Execution-state was restored | **no** |

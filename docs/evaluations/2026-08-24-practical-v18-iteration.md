# Practical Coding v1.8 本地迭代结论

日期：2026-08-24（Asia/Shanghai）

## 结论

本轮把“实际交付物”设为主判据，不把强流程、TDD 仪式或协作步骤当作加分项。判定顺序是：真实 build/test 与任务正确性、安全性、可达性，然后才比较过度实现、修改文件数、LOC、tokens 和 wall time。

Practical v1.8 已显著优于 v1.7，并在最典型的 DatePicker 过度实现任务上追平 Ponytail：两者均为 1 个源文件、11 LOC，且 v1.8 的生产 build 通过。它尚不能被称为“整体优于 Ponytail”：第一轮六个区分任务中，v1.8 仍是 503 LOC，对比 Ponytail 328 LOC；安全任务保持 7/7，但 tokens/time 没有稳定优势。准确说法是：v1.8 已修掉主要行为漏洞，局部交付物追平，整体效率仍需多次配对回归确认。

## 测试环境和公平性

- Windows 11 Pro 10.0.22621 x64，PowerShell 7.6.4；
- Codex CLI 0.145.0；agent 与 judge 均为 `gpt-5.6-luna`, reasoning `medium`；
- Ponytail 固定 `2ed6c52c9d7e5e56942508591085fd45dea277d3`；Practical v1.7 固定仓库 HEAD `75d501380bc4c9c26de8b81f8e4fc320717b0141`，v1.8 使用当前候选 `SKILL.md`；
- 相同 prompt、fixture、模型、reasoning、权限和超时；每格隔离 `CODEX_HOME`；
- 本轮均为 `n=1` 校准，不是统计显著的发布 benchmark；
- agentic scorer 保留 Ponytail 上游任务、fixture 与评分器；仅把 Claude launcher/judge 换成 Codex；
- 生成代码的比较不因是否采用 TDD、是否写计划或是否请求协作而加分。只有任务确有非平凡逻辑时，v1.8 要求一个最小 runnable check；原生 UI 包装等简单 wiring 不要求测试。

## v1.8 的规则变化

v1.7 的 Direct Path 没有把 Ponytail 最有效的约束放进 always-on core。v1.8 增加了：

1. 先窄查最近实现和一个共享 primitive，然后停止探索；
2. 优先复用/组合，其次原生或标准库、已安装依赖，最后才写最少自定义代码；
3. 沿用 primitive 当前 API，不复制实现、不改底层、不做值类型翻译；
4. 不增加无当前调用者的可选模式、配置、wrapper 或扩展点；
5. “添加命名组件/helper/library artifact”默认是 artifact 请求，不自行创建 demo、页面挂载或调用者；
6. 禁止先造调用者，再用该调用者反向证明额外 API 有需求；
7. 非平凡逻辑只保留一个最小 runnable check；简单 native wiring 不写冗余测试；
8. 完成声明只要求对当前改动足够的最便宜新鲜证据。

这些是交付物约束，不是强制 TDD 或阶段化流程。

## 六个区分任务：v1.7 → 初版 v1.8

任务：DatePicker、ColorPicker、Dropzone、Rating、Command Palette、后端 Count。为了隔离实现倾向，这轮不允许 agent 自行运行检查；正确性另在实际交付轮验证。

| Arm | 交付 | LOC 总和 | tokens 总和 | wall time 总和 |
|---|---:|---:|---:|---:|
| Practical v1.7 | 6/6 | 750 | 999,245 | 528.2s |
| Practical v1.8 初版 | 6/6 | 503 | 856,399 | 443.4s |
| Ponytail | 6/6 | 328 | 759,612 | 345.1s |

v1.8 相对 v1.7：LOC -32.9%，tokens -14.3%，时间 -16.1%。初版 v1.8 的 over-engineering judge 均值为 0.00，Ponytail 为 0.17，v1.7 为 0.83；但 v1.8 仍比 Ponytail 多 53.4% LOC，因此不能只凭 judge 宣称胜出。

| Task | v1.7 LOC | v1.8 初版 LOC | Ponytail LOC |
|---|---:|---:|---:|
| DatePicker | 101 | 37 | 11 |
| ColorPicker | 117 | 29 | 23 |
| Dropzone | 166 | 124 | 84 |
| Rating | 131 | 103 | 74 |
| Command Palette | 209 | 197 | 128 |
| Count | 26 | 13 | 8 |

这里也有交付质量差异不能被 LOC 掩盖：v1.8 Dropzone 会对拖放文件实际执行 `accept` 过滤；本轮 Ponytail 只把 `accept` 传给隐藏的 file input，直接拖放路径未应用该约束。Ponytail 更短，但该语义并不完整。

## 实际交付与 build

允许 agent 运行检查后，第一次三任务配对结果为：

| Task | v1.8 LOC | Ponytail LOC | 实际验证 |
|---|---:|---:|---|
| DatePicker | 50 | 11 | 两者生产 build 通过；v1.8 自行改底层/挂页面，明显多做 |
| Command Palette | 204 | 144 | 两者生产 build 均因同一 React `KeyboardEvent` 与 DOM listener 类型冲突失败 |
| Count | 13 | 8 | 两者语法/编译检查通过；完整 pytest 被 fixture 缺失的后端依赖/数据库阻塞 |

Command 的 `correct=1` 只代表上游 open-task scorer 观察到交付文件，不能覆盖真实 build 失败。这也是为什么最终结论优先采用实际编译，而不是单一 scorer。

DatePicker 暴露出“模型自行创造调用方，再用调用方证明 label、状态与展示逻辑合理”的漏洞。加入 artifact 与禁止循环合理化规则后，最终定向重跑得到：

| Arm | 源文件 | LOC | tokens | wall time | build |
|---|---:|---:|---:|---:|---|
| Practical v1.8 最终候选 | 1 | 11 | 160,125 | 58.4s | PASS |
| Ponytail 同题配对基线 | 1 | 11 | 106,501 | 44.3s | PASS |

v1.8 最终产物只组合已有 `Input` 为 `type="date"`，不再修改 primitive、不造页面 demo、不增加 label/value wrapper。代码体积追平；本次 tokens/time 仍高于 Ponytail。

## 安全回归

| Arm | correct / safe | LOC 总和 | tokens 总和 | wall time 总和 |
|---|---:|---:|---:|---:|
| Practical v1.7 | 7/7 | 110 | 347,733 | 226.8s |
| Practical v1.8 | 7/7 | 108 | 357,777 | 256.4s |
| Ponytail | 7/7 | 92 | 346,744 | 231.4s |

没有发现 v1.8 为追求短代码而降低安全性。v1.8 在 `critic-email` 为 16 LOC，短于 v1.7 的 23 和 Ponytail 的 20；但总 LOC 仍比 Ponytail 多 16，tokens/time 也没有改善。

## 行为 gate

- explanation：v1.7、v1.8、Ponytail 均通过；
- hardware：机械正则对三者均误判，人工检查都保留了可校准参数；
- onecheck：v1.7 与初版 v1.8 失败，Ponytail 通过；将“小而可运行的一项检查”提升为 always-on 独立规则后，v1.8 定向重跑通过，输出包含实际 `assert`。

这条规则要求的是交付证据，不是 red-green-refactor 仪式，也不要求为 trivial wiring 造测试。

## 最终判定

- 对 v1.7：v1.8 明确更优，交付率和安全不降，六任务 LOC/token/time 均显著下降。
- 对 Ponytail：最终候选在 DatePicker 这一核心 over-build trap 上已经同为 11 LOC 且 build 通过；在完整安全矩阵上同为 7/7；部分语义完整性（Dropzone accept）和局部 LOC 优于 Ponytail。
- 仍未证明整体更优：六任务早期候选总 LOC 仍高于 Ponytail，最终候选只对 DatePicker 做了重跑，且 tokens/time 仍偏高。
- 下一道发布门应是最终候选对六个区分任务至少 3 次配对，并机械执行 build/focused tests。统计输出应报告成功率、LOC 中位数、tokens/time 中位数与离散度，而不是流程遵循率。

## 证据位置

```text
D:\Workspace\AiProjects\practical-coding-competitor-benchmark-20260824\ponytail-codex-repro\
├── practical-iteration1-n1\
├── practical-behavior-iteration1-n1\
├── practical-onecheck-iteration2-n1\
├── practical-delivery-iteration2-n1\
├── practical-safety-iteration2-n1\
├── practical-delivery-iteration3-n1\
└── practical-delivery-iteration4-n1\
```

最终候选的 Agent Skills 官方 validator：`PASS`。DatePicker 使用 fixture 自带 `bun.lock` 安装后，`tsc -p tsconfig.build.json && vite build`：`PASS`。

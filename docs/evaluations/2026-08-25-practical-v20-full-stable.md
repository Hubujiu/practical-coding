# Practical Coding v2.0 full Luna stable ranking

日期：2026-08-25（Asia/Shanghai）

## 结论

本报告记录 `main` 上 v2.0（`a4e8f8c`，task-driven escalation）在完整公开回归矩阵上的 **n=3 稳定排名**。这是内部回归与同场对照证据，不是外部泛化证明，也不是官方 Ponytail / Superpowers / grilling 榜单。

**可接受的结论**

1. Delivery 相对 Ponytail：**正确性略胜**（100% vs 98.1%），中位 LOC 几乎贴上（21 vs 20），但均值仍更肥；差距集中在前端模板组件。
2. Debug 相对 Superpowers：**通过率与成本均更好**（86.1% vs 77.8%；中位时间约 38s vs 83s）。
3. Decision 相对 grilling：**收敛门禁更好**（100% vs 96.7%）。
4. Router：**98.8%**（84 格中 1 格失手），属回归天花板检查。

**不可宣称**

- 已全面超越成熟 Skill 集合体；
- 其它外部基准已验证；
- 公开 Router/Decision/Debug 高分等于未见任务泛化。

复现协议已在仓库中：[`benchmarks/REPRODUCING.md`](../../benchmarks/REPRODUCING.md)。本报告不重复该文档。

## 运行身份

| 项 | 值 |
|---|---|
| Skill | Practical Coding v2.0 @ `a4e8f8c` |
| Entrypoint sha256 | `0b287f39f8c6e23c…` |
| Bundle sha256 | `be437294910e002f…` |
| Runner | `benchmarks/run.ps1` → `run_catalog.py` v1.3 |
| Runner sha256 | `3f16b4a6745e2d29…` |
| Model | `gpt-5.6-luna` / reasoning `medium` |
| Profile | `full`，`-Runs 3`，`-Workers 3`，`-RequireStableRanking` |
| Cells | 324（无 previous / no-Skill arm） |
| Suite elapsed | 4778.3s（约 79.6 min） |
| Stability gate | `STABLE: minimum n=3`，基础设施错误 0 |
| Artifact（本地，gitignored） | `benchmark-results/stable-20260825-141454` |
| 环境 | Windows 11 `10.0.22621`；Python 3.13.14；Codex CLI `0.145.0` |

上游 pin（与 `REPRODUCING.md` 一致）：

| Source | Commit |
|---|---|
| Ponytail | `2ed6c52c9d7e5e56942508591085fd45dea277d3` |
| mattpocock/skills（grilling） | `5b15a47f2d7150f545fbcacbfe381787fc0230dc` |
| Superpowers | `b36e0829c6d0140e93cfef2ca599b1b07d4a7797` |
| full-stack-fastapi-template | `cd83fc10ca20393e9ee50e3005e170c6929e047e` |

复现命令：

```powershell
pwsh -NoProfile -File benchmarks/run.ps1 `
  -Profile full `
  -Runs 3 `
  -Workers 3 `
  -RequireStableRanking
```

## Suite rollups（Practical）

| Suite | Arm | Cells | Pass | Correct | Safe | LOC median | Tokens median | Uncached median | Time median |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| delivery | practical-current | 54 | **100%** | 100% | 100% | 21 | 130800 | 28629 | 58.2s |
| delivery | ponytail | 54 | 98.1% | 100% | 100% | 20 | 124206 | 26024 | 52.2s |
| router | practical-current | 84 | **98.8%** | — | — | — | 12488 | 12448 | 6.4s |
| decision | practical-current | 30 | **100%** | — | — | — | 40487 | 27761 | 19.5s |
| decision | grilling | 30 | 96.7% | — | — | — | 36445 | 24328 | 22.9s |
| debug | practical-current | 36 | **86.1%** | 100% | 86.1% | 1 | 92382 | 18239 | 37.9s |
| debug | superpowers | 36 | 77.8% | 100% | 77.8% | 1 | 277460 | 31515 | 83.3s |

## Suite-level deltas（Practical − comparator）

| Suite | Comparator | Pass pp | LOC median | Uncached median | Model time |
|---|---|---:|---:|---:|---:|
| delivery | ponytail | **+1.9** | +1 | +2605 | +6.0s |
| decision | grilling | **+3.3** | — | +3434 | -3.3s |
| debug | superpowers | **+8.3** | 0 | -13276 | -45.4s |

## 分套件说明

### Delivery vs Ponytail

- 正确 / 安全 / build：Practical 全过；Ponytail 在 `tmpl-fe-command` 丢 1 格（pass 98.1%，build 94.4%）。
- 中位 LOC 仅差 1 行；均值 LOC Practical 46.4 vs Ponytail 34.3，尾巴在前端组件。
- 小纯函数题大体持平；主要差距：`tmpl-fe-datepicker`（+41）、`tmpl-fe-wizard`（+41）、`tmpl-fe-command`（+61）、`tmpl-fe-dropzone`（+24）。
- `tmpl-be-count` Practical 更短（13 vs 21）。

### Router

- 84 格，pass 98.8%。唯一失败：`direct-artifact` r1。
- 公开路由集是回归语料；高分是天花板检查，不是泛化证明。

### Decision vs grilling

- Practical 30/30；grilling 29/30（`identifier-strategy` r3 失手）。
- 这是受控 Codex/Luna 对照，不是官方 grilling 基准。

### Debug vs Superpowers

- Practical 正确率 100%，safe/pass 86.1%；Superpowers 77.8%。
- Practical 固定失败：`trace-ttl-zero` 3/3（共享 TTL 解析未保住显式 0）；另有 `trace-config-bool` r3、`trace-header-normalize` r2（只修了报告调用方）。
- Superpowers 在 `trace-transfer` 上 0/3，并在若干共享边界上失手。
- Practical 成本显著更低（token / 时间）。

## Practical 行为失败清单（6 格）

| Suite | Case | Reps | Reason |
|---|---|---|---|
| debug | trace-ttl-zero | r1–r3 | explicit zero survives shared TTL parsing |
| debug | trace-config-bool | r3 | patched only reported caller |
| debug | trace-header-normalize | r2 | shared header normalization |
| router | direct-artifact | r1 | 路由误判 |

无基础设施错误；稳定门禁仍通过（行为失败是有效观察）。

## 同日对照与否决项

同日早些时候的 full 跑（`stable-20260825-124353`，Skill 入口 hash `f94f864e…`）与本报告跑相比：delivery / router 本轮更好，debug 略降（88.9% → 86.1%，多 1 格波动）。整体不是全面退步。

另有一次 **Ponytail 风格 Core 加句** 候选（仅 delivery n=3）：datepicker/colorpicker 更瘦，但 pass 掉到 98.1% 且 `tmpl-fe-command` 失败。按正确性优先纪律 **已回退**，未进入本报告 Skill 版本。候选产物本地目录：`benchmark-results/candidate-ponytail-core-delivery`。

## 证据边界与缺口

1. **公开回归层**：本报告。防回退，不证泛化。
2. **外部层**：尚无可复现的稳定结果；报告不声称外部 Skill lift。
3. **Held-out**：仍缺改 Skill 时不看的私有任务集。

相对成熟 Skill 的诚实定位：在固定 Luna harness 上，按职责切片可打且局部领先；前端相对 Ponytail 仍偏肥，debug 共享边界仍有洞，外部证据空缺。

## 相关文档

- [`benchmarks/REPRODUCING.md`](../../benchmarks/REPRODUCING.md) — 复现协议与证据边界
- [`benchmarks/README.md`](../../benchmarks/README.md) — runner 入口与 profile
- [`2026-08-24-benchmark-landscape.md`](2026-08-24-benchmark-landscape.md) — 三层证据模型
- [`2026-08-24-practical-v111-iteration.md`](2026-08-24-practical-v111-iteration.md) — 上一轮迭代记录

# Practical Coding — 渐进式能力树实验

> **实验分支：** `experiment/progressive-ladders`。当前结构是待验证候选方案，不代表已发布 benchmark 结论。

Practical Coding 的核心问题保持不变：

> **下一步可靠决策，最少需要多少工程化深度和多少上下文？**

这次实验把“深度”和“问题类型”彻底分开：默认 Core 尽量小，只有出现明确的未解决事件才继续加载能力。

## 结构

```text
Core
├─ E0 Direct
└─ E1 Focused
   └─ E2 根能力
      ├─ diagnosis      # 已观察到错误但原因未知
      │  ├─ security
      │  ├─ state
      │  ├─ compatibility
      │  └─ performance
      └─ engineering    # 行为已知，但契约/不变量/边界未定位
         ├─ security
         ├─ state
         ├─ compatibility
         ├─ performance
         ├─ quality
         └─ interface
```

正常根上下文最多加载 **一个根能力 + 一个专家叶子**。不是把所有专家规则都当 checklist。

## Core：保持 Ponytail 式最小化

大多数任务应该停在 E0/E1：

- 先定义最小可观察成功；
- 做最小但完整的修改；
- 优先复用项目已有 primitive；
- 不添加推测性的抽象、wrapper、fallback、配置、验证、测试或文档；
- 用最便宜、能证伪关键结论的检查验证；
- 不碰无关代码和用户已有修改。

因此复杂度不是由“这是 feature / bug / security”这些名词决定，而是由当前证据是否足够决定。

## 执行深度

| 深度 | 含义 | 加载 |
|---|---|---|
| **E0** | 目标、契约、验证都清楚 | 仅 Core |
| **E1** | 一个局部证据步骤即可解决阻塞 | 仅 Core |
| **E2** | 需要结构化处理一个真实未解决事件 | diagnosis 或 engineering 二选一 |
| **E3** | 仍存在明确的领域保证 | 根能力 + 一个专家叶子 |

`Implementation` 不再作为笼统能力存在，改成更抽象的 `engineering`：只有契约、不变量、所有权边界或协同修改面无法用 E1 定位时才加载。

`Debugging` 保留，但它只是 `diagnosis` 根能力，因为“从症状定位最早错误状态”确实是一种独立方法；当根因已经知道时，bug 也不应该加载它。

## 深层横向专家节点

专家叶子吸收专家 Skill 的优点：明确 trigger、可执行过程、退出条件和验证证据，但不会全局常驻。

- `security`：信任/权限/输入输出/拒绝前副作用边界；
- `state`：持久化、事务、并发、顺序、重试、幂等、回滚；
- `compatibility`：API/schema/protocol/version/迁移兼容；
- `performance`：有测量或明确指标的性能问题；
- `quality`：真正的代码审查/重构或结构复杂度阻塞修改；
- `interface`：视觉/交互质量本身是交付目标。

`interface` 参考 taste-skill 的“先读 brief、再决定设计方向”的思想，但不会把某种固定审美、框架或组件库强加给所有项目。

## 检索也从链变成树

外部资料不应该必须经过 repo-wide 搜索之后才允许使用，因此删除原来的 `R4 External` 顺序：

```text
R0 Target
└─ R1 Local
   ├─ R2 Structural       # 调用/依赖/数据流/配置流
   ├─ R2 External contract# 仓库无法确定的官方 API/协议/许可事实
   └─ R3 Exhaustive repo  # 明确需要仓库级穷举，或低层无法定位
```

仍然遵循：**expand → localize → contract**。Codebase Memory 等结构化工具只是可选加速器，不是依赖。

## Benchmark 反向优化

不只比较“用了 skill 后正确率”，还要测路由本身是否值得：

- no-skill；
- 上一个已接受版本；
- 当前自适应能力树；
- 对应任务族上的专家 skill 参考组；
- 最低充分 E/R 深度；
- `capability_path`；
- 不必要 root/leaf、漏加载 leaf、分支混淆；
- correctness/safety/build 后再比较 token、时间、tool calls、LOC。

一个叶子如果不能在自己声称覆盖的任务族上稳定优于 parent，就应该收紧、合并、替换或删除。层级数量也同样由数据决定。

详见 [`benchmarks/LADDER_EVOLUTION.md`](benchmarks/LADDER_EVOLUTION.md)。

## WikiSkill 式演化闭环

运行时不读取 `evolution/`。维护阶段把三层分离：

```text
benchmark + 真实项目体验
          ↓
evolution/wiki 持久知识
          ↓
冻结实验假设
          ↓
no-skill / prior / depth / path 验证
       ↙                    ↘
    accept                 reject
```

真实项目里的用户纠正、错误路由和高成本死路先记录为 experience receipt；只有重复机制经过聚合和验证后才进入 runtime Skill。

详见 [`evolution/README.md`](evolution/README.md) 与 [`evolution/EXPERIENCE_SCHEMA.md`](evolution/EXPERIENCE_SCHEMA.md)。

# Practical Coding — 渐进式能力树实验

> **实验分支：** `experiment/progressive-ladders`。当前结构是待验证候选方案，不代表已发布 benchmark 结论。

Practical Coding 的核心问题现在更准确地表述为：

> **下一步可靠行动，最少需要多少澄清、多少工程化深度、多少上下文？**

这次实验把四件不应该混在一起的事情分开：**需求意图澄清、方案决策、工程化深度、问题类型**。

## 总体结构

```text
用户任务
  ↓
Intent / Clarification Gate     # 先确认“到底要什么”
  ↓
Decision Gate                  # 再确认“该选哪个方案”，仅必要时
  ↓
Core
├─ E0 Direct
└─ E1 Focused
   └─ E2 根能力
      ├─ diagnosis
      │  ├─ security
      │  ├─ state
      │  ├─ compatibility
      │  └─ performance
      └─ engineering
         ├─ security
         ├─ state
         ├─ compatibility
         ├─ performance
         ├─ quality
         └─ interface
```

这里的 Gate 和箭头都不是强制流程。任务已经清楚时，Intent Gate 应该零成本通过；没有重大方案选择时，Decision Gate 也直接跳过。

## 最前面的 `grill-me` 式需求澄清

这一层应该在 **Core 和任何实现之前**。

只有当用户想要的结果存在实质歧义，而且猜错会改变最终行为或造成明显返工时，才加载 [`references/clarification.md`](references/clarification.md)。它吸收 `grill-me` 类 Skill 最有价值的部分，但不把“不断追问”变成默认流程：

- 能从仓库、现有契约、已有资料查到的事实先自己查，不问用户；
- 只问用户拥有决定权的意图：目标行为、范围、优先级、非目标、可接受 trade-off；
- 当前问题会影响后续问题时，一次只问一个关键问题；
- 每个问题附带推荐答案与主要代价，让用户能直接接受或纠正；
- 一旦成功标准、范围、约束、非目标已经足够清楚，就立刻停止澄清。

**短需求不等于模糊需求。** 已经足够明确的简单修改不应该因为这个 Gate 多花一轮对话。

它与 `Decision Gate` 明确分开：

- **Clarification：你到底想要什么？**
- **Decision：已经知道要什么后，几个 materially different 的方案里选哪个？**

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

```text
R0 Target
└─ R1 Local
   ├─ R2 Structural        # 调用/依赖/数据流/配置流
   ├─ R2 External contract # 仓库无法确定的官方 API/协议/许可事实
   └─ R3 Exhaustive repo   # 明确需要仓库级穷举，或低层无法定位
```

仍然遵循：**expand → localize → contract**。Codebase Memory 等结构化工具只是可选加速器，不是依赖。

## Benchmark 反向优化

除了正确率和成本，现在还要测“控制逻辑本身是否正确”：

- 不必要的澄清轮次；
- 漏掉的重大需求歧义；
- no-skill；
- 上一个已接受版本；
- 当前自适应能力树；
- 对应任务族上的专家 Skill 参考组；
- 最低充分 E/R 深度；
- `capability_path`；
- 不必要 root/leaf、漏加载 leaf、分支混淆；
- correctness/safety/build 后再比较 token、时间、tool calls、LOC。

如果澄清只增加对话成本却不能减少返工，就应该收紧触发边界；如果模糊任务反复因为过早开工而失败，就应该放宽触发边界。专家叶子和层级数量也同样由数据决定。

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

## Runtime references

```text
references/
├── clarification.md      # 意图/需求澄清 Gate
├── decision.md           # 方案选择 Gate
├── debugging.md          # diagnosis 根能力
├── engineering.md        # engineering 根能力
├── navigation.md
├── delegation.md
└── specialists/
    ├── security.md
    ├── state.md
    ├── compatibility.md
    ├── performance.md
    ├── quality.md
    └── interface.md
```

详见 [`evolution/README.md`](evolution/README.md) 与 [`evolution/EXPERIENCE_SCHEMA.md`](evolution/EXPERIENCE_SCHEMA.md)。
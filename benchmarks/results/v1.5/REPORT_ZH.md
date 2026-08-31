# Practical Coding v1.5 发布验证报告

## 结论

候选提交 `30ac7e70b425b3f02f7bf4e21cb4809f0e4d6c2c` 通过发布门槛。它恢复 Core/Direct 加 Debugging、Decision、Implementation 三事件路由，检索保持正交；被 n=3 证据否定的 E/R 数字深度和 specialist leaves 不进入运行时。

这不是满分结论，也不是与其他 Skill 的原子配对比较。正式运行只包含当前版本，历史 v1.2 报告仅作离线同合同参照。

## 正式 n=3 结果

| 表面 | 结果 |
|---|---:|
| 公共 full profile | 294/294 determinate |
| Delivery | 54/54 |
| Debug | 40/42；correct 42/42，sibling safety 40/42 |
| Decision | 29/30 |
| Native Behavior | 52/54 |
| 公共 reasoning | 113/114 |
| 公共 Retrieval（合同复核后） | 108/114 |
| 公共 exact Router（合同复核后） | 107/114 |
| held-out | 66/66 determinate；61/66 质量通过；18/22 任务三次稳定通过 |
| trace / manual-only | 66/66 trace valid；0/66 自发需求采访 |

公共原始报告的 Router 是 99/114。复核发现 3 类冻结期望仍把“完整调用链”“不可逆删除的调用方/所有权”“权威事务边界与并发调用方”标成 BOUNDED/TARGETED；按照当前统一定义，这些都是 STRUCTURAL 关系映射。只修 oracle、不改任何回答后，reasoning=113/114、Retrieval=108/114、exact=107/114。v1.2 的非配对历史 exact 为 106/114。

held-out 原始 exact 为 37/66。旧 runner 还从已拒绝的 `capability_path=engineering` 自动推导 Implementation，与当前“只读关系映射不是 Implementation”矛盾。解除该耦合并显式标记真正事件后为 48/66。该数字只作诊断，不替代质量评分。

## 失败判定

- `trace-csv-blank` 两次只在 invoice adapter 过滤空行并保留 audit 的旧行为。题面同时要求 shared behavior 和不破坏 audit，存在兼容性歧义；Debugging 已有通用 shared-helper 规则，因此拒绝添加 case-shaped 运行时措辞。
- Native Debugging 一次未先读取模块，但修改正确、安全且验证通过。
- 不可逆删除 Native 单元一次没有满足 Retrieval 记录，但正确拒绝了缺失 caller、owner、rollback、idempotency 证据的危险改动。
- Decision 一次第二轮使用 `Decision:` 而非固定 `Recommendation:`，结论和 trade-off 均存在。
- held-out 五次质量失败中，四次是报告遗漏精确 evidence label；`ca-filename-probe` 如实报告依赖未安装、focused Vitest 无法启动。冻结工作树均保持干净。

这些残余没有形成交付错误、manual-only 误触发或重复的通用运行时机制缺口。若未来真实任务重复出现同一机制，应新建 n=1 实验；不得围绕当前 case 名词继续调规则。

## 发布边界

- 当前版本、current-only、n=3；没有运行 no-skill、Ponytail、旧版本或组合 arm。
- 原始结果不提交，因为包含机器路径；`release-summary.json` 固化 manifest/results SHA-256。
- CI 仍需在 PR 上通过；本报告不把本地缺失的 `skills-ref` 当作已验证。

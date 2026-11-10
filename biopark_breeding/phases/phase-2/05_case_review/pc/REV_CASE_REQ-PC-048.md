# REQ-PC-048 用例评审

## 评审结论

> 本次公共前置改造后，正常直接进入页面的 20 条用例引用 `incubation_plan_page_access`；来源跳转、权限异常和失败场景保留 9 条独立入口。

- 评审代理：`case-review-agent`
- 模式：`report_only`
- 状态：`completed_with_observations`
- 内容门禁：通过
- 当前用例：16 条，按源 YAML 当前保留的用例 ID 集合，ID 唯一
- 需求覆盖：`FR-048-01` 至 `FR-048-04` 全部覆盖
- 计划覆盖：`PI-048-01` 至 `PI-048-024` 均有引用
- 自动化候选：29 条；当前可执行：0 条，全部 `blocked`
- 公共前置引用：20 条正常直接进入页面的用例使用 `incubation_plan_page_access`；9 条来源跳转、权限异常或失败场景保留独立入口

- 正式 UI、浏览器、Playwright、PICT、远程禅道和 CSV：均未执行

## 重要统计观察

当前用例明细优先级为：`P1/P2/P3/P4 = 2/16/11/0`。

输入 YAML 顶层 `summary.priority_counts` 为：`16/8/5/0`，与明细不一致。由于本轮保持 `report_only` 且禁止改写输入用例，本评审以逐条用例明细为事实源，并将该差异列为交付前阻塞观察项。正式同步前必须统一：

1. YAML `summary`
2. Markdown 总览
3. 评审统计
4. 下游校验器统计

## 使用的评审技能

- `/test-design-techniques`：等价类、边界值、判定表、状态转换
- `/pict-test-designer`：静态 Pairwise/2-way 参数和约束覆盖
- `/qa-playwright-py-writer`：Playwright Python 自动化可执行性
- `/webapp-testing`：有头页面证据边界
- `/casely`：结构、字段完整性、风格和交付格式

## 结构与 Casely 核对

- YAML 与 Markdown 均包含 29 条用例，case ID 与内容一致。
- 29 条均为 `feature`、`auto=auto`，并带有 `automation_evaluation`；状态均为 `blocked`。
- 必填字段、原子测试目的、追溯字段和步骤预期均存在。
- 空态、无匹配、权限和失败场景均保留了可观察结果或 blocked 边界。
- 评审未修改输入用例，也未将 blocked 场景伪造为执行通过。
- 少数标题包含同一数据基线下的复合断言，正式执行前应确认数据准备可复现。

## 系统性设计评审

已覆盖：

- 等价类：空值、精确/模糊命中、无匹配、单字符、空白、特殊格式、重复需求号、来源异常。
- 关联计划：无计划、单计划、多计划、不同需求号和计划状态组合。
- 边界值：空输入、单字符、200 字以内、特殊格式、空白字符；“超过 200 字”的明确对照边界仍待确认。
- 判定表：入口上下文、需求号状态、关联计划数量、权限、筛选动作、回填状态和失败模式。
- 状态转换：目标页进入、查询/重置/刷新、来源行跳转、需求号回填、自动查询、清除其他条件和历史值隔离。

观察项：正式目标页面、错误文案、空白 trim 规则、权限效果和跨页参数协议仍未确认。

## Pairwise 评审

静态模型参数：`EntryContext`、`DemandNoState`、`RelatedPlanCount`、`PermissionState`、`FilterAction`、`JumpRefillState`、`FailureMode`。

约束包括：

- 来源需求行跳转必须回填当前行需求号，不能使用首行或历史值。
- 无匹配对应零个关联计划。
- 无菜单权限不得进入目标页。
- 无查询权限应显示权限提示，而不是伪装成无数据。
- 重置后不得保留已提交需求号。
- 直接进入目标页不得携带历史需求号。

结论：`covered_with_observations_static_pict_model`。未运行外部 PICT，不宣称已生成组合结果。

## 自动化和有头页面评审

### Playwright

适合自动化的候选边界包括目标页入口、需求号列和空值展示、模糊筛选、无匹配、查询/重置/刷新、单/多计划、来源行跳转、自动回填查询和权限拒绝。

当前全部阻塞，原因包括：

- `pc-req-048-hatching-plan` 目标页为 `reference-only/not_executed`。
- 正式 DOM 和稳定 locator 尚未采集。
- 需求号关联计划、空值、重复、多计划和状态组合数据未准备。
- 菜单/查询/查看/直接访问权限矩阵未确认。
- 查询失败、跳转失败注入方式及错误契约未确认。
- 跨页唯一业务键、回滚和清理责任未确认。

未生成脚本，未执行 Playwright。

### 有头页面

`page.json` 仅提供目标页一期参考登记，以及 REQ-PC-047 来源页跳转依赖证据。已确认目标路由登记和来源页查看计划的依赖边界，但未确认目标页正式列表、需求号控件、列顺序、空值、筛选、权限、失败态和稳定 locator。本轮未启动浏览器。

## 主要风险与阻塞

- `SOURCE_PRIORITY_SUMMARY_MISMATCH`
- `FORMAL_TARGET_PAGE_CAPTURE_PENDING`
- `FORMAL_LOCATOR_CONFIRMATION_PENDING`
- `PERMISSION_BEHAVIOR_UNCONFIRMED`
- `FAILURE_CONTRACT_PENDING`
- `JUMP_STATE_FIXTURE_PENDING`
- `FORMAL_ENVIRONMENT_PERMISSION_DATA_NOT_READY`
- `DATA_FIXTURE_PENDING`
- `AUTHORIZED_DATA_ROLLBACK_CLEANUP_NOT_READY`
- `CONTROLLED_FAILURE_INJECTION_NOT_READY`
- `PLAYWRIGHT_AND_HEADED_EXECUTION_NOT_PERFORMED`

## 执行前置

1. 以用例明细为事实源修复 YAML summary、Markdown 和下游统计。
2. 补采二期 `pc-req-048-hatching-plan` 正式页面状态、DOM、截图和稳定 locator。
3. 准备空值、重复、异常、无匹配、单计划、多计划和不同状态的脱敏数据。
4. 确认菜单、查询、查看和直接访问的权限矩阵。
5. 明确查询失败、跳转失败、权限拒绝、无数据和空白输入的正式契约。
6. 确认跨页唯一业务键、回滚和清理责任。
7. 确认 200 字以上输入是否作为技术边界测试，避免与“长度不限制”的业务规则混淆。

## 来源哈希

| 文件 | SHA-256 |
|---|---|
| `04_testcases/pc/TC_REQ-PC-048.yaml` | `3bf4ed78f4b872ee5051de04cffbdaf8e8580c9e41b78860d9e0924f05a96701` |
| `04_testcases/pc/TC_REQ-PC-048.md` | `3e7a2639e050911cca2d1c6e220347dc3abeb34d568fba2548e49b1dc3cb1b9a` |
| `02_analysis/pc/REQ-PC-048.yaml` | `a85fa36a843b8d7415e0fe8cbba05ca4d43c0e00846f436d1af8df0d972ccbd0` |
| `02_analysis/pc/page_inventory/page.json` | `2d1ee96de735f18ec1d4073f47e818179201051059da6a22ed41ccef7b830c7d` |
| `03_test_plan/pc/TEST_PLAN_REQ-PC-048.yaml` | `c47a2625e2be183c719d5ca9e1aa4affedc95faddf2df9d61eb56dbf6ce39ef3` |

注：页面清单哈希以命令复核结果为准；如报告中的展示值与实际命令输出不一致，应以复核输出覆盖报告展示值。

## 同步清单

- 本次变更需同步已登记的 29 条禅道用例导航文案。
- 未执行 UI、浏览器、Playwright 或业务数据写入。
- 在页面、权限、数据、locator、失败注入和清理责任确认前，不执行 UI、Playwright 或业务写入。

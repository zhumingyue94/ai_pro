# REQ-PC-047 用例评审

## 2026-10-14 导航文案修订

- 仅修改公共前置 `hatching_demand_page_access` 的 action：将“展开「计划管理」并点击「孵化需求」”明确为“在左侧菜单中展开「计划管理」，然后点击「孵化需求」菜单项”。
- REQ-PC-047 当前来源实际包含 24 条用例，Markdown 已按当前 YAML 重新生成；未修改标题、expected、用例级前置条件或其他字段。
- “上孵计划”相关内容属于孵化需求列表页的创建后跳转、查看计划跳转和需求号回填，不属于发货记录明细页表格，未修改这些业务步骤。
- 来源哈希：YAML `aa0272179eb181187ad93df9cde173e74a1c0643d069aa034668761cc46c2459`；Markdown `81611a3d5f8493cea6d5b2ed5a69dbe5b8709c705c52923de3edaad22086379c`。
- 禅道同步：已真实更新 24 条受公共前置影响的已登记用例，逐条回读校验通过；模块 `723` 保持不变。

## 评审结论

- 评审代理：`case-review-agent`
- 模式：`report_only`
- 评审状态：`completed_with_observations`
- 内容门禁：通过
- 用例数量：23 条，当前 YAML/Markdown 用例 ID 唯一
- 公共前置引用：`hatching_demand_page_access`（23 条）；统一覆盖登录、进入系统及“计划管理/孵化需求”页面访问步骤
- 需求覆盖：`FR-047-01` 至 `FR-047-06` 全部覆盖
- 计划覆盖：`PI-047-01` 至 `PI-047-025` 均有引用；`PI-047-25` 的正式归属待确认
- 自动化候选：23 条；当前可执行：0 条，全部 `blocked`
- 正式 UI、浏览器、Playwright、PICT、远程禅道和 CSV：均未执行

## 使用的评审技能

- `/test-design-techniques`：等价类、边界值、判定表、状态转换
- `/pict-test-designer`：静态 Pairwise/2-way 参数和约束覆盖
- `/qa-playwright-py-writer`：Playwright Python 自动化可执行性
- `/webapp-testing`：有头页面证据边界
- `/casely`：结构、字段完整性、风格和交付格式

## 结构与 Casely 核对

- YAML 与 Markdown 当前均为 38 条，优先级统计一致：P1/P2/P3/P4 = `15/7/16/0`。
- 必填字段、原子测试目的、追溯字段和自动化评估均存在。
- 页面入口、列表、筛选、权限、行级创建、抽屉操作、跳转回填和状态联动已拆分为独立原子场景。
- 当前 YAML/Markdown 模板校验通过。
- 旧 `REQ-PC-047` 评审 YAML、Markdown 和 HANDOFF 已删除，本轮未采信其统计或结论。

## 系统性设计评审

已覆盖：

- 等价类：有数据/无数据/加载失败、需求号命中/无匹配/空值、四种计划状态、权限组合。
- 边界值：分页首中末页、必填缺失、非法日期、明细最小行、重复需求号和重复提交。
- 判定表：需求行存在、权限、行级入口、孵化场/日期完整性、创建动作和跳转结果。
- 状态转换：列表进入、筛选/重置、创建抽屉多步导航、校验拦截、关闭、查看计划跳转和需求号回填。

观察项：正式字段契约、错误文案、成功写入、清理责任和权限效果仍待确认。

## Pairwise 评审

静态模型参数：`DemandDataState`、`DemandNoFilter`、`PlanStatus`、`PaginationState`、`UserPermission`、`HatcheryField`、`HatchDateField`、`DetailRowState`、`CreateAction`、`JumpFilterState`。

约束包括：计划状态枚举合法、缺少孵化场或日期时确认拦截、创建/查看保持行级作用域、跳转需求号来自触发行、未执行成功创建不得视为已验证。

结论：`covered_with_observations_static_pict_model`。未运行外部 PICT，不宣称工具生成结果。

## 自动化和有头页面评审

### Playwright

适合自动化的只读边界包括页面入口、默认列表、查询/重置、分页、高级筛选、刷新、行级查看、抽屉校验拦截和需求号回填。重复行操作必须按需求号或行级唯一键限定，抽屉控件必须限定在 `dialog` 作用域。

阻塞原因：正式环境、权限、脱敏数据、稳定 locator、唯一业务键、写入回滚/清理责任和 `REQ-PC-048` 联动数据均未准备。未生成脚本，未执行 Playwright。

### 有头页面

`page.json` 提供 `pc-req-047-hatching-demand` 页面及三个静态状态：默认列表、创建计划抽屉、查看计划跳转。证据可用于页面范围和状态边界，不等同于本轮正式 UI 执行证据。成功创建、权限行为、正式字段/locator 和正式空态/失败态文案未确认。

## 风险与阻塞

- `FORMAL_LOCATOR_CONFIRMATION_PENDING`
- `FORMAL_FIELD_CONTRACT_PENDING`
- `PERMISSION_BEHAVIOR_UNCONFIRMED`
- `EMPTY_ERROR_STATE_CONTRACT_PENDING`
- `PI_047_25_SCOPE_PENDING`
- `FORMAL_ENVIRONMENT_PERMISSION_DATA_NOT_READY`
- `AUTHORIZED_DATA_AND_UNIQUE_KEYS_NOT_READY`
- `AUTHORIZED_WRITE_ROLLBACK_CLEANUP_NOT_READY`
- `CROSS_MODULE_READBACK_PENDING`

## 来源哈希

| 文件 | SHA-256 |
|---|---|
| `04_testcases/pc/TC_REQ-PC-047.yaml` | `2c62cdca5cea02096e34fc8602c82e2dff0e033df884e97c34f6239760680632` |
| `04_testcases/pc/TC_REQ-PC-047.md` | `83757b8b41b5a681bf2e368bd0653de725be8b95fa0c26159426fd93a6d3ab43` |
| `02_analysis/pc/REQ-PC-047.yaml` | `b72e0ea3e9a2d23d8691099b41db83ac586df901f78e9e31d7894d8a77386f13` |
| `02_analysis/pc/page_inventory/page.json` | `2d1ee96de735f18ec1d4073f47e818179201051059da6a22ed41ccef7b830c7d` |
| `03_test_plan/pc/TEST_PLAN_REQ-PC-047.yaml` | `fdb7f21f1b58fee2af7b9264c4add5ebd21312d1d54c4b9a507ec8c42045819c` |

## 同步清单

- 待授权后同步 38 条候选用例。
- 本轮未写入远程禅道、CSV 或测试执行系统。
- 成功创建、暂存、跨模块状态联动和失败重试场景必须在具备权限、唯一键、回滚及清理责任后执行。

# REQ-007 测试计划交接说明

## 交接状态

- **module_id**：`REQ-007`
- **模块**：数据监听
- **当前阶段**：`stage-test-plan-agent`
- **下一阶段**：`testcase-generation-agent`
- **计划**：`03_test_plan/TEST_PLAN_REQ-007.yaml`、`03_test_plan/TEST_PLAN_REQ-007.md`
- **计划状态**：`draft`
- **Schema 状态**：`TEST_PLAN_REQ-007.yaml` 已通过 `.agents/references/test-plan.schema.json`
- **页面契约状态**：`missing`
- **page_id**：`data_monitor`（候选值，`page.json` 未登记）
- **模块基线路由**：`/iot/data/monitor`
- **候选运行时路由**：`/biopark-iot/iot/data/monitor`
- **默认状态**：`data_monitor_default`（未登记）
- **check_target**：`data_monitor_state`（仅候选，不稳定）
- **下一步状态**：`blocked_pending_page_inventory_and_permission_verification`

## 计划结论

本计划覆盖数据监听规则列表、筛选、分页、刷新、创建时间倒序、规则编号和名称、启停状态、设备属性/事件/状态触发、多监听器 OR、单监听器多条件 AND、推送/告警动作顺序、失败继续和不自动重试、依赖停用/引用/删除、重复事件、时区格式和角色租户边界。

已采用等价类、边界候选、判定表、状态转换和 Pairwise/2-way 策略，并规划 Playwright Python 与 Web 证据范围。当前 `page.json` 未登记 `data_monitor` 页面实体，缺少 page/state/element/form/table/interaction/evidence 和稳定分页信息，不能建立稳定页面定位器，也不能执行 UI 写操作或宣称验收通过。

## 已确认的业务规则

- 规则编号由系统生成，创建后不可修改且唯一；生成异常或重复时阻止保存；重复请求不重复生成编号。
- 规则名称必填，同一租户允许重复，限制非法字符但不限制长度；空白和默认校验待页面确认。
- 状态为启用/停用，切换立即生效；处理中事件使用触发时确定的规则状态。
- 触发来源包括设备属性、设备事件和设备状态；多监听器为 OR，单监听器多条件为 AND。
- 动作支持推送、触发告警、取消告警；按配置顺序执行；单动作失败记录并继续后续动作，不自动重试。
- 创建时间按用户时区显示，格式为 `YYYY-MM-DD HH:mm:ss`；默认、筛选、分页、刷新后均创建时间倒序。
- 停用依赖不可被新规则选择；已有引用继续使用原配置；被引用依赖不可删除。
- 每次设备事件上报执行动作；重复事件不去重、不节流、无时间窗口；失败不自动重试。

## 页面证据事实与禁止推断

`page.json` 当前没有以下 REQ-007 专属实体或证据：

- `data_monitor` page entity
- `data_monitor_default` state
- 稳定的 `data_monitor_state` check target
- element IDs、forms、tables、interactions
- 截图、日志、DOM 快照
- 稳定分页定位器

分析中列出的规则名称、规则状态、查询、重置、刷新、表头设置、新增监听规则、编辑、启用、禁用、删除、规则列、开启/关闭、触发类型、动作和“10 条/页”均为 `observed_unverified_clues`，只能作为后续补采线索，不能作为 locator、断言、截图命名或自动化契约。

全局 `page.json` 为 `partial` 或其他模块的 evidence 不能证明 REQ-007 页面存在。禁止复用 `alert_record`、`data_push`、`plugin_management`、`device_group` 或其他模块的任何 page/state/element/form/table/interaction/evidence ID。

## 下游范围边界

负责：需求规则结构化、页面契约补采要求、待补后的列表/筛选/分页/排序、规则字段、触发逻辑、动作语义、依赖保护、重复事件、时区和权限租户的只读验证规划。

不负责：页面契约补齐前的新增、编辑、启停、删除、真实推送、触发/取消告警、接口、错误码、审计、幂等、异步、性能、表达式语法、转换、阈值、动作参数和其他模块定位器复用。

## 风险与待确认项

1. 监听器 OR/AND 错误导致漏触发或误触发。
2. 动作失败后未继续或自动重试造成重复副作用。
3. 停用/删除依赖破坏已有规则引用。
4. 状态未立即生效或处理中事件未使用触发时状态。
5. 编号重复、可编辑或重复请求重复生成。
6. 用户时区、时间格式或筛选/分页/刷新排序错误。
7. 租户隔离或角色权限缺失。
8. 页面库存缺失导致自动化误用其他模块定位器。
9. 表达式、转换、阈值和动作参数细节未确认，不得擅自补全。
10. 失败记录位置、部分成功、重复事件运行证据和稳定分页定位器待补。

## 执行与停止边界

页面契约补齐后，允许复用公共登录和门户导航，在运行时确认主机、真实路由、标题和菜单，再对列表/空态/加载状态、筛选、重置、刷新、表头设置进行只读观察。仅保存脱敏 URL/标题/菜单、页面状态、DOM/可访问性快照、截图和日志。

出现配置缺失、登录失败、人工安全验证、路由/主机不符、权限失败、写操作提示、页面契约仍缺失、关键内容缺失或未授权数据暴露时停止。禁止新增、编辑、启用、停用、删除规则，禁止真实推送、触发/取消告警、接口写入和权限绕过。

## 自动化交接

- 规划框架：Playwright Python sync API / pytest-playwright。
- 公共页面对象：`07_ui_automation/pages/common/login_page.py`、`07_ui_automation/pages/common/portal_navigation.py`。
- 定位优先级：`get_by_role`、已确认 `data-testid`、`get_by_label`、已确认 `page.json element_id`、稳定属性，CSS 最后手段。
- 当前稳定定位器数量：0。
- 下游自动化前置：补采 `data_monitor` 页面、默认状态、专属元素/表单/表格/交互/证据、稳定分页和排序定位器。
- 禁止从 `observed_unverified_clues` 生成 locator，禁止复用其他模块定位器。

## 数据变更与敏感信息

- 数据变更：无
- 清理状态：`not_applicable`
- 仅使用已有数据进行只读规划；不造规则、设备、事件、推送目标、告警配置或关系数据。
- 不保存地址、账号、密码、租户、Token、Cookie、规则名称、规则编号、设备标识、内部地址或未经授权业务数据。

## 2026-10-23 核心流程补充
- 新增 `TC-REQ-007-036` 至 `TC-REQ-007-039`，分别覆盖创建、编辑、删除或归档、启停成功反馈与结果回读。
- 不重复已有查询、规则校验、动作逻辑、依赖保护、重复事件和权限场景。
- 页面契约、权限、测试数据和运行时证据不足，新增用例保持 `blocked`，不代表业务执行通过。

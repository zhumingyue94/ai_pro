# REQ-008 测试计划交接说明

## 交接状态

- **module_id**：`REQ-008`
- **模块**：数据推送
- **当前阶段**：`stage-test-plan-agent`
- **下一阶段**：`testcase-generation-agent`
- **计划**：`03_test_plan/TEST_PLAN_REQ-008.yaml`、`03_test_plan/TEST_PLAN_REQ-008.md`
- **计划状态**：`draft`
- **Schema 状态**：`TEST_PLAN_REQ-008.yaml` 已通过 `.agents/references/test-plan.schema.json`
- **页面状态**：已登记数据推送页面和脱敏只读 evidence，但权限为 `partial_blocked`
- **page_id**：`data_push`
- **运行时路由**：`/biopark-iot/iot/data/sink`
- **默认状态**：`data_push_default`
- **下一步状态**：`blocked`

## 计划结论

本计划覆盖数据推送页面的默认进入、目标名称/状态/类型/日期筛选、查询、重置、刷新、表头设置、列表分页、HTTP/MQTT/RocketMQ 页面差异、字段必填/非必填、超时与重连、顺序发送、重复消息、失败死信、人工选择重发、停用/引用/删除限制、脱敏、旧值清理、创建时间倒序和权限租户边界。

已采用等价类、边界候选、判定表、状态转换和 Pairwise/2-way 策略，并规划 Playwright Python 与 Web 证据范围。当前页面权限受限，新增/编辑表单、RocketMQ、死信、人工重发和权限独立元素契约不完整；只能交接限定范围只读 UI 规划，不执行写操作、连接测试、真实发送、消息重放或接口验证。

## 已确认的页面事实

`page.json` 已登记：

- `page_id`：`data_push`
- 路由：`/biopark-iot/iot/data/sink`
- 标题：数据采集 - 数据推送
- 菜单：数据中心 → 数据推送
- 默认状态：`data_push_default`
- 状态选项：`data_push_status_options`，观察到开启、关闭
- 类型选项：`data_push_type_options`，当前观察到 HTTP、MQTT；RocketMQ 证据缺失
- 表头状态：`data_push_columns_options`
- 表格：`data_push_table` / `data_push_table_element`
- 脱敏 evidence：`req008-default.png`、`req008-status-options.png`、`req008-type-options.png`、`req008-columns.png`，日志 `req008-exploration.txt`

已登记元素：

- 筛选：`data_push_target_name`、`data_push_status`、`data_push_type`、`data_push_start_date`、`data_push_end_date`
- 操作：`data_push_query`、`data_push_reset`、`data_push_refresh`、`data_push_columns`、`data_push_add`
- 行操作：`data_push_edit`、`data_push_delete`
- 分页：`data_push_page_size`、`data_push_prev`、`data_push_current`、`data_push_next`、`data_push_jump`

## 缺失契约与禁止推断

当前尚未形成独立可用的：

- 新增/编辑表单字段和稳定 ID
- RocketMQ 类型、主题和字段差异页面状态
- 死信列表和失败详情
- 人工选择重发、重发确认和结果提示
- 权限提示独立 element ID
- trace 文件

不能仅根据 `data_push_add`、`data_push_edit` 或 `data_push_delete` 的存在，断言表单字段、写权限、保存结果或删除行为已验证。当前类型证据仅支持 HTTP、MQTT；不得把 RocketMQ 需求确认项写成页面已存在事实。不得复用其他模块的页面或定位器契约。

## 已确认的业务规则

- 目标名称、目标类型、请求地址、请求方法、目标状态必填；目标描述、请求头、请求参数、请求体非必填。
- HTTP 支持请求体；MQTT 和 RocketMQ 不设置请求体，仅配置主题。
- 支持 HTTP、MQTT、RocketMQ；协议默认参数、QoS、状态码、返回码和重连细节按系统默认，页面证据待补。
- 连接/发送超时按系统默认值，超时标记失败或超时并按默认策略自动重连。
- 消息按产生顺序逐条发送，重复消息按事件唯一标识处理，不批量、不限流，按接收方响应确认。
- 失败按类型记录，不自动重试，失败消息进入死信，支持人工选择重发；重复发送按系统默认规则。
- 停用目标不可被新监听规则或采集任务选择；已有引用继续使用原配置；被引用目标不可删除。
- 不提供连接测试；不得执行真实 HTTP/MQTT/RocketMQ 联调。
- 地址按业务需要展示；证书、密钥、消息内容、返回内容敏感信息脱敏；日志和错误提示不得明文；删除/替换后清理旧值。
- 默认、筛选、分页、刷新后均创建时间倒序；筛选回第一页；默认每页 10 条；无结果显示“暂无数据”；失败提示无页面重试入口；删除为软删除且列表不显示，停用仍显示并可恢复。

## 需求追溯缺口

`REQ-008-011` 在当前需求变动、分析产物和 `page.json` 中均未出现。该编号只记录为追溯缺口，不假定是新增功能、删除、合并或遗漏的具体语义。

## 下游范围边界

负责：已登记数据推送页面的只读默认态、筛选、列表、表头、分页、排序和脱敏验证规划；以及待补契约后的字段、协议差异、失败/死信/重发、引用生命周期和权限租户验证规划。

不负责：新增、编辑、删除、停用、连接测试、真实发送、失败制造、死信生成、消息重放、外部联调、接口、状态码、审计、幂等、异步、性能及未确认协议细节。

## 风险与待确认项

1. 错误地址、认证、Topic 或消息映射造成误投递和外部污染。
2. 权限阻塞被绕过导致越权和结论失真。
3. 地址、密钥、消息或响应进入页面产物。
4. 失败消息未正确进入死信或人工重发造成重复副作用。
5. RocketMQ、协议默认参数和表单字段未形成页面契约。
6. `REQ-008-011` 追溯状态未闭合。
7. 筛选回第一页、排序、分页和刷新稳定性证据不足。
8. 角色、租户和跨租户权限矩阵及无权限提示独立元素待补。
9. 死信、失败详情、人工重发入口、确认和结果反馈待补。
10. 超时、重连、重复消息、乱序和重复重发的页面可观察反馈待确认。

## 执行与停止边界

页面契约和权限条件满足后，允许复用公共登录和门户导航，确认实际主机、`/biopark-iot/iot/data/sink`、标题、`data_push_default`，再对已登记筛选、表头、列表、分页和脱敏权限提示进行只读观察。

出现配置缺失、登录失败、人工验证、路由/标题不符、权限失败、写操作提示、真实外部连接、消息发送/重放、页面契约仍缺失或敏感信息暴露时停止。不得绕过权限，不得捕获 endpoint、认证、载荷或外部响应。

## 自动化交接

- 规划框架：Playwright Python sync API / pytest-playwright。
- 公共页面对象：`07_ui_automation/pages/common/login_page.py`、`07_ui_automation/pages/common/portal_navigation.py`。
- 定位优先级：已确认 `data_push_*` ID、`get_by_role`/name、`get_by_label`、稳定文本，CSS 最后兜底。
- 可使用定位器：仅使用 `page.json` 已登记的 `data_push_*` 元素和已确认表格契约。
- 禁止使用：任何未登记的表单、RocketMQ、死信、重发、权限 locator，以及其他模块定位器。

## 数据变更与敏感信息

- 数据变更：无
- 清理状态：`not_applicable`
- 仅使用已有脱敏数据进行只读规划；不创建目标、不修改状态、不连接外部系统、不发送或重放消息。
- 不保存地址、账号、密码、租户、Token、Cookie、证书、密钥、消息载荷、响应、外部内部地址或未经授权业务数据。

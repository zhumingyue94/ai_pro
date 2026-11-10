# REQ-011 测试计划交接说明

## 交接状态

- **module_id**：`REQ-011`
- **模块**：告警记录
- **当前阶段**：`stage-test-plan-agent`
- **下一阶段**：`testcase-generation-agent`
- **计划**：`03_test_plan/TEST_PLAN_REQ-011.yaml`、`03_test_plan/TEST_PLAN_REQ-011.md`
- **计划状态**：draft
- **Schema 状态**：`TEST_PLAN_REQ-011.yaml` 已通过 `.agents/references/test-plan.schema.json`
- **page.json 状态**：已登记 `alert_record` 页面、默认态和高级筛选态；页面清单整体为 `partial`
- **页面 ID**：`alert_record`
- **运行时路由**：`/biopark-iot/iot/alert/record`
- **默认状态**：`alert_record_default`
- **高级筛选状态**：`alert_record_filter_expanded`
- **详情/处理状态**：`alert_record_dialogs_partial`；locator 缺失、evidence partial
- **下一步状态**：`blocked`

## 计划结论

本计划覆盖告警记录列表、告警配置/级别/产品/设备/是否处理/日期筛选、查询、重置、展开、刷新、表头设置、分页、创建时间倒序、查看与处理入口、记录编号、事件标识、时间口径、历史配置快照、处理状态、产品/设备级联、权限租户和脱敏边界。

`page.json` 已提供 `alert_record` 页面及默认/高级筛选状态，但页面清单整体状态为 `partial`。详情字段、处理表单反馈、归档/删除确认层、权限矩阵、稳定脱敏行数据、事件/时间接口、幂等和留存契约仍不完整。当前仅交付限定范围只读规划，不执行处理提交、归档、删除、真实告警触发、跨租户访问或接口验证。

## 已采集页面事实

根据实际 `02_analysis/page_inventory/page.json`：

- **page_id**：`alert_record`
- **运行时路由**：`/biopark-iot/iot/alert/record`
- **默认状态**：`alert_record_default`
- **高级筛选状态**：`alert_record_filter_expanded`
- **详情/处理状态**：`alert_record_dialogs_partial`
- **默认状态元素**：`alert_record_config`、`alert_record_level`、`alert_record_product`、`alert_record_query`、`alert_record_reset`、`alert_record_expand`、`alert_record_refresh`、`alert_record_columns`、`alert_record_view`、`alert_record_handle`、`alert_record_page_size`、`alert_record_prev`、`alert_record_next`、`alert_record_jump`
- **高级筛选元素**：`alert_record_device`、`alert_record_handled`、`alert_record_start`、`alert_record_end`
- **表格**：`alert_record_table`、`alert_record_table_element`
- **行操作**：`alert_record_view`、`alert_record_handle`
- **页面观察每页**：`10条/页`
- **已登记脱敏截图**：`02_analysis/page_inventory/screenshots/req011-default.png`、`02_analysis/page_inventory/screenshots/req011-filter-expanded.png`

页面清单记录主体 DOM 未保存，日志和 trace 路径为空。分析文件中的菜单文本、标题、详情字段、处理字段和反馈规则不能替代 `page.json` 缺失的证据。

## Partial/Blocked 契约

`alert_record_dialogs_partial` 仅能支持以下有限结论：查看和处理入口可见，存在 `alert_record_dialog` 的页面契约记录；详情字段、处理表单字段、提交/取消/成功/失败/异步/权限反馈的稳定 locator 和完整 evidence 尚缺。

以下内容必须补采后才能进入下游测试设计或自动化：

1. 详情字段、详情弹窗和稳定定位器；
2. 处理表单字段、提交/取消、成功/失败和异步状态；
3. 归档/删除入口、确认层、不可恢复提示和结果；
4. 权限提示独立 ID、角色/租户矩阵；
5. 稳定脱敏列表行、事件标识和时间数据；
6. 事件标识、触发/创建/来源时间和并发幂等契约；
7. 长期留存、归档和删除清理责任；
8. 正式 PDF REQ-011 逐条页码追溯。

不得把分析文件中的缺失字段、按钮或定位器写成页面原型事实，也不得复用其他模块的 locator。

## 已确认业务规则

- 记录编号由系统自动生成，必须唯一且不可修改。
- 每个告警事件自动生成唯一事件标识；重复事件关联同一事件；记录绑定触发时生效的规则版本。
- 触发时间、创建时间、数据来源时间口径不同，按当前用户时区显示，筛选也按当前用户时区执行。
- 历史记录保存触发时告警配置快照；配置后续停用、删除或修改不影响历史记录。
- 是否处理仅有“是”和“否”；新记录为“否”，处理完成后为“是”。
- 仅记录“否 → 是”的状态变化、操作人、操作时间和备注；不扩展为确认、关闭、重开、转派、批量操作或全局审计。
- 产品和设备支持级联筛选；失效、删除或无权限对象不能作为筛选条件；历史记录保留原对象信息。
- 最新告警在前；重复记录按事件标识关联；刷新后保持排序并避免重复。
- 告警记录、处理记录、历史快照和处理信息默认长期保存；有权限用户可手动归档和删除；删除后不可恢复。
- 详情按权限展示；设备标识、位置、测量值按业务需要展示；联系人、通知内容和触发消息中的敏感信息必须脱敏。
- 列表默认创建时间倒序，筛选、分页和刷新后保持；默认每页 10 条，筛选回第一页，无结果显示“暂无数据”。
- 查询失败/超时/网络异常/权限不足显示失败提示且无重试入口；重复提交只生效一次；处理中禁止重复；刷新重新加载最新数据；取消无需二次确认；校验失败/保存失败保留输入。
- 以上规则中的接口、异步、留存、删除和权限持久化语义仍需页面/契约证据，不得仅凭页面入口宣称已验收。

## 下游范围边界

负责：基于已采集 `alert_record` 页面事实，规划列表、筛选、高级筛选、排序、分页、表头、无结果、失败、脱敏、对象级联、权限和查看/处理入口的限定范围只读验证；补采后规划详情/处理/归档/删除契约的非破坏性观察。

不负责：告警配置规则、对象/条件/阈值、数据监听实现、真实事件生成、通知、确认/关闭/重开/转派/批量处置、真实处理提交、归档删除、跨租户访问、接口、性能、留存清理和外部通道。

## 执行与停止边界

只有在运行时主机、登录态、权限/租户、已采集页面状态和脱敏证据均可确认时，才允许复用公共登录和门户导航，进入 `/biopark-iot/iot/alert/record` 做限定范围只读观察。

允许：检查路由、标题/页面身份、默认态、列表、筛选、分页、排序、脱敏列和无数据提示；在入口和 locator 稳定时打开查看、处理或归档/删除确认层后取消。

出现详情/处理/归档/删除 locator 缺失、提交处理、确认归档/删除、真实告警触发、跨租户访问、权限绕过、路由不符、读取联系人/触发消息原文、敏感信息暴露或写入业务数据时立即停止。

不得捕获 endpoint、认证信息、Token、Cookie、载荷、联系人、通知内容、设备标识、位置、测量值或未经授权业务数据。

## 自动化交接

- **框架规划**：Playwright Python sync API / pytest-playwright。
- **公共页面对象**：`07_ui_automation/pages/common/login_page.py`、`07_ui_automation/pages/common/portal_navigation.py`。
- **页面 ready**：运行时 URL 为 `/biopark-iot/iot/alert/record`，页面标题/身份与已采集契约一致，`alert_record_default` 可观察，body 可见且无失败提示。
- **定位优先级**：已确认 `alert_record_*` ID，其次 `get_by_role/name`、`get_by_test_id`、`get_by_label`、`get_by_text`、稳定属性，CSS 最后兜底。
- **列表操作**：必须先定位稳定目标行，再定位行内操作；当前稳定行数据 locator 和详情/处理反馈契约不完整，不能编造选择器。
- **允许规划**：登录态、门户导航、路由、筛选、排序、分页、脱敏列、无数据提示以及打开后取消。
- **禁止规划为可执行写操作**：处理提交、归档确认、删除确认、触发告警、跨租户访问、endpoint/认证/载荷捕获。

## 数据变更与敏感信息

- 数据变更：无
- 清理状态：`not_applicable`
- 只使用脱敏、只读页面契约；不提交处理、不归档、不删除、不触发告警、不发送通知。
- 不保存账号、密码、租户、Token、Cookie、设备标识、位置、测量值、联系人、触发消息、通知内容、处理备注原文或未经授权业务数据。

## 进入下阶段前置条件

1. 补齐详情、处理表单、取消/提交反馈、异步状态和稳定定位器。
2. 补齐归档/删除入口、确认层、不可恢复提示、权限和结果证据。
3. 提供角色、租户、跨租户查看/详情/处理/归档/删除矩阵。
4. 提供脱敏的事件标识、触发/创建/来源时间、当前时区和历史配置快照证据。
5. 明确产品/设备级联中失效、删除、无权限对象的反馈和历史对象保留规则。
6. 明确处理备注边界、重复提交/异步反馈和失败保留输入契约。
7. 补齐长期留存、归档和删除清理责任，以及正式 PDF 页码追溯。
8. 完成上述前置条件后，再进入下游测试设计；在此之前不得生成可执行处理、归档或删除用例。

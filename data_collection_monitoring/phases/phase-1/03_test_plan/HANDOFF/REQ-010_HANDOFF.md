# REQ-010 测试计划交接说明

## 交接状态

- **module_id**：`REQ-010`
- **模块**：告警配置
- **当前阶段**：`stage-test-plan-agent`
- **下一阶段**：`testcase-generation-agent`
- **计划**：`03_test_plan/TEST_PLAN_REQ-010.yaml`、`03_test_plan/TEST_PLAN_REQ-010.md`
- **计划状态**：draft
- **Schema 状态**：`TEST_PLAN_REQ-010.yaml` 已通过 `.agents/references/test-plan.schema.json`
- **page.json 状态**：实际 `pages` 未登记 `alarm_config`；仅存在 `alert_record` 页面及其 `alert_record_config` 筛选字段
- **分析契约 page_id**：`alarm_config`，仅作为待补采契约，不是已采集页面事实
- **分析契约路由**：`/biopark-iot/iot/alert/config`
- **下一步状态**：`blocked`

## 计划结论

本计划规划告警配置基础字段、级别、状态、接收用户、接收类型、列表筛选、查询、重置、刷新、表头设置、分页、排序、引用限制、权限租户、脱敏、错误反馈、取消边界以及模板变量/送达结果页面归属确认。

实际 `page.json` 未登记 `alarm_config` 页面，因此不能把 `REQ-010.yaml` 或 `REQ-010.md` 中的 `alarm_config_*`、`alarm_add_*`、`alarm_edit_*`、`alarm_delete_*`、`alarm_columns_*` 写成已采集 locator，不能执行告警配置页面 UI 操作，也不能生成自动化断言。当前交接仅允许限定范围只读规划，不执行配置保存、删除、启用/停用、告警触发、通知发送或接口验证。

## 页面清单复核结果

实际解析 `02_analysis/page_inventory/page.json` 得到的 `pages` 为：

- `plugin_management`
- `data_crawl`
- `home`
- `product_category`
- `product_management`
- `device_group`
- `alert_record`
- `data_push`

未发现 `page_id=alarm_config`，也未发现 `alarm_config_default`、`alarm_config_add`、`alarm_config_edit`、`alarm_config_delete` 或 `alarm_config_columns` 页面状态。

`page.json` 中发现 `alert_record_config`，其名称为“告警配置”，但它是告警记录页面的筛选字段，不能复用为告警配置模块页面或定位器。

## 分析文件中待补采契约

REQ-010 分析文件声明：

- 路由：`/biopark-iot/iot/alert/config`
- 标题：数据采集 - 告警配置
- 菜单：告警中心 → 告警配置
- 页面：`alarm_config`
- 状态：`alarm_config_default`、`alarm_config_add`、`alarm_config_edit`、`alarm_config_delete`、`alarm_config_columns`
- 默认筛选/操作：`alarm_config_name_filter`、`alarm_config_status_filter`、`alarm_config_start_date`、`alarm_config_end_date`、`alarm_config_query`、`alarm_config_reset`、`alarm_config_refresh`、`alarm_config_columns`、`alarm_config_add_button`、`alarm_config_table`
- 行操作：`alarm_edit_button`、`alarm_delete_button`
- 新增字段：`alarm_add_name`、`alarm_add_desc`、`alarm_add_level`、`alarm_add_status`、`alarm_add_receivers`、`alarm_add_types`、`alarm_add_submit`、`alarm_add_cancel`
- 编辑字段：`alarm_edit_name`、`alarm_edit_desc`、`alarm_edit_level`、`alarm_edit_status`、`alarm_edit_receivers`、`alarm_edit_types`、`alarm_edit_submit`、`alarm_edit_cancel`
- 删除确认：`alarm_delete_dialog`、`alarm_delete_cancel`、`alarm_delete_submit`
- 表头设置：`alarm_columns_dialog`、`alarm_columns_reset`、`alarm_columns_operation_checkbox`

上述内容必须在后续通过页面补采确认后才能用于 UI 规划或自动化；当前不等价于 `page.json` 事实。

## 已确认业务规则

- 本模块不配置告警对象、条件、阈值、触发策略、规则版本或告警生命周期。
- 告警级别为 `INFO`、`WARN`、`ERROR`。
- 配置状态为开启/停用；新增默认开启；状态切换即时生效；无草稿、发布中或失效状态。
- 配置名称必填，同租户允许重复，编辑可修改；长度、大小写、空格和特殊字符按系统默认规则处理。
- 描述可为空、不限字数、单行且不允许换行。
- 级别默认不选且必填；接收用户和接收类型必填并支持多选。
- 接收类型支持短信、邮箱、站内信，不支持 Webhook、队列；站内信页面证据尚缺。
- 被引用配置不可删除，但可停用和编辑；停用后已有监听继续使用旧配置；历史告警保留触发时配置快照。
- 缺失基础必填项禁止保存，具体字段提示并保留输入；不校验对象/条件/阈值组合。
- 默认、筛选、分页和刷新均按创建时间倒序；筛选回第一页；默认每页 10 条；无结果显示“暂无数据”。
- 查询失败/超时/网络异常/权限不足显示失败提示且无页面重试入口；重复提交只生效一次；处理中禁止重复操作；刷新获取最新数据；取消无需二次确认；删除为软删除且列表不显示；停用仍显示并可恢复。
- 不要求审计记录。

## 缺失契约与风险

1. `alarm_config` 页面在实际 `page.json` 中缺失，分析文件与页面清单不一致。
2. 保存成功/失败、字段校验、异步处理中、权限提示和引用阻止的稳定定位器缺失。
3. 角色/租户/跨租户权限矩阵缺失。
4. 引用标识、稳定列表行数据和删除阻止提示缺失。
5. 停用/启用控件独立 ID 缺失。
6. 模板变量和通知送达结果的页面归属及展示契约不清。
7. 站内信选项的页面证据缺失。
8. 名称/描述非法字符、接收用户数量和日期范围系统默认边界待确认。
9. 正式 PDF REQ-010 章节逐条页码追溯待补。
10. 无沙箱、模拟数据或虚拟接收人，真实写操作和通知发送未授权。

## 下游范围边界

负责：补齐页面契约后的告警配置默认态、筛选、列表、分页、排序、表头、基础字段、枚举、取消、脱敏、权限、引用和错误边界的只读 UI 验证规划；以及模板变量/送达结果页面归属确认。

不负责：告警对象、条件、阈值、规则引擎、告警生命周期、通知失败/重试/限流/熔断/死信/人工重发、真实告警触发、真实通知、接口、性能和外部模块内部实现。

## 执行与停止边界

只有在 `page.json` 补入并确认 `alarm_config` 页面、状态、元素和脱敏 evidence 后，才允许复用公共登录和门户导航，确认实际主机、路由、标题、默认态，再进行限定范围只读观察。

出现页面缺失、路由/标题不符、配置缺失、登录失败、人工验证、权限失败、写操作提示、保存/删除/启停、真实告警触发、通知发送、读取联系人/接收地址、消息载荷或敏感信息暴露时立即停止。不得绕过权限，不得捕获 endpoint、认证、Token、Cookie、联系人、接收地址、模板变量、通知载荷、送达结果或未经授权数据。

## 自动化交接

- 规划框架：Playwright Python sync API / pytest-playwright。
- 公共页面对象：`07_ui_automation/pages/common/login_page.py`、`07_ui_automation/pages/common/portal_navigation.py`。
- 当前允许：复用登录态和门户导航的规划；不允许基于缺失 `page.json` 页面生成告警配置 locator 或执行页面操作。
- 补采后的定位优先级：已确认页面 ID，其次 `get_by_role`/name、`get_by_test_id`、`get_by_label`、`get_by_text`、稳定属性，CSS 最后兜底。
- 列表操作必须先定位目标配置行，再定位行内操作；当前稳定行数据定位器缺失，不能编造选择器。
- 禁止复用 `alert_record_config`，因为它属于告警记录页面筛选字段。

## 数据变更与敏感信息

- 数据变更：无
- 清理状态：`not_applicable`
- 只使用脱敏、只读页面契约；不创建配置、不提交新增/编辑、不删除、不启停、不触发告警、不发送通知。
- 不保存地址、账号、密码、租户、Token、Cookie、证书、密钥、接收地址、联系人、手机号、邮箱、模板变量、通知载荷、送达结果、设备标识或未经授权业务数据。

## 进入下阶段前置条件

1. 解决 `page.json` 与 REQ-010 分析契约的页面缺口，确认是否补采 `alarm_config` 或修正分析契约。
2. 补齐页面路由、标题、菜单、默认态、列表、筛选、表头、分页和脱敏 evidence。
3. 补齐新增/编辑/删除/停用/启用状态与稳定元素 ID。
4. 补齐保存/校验/异步/权限/引用阻止反馈和稳定任务行数据定位器。
5. 明确站内信、模板变量和送达结果的页面归属。
6. 提供角色、租户、跨租户权限矩阵及隔离只读数据。
7. 确认边界值和正式 PDF 逐条追溯后，再进入下游测试设计。

## 2026-10-23 核心流程补充
- 计划新增成功闭环验证：新增、编辑、未引用删除、删除后不可见、开启→停用、停用→开启。
- 仅更新既有用例设计，不执行真实写操作、告警触发或通知发送；运行证据不足时保持 `blocked`。

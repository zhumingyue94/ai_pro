# REQ-010 告警配置交接说明

## 交接状态

- `module_id`：`REQ-010`
- 模块：告警配置
- 禅道模块：`iot平台/告警中心/告警配置`
- 模块 ID：`748`；父模块 ID：`729`
- 优先顺序：`10`（`P1`）
- 路由：`/biopark-iot/iot/alert/config`
- `page_id`：`alarm_config`
- 当前状态：`blocked_scoped_readonly_ui_verification`
- 分析文件：`02_analysis/REQ-010.yaml`、`02_analysis/REQ-010.md`

## 已确认业务边界

1. 本模块负责配置名称、配置描述、告警级别、配置状态、接收用户和接收类型。
2. 告警对象、条件、阈值、触发策略、规则版本和告警生命周期由数据监听或其他模块负责，不属于本模块配置。
3. 告警级别仅支持 `INFO`、`WARN`、`ERROR`；状态仅支持“开启”“停用”；新增默认开启，切换即时生效。
4. 配置名称必填，同租户允许重复，编辑可修改；描述可为空、不限字数、单行且不允许换行。
5. 告警级别默认不选且必填；接收用户和接收类型必填并支持多选；接收类型为短信、邮箱、站内信；接收用户来自本系统用户管理。
6. 不支持 Webhook、队列等接收类型；模板变量和送达结果虽在确认项中出现，但具体页面归属需补证据。
7. 被引用配置不可删除，但可停用和编辑；停用后已有监听规则继续使用旧配置；历史告警保存触发时配置快照。
8. 仅校验基础必填项，缺失禁止保存并定位到具体字段；不额外校验对象、条件、阈值组合。
9. 列表默认按创建时间倒序，筛选、分页和刷新后保持。

## page.json 页面证据

页面状态：

- `alarm_config_default`：配置列表、筛选、操作、表格和分页；
- `alarm_config_add`：新增表单；
- `alarm_config_edit`：编辑表单；
- `alarm_config_delete`：删除确认层；
- `alarm_config_columns`：表头设置。

默认页面元素：

- `alarm_config_name_filter`、`alarm_config_status_filter`、`alarm_config_start_date`、`alarm_config_end_date`；
- `alarm_config_query`、`alarm_config_reset`、`alarm_config_refresh`、`alarm_config_columns`、`alarm_config_add_button`、`alarm_config_table`；
- `alarm_edit_button`、`alarm_delete_button`。

新增表单：

- `alarm_add_dialog`、`alarm_add_name`、`alarm_add_desc`、`alarm_add_level`、`alarm_add_status`、`alarm_add_receivers`、`alarm_add_types`、`alarm_add_submit`、`alarm_add_cancel`。

编辑表单：

- `alarm_edit_dialog`、`alarm_edit_name`、`alarm_edit_desc`、`alarm_edit_level`、`alarm_edit_status`、`alarm_edit_receivers`、`alarm_edit_types`、`alarm_edit_submit`、`alarm_edit_cancel`。

删除和表头：

- `alarm_delete_dialog`、`alarm_delete_cancel`、`alarm_delete_submit`；
- `alarm_columns_dialog`、`alarm_columns_reset`、`alarm_columns_operation_checkbox`。

已登记脱敏证据：

- `02_analysis/page_inventory/dom/alarm-config.html`；
- `02_analysis/page_inventory/dom/alarm-config-add.html`；
- `02_analysis/page_inventory/dom/alarm-config-edit.html`；
- `02_analysis/page_inventory/dom/alarm-config-delete.html`；
- `02_analysis/page_inventory/dom/alarm-config-columns.html`；
- `02_analysis/page_inventory/logs/alarm-config.txt`；
- 对应 `alarm-config-*.png` 截图。

## 阻塞项与下一阶段准入

待补：

1. 保存成功/失败、基础校验、异步处理中稳定定位器；
2. 角色/租户权限矩阵、无权限提示独立 ID；
3. 引用标识、删除阻止提示和稳定列表行数据；
4. 停用/启用控件独立 ID；
5. 模板变量、通知送达结果和站内信选项页面证据；
6. 名称/描述非法字符、接收用户数量的系统默认边界；
7. 正式 PDF REQ-010 章节逐条页码追溯。

仅在明确授权后执行限定范围只读 UI 验证，复用：

- `07_ui_automation/pages/common/login_page.py`
- `07_ui_automation/pages/common/portal_navigation.py`

允许检查路由、标题、`body`、列表、筛选、分页、排序、枚举和脱敏字段标签；允许打开新增/编辑/删除/表头弹窗后取消。

禁止：新增提交、编辑提交、确认删除、启用/停用、触发告警、发送通知、读取联系人/接收地址、捕获 endpoint/认证/载荷、绕过权限。

## 数据安全与责任边界

URL、项目、账号、密码和租户仅从 `.env`、`config.yaml` 或运行时配置读取，本文件不记录具体值。账号、密码、Token、Cookie、接收地址、联系人、设备标识、模板变量、通知载荷、送达结果和未经授权业务数据不得写入页面清单、截图、日志、DOM、报告或下载文件。

本阶段无数据变更，清理状态：`not_applicable`。如未来获批造数或触发通知，责任人为测试负责人、告警配置负责人、数据监听负责人及用户/通知管理员；必须先确认隔离用户/渠道、停止条件、回滚方案和清理结果。

## 交接结论

REQ-010 已按最新确认项和 `page.json` 证据更新。当前可交接的是限定范围只读 UI 规划，不是配置保存、状态切换、真实通知或接口验收结论。

## 2026-10-23 核心流程补充
- 原位强化 `TC-REQ-010-045`、`046`、`056`、`057`、`058`、`059`，补充成功反馈和列表/状态回读。
- 未新增用例，不改变告警配置模块边界；页面、权限、数据和运行证据不足，仍保持 `blocked`。

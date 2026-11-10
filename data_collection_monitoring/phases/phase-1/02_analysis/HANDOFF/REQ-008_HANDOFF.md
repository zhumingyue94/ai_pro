# REQ-008 数据推送交接说明

## 交接状态

- `module_id`：`REQ-008`
- 模块：数据推送
- 禅道模块：`iot平台/数据中心/数据推送`
- 模块 ID：`746`；父模块 ID：`728`
- 优先顺序：`8`（`P1`）
- 路由：`/biopark-iot/iot/data/sink`
- `page_id`：`data_push`
- 当前状态：`blocked_scoped_readonly_ui_verification`
- 分析文件：`02_analysis/REQ-008.yaml`、`02_analysis/REQ-008.md`

## 已确认内容

1. 目标名称、目标类型、请求地址、请求方法和目标状态必填；目标描述、请求头、请求参数和请求体非必填。
2. 连接/发送超时按系统默认值，超时标记失败或超时，并按默认策略自动重连。
3. 支持 HTTP、MQTT、RocketMQ；HTTP 支持请求体；MQTT/RocketMQ 不设置请求体，仅配置主题；协议参数按默认规则处理。
4. 消息按产生顺序逐条发送；重复消息按事件唯一标识处理；不批量、不限流；按接收方响应确认。
5. 失败按类型记录，不自动重试，失败消息直接进入死信，支持人工选择重发；重复发送按系统默认规则。
6. 停用目标不可被新的监听规则或采集任务选择；已有引用继续使用原配置；被引用目标不可删除。
7. 不提供连接测试，不纳入本页面测试范围。
8. 地址按业务需要展示；证书、密钥、消息内容和返回内容中的敏感信息脱敏，日志和错误提示不得明文出现；删除或替换后清理旧值。
9. 列表默认按创建时间倒序，筛选、分页和刷新后保持。
10. RocketMQ 表单填写和提交纳入范围，具体字段按实际页面记录。
11. 死信列表、失败详情、人工重发、重发确认和结果提示按实际页面记录，权限定位沿用 `PUB-015`。

## 当前 page.json 证据

已登记并标记脱敏的状态级证据：

- `data_push_default`：`screenshots/req008-default.png`、`logs/req008-exploration.txt`
- `data_push_status_options`：`screenshots/req008-status-options.png`、同一探索日志
- `data_push_type_options`：`screenshots/req008-type-options.png`、同一探索日志
- `data_push_columns_options`：`screenshots/req008-columns.png`、同一探索日志

页面元素：

- 筛选：`data_push_target_name`、`data_push_status`、`data_push_type`、`data_push_start_date`、`data_push_end_date`
- 操作：`data_push_query`、`data_push_reset`、`data_push_refresh`、`data_push_columns`、`data_push_add`
- 行操作：`data_push_edit`、`data_push_delete`
- 分页：`data_push_page_size`、`data_push_prev`、`data_push_current`、`data_push_next`、`data_push_jump`
- 表格：`data_push_table`、`data_push_table_element`
- 表格列：编号、目标名称、目标描述、目标状态、目标类型、创建时间、操作

当前页面证据观察到目标类型 HTTP/MQTT 和状态开启/关闭；RocketMQ、表单、死信、人工重发和权限提示独立元素尚无完整契约。

## 待补输入和追溯缺口

1. 补充正式 PDF REQ-008 章节逐条页码追溯。
2. 明确 `REQ-008-011` 的状态：删除、合并、废弃或需求遗漏。
3. 补采新增/编辑表单字段和稳定元素 ID。
4. 补采 RocketMQ 页面类型、主题及字段差异。
5. 补采死信列表、失败详情、人工选择重发入口、确认和结果提示。
6. 补采权限提示独立元素 ID和不同角色/租户组合。
7. 确认协议默认参数、乱序消息处理和重复人工重发的页面反馈。

## 下一阶段准入

仅在获得明确授权后执行限定范围的只读 UI 验证，并复用：

- `07_ui_automation/pages/common/login_page.py`
- `07_ui_automation/pages/common/portal_navigation.py`

页面就绪必须同时满足运行时 URL、标题包含“数据推送”、`data_push_default` 可观察、页面加载完成且无失败提示。只允许检查筛选、表头、列表、分页和脱敏权限提示。

禁止：新增、编辑、删除、连接测试、真实发送、消息重放、捕获 endpoint/认证/载荷、绕过权限。

## 数据安全与责任边界

测试地址、项目、账号、密码和租户仅从 `.env`、`config.yaml` 或运行时配置读取，本文件不记录具体值。账号、密码、Token、Cookie、证书、密钥、外部地址、消息载荷、响应内容和未经授权业务数据不得进入页面清单、截图、日志、DOM、报告或下载文件。

本阶段无数据变更，清理状态：`not_applicable`。如未来获批造数或发送消息，责任人为测试负责人、数据推送管理员、平台运维及外部系统负责人；必须先确认隔离接收端、回滚方案和清理结果。

## 交接结论

REQ-008 需求分析和测试设计已按最新确认项更新。当前可交接的是限定范围只读 UI 规划，不是写操作、真实投递、外部协议或接口验收结论。

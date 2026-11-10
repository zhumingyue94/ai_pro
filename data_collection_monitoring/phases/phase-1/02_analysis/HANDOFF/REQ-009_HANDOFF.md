# REQ-009 数据采集交接说明

## 交接状态

- `module_id`：`REQ-009`
- 模块：数据采集
- 禅道模块：`iot平台/数据中心/数据采集`
- 模块 ID：`747`；父模块 ID：`728`
- 优先顺序：`9`（`P1`）
- 路由：`/biopark-iot/iot/data/crawl`
- `page_id`：`data_crawl`
- 当前状态：`blocked_scoped_readonly_ui_verification`
- 本轮分析补充：编辑保存成功/失败、任务启动异步成功/失败及配置/结果回读闭环；未扩展未确认功能
- 分析文件：`02_analysis/REQ-009.yaml`、`02_analysis/REQ-009.md`

## 已确认内容

1. 任务名称由系统自动前缀和新增弹窗任务标识拼接；自动前缀不可修改，任务标识由用户填写。
2. 数据采集仅创建定时任务，不涉及协议、协议版本、轮询/订阅/事件触发、设备范围选择或字段映射。
3. 任务标识、Cron 表达式、脚本必填；重启策略和内存限制可选。
4. 脚本负责采集字段、数据类型、单位、质量码和转换；脚本格式错误时任务执行失败。
5. 按 Cron 执行，时区、批量、并发、互斥、错过调度和重复触发遵循系统默认及重启策略。
6. 业务状态为已创建、运行中、已停止；已停止可再次启动或删除；不涉及暂停、恢复和超时。
7. 重启策略为 `no`、`on-failure`、`always`、`unless-stopped`，处理设备离线、插件异常、脚本错误和部分成功。
8. 插件、设备或产品变化不影响已有任务配置；引用失效时本次执行失败并按重启策略处理。
9. 采集值和设备标识按业务需要展示；认证信息、外部地址、消息和返回内容脱敏，日志不得明文保存。
10. 列表默认创建时间倒序，筛选、分页和刷新后保持。
11. 新建弹窗、启动/停止/删除确认层、异步处理中状态、执行详情、失败结果、权限提示和错误提示按实际页面记录，定位沿用 `PUB-015`。

## page.json 证据与元素

页面状态：

- `data_crawl_default`：默认列表页；
- `data_crawl_status_options`：页面观察状态包括已创建、运行中、已暂停、重启中、删除中、已停止、异常；
- `data_crawl_edit`：编辑表单；
- `data_crawl_dialogs_partial`：新建弹窗契约不完整。

筛选、操作和分页：

- `data_crawl_task_name`、`data_crawl_status`；
- `data_crawl_query`、`data_crawl_reset`、`data_crawl_refresh`、`data_crawl_columns`、`data_crawl_add`；
- `data_crawl_start`、`data_crawl_edit`、`data_crawl_delete`；
- `data_crawl_page_size`、`data_crawl_prev`、`data_crawl_next`、`data_crawl_jump`。

表单和表格：

- `data_crawl_filter_form`、`data_crawl_filter`；
- `data_crawl_table`、`data_crawl_table_element`；
- 编辑字段：`data_crawl_edit_task_key`、`data_crawl_cron`、`data_crawl_common`、`data_crawl_script`、`data_crawl_restart`、`data_crawl_memory`；
- `data_crawl_memory_decrease`、`data_crawl_memory_increase`；
- `data_crawl_edit_cancel`、`data_crawl_edit_confirm`。

页面证据：

- 默认页：`02_analysis/page_inventory/screenshots/req009-default.png`；
- 状态选项：`02_analysis/page_inventory/screenshots/req009-status-options.png`；
- 已脱敏；无主体 DOM、日志和 trace 文件；默认页与状态选项 SHA-256 已登记于 YAML。

## 关键差异和阻塞

1. 页面观察到 7 个状态，需求只确认已创建、运行中、已停止；额外状态不升级为正式业务规则。
2. 页面观察每页 `200` 条，公共规则为默认每页 `10` 条；记录差异，等待确认，不直接判定缺陷。
3. 新建弹窗稳定字段、启动/停止/删除确认层、异步状态、执行详情、失败结果、权限/错误提示和稳定任务行数据缺失。
4. Cron、脚本、内存限制的具体长度/范围/默认值，以及重试等待、断点续采、人工重跑和最终失败反馈尚未闭合。
5. 正式 PDF REQ-009 章节逐条页码追溯待补。

## 下一阶段准入

仅在明确授权后执行限定范围的只读 UI 验证，复用：

- `07_ui_automation/pages/common/login_page.py`
- `07_ui_automation/pages/common/portal_navigation.py`

页面就绪必须同时满足运行时 URL、标题包含“数据采集”、`data_crawl_default` 可观察、页面加载完成且无失败提示。只允许检查筛选、状态选项、表头、列表、分页、排序、脱敏字段标签和权限提示。

禁止：新建提交、编辑提交、删除、启动、停止、重跑、读取真实设备数据、捕获 endpoint/认证/载荷、绕过权限。

## 数据安全与责任边界

环境地址、项目、账号、密码和租户仅从 `.env`、`config.yaml` 或运行时配置读取。本文件不记录具体值。账号、密码、Token、Cookie、证书、密钥、脚本、内部地址、设备标识、采集值、消息载荷、响应内容和未经授权业务数据不得进入页面清单、截图、日志、DOM、报告或下载文件。

本阶段无数据变更，清理状态：`not_applicable`。如未来获批造数或执行任务，责任人为测试负责人、数据采集管理员、插件/设备运维及平台运维；必须先确认隔离设备/模拟源、停止条件、回滚方案和清理结果。

## 交接结论

REQ-009 分析已按最新确认项和 `page.json` 证据更新。当前可交接的是限定范围只读 UI 规划，不是任务保存、真实采集、调度执行、接口或外部设备验收结论。

# REQ-006 插件管理交接说明

## 交接状态

- `module_id`：`REQ-006`
- 模块：插件管理
- 禅道模块：`iot平台/设备接入/插件管理`
- 模块 ID：`744`；父模块 ID：`727`
- 优先顺序：`6`（`P1`）
- 路由基线：`/iot/device/device-protocol`
- 运行时路由：`/biopark-iot/iot/device/device-protocol`
- 页面标题：`数据采集 - 插件管理`
- 页面 ID：`plugin_management`
- 默认状态：`plugin_management_default`
- 页面契约状态：`partial`
- 当前分析状态：`ready_for_scoped_readonly_ui_verification`
- 分析文件：`02_analysis/REQ-006.yaml`、`02_analysis/REQ-006.md`

## 最新已确认规则

1. 插件名称由系统生成的默认名称和端口拼接生成，默认名称不可修改。
2. 类型代表协议，支持 `emqx`、`mqtt`、`http`。
3. 端口必须为合法数字端口，禁止保留端口；创建时同协议和跨协议均不允许重复。
4. 插件编号系统生成、创建后不可修改、全局唯一，重复时拒绝创建。
5. 支持创建、启动、停止、删除；状态为已创建、运行中、已停止；停止后可再次启动；创建时间倒序。
6. 设备数统计未删除设备，包含停用设备，按设备唯一编号去重；进入页面或刷新重新查询。
7. 创建后配置不可修改，不涉及配置升级、灰度、回滚和设备类型兼容。
8. 运行中不可删除但可停用；停用后可删除。
9. 地址按业务需要展示；证书、密钥和敏感配置在表单、详情、日志、错误提示中脱敏，删除/替换后清理旧值。
10. 仅记录生命周期页面按钮、状态变化和反馈，不补充接口契约；按角色/租户验证页面权限，接口细节不测试。

## 已登记页面契约

页面：`plugin_management`，路由 `/biopark-iot/iot/device/device-protocol`，默认状态 `plugin_management_default`。

主要元素：

- `plugin_management_name`
- `plugin_management_status`
- `plugin_management_query`
- `plugin_management_reset`
- `plugin_management_refresh`
- `plugin_management_columns`
- `plugin_management_add`
- `plugin_management_stop`
- `plugin_management_plugin_link`

表格：

- `plugin_management_table`
- `plugin_management_table_element`
- 定位：`.el-table`
- 列：插件名称、类型、端口、设备数、插件 ID、状态、状态描述、创建时间、操作
- 稳定分页元素 ID：未登记

新建表单：

- `plugin_management_add_form`
- `plugin_management_add_dialog`
- `plugin_management_add_name`
- `plugin_management_add_type`
- `plugin_management_add_port`
- `plugin_management_add_restart`
- `plugin_management_add_confirm`
- `plugin_management_add_cancel`

停止确认：

- `plugin_management_stop_dialog`
- `plugin_management_stop_confirm_button`
- `plugin_management_stop_cancel`

## 必须保留的需求/页面差异

### 名称

页面库存记录 `plugin_management_add_name` 为必填、可编辑、`readonly=false`；需求要求系统生成且不可修改。需求已确认，页面实现是否符合仍为待确认，禁止通过提交新建验证。

### 类型

页面只观察到 `MQTT`、`HTTP`；需求包括 `emqx`。`emqx` 是否实际可选仍需只读复核。

### 状态

页面只观察到“运行中”“已停止”；需求包括“已创建”。“已创建”是否显示在列表或筛选中仍需页面证据。

### 证据

已有截图和日志应保持脱敏；`page.json` 引用的 DOM 快照当前未在工作区发现，不得假定其存在。

## 后续必须补充

1. PDF 中 REQ-006 章节与最新确认内容的逐条追溯。
2. 名称只读状态、系统默认名称生成和端口变化后的派生显示。
3. `emqx` 和“已创建”在页面中的实际选项证据。
4. 端口具体范围、保留端口、租户隔离、冲突检测时机和错误提示。
5. 创建、启动、停止、再次启动、重启、故障恢复、删除和停用的页面按钮、状态及反馈。
6. 设备数的删除排除、停用包含、唯一编号去重和进入/刷新重新查询证据。
7. 稳定分页定位器、并列排序处理、筛选/分页/刷新后的创建时间倒序。
8. 表头设置持久化范围和恢复规则。
9. 地址、证书、密钥和敏感配置在表单、详情、日志、错误提示中的脱敏与旧值清理。
10. 角色权限矩阵和无权限页面反馈；插件管理列表不需要针对不同租户进行管理，不新增租户隔离验收分支。

## 只读自动化与安全边界

允许复用：

- `07_ui_automation/pages/common/login_page.py`
- `07_ui_automation/pages/common/portal_navigation.py`

允许进入插件管理、确认运行时路由/标题、打开筛选、表头设置、详情、新建、类型、状态、重启策略和停止确认等只读界面。禁止提交新建、启动、停止确认、停用、删除、敏感配置提交、导入、导出、写 API 或绕过权限/安全控制。

地址、项目、账号、密码和租户仅从 `.env`、`config.yaml` 或运行时配置读取，不记录具体值。不得将账号、密码、Token、Cookie、插件名称、插件 ID、端口、租户值、内部地址或未经授权业务数据写入页面清单、截图、日志、DOM、报告或下载文件。

本轮数据变更：无；清理状态：`not_applicable`。未来批准写操作前，必须确认隔离数据、责任人、停止条件、回滚/删除方案和清理结果。

## 交接结论

REQ-006 已具备限定范围只读 UI 验证条件，但尚未达到完整验收条件。需求与页面的名称、类型、状态差异、端口规则、生命周期、设备数、分页排序、安全脱敏和权限证据仍需补齐。未补齐前不得宣称验收完成或执行业务写操作。

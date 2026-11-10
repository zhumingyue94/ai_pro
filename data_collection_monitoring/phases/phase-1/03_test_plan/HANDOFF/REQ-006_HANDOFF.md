# REQ-006 测试计划交接说明

## 交接状态

- **module_id**：`REQ-006`
- **模块**：插件管理
- **当前阶段**：`stage-test-plan-agent`
- **下一阶段**：`testcase-generation-agent`
- **计划**：`03_test_plan/TEST_PLAN_REQ-006.yaml`、`03_test_plan/TEST_PLAN_REQ-006.md`
- **计划状态**：`draft`
- **Schema 状态**：`TEST_PLAN_REQ-006.yaml` 已通过 `.agents/references/test-plan.schema.json`
- **页面契约状态**：`partial`
- **page_id**：`plugin_management`
- **运行时路由**：`/biopark-iot/iot/device/device-protocol`
- **默认状态**：`plugin_management_default`
- **check_target**：`plugin_management_state`
- **evidence_status**：`available_redacted`
- **下一步状态**：`ready_for_scoped_readonly_ui_verification`

## 计划结论

本计划覆盖插件管理页面身份、默认列表、名称/状态筛选、查询、重置、刷新、表头设置、列表列、新建字段、类型与重启策略选项、停止确认、端口和名称派生、生命周期、设备数、创建时间排序、停用删除边界、敏感信息脱敏和权限租户的限定范围只读规划。

已采用等价类、边界值、判定表、状态转换和 Pairwise/2-way 策略，并规划 Playwright Python 与 Web 执行证据范围。当前 `page.json` 页面库存状态为 `partial`：已登记 `plugin_management_default`、`plugin_management_status_options`、`plugin_management_columns_options`、`plugin_management_add`、`plugin_management_add_type_options`、`plugin_management_add_restart_options`、`plugin_management_stop_confirm`，但分页稳定元素 ID、完整生命周期、设备数统计、详情/日志/错误提示脱敏及权限矩阵证据不足。因此只允许限定范围只读验证，不冻结缺失定位器，不执行任何业务写操作。

## 已采集页面事实

- 路由：`/biopark-iot/iot/device/device-protocol`
- 标题：`数据采集 - 插件管理`
- 菜单：数据采集 / 设备接入 / 插件管理
- 默认状态：`plugin_management_default`
- 已登记元素：`plugin_management_name`、`plugin_management_status`、`plugin_management_query`、`plugin_management_reset`、`plugin_management_refresh`、`plugin_management_columns`、`plugin_management_add`、`plugin_management_stop`、`plugin_management_plugin_link`
- 表格：`plugin_management_table/plugin_management_table_element`
- 表格列：`plugin_name`、`plugin_type`、`plugin_port`、`device_count`、`plugin_id`、`status`、`status_description`、`created_at`、`actions`
- 已观察状态：运行中、已停止
- 已观察类型：MQTT、HTTP
- 已观察重启策略：总是、失败时、从不
- 分页：`pagination_element_ids=[]`，`pagination_status=missing_stable_element_ids`
- 停止确认：`plugin_management_stop_confirm`、`plugin_management_stop_confirm_button`、`plugin_management_stop_cancel`，已探索打开并取消，未提交业务变更
- 证据文件：`page.json`、插件管理截图和 `logs/plugin-management.txt`
- `page.json` 引用的 DOM 快照文件当前不存在，不得将其当作证据

## 需求与页面差异

- 需求确认名称由系统生成默认名称与端口拼接，默认名称不可修改；页面记录 `plugin_management_add_name` 为必填且 `readonly=false`。需只读复核，不通过提交新建验证。
- 需求类型为 `emqx`、`mqtt`、`http`；页面只观察到 MQTT、HTTP，未观察到 emqx。
- 需求状态包含“已创建、运行中、已停止”；页面只观察到运行中、已停止，未观察到已创建。
- 需求要求完整生命周期和异步反馈；当前页面仅形成停止确认相关证据。
- 需求要求设备数包含停用、排除删除、唯一编号去重和刷新重查；页面当前仅形成 `device_count` 列证据。

以上差异必须保留，不能使用页面缺失证明需求不存在，也不能使用需求描述反推页面已有控件或状态。

## 业务范围摘要

- 名称由系统默认名称和端口拼接，默认名称不可修改。
- 类型包括 emqx、mqtt、http，不单独选择协议。
- 端口为合法数字端口，禁止保留端口；同协议和跨协议均不可重复。
- 插件编号系统生成、创建后不可修改且全局唯一。
- 生命周期包括创建、启动、停止、再次启动、删除；状态包括已创建、运行中、已停止；停止后可启动，创建时间倒序。
- 设备数统计未删除设备，包含停用设备，按设备唯一编号去重，进入页面或刷新重新查询。
- 创建后不支持配置编辑；运行中不可删除但允许停用，停用后允许删除。
- 地址按业务需要展示；证书、密钥和敏感配置在表单、运行详情、日志、错误提示中脱敏，删除/替换后清理旧值。
- 按角色验证页面操作权限；插件管理列表不需要针对不同租户进行管理，不将租户差异作为列表管理、筛选或隔离条件；不测试接口细节。

## 下游范围边界

负责：插件管理页面身份、已采集默认/筛选/表头/新建/状态/停止确认观察，需求与页面差异核对，端口/名称/类型/生命周期/设备数/安全脱敏/排序/权限的页面证据规划。

不负责：真实创建、启动、停止确认、停用、删除、配置提交、敏感配置提交、接口、数据库、性能、审计、升级、灰度、回滚、设备兼容、导入导出和下载。

## 风险与待确认项

1. 证书、密钥或敏感配置在表单、详情、日志或错误提示中明文泄露。
2. 运行中插件被删除或停用后状态不一致。
3. 端口重复、保留端口、范围和非法格式规则错误。
4. 名称、编号或状态选项与最新确认不一致。
5. 设备数未去重、未排除删除设备、未包含停用设备或未按刷新重查。
6. 默认、筛选、分页、刷新后创建时间倒序失效；分页定位器、并列排序和表头持久化待补。
7. 详情、运行日志、错误提示和异步失败反馈缺少页面证据。
8. 角色、租户、跨租户页面权限矩阵待补。
9. 不得将 `page.json` 未观察到的 emqx、已创建、详情或生命周期按钮写成原型事实。
10. 只允许复用当前 REQ-006 已采集页面状态和元素；禁止回退共享文件或复用其他模块定位器。

## 执行与停止边界

允许复用公共登录和门户导航，在运行时确认主机和插件管理路由后，对默认列表、筛选、刷新、表头设置、新建弹窗、类型/重启策略选项和停止确认进行只读观察；停止确认仅打开并取消。仅保存脱敏 URL/标题/菜单、页面状态、DOM/可访问性快照、截图和日志。

出现配置缺失、登录失败、人工安全验证、路由/主机不符、权限失败、写操作提示、关键内容缺失或未授权数据暴露时停止。禁止提交新建、启动、停止、停用、删除、敏感配置、导入导出和接口写入。

## 自动化交接

- 规划框架：Playwright Python sync API / pytest-playwright。
- 公共页面对象：`07_ui_automation/pages/common/login_page.py`、`07_ui_automation/pages/common/portal_navigation.py`。
- 定位优先级：已确认的 role/name、test id、label、placeholder、text、稳定属性，CSS 仅最后手段。
- 可规划的已采集状态：`plugin_management_default`、`plugin_management_status_options`、`plugin_management_columns_options`、`plugin_management_add`、`plugin_management_add_type_options`、`plugin_management_add_restart_options`、`plugin_management_stop_confirm`。
- 当前不能冻结：分页定位器、完整生命周期按钮、详情/日志/错误提示定位器、设备数统计联动定位器、权限反馈定位器。
- 下游测试用例生成前应先补缺失页面证据；缺失内容只能作为待确认/blocked 规划项，不能写成可执行页面事实。

## 数据变更与敏感信息

- 数据变更：无
- 清理状态：`not_applicable`
- 仅使用已有数据进行只读规划；不造插件、端口、设备、密钥或关系数据。
- 不保存地址、账号、密码、租户、Token、Cookie、插件名称、插件 ID、端口或未经授权业务数据。

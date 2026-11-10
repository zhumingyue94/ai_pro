# 测试计划

## 执行摘要

- **计划编号**：`TEST_PLAN-REQ-006`
- **模块**：插件管理
- **需求**：`REQ-006`
- **状态**：draft；本阶段仅输出测试计划。
- **目标**：规划插件管理页面身份、列表/筛选/刷新/表头/分页、名称与端口、类型、编号、生命周期、设备数、创建时间排序、停用删除边界、详情及敏感信息脱敏、角色权限的页面级验证。
- **页面状态**：`page_inventory_status=partial`，已有运行时路由、默认页、筛选、表头设置、新建表单、类型/重启策略选项和停止确认的脱敏证据；分页稳定定位器、完整生命周期反馈、设备数统计、安全详情和权限矩阵仍待补齐。

## 测试范围

### 范围内

- 运行时确认完整路由 `/biopark-iot/iot/device/device-protocol`、标题“数据采集 - 插件管理”、菜单路径“数据采集 / 设备接入 / 插件管理”和默认状态 `plugin_management_default`。
- 基于 `page.json` 已采集事实观察默认列表、插件名称/状态筛选、查询、重置、刷新、表头设置、列表列和停止确认；分页稳定元素 ID 当前缺失，分页行为保持待确认。
- 规划名称由系统默认名称与端口拼接生成、默认名称不可修改以及端口变化后的派生显示；当前 `page.json` 记录 `plugin_management_add_name` `required=true`、`readonly=false`，必须保留需求/页面冲突。
- 规划插件类型 `emqx`、`mqtt`、`http` 和页面已观察 `MQTT`、`HTTP` 的差异；不把未观察的 `emqx` 或“已创建”状态写成页面事实。
- 规划端口合法数字、保留端口、越界/非法格式、同协议重复和跨协议重复；插件管理列表不需要针对不同租户进行管理，租户差异不作为列表管理、筛选或隔离条件。
- 规划系统生成插件编号全局唯一、创建后不可修改；本阶段仅观察列表字段 `plugin_id`，不提交创建。
- 规划已创建、运行中、已停止、停止后启动、重启、故障恢复、异步失败的状态和页面反馈；`page.json` 当前仅观察运行中、已停止及停止确认。
- 规划设备数包含未删除及停用设备、排除删除设备、按设备唯一编号去重、进入页面/刷新重新查询；当前 `page.json` 仅确认 `device_count` 列，统计语义证据待补。
- 规划创建后无配置编辑功能、运行中删除限制、停用后删除允许；本阶段不执行启动、停止、停用或删除。
- 规划地址展示与证书、密钥、敏感配置在表单/详情/日志/错误提示中的脱敏及旧值清理；当前详情、日志和错误提示证据不足，需记录风险。
- 规划默认、筛选、分页、刷新、排序和表头设置后的创建时间倒序及持久化；分页定位器、并列排序和持久化范围待确认。
- 规划插件查看人员、插件管理员、设备/产品管理员、平台运维/审计人员的角色页面权限；插件管理列表不按不同租户分别管理，不以按钮可见性推断写权限。

### 范围外

- 真实创建、启动、停止确认、停用、删除、配置提交、敏感配置提交和任何业务写入。
- 接口状态码、请求响应、错误码、数据库、审计字段、性能指标、配置升级、灰度、回滚和设备类型兼容。
- 导入、导出、下载、绕过权限或安全控制。
- 将需求中的 `emqx`、已创建、完整生命周期、设备数统计、详情/日志/错误提示脱敏或权限矩阵当作已由 `page.json` 证明的事实。
- 测试点、测试用例、CSV、禅道数据和 UI 自动化脚本。

## 测试策略

- 采用黑盒、风险优先、页面级只读策略；页面身份和已采集状态可进行有限观察，`partial` 区域记录待确认/无法验证，不伪造通过或失败。
- 等价类覆盖 `Name`、`Type`、`Port`、`Lifecycle`、`DeviceSet`、`SecurityLocation`、`Ordering`、`Permission`：系统生成/端口派生/编辑尝试；`emqx`/`mqtt`/`http`/不支持；唯一/同协议重复/跨协议重复/保留/越界/非法格式；已创建/运行中/已停止/停止后启动/重启/故障恢复/异步失败；活动/停用/删除/重复编号/刷新；地址可展示/证书密钥敏感配置脱敏/旧值清理/明文禁止；默认/筛选/分页/刷新；授权/未授权；租户差异不作为插件列表管理条件。
- 边界值覆盖端口最小/最大/保留/越界/格式、同协议与跨协议重复、名称派生和端口变化、已创建/运行中/已停止、运行中删除与停用、设备删除排除/停用包含/编号去重、进入页面和刷新、表单/详情/日志/错误提示四类敏感展示位置、筛选分页刷新后的创建时间倒序、未授权；不增加不同租户列表管理或隔离分支，未确认阈值不虚构具体数值。
- 判定表覆盖同协议或跨协议端口重复均拒绝、合法唯一端口按页面反馈处理；运行中删除拒绝但停用允许、停用后删除允许；设备删除排除、停用包含、唯一编号去重；敏感字段全链路脱敏且旧值清理；默认/筛选/分页/刷新均按创建时间倒序；未授权不超出角色页面权限，租户差异不作为插件列表管理条件。
- 状态转换覆盖不存在->已创建->运行中->已停止->运行中、运行中->停用->删除允许、运行中->删除请求->拒绝、关联变化->进入页面/刷新->重新查询->设备数更新、敏感值存在->删除/替换->旧值清理；当前只将已观察的页面状态作为事实，其余是待验证目标。
- Pairwise/2-way 评估 `Type`、`PortRelation`、`Lifecycle`、`DeviceSet`、`SecurityLocation`、`Ordering`、`Permission`。约束：重复/保留/越界/非法端口不得进入已创建成功结果；敏感位置仅在授权观察下验证；未授权不得产生越权生命周期成功结果；租户差异不构成插件列表管理组合。模型仅用于后续测试设计，不生成或执行真实写操作。
- Playwright Python/pytest-playwright 仅规划：复用 `login_page.py` 和 `portal_navigation.py`；依据 `page.json` 已确认的 `page_id`、`state_id`、`element_id` 和 evidence 观察路由、默认列表、筛选、表头设置、新建弹窗字段、类型/重启策略选项和停止确认；停止确认仅打开并取消，不提交。定位优先 role、test id、label、placeholder、text 和稳定属性，CSS 仅最后手段；分页因 stable element IDs 缺失不得冻结定位器。
- Web 执行采用导航后等待可观察状态，再保存脱敏 URL/标题/菜单、状态、DOM/可访问性快照和截图；禁止提交新建、启动、停止、停用、删除或敏感配置，配置缺失、登录失败、主机不符、权限失败、写操作提示或敏感信息暴露时停止。

## 测试环境

- **客户端**：PC Web
- **操作系统**：`win32`；正式执行前记录实际客户端版本
- **浏览器**：Chromium；Playwright Python 规划可视模式 `headless=False`
- **正式地址**：`${UI_TEST_URL}`
- **页面路径**：`/biopark-iot/iot/device/device-protocol`
- **门户入口**：数据采集监控平台 / 数据采集 / 设备接入 / 插件管理；`page.json` 已登记该运行时路由、标题、菜单和 `plugin_management_default`
- **登录**：使用测试账号登录；凭据仅从 `UI_TEST_USERNAME`、`UI_TEST_PASSWORD`、`UI_TEST_TENANT` 运行时读取，不写入计划、日志或证据；需确认正式权限、租户和数据范围。

## 测试数据与角色

### 测试数据

- 只读插件查看人员、插件管理员、设备/产品管理员、平台运维/审计人员角色；当前租户仅作为运行环境上下文，不作为插件管理列表的管理范围；账号、密码和租户值不写入产物。
- 经授权可读的插件列表、运行中/已停止状态、类型、端口、设备数、插件 ID、状态描述和创建时间；不造插件、端口或设备。
- `page.json` 已登记的 `plugin_management_default`、`plugin_management_status_options`、`plugin_management_columns_options`、`plugin_management_add`、`plugin_management_add_type_options`、`plugin_management_add_restart_options`、`plugin_management_stop_confirm` 状态和截图/日志证据。
- 需求/页面冲突样本：名称可编辑与系统生成只读、MQTT/HTTP 与 emqx/mqtt/http、运行中/已停止与已创建；只做页面事实核对，不提交表单。
- 批准的设备数、删除排除、停用包含、编号去重、刷新重查、详情/日志/错误提示脱敏和角色租户矩阵证据；缺失时标记待确认。
- 数据准备由测试、业务/产品、平台权限、插件管理、设备管理和研发负责人负责；本计划不修改业务数据，清理状态为 `not_applicable`。

### 角色

- 测试：执行插件管理页面身份、已采集状态和批准的只读观察；不提交任何业务写操作。
- 插件查看人员：确认授权范围内列表、状态、设备数和详情可见性。
- 插件管理员：确认创建、启动、停止、停用、删除权限语义，但本阶段只提供页面证据，不执行写入。
- 设备/产品管理员：确认插件关联设备、设备数和产品依赖的批准回读。
- 平台运维/审计人员：确认运行状态、安全保护和异常处置页面证据；不扩展审计接口验收。
- 研发：补充名称派生、协议/状态枚举、生命周期反馈、设备数统计、分页、详情/日志/错误提示脱敏和稳定定位器。
- 平台权限负责人：准备角色、租户、业务范围和跨租户样本。
- 测试设计：在计划通过后消费范围和策略生成下游测试设计。

## 依赖与风险

### 依赖

- 产品管理、设备管理：提供产品依赖和插件关联设备的批准跨模块回读；不得复用其他模块定位器。
- 设备消息、采集/连接链路、运行监控、告警和审计：仅作为范围依赖线索，不作为已验证接口事实。
- 登录、权限和租户上下文：控制页面可达性、角色范围和数据隔离。
- REQ-006 页面契约：`page_id=plugin_management`，`route=/biopark-iot/iot/device/device-protocol`，`default_state=plugin_management_default`，`check_target=plugin_management_state`，`page_inventory_status=partial`，`evidence_status=available_redacted`。
- 公共页面对象 `07_ui_automation/pages/common/login_page.py`、`07_ui_automation/pages/common/portal_navigation.py`。
- 运行时配置键 `UI_TEST_URL`、`UI_TEST_USERNAME`、`UI_TEST_PASSWORD`、`UI_TEST_TENANT`；只引用键名，不复制值。

### 风险

- 证书、密钥或敏感配置在表单、详情、日志或错误提示中明文泄露；全链路只读观察并禁止记录真实值。
- 运行中插件被删除或停用后状态不一致；确认页面按钮/状态/反馈，当前不执行写入。
- 端口重复、保留端口和范围规则错误；覆盖同协议、跨协议、保留、越界和非法格式，具体提示待页面证据。
- 名称、编号或状态选项与最新确认不一致；保留 `page.json` 与需求差异，不强行覆盖。
- 设备数未去重、未排除删除设备、未包含停用设备或未按刷新重查；当前仅有 `device_count` 列，统计语义保持待确认。
- 默认、筛选、分页、刷新后创建时间倒序失效；分页元素 ID、并列排序和持久化范围待补。
- REQ-006 页面状态为 `partial`，已观察 MQTT/HTTP、运行中/已停止和名称可编辑，但未观察 emqx、已创建和完整生命周期；不得把缺失内容判为不存在。
- 角色权限、异步失败提示和稳定定位器待确认；插件管理列表不需要针对不同租户进行管理，不将租户差异作为列表管理、筛选或隔离条件；缺失时记录无法验证或 `blocked`。
- `.env`/`config.yaml` 及页面证据可能含敏感数据；只引用配置键名，禁止保存地址、账号、密码、租户、Token、Cookie、插件名称、插件 ID、端口和未授权业务数据。

## 准入标准

- `REQ-006.yaml`、`REQ-006.md`、`需求变动.md`、`模块拆分清单.md`、`page.json`、插件管理日志、`config.yaml` 和 `../../../.agents/references/test-plan.schema.json` 可读取，REQ-ID 与模块身份一致。
- 已确认 `page.json` 页面对象为 `plugin_management`，路由、标题、默认状态和已采集状态与计划一致；页面库存状态 `partial` 被明确保留。
- 已确认 `page.json` 仅观察到 MQTT/HTTP、运行中/已停止及名称可编辑属性；需求中的 emqx、已创建和名称只读作为差异待验证，不当作页面事实。
- 只读账号/角色/租户、批准插件数据、脱敏安全证据、正式路由责任和页面补证责任已准备，或将缺失项标为 report_only/blocked。
- 需求追溯、范围责任、等价类/边界/判定表/状态转换/Pairwise、自动化边界和停止条件已评审。

## 准出标准

- YAML 通过 `test-plan.schema.json`，未新增字段且不含 `tp/tp_id`；Markdown 与 YAML 的范围、策略、风险、准入/准出、证据和套件建议一致。
- 冒烟、定向、全量三个计划层级已定义；未生成测试点、测试用例、CSV、禅道数据或 UI 脚本。
- 页面 `partial`、需求/页面枚举差异、端口规则、生命周期、设备数、敏感信息、分页/排序、权限租户和稳定定位器风险均已交接。
- 页面事实、需求确认和待确认项分离；缺失详情/日志/错误提示、分页、设备数统计或权限证据时记录无法验证/blocked，不伪造通过或失败。
- 限定范围只读验证无业务数据变更；出现意外写入、未授权数据暴露、主机不匹配、登录/权限失败或关键内容缺失时停止并留证。

## 证据要求

- 页面事实基线：`page_id=plugin_management`，`route=/biopark-iot/iot/device/device-protocol`，标题“数据采集 - 插件管理”，`default_state=plugin_management_default`，`check_target=plugin_management_state`，`page_inventory_status=partial`，`evidence_status=available_redacted`。
- 已登记状态：`plugin_management_default`、`plugin_management_status_options`、`plugin_management_columns_options`、`plugin_management_add`、`plugin_management_add_type_options`、`plugin_management_add_restart_options`、`plugin_management_stop_confirm`；证据路径见 `02_analysis/REQ-006.yaml` 的 `page_contract.evidence`。
- 已登记元素：`plugin_management_name`、`plugin_management_status`、`plugin_management_query`、`plugin_management_reset`、`plugin_management_refresh`、`plugin_management_columns`、`plugin_management_add`、`plugin_management_stop`、`plugin_management_plugin_link`；新建表单和停止确认元素仅按 `page.json` 记录引用。
- 已登记表格 `plugin_management_table/plugin_management_table_element`，当前列 `plugin_name`、`plugin_type`、`plugin_port`、`device_count`、`plugin_id`、`status`、`status_description`、`created_at`、`actions`；`pagination_element_ids` 为空且 `pagination_status=missing_stable_element_ids`。
- 已观察选项：状态“运行中/已停止”，类型“MQTT/HTTP”，重启策略“总是/失败时/从不”；emqx、“已创建”和完整生命周期未观察到，保留需求/页面差异。
- 证据文件：`page.json`、`screenshots/plugin-management-default-new.png`、`plugin-management-status-new.png`、`plugin-management-columns-new.png`、`plugin-management-add-new.png`、`plugin-management-add-type-new.png`、`plugin-management-add-restart-new.png`、`plugin-management-stop-confirm-new.png`、`logs/plugin-management.txt`；缺失 DOM 快照不视为证据。
- 执行前/后仅保存运行时 URL、标题、菜单、状态标识、脱敏截图、DOM/可访问性快照、浏览器版本、时间和必要日志；禁止保存真实敏感值和未经授权业务数据。

## 冒烟 / 定向 / 全量回归套件建议

- **冒烟**：使用可视 Chromium 登录并确认插件管理运行时路由、标题、菜单、`plugin_management_default`、列表及已登记筛选/刷新/表头状态；仅观察 `page.json` 已确认内容，出现 partial 缺口时标记 blocked。
- **定向**：定向规划名称派生/只读差异、类型枚举、端口冲突/保留端口、状态生命周期、运行中删除保护、设备数统计、创建时间倒序、敏感信息脱敏和角色租户边界；当前依赖批准只读数据和缺失页面证据补齐。
- **全量**：覆盖 REQ-006-001 至 REQ-006-016 的完整追溯、等价类、边界值、判定表、状态转换、Pairwise/2-way、列表筛选分页刷新表头、生命周期、设备数、排序、安全脱敏和权限租户回归；真实写入、接口、性能、导入导出、审计和未确认页面事实不纳入。

## 阶段交接边界

- **当前阶段代理**：`stage-test-plan-agent`
- **下一阶段**：`testcase-generation-agent`
- 本阶段不生成测试点、测试用例、CSV、禅道数据或 UI 自动化脚本。
- Schema 校验：`TEST_PLAN_REQ-006.yaml` 已通过 `.agents/references/test-plan.schema.json`。
- 交接状态：`ready_for_scoped_readonly_ui_verification`；REQ-006 页面可进行限定范围只读验证，但名称、类型、状态、端口、生命周期、设备数、分页、安全脱敏和角色租户证据仍未完整闭环。


## 本轮核心流程补充

依据核心功能检查结果，本轮新增 6 条去重用例 `TC-REQ-006-061` 至 `TC-REQ-006-066`，覆盖创建成功回读、已创建启动成功、运行中停止成功、停用后删除成功、删除后列表分页回读及生命周期失败保态反馈。已有停止确认、运行中删除阻断、权限不足、分页观察、设备数、脱敏和状态观察用例不重复创建；真实写操作仍受页面证据、测试数据和权限条件阻塞。

## 删除后同表单重建测试计划（TC-REQ-006-067）

- 测试范围：删除成功、删除后查询确认不存在、使用完全相同业务字段（插件名称、类型、端口及连接配置）重新创建并核对字段一致性。
- 业务边界：系统生成的唯一编号、状态、创建时间等系统字段不要求一致；存在业务引用、端口冲突、真实通知风险或无写权限时不得执行。
- 准入条件：隔离测试数据、可执行写权限、可复核页面定位和清理方案已具备；数据监听页面证据缺失时保持阻塞。
- 证据要求：记录删除前表单字段、删除成功和不存在回读、重建成功、字段对比、系统字段差异、清理结果；关联用例 `TC-REQ-006-067` 当前状态为 `blocked`，不得表述为已执行通过。

# REQ-009 测试计划交接说明

## 交接状态

- **module_id**：`REQ-009`
- **模块**：数据采集
- **当前阶段**：`stage-test-plan-agent`
- **下一阶段**：`testcase-generation-agent`
- **计划**：`03_test_plan/TEST_PLAN_REQ-009.yaml`、`03_test_plan/TEST_PLAN_REQ-009.md`
- **计划状态**：`draft`
- **Schema 状态**：`TEST_PLAN_REQ-009.yaml` 已通过 `.agents/references/test-plan.schema.json`
- **页面状态**：已登记数据采集页面和脱敏 evidence，但页面契约为 `partial_blocked`
- **page_id**：`data_crawl`
- **运行时路由**：`/biopark-iot/iot/data/crawl`
- **默认状态**：`data_crawl_default`
- **下一步状态**：`blocked`
- 本轮新增用例范围：`TC-REQ-009-050` 至 `TC-REQ-009-053`；仅补齐模块已确认的编辑/执行闭环，不新增未确认删除功能

## 计划结论

本计划覆盖数据采集页面默认进入、任务名称/状态筛选、查询、重置、刷新、表头设置、表格分页、创建时间倒序、编辑字段、编辑保存成功/失败与配置回读、Cron、脚本、重启策略、内存限制、任务启动异步状态与执行结果回读、业务状态、执行异常、引用变化、脱敏和权限租户边界。

已采用等价类、边界候选、判定表、状态转换和 Pairwise/2-way 策略，并规划 Playwright Python 与 Web 证据范围。当前新建弹窗、启动/停止/删除确认层、执行结果、权限/错误提示和稳定任务行数据契约不完整；页面观察状态与确认业务状态存在差异。只能交接限定范围只读 UI 规划，不执行保存、控制动作、真实调度、设备采集、消息读取或接口验证。

## 已确认的页面事实

`page.json` 已登记：

- `page_id`：`data_crawl`
- 路由：`/biopark-iot/iot/data/crawl`
- 标题：数据采集 - 数据采集
- 菜单：数据中心 → 数据采集
- 默认状态：`data_crawl_default`
- 状态选项：`data_crawl_status_options`
- 编辑状态：`data_crawl_edit`，状态为 `partial`
- 新建状态：`data_crawl_dialogs_partial`，状态为 `partial`
- 表格：`data_crawl_table` / `data_crawl_table_element`
- 脱敏 evidence：`req009-default.png`、`req009-status-options.png`
- evidence 无 log/trace 路径，不能虚构日志或 trace 证据

已登记元素：

- 筛选/操作：`data_crawl_task_name`、`data_crawl_status`、`data_crawl_query`、`data_crawl_reset`、`data_crawl_refresh`、`data_crawl_columns`、`data_crawl_add`
- 行操作：`data_crawl_start`、`data_crawl_edit`、`data_crawl_delete`
- 分页：`data_crawl_page_size`、`data_crawl_prev`、`data_crawl_next`、`data_crawl_jump`
- 筛选表单：`data_crawl_filter_form` / `data_crawl_filter`
- 编辑字段：`data_crawl_edit_task_key`、`data_crawl_cron`、`data_crawl_common`、`data_crawl_script`、`data_crawl_restart`、`data_crawl_memory`
- 内存控制：`data_crawl_memory_decrease`、`data_crawl_memory_increase`
- 编辑按钮：`data_crawl_edit_cancel`、`data_crawl_edit_confirm`
- 表格列：任务名称、插件 ID、状态、状态描述、创建时间、操作

## 页面状态差异

`page.json` 观察到的状态包括：已创建、运行中、已暂停、重启中、删除中、已停止、异常。当前业务确认状态只有已创建、运行中、已停止。

已暂停、重启中、删除中和异常只记录为页面/需求差异，不能直接升级为正式业务状态，也不能推断其状态转换、控制权限或最终结果。页面每页观察值为 `200`，公共确认项要求默认 `10` 条；该差异需记录并确认，不直接判为缺陷或改写业务规则。

## 缺失契约与禁止推断

当前尚未形成独立可用的：

- 新建弹窗稳定字段、确定/取消控件和稳定 ID
- 启动、停止、删除确认层和异步处理中/完成/失败状态 ID
- 任务执行详情和失败结果 ID
- 权限/错误提示独立 ID
- 稳定任务行数据定位器
- 页面额外状态与确认业务状态的映射

不能仅根据 `data_crawl_add`、`data_crawl_start`、`data_crawl_edit` 或 `data_crawl_delete` 的存在，断言表单字段、写权限、保存结果、控制结果或删除行为已验证。不得复用其他模块的页面或定位器契约。

## 已确认的业务规则

- 任务名称由系统自动生成前缀与新增弹窗中用户填写的任务标识拼接；自动前缀不可修改。
- 数据采集仅创建定时任务，不包含采集协议/版本、设备范围、设备选择、批量/分组选择或字段映射。
- 任务标识、Cron 表达式和脚本必填；重启策略和内存限制可选。
- 脚本负责采集字段、数据类型、单位、质量码和数据转换；脚本格式错误时任务执行失败。
- 按 Cron 表达式执行，时区按系统默认；批量、并发、互斥、错过调度和重复触发按系统默认及重启策略处理。
- 业务状态为已创建、运行中、已停止：创建后已创建，启动后运行中，停止后已停止；已停止可再次启动或删除；不涉及暂停、恢复和超时。
- 重启策略为 `no`、`on-failure`、`always`、`unless-stopped`；设备离线、插件异常、脚本错误和部分成功按策略处理。
- 插件、设备或产品变化不影响已有任务配置；引用失效时本次执行失败并按重启策略处理。
- 采集值和设备标识按业务需要展示；认证信息、外部地址、消息和返回内容脱敏，日志不得明文保存。
- 默认、筛选、分页和刷新后均按创建时间倒序；筛选回第一页；默认每页 10 条；无结果显示“暂无数据”；失败提示无页面重试入口。
- 取消或关闭表单直接关闭；校验失败字段旁提示并保留输入；保存失败保留输入；重复提交只生效一次；处理中禁止重复操作；删除为软删除且列表不显示。

## 下游范围边界

负责：已登记数据采集页面的只读默认态、状态选项、筛选、表头、列表、分页、排序、编辑字段可见性和脱敏验证规划；以及待补契约后的新建字段、控制确认层、执行反馈、状态差异、异常处理、引用生命周期和权限租户验证规划。

不负责：新建提交、编辑提交、启动、停止、删除、重跑、真实设备采集、真实调度、跨模块配置修改、接口、状态码、调度引擎、幂等、性能及未确认规则。

## 风险与待确认项

1. 错误脚本或任务引用造成错采、执行失败或下游污染。
2. 启动、停止、删除和重启策略影响设备、插件资源和消息流。
3. Cron、时区、重复触发、并发和错过调度造成重复、乱序或数据风暴。
4. 脚本、地址、认证、消息、设备标识或采集值进入页面产物。
5. 页面观察状态与确认业务状态不一致。
6. 页面每页观察 200 与公共默认 10 的差异未闭合。
7. 新建、控制、执行结果、权限/错误和稳定行数据契约缺失。
8. Cron、脚本、任务标识和内存限制的具体边界、默认值和页面反馈待确认。
9. 设备离线、插件异常、脚本错误、部分成功在各重启策略下的等待、最终失败和人工重跑反馈待确认。
10. 正式 PDF REQ-009 章节逐条页码追溯待补。

## 执行与停止边界

页面契约和权限条件满足后，允许复用公共登录和门户导航，确认实际主机、`/biopark-iot/iot/data/crawl`、标题、`data_crawl_default`，再对已登记筛选、状态选项、表头、列表、分页、排序、编辑字段标签和脱敏权限提示进行只读观察。

出现配置缺失、登录失败、人工验证、路由/标题不符、权限失败、写操作提示、真实调度/设备连接、任务控制、消息读取/发送、页面契约仍缺失或敏感信息暴露时停止。不得绕过权限，不得捕获 endpoint、认证、脚本、载荷、设备标识、采集值或外部响应。

## 自动化交接

- 规划框架：Playwright Python sync API / pytest-playwright。
- 公共页面对象：`07_ui_automation/pages/common/login_page.py`、`07_ui_automation/pages/common/portal_navigation.py`。
- 定位优先级：已确认 `data_crawl_*` ID、`get_by_role`/name、`get_by_test_id`、`get_by_label`、`get_by_placeholder`、稳定文本和稳定属性，CSS 最后兜底。
- 列表操作：先定位目标任务行，再定位行内操作控件；当前稳定任务行数据定位器缺失，不能编造选择器。
- 可使用定位器：仅使用 `page.json` 已登记的 `data_crawl_*` 元素和表格/编辑字段契约。
- 禁止使用：任何未登记的新建、确认层、异步结果、执行详情、错误/权限和稳定行数据 locator，以及其他模块定位器。

## 数据变更与敏感信息

- 数据变更：无
- 清理状态：`not_applicable`
- 仅使用已有脱敏数据进行只读规划；不创建任务、不修改任务、不启动/停止/删除、不执行调度、不读取真实设备数据。
- 不保存地址、账号、密码、租户、Token、Cookie、证书、密钥、脚本、设备标识、采集值、消息载荷、响应、外部内部地址或未经授权业务数据。

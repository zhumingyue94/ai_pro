# REQ-004 测试计划交接说明

## 交接状态

- **module_id**：`REQ-004`
- **模块**：设备分组
- **当前阶段**：`stage-test-plan-agent`
- **下一阶段**：`testcase-generation-agent`
- **计划**：`03_test_plan/TEST_PLAN_REQ-004.yaml`、`03_test_plan/TEST_PLAN_REQ-004.md`
- **计划状态**：`draft`
- **Schema 状态**：`TEST_PLAN_REQ-004.yaml` 已通过 `.agents/references/test-plan.schema.json`
- **页面对象**：`device_group`
- **page.json 路由**：`/biopark-iot/iot/device/device-group`
- **page.json 标题**：`数据采集 - 设备分组`
- **菜单路径**：数据采集 / 设备接入 / 设备分组
- **默认状态**：`device_group_default`
- **页面/弹层证据状态**：部分；`device_group_dialogs_partial.locator_status=partial`

## 计划结论

本计划限定为设备分组页面身份、默认列表、名称/日期筛选、查询/重置/刷新、表头和分页、日期面板、新增弹层只读观察及批准的设备关联回读规划。已采用等价类、边界值、判定表、状态转换和 Pairwise/2-way 策略，规划 Playwright Python 与 Web 执行证据范围；未生成测试点、测试用例、CSV、禅道数据或 UI 脚本。

## 已引用页面事实

- 已采集状态：`device_group_default`、`device_group_columns_expanded`、`device_group_date_filter_expanded`。
- 部分状态：`device_group_dialogs_partial`，其定位状态为 `partial`；新增、编辑、删除详情、稳定字段 ID、删除确认、保存反馈、状态切换、设备关联、加载和错误提示契约不完整。
- 已登记默认元素：`device_group_add_button`、`device_group_table`、`device_group_name`、`device_group_start_date`、`device_group_end_date`、`device_group_query`、`device_group_reset`、`device_group_refresh`、`device_group_columns`、`device_group_add`、`device_group_edit`、`device_group_delete`、`device_group_page_size`、`device_group_prev`、`device_group_page`、`device_group_next`。
- 当前表格契约：七列——编号、分组名字、分组状态、分组描述、创建时间、设备数量、操作；不得补写未登记字段。
- 新增弹层已观察分组名称、分组描述、启用/停用状态及确定/取消语义；空提交后取消关闭，未保存业务数据；稳定字段 ID 未确认。
- 既有证据：`02_analysis/page_inventory/dom/device-group.html`、脱敏截图 `device-group-capture.png`、`req004-default-explored.png`、`req004-columns-expanded.png`、`req004-date-filter-expanded.png`、`req004-add-form-20261021.png`，以及日志 `device-group.txt`、`req004-exploration.txt`。

不得猜测编辑/删除/状态/设备关联/失败/权限内部 ID、CSS、`data-testid`、错误码或未登记页面对象。运行时确认前不得把这些对象写成页面事实或生成自动化定位。

## 范围交接

- 负责：页面身份、默认七列表格、分组名称/日期筛选、查询/重置/刷新、表头/分页、默认创建时间倒序、日期面板、新增弹层字段观察与取消，以及经批准的状态、设备多分组、数量统计、关联删除和权限租户回读证据。
- 不负责：真实新增、编辑、保存、删除、停用、恢复、设备加入/移出、批量关联、导出、接口/数据库写入、造数、表头持久化、性能 SLA、错误码审计及未确认页面事实。
- 依赖：`REQ-001` 首页、`REQ-003` 产品管理、`REQ-005` 设备管理、`REQ-007` 数据监听、`REQ-008` 数据推送、`REQ-009` 数据采集、`REQ-010` 告警配置和首页统计；依赖模块不代表本需求已验收。

## 风险与待确认项

1. 页面及新增/编辑/删除弹层为 partial；需运行时补采稳定字段、编辑、删除确认和结果反馈证据。
2. 名称空白、首尾/连续空格、描述空白/换行/特殊字符及修改后的保存/展示规则待确认。
3. 日期当前用户时区、起止包含边界、最大跨度、反向输入、默认倒序和分页交互待确认。
4. 停用/恢复、停用后新设备禁止归属、已有设备保留、多分组和加入/移出立即生效待补批准跨模块证据。
5. 设备数量未删除范围、停用设备计入、唯一编号去重、权限过滤、刷新无缓存和不一致处理待补证据。
6. 有关联设备时删除阻止提示及停用、改名、恢复允许的页面反馈待确认。
7. 失败、超时、网络异常、权限不足、无重试入口、重复提交只生效一次和处理中禁用的稳定页面反馈待确认。
8. 正式 PDF REQ-004 章节与需求变动/分析 YAML 的逐条追溯需补齐。
9. 查看/维护/设备管理员/审计角色、租户隔离和权限矩阵待确认。
10. `.env` 和配置可能包含敏感值；下游只能引用 `UI_TEST_URL`、`UI_TEST_USERNAME`、`UI_TEST_PASSWORD`、`UI_TEST_TENANT` 键名，不得复制值、凭据、Token、Cookie、设备编号、分组名称或未经授权业务数据。

## 执行与停止边界

允许复用公共登录和门户导航，进入运行时设备分组页面，读取筛选、日期面板、表格、分页和表头设置，打开新增弹层并取消，观察已确认只读状态和批准跨模块回读。数据不足记录“因数据不足无法验证”，不据此判失败。

出现运行时配置缺失、登录失败或人工安全验证、主机不匹配、权限失败、关键内容缺失、加载失败、内容不稳定、意外写入提示或未授权数据暴露时停止。禁止新增、编辑、保存、删除、停用、恢复、设备加入/移出、批量关联、导出、下载、接口写入、造数、业务跳转及绕过权限/安全验证。

## 下游可执行性契约

下游仅可消费已通过 Schema 的计划范围和策略生成测试设计。人工步骤不得直接使用内部 `state_id`、元素 ID 或猜测定位器；页面可执行描述应以运行时确认的可见名称和业务行为为准。未满足前置数据、权限、路由、可观察结果或稳定定位器时，标记为待确认、人工执行或 blocked，不伪造自动化可执行性。

## 数据变更

- 数据变更：无
- 清理状态：`not_applicable`
- 敏感信息：仅引用配置键名，不写入地址、账号、密码、租户、Token、Cookie、设备编号、分组名称或未经授权业务值

## 2026-10-23 变更
- 测试计划增加 11 条新增/编辑/删除/状态/关联/统计/失败闭环。

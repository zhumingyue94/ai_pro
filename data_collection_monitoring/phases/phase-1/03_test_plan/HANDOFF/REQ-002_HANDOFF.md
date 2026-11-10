# REQ-002 测试计划交接说明

## 交接状态

- **module_id**：`REQ-002`
- **模块**：产品分类
- **当前阶段**：`stage-test-plan-agent`
- **下一阶段**：`testcase-generation-agent`
- **计划**：`03_test_plan/TEST_PLAN_REQ-002.yaml`、`03_test_plan/TEST_PLAN_REQ-002.md`
- **计划状态**：`draft`
- **Schema 状态**：`TEST_PLAN_REQ-002.yaml` 已通过 `.agents/references/test-plan.schema.json`
- **页面对象**：`product_category`
- **page.json 路由**：`/biopark-iot/iot/device/product-category`
- **page.json 标题**：`数据采集 - 产品分类`
- **菜单路径**：数据采集 / 设备接入 / 产品分类
- **采集状态**：`partial`

## 计划结论

本计划限定为产品分类页面身份、筛选查询、列表分页、表单与删除确认层、字段和状态规则的只读验证规划，并准备经批准的跨模块回读证据。已采用等价类、边界值、判定表、状态转换和 Pairwise/2-way 策略，规划 Playwright Python 与 Web 执行证据范围；未生成测试点、测试用例、CSV、禅道数据或 UI 脚本。

## 已引用页面事实

- 已采集状态：`product_category_default`、`product_category_columns_expanded`、`product_category_add_form`、`product_category_add_validation_error`、`product_category_edit_form`、`product_category_delete_confirm`。
- 已登记元素：分类名字、查询、重置、刷新、表头设置、新增、编辑、删除、每页条数、上一页、第1页、第2页、下一页、页；新增/编辑字段为分类名字、分类排序、开启、关闭、分类描述。
- 当前契约：六列表格；产品数量未纳入当前表格，REQ-002-013 仅通过批准的关联页面、统计或回读证据追踪。
- 既有证据：`02_analysis/page_inventory/screenshots/req002-default-full-20261021.png`、`req002-default-reopened-20261021.png`、`req002-columns-expanded-full-20261021.png`；DOM：`02_analysis/page_inventory/dom/req002-default.html`、`req002-columns.html`；日志：`02_analysis/page_inventory/logs/req002-exploration.txt`。

新增/编辑/删除的失败提示、保存中、并发冲突、删除失败和跨模块结果未形成完整稳定证据；不得猜测内部 ID、CSS、`data-testid`、错误码或未登记页面对象。运行时确认前不得将这些对象写成页面事实或生成自动化定位。

## 范围交接

- 负责：页面身份和可达性、分类名字查询/重置/刷新、六列表格、分页、表单/删除确认取消、空值/排序/状态/时间展示、权限租户、唯一编号及经批准的跨模块只读回读。
- 不负责：真实新增、编辑、删除、保存、停用/启用、导入、导出、接口/数据库写入、造数、表头持久化、性能 SLA、错误码审计及未确认页面事实。
- 依赖：`REQ-001` 首页统计、`REQ-003` 产品管理、设备分组/设备管理、登录权限和租户上下文；依赖模块不代表本需求已验收。

## 风险与待确认项

1. `page.json` 为 `partial`，失败提示、保存中、并发冲突、删除失败和跨模块结果证据不完整；需执行前重新采集运行时 DOM。
2. 产品数量不在当前六列表格；需确认批准的关联页面、统计或回读证据及停用包含规则，不得新增列表列事实。
3. 停用关联保留、新产品选择阻断、改名同步、删除关联阻断、唯一编号关联和相关页面刷新待补充运行时证据；只读观察，不执行写操作。
4. 正式 PDF REQ-002 章节与需求变动/分析 YAML 的逐条追溯需补齐。
5. 排序正整数、不限最大值、允许重复、严格升序、空值和时区来源待确认。
6. 查看/维护角色、租户隔离、错误/并发/接口字段/幂等/审计契约待确认。
7. `.env` 和配置可能含敏感值；下游只能引用 `UI_TEST_URL`、`UI_TEST_USERNAME`、`UI_TEST_PASSWORD`、`UI_TEST_TENANT` 键名，不得复制值、凭据、Token、Cookie、分类名称或未经授权业务数据。

## 执行与停止边界

允许复用公共登录和门户导航，进入运行时产品分类页面，读取筛选、列表和分页，展开已采集表头设置，打开新增/编辑表单或删除确认层并取消，观察已确认的只读状态。数据不足记录“因数据不足无法验证”，不据此判失败。

出现运行时配置缺失、登录失败或人工安全验证、主机不匹配、权限失败、关键内容缺失、意外写入提示或未授权数据暴露时停止。禁止新增、编辑、删除、提交、保存、停用/启用、导入、导出、下载、接口写入、造数、钻取、业务跳转及绕过权限/安全验证。

## 下游可执行性契约

下游仅可消费已通过 Schema 的计划范围和策略生成测试设计。人工步骤不得直接使用内部 `state_id`、元素 ID 或猜测定位器；页面可执行描述应以运行时确认的可见名称和业务行为为准。未满足前置数据、权限、路由、可观察结果或稳定定位器时，标记为待确认、人工执行或 blocked，不伪造自动化可执行性。

## 数据变更

- 数据变更：无
- 清理状态：`not_applicable`
- 敏感信息：仅引用配置键名，不写入地址、账号、密码、租户、Token、Cookie、分类名称或未经授权业务值


## 2026-10-23 变更
- 测试计划新增 8 条核心流程项，包含正向回读和反向保留数据断言。

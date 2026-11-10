# REQ-PC-047 孵化需求与逐行创建上孵计划

## 1. 分析结论

`REQ-PC-047` 为二期 PC 端“计划管理 / 孵化需求”，模块 ID `723`，优先级 `P0`；属于一期已开发、二期无独立原型的功能延续。需求变动明确：产业链生产排程系统推送孵化需求；列表支持逐行创建上孵计划；创建沿用一期新增计划弹窗；创建后进入上孵计划页；行内“查看计划”跳转上孵计划页，并按当前需求号默认筛选。

本次仅完成需求、范围、业务规则、角色、页面契约、风险、依赖、环境和数据前提分析，不生成测试用例、测试点、接口测试或自动化脚本。

## 2. 页面与状态契约

页面事实来源：`02_analysis/pc/page_inventory/page.json`。

- 页面：`pc-req-047-hatching-demand`
- 路由：`/biopark-breeding/breeding/hatchingplans/hatching-demand`
- 菜单：`计划管理 / 孵化需求`
- 状态：`st-req-047-list-default`、`st-req-047-create-plan-drawer`、`st-req-047-view-plan-jump`

列表状态引用元素：`el-page-req-047`、`el-filter-req-047`、`el-filter-demand-no-req-047`、`el-filter-breed-req-047`、`el-filter-status-req-047`、`el-filter-replenishment-req-047`、`el-filter-source-plan-req-047`、`el-btn-query-req-047`、`el-btn-reset-req-047`、`el-btn-expand-req-047`、`el-btn-column-settings-req-047`、`el-btn-refresh-req-047`、`el-table-req-047`、`el-btn-create-plan-req-047`、`el-btn-view-plan-req-047`、`el-pagination-req-047`。

列表字段包括需求号、上孵品种、上孵日期、计划上孵蛋数、已分配上孵蛋数、计划状态、补栏计划信息、来源计划编码、备注、创建时间和操作。采集事实为 45 条、20 条/页、3 页；每行有“创建计划”和“查看计划”。计划状态候选为：草稿、正常、延迟、终止。

创建抽屉引用：`el-drawer-create-plan-047`、`el-drawer-hatchery-047`、`el-drawer-hatch-date-047`、`el-drawer-detail-table-047`、`el-btn-next-step-047`、`el-btn-prev-step-047`、`el-btn-draft-047`、`el-btn-confirm-047`、`el-btn-add-plan-row-047`、`el-btn-add-detail-row-047`、`el-btn-copy-row-047`、`el-btn-delete-row-047`。第一步孵化场必填且有默认值；第二步上孵日期必填；明细首行自动带入品种、周龄、平均蛋重。明细列为 13 列：序号、养殖场、养殖批次、种蛋类型、品种、周龄、平均蛋重、蛋重类型、产蛋日期、上孵数量、孵化器、备注、操作。

查看跳转引用：`el-page-hatching-plan-047`、`el-filter-plan-no-jump-047`、`el-filter-demand-no-jump-047`、`el-btn-query-jump-047`、`el-table-hatching-plan-047`、`el-toolbar-hatching-plan-047`。跳转目标为上孵计划页，需求号字段自动回填；回填后结果由目标页数据决定，采集状态记录为 0 条，不代表所有环境均无计划。

## 3. 范围与规则

### 纳入

1. 孵化需求列表、筛选、重置、展开、分页、表头设置和刷新。
2. 需求行级创建计划及一期新增计划弹窗继承关系。
3. 孵化场、上孵日期、明细首行带入、新增/复制/删除行和必填校验边界。
4. 行级查看计划、跨页跳转和需求号默认回填。
5. 与产业链生产排程系统、一期上孵计划和 `REQ-PC-048` 的业务依赖。

### 排除

产业链推送接口实现、上孵计划完整 CRUD/终止/下发/导入导出、数据库和具体接口契约、有效暂存及确认落库、雏苗发货、库存、出入库、APP、禅道同步和 UI 自动化脚本。

### 关键规则

- 创建和查看必须保持当前需求行上下文，不能使用全局首个按钮。
- 必填项不完整时点击 `el-btn-confirm-047` 应被拦截，不产生提交或跳转。
- 本次未执行暂存或有效确认，不能把创建成功、落库和自动跳转视为已验证事实。
- 查看计划跳转后，`el-filter-demand-no-jump-047` 应来源于触发操作的需求行。
- 需求变动优先于历史原型表现；`page.json` 仅作为已采集页面事实，不推导接口契约。

## 4. 系统性边界与自动化规划

等价类/边界候选：有数据、无数据、加载失败；需求号命中、无匹配、空值、重复；四种计划状态；首/中/末页；默认/修改/缺失/非法孵化场和日期；首行自动带入、新增、复制、删除和不完整明细；确认成功、校验拦截、取消关闭和重复操作；需求号回填后有计划或无计划。

决策维度：需求行是否存在、列表/查看/创建权限、行级作用域、必填项完整性、明细自动带入、是否暂存/确认、回填是否正确、目标页是否存在关联计划。

PICT 参数候选：`DemandDataState`、`DemandNoFilter`、`PlanStatus`、`PaginationState`、`UserPermission`、`HatcheryField`、`HatchDateField`、`DetailRowState`、`CreateAction`、`JumpFilterState`。约束包括：状态仅限四个枚举；必填缺失必须拦截；首行默认值来自当前需求行；创建/查看必须行级定位；未执行确认不得宣称成功。

自动化定位优先使用 `get_by_role`、`get_by_label` 和 dialog/表格行作用域。`el-btn-create-plan-req-047` 与 `el-btn-view-plan-req-047` 是重复行元素，正式脚本必须以需求号或正式行级唯一键约束；抽屉内部按钮必须以 `get_by_role('dialog', name='新建上孵计划')` 隔离。使用可视浏览器，不硬编码凭据。

## 5. 角色、依赖、风险与数据责任

角色概念：孵化需求查看人员、上孵计划创建人员、产业链生产排程系统。正式角色名称、菜单权限和接口权限由平台配置确认，不写入账号或权限编码。

依赖：产业链推送数据、一期上孵计划新增流程、`REQ-PC-048` 需求号关联筛选、权限配置、授权且可清理的孵化需求/上孵计划数据。接口路径、方法、字段、鉴权、幂等、重试和错误码均待单独资料确认。

主要风险：一期继承功能无二期独立原型；有效创建和暂存未验证；行级按钮可能误定位；跨需求跳转依赖 `REQ-PC-048`；正式数据和权限未提供。

本次仅只读探索、筛选、分页、结构查看和校验拦截，未执行暂存或确认，未修改正式业务数据，无需清理，清理状态 `not_applicable`。未来正式验证由授权测试责任人负责准备、变更、回收和确认；不得把账号、密码、Token、Cookie 或未经授权业务数据写入页面清单、截图、日志、DOM 或报告。

## 6. 门禁与下游交接

`workflow.gate_policy=report_only`，`gate_passed=false`。原因：有效创建数据、清理责任、正式权限和一期完整继承规则尚未提供；不阻断下游。

下一阶段为 `stage-test-plan-agent`：先核对授权环境和一期页面，准备有/无匹配需求号、状态、权限及可清理创建数据；创建/暂存/确认必须记录责任边界和清理状态；不扩展为接口测试。

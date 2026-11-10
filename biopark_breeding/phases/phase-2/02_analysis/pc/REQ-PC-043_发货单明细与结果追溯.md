# REQ-PC-043 发货单明细与结果追溯需求分析

## 1. 分析结论

REQ-PC-043 对应需求说明书中的 `REQ-003 发货单明细与结果追溯`，归属 `计划管理 / 雏苗发货 / 发货单明细`，禅道模块对齐为二期 PC 雏苗发货，模块 ID 为 711，优先级 P1。

本需求提供发货单及其发货结果的只读查看能力：展示顶部基础信息、上孵计划、栋舍分布、来源计划和发货记录；支持计划筛选、栋舍范围切换、网格/列表切换、位置来源联动、批次展开和返回列表。

需求变动优先于需求说明书。历史原型与最新口径存在差异时，本文保留原型证据，但当前页面契约以 `需求变动.md` 为准。本阶段不生成测试用例、接口脚本或 UI 自动化脚本。

## 2. 输入与追溯

| 类型 | 路径 | 追溯内容 |
| --- | --- | --- |
| 需求说明书 | `01_requirements/种禽孵化管理系统二期_需求说明书_合并版.docx` | `REQ-003`，映射为 `REQ-PC-043` |
| PC 模块拆分 | `01_requirements/pc/模块拆分清单.md` | REQ-PC-043、模块 711、P1 |
| 需求变动 | `01_requirements/需求变动.md` | 清空/筛选联动、权限、空数据和范围规则 |
| 页面清单 | `02_analysis/pc/page_inventory/page.json` | `pc-chick-shipping-detail` 及 16 个页面状态 |
| 结构化分析 | `02_analysis/pc/REQ-PC-043.yaml` | 本文对应的结构化分析 |

原型入口为 `http://43.143.148.114:18885/biopark-breeding/`。正式明细页面路由已确认为 `/biopark-breeding/breeding/delivery/detail/{id}`，但页面仍处于开发阶段，本次不访问该真实路由。测试环境地址仅记录来源为 `.env`，不写入具体地址或凭据。

## 3. 范围边界

### 纳入范围

- 发货单顶部基础信息、数量、进度和状态只读展示。
- 上孵计划表格、计划进度/发货状态/关键字筛选、查询和重置。
- 栋舍总览加载全部有效计划，当前上孵计划仅加载当前计划。
- 栋舍网格/列表两种查看方式。
- 位置来源信息、来源计划和发货记录联动。
- 发货记录字段展示、批次位置明细展开/收起。
- 筛选后和清空筛选后的默认第一条计划选择。
- 筛选无数据时计划、栋舍分布和发货记录的空状态。
- 不同发货单状态下的只读展示、查看权限和返回列表。

### 不纳入范围

- 发货、补录、修改、删除、完成发货和结果提交。
- REQ-PC-041 列表查询、状态卡、分页和列表入口实现。
- REQ-PC-042 发货执行、位置录入、草稿和提交流程。
- REQ-PC-044 导出文件生成和下载。
- APP 页面及移动端专属交互。
- 库存、出入库及商品禽养殖端签收回写。
- 具体接口路径、方法、字段、分页和大数据量性能策略。
- 未开放的孵化排程计划、上孵计划和生产报表页面。
- “需求说明”弹窗自身的业务实现。

## 4. 角色与权限

| 角色 | 页面能力 | 权限结论 |
| --- | --- | --- |
| 孵化场发货填报人 | 查看有权限发货单的明细、计划、栋舍和记录 | 由平台菜单/查看接口权限配置，不绑定具体角色 |
| 发货组长 | 复核和追溯发货任务及历史结果 | 由平台菜单/查看接口权限配置 |
| 场长 | 查看发货进度、明细和历史记录 | 实际可见范围依赖正式环境配置 |
| 产品/研发/测试/实施/业务培训人员 | 评审和验收只读页面规则 | 不作为正式业务权限矩阵结论 |

依据 2026-09-03 权限规则：无菜单权限时菜单不显示；无查看权限、加载失败或无数据时页面显示“暂无数据”；底层无权限操作返回“无操作权限”。具体角色、权限编码和测试账号不写入本产物。

## 5. 业务规则与数据口径

1. 明细页只读展示发货单、上孵计划、栋舍分布、来源信息和发货记录，数据口径与列表页、发货执行页一致。
2. 顶部信息区仅支持返回列表，不提供编辑和业务提交。
3. 上孵计划区不展示发货操作列；终止计划不展示、不计入总条数、不参与筛选、选择和记录查看。
4. “栋舍总览”加载当前发货单下全部有效计划记录；“当前上孵计划”只加载当前选中计划记录。
5. 栋舍分布支持网格和列表两种展示方式；视图切换只改变展示范围，不修改业务数据。
6. 来源明细采用组合交互：点击位置行“明细”按钮时显示位置筛选标签并联动筛选发货记录；点击位置格其他区域时显示来源明细弹窗，展示当前位置的来源计划及数量。
7. 发货记录展示操作时间、上孵计划号、操作人、发货结果、本次发货数量、位置数、剩余未发货数、位置累计数量和备注，并支持展开批次位置明细。
8. 发货单记录范围包含当前发货单下全部有效计划，不受执行页当前选择的单个计划限制。
9. 筛选后默认选择第一条有效上孵计划，并同步更新栋舍分布和发货记录。
10. 清空筛选后恢复全部有效上孵计划，并默认选择第一条。
11. 筛选无数据时，上孵计划表格、栋舍分布和发货记录均显示“暂无数据”。
12. 返回、查询、重置、范围切换、视图切换、位置来源查看、清空筛选和记录展开均为只读展示操作，不修改业务数据。
13. 无查看权限、加载失败和无数据时页面均显示“暂无数据”；无权限操作的底层可见提示为“无操作权限”。

## 6. 页面与元素契约

页面清单来源为 `02_analysis/pc/page_inventory/page.json`，页面 ID 为 `pc-chick-shipping-detail`，菜单路径为 `计划管理 / 雏苗发货 / 发货单明细`。

| 状态 ID | 页面含义 | 关键元素 ID | DOM 证据 |
| --- | --- | --- | --- |
| `st-default` | 默认明细页 | `el-card-ship-doc`、`el-btn-back`、`el-table-incubate`、`el-section-house`、`el-section-record` | `dom/req-pc-043-detail-default.md` |
| `st-house-overview` | 栋舍总览，全部有效计划 | `el-btn-house-overview`、`el-section-house`、`el-section-record` | `dom/req-pc-043-detail-house-overview.md` |
| `st-house-current` | 当前上孵计划范围 | `el-btn-house-current`、`el-section-house`、`el-section-record` | `dom/req-pc-043-detail-house-current.md` |
| `st-house-list` | 栋舍位置列表 | `el-btn-house-list`、`el-table-house-list` | `dom/req-pc-043-detail-house-list.md` |
| `st-source-detail` | 位置来源及记录联动 | `el-tag-position-filter`、`el-btn-clear-filter`、`el-section-record` | `dom/req-pc-043-detail-source-detail.md` |
| `st-filter-dropdown` | 发货状态筛选下拉 | `el-filter-ship-status`、`el-option-shipped` | `dom/req-pc-043-detail-filter-dropdown.md` |
| `st-filter-shipped` | 已发货计划筛选结果 | `el-table-incubate`、`el-section-house`、`el-section-record` | `dom/req-pc-043-detail-filter-shipped.md` |
| `st-filter-empty` | 关键字筛选无结果 | `el-filter-keyword`、`el-table-incubate`、`el-section-house`、`el-section-record` | `dom/req-pc-043-detail-filter-empty.md` |
| `st-filter-reset` | 清空筛选后的结果 | `el-table-incubate`、`el-section-record` | `dom/req-pc-043-detail-filter-reset.md` |
| `st-doc-01` | 待发货单据只读明细 | `el-card-ship-doc`、`el-table-incubate`、`el-section-house`、`el-section-record` | `dom/req-pc-043-detail-doc01.md` |
| `st-doc-03` | 已发货单据只读明细 | `el-card-ship-doc`、`el-table-incubate`、`el-section-house`、`el-section-record` | `dom/req-pc-043-detail-doc03.md` |
| `st-doc-04` | 已签收单据只读明细 | `el-card-ship-doc`、`el-table-incubate`、`el-section-house`、`el-section-record` | `dom/req-pc-043-detail-doc04.md` |
| `st-doc-05` | 待发货单据只读明细 | `el-card-ship-doc`、`el-table-incubate`、`el-section-house`、`el-section-record` | `dom/req-pc-043-detail-doc05.md` |
| `st-doc-06` | 发货中单据只读明细 | `el-card-ship-doc`、`el-table-incubate`、`el-section-house`、`el-section-record` | `dom/req-pc-043-detail-doc06.md` |
| `st-doc-07` | 已发货单据只读明细 | `el-card-ship-doc`、`el-table-incubate`、`el-section-house`、`el-section-record` | `dom/req-pc-043-detail-doc07.md` |
| `st-doc-08` | 已签收单据只读明细 | `el-card-ship-doc`、`el-table-incubate`、`el-section-house`、`el-section-record` | `dom/req-pc-043-detail-doc08.md` |

### 需求与历史原型差异

- 最新需求要求筛选无数据时栋舍分布和发货记录均显示暂无数据；历史原型证据存在发货记录未清空，当前分析以需求变动为准。
- 最新需求要求清空筛选后默认选择第一条；历史原型重置后的默认选择并非第一条，保留为历史偏差证据。
- 需求说明书描述来源明细弹窗；历史原型使用位置筛选标签和记录联动。当前口径确认采用组合交互：位置行“明细”按钮联动记录，位置其他区域打开来源明细弹窗；`page.json` 仅保留已采集的标签和记录联动证据，不新增弹窗元素 ID。

## 7. 页面交互链路

```text
st-default
  → 栋舍总览(st-house-overview) / 当前上孵计划(st-house-current)
  → 网格 / 列表(st-house-list)
  → 位置行“明细”按钮：位置筛选标签(st-source-detail) → 发货记录联动 → 清空筛选
  → 位置格其他区域：来源明细弹窗 → 返回栋舍视图
  → 发货状态筛选(st-filter-dropdown → st-filter-shipped)
  → 关键字无结果(st-filter-empty) → 重置(st-filter-reset)
  → 返回列表
```

明细页不提供发货、补录、修改、删除和提交入口。任何视图、筛选、记录展开和返回操作只改变页面展示范围。

## 8. 接口与数据依赖边界

已知数据概念包括雏苗发货单、上孵计划、栋舍位置结果、位置来源关系和发货记录。它们分别支撑顶部信息、计划筛选、栋舍范围切换、来源联动和批次追溯。

本阶段不确认接口路径、HTTP 方法、请求/响应字段、具体权限编码、分页和大数据量策略；不依据原型 mock 数据补写接口契约。正式明细路由已确认但不访问；页面层只记录权限、空状态、筛选联动、来源弹窗和只读操作等可观察表现。

## 9. 系统化边界候选

### 等价类与边界值

- 发货单状态：待发货、发货中、已发货、已签收。
- 计划状态：未出雏、已出雏、终止。
- 筛选结果：全部、单条、多条、无数据。
- 栋舍范围：总览、当前上孵计划。
- 查看模式：网格、列表。
- 位置来源：无来源、单计划来源、多计划来源。
- 发货记录：无记录、单批次、多批次、展开、收起。
- 关键字：空、完整匹配、部分匹配、无匹配。
- 权限：有菜单/查看权限、无菜单权限、无查看接口权限。

### 决策表维度

以是否有查看权限、是否存在有效计划、筛选是否有结果、是否为终止计划、栋舍范围、视图模式、是否存在位置来源、是否存在发货记录以及是否执行清空/重置，推导页面可见内容、默认选择、空状态和只读行为。

### 状态转换维度

覆盖默认明细、栋舍总览、当前计划、列表视图、来源筛选、清空筛选、状态筛选、无数据、重置和返回列表；不把任何展示操作推断为业务数据写入。

### PICT 参数/约束候选

| 参数 | 候选取值 |
| --- | --- |
| `OrderStatus` | `Pending`、`Shipping`、`Shipped`、`Signed` |
| `PlanProgress` | `NotHatched`、`Hatched`、`Terminated` |
| `FilterResult` | `All`、`Single`、`Multiple`、`Empty` |
| `HouseScope` | `Overview`、`CurrentPlan` |
| `ViewMode` | `Grid`、`List` |
| `PositionSource` | `None`、`SinglePlan`、`MultiplePlans` |
| `RecordState` | `None`、`SingleBatch`、`MultipleBatches`、`Expanded`、`Collapsed` |
| `FilterAction` | `Initial`、`StatusFilter`、`KeywordFilter`、`Reset`、`ClearPositionFilter` |
| `PermissionState` | `MenuAndViewAllowed`、`MenuDenied`、`ViewDenied` |

约束候选：终止计划不展示、不参与筛选和选择；筛选无数据时计划、栋舍和记录均暂无数据；筛选和重置后默认第一条；总览包含全部有效计划，当前计划只包含选中计划；所有操作只读。以上不是测试用例或 PICT 测试集。

## 10. Playwright 定位边界

定位优先级为：`get_by_role`、`get_by_label`、唯一页面标题文本、页面区域作用域语义定位，最后使用作用域 CSS。

- 返回、栋舍总览、当前计划、列表、清空筛选按钮优先使用 role。
- `el-filter-ship-status` 必须限定在上孵计划区域；`el-option-shipped` 限定在该筛选浮层。
- `el-btn-position-detail` 必须绑定栋舍/列/层位置行上下文。
- `el-btn-record-expand` 必须绑定发货记录批次行或批次标识。
- 来源明细业务交互已确认；弹窗正式定位器需在自动化阶段按页面实际结构确认，不作为业务待确认项。
- 保持可视浏览器 `headless=False`，使用可观察状态等待，不使用固定等待，不写入凭据或真实业务数据。

## 11. 风险、依赖与待确认

主要风险：需求变动与历史原型在筛选无数据、重置默认选择和来源明细呈现上不一致；mock 数据不能证明正式权限、空状态和只读行为；位置明细、来源弹窗和发货记录展开按钮可能缺少稳定定位器；正式测试数据和清理责任尚未准备。

待确认问题：无。

说明：计划行、位置行、记录批次和来源明细弹窗的稳定唯一定位器或正式 `data-testid` 属于自动化阶段前置条件，不属于业务功能待确认。

## 12. 采集与门禁结论

- 原型采集状态：`captured`。
- 浏览器：可视 Chromium，`headless=False`。
- 本次只执行明细页查看、筛选和展示方式切换，未执行任何业务提交。
- 数据清理：`not_applicable`，明细页为只读探索。
- 门禁策略：`report_only`。
- `gate_passed=false`，原因是正式测试数据、权限配置、清理责任和正式页面执行证据尚未完全具备；业务待确认项为 0，需求/原型差异保留为风险证据，不阻断下游。

下一阶段：`stage-test-plan-agent`。

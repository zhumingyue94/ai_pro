# REQ-PC-044 雏苗发货导出需求分析

## 1. 分析结论

REQ-PC-044 对应需求说明书 `REQ-004 雏苗发货导出`，归属 `计划管理 / 雏苗发货`，禅道模块对齐为二期 PC 雏苗发货，模块 ID 为 711，优先级 P1。

当前页面能力是：从雏苗发货列表点击导出，显示系统确认提示“是否确认导出全部数据项？”。确认后导出当前筛选结果的全部字段；字段、顺序和显示名称与页面表格一致；无筛选条件时导出全部列表数据；取消则不导出。文件名固定为 `发货单.xls`。无数据时交互与有数据完全一致，确认后下载仅包含表头的 `发货单.xls`。

需求变动优先于需求说明书和历史原型。历史原型中的导出配置弹窗、导出范围选择、字段方案选择、结果预览和再次导出仅作为 `page.json` 证据保留，不作为当前需求能力。本阶段不执行接口测试、接口断言或实际业务导出。

## 2. 输入与追溯

| 类型 | 路径 | 追溯内容 |
| --- | --- | --- |
| 需求说明书 | `01_requirements/种禽孵化管理系统二期_需求说明书_合并版.docx` | `REQ-004`，导出概述和交互 |
| PC 模块拆分 | `01_requirements/pc/模块拆分清单.md` | REQ-PC-044、模块 711、P1 |
| 需求变动 | `01_requirements/需求变动.md` | 全字段、Excel、中文文件名、权限和确认导出新交互 |
| 页面清单 | `02_analysis/pc/page_inventory/page.json` | `pc-chick-shipping` 的列表及历史导出状态 |
| 结构化分析 | `02_analysis/pc/REQ-PC-044.yaml` | 本文对应的结构化分析 |

当前 `page.json` 还包含其他模块页面；本分析只引用 `pc-chick-shipping` 的导出状态和元素，不修改页面清单，也不复制 DOM 快照中的业务数据。

## 3. 范围边界

### 纳入范围

- 列表页导出入口 `el-btn-export`。
- 当前已应用筛选条件的导出范围，包括日期、状态卡、栋舍、品种和关键字。
- 点击导出后的系统确认提示及“确认/取消”分支。
- 确认后导出全部字段，不支持自定义字段。
- 有筛选条件时导出筛选结果；无筛选条件时导出全部列表数据。
- `发货单.xls` 文件名和文件下载的页面可观察属性。
- 无数据时仍执行相同确认流程，确认后文件仅包含表头。
- 导出权限由平台角色菜单/接口权限树配置；无导出权限时点击导出显示“没有操作权限”。
- 导出不改变列表数据、状态统计和当前筛选条件。

### 不纳入范围

- 自定义字段、简版字段和导出范围选择。
- 历史导出配置弹窗及结果预览。
- 导出失败、超时和重复点击反馈，需求变动已标记为不考虑。
- 具体接口路径、请求响应字段、错误码和文件生成实现。
- APP 导出、发货执行、发货单明细、库存和出入库联动。

## 4. 角色、权限与数据责任

导出能力不绑定具体角色，由平台角色权限树配置菜单权限和导出接口权限。无菜单权限时雏苗发货菜单不显示；无导出权限时点击导出提示“没有操作权限”。具体角色、权限编码、账号和凭据不写入分析产物。

原型使用公开 mock 数据。本次仅引用既有页面证据，未执行确认导出、实际下载或业务数据变更，清理状态为 `not_applicable`。正式环境中的导出测试数据、权限配置、下载目录和清理由授权测试责任人负责。

## 5. 业务规则与页面契约

1. 点击导出后显示系统提示框“是否确认导出全部数据项？”。
2. 点击确认后导出全部字段，不提供字段自定义能力。
3. 有筛选条件时导出筛选后的全部数据项；无筛选条件时导出全部列表数据。
4. 点击取消后关闭提示，不导出数据，列表和筛选条件保持不变。
5. 下载文件名固定为 `发货单.xls`。
6. 导出字段、顺序和显示名称均与页面表格一致。
7. 无数据时交互与有数据完全一致；确认后下载的 `发货单.xls` 仅包含表头。
8. 导出操作不改变列表数据、状态统计、分页或已应用筛选条件。
9. 无导出权限时点击导出显示“没有操作权限”，不发生下载。
10. 筛选条件沿用 REQ-PC-041 当前已应用条件；列表页状态下拉已按最新需求移除，状态以状态卡切换为准。

## 6. 页面、状态与元素证据

页面清单来源为 `02_analysis/pc/page_inventory/page.json`，页面 ID 为 `pc-chick-shipping`，菜单路径为 `计划管理 / 雏苗发货`。正式路由沿用 REQ-PC-041 已确认的 `/biopark-breeding/breeding/hatchingplans/delivery`，页面开发中，本次不访问。

| 状态 ID | 当前分析含义 | 关键元素 ID | 证据 |
| --- | --- | --- | --- |
| `st-default` | 列表默认状态和导出入口 | `el-btn-export`、`el-table`、`el-pagination` | `page.json` |
| `st-export-dialog` | 历史导出配置弹窗 | `el-dialog-export`、`el-dlg-data-scope`、`el-dlg-field-scheme`、`el-dlg-cancel`、`el-dlg-confirm` | `dom/req-pc-041-export-dialog.md` |
| `st-export-scope-options` | 历史导出范围选项 | `el-option-current-filter`、`el-option-current-page` | `dom/req-pc-044-export-scope-options.md` |
| `st-export-field-options` | 历史字段方案选项 | `el-option-all-fields`、`el-option-simple-fields` | `dom/req-pc-044-export-field-options.md` |
| `st-export-processing` | 历史处理状态 | `el-dialog-export`、`el-dlg-confirm` | `dom/req-pc-044-export-processing.md` |
| `st-export-result` | 历史结果预览 | `el-dialog-result`、`el-result-file-name`、`el-result-file-info`、`el-result-condition-summary`、`el-table-result-preview`、`el-btn-reexport`、`el-btn-result-close` | `dom/req-pc-044-export-result.md` |
| `st-export-reopen` | 历史再次打开配置弹窗 | `el-dialog-export`、`el-dlg-cancel` | `dom/req-pc-044-export-reopen.md` |
| `st-export-filter-status` | 历史状态筛选下的导出证据 | `el-dialog-export`、`el-stats-shipped` | `dom/req-pc-044-export-filter-status.md` |
| `st-export-filter-keyword` | 历史关键字筛选下的导出证据 | `el-dialog-export`、`el-filter-keyword` | `dom/req-pc-044-export-filter-keyword.md` |

最新需求所需的“系统确认提示框”尚未在 `page.json` 中单独采集，因此不新增状态或元素 ID；后续正式页面应提供可观察的确认/取消定位契约。

## 7. 历史原型与最新需求差异

- 历史原型显示导出配置弹窗，支持导出范围和字段方案选择；最新需求取消这些选择，固定导出当前范围的全部字段。
- 历史原型显示处理状态、结果预览和再次导出；最新需求明确不考虑导出预览及失败/超时/重复点击反馈。
- `page.json` 当前采集批次同时包含其他模块页面；REQ-PC-044 只引用雏苗发货列表页面证据，不将其他模块问题归入本需求。

## 8. 页面交互链路

```text
st-default
  → 点击 el-btn-export
  → 系统确认提示：是否确认导出全部数据项？
      → 取消：返回列表，保持筛选条件，不导出
      → 确认：下载当前筛选结果的全部字段（Excel）
```

历史原型链路 `st-export-dialog → st-export-scope-options/st-export-field-options → st-export-processing → st-export-result` 仅作为差异证据，不作为当前流程。

## 9. 系统化边界候选

### 等价类与边界值

- 筛选：无条件、单条件、多条件、无结果。
- 状态卡：全部、待发货、发货中、已发货、已签收。
- 日期：单日、跨日、空日期范围；日期筛选边界由 REQ-PC-041 列表筛选契约承接。
- 关键字：空、完整匹配、部分匹配、无匹配。
- 权限：有菜单和导出权限、无菜单权限、无导出权限。
- 确认：确认、取消。
- 数据：有结果、无结果。
- 文件：Excel、中文文件名不乱码。

### 决策表维度

是否显示菜单、是否有导出权限、是否有筛选条件、筛选结果是否为空、是否确认导出、是否发生下载。

### 状态转换维度

默认列表 → 导出确认 → 取消返回列表或确认下载；筛选条件变化 → 导出确认 → 下载范围随当前筛选结果变化。历史配置弹窗和预览状态不属于当前需求转换。

### PICT 参数候选

| 参数 | 候选取值 |
| --- | --- |
| `MenuPermission` | `Allowed`、`Denied` |
| `ExportPermission` | `Allowed`、`Denied` |
| `FilterState` | `None`、`SingleCondition`、`MultipleConditions`、`NoResult` |
| `StatusCard` | `All`、`Pending`、`Shipping`、`Shipped`、`Signed` |
| `ConfirmAction` | `Confirm`、`Cancel` |
| `DataState` | `HasData`、`Empty` |
| `FileProperty` | `ExcelChineseName`、`HeaderOnlyWhenEmpty` |

约束候选：无菜单权限时菜单不可见；无导出权限时提示“没有操作权限”且不下载；取消不下载；字段、顺序和显示名称与页面表格一致；有筛选条件只导出筛选结果；无数据时相同确认流程后只下载表头。以上仅为参数、取值和约束候选，不是测试用例或 PICT 测试集。

## 10. 接口与自动化边界

本阶段不执行接口测试、接口断言或接口注入，不虚构接口路径、方法、请求体、响应体或文件生成契约。页面层只记录导出入口、确认/取消、权限提示、筛选范围和下载文件可观察属性。

Playwright 定位优先使用 `get_by_role`、`get_by_label`、`get_by_test_id` 和页面区域作用域。`el-btn-export` 可优先定位为导出按钮；最新系统确认框和下载结果的正式定位器尚未在 `page.json` 中采集，自动化阶段需按正式页面的 role、label 或 `data-testid` 绑定。浏览器固定使用可视模式 `headless=False`，下载文件使用受控临时目录并由授权责任人清理，不写入凭据或真实业务数据。

## 11. 待确认问题、风险与门禁

业务待确认项：无。

说明：系统确认框和下载结果的稳定 role、label 或 `data-testid` 仍是自动化阶段前置条件，不属于业务待确认项。

主要风险：历史原型与最新需求的导出流程不一致；mock 结果不能证明正式 `发货单.xls` 下载行为和权限表现；无数据导出、系统确认框和下载定位器尚未具备正式页面执行证据；`page.json` 同时承载其他模块，需保持 REQ-PC-044 引用边界。

门禁采用 `report_only`，当前 `gate_passed=false`。原因是正式测试数据、权限配置、下载环境和清理责任尚未完全提供；业务待确认项为 0，不阻断下游。

## 12. 采集与交接结论

- 原型证据：沿用现有 `page.json` 和 REQ-PC-044 导出 DOM/截图证据；本次不访问正式路由。
- 数据变更：未执行确认导出、实际下载或业务数据变更，清理状态为 `not_applicable`。
- 敏感信息：未写入账号、密码、Token、Cookie、具体 `.env` 地址或未经授权业务数据。
- 下一阶段：`stage-test-plan-agent`，制定页面功能测试计划并准备导出权限、字段/文件规则、测试数据和下载清理责任。

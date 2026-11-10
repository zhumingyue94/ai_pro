# 02_analysis/pc 阶段交接

## 阶段

- 当前阶段：`02_analysis`
- 业务分区：`pc`
- 需求：`REQ-PC-041 雏苗发货列表与筛选`、`REQ-PC-042 发货单发货执行`、`REQ-PC-043 发货单明细与结果追溯`、`REQ-PC-044 雏苗发货导出`
- 处理时间：`2026-09-03`
- 下一阶段：`stage-test-plan-agent`

## 输入

- `01_requirements/种禽孵化管理系统二期_需求说明书_合并版.docx`
- `01_requirements/pc/模块拆分清单.md`
- `01_requirements/需求变动.md`
- `02_analysis/pc/page_inventory/page.json`
- 原型：`http://43.143.148.114:18885/biopark-breeding/`

需求说明书中的 `REQ-001` 已按 PC 模块拆分清单映射为 `REQ-PC-041`，未将其误判为独立需求。

## 输出

- `02_analysis/pc/REQ-PC-041.yaml`
- `02_analysis/pc/REQ-PC-041_雏苗发货列表与筛选.md`
- `02_analysis/pc/REQ-PC-042.yaml`
- `02_analysis/pc/REQ-PC-042_发货单发货执行.md`
- `02_analysis/pc/REQ-PC-043.yaml`
- `02_analysis/pc/REQ-PC-043_发货单明细与结果追溯.md`
- `02_analysis/pc/REQ-PC-044.yaml`
- `02_analysis/pc/REQ-PC-044_雏苗发货导出.md`
- `02_analysis/pc/HANDOFF.md`
- 现有 `02_analysis/pc/page_inventory/page.json`：保持不变，仅作为页面事实和证据引用。

## 页面采集状态与证据

- 页面：`pc-chick-shipping`
- 菜单路径：`计划管理 / 雏苗发货`
- 采集批次：`PAGE-PC-REQ041-REQ042-20260903`
- 采集状态：`captured`
- 浏览器：可视 Chromium，`headless=false`
- 覆盖状态：`st-default`、`st-stat-pending`、`st-filter-keyword`、`st-pagination-page2`、`st-export-dialog`
- 页面清单：`02_analysis/pc/page_inventory/page.json`
- DOM 证据：`02_analysis/pc/page_inventory/dom/req-pc-041-*.md`
- 截图证据：`02_analysis/pc/page_inventory/screenshots/req-pc-041-*.png`
- 日志/trace：未采集，当前页面事实已有 DOM 和截图证据。

原型为公开 mock 数据。REQ-PC-041 本次仅做只读探索，未执行发货提交、确认导出或其他业务数据变更；清理状态为 `not_applicable`。未在产物中写入账号、密码、Token、Cookie 或未经授权的真实业务数据。

## 分析范围

已覆盖列表页、组合筛选、状态统计、列表字段、进度/待发货数口径、排序、查询、重置、分页、发货/明细入口和导出配置入口。发货执行、发货单详情、实际导出、库存联动、禁用菜单和 APP 专属规则已明确排除。

已在分析中引用 `page.json` 的页面 ID、状态 ID 和元素 ID，并整理等价类/边界值、决策表维度、状态转换维度、PICT 参数/约束候选及 Playwright 定位边界；未生成测试点、测试用例、CSV 或 UI 脚本。

用户补充口径已回写：真实路由为 `/biopark-breeding/breeding/hatchingplans/delivery`，但页面仍在开发中，本次未探索；日期格式为 `YYYY-MM-DD`；关键字 200 字以内不得报错；状态下拉筛选已从当前需求移除，仅保留状态卡；平台通过菜单权限-接口权限树配置权限；导出无权限提示“没有操作权限”，无数据权限进入发货/明细后提示“暂无操作权限”并展示暂无数据；导出按当前筛选结果导出。

本次范围已调整为页面功能测试为主：不执行接口测试、接口断言、接口注入或接口契约验证；接口结果触发的无数据、权限提示和导出按钮表现仍保留为页面功能边界。

现有 `page.json` 中的 `el-filter-status` 和 `st-stat-pending` 保留为历史原型事实，不作为当前 REQ-PC-041 能力，也未修改 `page.json`。

## REQ-PC-042 发货单发货执行交接

### 输入与追溯

- 需求说明书：`01_requirements/种禽孵化管理系统二期_需求说明书_合并版.docx`，`REQ-002` 映射为 `REQ-PC-042`。
- PC 模块拆分：`01_requirements/pc/模块拆分清单.md`，二期 / pc / 雏苗发货，模块 ID=711，优先级 P0。
- 需求变动：`01_requirements/需求变动.md`，确认剩余待发货数量、累计数量、计划顺序和 PC 排除项。
- 页面清单：`02_analysis/pc/page_inventory/page.json`，引用 `pc-chick-shipping-ship` 和 `pc-chick-shipping-ship-bl02`。

### 页面证据

- 页面状态覆盖：默认查看、计划筛选、发货模式、位置录入、超量提示、页面草稿、退出确认、完成确认、提交结果和刷新恢复。
- 证据目录：`02_analysis/pc/page_inventory/dom/req-pc-042-*.md`、`02_analysis/pc/page_inventory/screenshots/req-pc-042-*.png`。
- 重点元素：`el-card-ship-doc`、`el-stats-available`、`el-progress-ship`、`el-filter-ship-status`、`el-filter-progress`、`el-filter-keyword`、`el-table-incubate`、`el-house-cell`、`el-dlg-location`、`el-dlg-qty`、`el-dlg-note`、`el-dlg-toast`、`el-draft-stats`、`el-dlg-exit-confirm`、`el-dlg-complete-confirm`、`el-ship-toast`、`el-record-table`。
- `el-filter-ship-status` 属于发货执行页上孵计划筛选，不与 REQ-PC-041 列表页已移除的状态下拉混淆。

### 范围与边界

- 已纳入发货单信息、实际可发数、上孵计划筛选、可发货计划判定、发货模式、位置数量和备注、重复位置累加、超量校验、页面暂存、退出/完成确认及提交后的页面联动。
- 已排除列表查询与导出、发货单明细、APP 规则、草稿持久化、签收回写、审计要求、库存联动和具体接口契约。
- 页面暂存只表示当前页面会话状态，不推断为持久化草稿。

### 数据责任与清理

- 原型使用公开 mock 数据，既有证据包含 mock 演示提交；本阶段未执行正式环境业务提交。
- 既有演示提交已通过刷新恢复初始状态并有 `st-reset` 证据；清理状态为 `not_applicable`。
- 正式环境测试数据的创建、修改、回收和清理由授权测试责任人负责；不得将账号、密码、Token、Cookie 或真实业务数据写入分析产物。

### 门禁、风险与未解决问题

- `workflow.gate_policy`：`report_only`。
- `gate_passed`：`false`。
- 原因：正式页面测试数据和清理前提尚未具备；不阻断下游。
- 已确认：正式路由为 `/biopark-breeding/breeding/delivery/execute/{id}`；环境地址来源于 `.env`；权限由平台角色菜单/接口权限配置；无权限菜单不显示、无权限接口返回“无操作权限”；空状态表格显示“暂无数据”。
- 已确认提交约束：前端自动校正；2 秒内重复提交时后一次失败；并发提交按上孵计划最新待发货数校验。
- 已确认完成发货规则：无论未发货数为 0 还是大于 0，点击完成发货都必须确认；继续发货不提交，确认结束才提交。计划列表待发货数为 0 仍不可进入发货模式。
- 主要风险：mock 行为不能证明正式提交持久化；页面暂存与草稿持久化边界可能混淆；并发/重复提交规则尚未进行正式页面验证；重复计划按钮和位置格需要稳定行级定位器。
- 业务待确认：无。
- `data-testid`/稳定定位器仅作为自动化前置条件和风险，不作为业务待确认项。

### 下一阶段

`stage-test-plan-agent`：基于 REQ-PC-041 和 REQ-PC-042 分析产物制定页面功能测试计划，准备授权测试数据、页面权限配置、清理责任和执行环境；不扩展为接口测试。

## 门禁与未解决问题

- `workflow.gate_policy`：`report_only`
- `gate_passed`：`false`
- `gate_reasons`：
  - 页面功能测试所需的授权测试数据和正式页面清理责任未提供。
- Pipeline Summary：`completed_with_gate_issues`
- 按约定继续交接，不以门禁问题阻断下游。

## 风险与下一步

1. 原型 mock 数据不能代表真实页面数据；测试计划阶段需补充页面功能测试数据、权限配置和清理责任，不扩展为接口测试。
2. 行级“发货/明细”按钮重复，后续自动化需使用行作用域唯一键或正式 `data-testid`。
3. 最新需求与历史原型存在状态下拉筛选差异，后续测试计划应以最新需求为准。
4. 后续自动化保持可视浏览器 `headless=False`，使用语义定位和可观察状态等待，不写入硬编码凭据。

Next Agent: `stage-test-plan-agent`

## REQ-PC-043 发货单明细与结果追溯交接

### 输入与追溯

- 需求说明书：`01_requirements/种禽孵化管理系统二期_需求说明书_合并版.docx`，`REQ-003` 映射为 `REQ-PC-043`。
- PC 模块拆分：`01_requirements/pc/模块拆分清单.md`，二期 / pc / 雏苗发货，模块 ID=711，优先级 P1。
- 需求变动：`01_requirements/需求变动.md`，确认明细权限、筛选/清空联动、空数据和终止计划规则；用户补充确认正式路由、来源明细组合交互和异常空状态。
- 页面清单：`02_analysis/pc/page_inventory/page.json`，引用 `pc-chick-shipping-detail` 及 16 个明细页状态。
- 输出：`02_analysis/pc/REQ-PC-043.yaml`、`02_analysis/pc/REQ-PC-043_发货单明细与结果追溯.md`。
- 本次未通过编辑操作写入 `page.json`；复核时发现其当前文件哈希与任务开始时交接记录不同，且当前文件为工作区已有未跟踪文件，未执行覆盖或回滚；当前内容已通过 `page.schema.json` 校验。

### 页面证据

- 状态覆盖：默认明细、栋舍总览、当前计划、网格/列表、位置来源、状态筛选、已发货结果、关键字无数据、重置及多种发货单状态只读明细。
- 证据目录：`02_analysis/pc/page_inventory/dom/req-pc-043-*.md`、`02_analysis/pc/page_inventory/screenshots/req-pc-043-*.png`。
- 重点元素：`el-card-ship-doc`、`el-btn-back`、`el-table-incubate`、`el-filter-ship-status`、`el-filter-progress`、`el-filter-keyword`、`el-btn-house-overview`、`el-btn-house-current`、`el-btn-house-list`、`el-table-house-list`、`el-btn-position-detail`、`el-tag-position-filter`、`el-btn-clear-filter`、`el-section-record`、`el-btn-record-expand`。

### 范围与差异处理

- 已纳入发货单明细只读展示、计划筛选、栋舍范围/视图切换、来源和发货记录联动、批次展开、空状态、重置和返回列表。
- 已排除发货执行、编辑、删除、提交、导出、APP、库存/出入库和具体接口契约。
- 需求变动优先于历史原型：筛选无数据时栋舍和记录均暂无数据；清空/筛选后默认第一条；终止计划不展示、不参与筛选和选择。
- 历史原型差异已如实保留：筛选无数据时记录未清空、重置默认选择非第一条；来源明细历史证据以位置筛选标签联动记录呈现，当前口径补充为位置行“明细”按钮联动记录、位置其他区域打开来源明细弹窗，当前口径优先。

### 数据责任与清理

- 原型使用公开 mock 数据，本次只读探索明细、筛选和视图切换，未执行业务提交。
- 清理状态为 `not_applicable`；正式环境测试数据、权限配置及清理由授权测试责任人负责。
- 不得将账号、密码、Token、Cookie、真实业务值或 `.env` 具体配置写入分析产物。

### 门禁、风险与待确认

- `workflow.gate_policy`：`report_only`。
- `gate_passed`：`false`。
- 原因：正式测试数据、权限配置、清理责任和正式页面执行证据尚未完全具备；不阻断下游。
- 已确认：正式路由为 `/biopark-breeding/breeding/delivery/detail/{id}`，测试环境地址来源于 `.env` 且不写入具体值；无查看权限、加载失败和无数据时页面显示“暂无数据”；位置行“明细”按钮联动位置筛选标签和发货记录，位置格其他区域显示来源明细弹窗。
- 风险：历史原型与最新需求在无数据、默认选择和来源展示形式上存在差异；mock 数据不能证明正式只读权限和空状态；位置明细、来源弹窗和批次展开可能缺少稳定定位器。
- 业务待确认：无。
- `data-testid`/稳定定位器仅作为自动化前置条件，不作为业务待确认项。

### 下一阶段

`stage-test-plan-agent`：基于 REQ-PC-041、REQ-PC-042 和 REQ-PC-043 分析产物制定页面功能测试计划，准备权限、只读测试数据、异常数据和清理责任；不扩展为接口测试。

## REQ-PC-044 雏苗发货导出交接

### 输入与追溯

- 需求说明书：`01_requirements/种禽孵化管理系统二期_需求说明书_合并版.docx`，`REQ-004` 映射为 `REQ-PC-044`。
- PC 模块拆分：`01_requirements/pc/模块拆分清单.md`，二期 / pc / 雏苗发货，模块 ID=711，优先级 P1。
- 需求变动：`01_requirements/需求变动.md`，以 2026.9.3 口径覆盖历史导出配置弹窗和预览流程。
- 页面清单：`02_analysis/pc/page_inventory/page.json`，引用 `pc-chick-shipping` 的导出状态和元素；当前采集批次还包含其他模块，未修改页面清单。
- 本次待确认项关闭复核时间：`2026-09-04`；用户补充答案已固化到 REQ-PC-044 YAML 和 Markdown，业务待确认项为无。
- REQ-PC-044 收口复核时的历史全量 `page.schema.json` 校验曾存在 1 项外部采集元数据错误：`$.capture.status=available` 不在 Schema 允许值中；该历史问题不归因于 REQ-PC-044，本次不修改、不回滚 `page.json`。
- 本次复核读取到 `page.json` SHA-256 为 `5596E0144AA0C76F8E86087ECD33DBEA3FE1C825EFF33154DBF1FC1180D1B011`（2026-09-04 13:22:15）；该哈希仅作为当前观察基线，外部采集更新不归因于 REQ-PC-044。
- 输出：`02_analysis/pc/REQ-PC-044.yaml`、`02_analysis/pc/REQ-PC-044_雏苗发货导出.md`。

### 页面证据与当前契约

- 历史证据覆盖 `st-export-dialog`、`st-export-scope-options`、`st-export-field-options`、`st-export-processing`、`st-export-result`、`st-export-reopen`、`st-export-filter-status`、`st-export-filter-keyword`。
- 最新需求覆盖：点击 `el-btn-export` 后显示“是否确认导出全部数据项？”；确认导出当前筛选结果中与页面表格一致的全部字段、顺序和显示名称；取消不导出；文件名固定为 `发货单.xls`。
- 无数据时交互与有数据完全一致，确认后下载仅包含表头的 `发货单.xls`。
- 历史配置弹窗、字段方案、范围选择、结果预览和再次导出不作为当前需求能力；系统确认框尚未在 `page.json` 中单独采集。
- 无导出权限时点击导出显示“没有操作权限”；权限由平台角色菜单/接口权限树配置，不写死角色或权限编码。

### 数据、范围与门禁

- 已纳入导出入口、筛选结果范围、全字段、确认/取消、Excel 文件属性和权限提示。
- 已排除自定义字段、配置弹窗、预览、失败/超时/重复点击反馈、接口测试和 APP 导出。
- 本次仅引用既有页面证据，未执行确认导出、实际下载或业务数据变更；清理状态为 `not_applicable`。
- `workflow.gate_policy=report_only`，`gate_passed=false`。原因：正式测试数据、权限配置、下载环境和清理责任尚未完全提供；不阻断下游。
- 业务待确认：无。
- 系统确认框/下载稳定定位器仅作为自动化前置条件，不作为业务待确认项。

### 下一阶段

`stage-test-plan-agent`：基于 REQ-PC-041 与 REQ-PC-044 制定页面功能测试计划，准备授权导出权限、字段和文件规则、筛选有/无结果数据及下载清理责任；不扩展为接口测试。

## REQ-PC-045 存发苗间库存查询交接

### 输入与输出

- 需求说明书：`01_requirements/种禽孵化管理系统二期_需求说明书_合并版.docx`。
- PC 需求说明书：`01_requirements/pc/种禽孵化管理系统二期_PC_需求说明书.docx`；明确二期 PC 存发苗间及出入库记录页面不在本次页面细节范围。
- PC 模块拆分：`01_requirements/pc/模块拆分清单.md`；REQ-PC-045，二期 / pc / 存发苗间 / 库存查询，模块 ID=720，优先级 P1，一期已开发、二期无原型的既有功能延续。
- 需求变动：`01_requirements/需求变动.md`；提供共用库存能力、自动出库、库存扣减和关联存发苗间顺序分配规则；用户补充确认本期只计算本存发苗间发货出库，其他入库、出库属于一期内容。
- 页面清单：`02_analysis/pc/page_inventory/page.json`；引用 `pc-inventory-query`。
- 当前页面清单采集批次：`PAGE-PC-REQ047-20260904-HEADED-BLOCKED`，全局采集状态为 `blocked`；REQ-PC-045 仅引用已有页面和历史状态证据。
- 输出：`02_analysis/pc/REQ-PC-045.yaml`、`02_analysis/pc/REQ-PC-045_存发苗间库存查询.md`。
- 本次处理时间：`2026-09-04`；本次补充口径回写后业务待确认项为无。

### 页面证据与范围

- 页面：`pc-inventory-query`，标题为“存发苗间库存查询”，菜单路径为“库存管理 / 存发苗间 / 库存查询”。
- 正式路由：`/biopark-breeding/breeding/stock/chick/chick-inventory`，已确认但本次不探索。
- 菜单权限：由平台角色权限配置；查询权限和数据权限属于一期内容，本期不考虑。
- 状态：`st-inventory-query-nanjing`、`st-inventory-query-nanjing-expanded`。
- 证据路径：`02_analysis/pc/page_inventory/dom/req-pc-045-nanjing-inventory-data.md`、`02_analysis/pc/page_inventory/dom/req-pc-045-nanjing-inventory-expanded-data.md` 及对应截图路径。
- 两个状态在 `page.json` 中均无结构化元素、表单、表格和交互，未新增或猜测元素 ID。
- 原型范围限定为雏苗发货，本次未访问库存查询页面；历史采集记录的空页面/登录阻塞仅作为历史证据，不作为正式功能结论。

### 已确认规则与未解决问题

- 已确认：发货确认后自动出库；出库数量等于发货数量；类型为出库、方式为自动、单位为只；批次、操作人、操作时间、养殖客户有明确来源；按关联存发苗间顺序分配；不允许负库存；对应存发苗间库存 = 原库存数量 - 本存发苗间发货出库数；其他入库、出库属于一期内容，本期不纳入计算。REQ-PC-046 仅作为一期出入库记录参考。
- 已确认：筛选、查询、重置、分页、排序、展开和表格字段沿用一期页面；库存为零、无数据、加载失败、权限不足和库存计算异常时显示“暂无数据”。
- 业务待确认：无。查询权限和数据权限属于一期内容，本期不考虑；一期页面行为由测试计划阶段核对实际表现。
- 接口路径、方法、字段、错误码和接口测试不在本阶段范围。

### 数据、风险与门禁

- 本次未执行库存查询、提交、库存调整、出入库或其他业务数据变更，清理状态为 `not_applicable`。
- 不写入账号、密码、Token、Cookie、具体环境地址或未经授权业务数据；未来测试数据由授权测试责任人准备和清理。
- 主要风险：现有 `page.json` 无元素级证据、历史采集未证明正式页面可用、一期页面实际表现尚未核对、库存计算依赖 REQ-PC-042 和正式业务数据。
- `workflow.gate_policy=report_only`，`gate_passed=false`；原因记录为正式测试数据、页面执行环境、一期页面核对证据和清理责任缺失，不阻断下游。
- 页面清单当前观察 SHA-256：`FE7CA18853745B14E5471EF99D5A7DFD5C5E70AB5E5876BB018BF036B79BA417`（`2026-09-04 15:04:58`）；该哈希来自本次任务期间外部采集更新，本次不修改或回滚 `page.json`。
- 当前 `page.schema.json` 校验：通过；REQ-PC-045 未产生任何页面清单修改。

### 下一阶段

`stage-test-plan-agent`：核对一期页面实际表现，准备授权测试数据和库存/本存发苗间发货出库关联数据及清理责任；不扩展为接口测试。

## REQ-PC-046 存发苗间出入库记录交接

### 输入与输出

- 输入：`01_requirements/种禽孵化管理系统二期_需求说明书_合并版.docx`、`01_requirements/pc/种禽孵化管理系统二期_PC_需求说明书.docx`、`01_requirements/pc/模块拆分清单.md`、`01_requirements/需求变动.md`、`02_analysis/pc/page_inventory/page.json`。
- 模块追溯：REQ-PC-046，二期 / pc / 存发苗间 / 出入库记录，模块 ID=715，优先级 P1；一期已开发、二期无原型的既有功能延续。
- 输出：`02_analysis/pc/REQ-PC-046.yaml`、`02_analysis/pc/REQ-PC-046_存发苗间出入库记录.md`。
- 处理时间：`2026-09-04`。
- 页面清单任务开始时观察 SHA-256：`7BDB2C0258FA6DB98EE989A01070F0FAA3AD4C949DEA7EE795163B7B1E592CA2`；本次未修改、覆盖或回滚 `page.json`。

### 页面证据与范围冲突

- 引用页面：`pc-stock-inout-records`。
- 引用状态：`st-stock-inout-nanjing`、`st-stock-inout-expanded`、`st-stock-inout-column-settings`、`st-stock-inout-reset`。
- 正式路由为 `/biopark-breeding/breeding/stock/chick/chickrecord`，正式菜单为“库存管理 / 存发苗间 / 出入库记录”；本次不访问该路由。
- 现有 page.json 页面事实为“库存管理 / 合格蛋蛋库 / 出入库记录”，与 REQ-PC-046 范围不一致；页面、状态和元素仅作为范围不匹配的历史采集证据，不作为正式契约。
- 历史元素候选：`page-layout`、`filter-hatchery`、`filter-storage`、`btn-query`、`btn-reset`、`btn-expand`、`btn-collapse`、`filter-advanced`、`btn-column-settings`、`btn-export`、`el-table-stock-inout`、`pagination-page-size`、`pagination-prev`、`pagination-next`、`pagination-page`。不将这些 ID 直接用于正式自动化脚本。
- 证据路径：`02_analysis/pc/page_inventory/dom/req-pc-046-*.md` 及对应 `02_analysis/pc/page_inventory/screenshots/req-pc-046-*.png`。

### 已确认范围与规则

- 一期页面筛选、字段、排序、分页、展开/收起和表头设置沿用，本期不重新定义；本期仅关注表格是否展示雏苗发货产生的出入库数据。
- 导出按钮功能属于一期，本期不考虑。
- 上孵计划确认发货后自动生成出库记录；数量等于本次发货数量；类型为“出库”、方式为“自动”、单位为“只”；批次取上孵计划批次；操作人和操作时间取雏苗发货记录；养殖客户取当前园区。
- 出库存发苗间由上孵计划关联关系决定；当前存发苗间不足时按关联排列顺序继续分配；不允许产生负库存。
- 菜单无权限时不显示菜单；查询或查看接口无权限时提示“没有操作权限”。表格无数据、加载失败、记录生成失败或异常数据时显示“暂无数据”。
- 排除 REQ-PC-042 发货执行、REQ-PC-045 库存余额计算、APP 页面、手工出入库/调整/盘点/修复、业务数据变更和接口测试。

### 未解决问题、风险与数据责任

- 业务待确认：无；一期页面细节由测试计划阶段按实际页面核对。
- 风险：当前 page.json 页面范围不匹配，二期页面无原型，无法据此形成正式页面定位器；自动出库和分配规则依赖 REQ-PC-042 与授权业务数据；历史导出入口不属于本期范围。
- 本次原型不探索，未访问库存/出入库真实路由，未执行查询、提交、导出或其他业务数据变更；清理状态为 `not_applicable`。
- 不写入账号、密码、Token、Cookie、具体环境地址或未经授权业务数据。未来测试数据由授权测试责任人准备、维护和清理。

### 门禁与下一阶段

- `workflow.gate_policy`：`report_only`。
- `gate_passed`：`false`。
- 原因：正式测试数据、执行环境、权限配置和清理责任未完全提供；不阻断下游。
- 下一阶段：`stage-test-plan-agent`，按页面功能范围核对表格数据展示、权限提示和空状态；不扩展为接口测试。

## REQ-PC-047 孵化需求与逐行创建上孵计划交接

### 输入与输出

- 输入：`01_requirements/种禽孵化管理系统二期_需求说明书_合并版.docx`、`01_requirements/pc/模块拆分清单.md`、`01_requirements/需求变动.md`、`02_analysis/pc/page_inventory/page.json`。
- 模块追溯：`REQ-PC-047`，二期 / pc / 计划管理 / 孵化需求，模块 ID `723`，优先级 `P0`；一期已开发、二期无独立原型的既有功能延续。
- 输出：`02_analysis/pc/REQ-PC-047.yaml`、`02_analysis/pc/REQ-PC-047_孵化需求与逐行创建上孵计划.md`。
- 页面：`pc-req-047-hatching-demand`；状态：`st-req-047-list-default`、`st-req-047-create-plan-drawer`、`st-req-047-view-plan-jump`。

### 范围与页面契约

- 需求变动明确：产业链生产排程系统推送孵化需求；列表逐行创建计划；创建沿用一期新增计划弹窗；创建后进入上孵计划页；行内查看计划跳转并按当前需求号默认筛选。
- 页面路径为 `/biopark-breeding/breeding/hatchingplans/hatching-demand`，目标上孵计划路径为 `/biopark-breeding/breeding/hatchingplans/hatching-plan`。
- 已引用列表、创建抽屉和跳转页面的元素 ID，重点包括 `el-table-req-047`、`el-btn-create-plan-req-047`、`el-btn-view-plan-req-047`、`el-drawer-create-plan-047`、`el-drawer-hatchery-047`、`el-drawer-hatch-date-047`、`el-drawer-detail-table-047`、`el-filter-demand-no-jump-047`。
- 创建计划/查看计划为重复行元素，后续自动化必须按需求号或行级唯一键限定作用域；抽屉内部按钮必须限定 dialog 作用域。

### 数据、风险与门禁

- 本次仅只读探索、筛选、分页、结构查看和校验拦截，未执行暂存或有效确认，未产生持久化业务数据；清理状态为 `not_applicable`。
- 不得将账号、密码、Token、Cookie 或未经授权业务数据写入页面清单、截图、日志、DOM 或报告；未来正式创建/暂存/确认由授权测试责任人准备、变更、回收并确认清理。
- 风险：一期继承规则、产业链推送接口、有效创建成功路径、正式权限和可清理测试数据尚未提供；`REQ-PC-048` 是需求号关联筛选依赖。
- `workflow.gate_policy=report_only`，`gate_passed=false`；原因记录为正式数据、权限、清理责任和完整一期继承资料缺失；不阻断下游。

### 下一阶段

`stage-test-plan-agent`：核对授权环境和一期页面，准备有/无匹配需求号、计划状态、权限及可清理创建数据；不扩展为接口测试。

## REQ-PC-048 上孵计划需求号关联与筛选交接

### 输入与输出

- 输入：`01_requirements/种禽孵化管理系统二期_需求说明书_合并版.docx`、`01_requirements/pc/模块拆分清单.md`、`01_requirements/需求变动.md`、`02_analysis/pc/page_inventory/page.json`。
- 模块追溯：`REQ-PC-048`，二期 / pc / 计划管理 / 上孵计划，模块 ID `724`，优先级 `P0`；一期已开发、二期无独立原型的既有功能延续。
- 输出：`02_analysis/pc/REQ-PC-048.yaml`、`02_analysis/pc/REQ-PC-048_上孵计划需求号关联与筛选.md`。
- 页面事实：二期上孵计划无独立 `page.json` 页面；复用 `pc-req-047-hatching-demand` 的 `st-req-047-list-default`、`st-req-047-view-plan-jump` 作为来源和跳转依赖证据。

### 范围与契约

- 已确认规则：增加“孵化需求号”表格列；列位于“养殖批次”之前，空值显示 `-`，格式与孵化需求页面一致；需求号筛选采用模糊匹配且输入长度/格式不限；承接孵化需求创建计划；跳转后自动查询当前需求号且不保留其他筛选条件。
- 目标路由引用：`/biopark-breeding/breeding/hatchingplans/hatching-plan`，但目标页面新增控件和列尚无独立元素 ID，不能臆造页面状态。
- 已引用来源元素：`el-btn-view-plan-req-047`、`el-filter-demand-no-jump-047`、`el-btn-query-jump-047`、`el-table-hatching-plan-047`；行级查看必须按需求号或唯一键限定作用域。

### 依赖、风险与数据责任

- 依赖 REQ-PC-047、一期上孵计划页面、产业链生产排程系统、平台角色/接口权限和授权可清理测试数据。
- 已确认边界：同一需求号多计划不要求排序；分页沿用一期且不纳入本期测试；状态按计划状态筛选框过滤；需求号为空、重复或来源异常显示 `-`，计划仍可正常创建但不关联孵化需求；本期新增和导入按钮暂时保留，后期隐藏规划不纳入本期测试。
- 风险：二期独立原型、一期具体页面实现、接口契约、正式权限及测试数据均未提供；跳转自动查询存在错误行或历史值污染风险。
- 本次仅整理需求并复用既有只读跳转证据，未执行创建、暂存、确认、修改、删除、导入、导出或其他持久化变更；清理状态为 `not_applicable`。
- 不得将账号、密码、Token、Cookie 或未经授权业务数据写入页面清单、截图、日志、DOM 或报告；未来写入由授权测试责任人负责准备、回收和清理确认。

### 门禁与下一阶段

- `workflow.gate_policy=report_only`，`gate_passed=false`；原因是目标页面元素 ID、一期继承规则、正式权限、接口契约和可清理数据未提供，不阻断下游。
- 下一阶段：`stage-test-plan-agent`。先补采上孵计划正式页面并登记页面/状态/元素 ID，核对一期列表字段、筛选、排序和权限规则（分页沿用一期且不纳入本期测试），准备需求号模糊命中、无匹配、空值/重复/来源异常、多计划、计划状态过滤、跳转自动查询和权限数据；确认本期新增/导入按钮暂时保留；不扩展为接口测试。

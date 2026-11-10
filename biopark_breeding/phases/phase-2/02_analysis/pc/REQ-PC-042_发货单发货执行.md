# REQ-PC-042 发货单发货执行需求分析

## 1. 分析结论

REQ-PC-042 对应需求说明书中的 `REQ-002 发货单发货执行`，归属 `计划管理 / 雏苗发货 / 发货执行`，禅道模块对齐为二期 PC 雏苗发货，模块 ID 为 711，优先级 P0。

本需求承接列表页选中的发货单，展示发货单和上孵计划信息，并在栋舍位置录入本次发货数量。页面先形成当前会话内的暂存结果，完成发货后提交并刷新位置、计划、发货单进度、状态和发货记录。

本阶段只形成需求、范围和页面契约分析，不生成测试用例、接口脚本或 UI 自动化脚本。原型使用公开 mock 数据；既有证据中的演示提交已通过刷新恢复初始状态，不代表正式业务数据变更。

## 2. 输入与追溯

| 类型 | 路径 | 追溯内容 |
| --- | --- | --- |
| 需求说明书 | `01_requirements/种禽孵化管理系统二期_需求说明书_合并版.docx` | `REQ-002`，映射为 `REQ-PC-042` |
| PC 模块拆分 | `01_requirements/pc/模块拆分清单.md` | REQ-PC-042、模块 711、P0 |
| 需求变动 | `01_requirements/需求变动.md` | PC 发货执行数量、累计和范围规则 |
| 页面清单 | `02_analysis/pc/page_inventory/page.json` | `pc-chick-shipping-ship`、`pc-chick-shipping-ship-bl02` 及执行状态 |
| 结构化分析 | `02_analysis/pc/REQ-PC-042.yaml` | 本文对应的结构化分析 |

原型入口为 `http://43.143.148.114:18885/biopark-breeding/`。正式页面路由已确认：`/biopark-breeding/breeding/delivery/execute/{id}`，本次不访问真实执行路由。测试环境地址来源于 `.env`，不在产物中写入具体地址或凭据。

## 3. 范围边界

### 纳入范围

- 发货单主表信息、实际可发数、发货进度和状态。
- 上孵计划列表、计划进度/发货状态/关键字筛选、查询和重置。
- 已出雏且待发货数大于零的计划进入发货模式。
- 当前计划锁定、其他计划发货入口暂不可用。
- 栋舍/列/层位置格录入、数量和备注、同位置回显修改及多位置暂存。
- 数量输入仅允许数字；0/负数失焦校正为 1，小数失焦四舍五入，超剩余数失焦校正为剩余数。
- 无草稿退出、有草稿退出确认、完成发货确认。
- 提交后的进度、状态、位置累计和发货记录联动。
- 不同发货状态下的计划入口可用性及页面刷新恢复证据。

### 不纳入范围

- REQ-PC-041 列表查询、状态卡、分页和列表导出。
- REQ-PC-043 发货单明细和结果追溯。
- REQ-PC-044 实际导出文件生成和下载。
- APP 发货执行及移动端专属交互。
- 发货草稿持久化保存规则。
- 商品禽养殖端签收回写。
- 存发苗间库存查询和出入库记录页面字段展示；相关页面仅由 REQ-PC-045、REQ-PC-046 做只读字段验证。
- 操作人、操作时间和备注的审计要求。
- 具体接口路径、方法、请求/响应字段、权限编码和接口独立测试。
- 未开放的孵化排程计划、上孵计划和生产报表管理页面。

## 4. 角色与责任

| 角色 | 页面能力 | 权限结论 |
| --- | --- | --- |
| 孵化场发货填报人 | 查看发货任务、录入位置数量并完成提交 | 具体角色和数据权限由平台配置，不写死权限编码 |
| 发货组长 | 复核任务、执行发货并查看结果 | 具体角色和数据权限由平台配置 |
| 场长 | 查看发货进度、计划状态和发货记录 | 实际可见范围依赖正式环境权限配置 |
| 产品/研发/测试/实施/业务培训人员 | 评审、承接和验证页面规则 | 不作为正式业务权限矩阵结论 |

正式环境中的测试数据创建、修改、回收和清理由授权测试责任人负责。本次分析未创建、修改或删除正式业务数据。

## 5. 业务规则与数据口径

1. 仅计划进度为“已出雏”且待发货数大于零的上孵计划允许进入发货模式；上孵计划列表待发货数为 0 时不可进入；终止计划不参与发货。
2. 发货单处于待发货或发货中时开放编辑；已发货或已签收时不开放发货编辑。
3. 进入当前计划发货模式后，其他计划的发货入口暂不可用，防止未完成暂存时切换计划。
4. 剩余待发货数量 = 实际可发数 - 所有发货位置累计数量。
5. 累计数量包括已完成发货数量和当前页面暂存但尚未完成发货的数量。
6. 点击具体栋舍/列/层位置格打开位置录入弹窗；发货数量输入框仅允许数字，0 或负数失焦后校正为 1，小数失焦后四舍五入，超过当前剩余数量失焦后校正为剩余数，点击“完成”按校正后的数量保存。
7. 再次点击已录入位置时，发货数量和备注回显；修改数量或备注后点击“完成”按最新值保存，不叠加旧值。
8. 无草稿时退出直接离开发货模式；有草稿时提示继续发货或继续退出，继续退出不保留未完成页面草稿。
9. 无论当前未发货数量为 0 还是大于 0，点击完成发货均展示结束确认；点击继续发货返回编辑且不提交，点击确认结束后才提交当前计划暂存结果，并刷新位置、计划、发货单进度、状态和发货记录。
10. 实际可发数来自关联上孵计划实际出雏结果；未达到已出雏的计划按零处理，实际可发数为零时进度按零展示。
11. 多个上孵计划的列表顺序不作业务限制。
12. 2 秒内重复提交时后一次提交失败；并发提交按上孵计划最新待发货数校验，超出最新数量时不得提交。
13. 无关联计划、全部计划终止、加载失败和无数据时，相关表格均显示“暂无数据”。
14. 菜单和接口权限由平台角色权限配置；无菜单权限时菜单不显示，无接口权限时页面操作返回“无操作权限”。
15. 本阶段仅记录提交成功、超量、无数据和刷新恢复等页面可见表现，不依据 mock 数据补写正式接口契约。

## 6. 页面与元素契约

页面清单来源为 `02_analysis/pc/page_inventory/page.json`。

### 6.1 `pc-chick-shipping-ship`

菜单路径为 `计划管理 / 雏苗发货 / 发货执行`。

| 状态 ID | 页面含义 | 关键元素 ID | DOM 证据 |
| --- | --- | --- | --- |
| `st-default` | 发货单、计划、栋舍和记录默认查看 | `el-card-ship-doc`、`el-stats-available`、`el-progress-ship`、`el-filter-ship-status`、`el-filter-progress`、`el-filter-keyword`、`el-btn-query`、`el-btn-reset`、`el-table-incubate` | `dom/req-pc-042-ship-default.md` |
| `st-filter-progress` | 按计划进度筛选 | `el-filter-progress`、`el-table-incubate`、`el-btn-reset` | `dom/req-pc-042-ship-filter-progress.md` |
| `st-ship-mode` | 当前计划发货填写模式 | `el-view-mode-badge`、`el-mode-tip`、`el-btn-finish-ship`、`el-btn-exit-ship`、`el-row1-ship`、`el-row2-ship`、`el-house-cell` | `dom/req-pc-042-ship-mode.md` |
| `st-location-dialog` | 位置数量和备注录入 | `el-dlg-location`、`el-dlg-qty`、`el-dlg-note`、`el-dlg-cancel`、`el-dlg-confirm` | `dom/req-pc-042-location-dialog.md` |
| `st-location-overlimit` | 数量超过剩余数量 | `el-dlg-qty`、`el-dlg-toast` | `dom/req-pc-042-location-overlimit.md` |
| `st-draft` | 位置累计和当前页面暂存 | `el-house-cell`、`el-draft-stats`、`el-row1-progress` | `dom/req-pc-042-draft-accumulated.md` |
| `st-exit-draft-confirm` | 有草稿退出确认 | `el-dlg-exit-confirm`、`el-dlg-keep-shipping`、`el-dlg-exit-direct` | `dom/req-pc-042-exit-draft-confirm.md` |
| `st-complete-confirm` | 完成发货统一确认（未发货数为 0 或大于 0 均适用） | `el-dlg-complete-confirm`、`el-dlg-back-shipping`、`el-dlg-submit-end` | `dom/req-pc-042-complete-confirm.md` |
| `st-submitted` | 提交后页面结果 | `el-ship-toast`、`el-progress-ship`、`el-row1-ship-status`、`el-record-table` | `dom/req-pc-042-submitted.md` |
| `st-reset` | 刷新后 mock 初始状态 | `el-page-reset` | `dom/req-pc-042-reset-after-refresh.md` |

### 6.2 `pc-chick-shipping-ship-bl02`

该页面用于补充不同发货状态下的计划展示和入口可用性。

| 状态 ID | 页面含义 | 关键元素 ID | DOM 证据 |
| --- | --- | --- | --- |
| `st-default` | 不同发货状态计划默认展示 | `el-card-ship-doc`、`el-stats-available`、`el-progress-ship`、`el-table-incubate`、`el-section-record` | `dom/req-pc-042-bl02-default.md` |
| `st-status-filter` | 打开发货状态筛选 | `el-filter-ship-status-open`、`el-option-all`、`el-option-pending`、`el-option-shipping`、`el-option-shipped`、`el-option-signed` | `dom/req-pc-042-bl02-status-filter.md` |
| `st-status-shipped` | 按已发货计划筛选 | `el-filter-ship-status`、`el-table-incubate`、`el-section-record` | `dom/req-pc-042-bl02-status-shipped.md` |
| `st-ship-mode` | 可执行计划进入发货模式 | `el-btn-complete-ship`、`el-btn-exit-ship`、`el-house-grid`、`el-row1-ship-editing` | `dom/req-pc-042-bl02-ship-mode.md` |
| `st-draft` | 位置录入后的页面草稿 | `el-btn-complete-ship`、`el-house-pos1` | `dom/req-pc-042-bl02-draft.md` |
| `st-complete-confirm` | 完成发货统一确认（未发货数为 0 或大于 0 均适用） | `el-dlg-complete`、`el-btn-continue`、`el-btn-end` | `dom/req-pc-042-bl02-complete-confirm.md` |
| `st-submitted` | 提交后的结果页面 | `el-card-ship-doc`、`el-table-incubate` | `dom/req-pc-042-bl02-submitted.md` |
| `st-reset` | 刷新后 mock 初始状态 | `el-page-reset` | `dom/req-pc-042-bl02-reset.md` |

`el-filter-ship-status` 是发货执行页上孵计划区筛选，不与 REQ-PC-041 列表页已移除的状态下拉混淆。

## 7. 页面交互链路

```text
st-default
  → 计划筛选（st-filter-progress / st-status-shipped）
  → 行内发货（st-ship-mode）
  → 位置录入（st-location-dialog）
  → 超量提示（st-location-overlimit）或页面草稿（st-draft）
  → 退出确认（st-exit-draft-confirm）或完成确认（st-complete-confirm）
  → 提交结果（st-submitted）
  → 刷新恢复（st-reset）
```

发货入口和位置格均为重复元素，后续自动化必须使用计划、栋舍、列/层等行级作用域或正式 `data-testid`，不能使用全局文本定位。

## 8. 接口与数据依赖边界

已知数据概念包括雏苗发货单、上孵计划、实际出雏结果、发货位置累计结果、发货记录和栋舍基础数据。它们分别支撑主表展示、可执行计划判定、实际可发计算、剩余数量计算、提交结果和位置工作区。

本阶段不确认接口路径、HTTP 方法、请求体、响应体、错误码、具体权限编码或幂等技术实现；不依据原型 mock 数据补写接口契约。前端自动校正、2 秒重复提交拦截、并发时按最新待发货数校验属于已确认的业务约束，页面层仅保留其可观察结果。

## 9. 系统化边界候选

### 等价类与边界值

- 计划进度：未达到已出雏、已出雏、终止。
- 发货状态：待发货、发货中、已发货、已签收。
- 日期：未到计划日期、已到计划日期。
- 数量：实际可发为零、部分剩余、剩余为零；输入为空、0、负数、小数、正整数、等于剩余、超过剩余及前端自动校正。
- 提交：首次提交、2 秒内重复提交、并发提交未超过最新剩余、并发提交超过最新剩余。
- 位置：新位置、同一位置重复录入、多个位置。
- 草稿：无草稿、单位置草稿、多位置草稿。

### 决策表维度

以计划是否已出雏、日期是否已到、计划列表待发货数是否大于零、发货单是否可编辑、是否已进入发货模式、是否存在草稿、完成时栋舍分布未发货数是否为零以及输入/提交是否合法，推导发货入口、位置确认、退出确认和完成确认表现；未发货数只影响确认内容，不影响确认框是否显示。

### 状态转换维度

覆盖默认查看、计划筛选、发货模式、位置弹窗、超量提示、页面草稿、退出确认、完成确认、提交结果和刷新恢复；不把页面暂存推断为持久化草稿。

### PICT 参数/约束候选

| 参数 | 候选取值 |
| --- | --- |
| `PlanProgress` | `NotHatched`、`Hatched`、`Terminated` |
| `ShipStatus` | `Pending`、`Shipping`、`Shipped`、`Signed` |
| `DateEligibility` | `BeforePlanDate`、`PlanDateReached` |
| `AvailableQty` | `Zero`、`Positive` |
| `AccumulatedQty` | `Zero`、`Partial`、`EqualsAvailable` |
| `PendingQty` | `Zero`、`Positive` |
| `DraftState` | `None`、`OnePosition`、`MultiplePositions` |
| `PositionState` | `New`、`Repeated`、`Multiple` |
| `InputQtyClass` | `Empty`、`Zero`、`Negative`、`Decimal`、`PositiveWithin`、`EqualRemaining`、`OverRemaining` |
| `SubmissionState` | `First`、`DuplicateWithin2Seconds`、`ConcurrentWithinLatestPending`、`ConcurrentOverLatestPending` |
| `CurrentPlan` | `Selectable`、`Editing`、`OtherPlan` |
| `ActionState` | `ShipEnabled`、`ShipDisabled`、`Complete`、`Exit` |

约束候选：终止计划不在发货执行列表展示；未出雏/待发货数为零的计划不可进入；当前计划编辑时其他计划发货入口禁用；数量按失焦规则校正后保存，非数字不可输入；同一位置回显并按最新值保存；有草稿退出需确认；实际可发为零时进度为 0%；点击完成发货始终需要确认，确认结束才提交；2 秒内重复提交时后一次失败；并发提交超过上孵计划最新待发货数时失败。以上不是测试用例或 PICT 测试集。

## 10. Playwright 定位边界

定位优先级为：`get_by_role`、`get_by_label`、`get_by_placeholder`、页面区域作用域语义定位，最后才使用作用域 CSS。

- 查询、重置、完成发货、退出发货和确认按钮优先使用 role。
- 数量输入优先使用 placeholder `请输入数量`，备注限定在位置弹窗内的 textbox。
- `el-dlg-toast` 使用 alert 语义定位。
- `el-dlg-exit-confirm` 和 `el-dlg-complete-confirm` 使用 dialog 作用域。
- `el-row1-ship`、`el-row2-ship` 和 `el-house-cell` 为重复元素，必须使用计划或栋舍/列/层作用域或正式 `data-testid`；这是自动化前置条件，不是业务待确认项。
- 后续自动化保持 `headless=False`，使用可观察状态等待，不使用固定等待，不写入凭据或真实业务数据。

## 11. 风险、依赖与待确认

主要风险：原型 mock 数据不能证明正式提交和持久化；页面暂存可能被误解为草稿持久化；并发/重复提交规则尚未进行正式页面验证；重复按钮缺少稳定定位器；正式测试数据和清理责任尚未准备。权限、空状态和完成发货统一确认规则已由补充口径确认。

待确认问题：无。

## 12. 采集与门禁结论

- 原型采集状态：`captured`。
- 浏览器：可视 Chromium，`headless=False`。
- 当前分析未访问未授权开发路由，未新增正式业务数据。
- 既有 mock 演示提交已通过刷新恢复初始状态，清理状态为 `not_applicable`。
- 门禁策略：`report_only`。
- `gate_passed=false`，原因是正式页面测试数据和清理前提尚未具备；权限、空状态和完成发货统一确认规则已确认，不阻断下游。

下一阶段：`stage-test-plan-agent`。

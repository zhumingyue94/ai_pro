# REQ-PC-046 用例重新评审

## 2026-10-14 导航文案修订

- 仅修改公共前置 `inventory_records_page_access` 的 action：将库存管理/存发苗间导航明确为左侧菜单及子菜单展开，并将“出入库记录”明确为菜单项。
- “上孵计划”在 `TC-PC-046-012` 中属于自动出库记录字段来源核对内容，不属于页面导航，未修改该业务步骤或预期。
- YAML/Markdown 用例编号、数量、统计和内容已重新生成并通过校验；本次未修改标题、expected、用例级前置条件或其他字段。
- 来源哈希：YAML `056dfb0121cca98607872f208dc7504e3da95751f622f4011aab0ca065e02ad4`；Markdown `d60bead962252f64a1eb1f0ce05c85bedff01678df3308fa2b410ba93e5ef4f7`。
- 禅道同步：已真实更新 3 条受公共前置影响的已登记用例，逐条回读校验通过；模块 `715` 保持不变。

## 1. 评审结论

- 评审标识：`REV_CASE_REQ-PC-046`
- 评审代理：`case-review-agent`
- 模式：`report_only`
- 评审日期：2026-09-14
- 模块：存发苗间出入库记录
- 用例来源：`04_testcases/pc/TC_REQ-PC-046.yaml`
- 用例数：**12**（当前源文件为 `TC-PC-046-010` 至 `TC-PC-046-021`）
- `case_id`：`TC-PC-046-010` 至 `TC-PC-046-021`；`TC-PC-046-002`～`TC-PC-046-009` 已按禅道用例 `49854~49861` 删除
- `gate_passed: true`
- 内容评审：通过但有观察项
- 正式执行状态：`blocked`，不代表 UI、浏览器、Playwright 或业务结果已通过

本轮已删除旧的 REQ-PC-046 评审 YAML、Markdown 和 HANDOFF，未使用旧评审历史作为本轮结论依据。

## 2. 使用规则与 Skill

规则：

- `test-design-enrichment-rule.md`
- `page-block-coverage-rule.md`
- `automation-judgment-rule.md`

Skill：

- `test-design-techniques`：系统性覆盖评审
- `pict-test-designer`：Pairwise 参数/约束静态覆盖评审
- `qa-playwright-py-writer`：Playwright Python 自动化可执行性评审
- `webapp-testing`：有头页面证据边界评审
- `casely`：结构、字段、风格和交付格式核对

## 3. 结构与统计

> `TC-PC-046-002`～`TC-PC-046-009` 已按禅道用例 `49854~49861` 删除；以下统计均按现有 5 条用例计算。

| 项目 | 结果 |
|---|---:|
| 用例总数 | 12 |
| ID 唯一/连续 | 当前范围内连续：`TC-PC-046-010..021` |
| `feature` | 12 |
| `interface` | 0 |
| `auto: auto` | 12 |
| `auto: no` | 0 |
| `automation_evaluation.status: blocked` | 12 |
| P1/P2/P3/P4 | 8/1/3/0 |
| YAML/Markdown | 已对齐 |
| 需求覆盖 | FR-046-01 至 FR-046-07 均有用例 |
| 计划项覆盖 | PI-046-01 至 PI-046-22 均有用例 |

结构核对通过：

- 当前 `case_id` 为 `TC-PC-046-010..TC-PC-046-021`，唯一且连续；`TC-PC-046-002..009` 已删除。
- 12 条现有用例均具有原子测试目的、追溯和自动化评估。
- 所有现有用例均为 `feature`、`auto=auto`，但均明确为 `blocked`，没有伪造自动化执行结果。
- 当前 YAML `summary.type_counts.auto=0` 是源文件中的统计字段语义问题；明细与 Markdown 校验均以 12 条 `feature`、12 条 `auto` 为准。
- `TC-PC-046-012` 已移除单位固定为“只”的预期，并将原单步字段核对拆分为 5 个步骤和预期，分别覆盖记录查询、基础字段、批次计划、操作人时间、客户园区。

## 4. 五类专项评审

### 4.1 系统性覆盖

结论：`pass_with_observations`。

已覆盖：

- 记录类型、数量正数/零/异常负数、自动出库来源。
- 单个/多个/无关联，当前存发苗间足够/不足/无法分配。
- 默认、单条件、多条件、无匹配、分页、排序、高级筛选展开/收起、表头设置、刷新。
- 发货确认后自动出库记录、数量等于发货数量、类型/方式/单位、批次/操作人/操作时间/养殖客户来源和目标存发苗间分配。
- 有菜单/查看权限、无菜单权限、无查询/查看权限。

已按独立原子目的拆分正向/负向、单关联/多关联/无关联等互斥场景。无数据、加载失败、正式字段名称和部分异常处置保留待确认表达，未臆造产品契约。

### 4.2 Pairwise 覆盖

结论：`covered_with_observations_static_pict_model`。

静态参数包括 `RecordType`、`RecordSource`、`StorageRelation`、`AllocationState`、`QueryFilter`、`QueryResult`、`PaginationState`、`AdvancedFilterState`、`PermissionState`、`DataLoadState`。

已核对约束：确认发货才生成自动出库、数量等于发货数量、不足时才进入下一个关联存发苗间、分配不得产生负库存，以及不能把合格蛋蛋库历史页面字段当作存发苗间正式字段。

未运行外部 PICT 工具，也未生成 PICT 测试集，本结论仅表示静态参数/约束覆盖。

### 4.3 Playwright Python 自动化可执行性

结论：`candidate_but_blocked`；12 条现有用例为自动化候选，当前可执行数为 0。

适合自动化的边界包括正式页面入口、默认列表、查询、重置、分页、排序、高级筛选、表头设置、刷新回读、自动出库字段、关联分配、非负库存和权限分支。

当前正式页面未在 `page.json` 形成范围匹配证据；正式字段、筛选控件、稳定 locator、记录唯一业务键、REQ-PC-042 联动回读、回滚和清理责任未准备。未执行 Playwright，未生成脚本。

### 4.4 有头页面可执行性

结论：`static_review_only_scope_mismatch`。

`page.json` 包含 Chromium 可视模式元数据和只读观察证据，但实际页面为：

- 页面：`pc-stock-inout-records`
- 标题：出入库记录
- 菜单：库存管理 / 合格蛋蛋库 / 出入库记录

这与 REQ-PC-046 的正式范围“库存管理 / 存发苗间 / 出入库记录”不一致。历史状态和观察路径仅作为范围风险证据，未作为正式字段或 locator 契约。本轮未重新打开正式存发苗间页面。

### 4.5 Casely 结构与交付核对

结论：`pass_with_observations`。

字段完整性、ID 唯一连续性、YAML/Markdown 对齐、`feature/auto/priority` 风格及 report_only 交付格式通过。旧评审产物已删除，本轮未采用旧历史结论。未写入远程注册号，未伪造执行结果。

## 5. 页面证据边界

分析资料确认的正式页面契约为：

- 标题：存发苗间出入库记录
- 菜单：库存管理 / 存发苗间 / 出入库记录
- 路由：`/biopark-breeding/breeding/stock/chick/chickrecord`
- `page_id`：`not_in_page_json`

`page.json` 中可见的是范围不匹配的历史页面：

- `page_id=pc-stock-inout-records`
- 菜单：库存管理 / 合格蛋蛋库 / 出入库记录
- 状态：`st-stock-inout-nanjing`、`st-stock-inout-expanded`、`st-stock-inout-column-settings`、`st-stock-inout-reset`

本轮未将这些历史元素、DOM 路径或截图中的列名直接作为正式 REQ-PC-046 页面事实。

## 6. 风险、阻塞与同步清单

| 代码 | 类别 | 结论 |
|---|---|---|
| `PAGE_INVENTORY_SCOPE_MISMATCH` | evidence_risk | page.json 页面为合格蛋蛋库，和存发苗间范围不匹配 |
| `FORMAL_PAGE_NOT_IN_PAGE_JSON` | evidence_risk | 正式 page_id 为 `not_in_page_json` |
| `FORMAL_LOCATOR_CONFIRMATION_PENDING` | evidence_risk | 正式筛选、分页、排序、展开、表头和记录字段缺少 locator |
| `FORMAL_FIELD_CONTRACT_PENDING` | evidence_risk | 正式字段、字段顺序、筛选项和空态/失败态待确认 |
| `HISTORICAL_ELEMENTS_NOT_FORMAL_LOCATORS` | evidence_risk | 历史页面元素未复用为正式定位器 |
| `PERMISSION_BEHAVIOR_UNCONFIRMED` | evidence_risk | 正式权限表现未在授权环境确认 |
| `EMPTY_ERROR_STATE_CONTRACT_PENDING` | evidence_risk | 无匹配、失败、无关联和无法分配处置口径待确认 |
| `FORMAL_ENVIRONMENT_PERMISSION_DATA_NOT_READY` | execution_blocker | 正式环境、权限、脱敏数据、页面结构和责任未准备 |
| `CROSS_MODULE_READBACK_PENDING` | execution_blocker | 发货确认触发自动出库及回读数据未准备 |
| `CROSS_MODULE_WRITE_ROLLBACK_CLEANUP_NOT_READY` | execution_blocker | 跨模块写入、回滚和清理责任未准备 |

以上问题均不作为内容门禁失败，`gate_reasons` 保持空数组。

正式执行前需要准备正式路由、权限、脱敏数据、字段契约、稳定 locator、唯一业务键、跨模块回读、回滚和清理责任。

## 7. 禁止操作确认

- 未读取或生成测试点/XMind。
- 未执行 UI、浏览器或 Playwright。
- 未生成 CSV。
- 未写入远程禅道或测试执行系统。
- 未修改 `04_testcases` 输入文件。
- 未宣称自动化、headed 页面、跨模块联动或业务验证成功。

## 8. 来源哈希

| 来源 | SHA-256 |
|---|---|
| `04_testcases/pc/TC_REQ-PC-046.yaml` | `66d1b4f4b218a57bcbcaa433613fa34b3a2791b525beae181d1dd9f0ba713418` |
| `04_testcases/pc/TC_REQ-PC-046.md` | `2a981649258e9709d89938168c8c450b0295b17bf3540af3c557fc6d5f7f3765` |
| `02_analysis/pc/REQ-PC-046.yaml` | `b14ff8c2114f1249cc70db5ac07183e087a7b532394a216ee7fe1836893572a4` |
| `02_analysis/pc/page_inventory/page.json` | `2d1ee96de735f18ec1d4073f47e818179201051059da6a22ed41ccef7b830c7d` |
| `03_test_plan/pc/TEST_PLAN_REQ-PC-046.yaml` | `60f13cb5bab0d762540c8a92bfcf367829e53711faef76ba6e2256b897a1b5c8` |

本轮输出仅为本地 `report_only` 评审交付物。

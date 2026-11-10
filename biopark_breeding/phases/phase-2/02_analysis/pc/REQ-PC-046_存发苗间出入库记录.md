# REQ-PC-046 存发苗间出入库记录

## 1. 分析结论

REQ-PC-046 对应“二期 / pc / 存发苗间 / 出入库记录”，模块 ID 为 715，优先级 P1。模块清单将其标记为一期已开发、二期无原型的既有功能延续；PC 需求说明书明确二期 PC 存发苗间及出入库记录页面本次不补充页面细节。

本分析固化需求变动中已确认的自动出库业务规则，整理只读记录查询的页面边界候选，并引用 page.json 中现有采集证据。正式路由为 `/biopark-breeding/breeding/stock/chick/chickrecord`，正式菜单路径为“库存管理 / 存发苗间 / 出入库记录”。当前 page.json 的对应页面实际属于“库存管理 / 合格蛋蛋库 / 出入库记录”，与本需求不一致，因此相关页面、状态和元素只能作为范围不匹配的历史采集证据，不能当作正式页面契约。

本阶段不访问库存或出入库真实路由，不执行查询、提交、导出或业务数据变更，不生成测试用例、CSV、接口脚本或 UI 自动化脚本。

## 2. 输入与追溯

- 需求说明书：01_requirements/种禽孵化管理系统二期_需求说明书_合并版.docx
- PC 需求说明书：01_requirements/pc/种禽孵化管理系统二期_PC_需求说明书.docx
- 模块拆分：01_requirements/pc/模块拆分清单.md
- 需求变动：01_requirements/需求变动.md
- 页面清单：02_analysis/pc/page_inventory/page.json
- 输出 YAML：02_analysis/pc/REQ-PC-046.yaml

需求变动优先于需求说明书。模块清单和需求变动均确认该模块承接雏苗发货确认后的自动出库记录；正式路由、菜单路径和权限表现已确认，筛选、字段、排序、分页、展开/收起和表头设置沿用一期页面，本期不重新定义。

## 3. 已确认业务规则

- 存发苗间出入库记录属于 PC 与 APP 共用业务能力。
- 发货执行全部完成后，出入库记录页面只读展示对应自动出库记录。
- 出库记录字段及来源值由本模块验证；生成时机、库存扣减时机及累计变动数量由 REQ-PC-042 负责，本模块不重复验证。
- 出入库类型为“出库”，方式为“自动”，单位为“只”。
- 出库批次取上孵计划批次。
- 操作人和操作时间取雏苗发货记录。
- 养殖客户取当前园区。
- 出库存发苗间由上孵计划关联关系决定。
- 当前存发苗间库存不足时，按关联排列顺序继续分配到下一个存发苗间。
- 不允许产生负库存。

以上是业务口径，不等同于已确认的接口路径、数据库字段或正式页面字段。REQ-PC-045 的库存余额计算和其他入库/出库行为不在本需求范围内。

## 4. 分析范围

### 纳入

- 自动出库记录只读列表和可见字段展示。
- 孵化场、存发苗间等查询条件候选。
- 查询、重置、分页和高级筛选展开/收起候选。
- 表头设置的观察边界和记录展示候选。
- 发货确认后自动生成出库记录、数量和分配顺序的页面可见影响。
- 页面、状态、元素 ID 和 DOM/截图证据路径的追溯。

### 排除

- REQ-PC-042 发货执行页面、发货录入和发货提交。
- REQ-PC-045 存发苗间库存余额计算。
- APP 出入库记录页面和移动端专属规则。
- 导出按钮功能；导出属于一期页面能力，本期不考虑。
- 手工入库、手工出库、库存调整、盘点、记录修改、记录删除和业务数据修复。
- 接口路径、请求/响应字段、错误码、接口断言和接口测试。
- 未授权真实页面访问、业务提交、真实数据变更、测试用例、CSV 和自动化脚本。

## 5. 页面证据与范围冲突

page.json 中可追溯页面为 pc-stock-inout-records，其当前页面事实如下：

- 标题：出入库记录
- 菜单路径：库存管理 / 合格蛋蛋库 / 出入库记录
- REQ-PC-046 需求范围：库存管理 / 存发苗间 / 出入库记录
- 当前页面证据状态：历史采集证据，不是正式 REQ-PC-046 页面契约。
- 正式路由：`/biopark-breeding/breeding/stock/chick/chickrecord`，已确认但本次不探索。
- 正式菜单：`库存管理 / 存发苗间 / 出入库记录`，已确认。

可引用状态：

- st-stock-inout-nanjing：默认列表历史状态，证据 02_analysis/pc/page_inventory/dom/req-pc-046-segmented-capture.md 及三段截图。
- st-stock-inout-expanded：高级筛选展开历史状态，证据 02_analysis/pc/page_inventory/dom/req-pc-046-reexplore-expanded.md 及截图。
- st-stock-inout-column-settings：表头设置观察历史状态，证据 02_analysis/pc/page_inventory/dom/req-pc-046-reexplore-column-settings.md 及截图。
- st-stock-inout-reset：重置按钮观察历史状态，证据 02_analysis/pc/page_inventory/dom/req-pc-046-reexplore-reset.md 及截图。

可追溯的历史元素候选包括：page-layout、filter-hatchery、filter-storage、btn-query、btn-reset、btn-expand、btn-collapse、filter-advanced、btn-column-settings、btn-export、el-table-stock-inout、pagination-page-size、pagination-prev、pagination-next、pagination-page。

这些 ID 仅表示现有页面清单中的历史元素。filter-storage 不直接等同于正式的“存发苗间”筛选，btn-export 仅为一期历史按钮证据，不属于本期功能；不新增、覆盖或修正 page.json，不复制其中的演示业务值或环境地址。

## 6. 页面与数据契约边界

### 页面层候选

正式页面路由和菜单路径已确认。筛选项、字段及顺序、排序、分页、展开/收起和表头设置沿用一期页面，本期不重新定义；导出按钮功能属于一期，本期不考虑。本期页面关注点仅为表格是否展示雏苗发货产生的出入库数据。

表格无数据、加载失败、记录生成失败或异常数据时显示“暂无数据”。

### 自动出库数据规则

自动出库记录由“上孵计划确认发货”触发，数量等于本次发货数量，类型为“出库”，方式为“自动”，单位为“只”；批次取上孵计划批次，操作人和操作时间取雏苗发货记录，养殖客户取当前园区。出库存发苗间由上孵计划关联关系决定；库存不足时按关联排列顺序继续分配，且不得产生负库存。

### 接口边界

本阶段不考虑接口路径、方法、请求体、响应体、错误码或分页协议；不执行接口测试、接口断言或接口注入。仅记录页面可见业务概念和已确认规则。

### 权限表现

- 菜单无权限时不显示“库存管理 / 存发苗间 / 出入库记录”菜单。
- 查询或查看接口无权限时提示“没有操作权限”。
- 权限由平台角色菜单/接口权限配置，不写死具体角色、权限编码、账号或凭据。

## 7. 系统化边界候选

### 等价类与边界值

- 记录类型：出库、其他类型。
- 数量：正数、零、异常负数。
- 来源：自动出库、其他来源。
- 存发苗间关联：单个、多个按顺序、无关联。
- 库存分配：当前存发苗间足够、不足需继续分配、无法分配。
- 查询结果：有数据、单条、多条、无匹配、加载失败。
- 筛选条件：默认、单条件、多条件、无匹配。
- 分页：首、中、末页及无分页。
- 高级筛选：展开、收起。
- 权限：有菜单/查看权限、无菜单权限、无查看权限。

### 决策表维度

- 是否由上孵计划确认发货触发。
- 是否存在有效上孵计划与存发苗间关联。
- 当前存发苗间库存是否足够。
- 是否需要按关联顺序继续分配。
- 查询是否成功、是否存在匹配记录。
- 是否具备菜单和查看权限。

### 状态转换候选

页面进入 → 默认记录列表
设置筛选 → 查询结果 → 分页浏览
展开高级筛选 → 高级筛选区域 → 收起高级筛选
打开表头设置 → 观察配置状态 → 返回列表
无数据/加载失败 → 空状态或异常状态
发货确认 → 自动生成出库记录 → 出入库记录可查询

### PICT 参数候选

| 参数 | 候选值 |
| --- | --- |
| RecordType | Outbound、OtherType、NotProvided |
| RecordSource | AutoFromShipment、OtherSource、NotProvided |
| StorageRelation | Single、OrderedMultiple、None、NotProvided |
| AllocationState | CurrentStorageSufficient、ContinueNextStorage、CannotAllocate、NotProvided |
| QueryFilter | Default、SingleCondition、MultipleConditions、NoMatch、NotProvided |
| QueryResult | HasData、Empty、LoadFailed、NotProvided |
| PaginationState | NoPagination、FirstPage、MiddlePage、LastPage、NotProvided |
| AdvancedFilterState | Collapsed、Expanded、NotProvided |
| PermissionState | MenuAllowed、MenuDenied、ViewAllowed、ViewDenied、NotProvided |
| DataLoadState | Loaded、Empty、Failed、NotExecuted |

候选约束：只有确认发货才生成自动出库记录；记录数量等于本次发货数量；库存不足才进入下一个关联存发苗间；分配不得产生负库存；当前历史页面范围不匹配，不能把合格蛋蛋库字段直接当作正式字段。以上仅为边界分析候选，不是测试用例或 PICT 测试集。

## 8. 角色、依赖与风险

### 角色

- 存发苗间出入库记录查看人员：查看自动生成的出库记录；菜单、查询和查看权限按平台角色权限配置。
- 孵化场发货相关人员：通过发货确认产生记录来源；发货执行不在本需求页面分析。
- 产品、研发、测试、实施及业务培训人员：评审和验收业务边界，不形成正式权限矩阵结论。

### 依赖

- REQ-PC-042 提供确认发货事件、本次发货数量、操作人和操作时间。
- REQ-PC-045 提供存发苗间库存约束的关联参考。
- 上孵计划与存发苗间关联关系决定出库目标和不足时的分配顺序。
- 存发苗间、园区、上孵计划和自动出库记录测试数据支持正式查询。

### 风险

- page.json 的页面范围是合格蛋蛋库，不是存发苗间；历史字段和元素不能直接作为正式契约。
- 二期页面无原型，一期页面细节需在测试计划阶段核对；本期只形成表格数据展示的页面范围。
- 自动出库记录生成和跨存发苗间分配依赖 REQ-PC-042 与真实业务数据，当前不能仅凭页面清单验证。
- 历史页面存在导出入口，但导出属于一期，本期不考虑按钮功能。

## 9. 自动化边界

正式页面确认后，Playwright 定位优先使用 get_by_role、get_by_label、get_by_test_id 和页面区域作用域。重复记录行、分页和高级筛选控件需要稳定、唯一且可观察的定位标识。

当前只能引用历史候选 ID，不能据此生成自动化脚本，也不能将“合格蛋蛋库”页面的元素直接用于存发苗间页面。自动化保持可视浏览器 headless=False，不写入凭据或真实业务数据。

## 10. 待确认问题与门禁

业务待确认项：无。

门禁采用 `report_only`，`gate_passed=false`。原因仅为正式测试数据、页面执行环境、权限配置和数据清理责任未完全提供；允许继续进入 `stage-test-plan-agent`，不因业务契约问题阻断下游。

## 11. 数据责任与交接结论

- 本次未访问库存或出入库真实路由，未执行查询、提交、导出或业务数据变更。
- 清理状态为 not_applicable；未来测试数据由授权测试责任人准备、维护和清理。
- 不写入账号、密码、Token、Cookie、具体环境地址或未经授权业务数据。
- 正式路由为 `/biopark-breeding/breeding/stock/chick/chickrecord`；菜单无权限不显示，查询/查看无权限提示“没有操作权限”。
- 本期仅关注表格是否展示雏苗发货产生的出入库数据；表格无数据、加载失败、记录生成失败或异常数据时显示“暂无数据”。
- page.json 保持不变；本次任务开始时观察 SHA-256 为 7BDB2C0258FA6DB98EE989A01070F0FAA3AD4C949DEA7EE795163B7B1E592CA2。
- 下一阶段：stage-test-plan-agent，先确认正式页面契约和权限/数据前提，再制定页面功能测试计划；不扩展为接口测试。

# REQ-PC-046 测试用例交接

## 2026-10-14 导航文案修订

- 仅更新公共前置 `inventory_records_page_access` 的 action：明确“在左侧菜单中展开「库存管理」”，在子菜单中展开「存发苗间」，并将“出入库记录”明确为“菜单项”。
- `TC-PC-046-012` 中的“上孵计划”属于自动出库记录字段来源核对内容，不属于页面导航，未修改该内容。
- YAML/Markdown 已重新生成并通过对齐及模板校验。
- 来源哈希：YAML `056dfb0121cca98607872f208dc7504e3da95751f622f4011aab0ca065e02ad4`；Markdown `d60bead962252f64a1eb1f0ce05c85bedff01678df3308fa2b410ba93e5ef4f7`。
- 禅道同步：已真实更新 3 条受公共前置影响的已登记用例并逐条回读校验通过；注册表映射有效，模块 `715` 未改变。

## 规则标识

- `test-design-enrichment-rule.md`：已完整读取，用于入口、前置条件、原子性、步骤预期、优先级、文本隔离和覆盖账本检查。
- `page-block-coverage-rule.md`：已完整读取，用于页面入口、列表/筛选/分页/高级筛选/表头设置的 L1/L2/L3 覆盖检查。
- 已调用 `test-design-techniques`、`pict-test-designer`、`qa-playwright-py-writer`、`webapp-testing`、`casely`；本阶段仅静态设计，不执行 UI，不生成脚本。

## 检查范围

- 输入：`02_analysis/pc/REQ-PC-046.yaml`、`03_test_plan/pc/TEST_PLAN_REQ-PC-046.yaml`、`02_analysis/pc/page_inventory/page.json`。
- 输出：`04_testcases/pc/TC_REQ-PC-046.yaml`、`04_testcases/pc/TC_REQ-PC-046.md`。
- 模块：PC 存发苗间出入库记录，模块 ID `715`。
- 页面入口：`/biopark-breeding/breeding/stock/chick/chickrecord`。

## 原子目的与系统化设计

- 等价类/边界：单/多/无关联；当前库存足够/不足；有数据/无数据/加载失败；默认/单条件/多条件/无匹配；首/中/末页；菜单/查看权限允许或拒绝。
- 判定表：发货确认、有效关联、库存足够、是否继续分配、查询是否成功、是否具备菜单和查看权限分别独立判定。
- 状态转换：页面进入→默认列表；筛选→查询→分页；高级筛选展开→收起；发货确认→自动记录→页面回读。
- Pairwise 模型参数：`RecordType`、`RecordSource`、`StorageRelation`、`AllocationState`、`QueryFilter`、`QueryResult`、`PaginationState`、`AdvancedFilterState`、`PermissionState`、`DataLoadState`。约束为确认发货才生成自动出库、不足才继续关联、分配不产生负库存；本阶段保留模型依据，不执行真实 PICT 或 UI。

## 公共前置改造

- `inventory_records_page_access`：登录系统；从应用门户进入「种禽孵化管理系统」；展开「库存管理 > 存发苗间」并点击「出入库记录」。
- 正常业务用例复用该公共前置；查询失败、无菜单权限和无查询/查看权限场景保留独立异常入口。

## L1/L2/L3 覆盖账本

- L1 页面/板块：记录区、分页、权限入口；对应当前保留的 `TC-PC-046-020/021`。
- L2 字段/控件：记录字段和权限提示；当前保留对应 `TC-PC-046-018` 至 `021`；`TC-PC-046-002`～`009` 已按禅道 `49854~49861` 删除。
- L3 值/规则：自动生成、数量、类型、方式、单位、来源字段、单/多/无关联、顺序分配和非负库存；对应 `TC-PC-046-010` 至 `017`。
- 每条用例只绑定一个 `coverage_id`、`plan_item_id` 和 `atomic_purpose_id`；未使用页面资料字段作为门禁依据。

## 证据阻塞与未确认项

1. `page.json` 的历史页面为“库存管理 / 合格蛋蛋库 / 出入库记录”，与本需求“库存管理 / 存发苗间 / 出入库记录”不匹配；不得将历史字段或定位器当作正式契约。
2. REQ-PC-046 正式页面未独立探索，Lanhu mapping 缺失；正式页面字段、筛选控件、空态、失败态和稳定定位器待执行前确认。
3. 自动出库、跨存发苗间关联顺序、库存不足和无关联数据依赖 REQ-PC-042、REQ-PC-045 及授权可回收测试数据。
4. 菜单、查询和查看权限配置、正式环境 URL、租户、数据回读和清理责任未提供。
5. 所有相关用例标记 `blocked` 或 `partial`，未执行内容未写成通过。

## 设计自检

- 前置条件只描述账号、权限、环境、浏览器、数据和初始状态；导航动作写入步骤。
- 页面到达步骤具有标题、区域或加载状态等可观察预期。
- 用例按单一原子目的拆分；字段展示、字段正确性、联动、分配、筛选、权限和异常未合并。
- 人工文本未引用 `page.json`、`state_id`、CSS、定位器或自动化术语；未使用范围否定步骤补偿覆盖。
- YAML/Markdown 用例数、需求、计划、入口和阻塞结论一致；未生成 `tp_id`、测试点、CSV、禅道同步结果、UI 执行结果或 Playwright 脚本。

## 交付门禁结论

**BLOCKED / 设计完成，待正式页面、环境、权限、数据和定位器证据补齐后进入评审。**

页面资料不匹配、Lanhu mapping 缺失和正式页面未探索仅作为风险、依赖或执行准备项，不作为本用例评审的失败门禁理由；当前阻塞来自真实执行证据和测试数据未提供。下一阶段：`stage-case-review-agent`。

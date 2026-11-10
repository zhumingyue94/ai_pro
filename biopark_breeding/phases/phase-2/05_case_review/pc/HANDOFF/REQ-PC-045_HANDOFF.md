# REQ-PC-045 评审交接

## 2026-10-14 导航文案修订

- 仅更新公共前置 `inventory_query_page_access` 的 action：明确“在左侧菜单中展开「库存管理」”，在子菜单中展开「存发苗间」，并将“库存查询”明确为“菜单项”。
- REQ-PC-045 当前 YAML 未包含计划管理、雏苗发货、上孵计划、出入库记录或孵化需求目标文案，未修改其他内容。
- YAML/Markdown 已重新生成并通过对齐及模板校验。
- 来源哈希：YAML `237c80a8e0fc256c7468dc4d042b9b889ea1eab4da1f1c19b22c97680842dd10`；Markdown `e75077741a8f9bb063773adb9bc6cc8dbf53debfe80de08b9fc2ace84941b259`。
- 禅道同步：已真实更新 4 条受公共前置影响的已登记用例并逐条回读校验通过；注册表映射有效，模块 `720` 未改变。

## 1. 模块身份

- 评审标识：`REV_CASE_REQ-PC-045`
- 分区：`pc`
- 需求/模块 ID：`REQ-PC-045`
- 模块：存发苗间库存查询
- 评审代理：`case-review-agent`
- 评审修订版本：3
- 模式：`report_only`
- 交接状态：`design_review_passed_with_execution_blockers`
- 评审产物：`05_case_review/pc/REV_CASE_REQ-PC-045.yaml`、`05_case_review/pc/REV_CASE_REQ-PC-045.md`
- 用例产物：`04_testcases/pc/TC_REQ-PC-045.yaml`、`04_testcases/pc/TC_REQ-PC-045.md`

本轮未发现 `05_case_review/pc/` 下 REQ-PC-045 专属旧评审产物，未使用历史评审结论。本交接未回退到共享文件。

## 2. 评审结论

- 设计门禁：`gate_passed: true`
- 原门禁问题：`TRACEABILITY_MISSING_FR_045_01`、`TRACEABILITY_MISSING_FR_045_05`，已由用例追溯字段修复
- 执行门禁：未执行，保持 `execution_status: not_executed`
- 用例：4 条，当前为 `TC-PC-045-009` 至 `TC-PC-045-022`；`TC-PC-045-002`～`TC-PC-045-008` 已按禅道用例 `49832~49838` 删除
- 类型：`feature=4`、`interface=0`
- 自动化候选：`auto=4`；自动化评估 `status=blocked` 为 14 条
- 优先级：P1/P2/P3/P4 = `7/3/4/0`
- YAML 与 Markdown：统计、编号、标题、优先级、类型、自动化字段、追溯、步骤和预期一致
- 正式执行：未执行，不能视为 UI、浏览器、Playwright 或业务验证通过

## 公共前置改造

- `inventory_query_page_access`：登录系统；从应用门户进入「种禽孵化管理系统」；展开「库存管理 > 存发苗间」并点击「库存查询」。
- 正常库存查询用例复用该公共前置；无菜单权限、无查询/数据权限和查询失败场景保留独立异常入口。

## 3. 覆盖账本

已覆盖：

- `FR-045-01`：已由 `TC-PC-045-001` 归属，PC 与 APP 共用业务能力
- `FR-045-02`：雏苗发货确认后自动生成存发苗间出库记录
- `FR-045-03`：出库数量、类型、方式和单位
- `FR-045-04`：批次、操作人、操作时间、养殖客户等字段来源
- `FR-045-05`：已由 `TC-PC-045-011` 归属，关联顺序分配
- `FR-045-06`：库存计算、零库存和非负库存
- `FR-045-07`：既有库存查询功能延续

已解决的原门禁覆盖：

- `FR-045-01`：已由 `TC-PC-045-001` 的 `coverage_ids` 归属
- `FR-045-05`：已由 `TC-PC-045-011` 的 `coverage_ids` 归属

观察项：

- `PI-045-15` 已补充对应原子测试目的 `AP-045-15`，但与 `PI-045-14` 同由 case 014 承接，需计划负责人确认是否拆分。
- 等价类、边界值、判定表、状态转换和静态 Pairwise 参数均已覆盖主要场景；静态 Pairwise 仍未运行外部 PICT 工具。

## 4. 页面证据与执行边界

正式页面登记为：

- 标题：存发苗间库存查询
- 菜单：库存管理 / 存发苗间 / 库存查询
- 路由：`/biopark-breeding/breeding/stock/chick/chick-inventory`
- 页面标识：`pc-inventory-query`

当前 `page.json` 的结构化元素、表单、表格和交互为空，正式字段与 locator 未确认。该事实作为 `evidence_risk` 和执行准备项，不作为本轮门禁失败依据。

本轮未执行：

- UI 测试或有头页面操作
- Playwright 脚本生成或执行
- PICT 工具运行或测试集生成
- CSV 生成
- 测试点/XMind 读取或生成
- 远程禅道写入、同步或导入

## 5. 修复和同步清单

| 项目 | 状态 |
|---|---|
| 评审 YAML | 已更新，设计门禁已通过 |
| 评审 Markdown | 已更新，设计门禁已通过 |
| 当前 REQ-ID HANDOFF | 已更新 |
| FR-045-01 追溯归属 | 已修复：TC-PC-045-001 |
| FR-045-05 追溯归属 | 已修复：TC-PC-045-011 |
| PI-045-15/AP-045-15 映射 | 已补充 AP-045-15 |
| YAML/Markdown 结构一致性 | 已通过 |
| UI/浏览器/Playwright 执行 | 未执行 |
| PICT 实际运行 | 未执行 |
| CSV | 未生成 |
| 测试点/XMind | 未读取、未生成 |
| 远程禅道同步 | 未执行 |

## 6. 来源哈希

- `04_testcases/pc/TC_REQ-PC-045.yaml`: `da23c9faa7c39cc4b8c4af9bcaacd4355424ad814bc2d4ccca1a983e56b36588`
- `04_testcases/pc/TC_REQ-PC-045.md`: `2753cf3f94a08998bc94955d5833390e50a9f53d5a6a6056bc2f3747a85cd082`
- `02_analysis/pc/REQ-PC-045.yaml`: `1472dca5b69e08714b24e9d00836e79963f1e41591e5364262832033209b60fa`
- `02_analysis/pc/page_inventory/page.json`: `2d1ee96de735f18ec1d4073f47e818179201051059da6a22ed41ccef7b830c7d`
- `03_test_plan/pc/TEST_PLAN_REQ-PC-045.yaml`: `58b0b0d03ac03c9dc01f45b2814c01f920b4c6a134c6174dfac8d747b9f585b9`

## 7. 下游交接

本轮 report_only 评审确认设计追溯门禁已通过；正式 UI 或自动化执行仍需另行授权，并准备页面字段、locator、权限、脱敏数据、唯一业务键以及跨需求回读和清理责任。`PI-045-15/AP-045-15` 的同用例承接仍待计划负责人复核。

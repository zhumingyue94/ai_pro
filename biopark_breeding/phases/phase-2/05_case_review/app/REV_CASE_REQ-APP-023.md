# REQ-APP-023 用例评审

## 1. 评审结论

- 评审代理：`case-review-agent`
- 模式：`report_only`
- 评审日期：2026-10-09
- 用例数量：19 条，ID 范围 `TC-APP-023-002` 至 `TC-APP-023-030`，唯一；`TC-APP-023-007` 已按禅道用例 51356 删除，`TC-APP-023-019` 已按禅道用例 51368 删除，`TC-APP-023-022` 已按禅道用例 51371 删除
- 公共前置同步：`app_shipment_records_access` 已按方案保留三步具体入口；`TC-APP-023-019` 权限异常用例不引用成功页面公共前置，继续使用独立异常触发链路。
- 设计门禁：**通过（保留证据观察项）**
- 已解决门禁问题：`REQ_APP023_COUNT_LABEL_ASSERTION_MISSING`、`AUTOMATION_SUMMARY_SCHEMA_MISMATCH`
- 正式执行：未执行，不代表 UI、浏览器、Playwright、PICT 或业务结果通过

第 4 点“列表标题右侧显示‘共 n 条’”已在 `TC-APP-023-003` 中补充固定文案、位置和全部记录统计口径断言；`TC-APP-023-022`（禅道 51371）已删除。

## 2. 评审依据与范围

### 输入

- `04_testcases/app/TC_REQ-APP-023.yaml`
- `04_testcases/app/TC_REQ-APP-023.md`
- `02_analysis/app/REQ-APP-023.yaml`
- `03_test_plan/app/TEST_PLAN_REQ-APP-023.yaml`
- `02_analysis/app/page_inventory/page.json`
- `02_analysis/app/page_inventory/lanhu_page_mapping/REQ-APP-023_lanhu_page_mapping.json`
- `reference/casely/`

### 应用规则与 Skill

- `test-design-enrichment-rule.md`
- `page-block-coverage-rule.md`
- `automation-judgment-rule.md`
- `test-design-techniques`
- `pict-test-designer`
- `qa-playwright-py-writer`
- `webapp-testing`
- `casely`

旧的 REQ-APP-023 评审 YAML、Markdown 和 HANDOFF 已在本轮评审前删除；本轮未使用旧评审历史。

## 3. 评审结果

### 3.1 结构、字段和对齐

| 项目 | 结果 |
|---|---:|
| YAML 可解析 | 通过 |
| 用例 ID 唯一/连续 | 是 / 否（删除 007、022） |
| feature / interface | 20 / 0 |
| auto / no | 20 / 0 |
| P1 / P2 / P3 / P4 | 4 / 10 / 6 / 0 |
| YAML 与 Markdown 数量、ID、标题、优先级、auto、type、步骤对齐 | 通过 |

Casely 检查结论：结构、字段、标题、前置条件、步骤、预期及 `report_only` 交付格式总体符合项目参考风格；未生成 CSV，未写入远程禅道。

### 3.2 系统性用例覆盖评审

使用等价类、边界值、判定表、状态转换和异常覆盖进行评审。

已覆盖：

- 空记录、1 条、多条和大数据量；
- 空态/有记录态、提交时间倒序、汇总、多位置明细；
- 返回列表保留日期、栋舍、状态、搜索关键字和页签；
- 权限、非法上下文及加载阈值。

缺口：

- 已补充 `TC-APP-023-003`：明确验证列表标题行右侧固定文案“共 n 条”、位置、0/1/3/超过 3 条边界；其中 `TC-APP-023-003` 已将发货单号、累计发货数量和记录数量拆分为独立步骤与预期。
- `TC-APP-023-007` 已按禅道用例 51356 删除，相关平铺展示断言不再作为本轮覆盖范围。
- `TC-APP-023-023` 的时间预期已统一为严格符合 `YYYY-MM-DD HH:SS` 格式，移除额外的“日期、小时、分钟和秒均按两位显示”表述。

结论：`pass_with_observations`；固定文案/位置及平铺统计口径缺口已整改，仍保留时间格式、页面归属和执行准备观察项。

### 3.3 Pairwise 覆盖评审

采用 PICT 2-way 静态模型，未执行 PICT。

参数：入口上下文、记录数分区、记录状态、位置数量、排序、折叠状态、加载规模、权限状态、返回上下文、页面归属。

约束覆盖：

- 空记录显示空状态且无记录明细；
- 未授权不可查看记录内容；
- 非法发货单上下文不展示无关数据；
- 页面归属确认前不将 APP-024 静态证据视为 APP-023 执行证据。

结论：`covered_with_observations_static_pict_model`；本轮不执行 PICT，未伪造生成集或执行结果。

### 3.4 Playwright Python 自动化可执行性评审

结论：`candidate_but_blocked`。

- 20 条均为自动化候选；
- 当前可执行数为 0；
- 正式环境、查询权限、脱敏只读数据、清理责任、正式路由、页面归属和稳定定位器尚未确认；
- 性能测量边界、分页/加载契约及错误响应契约尚未就绪；
- 本轮未生成或执行 Playwright 脚本。

这些属于执行准备或证据阻塞，不替代设计门禁判断。

### 3.5 有头页面可执行性评审

结论：`static_review_only`。

静态参考页面为 `app-plan-shipment-records`，页面资料和截图可用于区域语义参考；页面结构/路由存在 APP-023 与 APP-024 交叉，正式归属待确认。本轮未启动浏览器，静态资料不等同于正式页面执行证据。

### 3.6 优先级逐条评审

按 `test-design-enrichment-rule.md` 的业务影响、核心流程、关键数据、使用频率和替代路径逐条复核 20 条用例：

- P1：4（19.05%）
- P2：11（52.38%）
- P3：6（28.57%）
- P4：0（0%）
- 调整：0 条
- 未评审：0 条

分布与参考比例存在偏离，已记录为 `priority_distribution_observation`，不作为门禁，也未为满足比例擅自改写优先级。正式使用频率和替代路径仍需业务方确认。

## 4. 问题与门禁

| 编码 | 类别 | 结果 | 门禁 |
|---|---|---|---|
| `REQ_APP023_COUNT_LABEL_ASSERTION_MISSING` | `design_violation` | 已整改：003/008/010 补充文案、位置、边界及折叠统计断言 | 否 |
| `AUTOMATION_SUMMARY_SCHEMA_MISMATCH` | `design_violation` | 已整改：摘要仅保留实际 auto 统计 | 否 |
| `TIME_FORMAT_CONTRACT_AMBIGUOUS` | `evidence_risk` | 时间格式待确认 | 否 |
| `PAGE_APP023_APP024_OWNERSHIP_CROSS_MAPPING` | `evidence_risk` | 页面归属/路由待确认 | 否 |
| `PERFORMANCE_EXECUTION_NOT_READY` | `execution_blocker` | 性能正式执行条件未就绪 | 否 |
| `FORMAL_UI_AUTOMATION_NOT_EXECUTED` | `execution_blocker` | 本轮未执行 UI/自动化 | 否 |

### 整改建议

补充至少一个用例或拆分现有用例，明确验证：

1. 列表标题行右侧出现“共 n 条”；
2. n 等于当前发货单全部有效发货记录数；
3. 覆盖 0、1、3、超过 3 条边界；
4. 折叠展示 3 条时，n 仍为全部记录数而非可见 3 条。

## 5. 禁止事项确认

- 未读取或生成测试点/XMind；
- 未执行 UI 测试、浏览器或 Playwright；
- 未生成 CSV；
- 未写入远程禅道；
- 未伪造 Execute、远程导入成功或业务执行成功。

## 6. 来源哈希

详见同目录 `REV_CASE_REQ-APP-023.yaml` 的 `source_hashes`，并已同步至模块专属 HANDOFF。

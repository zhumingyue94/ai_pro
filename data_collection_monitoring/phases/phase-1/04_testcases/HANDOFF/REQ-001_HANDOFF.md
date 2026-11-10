# REQ-001 测试用例交接

## 交接状态

`report_only_blocked_scoped_readonly_ui_verification`

## 规则与输入

- 规则：`test-design-enrichment-rule.md`、`page-block-coverage-rule.md`。
- 技能：`test-design-techniques`、`pict-test-designer`、`qa-playwright-py-writer`、`webapp-testing`、`casely`。
- 输入：`02_analysis/REQ-001.yaml`、`03_test_plan/TEST_PLAN_REQ-001.yaml`、`02_analysis/page_inventory/page.json`、`.env`、需求变动记录。
- 输出事实源：`04_testcases/TC_REQ-001.yaml`；Markdown 由 `render_testcase_markdown.py` 派生。

## 覆盖账本

- 页面身份：路由、标题、菜单路径；对应 `AP-001-001`。
- 默认结构：日期控件、时间间隔、四类指标、三类图表；对应 `AP-001-002`。
- 日期边界：默认范围、最近七天、今天、跨月、未来范围；对应 `AP-001-003` 至 `AP-001-007`。
- 时间桶：天、周、月/季度/年；对应 `AP-001-008` 至 `AP-001-010`。
- 统计口径：租户、唯一编号、设备状态、消息到达时间；对应 `AP-001-011` 至 `AP-001-013`。
- 异常与行为：无数据、筛选更新、只读汇总、租户边界、无自动刷新；对应 `AP-001-014` 至 `AP-001-018`。
- 页面状态覆盖：`home_default`、`home_date_range`、`home_filtered_week_recent7`；`home_menu_expanded` 仅作为页面事实参考，未虚构菜单操作步骤。
- Pairwise 设计：保留 Tenant、Range、Boundary、Interval、Data、Message、Action、Result 参数及约束；本次不执行实际 PICT 生成或 UI 操作。

## 2026-10-29 修改禅道用例52129

- `TC-REQ-001-022` 保持原子目的和稳定禅道映射不变。
- 环状图验证已拆分为四个明确操作及逐项预期：观察图表、逐类悬停、记录提示数量、核对批准基线。
- YAML 为事实源，Markdown 已重新派生；用例总数和编号集合未变化。

## 原子性检查

- 每条用例仅包含一个 `atomic_purpose_ids`。
- 未生成测试点、CSV、禅道同步结果、UI 执行结果或 Playwright 脚本。
- 日期范围、时间桶、统计口径、异常、筛选、权限和只读边界均拆分为独立用例。
- 统计正确性、权限、租户、时区、异常、刷新和跨模块一致性因证据不足标记 `blocked`，未伪造通过。

## 页面与自动化边界

- 已使用 page.json 已确认的 `home_start_date`、`home_end_date`、`home_interval` 及已登记文本/可访问名称候选。
- 指标和 canvas 图表只验证已登记区域语义；动态数值、错误提示、刷新控件和加载状态未猜测定位器。
- 自动化评估仅记录在 YAML 的 `automation_evaluation`，不生成脚本；当前正式环境、授权账号、稳定运行时 DOM 和批准数据未闭环。

## 阻塞与未确认项

- `page.json` 的 `collection_status` 为 `partial`。
- 用户时区、租户上下文、唯一编号、消息到达时间和跨模块关联字段缺少运行时证据。
- 五种时间桶的完整结果、空数据、部分缺失、异常、刷新、失败、超时和权限状态尚未真实采集。
- 正式 PDF 的 REQ-001 章节逐条追溯仍待产品/分析负责人确认。
- 不得将上述缺口判定为失败；执行前应补充脱敏只读数据和页面证据。

## 门禁结论

通过设计交付门禁：YAML 为唯一事实源，Markdown 由脚本派生，范围保持只读且页面证据边界明确。执行门禁不通过：在环境、权限、数据和运行时页面证据补齐前，相关用例保持 blocked/report-only。
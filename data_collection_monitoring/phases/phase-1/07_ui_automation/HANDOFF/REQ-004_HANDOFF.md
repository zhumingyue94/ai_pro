# REQ-004 UI 自动化交接

- module_id：`733`
- 模块：`设备分组`
- 资格：仅执行 `priority: P3` 且 `auto: auto` 的 10 条用例；本模块未纳入的 P3 `auto: no` 用例为 `excluded`（如源数据存在）。
- 执行范围：`TC-REQ-004-009, TC-REQ-004-016, TC-REQ-004-020, TC-REQ-004-022, TC-REQ-004-023, TC-REQ-004-024, TC-REQ-004-025, TC-REQ-004-026, TC-REQ-004-027, TC-REQ-004-028`
- RUN：`07_ui_automation/reports/RUN_20261110T072513Z/`
- headed 浏览器：`headless: false`；复用 `07_ui_automation/auth-state.json`。
- 统计：`total: 10; passed: 6; product_defect: 4; test_script_error: 0; test_case_error: 0; blocked: 0; excluded: 0`
- 清理：`009/016/020/022/023/024/025/026` 未产生业务写入；`027/028` 发现测试分组被保存，因当前页面对象没有经过验证的安全删除契约，未伪造清理成功，已作为产品缺陷保留证据。
- 证据：默认生成视频和 SHA-256；失败用例生成截图；RUN 内无 `logs/`，无 `allure-report/`（Allure CLI 未成功生成 HTML），保留 `allure-results/`。
- 报告产物：`selection.yaml`、`results.yaml`、`case_results.xlsx`、`bug.xlsx`、`bugs_review.yaml`、`screenshots/`、`videos/`、`hashes/`、`allure-results/`。
- 不在 RUN 目录生成 Handoff.md；未创建远程 Bug。

## 逐条结果
- `TC-REQ-004-009`：`passed`；新增设备分组弹窗的名称、状态、描述及确定/取消控件可见可交互，取消后列表稳定。
- `TC-REQ-004-016`：`passed`；大小写变体查询完成，结果符合当前页面匹配规则。
- `TC-REQ-004-020`：`passed`；组合筛选后回到第 1 页，筛选条件保持。
- `TC-REQ-004-022`：`passed`；无匹配分组显示空结果状态。
- `TC-REQ-004-023`：`passed`；重置清空筛选条件并恢复默认列表。
- `TC-REQ-004-024`：`passed`；刷新后列表和分页状态符合预期。
- `TC-REQ-004-025`：`product_defect`；空名称提交未显示名称必填提示。视频：`videos/TC-REQ-004-025.webm`；截图：`screenshots/TC-REQ-004-025-failure.png`。
- `TC-REQ-004-026`：`product_defect`；纯空格名称提交后未显示名称校验提示。视频：`videos/TC-REQ-004-026.webm`；截图：`screenshots/TC-REQ-004-026-failure.png`。
- `TC-REQ-004-027`：`product_defect`；描述为空的合法名称分组被保存，且当前页面对象无安全删除契约，未伪造清理成功。视频：`videos/TC-REQ-004-027.webm`；截图：`screenshots/TC-REQ-004-027-failure.png`。
- `TC-REQ-004-028`：`product_defect`；特殊描述分组被保存，且当前页面对象无安全删除契约，未伪造清理成功。视频：`videos/TC-REQ-004-028.webm`；截图：`screenshots/TC-REQ-004-028-failure.png`。

## 缺陷结论
已确认 4 条产品行为问题，缺陷信息仅写入 RUN 内 `bug.xlsx`、`bugs_review.yaml` 及本模块 Handoff；未自动创建远程 Bug。

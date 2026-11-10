# 745 数据监听 模块级 UI 自动化交接（REQ-007 P3）

- module_id：`745`
- 需求：`REQ-007` 数据监听
- RUN：`07_ui_automation/reports/RUN_20261110T150000Z/`
- 执行时间：2026-11-10
- 统计：`total: 9; passed: 4; blocked: 2; excluded: 3`
- 缺陷数量：`0`；远程 Bug：未创建
- 结构化结果：`07_ui_automation/data/REQ-007_P3_results.yaml`
- 页面对象：`07_ui_automation/pages/req007/data_monitor_page.py`
- 独立脚本：`07_ui_automation/tests/module_REQ-007/`（4 个最终通过用例脚本）

## 逐条结果

| 用例 | 结果 | 说明 |
|---|---|---|
| TC-REQ-007-006 | passed | 空规则名称显示“规则名称不能为空”，表单保持打开且无写入 |
| TC-REQ-007-007 | passed | 非法名称样本未进入保存成功状态，列表无新增记录 |
| TC-REQ-007-008 | blocked | 缺少已批准的同租户重复规则样本与隔离验证授权 |
| TC-REQ-007-009 | blocked | 页面保存同时要求产品和至少一个触发器，批准业务数据不足，未写入 |
| TC-REQ-007-020 | passed | 只读检查列表执行动作，显示消息推送/触发告警/取消告警等实际动作 |
| TC-REQ-007-029 | passed | 创建时间格式为 `YYYY-MM-DD HH:mm:ss`，刷新前后保持一致 |
| TC-REQ-007-033 | excluded | `auto: no`，按资格规则排除 |
| TC-REQ-007-034 | excluded | `auto: no`，按资格规则排除 |
| TC-REQ-007-035 | excluded | `auto: no`，按资格规则排除 |

## 页面探索事实

- 运行时页面路径确认：`/biopark-iot/iot/data/monitor`。
- 页面标题确认：`数据采集 - 数据监听`。
- 页面菜单路径确认：`数据中心` → `数据监听`。
- 列表确认包含规则名称、规则状态、触发条件、执行动作、创建时间、操作列；当前显示 `12` 条记录，`10条/页`，存在分页。
- 新增表单确认包含规则名称、规则状态、规则描述、监听器、触发器和执行动作配置区域。
- 新增表单提交空值时，实际错误包括 `规则名称不能为空`、产品必填和至少一个触发器；未执行保存成功路径。
- 未使用其他模块定位器，不执行真实推送、告警、跨租户访问或权限绕过。

## 证据

- RUN 白名单产物：`selection.yaml`、`results.yaml`、`case_results.xlsx`、`bug.xlsx`、`bugs_review.yaml`、`videos/`、`hashes/`、`allure-results/`
- 失败截图：保留 `TC-REQ-007-009` 探索失败截图用于诊断；最终结果按前置条件不足分类为 `blocked`，未保存该用例脚本。
- Allure CLI 未生成 `allure-report/index.html`。

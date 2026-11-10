# 746 数据推送 模块级 UI 自动化交接（REQ-008 P3）

- module_id：`746`
- 需求：`REQ-008` 数据推送
- RUN：`07_ui_automation/reports/RUN_20261110T170000Z/`
- 执行时间：2026-11-10
- 统计：`total: 9; passed: 5; blocked: 2; product_defect: 2`
- 远程 Bug：未创建
- 结构化结果：`07_ui_automation/data/REQ-008_P3_results.yaml`
- 页面对象：`07_ui_automation/pages/req008/data_push_page.py`
- 独立脚本：`07_ui_automation/tests/module_REQ-008/`

## 逐条结果

| 用例 | 结果 | 说明 |
|---|---|---|
| TC-REQ-008-002 | passed | 按名称查询，结果名称匹配“内部” |
| TC-REQ-008-003 | passed | 启用状态筛选结果均为启用 |
| TC-REQ-008-004 | passed | 停用状态筛选结果均为停用 |
| TC-REQ-008-005 | product_defect | HTTP 控件回显正确，但查询结果混入内置队列和 MQTT |
| TC-REQ-008-006 | product_defect | MQTT 控件回显正确，但查询结果混入内置队列和 HTTP |
| TC-REQ-008-008 | blocked | 日期控件契约和经批准的同日/跨日脱敏数据不足 |
| TC-REQ-008-009 | blocked | 当前目标总数不足两页，未创建未经批准的分页数据 |
| TC-REQ-008-010 | passed | 刷新前后筛选条件、页码和目标记录保持一致 |
| TC-REQ-008-015 | passed | 无匹配名称显示空结果状态且不混入旧记录 |

## 页面探索事实

- 运行时页面路径：`/biopark-iot/iot/data/sink`。
- 页面标题：`数据采集 - 数据推送`。
- 当前列表共 3 条记录，分页为 `10条/页`，因此无法验证跨页重置。
- 表头：编号、目标名称、目标描述、目标状态、目标类型、创建时间、操作。
- 状态筛选“启用”“停用”按预期过滤。
- 类型筛选下拉包含“内置队列”“HTTP”“MQTT”；选择 HTTP 或 MQTT 后控件回显正确，但结果未按类型收窄，属于产品行为缺陷。
- 日期范围控件的稳定交互契约及批准测试数据未确认，未猜测操作。
- 未执行新增、编辑、删除或真实 HTTP/MQTT/RocketMQ 外部发送。

## 缺陷与证据

- 2 条产品行为缺陷仅写入标准 `bug.xlsx`、`bugs_review.yaml` 与本交接，不自动创建远程 Bug。
- RUN 白名单产物：`selection.yaml`、`results.yaml`、`case_results.xlsx`、`bug.xlsx`、`bugs_review.yaml`、`videos/`、`hashes/`、`allure-results/`；失败构建节点按需保留 `screenshots/`。
- 未保留 `logs/`；Allure CLI 未生成 `allure-report/index.html`。

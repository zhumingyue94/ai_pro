# 731 产品分类 模块级 UI 自动化交接（REQ-002 P3）

- module_id：`731`
- 需求：`REQ-002` 产品分类
- RUN：`07_ui_automation/reports/RUN_20261110T160000Z/`
- 执行时间：2026-11-10
- 统计：`total: 15; passed: 6; blocked: 8; excluded: 1`
- 缺陷数量：`0`；远程 Bug：未创建
- 结构化结果：`07_ui_automation/data/REQ-002_P3_results.yaml`
- 页面对象：`07_ui_automation/pages/req002/product_category_page.py`
- 独立脚本：`07_ui_automation/tests/module_REQ-002/`

## 逐条结果

| 用例 | 结果 | 说明 |
|---|---|---|
| TC-REQ-002-004 | passed | 不存在名称查询返回空结果，未产生写入 |
| TC-REQ-002-011 | passed | 空名称显示必填校验，表单保持打开且未写入 |
| TC-REQ-002-012 | passed | `input[type=number]` 拒绝非数字按键，未写入 |
| TC-REQ-002-013 | passed | 取消新增后表单关闭，列表不变 |
| TC-REQ-002-015 | passed | 删除确认层取消后分类保留 |
| TC-REQ-002-021 | excluded | `auto: no`，按资格规则排除 |
| TC-REQ-002-024 | blocked | 当前分类总数不足三页，未创建未经批准的分页数据 |
| TC-REQ-002-039 | blocked | 当前分类总数不足三页，未创建未经批准的分页数据 |
| TC-REQ-002-026 | passed | 空白查询行为已记录；页面保留空格并返回全部当前列表，业务规则未确认 |
| TC-REQ-002-027 | blocked | 缺少经授权的特殊字符分类数据 |
| TC-REQ-002-028 | blocked | 缺少经授权的同名分类数据 |
| TC-REQ-002-029 | blocked | 缺少经授权的特殊描述分类数据 |
| TC-REQ-002-030 | blocked | 缺少经授权的空描述分类数据 |
| TC-REQ-002-033 | blocked | 缺少经授权的重复排序分类数据 |
| TC-REQ-002-034 | blocked | 表头设置面板缺少稳定关闭控件，已探索定位但未保存失败脚本 |

## 页面探索事实

- 运行时路径：`/biopark-iot/iot/device/product-category`。
- 页面标题：`数据采集 - 产品分类`。
- 当前租户：`测试园区A`；可见分类总数曾为 `18`，页面每页 `10` 条。
- 新增表单字段：分类名字、分类排序、分类状态、分类描述；提交按钮实际文本为 `确 定`，取消按钮为 `取 消`。
- 分类排序字段实际为 `input[type=number]`；非数字按键被浏览器控件拒绝并保持 `0`。
- 空白名称查询实际保留三个空格并返回当前列表，属于业务规则待确认行为，未判定产品缺陷。
- 表头设置面板可打开，但运行时未确认稳定关闭图标或按钮；Escape 与再次点击入口均未关闭，因此分类为 `blocked`。
- 未创建分页、特殊字符、同名、特殊描述、空描述或重复排序数据；未执行未经批准的业务写入。

## 证据

- RUN 白名单产物：`selection.yaml`、`results.yaml`、`case_results.xlsx`、`bug.xlsx`、`bugs_review.yaml`、`videos/`、`hashes/`、`allure-results/`
- 失败构建节点按需保留 `screenshots/`；未保留 `logs/`。
- Allure CLI 未生成 `allure-report/index.html`。

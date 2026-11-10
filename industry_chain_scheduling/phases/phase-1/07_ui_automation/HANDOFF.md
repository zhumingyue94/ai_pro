# UI 自动化阶段总 Handoff

> 本文件由 08 阶段自动化框架自动维护：索引表与「最近一次 RUN」为机器维护区间，
> 其余内容属于历史归档，不会被自动删除。

<!-- BEGIN:UI_RUN_INDEX -->

（尚无执行记录）

<!-- END:UI_RUN_INDEX -->

<!-- BEGIN:UI_LATEST_RUN -->

（尚无执行记录）

<!-- END:UI_LATEST_RUN -->

## 历史归档

## 历史 RUN 汇总


---

## RUN_分段养殖模版_20260825_094111


- run_id: RUN_分段养殖模版_20260825_094111
- 生成时间: 2026-08-25T09:42:06
- 模块: 分段养殖模版（模块 ID 670）
- 需求: REQ-003
- 环境: 192.168.6.163:66（headless=true）

## 范围统计

- 本地 YAML 读取用例数: 157
- 本次新增自动化映射数: 0
- 修复既有自动化映射数: 0
- 已执行用例数: 19
- excluded 用例数: 0
- 仍为 pending_registry 的用例数: 5
- blocked 用例数: 13
- 结果统计: {'failed': 3, 'passed': 2, 'ignored': 1, 'blocked': 13}

## 映射与边界

- module_case_map.json：47578, 47579, 47580, 47581, 47582, 47584, 47603, 47634, 47635, 47703, 47705, 47709, 47711, 47712, 47713, 47714, 47715, 47717, 48741 为既有 registered 映射，本轮修复 handler/Page Object/data contract；未创建第二套注册表。
- 数据：按每条用例契约使用 existing_system_data 或 self_created；自造数据使用 AUTO测试_勿用_{{run_id}} 前缀，清理状态以契约为准。
- 禅道：未访问、未写入、未同步结果或创建 Bug。

## 用例结果

| 本地用例 | 禅道编号 | 状态 | 分类 | check_id | assertion_scope |
|---|---:|---|---|---|---|
| TC-003-06 | 47578 | failed | product_defect | TP-003-06 | feeding_template.query.name_filter |
| TC-003-07 | 47579 | passed | passed | TP-003-07 | feeding_template.query.breed_filter |
| TC-003-08 | 47580 | failed | product_defect | TP-003-08 | feeding_template.query.month_filter |
| TC-003-09 | 47581 | failed | product_defect | TP-003-09 | feeding_template.query.status_filter |
| TC-003-10 | 47582 | ignored | test_script_error | TP-003-10 | feeding_template.query.combined_filter |
| TC-003-12 | 47584 | passed | passed | TP-003-12 | feeding_template.query.reset |
| TC-003-31 | 47603 | blocked | blocked | missing_check_id | missing_assertion_scope |
| TC-003-62 | 47634 | blocked | blocked | missing_check_id | missing_assertion_scope |
| TC-003-63 | 47635 | blocked | blocked | missing_check_id | missing_assertion_scope |
| TC-003-131 | 47703 | blocked | blocked | missing_check_id | missing_assertion_scope |
| TC-003-133 | 47705 | blocked | blocked | missing_check_id | missing_assertion_scope |
| TC-003-137 | 47709 | blocked | blocked | missing_check_id | missing_assertion_scope |
| TC-003-139 | 47711 | blocked | blocked | missing_check_id | missing_assertion_scope |
| TC-003-140 | 47712 | blocked | blocked | missing_check_id | missing_assertion_scope |
| TC-003-141 | 47713 | blocked | blocked | missing_check_id | missing_assertion_scope |
| TC-003-142 | 47714 | blocked | blocked | missing_check_id | missing_assertion_scope |
| TC-003-143 | 47715 | blocked | blocked | missing_check_id | missing_assertion_scope |
| TC-003-145 | 47717 | blocked | blocked | missing_check_id | missing_assertion_scope |
| TC-003-149 | 48741 | blocked | blocked | missing_check_id | missing_assertion_scope |

## 产物路径

- RUN: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_分段养殖模版_20260825_094111
- 阶段 Handoff: 07_ui_automation/HANDOFF.md
- 选择: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_分段养殖模版_20260825_094111\selection.yaml
- 结果: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_分段养殖模版_20260825_094111\results.yaml
- Excel: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_分段养殖模版_20260825_094111\case_results.xlsx
- 截图: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_分段养殖模版_20260825_094111\screenshots
- Allure: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_分段养殖模版_20260825_094111\allure-results
- Bug 审核: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_分段养殖模版_20260825_094111\bugs_review.yaml


---

## RUN_分段养殖模版_20260825_094719


- run_id: RUN_分段养殖模版_20260825_094719
- 生成时间: 2026-08-25T09:48:15
- 模块: 分段养殖模版（模块 ID 670）
- 需求: REQ-003
- 环境: 192.168.6.163:66（headless=true）

## 范围统计

- 本地 YAML 读取用例数: 157
- 本次新增自动化映射数: 0
- 修复既有自动化映射数: 0
- 已执行用例数: 19
- excluded 用例数: 0
- 仍为 pending_registry 的用例数: 5
- blocked 用例数: 13
- 结果统计: {'passed': 6, 'blocked': 13}

## 映射与边界

- module_case_map.json：47578, 47579, 47580, 47581, 47582, 47584, 47603, 47634, 47635, 47703, 47705, 47709, 47711, 47712, 47713, 47714, 47715, 47717, 48741 为既有 registered 映射，本轮修复 handler/Page Object/data contract；未创建第二套注册表。
- 数据：按每条用例契约使用 existing_system_data 或 self_created；自造数据使用 AUTO测试_勿用_{{run_id}} 前缀，清理状态以契约为准。
- 禅道：未访问、未写入、未同步结果或创建 Bug。

## 用例结果

| 本地用例 | 禅道编号 | 状态 | 分类 | check_id | assertion_scope |
|---|---:|---|---|---|---|
| TC-003-06 | 47578 | passed | passed | TP-003-06 | feeding_template.query.name_filter |
| TC-003-07 | 47579 | passed | passed | TP-003-07 | feeding_template.query.breed_filter |
| TC-003-08 | 47580 | passed | passed | TP-003-08 | feeding_template.query.month_filter |
| TC-003-09 | 47581 | passed | passed | TP-003-09 | feeding_template.query.status_filter |
| TC-003-10 | 47582 | passed | passed | TP-003-10 | feeding_template.query.combined_filter |
| TC-003-12 | 47584 | passed | passed | TP-003-12 | feeding_template.query.reset |
| TC-003-31 | 47603 | blocked | blocked | missing_check_id | missing_assertion_scope |
| TC-003-62 | 47634 | blocked | blocked | missing_check_id | missing_assertion_scope |
| TC-003-63 | 47635 | blocked | blocked | missing_check_id | missing_assertion_scope |
| TC-003-131 | 47703 | blocked | blocked | missing_check_id | missing_assertion_scope |
| TC-003-133 | 47705 | blocked | blocked | missing_check_id | missing_assertion_scope |
| TC-003-137 | 47709 | blocked | blocked | missing_check_id | missing_assertion_scope |
| TC-003-139 | 47711 | blocked | blocked | missing_check_id | missing_assertion_scope |
| TC-003-140 | 47712 | blocked | blocked | missing_check_id | missing_assertion_scope |
| TC-003-141 | 47713 | blocked | blocked | missing_check_id | missing_assertion_scope |
| TC-003-142 | 47714 | blocked | blocked | missing_check_id | missing_assertion_scope |
| TC-003-143 | 47715 | blocked | blocked | missing_check_id | missing_assertion_scope |
| TC-003-145 | 47717 | blocked | blocked | missing_check_id | missing_assertion_scope |
| TC-003-149 | 48741 | blocked | blocked | missing_check_id | missing_assertion_scope |

## 产物路径

- RUN: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_分段养殖模版_20260825_094719
- 阶段 Handoff: 07_ui_automation/HANDOFF.md
- 选择: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_分段养殖模版_20260825_094719\selection.yaml
- 结果: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_分段养殖模版_20260825_094719\results.yaml
- Excel: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_分段养殖模版_20260825_094719\case_results.xlsx
- 截图: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_分段养殖模版_20260825_094719\screenshots
- Allure: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_分段养殖模版_20260825_094719\allure-results
- Bug 审核: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_分段养殖模版_20260825_094719\bugs_review.yaml


---

## RUN_分段养殖模版_20260825_100059


- run_id: RUN_分段养殖模版_20260825_100059
- 生成时间: 2026-08-25T10:06:33
- 模块: 分段养殖模版（模块 ID 670）
- 需求: REQ-003
- 环境: 192.168.6.163:66（headless=true）

## 范围统计

- 本地 YAML 读取用例数: 157
- 本次新增自动化映射数: 0
- 修复既有自动化映射数: 0
- 已执行用例数: 19
- excluded 用例数: 0
- 仍为 pending_registry 的用例数: 5
- blocked 用例数: 11
- 结果统计: {'passed': 7, 'ignored': 1, 'blocked': 11}

## 映射与边界

- module_case_map.json：47578, 47579, 47580, 47581, 47582, 47584, 47603, 47634, 47635, 47703, 47705, 47709, 47711, 47712, 47713, 47714, 47715, 47717, 48741 为既有 registered 映射，本轮修复 handler/Page Object/data contract；未创建第二套注册表。
- 数据：按每条用例契约使用 existing_system_data 或 self_created；自造数据使用 AUTO测试_勿用_{{run_id}} 前缀，清理状态以契约为准。
- 禅道：未访问、未写入、未同步结果或创建 Bug。

## 用例结果

| 本地用例 | 禅道编号 | 状态 | 分类 | check_id | assertion_scope |
|---|---:|---|---|---|---|
| TC-003-06 | 47578 | passed | passed | TP-003-06 | feeding_template.query.name_filter |
| TC-003-07 | 47579 | passed | passed | TP-003-07 | feeding_template.query.breed_filter |
| TC-003-08 | 47580 | passed | passed | TP-003-08 | feeding_template.query.month_filter |
| TC-003-09 | 47581 | passed | passed | TP-003-09 | feeding_template.query.status_filter |
| TC-003-10 | 47582 | ignored | test_script_error | TP-003-10 | feeding_template.query.combined_filter |
| TC-003-12 | 47584 | passed | passed | TP-003-12 | feeding_template.query.reset |
| TC-003-31 | 47603 | passed | passed | TP-003-31 | feeding_template.new.auto_calc |
| TC-003-62 | 47634 | blocked | blocked | TP-003-62 | feeding_template.new.save_draft |
| TC-003-63 | 47635 | blocked | blocked | TP-003-63 | feeding_template.new.save_and_submit |
| TC-003-131 | 47703 | blocked | blocked | TP-003-131 | feeding_template.submit.confirm_box |
| TC-003-133 | 47705 | blocked | blocked | TP-003-133 | feeding_template.submit.status_change |
| TC-003-137 | 47709 | blocked | blocked | TP-003-137 | feeding_template.review.reject_reason |
| TC-003-139 | 47711 | blocked | blocked | TP-003-139 | feeding_template.review.reject_status |
| TC-003-140 | 47712 | blocked | blocked | TP-003-140 | feeding_template.review.approve_action |
| TC-003-141 | 47713 | blocked | blocked | TP-003-141 | feeding_template.review.approve_confirm_box |
| TC-003-142 | 47714 | blocked | blocked | TP-003-142 | feeding_template.review.approve_status |
| TC-003-143 | 47715 | blocked | blocked | TP-003-143 | feeding_template.delete.confirm_box |
| TC-003-145 | 47717 | blocked | blocked | TP-003-145 | feeding_template.delete.removed_from_list |
| TC-003-149 | 48741 | passed | passed | TP-003-149 | feeding_template.copy.confirm_box |

## 产物路径

- RUN: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_分段养殖模版_20260825_100059
- 阶段 Handoff: 07_ui_automation/HANDOFF.md
- 选择: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_分段养殖模版_20260825_100059\selection.yaml
- 结果: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_分段养殖模版_20260825_100059\results.yaml
- Excel: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_分段养殖模版_20260825_100059\case_results.xlsx
- 截图: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_分段养殖模版_20260825_100059\screenshots
- Allure: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_分段养殖模版_20260825_100059\allure-results
- Bug 审核: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_分段养殖模版_20260825_100059\bugs_review.yaml


---

## RUN_分段养殖模版_20260825_100811


- run_id: RUN_分段养殖模版_20260825_100811
- 生成时间: 2026-08-25T10:14:28
- 模块: 分段养殖模版（模块 ID 670）
- 需求: REQ-003
- 环境: 192.168.6.163:66（headless=true）

## 范围统计

- 本地 YAML 读取用例数: 157
- 本次新增自动化映射数: 0
- 修复既有自动化映射数: 0
- 已执行用例数: 19
- excluded 用例数: 0
- 仍为 pending_registry 的用例数: 5
- blocked 用例数: 0
- 结果统计: {'passed': 7, 'ignored': 12}

## 映射与边界

- module_case_map.json：47578, 47579, 47580, 47581, 47582, 47584, 47603, 47634, 47635, 47703, 47705, 47709, 47711, 47712, 47713, 47714, 47715, 47717, 48741 为既有 registered 映射，本轮修复 handler/Page Object/data contract；未创建第二套注册表。
- 数据：按每条用例契约使用 existing_system_data 或 self_created；自造数据使用 AUTO测试_勿用_{{run_id}} 前缀，清理状态以契约为准。
- 禅道：未访问、未写入、未同步结果或创建 Bug。

## 用例结果

| 本地用例 | 禅道编号 | 状态 | 分类 | check_id | assertion_scope |
|---|---:|---|---|---|---|
| TC-003-06 | 47578 | passed | passed | TP-003-06 | feeding_template.query.name_filter |
| TC-003-07 | 47579 | passed | passed | TP-003-07 | feeding_template.query.breed_filter |
| TC-003-08 | 47580 | passed | passed | TP-003-08 | feeding_template.query.month_filter |
| TC-003-09 | 47581 | passed | passed | TP-003-09 | feeding_template.query.status_filter |
| TC-003-10 | 47582 | passed | passed | TP-003-10 | feeding_template.query.combined_filter |
| TC-003-12 | 47584 | passed | passed | TP-003-12 | feeding_template.query.reset |
| TC-003-31 | 47603 | ignored | test_script_error | TP-003-31 | feeding_template.new.auto_calc |
| TC-003-62 | 47634 | ignored | test_script_error | TP-003-62 | feeding_template.new.save_draft |
| TC-003-63 | 47635 | ignored | test_script_error | TP-003-63 | feeding_template.new.save_and_submit |
| TC-003-131 | 47703 | ignored | test_script_error | TP-003-131 | feeding_template.submit.confirm_box |
| TC-003-133 | 47705 | ignored | test_script_error | TP-003-133 | feeding_template.submit.status_change |
| TC-003-137 | 47709 | ignored | test_script_error | TP-003-137 | feeding_template.review.reject_reason |
| TC-003-139 | 47711 | ignored | test_script_error | TP-003-139 | feeding_template.review.reject_status |
| TC-003-140 | 47712 | ignored | test_script_error | TP-003-140 | feeding_template.review.approve_action |
| TC-003-141 | 47713 | ignored | test_script_error | TP-003-141 | feeding_template.review.approve_confirm_box |
| TC-003-142 | 47714 | ignored | test_script_error | TP-003-142 | feeding_template.review.approve_status |
| TC-003-143 | 47715 | ignored | test_script_error | TP-003-143 | feeding_template.delete.confirm_box |
| TC-003-145 | 47717 | ignored | test_script_error | TP-003-145 | feeding_template.delete.removed_from_list |
| TC-003-149 | 48741 | passed | passed | TP-003-149 | feeding_template.copy.confirm_box |

## 产物路径

- RUN: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_分段养殖模版_20260825_100811
- 阶段 Handoff: 07_ui_automation/HANDOFF.md
- 选择: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_分段养殖模版_20260825_100811\selection.yaml
- 结果: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_分段养殖模版_20260825_100811\results.yaml
- Excel: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_分段养殖模版_20260825_100811\case_results.xlsx
- 截图: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_分段养殖模版_20260825_100811\screenshots
- Allure: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_分段养殖模版_20260825_100811\allure-results
- Bug 审核: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_分段养殖模版_20260825_100811\bugs_review.yaml


---

## RUN_分段养殖模版_20260825_112953


- run_id: RUN_分段养殖模版_20260825_112953
- 生成时间: 2026-08-25T11:36:05
- 模块: 分段养殖模版（模块 ID 670）
- 需求: REQ-003
- 环境: 192.168.6.163:66（headless=true）

## 范围统计

- 本地 YAML 读取用例数: 157
- 本次新增自动化映射数: 0
- 修复既有自动化映射数: 0
- 已执行用例数: 19
- excluded 用例数: 0
- 仍为 pending_registry 的用例数: 5
- blocked 用例数: 11
- 结果统计: {'passed': 8, 'blocked': 11}

## 映射与边界

- module_case_map.json：47578, 47579, 47580, 47581, 47582, 47584, 47603, 47634, 47635, 47703, 47705, 47709, 47711, 47712, 47713, 47714, 47715, 47717, 48741 为既有 registered 映射，本轮修复 handler/Page Object/data contract；未创建第二套注册表。
- 数据：按每条用例契约使用 existing_system_data 或 self_created；自造数据使用 AUTO测试_勿用_{{run_id}} 前缀，清理状态以契约为准。
- 禅道：未访问、未写入、未同步结果或创建 Bug。

## 用例结果

| 本地用例 | 禅道编号 | 状态 | 分类 | check_id | assertion_scope |
|---|---:|---|---|---|---|
| TC-003-06 | 47578 | passed | passed | TP-003-06 | feeding_template.query.name_filter |
| TC-003-07 | 47579 | passed | passed | TP-003-07 | feeding_template.query.breed_filter |
| TC-003-08 | 47580 | passed | passed | TP-003-08 | feeding_template.query.month_filter |
| TC-003-09 | 47581 | passed | passed | TP-003-09 | feeding_template.query.status_filter |
| TC-003-10 | 47582 | passed | passed | TP-003-10 | feeding_template.query.combined_filter |
| TC-003-12 | 47584 | passed | passed | TP-003-12 | feeding_template.query.reset |
| TC-003-31 | 47603 | passed | passed | TP-003-31 | feeding_template.new.auto_calc |
| TC-003-62 | 47634 | blocked | blocked | TP-003-62 | feeding_template.new.save_draft |
| TC-003-63 | 47635 | blocked | blocked | TP-003-63 | feeding_template.new.save_and_submit |
| TC-003-131 | 47703 | blocked | blocked | TP-003-131 | feeding_template.submit.confirm_box |
| TC-003-133 | 47705 | blocked | blocked | TP-003-133 | feeding_template.submit.status_change |
| TC-003-137 | 47709 | blocked | blocked | TP-003-137 | feeding_template.review.reject_reason |
| TC-003-139 | 47711 | blocked | blocked | TP-003-139 | feeding_template.review.reject_status |
| TC-003-140 | 47712 | blocked | blocked | TP-003-140 | feeding_template.review.approve_action |
| TC-003-141 | 47713 | blocked | blocked | TP-003-141 | feeding_template.review.approve_confirm_box |
| TC-003-142 | 47714 | blocked | blocked | TP-003-142 | feeding_template.review.approve_status |
| TC-003-143 | 47715 | blocked | blocked | TP-003-143 | feeding_template.delete.confirm_box |
| TC-003-145 | 47717 | blocked | blocked | TP-003-145 | feeding_template.delete.removed_from_list |
| TC-003-149 | 48741 | passed | passed | TP-003-149 | feeding_template.copy.confirm_box |

## 产物路径

- RUN: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_分段养殖模版_20260825_112953
- 阶段 Handoff: 07_ui_automation/HANDOFF.md
- 选择: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_分段养殖模版_20260825_112953\selection.yaml
- 结果: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_分段养殖模版_20260825_112953\results.yaml
- Excel: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_分段养殖模版_20260825_112953\case_results.xlsx
- 截图: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_分段养殖模版_20260825_112953\screenshots
- Allure: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_分段养殖模版_20260825_112953\allure-results
- Bug 审核: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_分段养殖模版_20260825_112953\bugs_review.yaml


---

## RUN_制定排程_20260825_163225


- run_id: RUN_制定排程_20260825_163225
- 生成时间: 2026-08-25T17:02:06
- 模块: 制定排程（模块 ID 671）
- 需求: REQ-004
- 环境: 192.168.6.163:66（headless=true）

## 范围统计

- 本地 YAML 读取用例数: 232
- 本次新增自动化映射数: 0
- 修复既有自动化映射数: 0
- 已执行用例数: 19
- excluded 用例数: 0
- 仍为 pending_registry 的用例数: 5
- blocked 用例数: 2
- 结果统计: {'passed': 15, 'failed': 2, 'blocked': 2}

## 映射与边界

- module_case_map.json：47721, 47722, 47723, 47724, 47726, 47768, 47772, 47774, 47786, 47794, 47798, 47861, 47865, 47867, 47877, 47879, 48827, 48861, 48864 为既有 registered 映射，本轮修复 handler/Page Object/data contract；未创建第二套注册表。
- 数据：按每条用例契约使用 existing_system_data 或 self_created；自造数据使用 AUTO测试_勿用_{{run_id}} 前缀，清理状态以契约为准。
- 禅道：未访问、未写入、未同步结果或创建 Bug。

## 用例结果

| 本地用例 | 禅道编号 | 状态 | 分类 | check_id | assertion_scope |
|---|---:|---|---|---|---|
| TC-004-04 | 47721 | passed | passed | TP-004-04 | make_plan.query.month_filter |
| TC-004-05 | 47722 | passed | passed | TP-004-05 | make_plan.query.status_filter |
| TC-004-06 | 47723 | failed | product_defect | TP-004-06 | make_plan.query.line_filter |
| TC-004-07 | 47724 | failed | product_defect | TP-004-07 | make_plan.query.combined_filter |
| TC-004-09 | 47726 | passed | passed | TP-004-09 | make_plan.query.reset |
| TC-004-51 | 47768 | passed | passed | TP-004-51 | make_plan.create.template_autofill |
| TC-004-55 | 47772 | passed | passed | TP-004-55 | make_plan.create.restock_amount_calc |
| TC-004-57 | 47774 | passed | passed | TP-004-57 | make_plan.create.restock_date_calc |
| TC-004-69 | 47786 | passed | passed | TP-004-69 | make_plan.create.hatch_amount_calc |
| TC-004-77 | 47794 | passed | passed | TP-004-77 | make_plan.create.plan_code_format |
| TC-004-81 | 47798 | passed | passed | TP-004-81 | make_plan.create.save_draft_status |
| TC-004-144 | 47861 | passed | passed | TP-004-144 | make_plan.edit.save_and_submit_status |
| TC-004-148 | 47865 | passed | passed | TP-004-148 | make_plan.submit_month.confirm_dialog |
| TC-004-150 | 47867 | blocked | blocked | TP-004-150 | make_plan.submit_month.status_pending_review |
| TC-004-160 | 47877 | passed | passed | TP-004-160 | make_plan.delete.confirm_box |
| TC-004-162 | 47879 | passed | passed | TP-004-162 | make_plan.delete.removed_from_list |
| TC-004-175 | 48827 | passed | passed | TP-004-175 | make_plan.recommend.house_backfill |
| TC-004-176 | 48861 | passed | passed | TP-004-176 | make_plan.recommend.score_order_first |
| TC-004-223 | 48864 | blocked | blocked | TP-004-223 | make_plan.recommend.score_min_idle_first |

## 产物路径

- RUN: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_制定排程_20260825_163225
- 阶段 Handoff: 07_ui_automation/HANDOFF.md
- 选择: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_制定排程_20260825_163225\selection.yaml
- 结果: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_制定排程_20260825_163225\results.yaml
- Excel: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_制定排程_20260825_163225\case_results.xlsx
- 截图: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_制定排程_20260825_163225\screenshots
- Allure: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_制定排程_20260825_163225\allure-results
- Bug 审核: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_制定排程_20260825_163225\bugs_review.yaml


---

## RUN_目标制定_20260820_131108


- run_id: RUN_目标制定_20260820_131108
- 生成时间: 2026-08-20T13:11:17
- 模块: 目标制定（模块 ID 669）
- 需求: REQ-002
- 环境: 192.168.6.163:66（headless=false）

## 范围统计

- 本地 YAML 读取用例数: 91
- 本次新增自动化映射数: 0
- 修复既有自动化映射数: 1
- 已执行用例数: 1
- 仍为 pending_registry 的用例数: 5
- blocked 用例数: 0
- 结果统计: {'passed': 1}

## 映射与边界

- module_case_map.json：47482 为既有 registered 映射，本轮修复 handler/Page Object/data contract；未创建第二套注册表。
- 数据：只读 existing_system_data，creates_data=false，cleanup_status=not_required。
- 禅道：未访问、未写入、未同步结果或创建 Bug。

## 用例结果

| 本地用例 | 禅道编号 | 状态 | 分类 | check_id | assertion_scope |
|---|---:|---|---|---|---|
| TC-002-01 | 47482 | passed | passed | TP-002-01 | target_goal.query_form |

## 产物路径

- RUN: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_目标制定_20260820_131108
- 阶段 Handoff: 07_ui_automation/HANDOFF.md
- 选择: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_目标制定_20260820_131108\selection.yaml
- 结果: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_目标制定_20260820_131108\results.yaml
- Excel: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_目标制定_20260820_131108\case_results.xlsx
- 截图: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_目标制定_20260820_131108\screenshots
- Allure: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_目标制定_20260820_131108\allure-results
- Bug 审核: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_目标制定_20260820_131108\bugs_review.yaml


---

## RUN_目标制定_20260820_134449


- run_id: RUN_目标制定_20260820_134449
- 生成时间: 2026-08-20T13:45:02
- 模块: 目标制定（模块 ID 669）
- 需求: REQ-002
- 环境: 192.168.6.163:66（headless=false）

## 范围统计

- 本地 YAML 读取用例数: 91
- 本次新增自动化映射数: 0
- 修复既有自动化映射数: 1
- 已执行用例数: 1
- 仍为 pending_registry 的用例数: 5
- blocked 用例数: 1
- 结果统计: {'blocked': 1}

## 映射与边界

- module_case_map.json：47485 为既有 registered 映射，本轮修复 handler/Page Object/data contract；未创建第二套注册表。
- 数据：只读 existing_system_data，creates_data=false，cleanup_status=not_required。
- 禅道：未访问、未写入、未同步结果或创建 Bug。

## 用例结果

| 本地用例 | 禅道编号 | 状态 | 分类 | check_id | assertion_scope |
|---|---:|---|---|---|---|
| TC-002-04 | 47485 | blocked | blocked | TP-002-04 | target_goal.query_filters.year_results |

## 产物路径

- RUN: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_目标制定_20260820_134449
- 阶段 Handoff: 07_ui_automation/HANDOFF.md
- 选择: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_目标制定_20260820_134449\selection.yaml
- 结果: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_目标制定_20260820_134449\results.yaml
- Excel: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_目标制定_20260820_134449\case_results.xlsx
- 截图: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_目标制定_20260820_134449\screenshots
- Allure: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_目标制定_20260820_134449\allure-results
- Bug 审核: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_目标制定_20260820_134449\bugs_review.yaml


---

## RUN_目标制定_20260820_134639


- run_id: RUN_目标制定_20260820_134639
- 生成时间: 2026-08-20T13:46:50
- 模块: 目标制定（模块 ID 669）
- 需求: REQ-002
- 环境: 192.168.6.163:66（headless=false）

## 范围统计

- 本地 YAML 读取用例数: 91
- 本次新增自动化映射数: 0
- 修复既有自动化映射数: 1
- 已执行用例数: 1
- 仍为 pending_registry 的用例数: 5
- blocked 用例数: 1
- 结果统计: {'blocked': 1}

## 映射与边界

- module_case_map.json：47485 为既有 registered 映射，本轮修复 handler/Page Object/data contract；未创建第二套注册表。
- 数据：只读 existing_system_data，creates_data=false，cleanup_status=not_required。
- 禅道：未访问、未写入、未同步结果或创建 Bug。

## 用例结果

| 本地用例 | 禅道编号 | 状态 | 分类 | check_id | assertion_scope |
|---|---:|---|---|---|---|
| TC-002-04 | 47485 | blocked | blocked | TP-002-04 | target_goal.query_filters.year_results |

## 产物路径

- RUN: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_目标制定_20260820_134639
- 阶段 Handoff: 07_ui_automation/HANDOFF.md
- 选择: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_目标制定_20260820_134639\selection.yaml
- 结果: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_目标制定_20260820_134639\results.yaml
- Excel: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_目标制定_20260820_134639\case_results.xlsx
- 截图: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_目标制定_20260820_134639\screenshots
- Allure: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_目标制定_20260820_134639\allure-results
- Bug 审核: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_目标制定_20260820_134639\bugs_review.yaml


---

## RUN_目标制定_20260820_134813


- run_id: RUN_目标制定_20260820_134813
- 生成时间: 2026-08-20T13:48:24
- 模块: 目标制定（模块 ID 669）
- 需求: REQ-002
- 环境: 192.168.6.163:66（headless=false）

## 范围统计

- 本地 YAML 读取用例数: 91
- 本次新增自动化映射数: 0
- 修复既有自动化映射数: 1
- 已执行用例数: 1
- 仍为 pending_registry 的用例数: 5
- blocked 用例数: 0
- 结果统计: {'passed': 1}

## 映射与边界

- module_case_map.json：47485 为既有 registered 映射，本轮修复 handler/Page Object/data contract；未创建第二套注册表。
- 数据：只读 existing_system_data，creates_data=false，cleanup_status=not_required。
- 禅道：未访问、未写入、未同步结果或创建 Bug。

## 用例结果

| 本地用例 | 禅道编号 | 状态 | 分类 | check_id | assertion_scope |
|---|---:|---|---|---|---|
| TC-002-04 | 47485 | passed | passed | TP-002-04 | target_goal.query_filters.year_results |

## 产物路径

- RUN: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_目标制定_20260820_134813
- 阶段 Handoff: 07_ui_automation/HANDOFF.md
- 选择: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_目标制定_20260820_134813\selection.yaml
- 结果: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_目标制定_20260820_134813\results.yaml
- Excel: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_目标制定_20260820_134813\case_results.xlsx
- 截图: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_目标制定_20260820_134813\screenshots
- Allure: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_目标制定_20260820_134813\allure-results
- Bug 审核: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_目标制定_20260820_134813\bugs_review.yaml


---

## RUN_目标制定_20260820_143743


- run_id: RUN_目标制定_20260820_143743
- 生成时间: 2026-08-20T14:41:53
- 模块: 目标制定（模块 ID 669）
- 需求: REQ-002
- 环境: 192.168.6.163:66（headless=false）

## 范围统计

- 本地 YAML 读取用例数: 91
- 本次新增自动化映射数: 0
- 修复既有自动化映射数: 14
- 已执行用例数: 15
- excluded 用例数: 0
- 仍为 pending_registry 的用例数: 5
- blocked 用例数: 9
- 结果统计: {'passed': 6, 'blocked': 9}

## 映射与边界

- module_case_map.json：47485, 47486, 47487, 47489, 47501, 47508, 47509, 47556, 47558, 47565, 47566, 47567, 47568, 47569, 47571 为既有 registered 映射，本轮修复 handler/Page Object/data contract；未创建第二套注册表。
- 数据：按每条用例契约使用 existing_system_data 或 self_created；自造数据使用 AUTO测试_勿用_{{run_id}} 前缀，清理状态以契约为准。
- 禅道：未访问、未写入、未同步结果或创建 Bug。

## 用例结果

| 本地用例 | 禅道编号 | 状态 | 分类 | check_id | assertion_scope |
|---|---:|---|---|---|---|
| TC-002-04 | 47485 | passed | passed | TP-002-04 | target_goal.query_filters.year_results |
| TC-002-05 | 47486 | passed | passed | TP-002-05 | target_goal.query_filters.status_results |
| TC-002-06 | 47487 | passed | passed | TP-002-06 | target_goal.query_filters.combined_results |
| TC-002-08 | 47489 | passed | passed | TP-002-08 | target_goal.query_filters.reset_state |
| TC-002-20 | 47501 | blocked | blocked | TP-002-20 | target_goal.goal_form.monthly_distribution |
| TC-002-27 | 47508 | blocked | blocked | TP-002-27 | target_goal.goal_table.draft_status |
| TC-002-28 | 47509 | blocked | blocked | TP-002-28 | target_goal.goal_table.pending_review_status |
| TC-002-75 | 47556 | blocked | blocked | TP-002-75 | target_goal.submit_confirmation |
| TC-002-77 | 47558 | passed | passed | TP-002-77 | target_goal.goal_table.pending_review_status |
| TC-002-84 | 47565 | blocked | blocked | TP-002-84 | target_goal.reject_flow.rejected_status |
| TC-002-85 | 47566 | blocked | blocked | TP-002-85 | target_goal.reject_flow.reason_required |
| TC-002-86 | 47567 | blocked | blocked | TP-002-86 | target_goal.review_flow.approved_status |
| TC-002-87 | 47568 | blocked | blocked | TP-002-87 | target_goal.review_flow.audit_metadata |
| TC-002-88 | 47569 | passed | passed | TP-002-88 | target_goal.delete_confirmation |
| TC-002-90 | 47571 | blocked | blocked | TP-002-90 | target_goal.delete_flow.removed_row |

## 产物路径

- RUN: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_目标制定_20260820_143743
- 阶段 Handoff: 07_ui_automation/HANDOFF.md
- 选择: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_目标制定_20260820_143743\selection.yaml
- 结果: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_目标制定_20260820_143743\results.yaml
- Excel: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_目标制定_20260820_143743\case_results.xlsx
- 截图: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_目标制定_20260820_143743\screenshots
- Allure: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_目标制定_20260820_143743\allure-results
- Bug 审核: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_目标制定_20260820_143743\bugs_review.yaml


---

## RUN_目标制定_20260820_152912


- run_id: RUN_目标制定_20260820_152912
- 生成时间: 2026-08-20T15:29:25
- 模块: 目标制定（模块 ID 669）
- 需求: REQ-002
- 环境: 192.168.6.163:66（headless=false）

## 范围统计

- 本地 YAML 读取用例数: 91
- 本次新增自动化映射数: 0
- 修复既有自动化映射数: 1
- 已执行用例数: 1
- excluded 用例数: 0
- 仍为 pending_registry 的用例数: 5
- blocked 用例数: 0
- 结果统计: {'passed': 1}

## 映射与边界

- module_case_map.json：47508 为既有 registered 映射，本轮修复 handler/Page Object/data contract；未创建第二套注册表。
- 数据：按每条用例契约使用 existing_system_data 或 self_created；自造数据使用 AUTO测试_勿用_{{run_id}} 前缀，清理状态以契约为准。
- 禅道：未访问、未写入、未同步结果或创建 Bug。

## 用例结果

| 本地用例 | 禅道编号 | 状态 | 分类 | check_id | assertion_scope |
|---|---:|---|---|---|---|
| TC-002-27 | 47508 | passed | passed | TP-002-27 | target_goal.goal_table.draft_status |

## 产物路径

- RUN: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_目标制定_20260820_152912
- 阶段 Handoff: 07_ui_automation/HANDOFF.md
- 选择: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_目标制定_20260820_152912\selection.yaml
- 结果: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_目标制定_20260820_152912\results.yaml
- Excel: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_目标制定_20260820_152912\case_results.xlsx
- 截图: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_目标制定_20260820_152912\screenshots
- Allure: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_目标制定_20260820_152912\allure-results
- Bug 审核: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_目标制定_20260820_152912\bugs_review.yaml


---

## RUN_目标制定_20260820_152942


- run_id: RUN_目标制定_20260820_152942
- 生成时间: 2026-08-20T15:29:52
- 模块: 目标制定（模块 ID 669）
- 需求: REQ-002
- 环境: 192.168.6.163:66（headless=false）

## 范围统计

- 本地 YAML 读取用例数: 91
- 本次新增自动化映射数: 0
- 修复既有自动化映射数: 1
- 已执行用例数: 1
- excluded 用例数: 0
- 仍为 pending_registry 的用例数: 5
- blocked 用例数: 1
- 结果统计: {'blocked': 1}

## 映射与边界

- module_case_map.json：47508 为既有 registered 映射，本轮修复 handler/Page Object/data contract；未创建第二套注册表。
- 数据：按每条用例契约使用 existing_system_data 或 self_created；自造数据使用 AUTO测试_勿用_{{run_id}} 前缀，清理状态以契约为准。
- 禅道：未访问、未写入、未同步结果或创建 Bug。

## 用例结果

| 本地用例 | 禅道编号 | 状态 | 分类 | check_id | assertion_scope |
|---|---:|---|---|---|---|
| TC-002-27 | 47508 | blocked | blocked | TP-002-27 | target_goal.goal_table.draft_status |

## 产物路径

- RUN: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_目标制定_20260820_152942
- 阶段 Handoff: 07_ui_automation/HANDOFF.md
- 选择: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_目标制定_20260820_152942\selection.yaml
- 结果: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_目标制定_20260820_152942\results.yaml
- Excel: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_目标制定_20260820_152942\case_results.xlsx
- 截图: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_目标制定_20260820_152942\screenshots
- Allure: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_目标制定_20260820_152942\allure-results
- Bug 审核: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_目标制定_20260820_152942\bugs_review.yaml


---

## RUN_目标制定_20260820_153005


- run_id: RUN_目标制定_20260820_153005
- 生成时间: 2026-08-20T15:30:14
- 模块: 目标制定（模块 ID 669）
- 需求: REQ-002
- 环境: 192.168.6.163:66（headless=false）

## 范围统计

- 本地 YAML 读取用例数: 91
- 本次新增自动化映射数: 0
- 修复既有自动化映射数: 1
- 已执行用例数: 1
- excluded 用例数: 0
- 仍为 pending_registry 的用例数: 5
- blocked 用例数: 1
- 结果统计: {'blocked': 1}

## 映射与边界

- module_case_map.json：47508 为既有 registered 映射，本轮修复 handler/Page Object/data contract；未创建第二套注册表。
- 数据：按每条用例契约使用 existing_system_data 或 self_created；自造数据使用 AUTO测试_勿用_{{run_id}} 前缀，清理状态以契约为准。
- 禅道：未访问、未写入、未同步结果或创建 Bug。

## 用例结果

| 本地用例 | 禅道编号 | 状态 | 分类 | check_id | assertion_scope |
|---|---:|---|---|---|---|
| TC-002-27 | 47508 | blocked | blocked | TP-002-27 | target_goal.goal_table.draft_status |

## 产物路径

- RUN: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_目标制定_20260820_153005
- 阶段 Handoff: 07_ui_automation/HANDOFF.md
- 选择: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_目标制定_20260820_153005\selection.yaml
- 结果: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_目标制定_20260820_153005\results.yaml
- Excel: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_目标制定_20260820_153005\case_results.xlsx
- 截图: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_目标制定_20260820_153005\screenshots
- Allure: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_目标制定_20260820_153005\allure-results
- Bug 审核: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_目标制定_20260820_153005\bugs_review.yaml


---

## RUN_目标制定_20260820_153409


- run_id: RUN_目标制定_20260820_153409
- 生成时间: 2026-08-20T15:34:24
- 模块: 目标制定（模块 ID 669）
- 需求: REQ-002
- 环境: 192.168.6.163:66（headless=false）

## 范围统计

- 本地 YAML 读取用例数: 91
- 本次新增自动化映射数: 0
- 修复既有自动化映射数: 1
- 已执行用例数: 1
- excluded 用例数: 0
- 仍为 pending_registry 的用例数: 5
- blocked 用例数: 0
- 结果统计: {'passed': 1}

## 映射与边界

- module_case_map.json：47508 为既有 registered 映射，本轮修复 handler/Page Object/data contract；未创建第二套注册表。
- 数据：按每条用例契约使用 existing_system_data 或 self_created；自造数据使用 AUTO测试_勿用_{{run_id}} 前缀，清理状态以契约为准。
- 禅道：未访问、未写入、未同步结果或创建 Bug。

## 用例结果

| 本地用例 | 禅道编号 | 状态 | 分类 | check_id | assertion_scope |
|---|---:|---|---|---|---|
| TC-002-27 | 47508 | passed | passed | TP-002-27 | target_goal.goal_table.draft_status |

## 产物路径

- RUN: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_目标制定_20260820_153409
- 阶段 Handoff: 07_ui_automation/HANDOFF.md
- 选择: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_目标制定_20260820_153409\selection.yaml
- 结果: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_目标制定_20260820_153409\results.yaml
- Excel: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_目标制定_20260820_153409\case_results.xlsx
- 截图: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_目标制定_20260820_153409\screenshots
- Allure: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_目标制定_20260820_153409\allure-results
- Bug 审核: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_目标制定_20260820_153409\bugs_review.yaml


---

## RUN_目标制定_20260820_153436


- run_id: RUN_目标制定_20260820_153436
- 生成时间: 2026-08-20T15:34:49
- 模块: 目标制定（模块 ID 669）
- 需求: REQ-002
- 环境: 192.168.6.163:66（headless=false）

## 范围统计

- 本地 YAML 读取用例数: 91
- 本次新增自动化映射数: 0
- 修复既有自动化映射数: 1
- 已执行用例数: 1
- excluded 用例数: 0
- 仍为 pending_registry 的用例数: 5
- blocked 用例数: 1
- 结果统计: {'blocked': 1}

## 映射与边界

- module_case_map.json：47508 为既有 registered 映射，本轮修复 handler/Page Object/data contract；未创建第二套注册表。
- 数据：按每条用例契约使用 existing_system_data 或 self_created；自造数据使用 AUTO测试_勿用_{{run_id}} 前缀，清理状态以契约为准。
- 禅道：未访问、未写入、未同步结果或创建 Bug。

## 用例结果

| 本地用例 | 禅道编号 | 状态 | 分类 | check_id | assertion_scope |
|---|---:|---|---|---|---|
| TC-002-27 | 47508 | blocked | blocked | TP-002-27 | target_goal.goal_table.draft_status |

## 产物路径

- RUN: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_目标制定_20260820_153436
- 阶段 Handoff: 07_ui_automation/HANDOFF.md
- 选择: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_目标制定_20260820_153436\selection.yaml
- 结果: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_目标制定_20260820_153436\results.yaml
- Excel: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_目标制定_20260820_153436\case_results.xlsx
- 截图: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_目标制定_20260820_153436\screenshots
- Allure: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_目标制定_20260820_153436\allure-results
- Bug 审核: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_目标制定_20260820_153436\bugs_review.yaml


---

## RUN_目标制定_20260820_160411


- run_id: RUN_目标制定_20260820_160411
- 生成时间: 2026-08-20T16:04:24
- 模块: 目标制定（模块 ID 669）
- 需求: REQ-002
- 环境: 192.168.6.163:66（headless=false）

## 范围统计

- 本地 YAML 读取用例数: 91
- 本次新增自动化映射数: 0
- 修复既有自动化映射数: 1
- 已执行用例数: 1
- excluded 用例数: 0
- 仍为 pending_registry 的用例数: 5
- blocked 用例数: 0
- 结果统计: {'passed': 1}

## 映射与边界

- module_case_map.json：47508 为既有 registered 映射，本轮修复 handler/Page Object/data contract；未创建第二套注册表。
- 数据：按每条用例契约使用 existing_system_data 或 self_created；自造数据使用 AUTO测试_勿用_{{run_id}} 前缀，清理状态以契约为准。
- 禅道：未访问、未写入、未同步结果或创建 Bug。

## 用例结果

| 本地用例 | 禅道编号 | 状态 | 分类 | check_id | assertion_scope |
|---|---:|---|---|---|---|
| TC-002-27 | 47508 | passed | passed | TP-002-27 | target_goal.goal_table.draft_status |

## 产物路径

- RUN: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_目标制定_20260820_160411
- 阶段 Handoff: 07_ui_automation/HANDOFF.md
- 选择: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_目标制定_20260820_160411\selection.yaml
- 结果: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_目标制定_20260820_160411\results.yaml
- Excel: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_目标制定_20260820_160411\case_results.xlsx
- 截图: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_目标制定_20260820_160411\screenshots
- Allure: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_目标制定_20260820_160411\allure-results
- Bug 审核: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_目标制定_20260820_160411\bugs_review.yaml


---

## RUN_目标制定_20260820_160439


- run_id: RUN_目标制定_20260820_160439
- 生成时间: 2026-08-20T16:04:52
- 模块: 目标制定（模块 ID 669）
- 需求: REQ-002
- 环境: 192.168.6.163:66（headless=false）

## 范围统计

- 本地 YAML 读取用例数: 91
- 本次新增自动化映射数: 0
- 修复既有自动化映射数: 1
- 已执行用例数: 1
- excluded 用例数: 0
- 仍为 pending_registry 的用例数: 5
- blocked 用例数: 0
- 结果统计: {'passed': 1}

## 映射与边界

- module_case_map.json：47508 为既有 registered 映射，本轮修复 handler/Page Object/data contract；未创建第二套注册表。
- 数据：按每条用例契约使用 existing_system_data 或 self_created；自造数据使用 AUTO测试_勿用_{{run_id}} 前缀，清理状态以契约为准。
- 禅道：未访问、未写入、未同步结果或创建 Bug。

## 用例结果

| 本地用例 | 禅道编号 | 状态 | 分类 | check_id | assertion_scope |
|---|---:|---|---|---|---|
| TC-002-27 | 47508 | passed | passed | TP-002-27 | target_goal.goal_table.draft_status |

## 产物路径

- RUN: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_目标制定_20260820_160439
- 阶段 Handoff: 07_ui_automation/HANDOFF.md
- 选择: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_目标制定_20260820_160439\selection.yaml
- 结果: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_目标制定_20260820_160439\results.yaml
- Excel: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_目标制定_20260820_160439\case_results.xlsx
- 截图: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_目标制定_20260820_160439\screenshots
- Allure: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_目标制定_20260820_160439\allure-results
- Bug 审核: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_目标制定_20260820_160439\bugs_review.yaml


---

## RUN_目标制定_20260820_160545


- run_id: RUN_目标制定_20260820_160545
- 生成时间: 2026-08-20T16:05:53
- 模块: 目标制定（模块 ID 669）
- 需求: REQ-002
- 环境: 192.168.6.163:66（headless=false）

## 范围统计

- 本地 YAML 读取用例数: 91
- 本次新增自动化映射数: 0
- 修复既有自动化映射数: 1
- 已执行用例数: 1
- excluded 用例数: 0
- 仍为 pending_registry 的用例数: 5
- blocked 用例数: 1
- 结果统计: {'blocked': 1}

## 映射与边界

- module_case_map.json：47509 为既有 registered 映射，本轮修复 handler/Page Object/data contract；未创建第二套注册表。
- 数据：按每条用例契约使用 existing_system_data 或 self_created；自造数据使用 AUTO测试_勿用_{{run_id}} 前缀，清理状态以契约为准。
- 禅道：未访问、未写入、未同步结果或创建 Bug。

## 用例结果

| 本地用例 | 禅道编号 | 状态 | 分类 | check_id | assertion_scope |
|---|---:|---|---|---|---|
| TC-002-28 | 47509 | blocked | blocked | TP-002-28 | target_goal.goal_table.pending_review_status |

## 产物路径

- RUN: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_目标制定_20260820_160545
- 阶段 Handoff: 07_ui_automation/HANDOFF.md
- 选择: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_目标制定_20260820_160545\selection.yaml
- 结果: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_目标制定_20260820_160545\results.yaml
- Excel: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_目标制定_20260820_160545\case_results.xlsx
- 截图: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_目标制定_20260820_160545\screenshots
- Allure: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_目标制定_20260820_160545\allure-results
- Bug 审核: D:\05ui_pro\projects\产业链生产排程系统\07_ui_automation\reports\RUN_目标制定_20260820_160545\bugs_review.yaml

---
name: stage-automation-agent
description: "Stage agent for headed Playwright automation and same-run local defect report generation. Auto-select when the request contains any of: 执行UI自动化、运行UI自动化、执行自动化测试、运行自动化测试。"
---

# Automation Agent

## Quick Start

> **Activation：** 可通过 `/qa` 命令或中文自然语言请求触发；UI 自动化必须使用可视浏览器，默认只生成本地结果和缺陷报告。

**命令触发：**

```text
/qa automate --project {project} --req REQ-xxx
```

**触发关键词（包含任一即可）：** `执行UI自动化`、`运行UI自动化`、`执行自动化测试`、`运行自动化测试`

**输入：** `04_testcases/`、`05_case_review/`、`06_zentao_sync/` 和项目根 `module_case_map.json`；`page.json`、`design.json` 如存在，仅作为普通参考资料。

**输出：** `07_ui_automation/reports/RUN_{timestamp}/`，包括结果、截图、日志、Allure 证据和缺陷报告。

**关键边界：** 固定 `headless=False`；不扩展本地用例范围；只创建、验证和保存可独立启动的用例脚本；不得创建、恢复、要求或自动执行任何 `run_*.py`、批量 runner 或替代调度入口；不自动创建远程 Bug。批量执行文件由用户在独立脚本全部确认保存后自行创建和启动。

## 输入与输出

- 输入：`04_testcases/`、`05_case_review/`、`06_zentao_sync/` 和项目根 `module_case_map.json`。
- 依赖输入：无页面清单硬性依赖；`page.json`、`design.json` 如存在，仅作为普通参考资料。
- 输出：`07_ui_automation/reports/RUN_{timestamp}/`。
- 下游：`stage-bug-verification-agent`。

每个 RUN 至少保存 `selection.yaml`、`results.yaml`、`case_results.xlsx`、`bugs_review.yaml`、缺陷报告 Markdown/YAML、截图、日志和 Allure 证据。

每个模块执行单元生成独立 Handoff；路径为 `07_ui_automation/{partition}/{module_id}/HANDOFF.md`，没有业务分区时为 `07_ui_automation/{module_id}/HANDOFF.md`。`module_id` 从用例来源、`module_case_map.json` 或 RUN 元数据继承；同一模块重复执行只更新自己的文件，不得覆盖其他模块。

## 执行要求

1. 本地用例是执行范围唯一来源；注册表只负责映射，不扩展用例范围。
2. Playwright 固定 `headless=False`；浏览器无法可视启动时记录 `blocked`，不得切换无头模式。
3. 执行 UI 步骤前依据用例、脚本、DOM、等待和断言契约完成 readiness 检查；不执行页面清单、页面映射、元素映射或定位器来源存在性核对。
4. 每条用例独立执行 readiness、动作、断言、截图、结果分类和清理。
5. 使用 `passed`、`product_defect`、`test_script_error`、`test_case_error`、`blocked`、`excluded` 等明确分类。
6. 业务动作和断言失败处保留证据，并记录截图 SHA-256。

## 自动生成缺陷报告

自动化执行结束后，基于同一批 `CaseResult` 生成 `bugs_review.yaml` 及缺陷报告：

- 只有确认属于产品行为的问题才标记 `product_defect`；
- 脚本错误、环境问题、权限问题、数据问题和用例契约问题不得直接生成产品 Bug；
- 每条缺陷关联失败用例、RUN、环境、实际/预期结果、分类和证据路径；
- 默认只生成本地报告，不自动创建禅道 Bug。

## 模块级 Handoff

按当前模块写入独立 Handoff，不生成共享分区级文件。内容记录执行范围、结果统计、缺陷报告路径、未执行原因和 `Next Agent: stage-bug-verification-agent`。无法从上游产物或 RUN 元数据识别 `module_id` 时记录 `module_id_missing`，不得覆盖其他模块。

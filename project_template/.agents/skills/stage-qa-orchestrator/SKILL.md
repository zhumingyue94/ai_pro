---
name: stage-qa-orchestrator
description: "Multi-agent orchestrator for the eight-stage QA pipeline in this repository. Auto-select when the request contains any of: 运行完整QA流程、执行完整QA流程、启动QA流程、查看QA状态。"
---

# QA Orchestrator

只负责读取项目配置、调度阶段 Skill、校验模块级 Handoff 和汇总进度，不直接生成业务产物。

## Quick Start

> **Activation：** 可通过 `/qa` 命令或中文自然语言请求触发；必须遵守项目输入、门禁和授权边界，不因触发请求跳过上游阶段。

**命令触发：**

```text
/qa pipeline --project {project}
```

**触发关键词（包含任一即可）：** `运行完整QA流程`、`执行完整QA流程`、`启动QA流程`、`查看QA状态`

**输入：** 项目 `AGENTS.md`、`config.yaml`、各阶段输入和阶段 Skill。

**输出：** Pipeline Summary、模块级 Handoff 状态和缺失输入/门禁问题记录。

**关键边界：** 不直接生成业务产物；缺失输入记录 `input_missing`，门禁采用 `report_only`。

## 默认链路

```text
01_requirements
  -> 02_analysis / stage-requirements-analysis-agent
  -> 03_test_plan / stage-test-plan-agent
  -> 04_testcases / stage-testcase-generation-agent
  -> 05_case_review / stage-case-review-agent
  -> 06_zentao_sync / stage-zentao-sync-agent
  -> 07_ui_automation / stage-automation-agent
  -> 08_bug_verification / stage-bug-verification-agent
  -> 09_regression / stage-regression-agent
```

当前仓库不保留测试点和测点评审目录；主链路从 `01_requirements` 直接进入需求分析。

## 调度规则

1. 读取项目 `AGENTS.md`、`config.yaml` 和阶段 Skill。
2. 校验输入存在；缺失时记录 `input_missing`，不得伪造输出。正式环境 URL、权限、测试数据和清理责任不属于 `02_analysis` 至 `05_case_review` 的必需输入，可由这些阶段记录为风险、依赖或后续执行准备项。
3. `02_analysis` 至 `05_case_review` 的 `report_only` 门禁只反映需求、追溯、设计和产物质量问题；门禁失败继续交接，但必须保留 `gate_reasons`。
4. 禅道同步默认 dry-run；没有显式授权不得远程写入。真实 UI 执行和远程写入仍必须检查凭据、权限、环境、数据隔离和清理责任。
5. 禅道同步必须生成并校验项目根目录 `module_case_map.json`。
6. 自动化阶段读取本地用例、评审结果、同步结果和注册表，执行后在同一 RUN 生成结果和缺陷报告。
7. Bug 验证读取自动化 RUN 内的缺陷报告。
8. 生成和评审阶段必须使用同一份测试设计 Rule；入口动作应位于 `steps.action`，页面到达证据应位于对应 `steps.expected`，`preconditions` 仅保留静态执行条件。
9. Pipeline Summary 和 Handoff 中区分 `navigation_in_preconditions`、`missing_navigation_step`、`missing_page_entry_evidence`、`technical_evidence_leakage` 等问题；这些问题按项目既有 `report_only` 策略记录，不擅自改变流水线流转策略。用例评审还必须汇总 `priority_review`：规则标识、逐条评审覆盖数、P1-P4 统计/比例、优先级不一致项、待确认项及门禁结论；分布偏离只能作为观察项，不能以比例本身阻断交接。
8. 回归阶段读取代码 diff、用例来源和注册表，只执行受影响用例；无法映射的项标记 `impact_unknown`。

`page.json`、`design.json` 如存在，仅作为普通参考资料；下游阶段不得因其缺失、页面状态、页面/元素映射、定位器来源或引用不匹配设置门禁、阻塞或失败。`UI_TEST_*` 只用于测试环境，原型采集只使用 `PROTOTYPE_*`。

## 模块级 Handoff 规则

- 阶段下存在 `app/`、`pc/` 等直接业务分区时，每个模块使用 `{stage_dir}/{partition}/{module_id}/HANDOFF.md`。
- 阶段没有业务分区时，每个模块使用 `{stage_dir}/{module_id}/HANDOFF.md`。
- `module_id` 优先来自 REQ 或模块字段；自动化、Bug 验证和回归阶段从上游产物、注册表或 RUN 元数据继承。
- `module_id` 必须经过路径安全清洗；缺失时记录 `module_id_missing`，不得回退到共享分区级 `HANDOFF.md`。
- `pages/`、`tests/`、`reports/`、`config/`、`data/`、`utils/`、`allure-results/`、`screenshots/` 和 `RUN_*` 是技术目录，不生成 Handoff。
- 同一模块重复执行只更新自己的 Handoff，不得删除或覆盖其他模块文件；写入应采用单文件原子替换。
- 旧分区级 `HANDOFF.md` 不再作为必需输入，发现时记录 `legacy_partition_handoff`。
- Handoff 缺失时记录 `handoff_missing`，不得用 Pipeline Summary 伪造阶段完成。
- Pipeline Summary 递归扫描并汇总所有模块级 Handoff，不创建共享分区级 Handoff。

## 触发命令

```text
/qa pipeline --project {project}
/qa requirements-analysis --project {project} --req REQ-xxx
/qa test-plan --project {project} --req REQ-xxx
/qa generate-cases --project {project} --req REQ-xxx
/qa review-cases --project {project} --req REQ-xxx
/qa zentao-sync --project {project} --req REQ-xxx
/qa automate --project {project} --req REQ-xxx
/qa verify-bugs --project {project} --run RUN_xxx
/qa regression --project {project} --diff {diff_file}
/qa status --project {project}
```

## Pipeline Summary

```markdown
# Pipeline Summary — {project}

| 阶段 | Skill | 状态 | 产物 | Gate |
|---|---|---|---|---|
| 需求分析 | stage-requirements-analysis-agent | … | 02_analysis/ | … |
| 测试计划 | stage-test-plan-agent | … | 03_test_plan/ | … |
| 生成用例 | stage-testcase-generation-agent | … | 04_testcases/ | 包含适用操作核心流程校验 |
| 用例评审 | stage-case-review-agent | … | 05_case_review/ | 复核适用操作到成功用例映射 |
| 禅道同步 | stage-zentao-sync-agent | … | 06_zentao_sync/ + module_case_map.json | 授权/回读 |
| 自动化与缺陷报告 | stage-automation-agent | … | 07_ui_automation/reports/RUN_*/ | … |
| Bug 验证 | stage-bug-verification-agent | … | 08_bug_verification/ | … |
| 影响回归 | stage-regression-agent | … | 09_regression/ | … |

**Overall**: completed | completed_with_gate_issues | not_executed
```

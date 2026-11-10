---
name: stage-testcase-generation-agent
description: "Stage agent for executable testcase generation from requirement analysis and test plan. Auto-select when the request contains any of: 生成可执行测试用例、生成测试用例、生成用例、创建测试用例。"
metadata:
  skill_dependencies:
    required:
      - name: test-design-techniques
        level: required_reference
        trigger: strategy_selection
        purpose: systematic_case_design
    conditional:
      - name: pict-test-designer
        level: conditional
        trigger: multi_parameter
        purpose: pairwise_case_generation
      - name: qa-playwright-py-writer
        level: planning_reference
        trigger: ui_automation_planning
        purpose: automation_feasibility_assessment
      - name: webapp-testing
        level: conditional
        trigger: web_execution_planning
        purpose: headed_ui_case_feasibility
  dependency_contract:
    inputs:
      - path: "02_analysis"
        required: true
      - path: "03_test_plan"
        required: true
    outputs:
      - glob: "04_testcases/TC_{req_id}.yaml"
        required: true
      - glob: "04_testcases/TC_{req_id}*.md"
        required: true
    checks:
      - id: testcase_traceability
        all_markers: [id, steps, expected, trace]
      - id: coverage_ledger_traceability
        all_markers: [coverage_ids, plan_item_ids, atomic_purpose_ids]
        set_checks: [analysis_to_cases, plan_to_purposes, cases_to_valid_coverage]
        failure_status: missing_design
        gate: block_handoff
      - id: testcase_design_result
        any_markers: [BVA, 边界值, EP, 等价类, 决策表, 状态转换, Pairwise, 组合]
      - id: automation_judgment_rule
        required_rule: automation-judgment-rule
        allowed_auto_values: [auto, "no"]
        forbidden_auto_values: [true, false, "true", "false", manual, partial, blocked, null]
        require_decision_reason: true
      - id: testcase_type_rule
        allowed_type_values: [interface, feature, install, config, performance, security]
        forbidden_type_values: [unit, auto, other, negative, boundary, functional, data_consistency, permission, manual, null]
        classification_rules:
          feature: 仅通过页面观察反馈、控件和状态
          interface: 明确调用或校验API、请求响应或字段协议
          install: 安装、部署、升级、卸载、初始化或回滚
          config: 配置项、参数、设置保存读取校验或生效
          performance: 响应时间、吞吐量、并发、容量、资源或稳定性指标
          security: 认证、授权、越权、租户隔离、敏感信息或攻击防护
        failure_status: design_violation
        gate: block_handoff
      - id: human_text_isolation
        forbidden_in: [preconditions, steps.action, steps.expected]
        forbidden_markers: [page.json, state_id, st-default, sortable=false, actual_available, locator_ref, target_element_id, CSS, POM, Fixture, headless=False, 本用例不测, 不进入明细, 不执行导出]
        failure_status: design_violation
        gate: block_handoff
    dependency_checks:
      test-design-techniques:
        - id: design_method_evidence
          kind: contains_any
          any_markers: [BVA, 边界值, EP, 等价类, 决策表, 状态转换, Pairwise, 组合]
      pict-test-designer:
        - id: pairwise_case_evidence
          kind: contains_any
          any_markers: [Pairwise, 2-way, PICT, 组合参数, 组合测试, 参数组合]
      qa-playwright-py-writer:
        - id: automation_feasibility_evidence
          kind: contains_any
          any_markers: [auto, 自动化判定, 断言, 数据隔离, POM, Fixture]
      webapp-testing:
        - id: web_execution_planning
          kind: contains_any
          any_markers: [断言, 数据隔离, 等待, headless=False]
---

# Testcase Generation Agent

## Quick Start

> **Activation：** 可通过 `/qa` 命令或中文自然语言请求触发；必须同时读取需求分析和测试计划，不得伪造缺失输入。

**命令触发：**

```text
/qa generate-cases --project {project} --req REQ-xxx
```

**触发关键词（包含任一即可）：** `生成可执行测试用例`、`生成测试用例`、`生成用例`、`创建测试用例`

**输入：** `02_analysis/` 和 `03_test_plan/`；`page.json`、`design.json` 如存在，仅作为普通参考资料。

**输出：** `04_testcases/TC_{req_id}.yaml` 与 Markdown。

**关键边界：** 不生成测试点、CSV、禅道同步结果或 UI 执行结果；输入缺失时记录 `input_missing`。

## 输入与输出

- 输入：`02_analysis/` 和 `03_test_plan/`。
- 输出：`04_testcases/TC_{req_id}.yaml` 与 Markdown。
- 下游：`stage-case-review-agent`。
- 禁止输出：CSV、禅道同步结果、UI 执行结果。

## Skill 依赖与自动调用

编排器必须先读取本文件 front matter 中的 `metadata.skill_dependencies`，由通用依赖 runner 根据 `02_analysis/`、`03_test_plan/` 和实际用例内容判断触发结果，再把依赖调用说明注入本阶段提示词。Skill 执行状态只保留在当前运行上下文和 Pipeline Summary 中，不生成独立 Skill 执行证据文件。

### `test-design-techniques`

- 调用级别：必须参考。
- 触发约定：读取需求分析和测试计划后，选择适用的 BVA、EP、决策表、状态转换或组合测试方法。
- 调用作用：将测试设计方法、适用对象和选择理由落实到可执行测试用例。
- 阶段边界：不生成测试执行结果，不替代真实需求和测试计划事实。

### `pict-test-designer`

- 调用级别：条件调用。
- 触发约定：存在多个参数、角色、浏览器、环境、配置或组合约束时调用；无多参数场景记录 `not_applicable` 及原因。
- 调用作用：生成 2-way 组合，记录参数、取值、约束、预期结果和覆盖说明。
- 阶段边界：保留关键边界、状态、安全和数据一致性场景；不使用未经确认的业务值。

### `qa-playwright-py-writer`

- 调用级别：条件参考。
- 触发约定：用例存在 UI 自动化候选、页面定位器、自动化标记、断言、POM、Fixture 或数据隔离要求时参考。
- 调用作用：评估断言、数据隔离和自动化可行性，按 `automation-judgment-rule` 得出 `auto` 判定。
- 阶段边界：不生成 Playwright 脚本，不执行 UI 测试。

### `webapp-testing`

- 调用级别：Web 用例条件参考。
- 触发约定：用例包含 Web 步骤或 Web 执行前提时参考。
- 调用作用：评估等待、断言、数据隔离和可视浏览器规划；浏览器规划固定 `headless=False`，不执行页面清单或定位器来源检查。
- 阶段边界：不启动服务，不执行 UI 测试，不生成截图、日志或执行结果。

依赖调用成功不等同于测试用例批准或真实执行通过。必须通过 YAML/Markdown 产物检查和下游评审确认；依赖不可用时记录 `blocked` 或 `not_executed`，输入缺失时记录 `input_missing`。

## Rule 引用与执行

1. 生成前必须发现并读取当前项目声明或当前任务适用的测试设计 Rule；本 Skill 不复制 Rule 的具体条款。
2. 生成时必须以已读取的 Rule 作为唯一测试设计依据之一，先按 Rule 组织测试目的，再生成用例产物；不得仅复制历史用例结构或依赖关键词命中。
3. 生成后必须逐条引用同一份 Rule 对实际 YAML/Markdown 产物执行自检，并记录 Rule 名称、版本或其他可追溯标识、检查范围、通过项、设计违规项和证据阻塞项。
4. Rule 缺失、无法读取、版本不明确或发生冲突时，停止生成，不得使用旧规则或默认规则继续生成。
5. Rule 定义的设计要求未满足时，必须返工并重新自检；未修复前不得完成交接或宣称生成通过。
6. 页面、环境、权限、数据或定位证据不足时，不得伪造已确认、可执行或已通过；正式环境 URL、权限、测试数据和清理责任属于后续真实执行准备项，缺失时记录为待确认、风险或依赖，不以此阻断用例生成。真正缺少上游输入、测试设计目标或 Rule 文件时，才记录 `input_missing`、`blocked` 或阻止交接。
7. 本 Skill 只负责 Rule 的发现、读取、引用、执行和失败处理；具体测试设计要求全部以 Rule 原文为准。

## Casely 风格优先级与连续检测项分组

1. 本 Skill 必须以已读取的测试设计 Rule 中的 Casely 风格抽象为优先依据；若现有历史结构、项目惯例或其他非 Schema 约定与该风格冲突，按 Casely 风格执行。
2. 标题必须同时表达业务条件或动作、操作对象和可观察业务结果；不得只写字段名、功能名、“功能正常”或不可判定结论。
3. 步骤按业务发生顺序组织，动作必须可由测试人员直接执行；预期必须可观察、可判定，并说明比较对象或业务依据。
4. 生成原子目的后，先建立 `业务对象 + 页面/区域 + 数据基线 + 连续动作链 + 核心业务结果 + 检查项` 索引，再对候选执行 `merge`/`split` 判定。
5. 仅当候选同时满足同一页面、同一数据基线、同一业务对象、同一连续动作链、同一业务结果且每个检查项可独立定位失败时，才允许合并；页面切换、不同数据基线、不同对象、互斥状态/条件、不同业务结果、独立重置或无法独立定位失败时必须拆分。
6. 合并时选择主用例，保留来源用例、覆盖目标、原子目的和每个检查项对应的连续步骤/预期；跨页面动作不得仅因共享业务数据或最终结果而合并。
7. 生成完成后必须输出合并审计，至少记录 `merge_decision`、`primary_case_id`、`source_case_ids`、共享页面/数据/动作/结果、保留的 `coverage_ids`、`atomic_purpose_ids` 和 `failure_localization_supported`；使用现有 `trace`、handoff 或评审说明承载，不新增 Schema 字段。

## 产物要求

1. 每条用例包含唯一 `id`、`req_id`、标题、前置条件、步骤、预期、数据、优先级和 `trace`。
2. 每条用例必须携带合法的 `coverage_ids`、`plan_item_ids` 和 `atomic_purpose_ids`；这些集合只能引用当前分析和测试计划中已定义的标识。
3. 生成前先建立覆盖目标、计划范围和原子目的索引，按集合一次性比对分析目标 → 用例、计划项 → 原子目的/用例、用例 → 合法覆盖目标，避免逐条遗漏。
4. 需求或业务资料不足时保留可追溯的待确认说明；没有页面清单条目不得标记 `missing_design`、`blocked` 或阻止交接。真正缺少测试设计目标时仍按覆盖账本规则处理。
5. 维持 `type` 与 `auto` 的一致性。
6. 每条用例必须读取并执行 `automation-judgment-rule`：按适用范围、一票否决、操作可执行、断言、数据清理或隔离、状态控制和原子测试目的逐项判定后，再写入 `auto`；判定只依据步骤与预期，不依据页面清单或采集状态。
7. `auto` 只能写字符串 `auto` 或 `no`；`partial`、`blocked` 只能作为评审记录或 HANDOFF 中的执行准备状态说明，不能作为 `auto` 值。
8. `auto=auto` 必须记录满足条件；`auto=no` 必须记录具体否决原因；当前环境、账号、权限或数据未就绪但设计可自动化时，保持 `auto=auto`，并在评审记录或 HANDOFF 记录执行准备项。
9. 步骤和预期必须可观察、可判定，并引用分析和测试计划中的真实范围。
10. 不依赖测试点编号，不创建 `tp_id`，不生成测试点占位内容。
11. 输入缺失时记录 `input_missing`，不得生成伪造用例。
12. Markdown 必须由公共脚本 `scripts/render_testcase_markdown.py` 从 YAML 派生，唯一格式契约为 `.agents/references/testcase-markdown.template.md`；禁止继续使用旧版 `CASE INDEX` 摘要或项目私有格式。
13. Markdown 生成后必须运行 `scripts/validate_testcase_markdown.py`，交叉校验模板章节、逐条用例字段、步骤数量、统计、用例 ID 和 `auto`/优先级；校验返回非零时禁止完成交接，并保留具体错误。
13a. 若分析或测试计划包含操作能力适用性清单，必须运行 `scripts/validate_core_flow_coverage.py --analysis <analysis.yaml> --plan <test-plan.yaml> --testcases <testcases.yaml>`；返回非零时禁止交接，并逐项保留适用操作、缺失用例、证据不足、未确认项和执行阻塞。没有操作能力清单不应自行推断所有模块都必须具备 CRUD。
14. `page.json`、`design.json` 如存在，仅作为普通参考资料，不检查其存在性、映射完整性、定位器来源或引用一致性。
15. 生成前必须建立状态/条件分支矩阵，至少记录每个分支的静态前置条件、导航步骤、业务数据、页面结果、独立判定标准和资料状态；共享静态前置条件不得合并分支。
16. 生成前必须读取模块级操作能力适用性清单；不为所有模块固定生成 CRUD 或状态流转用例。对 `applicable` 操作必须生成至少一条成功正向用例，且步骤/预期包含触发动作、成功反馈和列表、详情、状态、文件或其他业务结果回读；仅打开表单、字段回显、确认弹窗、取消或失败校验不得计入成功覆盖。
17. 对 `not_applicable` 操作保留来源和业务理由；对 `unconfirmed` 操作保留待确认项，不得猜测为不适用或生成伪造成功结果。已设计但环境、权限、数据或清理未就绪时保留用例并记录 `execution_blocker`。
18. 每个 `atomic_purpose_id` 应对应一个业务目的和一套数据基线；同一业务结果下的关联字段、整体布局、统计字段、公式一致性及必要反向约束可共享该业务目的。若一个预期包含多个可独立失败的互斥状态、条件、对象或业务结果，必须先拆分原子目的再生成用例。
15. 生成后必须检查标题、数据、步骤、预期和 `atomic_purpose_ids` 是否指向同一业务目的和数据基线；发现多个互斥状态/条件、不同对象或不同业务结果混写时，记录 `design_violation` 并阻止交接。
16. 对同一字段存在多个互斥区间、边界或状态组合时，必须先生成分支矩阵，再按矩阵逐分支生成独立用例；禁止用一个“决策表”“分别查看”“依次验证”用例承载多个可独立通过或失败的分支。每个分支必须具备独立的静态数据条件、标题、操作步骤、唯一预期和原子目的；共享导航、权限、页面或数据准备不构成合并依据。
17. 同一套数据基线下，同一动作或连续动作链产生的多个同一业务结果，允许保留在同一个用例中；必须将触发动作、结果回读和关联一致性校验拆成多个连续步骤，每步一个动作单元并紧跟对应预期。该例外不适用于不同数据基线、互斥状态/条件、不同对象或不同业务结果。
18. 生成自检必须逐项核对分支矩阵覆盖：分支数量、分支条件、分支预期、用例 ID 与追溯关系一一对应；发现条件区间缺失、边界归属不清或互斥状态合并时，必须返工后才能交接。
19. 生成前必须为每个原子验证项指定唯一数据基线；一个用例的 `test_data`、`data_contract`、`records`、`fixtures` 或 `scenarios` 不得承载多套互斥数据；同一套关联数据可支持多个字段、整体布局、公式及必要反向约束的联合判定。生成后必须运行 `scripts/validate_case_atomicity.py`（或由 Markdown 校验器调用），命中 `ATOMICITY_MULTIPLE_DATA_BASELINES`、`ATOMICITY_MULTIPLE_BRANCHES` 或 `ATOMICITY_MERGED_SCENARIOS` 即记录 `design_violation` 并阻止交接；同一数据基线的并发动作若已按步骤拆分，不因“分别”描述两个执行端而误报。
19. 发货进度状态必须按五个独立分支生成用例：0%待发货、(0%,100%)发货中、100%待出雏发货中、100%已出雏未签收已发货、100%全部签收已签收；共享页面入口和数据前缀不构成合并理由。

## 分支矩阵与原子拆分示例

对页面入口的条件可见性，至少按以下维度生成独立场景，而不是写成一个复合预期：

| 分支 | 数据条件 | 独立判定 |
|---|---|---|
| 满足条件 | 日期和状态均满足规则 | 目标行显示可用发货入口 |
| 已发货 | 发货单状态为已发货 | 目标行不显示可用发货入口 |
| 已签收 | 发货单状态为已签收 | 目标行不显示可用发货入口 |
| 未来日期 | 计划发货日期晚于当前业务日期 | 目标行不显示可用发货入口 |

这些场景可以共享页面入口和定位依据，但必须有独立标题、数据条件、预期和追溯关系。

## 模块级 Handoff

按当前模块写入独立文件：存在 `app/`、`pc/` 等业务分区时写入 `{stage_dir}/{partition}/{module_id}/HANDOFF.md`，没有业务分区时写入 `{stage_dir}/{module_id}/HANDOFF.md`。`module_id` 优先使用当前 REQ ID；重复执行只更新该模块文件，不得覆盖其他模块。内容汇总生成数量、来源路径、格式检查、门禁结论和 `Next Agent: stage-case-review-agent`。

## 人工文本与机器证据隔离

1. 生成每条用例前，先确定当前需求对该目标的责任边界；`out_of_scope_with_owner` 不生成当前需求的人工操作用例，最多保留账本责任映射。
2. 人工字段仅允许写测试人员可准备、可执行、可观察且直接服务于当前 `atomic_purpose_id` 的内容：标题只写业务对象、条件/动作和唯一判定；`preconditions` 只写账号/权限/环境/浏览器/数据和初始业务状态；`steps.action` 只写完成核心判定所需的最小登录/授权、菜单、模块、页面及页面内动作；`steps.expected` 只写对应动作的可观察业务到达或业务结果。具体登录步骤、正式测试环境 URL 和测试租户不是强制人工字段。
3. 生成每条用例时对标题、每条前置条件、每个步骤和每个预期执行“删除测试”：删除该项后若仍能完成当前原子目的和唯一判定，则不得保留该项。不得为了填充模板固定数量而增加条件、动作或预期。
4. 禁止把 `page.json`、`state_id`、`st-default`、`sortable=false`、`actual_available`、定位器、CSS、POM、Fixture 或 `headless=False` 写入上述人工字段。业务键定位、行级作用域、其他行防误判等自动化策略，除非需求明确将其作为业务验收条件，否则保留在 `ui_source`、`trace`、`locator_ref` 和 `test_data`。
4. 技术字段必须翻译为页面或业务语言，例如将 `actual_available=0` 写为“实际可发数为 0”，将实现属性转换为“页面未提供排序操作”或其他可通过页面观察的描述；不能只删除技术依据而保留不可判定结论。
5. 禁止生成“本用例不测……”“不进入明细页”“不执行导出”等范围声明式步骤。范围边界写入测试计划、覆盖账本和依赖字段。
6. 生成后逐条执行人工可执行性 lint：范围越界、范围声明式短语、内部字段/源文件名/定位器/自动化术语命中均属于设计违规，必须返工；不得仅记录为一般警告。

---
name: stage-case-review-agent
description: "Stage agent for testcase review, executability checks, and ZenTao synchronization package preparation. Auto-select when the request contains any of: 评审用例、审核用例、用例评审、检查用例。"
---

# Case Review Agent

## Quick Start

> **Activation：** 可通过 `/qa` 命令或中文自然语言请求触发；评审失败只记录门禁原因，不自动改写用例或写入远程禅道。

**命令触发：**

```text
/qa review-cases --project {project} --req REQ-xxx
```

**触发关键词（包含任一即可）：** `评审用例`、`审核用例`、`用例评审`、`检查用例`

**输入：** `04_testcases/{partition}/TC_{req_id}.yaml`、同目录配套的 `TC_{req_id}.md`、`02_analysis/` 和 `03_test_plan/`。YAML 是 `auto` 和用例明细的唯一事实源，Markdown 是派生交付物。

**输出：** `05_case_review/REV_CASE_{req_id}.yaml`、Markdown、待同步清单以及对应业务分区的 `HANDOFF.md`。

**关键边界：** 不读取或生成测试点/XMind，不执行 UI 测试，不生成 CSV，不写入远程禅道。

**禅道编号边界：** `04_testcases/` 和 `05_case_review/` 只要求本地用例 `case_id`。评审不得要求或校验真实 `zentao_case_id`、`registry_status` 或 `zentao_type_sync`；这些信息由 `stage-zentao-sync-agent` 在授权同步并完成真实回读后写入项目根目录 `module_case_map.json`。历史用例中存在这些字段时仅作兼容读取，不参与评审门禁。

## 输入与输出

- 输入：`04_testcases/{partition}/TC_{req_id}.yaml` 及同目录同基名的 `TC_{req_id}.md`；`02_analysis/` 和 `03_test_plan/`。
- 输出：`05_case_review/REV_CASE_{req_id}.yaml`、Markdown、待同步清单以及对应业务分区的 `HANDOFF.md`。待同步清单只记录本地 `case_id`、`type`、`auto`、`priority`、来源路径和同步状态，不写入或要求真实禅道编号。
- 评审输出必须包含 `alignment`：记录 YAML/Markdown 路径、执行状态、检查字段、双方统计、差异明细和门禁原因码；同时必须包含 `priority_review`，并在评审 Markdown 和模块级 HANDOFF 中同步优先级逐条评审摘要、P1-P4 统计及分布观察。
- 下游：`stage-zentao-sync-agent`。

## Rule 引用与评审

1. 评审前必须读取生成阶段声明使用的同一测试设计 Rule；本 Skill 不复制 Rule 的具体条款。
2. Rule 缺失、无法读取、版本不明确或与当前适用规则冲突时，停止评审并报告原因，不得使用旧规则替代。
3. 必须依据 Rule 逐条检查实际 YAML/Markdown 结构和语义，不能用关键词存在、字段存在、摘要或历史用例结构代替检查。
4. 评审结果必须记录 Rule 名称、版本或其他可追溯标识、检查范围、设计违规项、证据阻塞项、未确认项和门禁结论。
5. Rule 定义的设计违规属于阻断问题：必须保留 `gate_reasons`，不得完成评审交接或给出通过结论。
6. 正式环境 URL、权限、测试数据或清理责任不足时，记录为执行准备项、风险或依赖，不作为用例评审门禁。只有实际发生的设计违规、追溯缺失或明确的评审输入门禁，才可设置 `gate_reason: true`。
7. 每个评审项必须记录 `code`、`category`、`result`、`gate_reason` 和 `reason`。`category` 至少区分 `design_violation`、`traceability_failure`、`input_gate_failure`、`evidence_risk` 和 `execution_blocker`。只有 `gate_reason: true` 的评审项可进入顶层 `gate_reasons`。
8. 门禁必须按以下公式计算：`gate_reasons` 等于所有 `gate_reason: true` 评审项的 `code` 集合；`gate_passed` 等于 `gate_reasons` 为空。`evidence_risks`、`execution_blockers`、自动化 `status=partial/blocked` 不得自动写入 `gate_reasons`。
9. 本 Skill 只负责 Rule 的读取、引用、复核和结果分类；具体测试设计要求全部以 Rule 原文为准。

### 全局排除的评审门禁项

以下事项对所有模块都不得作为用例评审的 `gate_reasons`、blocking gate 或 `gate_passed: false` 的失败依据：

- `formal_route_not_explored`：正式 URL、菜单承接或运行环境尚未在正式页面确认；
- `authorized_data_missing`：正式账号、菜单/接口权限、脱敏业务数据、可回收提交数据或清理责任未确认。

上述事项只能记录为 `evidence_risks`、`execution_blockers`、`risks`、`dependencies`、`execution_readiness` 或 `unconfirmed_items`，且必须标记 `gate_reason: false`。不得通过 `blocked`、`input_missing` 或 `headed_and_automation_blocked` 变相升级为用例评审门禁。正式 UI/自动化执行阶段仍可按执行规则独立管理 readiness 和数据夹具状态。

### 评审范围与执行状态隔离

本 Skill 的 Case Review 默认只评审用例设计：结构、覆盖、追溯、原子性、步骤/预期可判定性、人工文本隔离和自动化设计适配性。UI、Playwright、有头浏览器、自动化实际执行、PICT 实际执行、CSV 生成和远程禅道同步不属于本轮用例设计评审范围，必须记录为 `not_in_scope` 或项目既有等价的范围外事项，不得作为设计门禁失败原因。

`execution_status: not_executed`、自动化 `status: blocked`、`pending_implementation`、正式环境/权限/数据未就绪均保留为事实状态；它们不得被改写为执行通过，也不得进入设计 `gate_reasons`。评审结论必须分别记录设计门禁、执行评审范围和执行事实，不能用单一总体字段把“设计通过”解释为“执行通过”。

## 检查

检查 Schema、唯一 ID、需求与计划追溯关系、步骤可执行性、预期可判定性、用例重复、自动化标记和模块信息，并按适用 Rule 复核测试设计质量。权限、异常和数据边界不作为独立的评审维度；它们仅在需求覆盖、原子测试目的、状态/条件分支、风险或执行准备项中按实际适用情况检查。自动化标记必须使用 `automation-judgment-rule` 逐条复核：检查操作、断言、数据清理或隔离、状态控制、原子测试目的和一票否决条件，不能只检查字段是否存在。`auto` 只能是字符串 `auto` 或 `no`；`partial`、`blocked`、`manual`、`false` 不能作为 `auto` 值。评审不得要求用例产物包含任何自动化评估结构字段；`auto=no` 必须有具体的一票否决原因。不得使用 `trace.status=blocked` 推断 `auto=no`，也不得因页面清单缺失、页面未采集或缺少已确认 locator 把 `auto=auto` 改为 `no`。对存在 `coverage_ledger` 的需求，检查分析覆盖目标 → 用例、测试计划范围项 → 原子测试目的/用例、用例 → 合法覆盖目标。评审还必须按模块操作能力适用性清单执行集合级检查：不把 CRUD 或状态流转设为固定必选项；`applicable` 操作必须关联成功正向用例和业务结果回读，`not_applicable` 必须有可追溯理由，`unconfirmed` 必须列入待确认项。仅按钮可见、表单打开、字段回显、确认弹窗、取消或失败校验不得计为成功覆盖；缺少适用操作成功用例记录 `missing_design`/`design_violation` 并进入 `gate_reasons`，环境、权限、数据或清理不足则记录 `execution_blocker` 且不自动升级为设计门禁。

### 优先级逐条评审

优先级是独立评审维度，必须在系统性覆盖评审之后、组合覆盖评审之前执行；评审前必须完整读取本项目适用的 `test-design-enrichment-rule.md`，并在评审 YAML、Markdown 和 HANDOFF 中记录规则标识、检查范围及结论。不得仅以优先级字段存在、摘要统计或测试类型代替语义评审。

1. 以 `04_testcases` YAML 的 `case.priority` 作为当前优先级唯一事实源；每条用例必须且只能是 `P1`、`P2`、`P3` 或 `P4`。建立 `case_id -> atomic_purpose_id -> state/condition branch -> priority` 索引，逐条记录评审结果，评审覆盖数必须等于用例总数。
2. 依据需求分析、测试计划及可追溯的业务影响资料，按 Rule 固定判定链检查核心流程阻断、关键数据影响、主要业务结果、使用频率和替代路径。禁止按 `type`、模块、来源优先级、用例数量或“正常/异常”标签直接映射。
3. 每条 `items` 必须结构化记录 `source_priority`、`reviewed_priority`、`impact_area`、`blocks_core_flow`、`causes_key_data_error`、`has_workaround`、`user_frequency` 和具体 `reason`；`reviewed_priority` 必须与 `recommended_priority`（如存在）一致。检查优先级是否与单一原子测试目的、状态/条件分支和独立判定标准一致。
4. 一条用例覆盖多个可独立定级的影响时，记录 `design_violation`，不得用一个优先级掩盖复合测试目的。边界、异常、兼容类场景不得因测试类型自动降级。理由不得只写“沿用来源优先级”“模块重要”“属于核心页面”或其他无业务后果说明。
5. 重算 P1-P4 数量、百分比、变化数量，并核对评审 YAML、Markdown 和 HANDOFF 的统计及 alignment。参考分布偏离时生成 `priority_distribution_observation`，记录实际比例、偏离原因和特殊业务依据；该观察项必须 `gate_reason: false`，不得进入 `gate_reasons`，也不得为满足比例擅自改写优先级。
6. 优先级评审至少输出 `priority_review`，包含 `rule_ref`、`scope`、`case_count`、`reviewed_case_count`、`unreviewed_case_ids`、`distribution`、`change_summary`、`distribution_observations`、逐条 `items`、`mismatches`、`unconfirmed_items` 和 `gate_reasons`。必须校验用例与 items 的数量相等、ID 集合一致、逐条字段完整；Markdown/HANDOFF 应提供同等可追溯摘要。

门禁结果必须区分设计违规、环境/权限/数据阻塞和一般警告。自动化设计条件不满足属于自动化判定问题；仅因环境、账号、权限或数据未就绪时，保留 `auto=auto` 并记录 `blocked`、风险或依赖。生成结论与复核结论不一致时必须记录具体差异和原因码。字段非法、原因缺失或 `auto` 与判定结论矛盾属于结构或设计违规。失败必须保留与独立问题对应的 `gate_reason: true` 评审项和 `gate_reasons`，不得伪造通过，也不得自动改写 `04_testcases`。仅有证据风险或执行阻塞时，评审可以 `gate_passed: true`，但必须如实保留对应风险和阻塞；改写必须有用户明确授权。

## Casely 风格与统一 merge/split 评审

评审以生成阶段使用的同一测试设计 Rule 中的 Casely 风格为优先依据。标题必须表达条件或动作、对象和可观察结果；步骤必须按业务顺序且可人工执行；预期必须可观察、可判定并具有明确比较对象。

对相似用例必须建立 `业务对象 + 页面/区域 + 数据基线 + 连续动作链 + 核心业务结果 + 检查项` 职责索引，并统一按以下模型判定：

- `merge`：同一页面、同一数据基线、同一业务对象、同一连续动作链、同一业务结果，且各检查项仍可通过独立步骤和预期定位失败。
- `split`：存在页面切换、不同数据基线、不同业务对象、互斥状态/条件、不同业务结果、独立重置需求或无法独立定位失败。

评审不得仅因共享页面、导航、权限、数据前缀或最终业务结果而合并；跨页面动作必须作为不同动作处理。合并建议必须记录主用例、来源用例、共享页面/数据/动作/结果、保留的覆盖目标和原子目的、步骤/预期映射及失败定位结论，并写入现有评审说明、trace 或 handoff 承载位置，不新增 Schema 字段。

## 用例重复评审

“用例重复”仅比较不同用例之间的主测试点是否重复，重点检查核心业务行为、状态或条件分支、被测结果以及独立判定标准。若两条用例的主测试点相同，仅数据表现、措辞或过程步骤不同，应记录重复候选并按上述统一模型判断 `merge` 或保留；若主测试点、状态/条件分支或独立判定不同，不因共享前置条件或页面流程判定重复。

以下内容属于过程性页面到达或证据验证，不属于主测试点：登录、菜单导航、进入页面、页面标题验证、菜单高亮验证、加载状态验证，以及为证明页面已打开而执行的同类步骤。不同用例共享这些步骤时，不得据此判定用例重复。重复评审必须忽略这些公共过程步骤，只比较用例核心业务操作与结果判定；确认主测试点重复且无独立覆盖价值时，记录为 `design_violation`，并保留对应的重复用例 `case_id`、重复依据和处理建议。

## 跨用例职责唯一性复核

评审必须在单条用例原子性检查之后、最终门禁之前，对当前需求的全部用例执行集合级职责复核，不得只抽查重点场景或只按标题、`atomic_purpose_ids` 判断。

### 条件适用的操作覆盖复核

评审必须以需求分析和测试计划中的操作能力适用性清单为准，建立 `operation_capability -> applicability -> positive_case_ids -> success_evidence` 索引。只对明确为 `applicable` 的操作要求成功正向覆盖，不得因模块没有新增、编辑、删除或状态按钮而报缺失。`not_applicable` 必须有业务理由；`unconfirmed` 不得被当作不适用，需保留待确认或证据风险。成功用例必须体现触发/提交、成功反馈和业务结果回读；仅入口、表单、弹窗、取消及失败校验不计入。`applicable` 无成功用例属于 `missing_design`，必须设置 `gate_reason: true`；已有用例但执行条件不足属于 `execution_blocker`，`gate_reason: false`。

1. 为每条用例建立并保留职责指纹：业务对象、初始状态、触发动作、状态/条件分支、核心结果、数据影响和验证层级；忽略登录、菜单导航、进入页面、页面标题、加载状态等过程性步骤。
2. 对全量用例比较主测试点、状态/条件、被测结果和独立判定标准；重点覆盖退出草稿、重复提交、提交状态、权限、页面状态、数据一致性，同时覆盖筛选、输入校验、空态、公式、异常、位置录入、页面展示、状态流转和跨页面联动等其他场景。
3. 发现复合用例时，先记录拆分候选，再判断跨用例重叠；不得以共享前置条件、页面流程、数据前缀或相同优先级判定重复。
4. 每个相似候选必须记录 `case_ids`、行为指纹、重叠点、每条用例的独有职责、验证层级、处理决定（`retain`/`retain_and_narrow`/`merge`/`split`/`delete`）和决定依据。
5. 仅当主测试点、状态/条件分支、结果和独立判定均相同且无独有风险时，才可合并或删除；不同验证层级可以保留，但必须删除重复断言并明确层级边界。
6. 每条保留用例必须有可审计的独有职责；无法说明删除后丢失的独有风险时，必须记录 `design_violation`，不得以覆盖完整或单条用例质量合格替代集合级去重。
7. 评审结果必须包含全量检查数量、相似候选数量、重叠处理统计、未确认候选和最终门禁结论。未解释的重复候选必须进入 `gate_reasons`。

## YAML/Markdown 对齐复核

评审开始时必须先读取同目录配套的 `TC_{req_id}.yaml` 和 `TC_{req_id}.md`，并调用项目配置的 Markdown 校验器；缺失 Markdown 必须记录 `TESTCASE_MARKDOWN_MISSING`，校验失败必须记录 `TESTCASE_MARKDOWN_YAML_MISMATCH` 或 `TESTCASE_MARKDOWN_SUMMARY_MISMATCH`。逐条按 `case_id` 建立索引，至少核对总数、ID 唯一性和集合、标题、优先级、`auto`、`type`、`atomic_purpose_ids`、追溯字段、步骤数量以及每个步骤的 action/expected；同时核对 YAML 明细重算的总数、`auto`、类型和优先级统计与 Markdown 展示统计。对齐检查结果必须写入评审 YAML、Markdown 和 HANDOFF 的 `alignment` 区块。对齐失败属于测试用例交付物/结构一致性问题，必须设置 `gate_passed: false` 并保留具体 `gate_reasons`；不得用 Markdown 的 `auto` 或统计替代 YAML 的自动化评审事实源，也不得自动改写 `04_testcases`。

## 自动化判定复核

评审开始前应运行 `scripts/validate_core_flow_coverage.py`（当上游存在操作能力适用性清单时），并将其逐项结果写入评审或 HANDOFF 的现有说明区；返回非零时按 `missing_design`/`design_violation` 阻断，`unconfirmed` 和 `execution_blocker` 必须分别记录，不得互相替代。

评审必须读取生成阶段使用的同一份 `automation-judgment-rule`，并在评审记录中保留规则标识、生成结论、复核结论和差异原因。对每条用例建立 `case_id -> auto -> decision/status -> matched/reason_codes` 检查索引，并从实际用例集合重算 `auto_counts` 和状态分布；发现摘要与明细不一致时必须报错。评审不得因为缺少正式 URL、账号、权限、测试数据或清理责任而直接把设计结论改为 `auto=no`；这些属于执行准备、风险、依赖或 `blocked`。只有系统设计上无法清理或隔离数据、无法控制关键状态、无法形成稳定断言或命中其他一票否决条件时，才判定为 `auto=no`。

## 禁止事项

- 不读取或生成测试点、TP 文件或 XMind 测点评审产物。
- 不执行 UI 测试。
- 不在评审阶段自动或按门禁结果生成 CSV；CSV 如确有需要，只能由后续同步流程或用户明确调用导出工具生成。
- 不写入远程禅道。
- 不因测试用例缺少 `zentao_case_id`、`registry_status` 或 `zentao_type_sync` 设置 `gate_reasons`。

## 模块级 Handoff

按当前模块写入独立文件：存在 `app/`、`pc/` 等业务分区时写入 `{stage_dir}/{partition}/{module_id}/HANDOFF.md`，没有业务分区时写入 `{stage_dir}/{module_id}/HANDOFF.md`。`module_id` 优先使用当前 REQ ID；重复执行只更新该模块文件，不得覆盖其他模块。内容汇总评审结果、问题、同步清单、来源哈希和 `Next Agent: stage-zentao-sync-agent`。

## 人工可执行性与范围门禁

除 Schema、需求与计划追溯、覆盖和人工可执行性检查外，必须逐条检查人工字段：

- 标题是否只表达当前原子测试目的的业务对象、条件/动作和唯一判定，未混入页面路径、自动化状态、定位策略、排除项或其他分支；
- `preconditions` 是否只包含可准备的账号、权限、环境、浏览器、数据和初始业务状态，且不包含菜单/页面导航动作、业务键、行级作用域或定位器确认；
- 是否对前置条件和步骤执行删除测试，删除后仍能完成当前原子目的的无贡献项是否已移除；
- `steps.action` 是否包含适用的登录/授权、菜单、模块、页面入口及当前需求范围内的最小必要页面动作；
- 导航步骤是否具有页面标题、菜单高亮、目标区域、加载状态及错误提示等可观察到达证据；
- `steps.expected` 是否为与对应动作直接关联的最小、可观察、可判定导航证据或业务结果，且未混入技术定位、防误判或范围声明；
- 是否存在“本用例不测”“不进入”“不执行”等范围声明式步骤；
- 是否泄漏内部字段名、实现属性、定位器、CSS、POM、Fixture 等机器实现细节。

前置条件包含导航动作、步骤缺少适用的页面入口动作、导航步骤缺少页面到达证据、标题与原子目的不一致、存在删除后仍不影响核心判定的无贡献条件或动作、范围越界、声明式范围步骤和技术字段泄漏，均记录为 `gate_reasons` 中的设计违规；不能通过删除断言、保留 `blocked` 或增加说明文字规避。业务键定位、行级作用域和防误判策略只有在需求明确作为业务验收条件时才可出现在人工字段。跨需求目标必须检查计划/覆盖账本中的 `owner_req_id`，当前用例不得承担责任需求的交互验证。

## 原子性与状态分支评审门禁

必须为每条用例建立“用例 → 原子目的 → 状态/条件分支”的检查索引，并按以下顺序核对；具体拆分标准以已读取的 `test-design-enrichment-rule` 为准，本 Skill 不复制其条款。

1. 先确认 `expected` 中并列项的容器：是否同属一个已打开的控件、弹层或下拉。
2. 同一容器内的组成选项或按钮列举（如日期弹层中的昨天、今天、明天、自定义日期、重置和确定）是该控件一次完整性判定，不得仅因顿号、“和”或“以及、同时、分别、依次、均、都应”记为复合 `expected` 或 `design_violation`。
3. 容器不同、业务结果不同、互斥日期/状态分支或正负混合时，再按 Rule 判定是否复合。
4. 继续核对：一个用例是否只有一个业务目的、一套数据基线和一个核心业务结果；同一业务结果下的关联字段、整体布局、公式一致性及必要反向约束可以合并；多个互斥状态/条件、不同对象、不同数据基线或不同业务结果不得放在同一用例；标题、前置数据、步骤、预期和 `atomic_purpose_ids` 是否指向同一业务目的；状态/条件分支矩阵中的每个适用分支是否都有独立用例。
5. 对同一字段的互斥区间或状态组合，必须逐项核对“条件边界、静态数据、唯一状态预期、独立用例 ID”四项是否完整。例如发货进度的 0%、(0%,100%)、100% 且待出雏、100% 且已出雏未签收、100% 且全部签收，必须是五个独立分支；将其合并为一条决策表用例属于 `design_violation`，即使步骤中逐项列举了五种数据也不得视为覆盖。
6. 评审必须执行 `scripts/validate_case_atomicity.py`；一个用例包含多套 `test_data` 数据基线、多个互斥分支、不同对象/业务结果或多个可独立定级的目的时，记录 `ATOMICITY_MULTIPLE_DATA_BASELINES`、`ATOMICITY_MULTIPLE_BRANCHES` 或 `ATOMICITY_MERGED_SCENARIOS`，并纳入 `gate_reasons`。同一套关联数据下的字段、整体布局、公式和必要反向约束不应仅因断言数量被判为违规。

以下问题统一记为 `design_violation`，保留具体 `gate_reasons`，不得降级为一般表达问题或 `blocked`：跨区域或跨结果的复合预期、多个互斥状态共用断言、分支无独立用例、标题与预期不一致、仅因共享前置条件而合并用例。REQ-PC-041 的“满足条件显示、已发货不显示、已签收不显示、未来日期不显示”应分别形成四条独立用例。同一已打开控件内的组成项列举不在此列。

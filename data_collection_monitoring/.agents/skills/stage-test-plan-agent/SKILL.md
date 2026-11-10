---
name: stage-test-plan-agent
description: "Stage agent for test planning. Reads 02_analysis and writes a test plan without generating test points. Auto-select when the request contains any of: 生成测试计划、创建测试计划、制定测试计划、编写测试计划。"
---

# Test Plan Agent

## Quick Start

> **Activation：** 可通过 `/qa` 命令或中文自然语言请求触发；本阶段必须先读取上游分析，并保留 `report_only` 门禁结论。

**命令触发：**

```text
/qa test-plan --project {project} --req REQ-xxx
```

**触发关键词（包含任一即可）：** `生成测试计划`、`创建测试计划`、`制定测试计划`、`编写测试计划`

**输入：** `02_analysis/REQ-{id}.yaml`、需求来源和项目配置；`page.json`、`design.json` 如存在，仅作为普通参考资料。

**输出：** `03_test_plan/TEST_PLAN_{id}.yaml`、对应模块独立的 `HANDOFF.md`。

**关键边界：** 只生成测试计划；不生成测试点、测试用例、CSV、禅道数据或 UI 脚本。

## 输入与输出

- 输入：`02_analysis/REQ-{id}.yaml`、需求来源和项目配置；`page.json`、`design.json` 如存在，仅作为普通参考资料。
- 输出：`03_test_plan/TEST_PLAN_{id}.yaml`、对应 Markdown，以及对应模块独立的 `HANDOFF.md`。
- Schema：`../../.agents/references/test-plan.schema.json`。
- 下游：`stage-testcase-generation-agent`。

### 页面参考资料使用规则

- `page.json`、`design.json` 如存在，可读取其中与需求相关的普通参考信息。
- 页面清单缺失、页面状态、页面映射、元素映射、定位器来源或页面引用不匹配，不设置门禁、`input_missing`、`blocked` 或失败结论。
- 测试计划依据需求、分析资料、环境、数据、权限和其他有效业务资料生成，不执行页面证据专项检查。

## 计划内容

测试计划必须覆盖：测试范围与非范围、测试策略、环境、数据、角色、风险、依赖、优先级、准入/准出标准、证据要求和 Smoke/Targeted/Full 套件建议。

### 计划设计流程

1. **分析**：解析需求和上游分析，识别测试范围、目标、测试类型、风险、依赖和待确认问题。
2. **生成**：形成结构化测试计划，覆盖边界、变化场景、环境、数据、角色、证据和回归套件建议。
3. **校验**：检查范围是否完整、策略是否可执行、环境和数据前提是否被正确记录、风险及缓解措施是否记录、准入/准出标准是否完整、证据要求是否可落地。正式环境 URL、权限、测试数据和清理责任未就绪时记录为依赖或后续执行准备项，不作为测试计划阶段门禁。
4. 对上游操作能力适用性清单逐项定义主流程要求：`applicable` 操作必须说明触发动作、成功反馈、数据/状态变化、回读证据和清理方式；`not_applicable` 必须保留业务理由；`unconfirmed` 必须进入待确认项，不能按不适用跳过。

计划 Markdown 必须使用本项目规定的中文标题和章节顺序；不复制外部模板中的英文标题或不属于本阶段的测试用例、回归执行内容。

### 计划完整性检查

- 范围明确区分范围内和范围外。
- 测试策略与需求对象、风险和选用方法一致。
- 环境、页面入口、登录前提和浏览器信息完整。
- 测试数据的准备、修改、清理责任和敏感信息边界明确。
- 依赖、风险、待确认问题和缓解措施已记录。
- 准入标准和准出标准可检查、可判定。
- 证据要求包含执行范围、环境、时间和证据位置。
- Smoke、Targeted、Full 套件建议完整。
- 每个 `applicable` 操作均定义成功证据、回读方式、数据/状态变化和清理责任；不适用操作有理由，未确认操作已列入待确认项。
- 计划不把所有模块固定要求为 CRUD 或状态流转模块。

### 计划编写反模式

- 测试范围或目标表述模糊，无法判断是否覆盖需求。
- 缺少环境、页面入口、登录前提或测试数据条件。
- 缺少依赖、风险、准入标准、准出标准或证据要求。
- 以通用通过率或未确认的发布规则替代当前项目契约。
- 将测试计划生成、测试用例生成或真实执行结果混为同一阶段。

### 计划字段映射

计划分析结果必须写入现有测试计划字段：

- `strategy`：测试设计方法及选择理由。
- `environment`：浏览器、页面、入口和登录前提。
- `data`：测试数据准备、修改和清理边界。
- `risks`、`dependencies`：组合测试、自动化、环境和工具依赖。
- `evidence`：浏览器、截图、日志和结果证据要求。
- `suites`：`Smoke`、`Targeted`、`Full` 三类套件建议。

不得新增测试计划 YAML 字段或修改 `test-plan.schema.json`。

## 失败处理

- 上游分析缺失：记录 `input_missing`，不得编造测试范围、环境、参数或预期结果。
- 工具或环境不可用：记录 `blocked` 或 `not_executed`。
- Schema 校验失败：记录 `schema_error`，不得生成已完成状态的 Markdown。
- 门禁继续采用 `report_only`。

## 禁止事项

- 不生成 `TP_*` 或测试点评审文件。
- 不生成测试用例、CSV、禅道数据、注册表或 UI 脚本。
- 不把测试点能力换名后继续输出。
- 事实不足时使用待确认项，不填猜测结论。

## 输出校验

输出 YAML 前必须依据 `../../.agents/references/test-plan.schema.json` 校验结构。缺少必填字段、字段类型错误、非法状态、缺少 Smoke/Targeted/Full 套件或出现未约定字段时，记录 `schema_error`，不得伪造通过或交接下游。

输出不得包含 `tp`、`tp_id` 或其他测试点相关字段。

## Markdown 输出规范

1. 必须先生成并通过 `../../.agents/references/test-plan.schema.json` 校验 YAML，再生成对应 Markdown；Schema 校验失败时不得生成“已完成”的 Markdown，必须记录 `schema_error`。
2. Markdown 必须按以下固定顺序使用中文标准标题：

```text
测试计划
执行摘要
测试范围
  范围内
  范围外
测试策略
测试环境
测试数据与角色
依赖与风险
准入标准
准出标准
证据要求
冒烟 / 定向 / 全量回归套件建议
阶段交接边界
```

3. 标准标题不得输出 `Test Scope`、`In Scope`、`Out of Scope`、`Test Strategy` 等英文标题。
4. `Smoke`、`Targeted`、`Full` 在 Markdown 中分别显示为“冒烟”“定向”“全量”；YAML Schema 字段名保持不变。
5. 只翻译标准章节标题和套件显示标签，不翻译需求原文、业务名称、接口名、状态值、风险描述或证据内容。
6. Markdown 内容必须与已通过 Schema 校验的 YAML 保持范围、策略、风险、准入/准出、证据和套件建议一致。

## 模块级 Handoff

按当前模块写入独立文件：存在 `app/`、`pc/` 等业务分区时写入 `{stage_dir}/{partition}/{module_id}/HANDOFF.md`，没有业务分区时写入 `{stage_dir}/{module_id}/HANDOFF.md`。`module_id` 优先使用当前 REQ ID；重复执行只更新该模块文件，不得覆盖其他模块。内容汇总计划状态、风险、待确认项、Schema 校验状态和 `Next Agent: stage-testcase-generation-agent`。

## 下游用例范围契约

1. `scope.in_scope` 只列当前需求负责的可验证行为；跨需求能力必须在 `scope.out_scope`、`dependencies` 和 `traceability_contract` 中标注责任需求。
2. `out_of_scope_with_owner` 仅用于覆盖账本和交接，不得要求下游用例添加“不测”“不进入”“不执行”等说明步骤。
3. 对跨需求页面元素，明确允许的最小验证粒度。例如当前需求只负责按钮可见性时，计划不得把弹窗配置、确认、文件生成或下载作为当前需求用例目标。
4. 计划中的内部证据（`page.json`、`state_id`、定位器、实现字段）用于证据和自动化规划，不得作为人工用例前置条件、操作或期望的措辞来源；计划应同时给出页面可见名称和业务可执行描述。
5. 测试计划交接前增加“用例可执行性契约”：前置条件可准备、步骤可操作、期望可观察；未满足时标记风险或阻塞，不把规划术语下传为人工文本。

# UI 执行与 Bug 审核公共规则

## 文档定位

本规则适用于 Harness 阶段 8 UI 自动化执行，以及执行结果进入禅道 Bug 的审核流程。
项目规则可以补充页面、账号、数据和用例细节，但不得降低本规则的证据和人工审核要求。

## 失败分类

执行失败后，必须先完成分类，再决定是否进入 Bug 审核文件：

| 分类 | 定义 | 是否允许进入 Bug 审核 |
| --- | --- | --- |
| `product_defect` | 产品真实行为、数据、业务规则或用户可见结果不符合有效预期 | 是 |
| `test_script_error` | 定位器、等待、断言实现、浏览器驱动或脚本逻辑错误 | 否 |
| `test_case_error` | 用例步骤、预期或测试数据设计错误，未正确描述真实验证路径 | 否 |
| `blocked` | 环境、登录、权限、网络、服务或数据准备阻塞 | 否，记录阻塞证据 |
| `accepted_variation` | 与预期文字存在差异，但业务语义、操作结果和用户理解等价 | 否，按通过或接受偏差记录 |

## 数据夹具与关联证据

- 数据依赖用例必须在业务断言前通过夹具门禁；记录自然唯一键、上游状态、下游匹配字段和 `association_verified` 关联结果。
- 上游存在多条候选记录时必须遍历并实时验证，禁止默认取第一条记录。
- 只有满足前置条件且能证明主键关联的记录才可作为测试夹具；缺失数据或关联失败分类为 `blocked`。
- 查询、筛选、列表/详情展示、状态展示和状态筛选可登记为 `existing_system_data` 只读夹具；会改变状态的用例仍优先使用专属数据。只有取得用户明确授权并登记前后状态、自然唯一键和关联证据后，才可对现有数据执行必要状态动作；不得默认修改、审批、删除或清理。

## 弹窗与 DOM 语义门禁

- 每条弹窗用例开始前必须清理前一条用例遗留的弹窗、遮罩和页面状态。
- 关闭逻辑必须依据真实 DOM 支持 `×`、SVG close 图标和“取消”等页面实际控件；点击后必须等待并断言弹窗已消失。
- 断言必须限定在当前查询区、列表区、数据行或弹窗区域；禁止用整页文本替代区域断言。
- 禁用/只读控件不是可编辑控件；控件值优先读取 `input_value()` 或属性值，不能用 `inner_text()` 判断表单字段值。

## UI 文字与语义判定

- UI 文案不一致不自动判定为 Bug。
- “查看”与“查看{年度业务目标}”、“编辑目标”与“编辑{年度业务目标}”、“审批”与“审核{年度业务目标}”等语义等价的简写，在未明确要求精确文案时视为 `accepted_variation`。
- 只有以下情况才可将文案差异判定为 `product_defect`：
  - 需求、验收标准或设计规范明确要求精确文本；
  - 文案造成业务含义歧义或误导；
  - 文案导致操作对象、状态、权限或结果被误解；
  - 文案违反法规、品牌、国际化或无障碍要求。
- 自动化断言优先验证功能语义、控件能力、数据结果和状态变化；精确标题断言必须有明确需求依据。

## 用例步骤完整性

- 创建 Bug 前必须确认自动化步骤覆盖了触发问题所需的完整动作路径。
- 未执行关键动作、未进入目标状态或只检查初始页面时，不得据此创建产品 Bug。
- 如果步骤或预期不正确，分类为 `test_case_error`，先修正用例或自动化脚本。
- 弹窗、确认框、二次输入框等嵌套交互必须按真实顺序执行并记录实际结果。

## 断言契约与失败分类

- 每条被筛选的自动化用例必须有显式断言契约，至少声明 `check_id`、`assertion_scope` 和期望来源。
- 页面对象只提供定位、读取和操作能力；不得在公共页面方法中附加不属于当前用例的业务断言。
- 查询区、列表区、弹窗和数据行必须按独立 DOM 区域读取；不得用整页文本把其他区域的字段作为当前用例结果。
- `product_defect` 只能由显式产品断言失败产生；普通 `AssertionError`、定位失败或等待失败一律不得自动升级为产品缺陷。
- 弹窗残留、定位器错误、等待超时、错误的 DOM 读取方式和脚本断言实现错误必须归为 `test_script_error` 或 `blocked`，不得创建 Bug。
- 失败记录必须保存 `check_id`、`assertion_scope`、`expected`、`actual`、`failure_origin` 和当前用例的数字 `zentao_case_id`。
- 结果状态映射固定为：`product_defect -> failed`、`blocked -> blocked`、`accepted_variation -> passed`、`test_script_error/test_case_error -> ignored`。

## Bug 两阶段门禁

### 阶段一：项目内审核

每次执行只在以下 RUN 目录生成审核文件：

```text
07_ui_automation/reports/RUN_{timestamp}/bugs_review.yaml
```

执行阶段禁止自动调用禅道创建 Bug。文件只记录 `product_defect`，并使用以下结构：

```yaml
review_status: pending
bugs:
  - case_id: TC-xxx
    zentao_case_id: 47542
    classification: product_defect
    title: 纯问题标题
    keywords:
      - REQ-xxx
      - TC-xxx
      - TP-xxx
    precondition: []
    steps: []
    actual: ""
    expected: ""
    evidence:
      screenshot: screenshots/TC-xxx.png
      console_errors: []
      page_errors: []
      request_errors: []
    zentao_bug_id: null
```

### 阶段二：用户确认后提交禅道

- 只有用户明确确认后，才允许创建审核文件中的 Bug。
- 仅提交用户确认的条目；未确认、`test_script_error`、`test_case_error`、`blocked` 和 `accepted_variation` 不得提交。
- 创建成功后回写 `zentao_bug_id`，并保留禅道返回的真实编号。
- 每条 Bug 候选默认只对应一个实际产生该缺陷的用例；不得因为多个用例访问同一页面、截图相同或缺少同一字段就自动合并。
- 只有多个用例都独立执行了同一触发路径、各自期望均覆盖该问题，并经用户确认后，才允许人工合并 Bug；合并时仍须保留每个数字来源用例和独立证据映射。

## 禅道字段与证据

- 标题只描述问题，不写 `REQ-xxx` 或来源用例编号。
- “来源用例”必须在禅道选择框中选择数字用例 ID，例如 `47542`；不能填写 `TC-xxx` 文本代替。
- 关键词可写 `REQ-xxx`、来源用例编号和真实 `zentao_case_id`。
- 中文重现内容使用独立换行的 `[前置条件]`、`[步骤]`、`[结果]`、`[期望]`、`[证据]` 区块。
- 创建 Bug 时，重现步骤（steps/描述编辑器）必须先清空编辑器中的默认、占位或预填内容，再按模板区块填写；禁止在残留内容上追加或混排。
- 截图优先直接嵌入禅道证据区；只有无法嵌入时才上传附件。
- 禅道内容不得填写本地截图路径、`file://` 链接或仅本机可访问的 URL。
- 项目内审核文件可以保存相对截图路径，用于本地复核。
- 截图元数据必须记录用例 ID、检查 ID和 SHA-256；截图文件名至少包含用例 ID和检查 ID。
- 禅道图片嵌入必须回读确认真实 `fileID` URL和附件文件名；禁止 `{711.png}`、`%7B711.png%7D` 等占位或编码错误地址。嵌入失败才允许附件兜底。
- 禅道来源用例、测试单属于关联关系，必须通过专用关联接口或页面维护；不得以 v1 Bug 普通字段更新成功作为关联成功依据。

## 执行完整性与重跑隔离

- 每条用例必须独立完成执行、证据保存、结果回写、读回确认和页面状态清理；单条异常不得造成后续结果重复或错位。
- 报告必须校验实际结果数量、数字用例 ID顺序、ID唯一性、每条禅道读回状态、截图 SHA-256 和 Allure 附件映射。
- 外层命令超时、浏览器仍在运行或结果数量不完整时，RUN 必须标记为不完整，不得作为最终交付报告。
- 失败重跑必须使用新的唯一 `run_id`，不得覆盖、追加污染或混用历史 RUN 结果；定向重跑仍须先读取原始完整用例范围。
- 禅道同步必须完成 `zentao readback`，逐条确认实际结果，不得只依据提交响应或 HTTP 状态判定成功。

## 测试数据与清理

- UI 执行必须优先使用本次运行自建数据（**自造数据强制加前缀 `{test_data_prefix}`**）。查询/展示/只读状态可使用不带此前缀的 `existing_system_data`；状态变更使用现有数据必须有用户明确授权并记录变更前后值、自然唯一键和关联证据，不得默认修改、审批、删除或清理。
- 每次 UI 执行结束后必须更新项目内 `07_ui_automation/data/REQ-{req_id}.yaml`。该文件是紧凑的复用登记索引，RUN 报告仍是完整证据来源。
- 创建前先以登记清单识别候选，再在系统实时核验自然唯一键、测试数据归属和目标状态；只有可证明为**自造的** `{test_data_prefix}` 专属数据且满足前置条件时可复用。
- 对重复或唯一键冲突：不得触碰归属不明或业务数据；先回查本 RUN 的同键记录，只有字段和状态匹配才按幂等成功处理，否则换候选键。每次最多尝试 10 个实时可用候选键；耗尽时分类为 `blocked` 并记录尝试证据。
- 登记文件不保存页面正文、截图、本地证据路径、密码、Cookie、Token 或认证信息。清理成功后保留登记历史并标记 `deleted`。
- 测试数据执行后默认保留；任何清理动作必须先获得用户确认。
## Automatic data provisioning and test-task result synchronization

- Provision self-created data with mandatory `{test_data_prefix}{run_id}_...` prefix; system-existing data may be used without this prefix as read-only fixtures. Verify via registry and live-page before business assertions.
- Recheck duplicate responses before retrying; never modify non-owned records; try at most 10 candidates and record `blocked` when exhausted.
- Gate readiness per case or role. Missing data is `blocked`; selector or DOM mismatch is `test_script_error`.
- Map local results to ZenTao as `passed -> pass`, `failed -> fail`, `blocked -> blocked`, `ignored -> n/a`, then verify every case's actual result by readback.
- API fallback through the headed ZenTao page may be used only when configured and must still be readback-verified; otherwise report synchronization as blocked.

## 页面就绪、表格列与复核隔离

- 造数或状态流转完成后，必须刷新目标表格并等待表头、表体和加载遮罩稳定；刷新前读取到的旧列表不得作为证据。
- 每条用例前后清理可见弹窗、确认框和遮罩；弹窗内控件必须限定在当前可见容器内定位。
- Element Plus 表格的列断言必须先滚动目标表格横向容器到最右侧，再读取表头和单元格。简称与全称在未明确要求精确文本时按语义等价处理，例如“修改人/修改人员”“提交人/创建人员”。
- 数据角色是按用例隔离的 readiness 门禁；表头、分页和控件结构检查不得因为无关数据角色缺失而阻塞，状态/编辑/审核/删除应优先定位本 RUN 自建且登记的专属记录。
- 分页控件使用前先检查 disabled 状态；没有足够页数、没有合格长文本或没有可操作状态行时，记录 `blocked` 及前置原因，不能升级为 `product_defect`。
- 远端步骤与当前页面契约不一致时分类为 `test_case_error`/`blocked`，不执行猜测性操作，也不创建 Bug。

## 用例前置条件与自动造数强制流程

每条用例在执行业务步骤和断言前必须按以下顺序通过 readiness 门禁：

```text
读取用例契约
→ 评估前置条件
→ 查询数据登记
→ 页面实时核验自然唯一键和状态
→ 条件不足时自动造数/扩充
→ 刷新页面并验收字段、状态和数量
→ ready=true
→ 执行业务步骤和断言
```

契约至少记录 `case_id`、`required_roles`、`preconditions`、`prepare`、`execute` 和
`assertions`。示例：

```yaml
case_id: 47617
required_roles: []
preconditions:
  - name: plan_row_count
    operator: ">="
    expected: 2
prepare: ensure_plan_rows
execute: delete_plan_row
assertions:
  - plan_row_count_decreased
  - remaining_rows_at_least_one
```

- `ready=false` 时不得执行业务断言、不得创建 Bug；数据准备失败或前置条件耗尽记为 `blocked`。
- 定位器、DOM、等待和脚本实现不匹配记为 `test_script_error`，不能伪装成数据阻塞。
- 删除类先确认目标存在；若有“删除后至少保留一条”等约束，先造数或补行，验收数量满足后才删除。
- 分页类先确认总数大于当前每页条数；不足时创建专属数据并刷新、验收总数和页码，无法满足才阻塞。
- 查询类先准备可匹配数据、组合条件数据和实时确认不存在的空结果值；编辑/更新类先准备状态允许编辑且字段可修改的数据；审核类先准备待审核及目标状态数据。
- 方案/明细行操作必须在当前弹窗内检查行数；例如删除操作必须先达到至少 2 行，删除后校验减少 1 行且剩余至少 1 行。
- 长文本造数必须先读取目标前端输入框的 `maxlength`、组件校验规则或等价的页面约束，生成长度不超过且优先等于该输入框允许最大长度的专属值；不得用超过前端允许长度的字符串强行触发省略号。
- 长文本值仍须保留 `{test_data_prefix}{run_id}_` 归属标识；应在最大允许长度内压缩可变后缀，提交后刷新页面并回查实际保存值、单元格展示和 Tooltip/详情内容。
- 若前端允许的最大长度不足以产生用例要求的省略效果，不得伪造数据或判定产品缺陷；记录实际长度、页面约束和验收结果，按 `blocked` 或 `test_case_error` 处理。
- 所有自造数据使用 `{test_data_prefix}{run_id}_` 前缀；非专属数据只读，禁止修改、审核、删除或清理。
- 造数或状态流转后必须刷新目标表格，等待表头、表体和加载遮罩稳定，再查找测试数据；旧的前端列表缓存不能作为验收证据。

## 公共执行稳定性与完整性补充

- 页面 readiness 不以 `networkidle` 单一条件判定；必须结合目标控件可见/可用、请求完成、弹窗稳定、表头/表体存在和业务数据可读。
- 查询条件、造数或状态变化后必须刷新目标表格并等待加载遮罩消失、表头和表体稳定；刷新前的旧缓存不得作为断言证据。
- Element Plus 分页点击前读取 `disabled`、`aria-disabled`、`is-disabled`；没有足够数据、合格长文本或可操作状态行时，只记录 `blocked/data_provisioning`。
- 表格右侧列断言前先滚动对应横向容器到最右侧；控件值用 `input_value()` 或属性读取，不能用整页 `inner_text()`。
- 每条用例的动作路径必须完整到达目标状态，且断言必须属于当前 `check_id`；未完成关键动作、只检查初始页或读错区域，不得创建 Bug。
- 结果交付前校验结果数量、数字用例 ID 的升序和唯一性、每条禅道 readback、截图 SHA-256、Allure 附件映射。外层超时或部分结果不得作为最终 RUN。

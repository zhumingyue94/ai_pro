# 禅道 `type` / `auto` 字段规则

## 定位

本规则约束禅道同步、显式 CSV/API 导入和后续自动化消费时的字段对齐。

## 字段来源

| 本地字段 | 禅道字段 | 含义 |
|---|---|---|
| `type` | `type` | 本地用例类型仅允许 `interface`、`feature`、`install`、`config`、`performance`、`security`；禁止使用 `unit`；禅道远程类型还可为映射值 `other` |
| `auto` | 本地选择字段 | 本地自动化候选标记，只允许字符串 `auto`、`no` |

本地 `type` 只允许 `interface`、`feature`、`install`、`config`、`performance`、`security`，禁止使用 `unit`。`negative`、`boundary`、`functional`、`data_consistency`、`permission`、`other` 等场景标签或禅道类型不得作为新的本地 `type`；异常、边界、权限和数据一致性按实际验证对象归类。纯元素展示、页面布局或视觉结果验证归为 `config`；交互、筛选、分页、弹窗、按钮状态、页面跳转、前端提示及页面状态变化归为 `feature`；明确调用或校验 API、请求响应或字段协议归为 `interface`。

本地 `auto` 字段不得使用布尔值 `true`/`false`、`manual`、`partial` 或 `blocked`。历史产物中的 `false`、`manual` 仅作为兼容读取，不得作为新用例生成值；汇总统计使用 `auto` 和 `no`。自动化适配的具体判定以 `automation-judgment-rule` 为准。非法本地 `type` 必须在校验、导出和远程写入前阻断，不得默认回退到 `feature`。

禅道同步阶段对完成真实回读的用例必须满足：

```text
local.auto == "auto"  => zentao.type == "other"
local.auto != "auto"  => zentao.type == local.type
```

`auto=auto` 只决定禅道类型为 `other`（其他），不写入关键词，也不写入禅道 `auto` 字段。

YAML 中的 `auto: no` 必须以字符串形式写入（例如 `auto: 'no'`），避免被 YAML 解析器当作布尔值 `false`。

## 可选 CSV 与同步

- `auto=auto`：CSV 继续使用原有“自动化测试”导出分支。
- `auto=no`：CSV 的“用例类型”按 `type` 映射为功能测试、接口测试等。
- CSV 不新增“自动化”列。
- 禅道 API 更新必须同时发送：

  ```json
  {"type": "<local.type>", "auto": "<local.auto>"}
  ```

## 适用环节

| 环节 | 要求 |
|---|---|
| CSV 导出 | 仅在用户或同步流程显式触发时读取当前 TC 的 `type` / `auto` |
| 禅道同步 | 发送并回读 `type`，并将真实编号写入 `module_case_map.json` |
| UI 自动化 | 只按 `auto=auto` 选择可执行候选 |

历史产物中的旧字段仅作为历史证据，不参与当前流程。

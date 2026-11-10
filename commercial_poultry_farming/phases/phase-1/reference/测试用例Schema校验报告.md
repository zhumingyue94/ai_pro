# 本地测试用例 Schema 校验报告

- 报告生成时间：`2026-08-25T10:43:48+08:00`
- Schema：`D:\05ui_pro\.agents/references\testcase.schema.json`
- 校验对象：7 个 `TC_REQ-*.yaml` 文件中的 `cases[]` 单个用例对象
- 本报告记录修正前分析与修正后结果；未访问禅道远程接口。

## 校验范围

| 文件 | 用例数 |
|---|---:|
| `TC_REQ-000.yaml` | 29 |
| `TC_REQ-002.yaml` | 38 |
| `TC_REQ-003.yaml` | 92 |
| `TC_REQ-004.yaml` | 106 |
| `TC_REQ-005.yaml` | 94 |
| `TC_REQ-006.yaml` | 43 |
| `TC_REQ-007.yaml` | 114 |
| 合计 | 516 |

## 修正前分析

| 指标 | 数量 |
|---|---:|
| 总用例 | 516 |
| 校验通过 | 22 |
| 校验不通过 | 494 |
| Schema 错误总数 | 1027 |

### 违规类型

| 规则 | 涉及用例数 | 说明 |
|---|---:|---|
| required | 16 | 16 条新增禅道用例缺少 tp_id、feature、trace |
| test_data.page_url type | 7 | 7 条新增用例 page_url=null，但原 Schema 要求非空字符串 |
| test_data project extensions | 487 | 487 条用例使用 module、zentao_module_id 或其他项目级 test_data 扩展字段 |
| trace.source_review | 478 | 478 条用例使用 Schema 未声明的 trace.source_review |

补充说明：同一用例可能同时违反多个规则，因此各规则数量不能相加得到不通过用例数。

## 修正内容

- Schema 增加当前项目实际使用的 `test_data` 扩展字段和 `trace.source_review`。
- `feature`、`trace.tp`、`test_data.page_url` 增加对来源未提供时 `null` 的支持。
- 16 条新增禅道用例补充 `tp_id: null`、`feature: null` 和带禅道快照来源的 `trace`。
- 未修改已有 500 条用例的业务字段、步骤、预期或数据契约。

## 修正后结果

- 校验用例：`516`
- 校验通过：`516`
- 校验不通过：`0`
- Schema 错误：`0`
- 预期：516 条全部通过；实际结果见上述统计生成时的校验输出。

## 16 条新增禅道用例的边界

以下用例的测试点编号、功能分类或页面地址不是禅道快照直接提供的信息，使用 `null` 或保留来源未提供状态，不作为已确认业务事实：

| 禅道编号 | 本地编号 | 缺失/待确认字段 |
|---:|---|---|
| 48793 | TC-004-104 | `tp_id=null`、`feature=null` |
| 48794 | TC-000-23 | `tp_id=null`、`feature=null`、`page_url=null` |
| 48795 | TC-000-24 | `tp_id=null`、`feature=null`、`page_url=null` |
| 48796 | TC-000-25 | `tp_id=null`、`feature=null`、`page_url=null` |
| 48797 | TC-000-26 | `tp_id=null`、`feature=null`、`page_url=null` |
| 48798 | TC-000-27 | `tp_id=null`、`feature=null`、`page_url=null` |
| 48807 | TC-000-28 | `tp_id=null`、`feature=null`、`page_url=null` |
| 48810 | TC-002-37 | `tp_id=null`、`feature=null` |
| 48811 | TC-002-38 | `tp_id=null`、`feature=null` |
| 48812 | TC-003-91 | `tp_id=null`、`feature=null` |
| 48813 | TC-003-92 | `tp_id=null`、`feature=null` |
| 48814 | TC-004-105 | `tp_id=null`、`feature=null` |
| 48815 | TC-004-106 | `tp_id=null`、`feature=null` |
| 48816 | TC-005-94 | `tp_id=null`、`feature=null` |
| 48863 | TC-007-114 | `tp_id=null`、`feature=null` |
| 49257 | TC-000-29 | `tp_id=null`、`feature=null`、`page_url=null` |

## 保护边界

- 未修改 `05_case_review/`。
- 未修改 `07_ui_automation/`。
- 未访问或写入禅道远程数据。

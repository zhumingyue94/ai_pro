<!-- 禅道状态由 module_case_map.json 统一管理；新建映射记录默认 zentao_status=normal。本源模板不填写该字段。 -->
# 测试用例 — {module} ({req_id})

- 用例数：**{case_count}**
- 需求编号：{req_id}
- 测试计划：{tp_id}
- 版本：{version}
- 追溯状态：{trace_status}
- 来源评审：{source_review}

## 覆盖与审核信息

- 模块：{module}
- 需求：{req_id}
- 测试计划：{tp_id}
- 页面/入口：{page_url}
- 覆盖范围：{coverage_summary}
- 审核结论：{review_conclusion}

## {case_id} / {tp_case_id} [{priority}] auto={auto}

**标题**: {title}

**原子测试目的**: {atomic_purpose_id}

**状态/条件分支**: {scenario_branch}

**auto**: {auto}

**type**: {type}

**功能**: {feature}

**追溯**: 需求={req_id}；测试计划={tp_case_id}；项目={project}；版本={version}；状态={trace_status}

<!-- 仅当用例存在 common_preconditions_ref 时渲染下一行；无引用时删除该行。 -->
**公共前置引用**: `{common_preconditions_ref}`

**前置条件**:

- {precondition_1}
- {precondition_2}

**步骤**:

1. {action_1}
   - 预期：{expected_result_1}
2. {action_2}
   - 预期：{expected_result_2}

<!-- 复制以上“单条用例”区块，为每条用例使用独立的二级标题；按实际步骤数量增删步骤和前置条件。 -->

## 结论

- 用例交付状态：{delivery_status}
- 未覆盖项/待确认项：{open_items}
- 备注：{remark}

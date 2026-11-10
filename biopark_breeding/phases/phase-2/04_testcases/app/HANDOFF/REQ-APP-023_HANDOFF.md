# REQ-APP-023 用例交接

- 规则标识：`test-design-enrichment-rule`、`page-block-coverage-rule`、`automation-judgment-rule`
- 来源评审：`REV_CASE_REQ-APP-023`
- 检查范围：按评审门禁返工 YAML/Markdown，未改分析或测试计划正文
- 设计修复：已补齐 automation_evaluation；修正 summary.auto_counts；为记录页操作补列表进入步骤；按参考区间重标定级；将 `TC-APP-023-003` 的复合预期拆分为发货单号、累计发货数量和记录数量三个步骤。
- 统计：20 条；auto=auto 20；P1=4 / P2=10 / P3=6 / P4=0。
- 公共前置：`app_shipment_records_access`（三步：打开小程序并登录、切换到正确孵化场；点击「雏苗发货」入口进入列表；在目标发货单卡片点击「记录」进入发货记录页并确认当前发货单上下文）；正常用例引用，权限异常用例 `TC-APP-023-019` 保留独立异常触发链路，不引用成功页面公共前置。
- 本次变更：删除 `TC-APP-023-022`（禅道 51371），同步移除注册表关联；已同步公共前置展示和引用策略。
- Markdown：已由 `scripts/render_testcase_markdown.py` 派生，并通过 `scripts/validate_testcase_markdown.py`；顶部展示 `app_shipment_records_access` 的三步公共前置，权限异常用例不展示成功页面公共前置引用。
- 自动化判定：已通过 `scripts/validate_automation_judgment.py`
- 未执行真实 UI、未生成 CSV、未写入禅道
- Next Agent: stage-case-review-agent

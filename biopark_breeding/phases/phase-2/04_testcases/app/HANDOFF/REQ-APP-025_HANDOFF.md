# REQ-APP-025 HANDOFF

- 当前状态：ready_for_revalidation
- 当前用例数：19（feature 2，interface 17；auto 候选 19，均 blocked）
- 公共前置：`app_inventory_records_access`；正常记录查询用例引用；重复确认、失败回滚、关联缺失、权限和补偿重试等异常链路保留独立触发步骤，不引用成功访问公共前置。
- 业务契约：业务单据幂等；库存不足整单失败；关联数据缺失整单失败；任一步骤失败事务回滚。
- 数据准备与清理：测试人员负责。
- 历史问题：保留为历史摘要，当前事实以最终 YAML、Markdown 和本地映射为准。

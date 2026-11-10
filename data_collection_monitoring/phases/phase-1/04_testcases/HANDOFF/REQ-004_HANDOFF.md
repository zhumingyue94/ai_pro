# REQ-004 测试用例整改 HANDOFF

- 模块：设备分组；禅道模块 `733`；项目 `46`；产品 `8`。
- 用例数量：**34**；统计：P1 11、P2 9、P3 14、P4 0；auto 27、手工 7。
- YAML：`04_testcases/TC_REQ-004.yaml`；Markdown：`04_testcases/TC_REQ-004.md`。
- 状态：`design_validated_remote_sync_validated`；禅道 17 条类型更新已逐条回读通过；UI/Playwright 未执行。

## 2026-11-02 更新

按步骤拆分建议更新现有 34 条用例的标题、步骤和预期，未新增、删除或重编号；公共前置、优先级、追溯和原子目的保持不变。Markdown 从 YAML 重新生成；模板、Markdown 一致性、原子性校验通过。

后续禅道同步必须按 `zentao_case_id` 逐条原位更新并立即回读；回读通过后才更新注册表，失败即停止，禁止删除重建。

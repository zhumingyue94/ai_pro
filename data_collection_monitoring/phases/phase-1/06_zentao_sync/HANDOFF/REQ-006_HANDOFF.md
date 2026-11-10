# REQ-006 禅道同步 HANDOFF

- 模块：插件管理；禅道模块 `744`；项目 `46`；产品 `8`。
- 本次操作：删除 `TC-REQ-006-040`→`51802`、`TC-REQ-006-053`→`51815`。
- 本地来源：`04_testcases/TC_REQ-006.yaml`；Markdown：`04_testcases/TC_REQ-006.md`；评审：`05_case_review/REV_CASE_REQ-006.yaml`。
- 本地用例数量：**33**；统计：P1 9、P2 8、P3 16、P4 0；auto 29、手工 4。
- 执行方式：公共同步脚本真实删除，逐条串行处理并立即回读。
- 结果：51802、51815 删除响应成功，回读均为 `confirmed_not_found`；未删除后重建，未更新其他用例。
- 详细日志：`06_zentao_sync/REQ-006/deletion_51802_51815_20261109.json`。
- 注册表：唯一 `module_case_map.json` 已移除两个来源编号，`source_case_count` 已更新为 33；YAML/Markdown/注册表 ID 集合一致；仅在删除及回读校验通过后更新。
- 来源哈希：YAML `a1738d799634f672cf4d97ec63bdcb5e74bb61eea3b4478c7d8ee1e9e929b450`；Markdown `308ac26024289d66aea5e40422544bd718d56107749971897ddd9f7100458a56`。
- 后续：如继续同步其他用例，必须先核对稳定 `zentao_case_id`，更新失败立即停止，不得降级为删除重建。

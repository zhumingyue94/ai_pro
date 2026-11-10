# 用例评审 — REQ-014

- **gate_passed**: `False`（内容同步后待重新评审）
- **评审状态**: `stale`
- **当前 TC 来源 SHA-256**: `3e5906ae4ef9f929e1c0cc5fcabbc88e684440878f41a4ac2469a6190d7fefdf`
- **errors**: 0
- **shell rewrite**: masterdata empty-shell/mismatch cleared (see rewrite_masterdata_shells.log)
- **warnings**: 2
- **csv_path**: None（历史 CSV 已删除且不作为当前有效产物）

## Issues

- （无）
## 2026-08-13 type/auto 全量同步复核

- Evidence status: original ZenTao evidence deleted during cleanup; unavailable for review.
- 范围：847 条已有真实禅道编号的本地用例。
- 规则：`local.type=zentao.type`、`local.auto=zentao.auto`。
- 不执行本地自动化适配性判定；5 条 pending 用例不猜测禅道字段。
- 本次只更新字段和来源哈希，不修改步骤、预期、测试点或禅道远程数据。

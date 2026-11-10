# 用例评审 — REQ-006

- **gate_passed**: `False`（内容同步后待重新评审）
- **评审状态**: `stale`
- **当前 TC 来源 SHA-256**: `97452344a2cd7b3ae72576fd4c565e5725624568aa313cc763c6da0d423c54dd`
- **errors**: 0
- **warnings**: 0
- **csv_path**: None（历史 CSV 已删除且不作为当前有效产物）

## Issues

- （无）
## 2026-08-13 type/auto 全量同步复核

- Evidence status: original ZenTao evidence deleted during cleanup; unavailable for review.
- 范围：847 条已有真实禅道编号的本地用例。
- 规则：`local.type=zentao.type`、`local.auto=zentao.auto`。
- 不执行本地自动化适配性判定；5 条 pending 用例不猜测禅道字段。
- 本次只更新字段和来源哈希，不修改步骤、预期、测试点或禅道远程数据。

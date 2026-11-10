# 用例评审 — REQ-005

- **gate_passed** (模块): `False`（内容同步后待重新评审）
- **评审状态**: `stale`
- **当前 CSV**: 无；历史 `05_case_review/005_排程审批_测试用例.csv` 已删除且不作为当前有效产物
- **当前 TC 来源 SHA-256**: `f121022500303489f9b0c65299074fd3a40b4ec9e4003345287316c6372dd1e9`
- **delta_passed** (变动集): `True`
- **delta_review_note**: 2026-07-22 增量用例评审 2 条；delta_passed=True；模块 gate 保持 True（未全量复评）

## 增量评审（变动用例）

- 日期: 2026-07-22
- 范围: 2 条

| case_id | verdict | errors | warnings |
|---------|---------|--------|----------|
| TC-005-67 | pass | 0 | 0 |
| TC-005-68 | pass | 0 | 0 |

## Issues（变动集）

- （无 error）

## 模块级 Issues（历史）

- （无）

## 2026-08-13 ZenTao auto type sync

- Evidence status: original ZenTao evidence deleted during cleanup; unavailable for review.
- Rule: type=auto -> auto=auto/type=auto; type=feature -> auto=no/type=feature.
- Local auto suitability assessment: not performed.

| case_id | ZenTao ID | type/auto | auto | type | status |
|---|---:|---|---|---|---|
| TC-005-23 | 47904 | auto/auto | auto | auto | synced_by_zentao_type |
| TC-005-78 | 47959 | feature/no | no | feature | synced_by_zentao_type |

- Reviewed: 2 cases; type_source_conflict: 0.
- No ZenTao remote write, UI execution, or destructive data operation performed.
## 2026-08-13 type/auto 全量同步复核

- Evidence status: original ZenTao evidence deleted during cleanup; unavailable for review.
- 范围：847 条已有真实禅道编号的本地用例。
- 规则：`local.type=zentao.type`、`local.auto=zentao.auto`。
- 不执行本地自动化适配性判定；5 条 pending 用例不猜测禅道字段。
- 本次只更新字段和来源哈希，不修改步骤、预期、测试点或禅道远程数据。

# 用例评审 — REQ-000

- **gate_passed** (模块): `False`（内容同步后待重新评审）
- **评审状态**: `stale`
- **当前 CSV**: 无；历史 `05_case_review/000_系统总览_测试用例.csv` 已删除且不作为当前有效产物
- **当前 TC 来源 SHA-256**: `8043ba2237abe53f02a7bc8e0144470458a698087224a14ae74aff2899a2b985`
- **delta_passed** (变动集): `True`
- **delta_review_note**: 2026-07-23 增量用例评审 40 条；delta_passed=True；模块 gate 保持 True（未全量复评）

## 增量评审（变动用例）

- 日期: 2026-07-23
- 范围: 40 条

| case_id | verdict | errors | warnings |
|---------|---------|--------|----------|
| TC-000-17 | pass | 0 | 0 |
| TC-000-18 | pass | 0 | 0 |
| TC-000-19 | pass | 0 | 0 |
| TC-000-20 | pass | 0 | 0 |
| TC-000-21 | pass | 0 | 0 |
| TC-000-22 | pass | 0 | 0 |
| TC-000-23 | pass | 0 | 0 |
| TC-000-24 | pass | 0 | 0 |
| TC-000-25 | pass | 0 | 0 |
| TC-000-26 | pass | 0 | 0 |
| TC-000-27 | pass | 0 | 0 |
| TC-000-28 | pass | 0 | 0 |
| TC-000-29 | pass | 0 | 0 |
| TC-000-30 | pass | 0 | 0 |
| TC-000-31 | pass | 0 | 0 |
| TC-000-32 | pass | 0 | 0 |
| TC-000-33 | pass | 0 | 0 |
| TC-000-34 | pass | 0 | 0 |
| TC-000-35 | pass | 0 | 0 |
| TC-000-36 | pass | 0 | 0 |
| TC-000-37 | pass | 0 | 0 |
| TC-000-38 | pass | 0 | 0 |
| TC-000-39 | pass | 0 | 0 |
| TC-000-40 | pass | 0 | 0 |
| TC-000-41 | pass | 0 | 0 |
| TC-000-42 | pass | 0 | 0 |
| TC-000-43 | pass | 0 | 0 |
| TC-000-44 | pass | 0 | 0 |
| TC-000-45 | pass | 0 | 0 |
| TC-000-46 | pass | 0 | 0 |
| TC-000-47 | pass | 0 | 0 |
| TC-000-48 | pass | 0 | 0 |
| TC-000-49 | pass | 0 | 0 |
| TC-000-50 | pass | 0 | 0 |
| TC-000-51 | pass | 0 | 0 |
| TC-000-52 | pass | 0 | 0 |
| TC-000-53 | pass | 0 | 0 |
| TC-000-54 | pass | 0 | 0 |
| TC-000-55 | pass | 0 | 0 |
| TC-000-56 | pass | 0 | 0 |

## Issues（变动集）

- （无 error）

## 模块级 Issues（历史）

- （无）

## 2026-08-13 禅道缺失用例增量评审

- Evidence status: original ZenTao evidence deleted during cleanup; unavailable for review.
- 范围：8 条；禅道 type/auto 无冲突；不执行本地自动化适配性评估。

| case_id | ZenTao ID | type/auto | auto | type | verdict |
|---|---:|---|---|---|---|
| TC-000-57 | 48799 | feature/no | no | feature | pass |
| TC-000-58 | 48800 | feature/no | no | feature | pass |
| TC-000-59 | 48801 | feature/no | no | feature | pass |
| TC-000-60 | 48802 | feature/no | no | feature | pass |
| TC-000-61 | 48803 | feature/no | no | feature | pass |
| TC-000-62 | 48804 | feature/no | no | feature | pass |
| TC-000-63 | 48805 | feature/no | no | feature | pass |
| TC-000-64 | 48806 | feature/no | no | feature | pass |

- 破坏性删除/停用/用户删除未执行；相关用例保留管理员预置前置条件。
- 旧 CSV 不作为本轮评审结果输入。

## 2026-08-13 ZenTao auto type sync

- Evidence status: original ZenTao evidence deleted during cleanup; unavailable for review.
- Rule: type=auto -> auto=auto/type=auto; type=feature -> auto=no/type=feature.
- Local auto suitability assessment: not performed.

| case_id | ZenTao ID | type/auto | auto | type | status |
|---|---:|---|---|---|---|
| TC-000-05 | 48019 | interface/no | auto | feature | type_source_conflict |
| TC-000-16 | 48030 | feature/no | no | feature | synced_by_zentao_type |

- Reviewed: 2 cases; type_source_conflict: 1.
- No ZenTao remote write, UI execution, or destructive data operation performed.
## 2026-08-13 type/auto 全量同步复核

- Evidence status: original ZenTao evidence deleted during cleanup; unavailable for review.
- 范围：847 条已有真实禅道编号的本地用例。
- 规则：`local.type=zentao.type`、`local.auto=zentao.auto`。
- 不执行本地自动化适配性判定；5 条 pending 用例不猜测禅道字段。
- 本次只更新字段和来源哈希，不修改步骤、预期、测试点或禅道远程数据。

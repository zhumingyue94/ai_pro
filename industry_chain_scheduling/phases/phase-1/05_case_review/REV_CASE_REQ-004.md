# 用例评审 — REQ-004

- **gate_passed**: `true`（内容同步后待重新评审）
- **评审状态**: `stale`
- **当前 TC 来源 SHA-256**: `5d7ddeda128da6147e238de3ea4e621f24f43d70c03d1818044878849ac96a22`
- **errors**: 0
- **warnings**: 46
- **csv_path**: None（原测试用例 CSV 已按项目清理计划删除）

## Issues

- （无）

## 下一步

当前评审因用例内容同步已失效，需重新执行。**历史 CSV 不作为当前有效产物**。
本轮不执行自动化筛选、CSV 生成或禅道远程写入；自动化字段已按禅道详情同步。

## 2026-08-13 禅道缺失用例增量评审

- Evidence status: original ZenTao evidence deleted during cleanup; unavailable for review.
- 范围：13 条；禅道 type/auto 无冲突；不执行本地自动化适配性评估。

| case_id | ZenTao ID | type/auto | auto | type | verdict |
|---|---:|---|---|---|---|
| TC-004-215 | 48784 | auto/auto | auto | auto | pass |
| TC-004-216 | 48785 | auto/auto | auto | auto | pass |
| TC-004-217 | 48786 | auto/auto | auto | auto | pass |
| TC-004-218 | 48787 | auto/auto | auto | auto | pass |
| TC-004-219 | 48788 | auto/auto | auto | auto | pass |
| TC-004-220 | 48789 | auto/auto | auto | auto | pass |
| TC-004-221 | 48790 | auto/auto | auto | auto | pass |
| TC-004-222 | 48791 | auto/auto | auto | auto | pass |
| TC-004-223 | 48864 | auto/auto | auto | auto | pass |
| TC-004-224 | 48865 | auto/auto | auto | auto | pass |
| TC-004-225 | 49111 | auto/auto | auto | auto | pass |
| TC-004-226 | 49112 | feature/no | no | feature | pass |
| TC-004-227 | 49114 | feature/no | no | feature | pass |

- 破坏性删除/停用/用户删除未执行；相关用例保留管理员预置前置条件。
- 旧 CSV 不作为本轮评审结果输入。

## 2026-08-13 ZenTao auto type sync

- Evidence status: original ZenTao evidence deleted during cleanup; unavailable for review.
- Rule: type=auto -> auto=auto/type=auto; type=feature -> auto=no/type=feature.
- Local auto suitability assessment: not performed.

| case_id | ZenTao ID | type/auto | auto | type | status |
|---|---:|---|---|---|---|
| TC-004-46 | 47763 | feature/no | no | feature | synced_by_zentao_type |
| TC-004-64 | 47781 | feature/no | no | feature | synced_by_zentao_type |
| TC-004-70 | 47787 | feature/no | no | feature | synced_by_zentao_type |
| TC-004-166 | 48818 | auto/auto | auto | auto | synced_by_zentao_type |
| TC-004-167 | 48819 | auto/auto | auto | auto | synced_by_zentao_type |
| TC-004-169 | 48821 | auto/auto | auto | auto | synced_by_zentao_type |
| TC-004-177 | 48828 | auto/auto | auto | auto | synced_by_zentao_type |
| TC-004-208 | 48859 | auto/auto | auto | auto | synced_by_zentao_type |
| TC-004-176 | 48861 | auto/auto | auto | auto | synced_by_zentao_type |

- Reviewed: 9 cases; type_source_conflict: 0.
- No ZenTao remote write, UI execution, or destructive data operation performed.
## 2026-08-13 type/auto 全量同步复核

- Evidence status: original ZenTao evidence deleted during cleanup; unavailable for review.
- 范围：847 条已有真实禅道编号的本地用例。
- 规则：`local.type=zentao.type`、`local.auto=zentao.auto`。
- 不执行本地自动化适配性判定；5 条 pending 用例不猜测禅道字段。
- 本次只更新字段和来源哈希，不修改步骤、预期、测试点或禅道远程数据。

## 2026-08-19 禅道存在但本地缺失用例增量评审

- Evidence status: original ZenTao evidence deleted during cleanup; unavailable for review.
- 范围：5 条；禅道 `type/auto` 无冲突；不执行本地自动化适配性评估。

| case_id | ZenTao ID | type/auto | verdict |
|---|---:|---|---|
| TC-004-228 | 49115 | auto/auto | pass |
| TC-004-229 | 49116 | auto/auto | pass |
| TC-004-230 | 49117 | auto/auto | pass |
| TC-004-231 | 49118 | auto/auto | pass |
| TC-004-232 | 49119 | auto/auto | pass |

- 新增映射登记为 `registered`，自动化实现状态保持 `pending_implementation`。
- 未执行禅道远程写入、UI 自动化或破坏性数据操作。

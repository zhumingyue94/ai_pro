# REQ-APP-021 评审交接

- 2026-10-14 删除禅道 `50942` 对应本地用例 `TC-APP-021-020`，已从源 YAML、Markdown、评审记录和注册表移除，禅道回读确认不存在。

## 交接标识

- `module_id`：`REQ-APP-021`
- `req_id`：`REQ-APP-021`
- `review_id`：`REV_CASE_REQ-APP-021`
- `agent`：`case-review-agent`
- `mode`：`report_only`
- `status`：`completed_with_observations`
- `gate_passed`：是

## 本轮单一职责拆分（2026-09-23）

- 依据 `职责检查.md` 第 4 节，删除 8 条复合职责用例：`TC-APP-021-025`、`TC-APP-021-031`、`TC-APP-021-032`、`TC-APP-021-050`、`TC-APP-021-057`、`TC-APP-021-060`、`TC-APP-021-069`、`TC-APP-021-070`。
- 新增 24 条拆分用例：`TC-APP-021-074`～`TC-APP-021-097`，逐条建立 `priority_review.items`（`result: split_added`）。
- 历史中间状态曾为 82 条；当前全量评审范围为 80 条，P1/P2/P3/P4 为 **24/25/25/6**。
- 排序方向相关用例 `TC-APP-021-076`～`TC-APP-021-080` 仍列入 `unconfirmed_items`，证据状态为 `evidence_risk`。
- 本次合并：禅道 `50986`、`50987`、`50988` 合并保留 `50987`；本地删除 `TC-APP-021-081`、`TC-APP-021-083`，保留用例覆盖列表空状态及各状态统计值为 0。
- 本次删除：禅道 `50984`、`50985` 对应本地 `TC-APP-021-079`、`TC-APP-021-080` 已从 YAML、Markdown、评审和注册表移除。
- 本次删除：禅道 `51007` 对应本地 `TC-APP-021-103`，保留 `50991` 对应 `TC-APP-021-086`，已从 YAML、Markdown、评审和注册表移除。
- 本次删除：禅道 `50944`、`50978` 对应本地 `TC-APP-021-022`、`TC-APP-021-073`，已同步从 YAML、Markdown、评审和注册表移除。
- 本次更新：`TC-APP-021-105` / 禅道 `51010` 补充进入雏苗发货列表的独立步骤，形成 4 步操作链。
- `TC-APP-021-091` / 禅道 `50995`、`TC-APP-021-092` / 禅道 `50996`、`TC-APP-021-093` / 禅道 `50997` 已移除步骤和期望中的关键字搜索，仅保留日期、栋舍、状态三项组合筛选，并纳入禅道同步。

## 本轮单一职责拆分（第 2 轮，2026-09-23）

- 依据 `职责检查.md` 第 4 节，删除 3 条复合职责用例：`TC-APP-021-030`、`TC-APP-021-051`、`TC-APP-021-087`。
- 新增 7 条拆分用例：`TC-APP-021-098`～`TC-APP-021-104`，逐条建立 `priority_review.items`（`result: split_added`）。
- 全量评审范围调整为 83 条；P1/P2/P3/P4 为 **25/24/26/8**。
- 拆分映射：

| 原用例 | 拆分后用例 |
|---|---|
| `TC-APP-021-030` | `TC-APP-021-098`、`TC-APP-021-099` |
| `TC-APP-021-051` | `TC-APP-021-100`、`TC-APP-021-101` |
| `TC-APP-021-087` | `TC-APP-021-102`、`TC-APP-021-103`、`TC-APP-021-104` |

- `TC-APP-021-087` 拆分后的数量边界用例移除与 `TC-APP-021-085` 重复的“未出雏不计入实际可发数”断言。
- `module_case_map.json`：删除 `TC-APP-021-030`、`TC-APP-021-051`、`TC-APP-021-087` 关联，新增 `TC-APP-021-098`～`TC-APP-021-104` 共 7 条 `pending_registry` 记录（`zentao_case_id` 为 null）。
- 历史禅道用例 `50009`（原 `TC-APP-021-030`）和 `50030`（原 `TC-APP-021-051`）本轮未在禅道侧删除或更新，需后续单独处理。
- 拆分用例本轮仅更新本地评审资产，远程禅道同步未执行。

## 本轮职责重叠处理（2026-09-23）

- 删除重复用例：`TC-APP-021-038`、`TC-APP-021-046`、`TC-APP-021-047`、`TC-APP-021-048`、`TC-APP-021-049`、`TC-APP-021-062`、`TC-APP-021-063`。
- 本轮仅更新本地评审和交付材料，远程禅道同步未执行。

## 本轮职责重叠收窄（2026-09-23）

- `TC-APP-021-052` 已收窄为指定栋舍无发货数据时列表显示空状态，筛选条件职责由 `TC-APP-021-005` 等基线用例承担。
- `TC-APP-021-098` 已收窄为发货中卡片发货入口展示与可操作性，导航与上下文由 `TC-APP-021-058`（任意发货单点击发货）承担。
- `TC-APP-021-099` 已收窄为发货中卡片记录入口展示与可操作性，导航由 `TC-APP-021-090` 承担。
- `TC-APP-021-059` 与 `TC-APP-021-058` 的点击发货导航职责重复，已删除 059；发货中场景并入 058 的合法数据分支。
- 收窄不新增其他相似用例；当前无未处理的非单一职责用例。

## 逐条优先级复核摘要

- YAML 已补充 83 条逐条 `priority_review.items`。
- 每条记录覆盖核心流程阻断、关键数据影响、业务影响区域、使用频率、替代路径、失败后果、追溯和证据状态。
- 源/复核分布为 P1/P2/P3/P4 = 25/24/26/8。
- 原有 `open_evidence` 用例仍标记为 `unconfirmed_evidence_risk`，下游不得视为定级证据完备。

## 结论

- 全量评审 83 条用例，ID `001..104` 唯一但不连续（累计删除 12 条复合职责用例并新增 31 条拆分用例）；P1/P2/P3/P4 为 **25/24/26/8**。
- 系统化设计、静态 Pairwise、Playwright Python、有头页面、Casely 结构和交付格式均已完成静态评审；存在执行准备与证据观察项。
- 83 条为自动化候选，当前可执行 0 条；未执行 Playwright、浏览器、有头页面或 PICT。
- 主要待办：正式路由和 locator、状态统计/列表接口口径、外部签收来源、权限/数据环境、部分 `tp/tp_id` 追溯。

## 同步清单

- [x] 本地评审 YAML
- [x] 本地评审 Markdown
- [x] REQ-ID 专属 HANDOFF
- [x] 来源 SHA-256
- [ ] 远程禅道同步：未执行（本次职责收窄涉及 3 条用例，不进入同步；历史拆分用例仍按既有待办处理）
- [ ] CSV：未生成
- [ ] UI/浏览器/Playwright：未执行
- [ ] PICT：未运行
- [ ] 测试点/XMind：未读取或生成

## 交付文件

- `05_case_review/app/REV_CASE_REQ-APP-021.yaml`
- `05_case_review/app/REV_CASE_REQ-APP-021.md`
- `05_case_review/app/HANDOFF/REQ-APP-021_HANDOFF.md`

## 来源哈希

| 来源 | SHA-256 |
|---|---|
| `04_testcases/app/TC_REQ-APP-021.yaml` | `171c3019b4548d301e142c58d30739cfcdea39763fee52ba080bd469204daf25` |
| `04_testcases/app/TC_REQ-APP-021.md` | `fbcf79ed9667a8a9fea30fe4db57d954e51fdcf22e99eac0fd40b4c6f740c98a` |
| `02_analysis/app/REQ-APP-021.yaml` | `c2636ae8eea22a0189c4f314e692962157de566cc83c41a06557ba225d85825d` |
| `03_test_plan/app/TEST_PLAN_REQ-APP-021.yaml` | `b21d17a2503c038d2f185ae6ec01e3777f2c9c0edccf2eb415b6206f372d36a8` |
| `02_analysis/app/page_inventory/page.json` | `e108ca702f037f88fcb943b8d1ffa26c43e12139fe20e6b6847957d9e5265112` |

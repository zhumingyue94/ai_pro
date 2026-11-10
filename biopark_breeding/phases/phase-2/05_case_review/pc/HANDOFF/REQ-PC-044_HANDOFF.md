# REQ-PC-044 用例评审交接

## 2026-10-14 导航文案修订

- 仅更新公共前置 `delivery_export_page` 的 action：明确“在左侧菜单中展开「计划管理」”，并将“雏苗发货”明确为“菜单项”。
- REQ-PC-044 当前 YAML 未包含上孵计划列表、库存管理、库存查询、出入库记录或孵化需求目标文案；未修改表格描述及其他字段。
- YAML/Markdown 已重新生成并通过对齐校验；模板校验保留既有 `common_preconditions.conditions` 结构问题。
- 来源哈希：YAML `e0e669308bdaea864b153acc7c7106d42e2863e8a8edf0aa792443b894497d98`；Markdown `15eb72ad17cb5bdbeb2e1b5a3000c8f99c75ac24fd7f3fd4ad9142aafddfb796`。
- 禅道同步：已真实更新 19 条受公共前置影响的已登记用例并逐条回读校验通过；注册表映射有效，模块 `739` 未改变。

- 模块 ID（当前 REQ-ID）：`REQ-PC-044`
- 需求：`REQ-PC-044`（雏苗发货导出）
- 评审 ID：`REV_CASE-REQ-PC-044`
- 代理：`case-review-agent`
- 模式：`report_only`
- 门禁：**通过（带观察项）**

## 结果汇总

- 用例数：20（当前 ID 为 `TC-PC-044-002`~`TC-PC-044-023`，已删除 001、011、013、024、025、026）
- 覆盖：`FR-044-01`~`FR-044-07`
- 结构/字段完整性：通过
- YAML↔MD 对齐：20/20，通过
- 页面引用：入口、列表、筛选、状态卡和已采集状态可追溯
- 自动化：20 条 `decision=auto`、`status=blocked`
- 公共前置：`delivery_export_page`；正常场景引用，`TC-PC-044-010` 无导出权限异常场景保留独立访问步骤。
- 未执行：UI 测试、Playwright、Pairwise 运行、远程同步

## 问题与风险

1. `PI-044-02~23`、`AP-044-02~23` 在测试计划/分析文件中没有注册项；`FR-044-*` 可追溯。
2. 确认提示为原生 `confirm`，`page.json` 未单独采集确认框；下载成功状态也无独立证据。
3. 正式数据、权限、环境、受控下载目录和清理责任未齐备。
4. `TC-PC-044-022`~`023` 的日期端点、单侧日期契约待确认，保持 blocked。

## 同步清单

- [ ] 补充 PI/AP 注册或修正引用。
- [ ] 准备正式 URL、授权账号、脱敏数据、下载目录及清理责任。
- [ ] 确认原生确认框与下载回读契约。
- [ ] 需求确认后解除 022~023 的 blocked。
- [ ] report_only：不得写入远程禅道、生成 CSV 或伪造 Execute/导入成功。

## 来源哈希

- `04_testcases/pc/TC_REQ-PC-044.yaml`：`c7218fda4cac68b68c02cc925082530d378d3e5944b33e112d47bc7c98aeb913`
- `04_testcases/pc/TC_REQ-PC-044.md`：`e3797c4a0144ad890c671e3c77079decfd124c0836b52f302c3b11651eb0537a`
- `02_analysis/pc/REQ-PC-044.yaml`：`f26083102fd54a746e948e470c8ec4f67a751972d2c795067a790e89cdd6c568`
- `03_test_plan/pc/TEST_PLAN_REQ-PC-044.yaml`：`04fb2b258373c53a9fa7e1a3a883195c029ab9ca2d5485a115db773dda895f76`
- `02_analysis/pc/page_inventory/page.json`：`2d1ee96de735f18ec1d4073f47e818179201051059da6a22ed41ccef7b830c7d`

## 产出文件

- `05_case_review/pc/REV_CASE_REQ-PC-044.yaml`
- `05_case_review/pc/REV_CASE_REQ-PC-044.md`
- `05_case_review/pc/HANDOFF/REQ-PC-044_HANDOFF.md`

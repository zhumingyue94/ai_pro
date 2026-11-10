# REQ-008 禅道同步 HANDOFF

- 模块：数据推送；禅道模块 `746`；项目 `46`；产品 `8`。
- 本轮目标：`TC-REQ-008-044`、`045`、`046`、`050`、`052`、`053`、`054`、`055`。
- 稳定禅道映射：`51866`、`51867`、`51868`、`51872`、`51874`、`51875`、`51876`、`51877`。
- 本地变更：上述 8 条用例 `auto: no` → `auto: auto`；权限/租户用例 `028`、`047`、`048` 保持 `auto: no`。
- 本地统计：总数 **49**；auto **46**；手工 **3**。

## 2026-11-03 同步结果

按真实同步模式调用 `scripts/zentao_create_testcase.py`，目标为项目 `46`、产品 `8`、模块 `746`，操作类型为现有用例原位 `update`。

同步在远程写入前被阻止：`01_requirements/禅道模块id.md` 缺失。根据同步规则，首条 `TC-REQ-008-044` 失败后停止后续同步，未删除、重建或创建替代用例，未执行远程回读，也未更新未经验证的注册表字段。

证据文件：

- `REQ-008/sync_plan_20261103_auto_corrections.json`
- `REQ-008/sync_log_20261103_auto_corrections.json`
- `REQ-008/readback_20261103_auto_corrections.json`
- `REQ-008/source_hashes_20261103_auto_corrections.json`

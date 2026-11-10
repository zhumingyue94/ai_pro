# 06_zentao_sync Handoff Report

## 当前状态

- `module_case_map.json`：由当前项目 `04_testcases/TC_*.yaml` 本地生成。
- 注册用例数：824。
- 禅道用例 ID：824 个，数字格式且无重复。
- 当前项目远程写入：未执行。
- 当前项目远程回读：未执行；本目录中的历史日志仅作为旧项目证据。
- 自动化映射：全部为 `pending_implementation`，没有虚构 handler、Page Object 或执行结果。

## 来源与边界

- 用例来源：`04_testcases/TC_*.yaml`。
- 评审来源：`05_case_review/REV_CASE_*.yaml`，当前 11 个评审文件均为 `gate_passed: true`。
- 模块来源：`01_requirements/禅道模块id.md`。
- 历史同步来源：`history/`，来自 `产业链生产排程系统_old/06_zentao_sync/`。
- 历史证据不等于本项目当前运行结果，不用于证明当前禅道状态仍未变化。

## 脚本入口

当前可执行的项目级适配器仅保留公共入口包装器：

```powershell
python 06_zentao_sync/update_zentao_from_tc.py --req REQ-003 --dry-run
```

以下历史命令已废弃，脚本文件已移除，不得重新执行：

```text
import_testcases.py
sync_zentao_case_types.py
migrate_zentao_modules.py
verify_zentao_type_auto.py
```

远程操作必须显式使用对应的 `--execute`，并从进程环境读取
`ZENTAO_URL`、`ZENTAO_ACCOUNT`、`ZENTAO_PASSWORD`。脚本不会把凭据写入仓库、日志或报告。

## 下一步

如需再次确认禅道远程状态，应先执行只读回读并保留新的 RUN/日志；如需新增或修改远程用例，
必须在用户明确授权后执行，并保存逐条结果与回读证据。

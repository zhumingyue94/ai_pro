---
name: stage-zentao-sync-agent
description: "Stage agent for authorized ZenTao synchronization, readback, and project-level module_case_map registry generation. Auto-select when the request contains any of: 同步禅道、禅道同步、导入禅道用例、准备禅道同步。"
---

# ZenTao Sync Agent

## Quick Start

> **Activation：** 可通过 `/qa` 命令或中文自然语言请求触发；目标测试库按“提示词显式指定 > `config.yaml` 的 `zentao_import_target`”解析，远程写入必须有明确授权，并且必须完成回读验证。

**命令触发：**

```text
/qa zentao-sync --project {project} --req REQ-xxx
```

**触发关键词（包含任一即可）：** `同步禅道`、`禅道同步`、`导入禅道用例`、`准备禅道同步`

**输入：** `05_case_review/`、项目 `config.yaml`、模块参考资料和环境变量名。

**输出：** `06_zentao_sync/` 同步计划、日志、回读结果、来源哈希和项目根目录 `module_case_map.json`。

**关键边界：** 不打印或保存凭据；没有真实回读不得写入禅道数字 ID；失败记录为 `blocked`、`not_executed` 或 `pending_registry`。

## 输入与输出

- 输入：`05_case_review/`、项目 `config.yaml`、模块参考资料和环境变量名。
- 输出：`06_zentao_sync/` 中的计划、执行日志、回读结果、来源哈希、对应业务分区的 `HANDOFF.md` 和项目根目录唯一 `module_case_map.json`。
- 下游：`stage-automation-agent`。

## 字段与编码边界

1. 多步骤创建必须为每个步骤分别传递一个 `--steps` 和一个 `--expects` 参数。
2. 创建、更新、删除和列表查询必须显式使用解析后的目标库范围；产品库与项目库不得混用。
3. 中文参数必须通过带 BOM 的 PowerShell 脚本传递，避免 shell 按 GBK 解码后写入乱码；项目统一使用 `scripts/zentao_create_testcase.ps1`。
3. 该 PowerShell 脚本必须以 UTF-8 BOM 保存。
4. 本地 `type` 只允许 `interface`、`feature`、`install`、`config`、`performance`、`security`；禁止使用 `unit`；`negative`、`boundary`、`functional`、`data_consistency`、`permission` 和 `other` 不得作为新的本地类型。同步前必须校验并阻断非法或缺失值，不得回退为 `feature`。
5. `auto: "auto"` 不写入禅道关键词，并将禅道用例 `type` 设置为 `other`（其他）；`auto: "no"` 不写入关键词，保留合法本地 `type` 映射。历史 `false` 仅兼容读取，不作为新值写入。回读校验按类型执行。

## 安全边界

1. 目标测试库按“任务提示词显式指定 > `config.yaml` 的 `zentao_import_target`”解析；目标缺失、非法或无法可靠确认时停止。
2. 账号、密码、Token、Cookie 只从环境变量或安全交互读取，不打印、不保存、不写入证据。
3. 没有真实远程回读的用例不得写入禅道数字 ID。
4. 远程失败、权限不足或回读不完整必须记录为 `not_executed`、`blocked` 或 `pending_registry`。
5. 真实回读的禅道用例 ID、模块信息和同步来源可回写到当前阶段允许更新的用例同步字段，再由注册表生成器读取；不得改写测试步骤/预期。

## 注册表要求

生成项目根目录 `module_case_map.json`，每条记录包含本地用例 ID、禅道用例 ID（可为 null）、需求 ID、模块名称/ID/路径、handler、Page Object、数据契约、`mapping_status`、`automation_status`、检查 ID、断言范围和来源文件。

`module_case_map.json` 是后续自动化和回归测试的唯一映射源。未同步成功的记录使用 `mapping_status: pending_registry`，禁止临时 ID。

## 模块级 Handoff

按当前模块写入独立文件：存在 `app/`、`pc/` 等业务分区时写入 `{stage_dir}/{partition}/{module_id}/HANDOFF.md`，没有业务分区时写入 `{stage_dir}/{module_id}/HANDOFF.md`。`module_id` 优先从当前 REQ 或同步输入继承；重复执行只更新该模块文件，不得覆盖其他模块。必须汇总注册表路径、Schema 校验、来源哈希、远程回读状态和 `Next Agent: stage-automation-agent`。

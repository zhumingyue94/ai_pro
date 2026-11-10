# 公共 Agent 资源约定

本目录是当前根目录下两个 QA 项目共享的通用 Agent 资源。

公共项目流程、门禁、安全和证据约定见根目录 `../AGENTS.md`；本目录只负责 Agent 资源，不重复项目约定。

## 目录

- `skills/`：不含具体项目业务的阶段 Skill 和辅助 Skill；环节 Skill 统一使用 `stage-` 前缀，辅助 Skill 和外部社区 Skill 保持原名。
- `rules/`：不含具体业务事实的通用 Rule。
- `references/`：通用测试用例、Bug 和回归模板。

## 边界

公共资源只能使用通用术语和占位符，不得写入项目名、业务模块、业务字段、真实 URL、ZenTao ID、REQ 专属示例、账号密码、Token、Cookie 或执行结果。当前仓库不保留测试点和测点评审阶段资源。
项目目录通过 `config.yaml` 引用本目录；项目本地 `.agents/rules/` 只允许保存业务覆盖层，且文件名不得与本目录重名。

## Skill 命名

- `stage-*`：当前 QA 流程环节 Skill。
- 无前缀：仓库辅助 Skill 或外部社区 Skill；外部 Skill 的原始目录名、`name` 和调用方式不得改写。

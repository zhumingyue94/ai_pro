# 模块级 Handoff 契约

每个模块或稳定 REQ 执行单元在固定的 `HANDOFF/` 目录下生成独立的 `{module_id}_HANDOFF.md`；技术目录不生成 Handoff。

## 路径规则

```text
有业务分区：{stage_dir}/{partition}/HANDOFF/{module_id}_HANDOFF.md
无业务分区：{stage_dir}/HANDOFF/{module_id}_HANDOFF.md
```

`module_id` 优先使用当前 REQ ID 或模块 ID；自动化、Bug 验证和回归阶段必须从上游产物、注册表或 RUN 元数据继承模块 ID。无法识别时记录 `module_id_missing`，不得回退到共享 `HANDOFF.md`。

`module_id` 只能包含字母、数字、`.`、`_` 和 `-`；不得包含路径分隔符、`..` 或控制字符。模块 ID 为空时不得回退到共享分区级 `HANDOFF.md`。

## 内容要求

每个模块 Handoff 必须记录当前模块的：

- 平台和业务范围；
- REQ、模块和输入路径；
- 输出产物路径；
- Gate、GateReasons、阻塞项和风险；
- 下一阶段；
- 执行 RUN、结果、缺陷和证据路径。

Handoff 只描述当前 `module_id`，不得汇总或改写其他模块的 Handoff。分区级汇总由 Pipeline Summary 扫描 `HANDOFF/{module_id}_HANDOFF.md` 动态生成。

## 幂等与并行规则

1. 写入前先解析当前模块 ID，并只操作 `HANDOFF/{module_id}_HANDOFF.md`。
2. 同一模块重复执行只更新自己的 Handoff 文件，不删除其他模块文件。
3. 不同模块不得使用同一模块 ID；无法区分模块时必须记录 `module_id_missing`，不得写入共享文件。
4. 写入应采用单文件原子替换；并行执行不得通过共享临时文件或共享 Handoff 汇总结果互相覆盖。
5. 旧的分区级 `HANDOFF.md` 不再作为必需输入；发现时记录 `legacy_partition_handoff`，不得覆盖或当作当前模块 Handoff。

## 模板

```markdown
# {阶段名称} Handoff

- 项目：{project}
- 阶段：{stage}
- 分区：{partition | root}
- 模块 ID：{module_id}
- 模块 ID 来源：{req | module | upstream | run | fallback}
- 更新时间：{timestamp}
- 状态：completed | completed_with_gate_issues | not_executed

## 覆盖范围

| 平台 | 模块 | REQ/范围 | 状态 |
|---|---|---|---|

## 输入产物

- {path}

## 输出产物

- {path}

## Gate 与问题

- Gate：{passed | failed | n/a}
- GateReasons：{list}
- Blockers：{list}
- Risks：{list}

## 执行与证据

- RUN：{path}
- 结果：{path}
- 缺陷：{path}
- 证据：{path}

## 下一阶段

- {next_agent}
```

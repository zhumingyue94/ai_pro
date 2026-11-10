# 07_ui_automation 框架说明

本目录已重构为**统一的 playwright + pytest 工程**。原先的 `tests/run_case.py` 与
`tests/run_module.py` 两个自研 runner 已删除，其产物流水线下沉到 pytest 钩子里，
现在只有一条执行入口：`pytest`。

## 一、快速开始

工作目录固定为 `07_ui_automation`，解释器用 `D:/tools/python3.10/python.exe`（记为 `PY`）。

```bash
# 按需求执行
PY -m pytest --req REQ-002
PY -m pytest --req REQ-004 --priority P1

# 按模块 / 禅道用例编号执行
PY -m pytest --module 宰杀线管理
PY -m pytest --zentao-case-id 47482

# 用 nodeid 直接选（需求与模块由注册表自动反查，无需显式传 --req）
PY -m pytest tests/modules/scheduling/test_target_goal.py::test_tc_002_01

# 只收集不执行 / 只验证产物链路 / 框架自检
PY -m pytest --collect-only -q --req REQ-002
PY -m pytest --dry-run --req REQ-004
PY -m pytest --self-test --req REQ-002
```

## 二、命令行选项

| 选项 | 作用 |
|---|---|
| `--req` | 需求编号，可重复传入或用逗号分隔 |
| `--module` | 按 `module_case_map.json` 的 `module.name` 精确匹配 |
| `--priority` | 按本地用例 `priority` 精确匹配，如 `P1` |
| `--zentao-case-id` | 数字禅道用例编号，仅作本地字段匹配 |
| `--run-label` | 强制指定 RUN 目录名中的模块标签 |
| `--dry-run` | 不启动浏览器、不执行用例，只验证筛选与产物链路 |
| `--self-test` | 用桩替代浏览器，验证执行与产物链路（自动跳过数据登记与 Handoff 写入） |
| `--allow-empty` | 无匹配用例时静默退出 0；缺省报错退出 4 |
| `--max-run-seconds` | 超时即标记 RUN 不完整；0 为不限 |
| `--no-update-registry` | 不更新 `data/REQ-{req_id}.yaml` |
| `--no-handoff` | 不更新 `HANDOFF.md` |

**不提供** `--headed` / `--headless` / `--browser` / `--output`：浏览器固定可视模式
（`headless=False`），不可通过命令行切换；无法启动可视浏览器时全部记为 `blocked`。

## 三、退出码

| 码 | 含义 |
|---|---|
| 0 | 全部通过（含 `accepted_variation`、`excluded`）或 `--dry-run` |
| 1 | 存在 `product_defect` |
| 2 | 被键盘中断 |
| 4 | 使用错误：无匹配用例、参数非法、启用了 xdist |
| 5 | 配置阻塞：UI 环境变量缺失或浏览器无法启动 |
| 7 | 不完整：结果数不符、产物缺失、证据不全或超时 |

## 四、目录结构

```
07_ui_automation/
├── conftest.py                 唯一 conftest：注册命令行选项
├── pytest.ini                  rootdir 配置；-p no:playwright；pythonpath = .
├── README_框架说明.md           本文件
├── HANDOFF.md                  阶段总 Handoff（索引 + 最近一次 RUN + 历史归档）
├── config/settings.py          运行配置（凭据只从 .env 读，不使用 storage state）
├── data/REQ-*.yaml             数据登记索引（每次执行后追加 last_run / run_history）
├── pages/**                    页面对象（本次零改动）
├── tests/modules/**            return-dict 用例（本次零改动，89 个函数）
├── framework/                  框架内核（本次新增）
│   ├── options.py              CLI 选项与筛选条件
│   ├── plugin.py               全部 pytest 钩子
│   ├── orchestrator.py         会话状态载体（挂 config.stash）
│   ├── fixtures.py             settings / browser / context / page / evidence_dir / case_meta
│   ├── registry.py             module_case_map.json 只读访问与 handler 反查
│   ├── case_source.py          04 / 05 / 07 阶段数据源
│   ├── classify.py             失败分类引擎（唯一真源）
│   ├── contract.py             用例结果记录契约
│   ├── evidence.py             截图规范化、SHA-256、兜底截图
│   ├── run_layout.py           run_id 与 RUN 目录编排
│   ├── integrity.py            完整性校验与退出码
│   └── reporters/              一文件一产物
├── scripts/                    自检脚本
└── reports/RUN_{模块}_{时间戳}/ 每次执行的产物（历史 RUN 一律不覆盖）
```

## 五、产物清单（每个 RUN 目录）

| 产物 | 说明 |
|---|---|
| `selection.yaml` | 选择清单：完整本地范围、筛选条件、评审门禁、禅道同步历史证据 |
| `results.yaml` / `results.json` | 执行结果（机器与人工两种读法一致） |
| `results.jsonl` | 增量落盘，进程被杀死时可恢复 |
| `bugs_review.yaml` | **只含 `product_defect`**，`review_status` 恒为 `pending` |
| `缺陷报告.md` | 给人看的缺陷报告；无缺陷时输出占位报告并列出被排除项 |
| `case_results.xlsx` | 三张表：Summary / Case Results(20 列) / Steps & Evidence |
| `testcase.csv` | 十列实时结果表，utf-8-sig |
| `screenshots/` | 截图证据，文件名含用例 ID 与检查 ID |
| `allure-results/` | Allure 结果与截图附件 |
| `RUN_STATUS.json` | 完整性状态；`complete=false` 时不得作为交付报告 |

## 六、硬约束（代码已固化，不依赖使用者自觉）

- **固定可视浏览器**：`HEADLESS = False` 常量，无命令行开关；启动失败记 `blocked`，绝不降级无头。
- **不自动创建远程 Bug**：全仓库无禅道 Bug 创建代码；`zentao_bug_id` 恒为 `null`。
- **只有产品行为失败才算缺陷**：`product_defect` 只能由用例显式声明产生，且须
  `status=failed` + `check_id` + `assertion_scope` + `expected` + `actual` 五要素齐全，
  否则降级为 `test_case_error`；普通 `AssertionError`、定位失败、等待超时在任何路径下都不升级。
- **分类映射固定**：`product_defect→failed`、`blocked→blocked`、`accepted_variation→passed`、
  `test_script_error/test_case_error→ignored`、`excluded→excluded`。
- **重跑必须用新 run_id**：目录创建用 `exist_ok=False`，永不覆盖历史 RUN。
- **自造数据前缀**：`AUTO测试_勿用_{run_id}_`；执行后默认保留，清理须用户确认。
- **评审门禁只记录不阻断**：`05_case_review` 的 `gate_passed` / `gate_reasons` 写入 selection.yaml。

## 七、自检脚本

```bash
PY scripts/selftest_classify.py     # 分类引擎 15 项断言
PY scripts/selftest_pipeline.py     # 产物流水线（缺陷只收录 product_defect、退出码、占位报告）
PY scripts/check_docstrings.py      # docstring 覆盖（AGENTS.md 硬性要求）
PY scripts/check_docstrings.py --all
```

## 八、禁用 pytest-playwright 插件的原因

`pytest.ini` 中固定了 `-p no:playwright`：

1. 插件注册的 `--headed` 与"固定 headless=False"语义冲突；
2. 插件的 autouse session fixture `delete_output_dir` 会对 `--output` 目录执行 `shutil.rmtree`；
3. 插件的 `context`/`page` 是 function 级，会破坏本框架 session 级共享登录态
   （89 个用例依赖 context 内共享 cookie 免重复登录）。

浏览器因此由 `framework/fixtures.py` 用 `sync_playwright` 自行管理，这仍是标准 pytest 用法。

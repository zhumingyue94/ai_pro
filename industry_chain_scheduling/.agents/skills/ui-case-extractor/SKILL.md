---
name: ui-case-extractor
description: >
  Extract the test cases that will be executed in a UI automation run into a
  testcase.csv under reports/RUN_{timestamp}/, with columns 用例编号/所属模块/用例函数名称/标题/
  前置条件/预期/步骤/结果/错误原因/截图路径, sorted by case number. Use when the user asks to
  "提取用例" / "导出本次执行的用例" / "生成 testcase.csv" / "预览要跑的用例", or wants a
  per-run case清单 for UI automation before/without running pytest.
license: "MIT"
metadata:
  author: "zhumi"
  version: "0.1.0"
  category: "QA Automation"
---

# UI Case Extractor

把"本次 UI 自动化要执行的用例"提取成 `reports/RUN_{时间戳}/testcase.csv`（10 列），
用例**按编号（zentao_case_id）升序**预填。本 skill 是**独立于 pytest 的提取工具**——
它只负责「提取/预览/导出用例清单」，不执行任何用例，结果的回填由
`07_ui_automation/tests/conftest.py` 负责。

## When to use

- 用户要求「提取用例」「导出本次执行的用例」「生成 testcase.csv」「预览要跑的用例」；
- 在跑 pytest 之前，想先确认本次执行涉及哪些用例及其前置条件/步骤/预期；
- 想给某次执行留一份可读的用例清单（含 auto:no 标记为 excluded 的用例）。

## Workflow

1. **定位项目根**：脚本自动从当前目录向上搜索 `module_case_map.json`；若不在项目目录下执行，用 `--root` 显式指定。
2. **选择用例范围**：至少指定一个选择器 `--req` / `--module` / `--case` / `--handler`（可组合）。
3. **运行脚本**：用含 PyYAML 的 managed venv 运行（见下），脚本在
   `<root>/07_ui_automation/reports/RUN_{时间戳}/` 下生成 `testcase.csv`（UTF-8 with BOM，Excel 可直接打开）。
4. **得到 CSV**：10 列、按编号升序；`auto: no` 的用例结果列标 `excluded` 并附原因，其余行结果列留空待执行回填。

## CLI

| 参数 | 说明 | 示例 |
|---|---|---|
| `--root PATH` | 项目根（含 `module_case_map.json`），缺省自动向上搜索 | `--root {project_root} |
| `--req` | 按需求筛选（可多个） | `--req REQ-xxx` |
| `--module` | 按模块名筛选（可多个） | `--module {业务维度}管理` |
| `--case` | 按用例编号筛选（可多个） | `--case TC-xxx-07 TC-xxx-09` |
| `--handler` | 按 handler 前缀（测试文件模块路径）筛选 | `--handler tests.modules.master_data.test_slaughter_line` |
| `--out PATH` | 覆盖输出目录（默认 `reports/RUN_{ts}`） | `--out D:/tmp/myrun` |

> 至少指定一个选择器，否则脚本报错退出。

## 调用示例

```bash
PY="C:/Users/zhumi/.workbuddy/binaries/python/envs/ui_auto/Scripts/python.exe"

# 按模块提取（当前在项目目录下）
"$PY" <skill-path>/scripts/extract_cases.py --module "{业务维度}管理"

# 按需求提取（显式指定项目根）
"$PY" <skill-path>/scripts/extract_cases.py --req REQ-xxx --root {project_root}

# 按用例编号提取
"$PY" <skill-path>/scripts/extract_cases.py --case TC-xxx-07 TC-xxx-09

# 按 handler 前缀提取（某测试文件的全部用例）
"$PY" <skill-path>/scripts/extract_cases.py --handler tests.modules.master_data.test_slaughter_line

# 组合选择器 + 自定义输出目录
"$PY" <skill-path>/scripts/extract_cases.py --req REQ-xxx --module {业务维度}管理 --out D:/tmp/myrun
```

## Output（testcase.csv）

10 列（顺序固定）：`用例编号`、`所属模块`、`用例函数名称`、`标题`、`前置条件`、`预期`、`步骤`、`结果`、`错误原因`、`截图路径`。

- 排序：按 `zentao_case_id` 升序。
- 前置条件 / 预期 / 步骤：取自 `04_testcases/TC_{req_id}.yaml`，多行以 `1. xxx\n2. yyy` 合并进单个单元格（Excel 内换行）。
- 预期 = 各步骤 `expected` 的合并；步骤 = 各步骤 `action` 的合并。
- `auto: no` 的用例：结果列标 `excluded`，错误原因列写 `automation: no，按规则 excluded 不执行`。
- 其余行的结果/错误原因/截图路径**留空**——提取阶段不产生执行结果，回填由 conftest.py 负责。
- 编码：UTF-8 with BOM（`utf-8-sig`），Excel 直接打开不乱码。
- 输出目录下同时创建 `screenshots/` 子目录，供后续执行阶段存放截图。

## Notes

- 脚本**不依赖 pytest**，不触碰 conftest 的 collection 逻辑；与 conftest.py 的提取逻辑并存、互不影响。
- 数据源为只读输入：`<root>/module_case_map.json`（cases 列表）+ `<root>/04_testcases/TC_{req_id}.yaml`，两者必须存在。
- YAML 用例的字段约定：`id`（TC-xxx-yy）、`zentao_case_id`、`auto`（auto|no）、`title`、`preconditions`（list[str]）、`steps`（list[{action, expected}]）。
- 执行结果回填（failed/error/blocked + 错误原因 + 截图路径）由 `07_ui_automation/tests/conftest.py` 的 `pytest_runtest_makereport` 负责，本 skill 不涉及。

## Skill Files

- `scripts/extract_cases.py` — 提取用例并写出 `testcase.csv`（纯 Python stdlib + PyYAML）。

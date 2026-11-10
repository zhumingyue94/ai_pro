"""缺陷报告：RUN/缺陷报告.md（给人看的产品缺陷报告）。

**只收录 classification=product_defect 的条目**。无产品缺陷时输出占位报告，
并完整列出被排除的脚本错误、用例错误与阻塞，避免"没有缺陷"被误读为"没有问题"。
"""

from __future__ import annotations

import json
from typing import Any

from .. import options

FILENAME = "缺陷报告.md"

# 不进入缺陷报告的分类，仅登记到「三、被排除项」。
EXCLUDED_TABLE_HEADER = (
    "| 本地用例 ID | 禅道用例 ID | 分类 | 状态 | 原因摘要 | 截图 |\n"
    "|---|---:|---|---|---|---|"
)


def _as_text(value: Any) -> str:
    """把任意值转为可读文本；结构化的值用 JSON 代码块展示。"""
    if value is None or value == "":
        return "—"
    if isinstance(value, str):
        return value
    return "```json\n" + json.dumps(value, ensure_ascii=False, indent=2) + "\n```"


def _one_line(value: Any, limit: int = 80) -> str:
    """把值压成单行摘要，超长截断，并保证不破坏 Markdown 表格结构。"""
    if value is None or value == "":
        return "—"
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)
    text = " ".join(text.split())
    if len(text) > limit:
        text = text[: limit - 1] + "…"
    return text.replace("|", "\\|")


def _numbered(values: Any) -> str:
    """把列表渲染为带编号的多行文本。"""
    if not isinstance(values, list) or not values:
        return "—"
    return "\n".join(f"{index}. {item}" for index, item in enumerate(values, start=1))


def _count(records: list[dict], key: str, value: str) -> int:
    """统计指定字段等于给定值的记录数。"""
    return sum(1 for item in records if str(item.get(key)) == value)


def _overview(records: list[dict], bugs: list[dict]) -> list[str]:
    """渲染「一、总览」章节。"""
    executed = sum(1 for item in records if not item.get("excluded"))
    excluded = sum(1 for item in records if item.get("excluded"))
    lines = [
        "## 一、总览",
        "",
        "| 指标 | 值 |",
        "|---|---:|",
        f"| 选中用例数 | {len(records)} |",
        f"| 实际执行 | {executed} |",
        f"| 排除（未执行） | {excluded} |",
        f"| passed（含 accepted_variation） | {_count(records, 'status', 'passed')} |",
        f"| failed（product_defect） | {_count(records, 'status', 'failed')} |",
        f"| blocked | {_count(records, 'status', 'blocked')} |",
        f"| ignored（脚本/用例错误） | {_count(records, 'status', 'ignored')} |",
        f"| **本文件收录缺陷数** | **{len(bugs)}** |",
        "",
    ]
    return lines


def _bug_block(index: int, bug: dict) -> list[str]:
    """渲染单个缺陷的完整条目。"""
    shots = bug.get("evidence", {}).get("screenshots") or []
    evidence_rows = (
        "\n".join(
            f"| `{shot.get('path', '')}` | `{shot.get('sha256', '')}` |"
            for shot in shots
            if isinstance(shot, dict)
        )
        or "| — | — |"
    )
    steps = bug.get("steps") or []
    steps_text = "\n".join(
        f"{item.get('index', i + 1)}. {item.get('action', '')}"
        + (f" —— 预期：{item['expected']}" if item.get("expected") else "")
        for i, item in enumerate(steps)
        if isinstance(item, dict)
    ) or "—"
    return [
        f"### 缺陷 {index}：{_one_line(bug.get('title'), 120)}",
        "",
        "| 字段 | 值 |",
        "|---|---|",
        f"| 本地用例 ID | {bug.get('case_id') or '—'} |",
        f"| 禅道用例 ID（数字） | {bug.get('zentao_case_id') or '—'} |",
        f"| check_id | {bug.get('keywords', [None, None, None])[2] or '—'} |",
        f"| assertion_scope | {bug.get('assertion_scope') or '—'} |",
        f"| failure_origin | {bug.get('failure_origin') or '—'} |",
        f"| 状态映射 | failed |",
        f"| 禅道 Bug ID | 未创建（pending） |",
        "",
        "**前置条件**",
        "",
        _numbered(bug.get("precondition")),
        "",
        "**重现步骤**",
        "",
        steps_text,
        "",
        "**期望结果**",
        "",
        _as_text(bug.get("expected")),
        "",
        "**实际结果**",
        "",
        _as_text(bug.get("actual")),
        "",
        "**证据**",
        "",
        "| 截图相对路径 | SHA-256 |",
        "|---|---|",
        evidence_rows,
        "",
        "**控制台 / 页面 / 请求错误**",
        "",
        "- console_errors: []",
        "- page_errors: []",
        "- request_errors: []",
        "",
        "**审核结论**",
        "",
        "- review_status: `pending` —— 待人工确认是否为产品缺陷，确认后方可提交禅道。",
        "",
        "---",
        "",
    ]


def _defect_list(bugs: list[dict]) -> list[str]:
    """渲染「二、缺陷清单」章节。"""
    if not bugs:
        return [
            "## 二、缺陷清单",
            "",
            "（无。本次执行 `classification == product_defect` 的条目数为 0，未收录任何缺陷。）",
            "",
        ]
    lines = ["## 二、缺陷清单", ""]
    for index, bug in enumerate(bugs, start=1):
        lines.extend(_bug_block(index, bug))
    return lines


def _excluded(records: list[dict]) -> list[str]:
    """渲染「三、被排除项」章节，列出全部非产品缺陷条目。"""
    lines = ["## 三、被排除项（非产品缺陷）", "", EXCLUDED_TABLE_HEADER]
    rows: list[str] = []
    for record in records:
        if record.get("classification") == "product_defect":
            continue
        shot = record.get("screenshots") or []
        first = shot[0].get("path") if shot and isinstance(shot[0], dict) else "—"
        rows.append(
            f"| {record.get('case_id') or '—'} | {record.get('zentao_case_id') or '—'} "
            f"| {record.get('classification') or '—'} | {record.get('status') or '—'} "
            f"| {_one_line(record.get('detail') or record.get('actual'))} | `{first}` |"
        )
    if not rows:
        rows.append("| — | — | — | — | 无被排除项 | — |")
    else:
        rows.append("")
        rows.append("> 说明：上述条目**不作为产品缺陷**，仅作为脚本、用例或环境问题登记，需人工跟进修复。")
    lines.extend(rows)
    lines.append("")
    return lines


def _scope(orch, records: list[dict]) -> list[str]:
    """渲染「四、执行范围与门禁」章节。"""
    from .. import case_source

    reqs = orch.req_ids or ["（未指定）"]
    lines = [
        "## 四、执行范围与门禁",
        "",
        f"- 筛选条件：`{json.dumps(orch.filter_desc, ensure_ascii=False)}`",
        f"- 需求范围：{'、'.join(reqs)}",
        f"- 模块范围：{'、'.join(orch.module_names) or '（未指定）'}",
        f"- 数据来源：`04_testcases/TC_{{req_id}}.yaml`；注册表 `module_case_map.json`（唯一映射来源）",
        f"- 自造数据前缀：`{options.TEST_DATA_PREFIX}{{run_id}}_`；**执行后默认保留，清理须用户确认**",
    ]
    for req_id in reqs:
        gate = case_source.review_gate_summary(str(req_id))
        sync = case_source.load_zentao_sync_evidence(str(req_id))
        lines.append(
            f"- `{req_id}` 评审门禁：`gate_passed = {gate.get('gate_passed')}`；"
            f"`gate_reasons = {gate.get('gate_reasons')}`（**仅记录，不阻断执行**）"
        )
        lines.append(
            f"- `{req_id}` 禅道同步历史证据：`06_zentao_sync/history/` 命中 "
            f"{len(sync.get('log_files') or [])} 个日志；`operations_executed = {sync.get('operations_executed')}`"
            "（本项目未执行过远程同步）"
        )
    lines.append("")
    return lines


def _artifacts(orch) -> list[str]:
    """渲染「五、产物索引」章节。"""
    return [
        "## 五、产物索引",
        "",
        "| 产物 | 路径 |",
        "|---|---|",
        "| 选择 | `selection.yaml` |",
        "| 结果 | `results.yaml` / `results.json` / `results.jsonl` |",
        "| Bug 审核 | `bugs_review.yaml` |",
        "| 缺陷报告 | `缺陷报告.md` |",
        "| 结果表 | `case_results.xlsx` |",
        "| 实时 CSV | `testcase.csv` |",
        "| 截图 | `screenshots/` |",
        "| Allure | `allure-results/` |",
        "| 完整性 | `RUN_STATUS.json` |",
        "",
    ]


def build(orch, records: list[dict], bugs: list[dict], complete: bool, reasons: list[str]) -> str:
    """渲染完整的缺陷报告 Markdown 文本。"""
    integrity_text = "完整" if complete else f"⚠ 不完整（原因：{'；'.join(reasons) or '未标注'}）"
    head = [
        f"# 缺陷报告 · {orch.run_id}",
        "",
        f"> 生成时间：{orch.finished_at or '—'}",
        f"> 需求：{'、'.join(orch.req_ids) or '（未指定）'} ｜ 模块：{'、'.join(orch.module_names) or '（未指定）'}"
        f" ｜ 环境：{orch.settings_snapshot.get('base_host', 'browser_not_started')}（headless=false）",
        f"> 执行完整性：**{integrity_text}**",
        "> 收录范围：本文件**仅收录 `classification=product_defect`** 的条目；"
        "脚本错误、用例错误、阻塞一律不进入本文件，见「三、被排除项」。",
        "> 禅道：**未自动创建任何 Bug**。`review_status = pending`，需人工审核后再提交。",
        "",
    ]
    if not complete:
        head += ["> ⚠ 本次 RUN 不完整，不得作为最终交付报告。", ""]
    if not bugs:
        head += ["> **本次执行未发现产品缺陷：`classification == product_defect` 的条目数为 0。**", ""]
    lines = head + _overview(records, bugs) + _defect_list(bugs) + _excluded(records)
    lines += _scope(orch, records) + _artifacts(orch)
    return "\n".join(lines) + "\n"


def write(orch, records: list[dict], bugs: list[dict], complete: bool, reasons: list[str]) -> None:
    """写出缺陷报告 Markdown。"""
    if orch.run_dir is None:
        return
    (orch.run_dir / FILENAME).write_text(
        build(orch, records, bugs, complete, reasons), encoding="utf-8"
    )

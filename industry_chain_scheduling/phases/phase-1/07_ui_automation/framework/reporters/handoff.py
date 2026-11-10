"""阶段总 Handoff 维护：07_ui_automation/HANDOFF.md。

按 08 阶段约定，Handoff 是**一个总文件**，不按模块或 RUN 单独生成。
原实现是纯追加式（19 次 RUN 后已达 53KB 不可读），这里改为「索引表 + 最近一次详情 +
历史归档」三段结构，用注释锚点做幂等区间替换，历史正文一字不删。
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from ..registry import AUTO_DIR

HANDOFF_PATH = AUTO_DIR / "HANDOFF.md"
TITLE = "# UI 自动化阶段总 Handoff"
INDEX_BEGIN = "<!-- BEGIN:UI_RUN_INDEX -->"
INDEX_END = "<!-- END:UI_RUN_INDEX -->"
LATEST_BEGIN = "<!-- BEGIN:UI_LATEST_RUN -->"
LATEST_END = "<!-- END:UI_LATEST_RUN -->"
ARCHIVE_HEADING = "## 历史归档"
MAX_INDEX_ROWS = 50

_INDEX_ROW_RE = re.compile(r"^\|\s*(RUN_\S+)\s*\|")


def _ensure_structure(text: str) -> str:
    """把既有正文迁移进「历史归档」并插入索引与最近一次详情锚点。"""
    if INDEX_BEGIN in text and LATEST_BEGIN in text:
        return text
    # 只剥离最外层的总标题，其余正文（含历史块的各级标题）原样保留。
    body = text
    if body.lstrip().startswith(TITLE):
        body = body.lstrip()[len(TITLE):]
    archive = body.strip("\n")
    blocks = [
        TITLE,
        "",
        "> 本文件由 08 阶段自动化框架自动维护：索引表与「最近一次 RUN」为机器维护区间，",
        "> 其余内容属于历史归档，不会被自动删除。",
        "",
        INDEX_BEGIN,
        "",
        "（尚无执行记录）",
        "",
        INDEX_END,
        "",
        LATEST_BEGIN,
        "",
        "（尚无执行记录）",
        "",
        LATEST_END,
        "",
        ARCHIVE_HEADING,
        "",
        archive,
        "",
    ]
    return "\n".join(blocks)


def _replace_block(text: str, begin: str, end: str, payload: list[str]) -> str:
    """替换两个锚点之间的内容；锚点缺失时返回原文。"""
    start = text.find(begin)
    stop = text.find(end)
    if start < 0 or stop < 0 or stop < start:
        return text
    return text[: start + len(begin)] + "\n" + "\n".join(payload) + "\n" + text[stop:]


def _index_rows(text: str) -> list[str]:
    """从索引锚点区间中解析已有的表格行（不含表头与分隔行）。"""
    start = text.find(INDEX_BEGIN)
    stop = text.find(INDEX_END)
    if start < 0 or stop < 0:
        return []
    segment = text[start + len(INDEX_BEGIN): stop]
    return [
        line
        for line in segment.splitlines()
        if _INDEX_ROW_RE.match(line.strip()) and "---" not in line
    ]


def _index_row(orch, records: list[dict], complete: bool) -> str:
    """构造本次 RUN 在索引表中的一行。"""
    defects = sum(1 for item in records if item.get("classification") == "product_defect")
    executed = sum(1 for item in records if not item.get("excluded"))
    return (
        f"| {orch.run_id} | {orch.finished_at} | {'、'.join(orch.req_ids) or '—'} "
        f"| {'、'.join(orch.module_names) or '—'} | {executed} | {defects} "
        f"| {'完整' if complete else '不完整'} | `reports/{orch.run_id}` |"
    )


def _index_table(rows: list[str]) -> list[str]:
    """渲染完整的索引表格文本。"""
    header = [
        "| run_id | 完成时间 | 需求 | 模块 | 执行数 | 产品缺陷 | 完整性 | 产物路径 |",
        "|---|---|---|---|---:|---:|---|---|",
    ]
    return header + rows if rows else ["（尚无执行记录）"]


def _latest_block(orch, records: list[dict], bugs: list[dict], complete: bool, reasons: list[str]) -> list[str]:
    """渲染「最近一次 RUN」详情块。"""
    counts: dict[str, int] = {}
    for record in records:
        status = str(record.get("status") or "unknown")
        counts[status] = counts.get(status, 0) + 1
    lines = [
        f"### {orch.run_id}",
        "",
        f"- 完成时间：{orch.finished_at}",
        f"- 需求：{'、'.join(orch.req_ids) or '—'} ｜ 模块：{'、'.join(orch.module_names) or '—'}",
        f"- 环境：{orch.settings_snapshot.get('base_host', 'browser_not_started')}（headless=false）",
        f"- 筛选条件：`{json.dumps(orch.filter_desc, ensure_ascii=False)}`",
        f"- 计划 {len(orch.planned)} 条，实际执行 {orch.executed_count()} 条",
        f"- 状态统计：{json.dumps(counts, ensure_ascii=False)}",
        f"- 产品缺陷：{len(bugs)} 条（见 `reports/{orch.run_id}/缺陷报告.md`）",
        f"- 完整性：{'完整' if complete else '⚠ 不完整（' + '；'.join(reasons) + '）'}",
        f"- 禅道：未访问、未写入、未创建 Bug",
        "",
    ]
    return lines


def build(orch, records: list[dict], bugs: list[dict], complete: bool, reasons: list[str]) -> str:
    """渲染更新后的完整 Handoff 文本。"""
    original = HANDOFF_PATH.read_text(encoding="utf-8") if HANDOFF_PATH.is_file() else ""
    text = _ensure_structure(original)
    rows = [row for row in _index_rows(text) if f"| {orch.run_id} |" not in row]
    rows.insert(0, _index_row(orch, records, complete))
    text = _replace_block(text, INDEX_BEGIN, INDEX_END, _index_table(rows[:MAX_INDEX_ROWS]))
    text = _replace_block(
        text, LATEST_BEGIN, LATEST_END, _latest_block(orch, records, bugs, complete, reasons)
    )
    return text


def update(orch, records: list[dict], bugs: list[dict], complete: bool, reasons: list[str]) -> Path:
    """更新 HANDOFF.md，返回文件路径。"""
    HANDOFF_PATH.write_text(build(orch, records, bugs, complete, reasons), encoding="utf-8")
    return HANDOFF_PATH


def preview(orch, records: list[dict], bugs: list[dict], complete: bool, reasons: list[str]) -> Path | None:
    """在 dry-run 模式下写出预览，不触碰真实 Handoff 文件。"""
    if orch.run_dir is None:
        return None
    lines = ["> --dry-run 预览：以下内容仅示意将如何更新 HANDOFF.md，未写入真实文件。", ""]
    lines += _latest_block(orch, records, bugs, complete, reasons)
    target = orch.run_dir / "handoff.preview.md"
    target.write_text("\n".join(lines), encoding="utf-8")
    return target

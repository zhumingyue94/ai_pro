"""结果表：RUN/case_results.xlsx（openpyxl 直出，替代原 Node 子进程实现）。

原实现通过 ``subprocess`` 调用 ``utils/build_case_results.mjs``，依赖硬编码的
``C:/Users/zhumi/.workbuddy/binaries/node/...`` 路径与仓库外的 ``@oai/artifact-tool``。
本模块用已安装的 openpyxl 直接生成，保持原有的三张表结构并补齐字段。
"""

from __future__ import annotations

import json
from typing import Any

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

from .. import options

FILENAME = "case_results.xlsx"

HEADER_FILL = PatternFill("solid", fgColor="305496")
HEADER_FONT = Font(color="FFFFFF", bold=True)
HEADER_ALIGN = Alignment(horizontal="center", vertical="center", wrap_text=True)
BODY_ALIGN = Alignment(vertical="top", wrap_text=True)

STATUS_STYLE: dict[str, tuple[str, str, bool]] = {
    "passed": ("C6EFCE", "006100", False),
    "accepted_variation": ("C6EFCE", "006100", False),
    "failed": ("FFC7CE", "9C0006", False),
    "blocked": ("FFEB9C", "9C6500", False),
    "ignored": ("D9D9D9", "3F3F3F", True),
    "excluded": ("DDEBF7", "1F4E79", False),
}

CASE_COLUMNS: tuple[tuple[str, int], ...] = (
    ("本地用例ID", 14),
    ("禅道用例ID", 12),
    ("标题", 40),
    ("类型", 10),
    ("自动化", 10),
    ("状态", 12),
    ("失败分类", 18),
    ("check_id", 14),
    ("assertion_scope", 34),
    ("前置条件", 40),
    ("预期", 50),
    ("实际情况", 50),
    ("错误原因", 50),
    ("错误来源", 22),
    ("用例函数", 34),
    ("截图相对路径", 46),
    ("截图SHA-256", 68),
    ("开始时间", 20),
    ("结束时间", 20),
    ("数据准备", 46),
)

STEP_COLUMNS: tuple[tuple[str, int], ...] = (
    ("本地用例ID", 14),
    ("禅道用例ID", 12),
    ("check_id", 14),
    ("assertion_scope", 34),
    ("步骤序号", 10),
    ("动作", 50),
    ("预期", 50),
    ("实际观测", 50),
    ("截图路径", 46),
    ("截图SHA-256", 68),
)


def _style_header(worksheet, columns: tuple[tuple[str, int], ...]) -> None:
    """写入表头并应用样式、列宽、冻结窗格与自动筛选。"""
    for index, (name, width) in enumerate(columns, start=1):
        cell = worksheet.cell(row=1, column=index, value=name)
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
        cell.alignment = HEADER_ALIGN
        worksheet.column_dimensions[get_column_letter(index)].width = width
    worksheet.freeze_panes = "C2"
    worksheet.sheet_view.showGridLines = False


def _apply_filter(worksheet, last_row: int, last_col: int) -> None:
    """为工作表启用自动筛选；无数据行时跳过。"""
    if last_row >= 2:
        worksheet.auto_filter.ref = f"A1:{get_column_letter(last_col)}{last_row}"


def _text(value: Any) -> str:
    """把任意值转为单元格文本。"""
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False)


def _numbered(value: Any) -> str:
    """把列表渲染为带编号的多行文本。"""
    if not isinstance(value, list):
        return _text(value)
    return "\n".join(f"{index}. {item}" for index, item in enumerate(value, start=1))


def _shots(record: dict) -> tuple[str, str]:
    """返回记录的截图路径与 SHA-256 的多行文本。"""
    shots = [item for item in (record.get("screenshots") or []) if isinstance(item, dict)]
    paths = "\n".join(str(item.get("path") or "") for item in shots)
    digests = "\n".join(str(item.get("sha256") or "") for item in shots)
    return paths, digests


def _data_preparation_text(record: dict) -> str:
    """把数据登记摘要压成单行文本。"""
    data = record.get("data_preparation") or {}
    return (
        f"fixture_type={data.get('fixture_type')}；"
        f"creates_data={data.get('creates_data')}；"
        f"cleanup_status={data.get('cleanup_status')}"
    )


def _write_summary(worksheet, orch, records: list[dict], bugs: list[dict], complete: bool, reasons: list[str]) -> None:
    """写入 Summary 工作表。"""
    worksheet.append(["字段", "值"])
    for cell in worksheet[1]:
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
        cell.alignment = HEADER_ALIGN
    worksheet.column_dimensions["A"].width = 22
    worksheet.column_dimensions["B"].width = 90
    worksheet.freeze_panes = "A2"

    counts: dict[str, int] = {}
    classification_counts: dict[str, int] = {}
    for record in records:
        status = str(record.get("status") or "unknown")
        counts[status] = counts.get(status, 0) + 1
        key = str(record.get("classification") or "unknown")
        classification_counts[key] = classification_counts.get(key, 0) + 1

    rows: list[tuple[str, Any]] = [
        ("RUN ID", orch.run_id),
        ("开始时间", orch.started_at),
        ("结束时间", orch.finished_at),
        ("需求", "、".join(orch.req_ids)),
        ("模块", "、".join(orch.module_names)),
        ("环境 host", orch.settings_snapshot.get("base_host", "browser_not_started")),
        ("headless", str(options.HEADLESS).lower()),
        ("执行完整性", "完整" if complete else f"不完整：{'；'.join(reasons)}"),
        ("dry_run", str(orch.dry_run).lower()),
        ("筛选条件", json.dumps(orch.filter_desc, ensure_ascii=False)),
        ("计划执行数", len(orch.planned)),
        ("实际执行数", orch.executed_count()),
        ("结果记录数", len(records)),
        ("状态统计", json.dumps(counts, ensure_ascii=False)),
        ("分类统计", json.dumps(classification_counts, ensure_ascii=False)),
        ("产品缺陷数", len(bugs)),
        ("禅道", "未访问、未写入、未创建 Bug（review_status=pending）"),
        ("RUN 目录", str(orch.run_dir)),
    ]
    for name, value in rows:
        worksheet.append([name, _text(value)])
        worksheet.cell(row=worksheet.max_row, column=2).alignment = BODY_ALIGN
    worksheet.sheet_view.showGridLines = False


def _write_case_results(worksheet, records: list[dict]) -> None:
    """写入 Case Results 工作表并按状态着色。"""
    _style_header(worksheet, CASE_COLUMNS)
    for record in records:
        paths, digests = _shots(record)
        worksheet.append(
            [
                str(record.get("case_id") or ""),
                int(record.get("zentao_case_id") or -1),
                str(record.get("title") or ""),
                str(record.get("type") or ""),
                str(record.get("auto") or ""),
                str(record.get("status") or ""),
                str(record.get("classification") or ""),
                str(record.get("check_id") or ""),
                str(record.get("assertion_scope") or ""),
                _numbered(record.get("preconditions")),
                _text(record.get("expected")),
                _text(record.get("actual")),
                _text(record.get("detail")),
                str(record.get("failure_origin") or ""),
                str(record.get("handler") or "").rsplit(":", 1)[-1],
                paths,
                digests,
                str(record.get("started_at") or ""),
                str(record.get("finished_at") or ""),
                _data_preparation_text(record),
            ]
        )
        row = worksheet.max_row
        for column in range(1, len(CASE_COLUMNS) + 1):
            worksheet.cell(row=row, column=column).alignment = BODY_ALIGN
        # 禅道用例 ID 用文本格式，避免长数字被科学计数法改写。
        worksheet.cell(row=row, column=2).number_format = "0"
        fill_color, font_color, italic = STATUS_STYLE.get(
            str(record.get("status") or ""), ("FFFFFF", "000000", False)
        )
        status_cell = worksheet.cell(row=row, column=6)
        status_cell.fill = PatternFill("solid", fgColor=fill_color)
        status_cell.font = Font(color=font_color, italic=italic)
        status_cell.alignment = Alignment(horizontal="center", vertical="top")
    _apply_filter(worksheet, worksheet.max_row, len(CASE_COLUMNS))


def _write_steps(worksheet, records: list[dict]) -> None:
    """写入 Steps & Evidence 工作表；截图挂在每条记录的最后一步。"""
    _style_header(worksheet, STEP_COLUMNS)
    for record in records:
        paths, digests = _shots(record)
        steps = [item for item in (record.get("steps") or []) if isinstance(item, dict)]
        if not steps:
            worksheet.append(
                [
                    str(record.get("case_id") or ""),
                    int(record.get("zentao_case_id") or -1),
                    str(record.get("check_id") or ""),
                    str(record.get("assertion_scope") or ""),
                    0,
                    "（无步骤契约）",
                    _text(record.get("expected")),
                    _text(record.get("actual")),
                    paths,
                    digests,
                ]
            )
            _align_row(worksheet, len(STEP_COLUMNS))
            continue
        total = len(steps)
        for offset, step in enumerate(steps):
            last = offset == total - 1
            worksheet.append(
                [
                    str(record.get("case_id") or ""),
                    int(record.get("zentao_case_id") or -1),
                    str(record.get("check_id") or ""),
                    str(record.get("assertion_scope") or ""),
                    int(step.get("index") or (offset + 1)),
                    _text(step.get("action")),
                    _text(step.get("expected")),
                    _text(step.get("actual")),
                    paths if last else "",
                    digests if last else "",
                ]
            )
            _align_row(worksheet, len(STEP_COLUMNS))
            worksheet.cell(row=worksheet.max_row, column=2).number_format = "0"
    _apply_filter(worksheet, worksheet.max_row, len(STEP_COLUMNS))


def _align_row(worksheet, columns: int) -> None:
    """为最后一行统一应用正文对齐方式。"""
    row = worksheet.max_row
    for column in range(1, columns + 1):
        worksheet.cell(row=row, column=column).alignment = BODY_ALIGN


def write(orch, records: list[dict], bugs: list[dict], complete: bool, reasons: list[str]) -> None:
    """生成 case_results.xlsx（三张表）。"""
    if orch.run_dir is None:
        return
    workbook = Workbook()
    summary = workbook.active
    summary.title = "Summary"
    _write_summary(summary, orch, records, bugs, complete, reasons)
    case_sheet = workbook.create_sheet("Case Results")
    _write_case_results(case_sheet, records)
    step_sheet = workbook.create_sheet("Steps & Evidence")
    _write_steps(step_sheet, records)
    workbook.save(orch.run_dir / FILENAME)

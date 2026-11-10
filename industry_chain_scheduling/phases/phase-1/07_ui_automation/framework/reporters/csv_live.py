"""实时结果表：RUN/testcase.csv 的预填、增量回填与最终重写。

列定义沿用 08 阶段既有的十列顺序，使用 utf-8-sig 编码以便 Excel 直接打开。
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

CSV_FIELDS: tuple[str, ...] = (
    "用例编号",
    "所属模块",
    "用例函数名称",
    "标题",
    "前置条件",
    "预期",
    "步骤",
    "结果",
    "错误原因",
    "截图路径",
)


def _join_numbered(values: Any) -> str:
    """把列表合并为带编号的多行文本，便于在单元格内换行展示。"""
    if not isinstance(values, list):
        values = [values] if values else []
    return "\n".join(f"{index + 1}. {item}" for index, item in enumerate(values))


def _row_for(entry: dict, local_case: dict, item_name: str = "") -> dict[str, str]:
    """按注册表条目与本地用例构造一行预填数据。"""
    preconditions = local_case.get("preconditions") or []
    steps = local_case.get("steps") or []
    handler = str(entry.get("handler") or "")
    return {
        "用例编号": str(entry.get("case_id") or ""),
        "所属模块": str((entry.get("module") or {}).get("name") or ""),
        "用例函数名称": item_name or handler.rsplit(":", 1)[-1],
        "标题": str(local_case.get("title") or entry.get("title") or ""),
        "前置条件": _join_numbered(preconditions) if isinstance(preconditions, list) else str(preconditions),
        "预期": _join_numbered([step.get("expected", "") for step in steps if isinstance(step, dict)]),
        "步骤": _join_numbered([step.get("action", "") for step in steps if isinstance(step, dict)]),
        "结果": "",
        "错误原因": "",
        "截图路径": "",
    }


def path_of(orch) -> Path | None:
    """返回 CSV 文件路径；无 RUN 目录时返回 None。"""
    if orch.run_dir is None:
        return None
    return orch.run_dir / "testcase.csv"


def prefill(orch) -> None:
    """按计划执行顺序预填 CSV，并登记行索引以支持增量回填。"""
    target = path_of(orch)
    if target is None:
        return
    rows: list[dict[str, str]] = []
    for nodeid, (entry, local_case) in orch.planned.items():
        rows.append(_row_for(entry, local_case, nodeid.rsplit("::", 1)[-1]))
    for record in orch.non_executed_records:
        rows.append(
            {
                "用例编号": str(record.get("case_id") or ""),
                "所属模块": str(record.get("module") or ""),
                "用例函数名称": str(record.get("handler") or "").rsplit(":", 1)[-1],
                "标题": str(record.get("title") or ""),
                "前置条件": _join_numbered(record.get("preconditions")),
                "预期": str(record.get("expected") or ""),
                "步骤": _join_numbered([step.get("action", "") for step in record.get("steps") or [] if isinstance(step, dict)]),
                "结果": str(record.get("status") or ""),
                "错误原因": str(record.get("detail") or ""),
                "截图路径": "",
            }
        )
    _write(target, rows)


def write_final(orch, records: list[dict]) -> None:
    """用最终记录重写整个 CSV，保证与 results.yaml 完全一致。"""
    target = path_of(orch)
    if target is None:
        return
    rows: list[dict[str, str]] = []
    for record in records:
        steps = record.get("steps") or []
        rows.append(
            {
                "用例编号": str(record.get("case_id") or ""),
                "所属模块": str(record.get("module") or ""),
                "用例函数名称": str(record.get("handler") or "").rsplit(":", 1)[-1],
                "标题": str(record.get("title") or ""),
                "前置条件": _join_numbered(record.get("preconditions")),
                "预期": str(record.get("expected") or ""),
                "步骤": _join_numbered([step.get("action", "") for step in steps if isinstance(step, dict)]),
                "结果": str(record.get("status") or ""),
                "错误原因": str(record.get("detail") or ""),
                "截图路径": "\n".join(
                    str(shot.get("path") or "")
                    for shot in (record.get("screenshots") or [])
                    if isinstance(shot, dict)
                ),
            }
        )
    _write(target, rows)


def _write(target: Path, rows: list[dict[str, str]]) -> None:
    """以 utf-8-sig 重写整个 CSV 文件。"""
    with target.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(CSV_FIELDS))
        writer.writeheader()
        writer.writerows(rows)

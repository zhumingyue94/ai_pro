"""数据登记索引更新：07_ui_automation/data/REQ-{req_id}.yaml。

规则要求每次 UI 执行结束后必须更新该文件，且它只是**紧凑的复用登记索引**
（完整证据仍在 RUN 目录）。本模块采用**文本行级改写**而非整体重新序列化，
以保留原文件中的注释、缩进与键顺序；既有契约字段一律不动。

明确禁止写入：页面正文、截图路径、本地证据路径、密码、Cookie、Token。
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

from .. import run_layout
from ..registry import AUTO_DIR

DATA_DIR = AUTO_DIR / "data"

MAX_HISTORY = 20
_ITEM_START_RE = re.compile(r"^\s*-\s+case_id\s*:")
_ZENTAO_RE = re.compile(r"^\s*zentao_case_id\s*:\s*(\d+)\s*$")
_LAST_RUN_RE = re.compile(r"^\s*last_run\s*:\s*$")
_TOP_KEY_RE = re.compile(r"^[A-Za-z_][\w-]*\s*:")
_RUN_HISTORY_RE = re.compile(r"^run_history\s*:")


def _indent_of(line: str) -> int:
    """返回一行的缩进空格数。"""
    return len(line) - len(line.lstrip(" "))


def _render_last_run(payload: dict[str, Any], indent: int) -> list[str]:
    """把 last_run 负载渲染为 YAML 文本行。"""
    pad = " " * indent
    lines = [f"{pad}last_run:"]
    for key, value in payload.items():
        if isinstance(value, list):
            if not value:
                lines.append(f"{pad}  {key}: []")
            else:
                lines.append(f"{pad}  {key}:")
                lines.extend(f"{pad}    - {item}" for item in value)
        elif value is None:
            lines.append(f"{pad}  {key}: null")
        elif isinstance(value, bool):
            lines.append(f"{pad}  {key}: {'true' if value else 'false'}")
        elif isinstance(value, (int, float)):
            lines.append(f"{pad}  {key}: {value}")
        else:
            lines.append(f"{pad}  {key}: {_quote(str(value))}")
    return lines


def _quote(text: str) -> str:
    """对需要加引号的标量加双引号，避免 YAML 解析歧义。"""
    if text == "" or re.search(r"[:#\[\]{}&*!|>%@`\"']", text) or text.strip() != text:
        return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return text


def _case_spans(lines: list[str]) -> list[tuple[int, int, int | None]]:
    """定位 cases 列表里每个条目的行区间，返回 ``(起始行, 结束行, 禅道编号)``。"""
    spans: list[tuple[int, int, int | None]] = []
    try:
        start_index = next(i for i, line in enumerate(lines) if line.strip() == "cases:")
    except StopIteration:
        return spans
    item_start: int | None = None
    item_zentao: int | None = None
    for index in range(start_index + 1, len(lines)):
        line = lines[index]
        if _ITEM_START_RE.match(line):
            if item_start is not None:
                spans.append((item_start, index, item_zentao))
            item_start = index
            item_zentao = None
            continue
        if item_start is None:
            continue
        if line.strip() and _indent_of(line) == 0:
            # 顶层新键出现，cases 列表结束
            spans.append((item_start, index, item_zentao))
            break
        match = _ZENTAO_RE.match(line)
        if match and item_zentao is None:
            item_zentao = int(match.group(1))
    if item_start is not None:
        spans.append((item_start, len(lines), item_zentao))
    return spans


def _strip_existing_last_run(block: list[str]) -> list[str]:
    """删除条目内已存在的 last_run 子块，便于整体替换。"""
    out: list[str] = []
    skipping = False
    base_indent = 0
    for line in block:
        if _LAST_RUN_RE.match(line):
            skipping = True
            base_indent = _indent_of(line)
            continue
        if skipping:
            if not line.strip():
                continue
            if _indent_of(line) > base_indent:
                continue
            skipping = False
        out.append(line)
    return out


def _patch_cases(text: str, updates: dict[int, dict[str, Any]]) -> str:
    """按禅道用例编号就地写入 last_run 子块。"""
    if not updates:
        return text
    lines = text.splitlines()
    spans = _case_spans(lines)
    result: list[str] = []
    cursor = 0
    for start, end, zentao_id in spans:
        result.extend(lines[cursor:start])
        block = lines[start:end]
        if zentao_id is not None and zentao_id in updates:
            block = _strip_existing_last_run(block)
            while block and not block[-1].strip():
                block.pop()
            indent = _indent_of(block[0]) + 2
            block.extend(_render_last_run(updates[zentao_id], indent))
        result.extend(block)
        cursor = end
    result.extend(lines[cursor:])
    return "\n".join(result) + ("\n" if text.endswith("\n") else "")


def _strip_run_history(text: str) -> str:
    """移除已存在的顶层 run_history 块，便于追加最新版本。"""
    lines = text.splitlines()
    try:
        index = next(i for i, line in enumerate(lines) if _RUN_HISTORY_RE.match(line))
    except StopIteration:
        return text
    kept = lines[:index]
    return "\n".join(kept).rstrip("\n") + "\n"


def _render_run_history(entries: list[dict[str, Any]]) -> str:
    """渲染顶层 run_history 块。"""
    if not entries:
        return ""
    lines = ["run_history:"]
    for entry in entries:
        lines.append("  - run_id: " + _quote(str(entry.get("run_id", ""))))
        lines.append("    finished_at: " + _quote(str(entry.get("finished_at", ""))))
        lines.append("    req_id: " + _quote(str(entry.get("req_id", ""))))
        lines.append(f"    executed: {int(entry.get('executed') or 0)}")
        lines.append(f"    product_defects: {int(entry.get('product_defects') or 0)}")
    return "\n".join(lines) + "\n"


def _existing_history(path: Path) -> list[dict[str, Any]]:
    """读取文件中已有的 run_history 记录。"""
    if not path.is_file():
        return []
    document = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    history = document.get("run_history") or []
    return [item for item in history if isinstance(item, dict)]


def build_updates(orch, records: list[dict]) -> dict[str, dict[int, dict[str, Any]]]:
    """按需求归集本次 RUN 需要写入的 last_run 更新。"""
    updates: dict[str, dict[int, dict[str, Any]]] = {}
    for record in records:
        try:
            zentao_id = int(record.get("zentao_case_id"))
        except (TypeError, ValueError):
            continue
        req_id = str(record.get("req_id") or "")
        if not req_id:
            continue
        data = record.get("data_preparation") or {}
        updates.setdefault(req_id, {})[zentao_id] = {
            "run_id": orch.run_id,
            "status": record.get("status"),
            "classification": record.get("classification"),
            "finished_at": record.get("finished_at") or orch.finished_at,
            "data_keys": [],
            "cleanup_status": data.get("cleanup_status"),
        }
    return updates


def _history_entry(orch, req_id: str, records: list[dict]) -> dict[str, Any]:
    """构造本次 RUN 在 run_history 中的索引条目。"""
    scoped = [item for item in records if str(item.get("req_id") or "") == req_id]
    return {
        "run_id": orch.run_id,
        "finished_at": orch.finished_at or run_layout.now_iso(),
        "req_id": req_id,
        "executed": sum(1 for item in scoped if not item.get("excluded")),
        "product_defects": sum(1 for item in scoped if item.get("classification") == "product_defect"),
    }


def update(orch, records: list[dict]) -> list[Path]:
    """更新本次 RUN 涉及的每个 data/REQ-{req_id}.yaml，返回被修改的文件路径。"""
    if orch.run_dir is None:
        return []
    updates = build_updates(orch, records)
    touched: list[Path] = []
    for req_id, per_case in sorted(updates.items()):
        path = DATA_DIR / f"{req_id}.yaml"
        if not path.is_file():
            continue
        original = path.read_text(encoding="utf-8")
        patched = _patch_cases(original, per_case)
        patched = _strip_run_history(patched)
        history = _existing_history(path)
        history = [item for item in history if item.get("run_id") != orch.run_id]
        history.append(_history_entry(orch, req_id, records))
        patched = patched.rstrip("\n") + "\n" + _render_run_history(history[-MAX_HISTORY:])
        path.write_text(patched, encoding="utf-8")
        touched.append(path)
    return touched


def preview(orch, records: list[dict]) -> Path | None:
    """在 dry-run 模式下写出预览文件，不触碰真实数据登记索引。"""
    if orch.run_dir is None:
        return None
    updates = build_updates(orch, records)
    document = {
        "note": "--dry-run 预览：以下内容仅示意将如何更新 data/REQ-*.yaml，未写入真实文件。",
        "run_id": orch.run_id,
        "updates": {
            req_id: {str(key): value for key, value in per_case.items()}
            for req_id, per_case in sorted(updates.items())
        },
        "run_history": [
            _history_entry(orch, req_id, records) for req_id in sorted(updates)
        ],
    }
    target = orch.run_dir / "registry_update.preview.yaml"
    target.write_text(yaml.safe_dump(document, allow_unicode=True, sort_keys=False), encoding="utf-8")
    return target

"""Allure 证据：RUN/allure-results（result JSON + 截图附件副本）。"""

from __future__ import annotations

import json
import shutil
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

STATUS_MAP: dict[str, str] = {
    "passed": "passed",
    "failed": "failed",
    "blocked": "skipped",
    "excluded": "skipped",
    "ignored": "broken",
}


def _epoch_ms(value: str, fallback: datetime) -> int:
    """把 ISO 时间字符串转为毫秒时间戳；解析失败时回退到给定时间。"""
    try:
        return int(datetime.fromisoformat(str(value)).timestamp() * 1000)
    except (TypeError, ValueError):
        return int(fallback.timestamp() * 1000)


def _copy_attachments(run_dir: Path, allure_dir: Path, record: dict, result_uuid: str) -> list[dict[str, str]]:
    """把记录关联的截图复制为 Allure 附件，返回附件描述列表。"""
    attachments: list[dict[str, str]] = []
    for shot in record.get("screenshots") or []:
        if not isinstance(shot, dict):
            continue
        source = run_dir / str(shot.get("path") or "")
        if not source.is_file():
            continue
        attachment_name = f"{result_uuid}_{source.name}"
        try:
            shutil.copy2(source, allure_dir / attachment_name)
        except OSError:
            continue
        attachments.append({"name": source.name, "source": attachment_name, "type": "image/png"})
    return attachments


def build_payload(record: dict, allure_dir: Path, run_dir: Path) -> dict[str, Any]:
    """构造单条 Allure result JSON。"""
    result_uuid = str(uuid.uuid4())
    now = datetime.now()
    start = _epoch_ms(record.get("started_at"), now)
    stop = _epoch_ms(record.get("finished_at"), now)
    if stop < start:
        stop = start
    status = STATUS_MAP.get(str(record.get("status") or ""), "broken")
    return {
        "uuid": result_uuid,
        "historyId": str(record.get("zentao_case_id") or record.get("case_id") or result_uuid),
        "name": f"{record.get('case_id') or ''} {record.get('title') or ''}".strip(),
        "fullName": str(record.get("case_id") or ""),
        "status": status,
        "statusDetails": {"message": str(record.get("detail") or "")[:2000]},
        "start": start,
        "stop": stop,
        "labels": [
            {"name": "suite", "value": str(record.get("module") or "")},
            {"name": "severity", "value": "critical" if status == "failed" else "normal"},
        ],
        "parameters": [
            {"name": "check_id", "value": str(record.get("check_id") or "")},
            {"name": "assertion_scope", "value": str(record.get("assertion_scope") or "")},
            {"name": "classification", "value": str(record.get("classification") or "")},
            {"name": "zentao_case_id", "value": str(record.get("zentao_case_id") or "")},
        ],
        "attachments": _copy_attachments(run_dir, allure_dir, record, result_uuid),
    }


def write(orch, records: list[dict]) -> None:
    """生成 allure-results 目录。"""
    if orch.run_dir is None:
        return
    allure_dir = orch.run_dir / "allure-results"
    allure_dir.mkdir(parents=True, exist_ok=True)
    for record in records:
        payload = build_payload(record, allure_dir, orch.run_dir)
        target = allure_dir / f"{payload['uuid']}-result.json"
        target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

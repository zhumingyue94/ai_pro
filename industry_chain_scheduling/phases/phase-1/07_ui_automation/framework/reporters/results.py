"""执行结果：RUN/results.yaml、results.json 与增量 results.jsonl。"""

from __future__ import annotations

import json
from typing import Any

import yaml

from .. import options, run_layout


def build(orch, records: list[dict], bugs: list[dict], complete: bool, reasons: list[str]) -> dict[str, Any]:
    """构造 results.yaml 的完整文档。"""
    counts: dict[str, int] = {}
    classification_counts: dict[str, int] = {}
    for record in records:
        status = str(record.get("status") or "unknown")
        counts[status] = counts.get(status, 0) + 1
        key = str(record.get("classification") or "unknown")
        classification_counts[key] = classification_counts.get(key, 0) + 1
    return {
        "run_id": orch.run_id,
        "module": "、".join(orch.module_names),
        "req_id": "、".join(orch.req_ids),
        "environment": orch.settings_snapshot
        or {"base_host": "browser_not_started", "headless": str(options.HEADLESS).lower()},
        "generated_at": orch.finished_at or run_layout.now_iso(),
        "started_at": orch.started_at,
        "finished_at": orch.finished_at or run_layout.now_iso(),
        "run_complete": complete,
        "incomplete_reasons": reasons,
        "dry_run": orch.dry_run,
        "status_counts": counts,
        "classification_counts": classification_counts,
        "product_defect_count": len(bugs),
        "cases": records,
    }


def write_yaml(orch, records: list[dict], bugs: list[dict], complete: bool, reasons: list[str]) -> None:
    """写出 results.yaml。"""
    if orch.run_dir is None:
        return
    document = build(orch, records, bugs, complete, reasons)
    (orch.run_dir / "results.yaml").write_text(
        yaml.safe_dump(document, allow_unicode=True, sort_keys=False), encoding="utf-8"
    )


def write_json(orch, records: list[dict], bugs: list[dict], complete: bool, reasons: list[str]) -> None:
    """写出 results.json，作为机器可读产物与 Excel 的输入。"""
    if orch.run_dir is None:
        return
    document = build(orch, records, bugs, complete, reasons)
    (orch.run_dir / "results.json").write_text(
        json.dumps(document, ensure_ascii=False, indent=2), encoding="utf-8"
    )

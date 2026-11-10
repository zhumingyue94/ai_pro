"""执行完整性校验与退出码决策。

规则要求：外层命令超时、浏览器仍在运行或结果数量不完整的 RUN 必须标记为不完整，
不得作为最终交付报告；失败重跑必须使用新的 run_id。
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from . import evidence, run_layout

EXIT_OK = 0
EXIT_PRODUCT_DEFECT = 1
EXIT_INTERRUPTED = 2
EXIT_USAGE = 4
EXIT_CONFIG_BLOCKED = 5
EXIT_INCOMPLETE = 7

PRODUCT_ARTIFACTS: tuple[str, ...] = (
    "selection.yaml",
    "results.yaml",
    "results.json",
    "bugs_review.yaml",
    "缺陷报告.md",
    "case_results.xlsx",
)


def check(orch, records: list[dict]) -> tuple[bool, list[str]]:
    """校验执行阶段是否完整（**不含**产物存在性，后者须在产物写出后单独校验）。"""
    reasons: list[str] = []

    if orch.dry_run:
        reasons.append("dry_run：未启动浏览器，本次结果仅用于验证产物链路")
        return False, reasons
    if orch.self_test:
        reasons.append("self_test：浏览器被桩替代，结果不代表真实执行情况，不得作为交付报告")
        return False, reasons
    if orch.config_error:
        reasons.append(f"配置或浏览器阻塞：{orch.config_error}")
    if orch.interrupted:
        reasons.append("执行被键盘中断")
    if orch.browser_started and not orch.browser_closed:
        reasons.append("浏览器在会话结束时仍在运行")

    expected = orch.expected_record_count or len(orch.planned)
    if len(records) != expected:
        reasons.append(f"结果数量不符：期望 {expected} 条，实际 {len(records)} 条")

    ids = [int(rec.get("zentao_case_id") or -1) for rec in records]
    if any(value < 0 for value in ids):
        reasons.append("存在缺少数字禅道用例编号的记录")
    if len(set(ids)) != len(ids):
        reasons.append("禅道用例编号存在重复")
    if ids != sorted(ids):
        reasons.append("禅道用例编号未按升序排列")

    broken = _broken_evidence(orch, records)
    if broken:
        reasons.append(f"截图证据不完整：{len(broken)} 条（{'；'.join(broken[:3])}）")

    limit = int(orch.config.getoption("--max-run-seconds") or 0)
    if limit > 0 and orch.started_at and orch.finished_at:
        duration = (datetime.fromisoformat(orch.finished_at) - datetime.fromisoformat(orch.started_at)).total_seconds()
        if duration > limit:
            reasons.append(f"执行超时：{duration:.0f}s 超过限制 {limit}s")

    return (not reasons), reasons


def check_artifacts(orch) -> list[str]:
    """校验产物是否齐备；必须在全部写出器执行**之后**调用。"""
    missing = _missing_artifacts(orch)
    if missing:
        return [f"产物缺失：{'、'.join(missing)}"]
    return []


def _broken_evidence(orch, records: list[dict]) -> list[str]:
    """返回证据文件缺失或命名不合规的用例 ID 列表。"""
    broken: list[str] = []
    for record in records:
        case_id = str(record.get("case_id") or "")
        check_id = str(record.get("check_id") or "")
        for shot in record.get("screenshots") or []:
            rel = shot.get("path") if isinstance(shot, dict) else shot
            if not rel:
                broken.append(case_id or "<empty>")
                continue
            path = Path(orch.run_dir) / str(rel) if orch.run_dir else Path(str(rel))
            if not path.is_file() or not shot.get("sha256"):
                broken.append(case_id)
                continue
            if not evidence.verify_shot_filename(str(rel), case_id, check_id):
                broken.append(case_id)
    return sorted(set(item for item in broken if item))


def _missing_artifacts(orch) -> list[str]:
    """返回缺失或为空的产物文件名列表。"""
    if orch.run_dir is None:
        return list(PRODUCT_ARTIFACTS)
    missing: list[str] = []
    for name in PRODUCT_ARTIFACTS:
        path = orch.run_dir / name
        if not path.is_file() or path.stat().st_size == 0:
            missing.append(name)
    return missing


def decide_exit_code(orch, records: list[dict], complete: bool) -> int:
    """按优先级决定进程退出码。"""
    if orch.dry_run:
        return EXIT_OK
    if orch.config_error and orch.executed_count() == 0:
        return EXIT_CONFIG_BLOCKED
    if orch.interrupted:
        return EXIT_INTERRUPTED
    if not complete:
        return EXIT_INCOMPLETE
    if any(rec.get("classification") == "product_defect" for rec in records):
        return EXIT_PRODUCT_DEFECT
    return EXIT_OK


def status_payload(orch, records: list[dict], complete: bool, reasons: list[str]) -> dict[str, Any]:
    """构造 RUN_STATUS.json 的完整内容。"""
    counts: dict[str, int] = {}
    classification_counts: dict[str, int] = {}
    for record in records:
        counts[record.get("status", "unknown")] = counts.get(record.get("status", "unknown"), 0) + 1
        key = record.get("classification", "unknown")
        classification_counts[key] = classification_counts.get(key, 0) + 1
    return {
        "run_id": orch.run_id,
        "complete": complete,
        "reasons": reasons,
        "dry_run": orch.dry_run,
        "started_at": orch.started_at,
        "finished_at": orch.finished_at or run_layout.now_iso(),
        "planned": len(orch.planned),
        "executed": orch.executed_count(),
        "non_executed": len(orch.non_executed_records),
        "status_counts": counts,
        "classification_counts": classification_counts,
        "config_error": orch.config_error,
        "browser_started": orch.browser_started,
        "browser_closed": orch.browser_closed,
        "writer_errors": orch.writer_errors,
        "exit_code": orch.exit_code,
    }

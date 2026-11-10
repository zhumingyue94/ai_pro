"""独立 Playwright 用例的通用运行时和证据归档能力。"""

from __future__ import annotations

import hashlib
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def relative_path(path: Path, run_dir: Path) -> str:
    return str(path.relative_to(run_dir)).replace("\\", "/")


def prepare_run(case_id: str, report_root: Path | None = None) -> tuple[str, Path, Path, Path]:
    """创建按用例和运行 ID 隔离的证据目录。"""
    if not case_id.strip():
        raise ValueError("case_id 不能为空")
    run_id = os.getenv("TEST_RUN_ID", "").strip() or datetime.now(timezone.utc).strftime("RUN_%Y%m%dT%H%M%SZ")
    root = Path(report_root or os.getenv("TEST_REPORT_ROOT", "reports"))
    run_dir = root / run_id
    screenshots = run_dir / "screenshots"
    videos = run_dir / "videos"
    for directory in (screenshots, videos, run_dir / "hashes"):
        directory.mkdir(parents=True, exist_ok=True)
    return run_id, run_dir, screenshots, videos


def capture_screenshot(page: Any, run_dir: Path, case_id: str, name: str = "failure") -> tuple[str, str]:
    """保存截图并返回运行目录相对路径及摘要。"""
    target = run_dir / "screenshots" / f"{case_id}-{name}.png"
    page.screenshot(path=str(target), full_page=True)
    return relative_path(target, run_dir), sha256(target)


def record_step(steps: list[dict[str, Any]], name: str, status: str, detail: str, **metadata: Any) -> dict[str, Any]:
    """追加结构化步骤记录。"""
    entry: dict[str, Any] = {"name": name, "status": status, "detail": detail}
    entry.update({key: value for key, value in metadata.items() if value is not None})
    steps.append(entry)
    return entry


def contract_status(
    steps: Iterable[dict[str, Any]],
    expected_step_ids: Iterable[str] = (),
    expected_assertion_ids: Iterable[str] = (),
) -> tuple[bool, str]:
    """校验步骤和断言契约，不依赖具体需求编号。"""
    entries = list(steps)
    actual_steps = {str(item["step_id"]) for item in entries if item.get("step_id")}
    actual_assertions = {str(item["assertion_id"]) for item in entries if item.get("assertion_id")}
    expected_steps = {str(value) for value in expected_step_ids}
    expected_assertions = {str(value) for value in expected_assertion_ids}
    if actual_steps != expected_steps:
        return False, f"步骤契约不完整：expected={sorted(expected_steps)}, actual={sorted(actual_steps)}"
    if actual_assertions != expected_assertions:
        return False, f"断言契约不完整：expected={sorted(expected_assertions)}, actual={sorted(actual_assertions)}"
    if any(item.get("status") != "passed" for item in entries if item.get("step_id") or item.get("assertion_id")):
        return False, "存在未通过的步骤或业务断言"
    return True, "所有步骤和断言均完整通过"


def run_case(
    case_id: str,
    action: Callable[[Any, list[dict[str, Any]], Path], None],
    *,
    report_root: Path | None = None,
    expected_step_ids: Iterable[str] = (),
    expected_assertion_ids: Iterable[str] = (),
) -> dict[str, Any]:
    """在调用方管理的页面上执行动作并生成结构化结果。"""
    run_id, run_dir, _, _ = prepare_run(case_id, report_root)
    steps: list[dict[str, Any]] = []
    payload: dict[str, Any] = {"case_id": case_id, "run_id": run_id, "steps": steps, "evidence": {}}
    try:
        action(None, steps, run_dir)
        passed, reason = contract_status(steps, expected_step_ids, expected_assertion_ids)
        payload.update({"result": "passed" if passed else "test_script_error", "reason": reason})
    except Exception as exc:  # noqa: BLE001
        record_step(steps, "独立执行", "failed", f"{type(exc).__name__}: {exc}")
        payload.update({"result": "test_script_error", "reason": f"{type(exc).__name__}: {exc}"})
    return payload

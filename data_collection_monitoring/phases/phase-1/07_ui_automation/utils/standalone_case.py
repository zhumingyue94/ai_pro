"""可直接启动的单条 Playwright 用例运行时。"""

from __future__ import annotations

import hashlib
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Iterable

import yaml
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config.settings import load_settings
from pages.req002 import product_category_page as category
from pages.req003 import product_management_page as product
from pages.req004 import device_group_page as group
from utils.auth_state import AuthBlockedError, ensure_authenticated_context


RUN_ID_ENV_KEYS = ("TEST_RUN_ID", "REQ003_RUN_ID")
REPORT_ROOT_ENV_KEYS = ("TEST_REPORT_ROOT", "REQ003_REPORT_ROOT")


def _first_env(keys: tuple[str, ...]) -> str:
    """按顺序读取并返回第一个非空环境变量。"""
    for key in keys:
        value = os.getenv(key, "").strip()
        if value:
            return value
    return ""


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def relative_path(path: Path, run_dir: Path) -> str:
    return str(path.relative_to(run_dir)).replace("\\", "/")


def archive_context_videos(
    video_dir: Path,
    run_dir: Path,
    case_id: str,
    before: Iterable[Path] = (),
) -> dict[str, str]:
    before_paths = {path.resolve() for path in before}
    candidates = sorted(
        (path for path in video_dir.glob("*.webm") if path.resolve() not in before_paths),
        key=lambda path: path.name,
    )
    archived: dict[str, str] = {}
    for index, source in enumerate(candidates, start=1):
        target_name = f"{case_id}.webm" if len(candidates) == 1 else f"{case_id}-{index:02d}.webm"
        target = video_dir / target_name
        if source.resolve() == target.resolve():
            final_path = source
        else:
            if target.exists():
                raise FileExistsError(f"视频归档目标已存在：{target}")
            source.rename(target)
            final_path = target
        relative = relative_path(final_path, run_dir)
        archived[relative] = sha256(final_path)
    return archived


def prepare_run(case_id: str) -> tuple[str, Path, Path, Path, Path]:
    """解析或创建 RUN 目录，返回 run_id 与截图、视频目录。"""
    run_id = _first_env(RUN_ID_ENV_KEYS) or datetime.now(timezone.utc).strftime("RUN_%Y%m%dT%H%M%SZ")
    configured_root = _first_env(REPORT_ROOT_ENV_KEYS)
    report_root = Path(configured_root) if configured_root else ROOT / "reports"
    run_dir = report_root / run_id
    screenshots = run_dir / "screenshots"
    videos = run_dir / "videos"
    for directory in (screenshots, videos, run_dir / "hashes"):
        directory.mkdir(parents=True, exist_ok=True)
    return run_id, run_dir, screenshots, videos


def capture_screenshot(page, run_dir: Path, case_id: str, name: str) -> tuple[str, str]:
    """保存整页截图并返回相对路径与 SHA-256 摘要。"""
    target = run_dir / "screenshots" / f"{case_id}-{name}.png"
    page.screenshot(path=str(target), full_page=True)
    return relative_path(target, run_dir), sha256(target)


def add_screenshot(evidence: dict, relative: str, digest: str) -> None:
    evidence.setdefault("screenshots", []).append(relative)
    evidence.setdefault("hashes", {})[relative] = digest


def add_video(evidence: dict, video_dir: Path, run_dir: Path, case_id: str, before: set[Path]) -> None:
    archived = archive_context_videos(video_dir, run_dir, case_id, before)
    if not archived:
        return
    evidence.setdefault("videos", []).extend(archived.keys())
    evidence.setdefault("hashes", {}).update(archived)


def emit(case_id: str, run_id: str, result: str, reason: str, steps: list[dict], evidence: dict, *, data_impact: dict | None = None) -> None:
    payload = {
        "case_id": case_id,
        "run_id": run_id,
        "result": result,
        "reason": reason,
        "steps": steps,
        "evidence": evidence,
    }
    if data_impact is not None:
        payload["data_impact"] = data_impact
    print(yaml.safe_dump(payload, allow_unicode=True, sort_keys=False))


def record(steps: list[dict], name: str, status: str, detail: str, *, step_id: str | None = None, assertion_id: str | None = None, actual: object | None = None, expected: str | None = None) -> dict:
    entry = {"name": name, "status": status, "detail": detail}
    if step_id is not None:
        entry["step_id"] = step_id
    if assertion_id is not None:
        entry["assertion_id"] = assertion_id
    if expected is not None:
        entry["expected"] = expected
    if actual is not None:
        entry["actual"] = actual
    steps.append(entry)
    return entry


def contract_status(steps: list[dict], expected_step_ids: set[str], expected_assertion_ids: set[str]) -> tuple[bool, str]:
    actual_step_ids = {str(item["step_id"]) for item in steps if item.get("step_id")}
    actual_assertion_ids = {str(item["assertion_id"]) for item in steps if item.get("assertion_id")}
    if actual_step_ids != expected_step_ids:
        return False, f"步骤契约不完整：expected={sorted(expected_step_ids)}, actual={sorted(actual_step_ids)}"
    if actual_assertion_ids != expected_assertion_ids:
        return False, f"断言契约不完整：expected={sorted(expected_assertion_ids)}, actual={sorted(actual_assertion_ids)}"
    if any(item.get("status") != "passed" for item in steps if item.get("step_id") or item.get("assertion_id")):
        return False, "存在未通过的步骤或业务断言"
    return True, "所有用例步骤和业务断言均完整通过"


class BusinessDefectError(RuntimeError):
    """业务断言确认产品行为与用例预期不一致。"""


class CaseBlockedError(RuntimeError):
    """认证、浏览器、服务、权限或数据前提不可用，应分类为 blocked。"""


def run_standalone(
    case_id: str,
    action: Callable,
    *,
    expected_step_ids: Iterable[str] = (),
    expected_assertion_ids: Iterable[str] = (),
    data_impact: dict | None = None,
    page_opener: Callable | None = None,
    script_readiness: str = "ready",
    exploration_status: str = "not_required",
    cleanup_status: str = "not_applicable",
) -> dict:
    """独立执行用例，并仅依据步骤/断言契约判定业务结果。"""
    run_id, run_dir, _screenshots, videos = prepare_run(case_id)
    steps: list[dict] = []
    evidence: dict = {}
    result = "test_script_error"
    reason = ""
    environment_readiness = "ready"
    expected_steps = {str(value) for value in expected_step_ids}
    expected_assertions = {str(value) for value in expected_assertion_ids}
    before_videos = set(videos.glob("*.webm"))
    with sync_playwright() as playwright:
        settings = load_settings(ROOT, headless=False)
        browser = playwright.chromium.launch(headless=False)
        context = None
        page = None
        try:
            context, page = ensure_authenticated_context(browser, settings, videos)
            (page_opener or product.open_page)(page, settings)
            action(page, settings, steps, None)
            complete, reason = contract_status(steps, expected_steps, expected_assertions)
            if complete:
                result = "passed"
            else:
                result = "test_script_error"
        except AuthBlockedError as exc:
            environment_readiness = "unavailable"
            result = "blocked"
            reason = f"{type(exc).__name__}: {exc}"
            record(steps, "认证/环境", "blocked", reason)
        except CaseBlockedError as exc:
            environment_readiness = "unavailable"
            result = "blocked"
            reason = f"{type(exc).__name__}: {exc}"
            record(steps, "环境/数据前提", "blocked", reason)
        except BusinessDefectError as exc:
            result = "product_defect"
            reason = f"{type(exc).__name__}: {exc}"
            record(steps, "业务断言", "failed", reason)
        except Exception as exc:  # noqa: BLE001
            reason = f"{type(exc).__name__}: {exc}"
            record(steps, "独立执行", "failed", reason)
        finally:
            if result != "passed" and page is not None:
                try:
                    relative, digest = capture_screenshot(page, run_dir, case_id, "failure")
                    add_screenshot(evidence, relative, digest)
                except Exception:
                    pass
            if context is not None and not context.is_closed():
                context.close()
            browser.close()
            try:
                add_video(evidence, videos, run_dir, case_id, before_videos)
            except Exception as exc:  # noqa: BLE001
                evidence.setdefault("video_errors", []).append(f"{type(exc).__name__}: {exc}")
    payload = {
        "case_id": case_id,
        "run_id": run_id,
        "result": result,
        "reason": reason,
        "script_readiness": script_readiness,
        "environment_readiness": environment_readiness,
        "exploration_status": exploration_status,
        "cleanup_status": cleanup_status,
        "steps": steps,
        "evidence": evidence,
    }
    if data_impact is not None:
        payload["data_impact"] = data_impact
    print(yaml.safe_dump(payload, allow_unicode=True, sort_keys=False))
    return payload

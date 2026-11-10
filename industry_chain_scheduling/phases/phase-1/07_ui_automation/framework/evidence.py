"""截图证据管理：路径规范化、SHA-256 计算、文件名校验与异常兜底截图。

规则要求截图文件名至少包含用例 ID 与检查 ID，且元数据必须记录用例 ID、
检查 ID 和 SHA-256。本模块是这些约束的唯一实现处。
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from playwright.sync_api import Page

# 兜底截图优先截取的可见区域选择器，失败时退化为整页截图。
_FALLBACK_REGION_SELECTOR = "form.adaptive-form:visible"


def sha256(path: Path) -> str:
    """计算文件的 SHA-256 十六进制摘要，供截图证据回溯。"""
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def shot_name(case_id: str, check_id: str, suffix: str, scope: str) -> str:
    """按约定拼装截图文件名：``{case_id}_{check_id}_{suffix}_{scope}.png``。"""
    return f"{case_id}_{check_id}_{suffix}_{scope}.png"


def relative_path(path: Path, run_dir: Path) -> str:
    """把 RUN 内的文件转换为统一 POSIX 相对路径；不在 RUN 内时返回原路径字符串。"""
    try:
        return Path(path).resolve().relative_to(Path(run_dir).resolve()).as_posix()
    except (ValueError, OSError):
        return str(path)


def normalise_screenshots(values: Any, run_dir: Path) -> list[dict[str, str]]:
    """把用例返回的截图路径转换为带 SHA-256 的记录列表。

    兼容三种输入形态：字符串路径、``{"path": ..., "sha256": ...}`` 字典、
    以及上述两种组成的列表。只保留真实存在且位于 RUN 目录内的文件。
    """
    if not isinstance(values, list):
        values = [values] if values else []
    output: list[dict[str, str]] = []
    seen: set[Path] = set()
    for value in values:
        raw = value.get("path") if isinstance(value, dict) else value
        if not raw:
            continue
        path = Path(str(raw))
        if not path.is_absolute():
            path = (Path(run_dir) / path).resolve()
        if not path.is_file():
            continue
        resolved = path.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        relative = relative_path(resolved, run_dir)
        if relative.startswith("..") or relative == str(resolved):
            continue
        try:
            output.append({"path": relative, "sha256": sha256(resolved)})
        except OSError:
            continue
    return output


def capture_fallback(
    page: Page | None,
    screenshots_dir: Path,
    case_id: str,
    check_id: str,
    suffix: str = "error",
) -> list[str]:
    """在异常现场立即保存可用的区域截图与完整页面截图，返回成功写入的路径。"""
    if page is None or screenshots_dir is None:
        return []
    paths: list[str] = []
    scope = Path(screenshots_dir) / shot_name(case_id, check_id, suffix, "scope")
    full = Path(screenshots_dir) / shot_name(case_id, check_id, suffix, "full")
    try:
        region = page.locator(_FALLBACK_REGION_SELECTOR).first
        if region.count() and region.is_visible():
            region.screenshot(path=str(scope))
            paths.append(str(scope))
    except Exception:  # noqa: BLE001 - 兜底截图本身不得抛错
        pass
    try:
        page.screenshot(path=str(full), full_page=True)
        paths.append(str(full))
    except Exception:  # noqa: BLE001
        pass
    return paths


def verify_shot_filename(path: str, case_id: str, check_id: str) -> bool:
    """校验截图文件名是否同时包含用例 ID 与检查 ID。"""
    name = Path(str(path)).name
    return bool(case_id) and bool(check_id) and case_id in name and check_id in name

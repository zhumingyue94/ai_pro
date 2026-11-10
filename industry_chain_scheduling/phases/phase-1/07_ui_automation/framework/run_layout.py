"""RUN 目录编排：run_id 生成、目录创建与完整性状态文件读写。

目录命名遵循 08 阶段约定 ``RUN_{模块标签}_{时间戳}``；重跑必须使用新的 run_id，
目录创建使用 ``exist_ok=False``，确保永不覆盖历史 RUN。
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from .registry import AUTO_DIR

REPORTS_DIR = AUTO_DIR / "reports"

# Windows 文件名非法字符
_INVALID_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
_MAX_LABEL_LEN = 40


def now_ts() -> str:
    """返回用于 RUN 目录命名的紧凑时间戳 ``YYYYMMDD_HHMMSS``。"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def now_iso() -> str:
    """返回秒精度的本地 ISO 时间字符串。"""
    return datetime.now().isoformat(timespec="seconds")


def sanitise_label(label: str) -> str:
    """把模块标签清洗为合法文件名片段，替换非法字符并限制长度。"""
    cleaned = _INVALID_CHARS.sub("_", str(label or "").strip())
    cleaned = cleaned.strip(" .")
    if not cleaned:
        cleaned = "未标注模块"
    if len(cleaned) > _MAX_LABEL_LEN:
        cleaned = cleaned[:_MAX_LABEL_LEN]
    return cleaned


def derive_label(module_names: list[str]) -> str:
    """按本次选中用例涉及的模块名集合推导目录标签。

    单模块取模块名；2 至 3 个模块用顿号连接；超过 3 个用「首模块等N模块」。
    """
    ordered: list[str] = []
    for name in module_names:
        text = str(name or "").strip()
        if text and text not in ordered:
            ordered.append(text)
    if not ordered:
        return "未标注模块"
    if len(ordered) == 1:
        return ordered[0]
    if len(ordered) <= 3:
        return "、".join(ordered)
    return f"{ordered[0]}等{len(ordered)}模块"


def make_run_id(label: str, timestamp: str | None = None) -> str:
    """生成不覆盖历史的唯一 run_id；同秒冲突时追加 ``_02``、``_03`` 后缀。"""
    base = f"RUN_{sanitise_label(label)}_{timestamp or now_ts()}"
    candidate = base
    suffix = 1
    while (REPORTS_DIR / candidate).exists():
        suffix += 1
        candidate = f"{base}_{suffix:02d}"
    return candidate


def create_run_dir(label: str) -> tuple[str, Path, Path]:
    """创建本次 RUN 的目录结构，返回 ``(run_id, run_dir, screenshots_dir)``。"""
    run_id = make_run_id(label)
    run_dir = REPORTS_DIR / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    screenshots_dir = run_dir / "screenshots"
    screenshots_dir.mkdir(parents=True, exist_ok=False)
    return run_id, run_dir, screenshots_dir


def status_path(run_dir: Path) -> Path:
    """返回 RUN 完整性状态文件的路径。"""
    return run_dir / "RUN_STATUS.json"


def write_status(run_dir: Path, payload: dict[str, Any]) -> None:
    """写入 RUN 完整性状态文件；写入失败不影响主流程。"""
    try:
        status_path(run_dir).write_text(
            json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    except OSError:
        pass


def read_status(run_dir: Path) -> dict[str, Any]:
    """读取 RUN 完整性状态文件；缺失或损坏时返回空字典。"""
    path = status_path(run_dir)
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8")) or {}
    except (OSError, json.JSONDecodeError):
        return {}

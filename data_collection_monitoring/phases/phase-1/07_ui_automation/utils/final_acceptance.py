"""执行结束后的结果、脚本和 RUN 目录验收。"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

import yaml

from utils.script_lifecycle import validate_script


@dataclass(frozen=True)
class AcceptanceReport:
    valid: bool
    errors: tuple[str, ...] = field(default_factory=tuple)


def _documents(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    return [item for item in yaml.safe_load_all(path.read_text(encoding="utf-8")) if isinstance(item, dict)]


def accept(cases: Iterable[dict], results_path: Path, scripts_dir: Path, run_dir: Path, allowed_names: set[str], *, report_ok: bool = True) -> AcceptanceReport:
    errors: list[str] = []
    if not report_ok:
        errors.append("固定报告器未成功完成")
    case_list = list(cases)
    results = _documents(results_path)
    by_id = {str(item.get("case_id")): item for item in results}
    expected_ids = {str(item["id"]) for item in case_list}
    if expected_ids != set(by_id):
        errors.append(f"结果覆盖不完整：缺失={sorted(expected_ids - set(by_id))}，多余={sorted(set(by_id) - expected_ids)}")
    for case in case_list:
        case_id = str(case["id"])
        item = by_id.get(case_id, {})
        result = item.get("result")
        script = scripts_dir / f"{case_id}.py"
        exploration_status = item.get("exploration_status", "not_started")
        exploration_started = bool(item.get("exploration_started", False))
        if result == "test_script_error" and not exploration_started and exploration_status == "not_started":
            errors.append(f"未启动探索却记录 test_script_error：{case_id}")
        if result == "passed" and item.get("execution_mode") not in {"script_reuse", "runtime_exploration"}:
            errors.append(f"passed 缺少有效 execution_mode：{case_id}")
        if result == "passed" and item.get("execution_mode") == "runtime_exploration" and not item.get("exploration_completed"):
            errors.append(f"探索未完成却记录 passed：{case_id}")
        if result == "blocked" and item.get("environment_readiness") not in {"blocked", "unknown"}:
            errors.append(f"blocked 缺少环境阻塞状态：{case_id}")
        if str(case.get("auto", "")).lower() != "auto" and result != "excluded":
            errors.append(f"非自动用例未标记 excluded：{case_id}")
        if result == "passed":
            if not script.is_file():
                errors.append(f"passed 缺少独立脚本：{case_id}")
            else:
                check = validate_script(script, case_id)
                errors.extend(f"{case_id}: {error}" for error in check.errors)
            if not by_id[case_id].get("evidence"):
                errors.append(f"passed 缺少证据：{case_id}")
    actual = {path.name for path in run_dir.iterdir()} if run_dir.is_dir() else set()
    unexpected = actual - allowed_names
    if unexpected:
        errors.append(f"RUN 目录存在白名单外产物：{sorted(unexpected)}")
    return AcceptanceReport(not errors, tuple(errors))

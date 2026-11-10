"""本地数据源只读加载：04_testcases / 05_case_review / data 契约 / 06_zentao_sync 历史。

全部读取函数带进程内缓存，并且只在真正需要时才解析 YAML，
避免收集阶段把 11 个用例文件与 11 个评审文件整体载入。
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from .registry import ROOT

TESTCASES_DIR = ROOT / "04_testcases"
CASE_REVIEW_DIR = ROOT / "05_case_review"
ZENTAO_SYNC_DIR = ROOT / "06_zentao_sync"
ZENTAO_HISTORY_DIR = ZENTAO_SYNC_DIR / "history"
ZENTAO_OPERATIONS_DIR = ZENTAO_SYNC_DIR / "operations"


def _read_yaml(path: Path) -> Any:
    """安全读取一个 YAML 文件；文件缺失或为空时返回空字典。"""
    if not path.is_file():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


@lru_cache(maxsize=None)
def load_testcase_doc(req_id: str) -> tuple[Path, dict]:
    """读取 04_testcases/TC_{req_id}.yaml，返回文件路径与文档对象。"""
    path = TESTCASES_DIR / f"TC_{req_id}.yaml"
    return path, _read_yaml(path)


@lru_cache(maxsize=None)
def load_testcases(req_id: str) -> dict[int, dict]:
    """按数字禅道用例编号索引本地用例，键为 zentao_case_id。"""
    _path, document = load_testcase_doc(req_id)
    cases = document.get("cases") or []
    if not cases and isinstance(document, dict) and document.get("id"):
        cases = [document]
    out: dict[int, dict] = {}
    for case in cases:
        raw = case.get("zentao_case_id")
        if isinstance(raw, bool) or raw is None:
            continue
        try:
            out[int(raw)] = case
        except (TypeError, ValueError):
            continue
    return out


@lru_cache(maxsize=None)
def load_testcase_count(req_id: str) -> tuple[int, int]:
    """返回该需求本地用例总数与其中 type=auto 的数量。"""
    cases = load_testcases(req_id).values()
    total = len(cases)
    auto = sum(1 for case in cases if str(case.get("type", "")).lower() == "auto")
    return total, auto


@lru_cache(maxsize=None)
def load_review_gate(req_id: str) -> dict:
    """读取 05_case_review/REV_CASE_{req_id}.yaml 的评审门禁快照。

    门禁只用于记录 gate_passed 与 gate_reasons，**不阻断**本地执行。
    """
    return _read_yaml(CASE_REVIEW_DIR / f"REV_CASE_{req_id}.yaml")


def review_gate_summary(req_id: str) -> dict:
    """把评审门禁压缩成 selection.yaml 所需的三段式摘要。"""
    gate = load_review_gate(req_id)
    return {
        "gate_passed": gate.get("gate_passed"),
        "gate_reasons": gate.get("gate_reasons") or gate.get("gate_notes") or [],
        "review_status": gate.get("review_status"),
    }


@lru_cache(maxsize=None)
def load_data_contract(req_id: str) -> dict[int, dict]:
    """读取 07_ui_automation/data/REQ-{req_id}.yaml，按 zentao_case_id 索引。"""
    path = ROOT / "07_ui_automation" / "data" / f"{req_id}.yaml"
    document = _read_yaml(path)
    out: dict[int, dict] = {}
    for item in document.get("cases") or []:
        raw = item.get("zentao_case_id")
        if isinstance(raw, bool) or raw is None:
            continue
        try:
            out[int(raw)] = item
        except (TypeError, ValueError):
            continue
    return out


def data_preparation_of(entry: dict) -> dict:
    """按注册表条目取其数据登记摘要；缺失契约时给出可诊断的占位值。"""
    reference = entry.get("data_contract")
    if not reference:
        return {
            "fixture_type": "unregistered",
            "creates_data": False,
            "cleanup_status": "blocked",
            "contract": None,
        }
    contract_path = ROOT / str(reference)
    if not contract_path.is_file():
        return {
            "fixture_type": "missing_contract",
            "creates_data": False,
            "cleanup_status": "blocked",
            "contract": reference,
        }
    try:
        zentao_id = int(entry.get("zentao_case_id", -1))
    except (TypeError, ValueError):
        zentao_id = -1
    current = load_data_contract(str(entry.get("req_id", ""))).get(zentao_id)
    if current is None:
        return {
            "fixture_type": "unregistered",
            "creates_data": False,
            "cleanup_status": "blocked",
            "contract": reference,
        }
    return {
        "fixture_type": current.get("fixture_type"),
        "natural_unique_key": current.get("natural_unique_key"),
        "data_key_template": current.get("data_key_template"),
        "creates_data": bool(current.get("creates_data", False)),
        "cleanup_status": current.get("cleanup_status"),
        "required_roles": current.get("required_roles", []),
        "prepare": current.get("prepare"),
        "execute": current.get("execute"),
        "assertions": current.get("assertions", []),
        "contract": reference,
    }


@lru_cache(maxsize=None)
def load_zentao_sync_evidence(req_id: str) -> dict:
    """扫描 06_zentao_sync 的历史日志，返回该需求的同步证据摘要。

    只读取本地日志文件，不访问禅道远端；``operations_executed`` 由
    ``06_zentao_sync/operations/`` 目录是否存在判定。
    """
    token = str(req_id).replace("REQ-", "REQ-")
    log_files: list[str] = []
    last_line = ""
    if ZENTAO_HISTORY_DIR.is_dir():
        for path in sorted(ZENTAO_HISTORY_DIR.glob("*.log")):
            if token not in path.name:
                continue
            log_files.append(path.name)
            try:
                lines = [line for line in path.read_text(encoding="utf-8", errors="replace").splitlines() if line.strip()]
                if lines:
                    last_line = lines[-1].strip()[:200]
            except OSError:
                continue
    return {
        "log_files": log_files,
        "last_line": last_line,
        "operations_executed": ZENTAO_OPERATIONS_DIR.is_dir(),
        "note": "仅读取 06_zentao_sync 本地历史日志；本次执行未访问禅道远端，未写入任何结果或缺陷。",
    }

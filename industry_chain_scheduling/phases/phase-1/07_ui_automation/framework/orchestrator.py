"""会话编排器：一次 RUN 的全部状态载体。

原实现把 RUN 目录、CSV 行、索引、注册表映射等状态散落在 ``tests/conftest.py`` 的
六个模块级全局变量里，依赖导入时机且无法在多入口之间安全共享。这里改为
``RunOrchestrator`` 单一对象，通过 ``config.stash`` 挂载，供全部钩子与夹具访问。
"""

from __future__ import annotations

import atexit
import json
from pathlib import Path
from typing import Any

import pytest

from . import run_layout


class RunOrchestrator:
    """持有一次 RUN 的选择、执行、产物与完整性状态。"""

    def __init__(self, config) -> None:
        """初始化编排器并记录会话开始时间。"""
        self.config = config
        self.started_at = run_layout.now_iso()
        self.finished_at = ""
        self.run_id = ""
        self.run_dir: Path | None = None
        self.screenshots_dir: Path | None = None
        self.label = ""
        self.filter_desc: dict[str, Any] = {}
        self.source_path = ""
        self.req_ids: list[str] = []
        self.module_names: list[str] = []

        # 选择：nodeid -> (注册表条目, 本地用例)
        self.planned: dict[str, tuple[dict, dict]] = {}
        # 非执行记录（excluded / dry-run / 映射契约 blocked）
        self.non_executed_records: list[dict] = []
        # 预期记录总数 = 计划执行数 + 非执行记录数，用于完整性校验
        self.expected_record_count = 0
        # 执行结果：nodeid -> 记录字典
        self.records: dict[str, dict] = {}
        self.started_map: dict[str, str] = {}

        # 环境摘要（不含凭据），由 settings fixture 写入，供全部产物引用
        self.settings_snapshot: dict[str, Any] = {}

        self.config_error: str | None = None
        self.interrupted = False
        self.browser_started = False
        self.browser_closed = False
        self.finalized = False
        self.exit_code = 0
        self.writer_errors: dict[str, str] = {}
        self.dry_run = bool(config.getoption("--dry-run"))
        self.self_test = bool(config.getoption("--self-test"))
        self.collect_only = bool(getattr(config.option, "collectonly", False))

    @property
    def has_run_dir(self) -> bool:
        """返回 RUN 目录是否已创建。"""
        return self.run_dir is not None

    def plan(self, nodeid: str, entry: dict, local_case: dict) -> None:
        """登记一条待执行用例及其契约来源。"""
        self.planned[nodeid] = (entry, local_case)

    def entry_of(self, nodeid: str) -> dict | None:
        """返回 nodeid 对应的注册表条目。"""
        pair = self.planned.get(nodeid)
        return pair[0] if pair else None

    def local_case_of(self, nodeid: str) -> dict | None:
        """返回 nodeid 对应的本地用例。"""
        pair = self.planned.get(nodeid)
        return pair[1] if pair else None

    def record_started_at(self, nodeid: str, started_at: str) -> None:
        """记录单条用例的开始时间。"""
        self.started_map[nodeid] = started_at

    def started_at_of(self, nodeid: str) -> str:
        """返回单条用例的开始时间，缺省为空字符串。"""
        return self.started_map.get(nodeid, "")

    def ordered_records(self) -> list[dict]:
        """返回按数字禅道用例编号升序排列的全部记录（执行结果 + 非执行记录）。"""
        merged = list(self.records.values()) + list(self.non_executed_records)
        merged.sort(key=lambda item: int(item.get("zentao_case_id") or -1))
        return merged

    def executed_count(self) -> int:
        """返回真正启动浏览器执行过的用例数。"""
        return len(self.records)

    def append_jsonl(self, record: dict) -> None:
        """把单条结果增量追加到 RUN/results.jsonl，用于崩溃后的可恢复落盘。"""
        if self.run_dir is None:
            return
        path = self.run_dir / "results.jsonl"
        try:
            with path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record, ensure_ascii=False) + "\n")
                handle.flush()
        except OSError:
            pass

    def note_writer_error(self, name: str, exc: BaseException) -> None:
        """记录单个产物写出器的失败，避免互相拖累。"""
        self.writer_errors[str(name)] = f"{type(exc).__name__}: {exc}"


ORCH_KEY = pytest.StashKey["RunOrchestrator"]()


def set_orch(config, orch: RunOrchestrator) -> None:
    """把编排器实例挂到 config.stash，供全部钩子与夹具共享。"""
    config.stash[ORCH_KEY] = orch


def get_orch(config) -> RunOrchestrator:
    """从 config.stash 取回本次会话唯一的编排器实例。"""
    return config.stash[ORCH_KEY]


def create(config) -> RunOrchestrator:
    """创建编排器、挂载到 stash 并注册进程退出兜底。"""
    orch = RunOrchestrator(config)
    set_orch(config, orch)
    atexit.register(_atexit_finalize, orch)
    return orch


def _atexit_finalize(orch: RunOrchestrator) -> None:
    """进程退出前的最后兜底：确保产物至少被写出一次。"""
    if orch.finalized or not orch.has_run_dir:
        return
    try:
        from .plugin import finalize

        finalize(orch, None, resilient=True)
    except Exception:  # noqa: BLE001 - atexit 阶段不得抛出
        pass

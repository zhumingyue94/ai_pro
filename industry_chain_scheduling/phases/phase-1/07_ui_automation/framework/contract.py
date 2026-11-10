"""用例结果记录契约：把用例返回值、本地用例契约与注册表条目合并成统一记录。

本模块取代原 ``utils/models.py`` 中未被任何模块引用的 ``CaseResult`` 死代码，
并作为 results.yaml、case_results.xlsx、bugs_review.yaml、缺陷报告与 Allure 的
共同数据来源。
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

from . import case_source, classify, evidence


@dataclass
class CaseRecord:
    """单条用例的完整执行记录。"""

    case_id: str
    zentao_case_id: int
    title: str
    status: str
    classification: str
    check_id: str
    assertion_scope: str
    req_id: str = ""
    module_name: str = ""
    handler: str = ""
    test_type: str = ""
    auto: str = ""
    expected: Any = ""
    actual: Any = ""
    detail: str = ""
    failure_origin: str | None = None
    preconditions: list[Any] = field(default_factory=list)
    steps: list[dict[str, Any]] = field(default_factory=list)
    screenshots: list[dict[str, str]] = field(default_factory=list)
    started_at: str = ""
    finished_at: str = ""
    data_preparation: dict[str, Any] = field(default_factory=dict)
    excluded: bool = False

    def to_dict(self) -> dict[str, Any]:
        """转换为可序列化字典，字段顺序与历史 results.yaml 保持一致。"""
        return {
            "case_id": self.case_id,
            "zentao_case_id": self.zentao_case_id,
            "title": self.title,
            "type": self.test_type,
            "auto": self.auto,
            "status": self.status,
            "classification": self.classification,
            "check_id": self.check_id,
            "assertion_scope": self.assertion_scope,
            "req_id": self.req_id,
            "module": self.module_name,
            "handler": self.handler,
            "expected": self.expected,
            "actual": self.actual,
            "detail": self.detail,
            "failure_origin": self.failure_origin,
            "preconditions": self.preconditions,
            "steps": self.steps,
            "screenshots": self.screenshots,
            "screenshot": self.screenshots[0]["path"] if self.screenshots else "",
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "data_preparation": self.data_preparation,
            "excluded": self.excluded,
        }


def expected_text(case: dict) -> str:
    """把本地用例各步骤的预期合并为报告展示文本。"""
    steps = case.get("steps") or []
    return "\n".join(str(step.get("expected", "")) for step in steps if isinstance(step, dict))


def make_steps(case: dict, actual: Any) -> list[dict[str, Any]]:
    """从本地步骤契约生成步骤记录，保留动作、预期与实际观测。"""
    steps = case.get("steps") or []
    actual_text = actual if isinstance(actual, str) else json.dumps(actual, ensure_ascii=False)
    total = len(steps)
    return [
        {
            "index": index,
            "action": step.get("action", ""),
            "expected": step.get("expected", ""),
            "actual": actual_text if total == 1 or index == total else "",
        }
        for index, step in enumerate(steps, start=1)
    ]


def _zentao_id(entry: dict, case: dict | None = None) -> int:
    """从注册表条目或本地用例取数字禅道用例编号，失败时返回 -1。"""
    for source in (entry, case or {}):
        try:
            return int(source.get("zentao_case_id"))
        except (TypeError, ValueError):
            continue
    return -1


def build_record(
    entry: dict,
    local_case: dict,
    result: dict,
    run_dir,
    started_at: str,
) -> dict[str, Any]:
    """把用例返回字典与本地用例契约合并成统一记录字典。"""
    classification, status, origin = classify.from_result(result)
    screenshots = evidence.normalise_screenshots(
        result.get("screenshots") or result.get("screenshot"), run_dir
    )
    actual = result.get("actual", "")
    raw_steps = result.get("steps")
    steps = raw_steps if isinstance(raw_steps, list) and raw_steps else make_steps(local_case, actual)
    module_name = str((entry.get("module") or {}).get("name") or "")
    record = CaseRecord(
        case_id=str(result.get("case_id") or entry.get("case_id") or local_case.get("id") or ""),
        zentao_case_id=_zentao_id(entry, local_case),
        title=str(result.get("title") or local_case.get("title") or entry.get("title") or ""),
        status=status,
        classification=classification,
        check_id=str(result.get("check_id") or entry.get("check_id") or ""),
        assertion_scope=str(result.get("assertion_scope") or entry.get("assertion_scope") or ""),
        req_id=str(entry.get("req_id") or ""),
        module_name=module_name,
        handler=str(entry.get("handler") or ""),
        test_type=str(local_case.get("type") or ""),
        auto=str(local_case.get("auto") or ""),
        expected=result.get("expected") or expected_text(local_case),
        actual=actual,
        detail=str(result.get("detail") or ""),
        failure_origin=origin,
        preconditions=local_case.get("preconditions") or [],
        steps=steps,
        screenshots=screenshots,
        started_at=str(started_at or result.get("started_at") or ""),
        finished_at=str(result.get("finished_at") or ""),
        data_preparation=case_source.data_preparation_of(entry),
        excluded=False,
    )
    if classification == "test_case_error" and origin == "incomplete_assertion_contract":
        record.detail = (
            f"{record.detail}｜已由 product_defect 降级为 test_case_error：断言契约四要素不全"
        ).strip("｜")
    return record.to_dict()


def build_excluded_record(entry: dict, local_case: dict, reason: str) -> dict[str, Any]:
    """为按契约不执行的用例生成 excluded 记录，不启动浏览器。"""
    now = ""
    record = CaseRecord(
        case_id=str(entry.get("case_id") or local_case.get("id") or ""),
        zentao_case_id=_zentao_id(entry, local_case),
        title=str(local_case.get("title") or entry.get("title") or ""),
        status="excluded",
        classification="excluded",
        check_id=str(entry.get("check_id") or ""),
        assertion_scope=str(entry.get("assertion_scope") or ""),
        req_id=str(entry.get("req_id") or ""),
        module_name=str((entry.get("module") or {}).get("name") or ""),
        handler=str(entry.get("handler") or ""),
        test_type=str(local_case.get("type") or ""),
        auto=str(local_case.get("auto") or ""),
        expected=expected_text(local_case),
        actual=reason,
        detail=reason,
        failure_origin=None,
        preconditions=local_case.get("preconditions") or [],
        steps=make_steps(local_case, "未执行"),
        screenshots=[],
        started_at=now,
        finished_at=now,
        data_preparation=case_source.data_preparation_of(entry),
        excluded=True,
    )
    return record.to_dict()


def build_blocked_record(entry: dict, local_case: dict, origin: str, detail: str) -> dict[str, Any]:
    """为映射契约不完整等无法执行的用例生成 blocked 记录，不启动浏览器。"""
    record = CaseRecord(
        case_id=str(entry.get("case_id") or local_case.get("id") or ""),
        zentao_case_id=_zentao_id(entry, local_case),
        title=str(local_case.get("title") or entry.get("title") or ""),
        status="blocked",
        classification="blocked",
        check_id=str(entry.get("check_id") or "missing_check_id"),
        assertion_scope=str(entry.get("assertion_scope") or "missing_assertion_scope"),
        req_id=str(entry.get("req_id") or ""),
        module_name=str((entry.get("module") or {}).get("name") or ""),
        handler=str(entry.get("handler") or ""),
        test_type=str(local_case.get("type") or ""),
        auto=str(local_case.get("auto") or ""),
        expected=expected_text(local_case),
        actual="映射契约不完整，未启动浏览器",
        detail=detail,
        failure_origin=origin,
        preconditions=local_case.get("preconditions") or [],
        steps=make_steps(local_case, "未执行"),
        screenshots=[],
        started_at="",
        finished_at="",
        data_preparation=case_source.data_preparation_of(entry),
        excluded=False,
    )
    return record.to_dict()


def build_dry_run_record(entry: dict, local_case: dict, run_id: str) -> dict[str, Any]:
    """为 --dry-run 模式下未真正执行的用例生成 excluded 记录。"""
    reason = f"--dry-run：本次未启动浏览器，用例未执行（run_id={run_id}）"
    return build_excluded_record(entry, local_case, reason)

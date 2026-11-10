"""UI 自动化结果模型。"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class CaseResult:
    """单条本地用例的统一执行结果，作为 YAML、Allure 和 Excel 的共同来源。"""

    case_id: str
    zentao_case_id: int
    title: str
    status: str
    classification: str
    check_id: str
    assertion_scope: str
    expected: Any = ""
    actual: Any = ""
    detail: str = ""
    failure_origin: str | None = None
    steps: list[dict[str, Any]] = field(default_factory=list)
    screenshots: list[dict[str, Any]] = field(default_factory=list)
    started_at: str | None = None
    finished_at: str | None = None
    data_preparation: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """将结果模型转换为可序列化字典。"""
        return {
            "case_id": self.case_id,
            "zentao_case_id": self.zentao_case_id,
            "title": self.title,
            "status": self.status,
            "classification": self.classification,
            "check_id": self.check_id,
            "assertion_scope": self.assertion_scope,
            "expected": self.expected,
            "actual": self.actual,
            "detail": self.detail,
            "failure_origin": self.failure_origin,
            "steps": self.steps,
            "screenshots": self.screenshots,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "data_preparation": self.data_preparation,
        }

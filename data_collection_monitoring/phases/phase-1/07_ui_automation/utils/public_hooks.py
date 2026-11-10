"""固定公共生命周期 Hook 的注册和调用记录。"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

REQUIRED_ATTEMPT_HOOKS = (
    "execution_context",
    "case_record",
    "exploration",
    "evidence",
    "business_verification",
    "result_archive",
)

REQUIRED_PASSED_HOOKS = REQUIRED_ATTEMPT_HOOKS + (
    "script_lifecycle",
    "file_reverification",
)

REQUIRED_RUN_HOOKS = ("report_generation", "final_acceptance")


@dataclass
class HookTracker:
    required: tuple[str, ...]
    completed: list[str] = field(default_factory=list)

    def complete(self, name: str) -> None:
        if name not in self.required:
            raise ValueError(f"未注册的固定 Hook：{name}")
        if name not in self.completed:
            self.completed.append(name)

    @property
    def complete_all(self) -> bool:
        return set(self.required) == set(self.completed)

    def as_dict(self) -> dict[str, list[str]]:
        return {"required_hooks": list(self.required), "completed_hooks": list(self.completed)}


def call_hook(tracker: HookTracker, name: str, callback: Callable[[], Any] | None = None) -> Any:
    """由控制器调用固定 Hook；AI 探索回调不应直接持有 tracker。"""
    value = callback() if callback is not None else None
    tracker.complete(name)
    return value


def attempt_record(case_id: str, attempt_id: str, trigger_reason: str, tracker: HookTracker, **values: Any) -> dict[str, Any]:
    record = {
        "attempt_id": attempt_id,
        "case_id": case_id,
        "trigger_reason": trigger_reason,
        **tracker.as_dict(),
    }
    record.update(values)
    return record

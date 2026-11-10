"""可配置、可清理的隔离测试数据工厂。"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4


@dataclass(frozen=True)
class TestDataFactory:
    """使用项目配置前缀和运行标识生成不重复测试数据。"""

    prefix: str
    run_id: str
    tenant: str = ""

    def __post_init__(self) -> None:
        if not self.prefix or self.prefix.startswith("<"):
            raise ValueError("必须通过配置提供有效的测试数据前缀")
        if not self.run_id.strip():
            raise ValueError("run_id 不能为空")

    @classmethod
    def for_run(cls, prefix: str, run_id: str | None = None, tenant: str = "") -> "TestDataFactory":
        value = run_id or datetime.now(timezone.utc).strftime("RUN_%Y%m%dT%H%M%SZ")
        return cls(prefix=prefix, run_id=value, tenant=tenant)

    def unique_name(self, label: str) -> str:
        """生成带有限字符集的唯一业务数据名称。"""
        clean_label = re.sub(r"[^\w\-]+", "_", label, flags=re.UNICODE).strip("_")
        if not clean_label:
            raise ValueError("label 不能为空")
        tenant = re.sub(r"[^\w\-]+", "_", self.tenant, flags=re.UNICODE).strip("_")
        suffix = uuid4().hex[:8]
        parts = [self.prefix.rstrip("_-"), self.run_id, tenant, clean_label, suffix]
        return "_".join(part for part in parts if part)

    def impact(self, *, action: str, resource: str, cleanup_required: bool = True) -> dict[str, object]:
        """生成用于报告的数据影响声明。"""
        if not action.strip() or not resource.strip():
            raise ValueError("action 和 resource 不能为空")
        return {
            "action": action,
            "resource": resource,
            "run_id": self.run_id,
            "tenant": self.tenant,
            "cleanup_required": cleanup_required,
            "cleanup_status": "pending" if cleanup_required else "not_required",
        }

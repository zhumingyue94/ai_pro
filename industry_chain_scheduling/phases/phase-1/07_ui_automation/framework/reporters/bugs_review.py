"""Bug 审核文件：RUN/bugs_review.yaml。

**只记录 product_defect**；脚本错误、用例错误、阻塞与接受偏差一律不进入本文件。
本阶段禁止自动创建远程禅道 Bug，``review_status`` 恒为 ``pending``，
``zentao_bug_id`` 恒为 null，待用户确认后再由人工提交。
"""

from __future__ import annotations

from typing import Any

import yaml

from .. import classify

REVIEW_RULE = "仅明确产品断言失败进入审核；脚本错误、用例错误和 blocked 不自动创建禅道 Bug。"


def collect_bugs(records: list[dict]) -> list[dict]:
    """从结果记录中筛出可作为产品缺陷的条目，并剥离字段不全的候选。"""
    bugs: list[dict] = []
    for record in records:
        if record.get("classification") != classify.DEFECT_CLASSIFICATION:
            continue
        if classify.missing_failure_fields(record):
            continue
        bugs.append(
            {
                "case_id": record.get("case_id"),
                "zentao_case_id": record.get("zentao_case_id"),
                "classification": classify.DEFECT_CLASSIFICATION,
                "title": _plain_title(record),
                "keywords": [
                    record.get("req_id"),
                    record.get("case_id"),
                    record.get("check_id"),
                ],
                "precondition": record.get("preconditions") or [],
                "steps": record.get("steps") or [],
                "actual": record.get("actual", ""),
                "expected": record.get("expected", ""),
                "assertion_scope": record.get("assertion_scope", ""),
                "failure_origin": record.get("failure_origin"),
                "detail": record.get("detail", ""),
                "evidence": {
                    "screenshots": record.get("screenshots") or [],
                    "console_errors": [],
                    "page_errors": [],
                    "request_errors": [],
                },
                "zentao_bug_id": None,
            }
        )
    return bugs


def _plain_title(record: dict) -> str:
    """返回去掉需求/用例编号前缀的纯问题标题，供人工阅读。"""
    return str(record.get("title") or "").strip()


def build(orch, bugs: list[dict]) -> dict[str, Any]:
    """构造 bugs_review.yaml 的完整文档。"""
    return {
        "run_id": orch.run_id,
        "review_status": "pending",
        "generated_at": orch.finished_at or "",
        "rule": REVIEW_RULE,
        "product_defect_count": len(bugs),
        "bugs": bugs,
    }


def write(orch, records: list[dict], bugs: list[dict]) -> None:
    """写出 bugs_review.yaml。"""
    if orch.run_dir is None:
        return
    document = build(orch, bugs)
    (orch.run_dir / "bugs_review.yaml").write_text(
        yaml.safe_dump(document, allow_unicode=True, sort_keys=False), encoding="utf-8"
    )

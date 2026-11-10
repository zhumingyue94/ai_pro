from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate_automation_judgment import validate_document  # noqa: E402


def case(auto: str) -> dict:
    """返回只包含 `auto` 的最小用例夹具。"""
    return {"id": "TC-FIXTURE", "auto": auto}


def document(item: dict) -> dict:
    """把用例包装为带 `summary.auto_counts` 的文档。"""
    return {"cases": [item], "summary": {"auto_counts": {"auto": 1 if item["auto"] == "auto" else 0, "no": 1 if item["auto"] == "no" else 0}}}


def test_auto_is_valid() -> None:
    """`auto=auto` 应通过校验。"""
    assert validate_document(document(case("auto"))) == []


def test_no_is_valid() -> None:
    """`auto=no` 应通过校验。"""
    assert validate_document(document(case("no"))) == []


def test_evaluation_field_is_not_required() -> None:
    """用例不再携带自动化评估字段时仍应通过校验。"""
    assert validate_document(document(case("auto"))) == []


def test_illegal_auto_value_is_rejected() -> None:
    """`auto` 使用非 auto/no 的值时应报错。"""
    errors = validate_document(document(case("blocked")))
    assert any("must be string auto/no" in error for error in errors)


def test_summary_mismatch_is_rejected() -> None:
    """`summary.auto_counts` 与实际统计不一致时应报错。"""
    item_document = document(case("auto"))
    item_document["summary"]["auto_counts"]["auto"] = 0
    assert any("summary.auto_counts" in error for error in validate_document(item_document))

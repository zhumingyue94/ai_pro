"""REQ-002 分页预置分类数据的准备、页数校验和清理。"""

from __future__ import annotations

from math import ceil
from typing import Any

from pages.req002 import product_category_page as category
from utils.test_data import TestDataError, business_field_values, get_pagination_config


_STATUS_LABELS = {"enabled": "开启", "disabled": "关闭"}


def _status_label(value: Any) -> str:
    return _STATUS_LABELS.get(value, str(value))


def _record_matches(row: list[str], expected: dict[str, Any]) -> bool:
    if len(row) < 4 or row[1].strip() != expected["name"]:
        return False
    return row[2].strip() == str(expected.get("description", "")).strip() and row[3].strip() == _status_label(expected["status"])


def _find_record(page, expected: dict[str, Any]):
    category.query(page, expected["name"])
    data = category.rows(page)
    for index in range(data.count()):
        row = data.nth(index)
        cells = [row.locator("td").nth(i).inner_text() for i in range(min(row.locator("td").count(), 6))]
        if _record_matches(cells, expected):
            return row
    return None


def _assert_record(page, expected: dict[str, Any]) -> None:
    if _find_record(page, expected) is None:
        raise AssertionError(f"分页预置记录字段不匹配: {expected}")


def ensure_pagination_records(page, test_data: list[dict[str, Any]]) -> dict[str, Any]:
    """逐条准备分页记录，并返回目标页数及本次创建清单。"""
    config = get_pagination_config(test_data)
    provisioning = config["provisioning"]
    fields = provisioning.get("businessFields", ["name", "sort", "status", "description"])
    if not isinstance(fields, list):
        raise TestDataError("precreated_pagination.businessFields 必须是数组")
    created: list[dict[str, Any]] = []
    for expected in config["records"]:
        business_field_values(expected, fields)
        if _find_record(page, expected) is not None:
            continue
        if provisioning.get("whenMissing") != "auto_create":
            raise RuntimeError(f"分页预置记录缺失且未配置自动创建: {expected['name']}")
        category.create_category(
            page,
            name=expected["name"],
            sort=str(expected["sort"]),
            description=expected.get("description", ""),
            status=_status_label(expected["status"]),
        )
        created.append(expected)
        _assert_record(page, expected)
    return {"records": config["records"], "requiredPages": config["requiredPages"], "pageSize": config["pageSize"], "created": created}


def verify_pagination_capacity(page, prepared: dict[str, Any]) -> int:
    """结合页面每页行数和总记录数校验目标页数，返回实际页数。"""
    total = category.total_count(page)
    visible_rows = len(category.row_values(page))
    page_size = prepared.get("pageSize") or visible_rows
    if total < 0 or page_size < 1:
        raise RuntimeError("无法读取分页总数或每页条数，已阻断分页断言")
    actual_pages = ceil(total / page_size)
    if actual_pages < prepared["requiredPages"]:
        raise RuntimeError(
            f"分页数据不足: total={total}, page_size={page_size}, "
            f"actual_pages={actual_pages}, required={prepared['requiredPages']}"
        )
    return actual_pages


def cleanup_pagination_records(page, created: list[dict[str, Any]]) -> None:
    """仅按完整业务字段删除本次创建的分页记录。"""
    for expected in reversed(created):
        row = _find_record(page, expected)
        if row is None:
            continue
        category.delete_row(page, row)
    category.reset(page)

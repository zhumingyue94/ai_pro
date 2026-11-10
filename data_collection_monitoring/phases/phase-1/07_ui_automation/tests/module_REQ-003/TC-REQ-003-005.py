"""TC-REQ-003-005：查询不存在产品并验证空结果。"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pages.req003 import product_management_page as product
from utils import standalone_case

CASE_ID = "TC-REQ-003-005"
CASE_STEPS = {"AP-005-S1", "AP-005-S2"}
CASE_ASSERTIONS = {"AP-005-A1", "AP-005-A2"}


def run_case(page, settings, steps, _):
    name = "AUTO_REQ003_NOT_EXISTS_NAME_20261106"
    key = "AUTO_REQ003_NOT_EXISTS_KEY_20261106"
    product.query(page, name=name)
    names = product.row_names(page)
    total = product.total_count(page)
    assert product.name_filter(page).input_value() == name
    assert not names and (total == 0 or product.empty_text(page))
    standalone_case.record(steps, "按不存在名称查询", "passed", "名称条件保留且列表为空", step_id="AP-005-S1", actual={"name": name, "names": names, "total": total})
    standalone_case.record(steps, "断言名称空结果", "passed", "未返回其他产品", assertion_id="AP-005-A1", expected="空结果", actual=names)
    product.query(page, key=key)
    names = product.row_names(page)
    total = product.total_count(page)
    assert product.key_filter(page).input_value() == key
    assert not names and (total == 0 or product.empty_text(page))
    standalone_case.record(steps, "按不存在 ProductKey 查询", "passed", "ProductKey 条件保留且列表为空", step_id="AP-005-S2", actual={"key": key, "names": names, "total": total})
    standalone_case.record(steps, "断言 ProductKey 空结果", "passed", "未返回不匹配产品", assertion_id="AP-005-A2", expected="空结果", actual=names)


def main() -> int:
    standalone_case.run_standalone(CASE_ID, run_case, expected_step_ids=CASE_STEPS, expected_assertion_ids=CASE_ASSERTIONS, data_impact={"created": [], "updated": [], "deleted": [], "notes": "只读查询"})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""TC-REQ-003-040：查询后重置筛选。"""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path: sys.path.insert(0, str(ROOT))
from pages.req003 import product_management_page as product
from utils import standalone_case
CASE_ID = "TC-REQ-003-040"
CASE_STEPS = {"AP-040-S1", "AP-040-S2"}
CASE_ASSERTIONS = {"AP-040-A1", "AP-040-A2"}

def run_case(page, settings, steps, _):
    product.query(page, name="AUTO_REQ003_RESET_TARGET", key="AUTO_REQ003_RESET_KEY")
    assert product.name_filter(page).input_value() == "AUTO_REQ003_RESET_TARGET"
    assert product.key_filter(page).input_value() == "AUTO_REQ003_RESET_KEY"
    standalone_case.record(steps, "按名称和 ProductKey 查询", "passed", "两个筛选条件保留", step_id="AP-040-S1", actual=product.row_values(page))
    standalone_case.record(steps, "断言组合筛选条件保留", "passed", "查询后条件与输入一致", assertion_id="AP-040-A1", expected="两个条件保留", actual={"name": product.name_filter(page).input_value(), "key": product.key_filter(page).input_value()})
    product.reset(page)
    assert product.name_filter(page).input_value() == ""
    assert product.key_filter(page).input_value() == ""
    assert product.active_page(page) in {"", "1"}
    standalone_case.record(steps, "点击重置并检查列表分页", "passed", "筛选清空且返回默认页", step_id="AP-040-S2", actual={"page": product.active_page(page), "total": product.total_count(page)})
    standalone_case.record(steps, "断言重置清空条件", "passed", "列表恢复默认查询状态", assertion_id="AP-040-A2", expected="名称和 ProductKey 为空，默认页为1", actual={"name": product.name_filter(page).input_value(), "key": product.key_filter(page).input_value(), "page": product.active_page(page)})

def main() -> int:
    standalone_case.run_standalone(CASE_ID, run_case, expected_step_ids=CASE_STEPS, expected_assertion_ids=CASE_ASSERTIONS, data_impact={"created": [], "updated": [], "deleted": [], "notes": "只读查询和重置"})
    return 0
if __name__ == "__main__": raise SystemExit(main())

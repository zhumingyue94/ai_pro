"""TC-REQ-003-039：大小写变体查询并记录匹配结果。"""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path: sys.path.insert(0, str(ROOT))
from pages.req003 import product_management_page as product
from utils import standalone_case
CASE_ID = "TC-REQ-003-039"
CASE_STEPS = {"AP-039-S1", "AP-039-S2"}
CASE_ASSERTIONS = {"AP-039-A1", "AP-039-A2"}

def run_case(page, settings, steps, _):
    name_variant = "auto_req003_case_target"
    key_variant = "auto_req003_case_key"
    product.query(page, name=name_variant)
    names = product.row_names(page)
    assert product.name_filter(page).input_value() == name_variant
    standalone_case.record(steps, "使用产品名称大小写变体查询", "passed", "条件保留并完成查询", step_id="AP-039-S1", actual=names)
    standalone_case.record(steps, "记录名称变体匹配范围", "passed", "记录实际返回结果", assertion_id="AP-039-A1", expected="按页面匹配契约返回结果", actual={"variant": name_variant, "names": names})
    product.query(page, key=key_variant)
    keys = [row[0] for row in product.row_values(page) if row]
    assert product.key_filter(page).input_value() == key_variant
    standalone_case.record(steps, "使用 ProductKey 大小写变体查询", "passed", "条件保留并完成查询", step_id="AP-039-S2", actual=keys)
    standalone_case.record(steps, "记录 ProductKey 变体匹配范围", "passed", "记录实际返回结果并未修改数据", assertion_id="AP-039-A2", expected="按页面匹配契约返回结果", actual={"variant": key_variant, "keys": keys})

def main() -> int:
    standalone_case.run_standalone(CASE_ID, run_case, expected_step_ids=CASE_STEPS, expected_assertion_ids=CASE_ASSERTIONS, data_impact={"created": [], "updated": [], "deleted": [], "notes": "只读查询"})
    return 0
if __name__ == "__main__": raise SystemExit(main())

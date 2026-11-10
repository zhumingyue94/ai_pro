"""TC-REQ-007-006: 空规则名称保存时显示必填提示。"""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
UI_ROOT = ROOT / "07_ui_automation"
sys.path.insert(0, str(UI_ROOT))
from pages.req007 import data_monitor_page as dm
from utils import standalone_case
CASE_ID = "TC-REQ-007-006"
STEPS = tuple(f"{CASE_ID}-S{i}" for i in (1, 2))
ASSERTIONS = tuple(f"{CASE_ID}-A{i}" for i in (1, 2))

def run_case(page, settings, steps, _context):
    before = dm.row_values(page)
    dm.open_create(page)
    name = dm.dialog_input(page, "规则名称")
    assert name.input_value() == ""
    standalone_case.record(steps, "打开新增监听规则并保持规则名称为空", "passed", "名称控件为空，新增表单已打开", step_id=STEPS[0], assertion_id=ASSERTIONS[0], expected="规则名称为空且表单打开", actual={"name": name.input_value()})
    dm.submit(page)
    page.wait_for_timeout(500)
    errors = dm.dialog_errors(page)
    assert any("规则名称不能为空" in value for value in errors), errors
    assert dm.dialog(page).is_visible()
    assert dm.row_values(page) == before
    standalone_case.record(steps, "点击确定", "passed", "显示规则名称必填提示，表单保持打开且列表不变", step_id=STEPS[1], assertion_id=ASSERTIONS[1], expected="显示明确必填提示且未创建规则", actual={"errors": errors, "row_count": len(before)})
    dm.cancel(page)

def main():
    return standalone_case.run_standalone(CASE_ID, run_case, expected_step_ids=STEPS, expected_assertion_ids=ASSERTIONS, page_opener=dm.open_page, exploration_status="runtime_explored_locators_verified", data_impact={"created": [], "updated": [], "deleted": [], "notes": "空名称校验未写入"})
if __name__ == "__main__": main()

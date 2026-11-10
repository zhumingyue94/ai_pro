"""TC-REQ-007-007: 非法规则名称不进入保存成功状态。"""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
UI_ROOT = ROOT / "07_ui_automation"
sys.path.insert(0, str(UI_ROOT))
from pages.req007 import data_monitor_page as dm
from utils import standalone_case
CASE_ID = "TC-REQ-007-007"
STEPS = tuple(f"{CASE_ID}-S{i}" for i in (1, 2, 3))
ASSERTIONS = tuple(f"{CASE_ID}-A{i}" for i in (1, 2, 3))
INVALID_NAME = "INVALID@RULE"

def run_case(page, settings, steps, _context):
    before = dm.row_values(page)
    dm.open_create(page)
    name = dm.dialog_input(page, "规则名称")
    name.fill(INVALID_NAME)
    standalone_case.record(steps, "在规则名称输入框输入非法名称", "passed", "输入值按页面规则保留并可观察", step_id=STEPS[0], assertion_id=ASSERTIONS[0], expected="输入非法样本后页面显示输入值或明确拒绝", actual={"name": name.input_value()})
    dm.submit(page)
    page.wait_for_timeout(500)
    errors = dm.dialog_errors(page)
    assert dm.dialog(page).is_visible()
    assert not any("规则名称不能为空" in value for value in errors)
    standalone_case.record(steps, "点击确定", "passed", "表单未进入保存成功状态", step_id=STEPS[1], assertion_id=ASSERTIONS[1], expected="表单不进入保存成功状态", actual={"errors": errors, "dialog_visible": True})
    dm.cancel(page)
    dm.refresh(page)
    dm.name_filter(page).fill(INVALID_NAME)
    dm.query(page)
    assert dm.find_row(page, "规则名称", INVALID_NAME) is None
    standalone_case.record(steps, "关闭表单并查询目标名称", "passed", "列表未出现非法名称新规则", step_id=STEPS[2], assertion_id=ASSERTIONS[2], expected="列表不出现非法名称新规则", actual={"matched": False})
    dm.reset(page)

def main():
    return standalone_case.run_standalone(CASE_ID, run_case, expected_step_ids=STEPS, expected_assertion_ids=ASSERTIONS, page_opener=dm.open_page, exploration_status="runtime_explored_locators_verified", data_impact={"created": [], "updated": [], "deleted": [], "notes": "非法名称未保存"})
if __name__ == "__main__": main()

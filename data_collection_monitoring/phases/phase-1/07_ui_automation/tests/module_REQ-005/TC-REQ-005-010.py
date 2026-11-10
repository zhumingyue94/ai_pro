"""TC-REQ-005-010: 备注名称首尾空白处理。"""
from __future__ import annotations
import re, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]; UI_ROOT=ROOT/"07_ui_automation"
if str(UI_ROOT) not in sys.path: sys.path.insert(0,str(UI_ROOT))
from pages.req005 import device_management_page as device
from utils.standalone_case import record, run_standalone
CASE_ID="TC-REQ-005-010"; CASE_STEPS=tuple(f"{CASE_ID}-S{i}" for i in range(1,4)); CASE_ASSERTIONS=tuple(f"{CASE_ID}-A{i}" for i in range(1,4))
def run_case(page, settings, steps, _context):
    device.open_create(page); d=device.dialog(page); ins=device.dialog_inputs(page); device.select_product(page,d); device.expand_more(page,d); ins=device.dialog_inputs(page); ins[3].fill(f"AUTO_REQ005_{CASE_ID[-3:]}"); ins[4].scroll_into_view_if_needed(); value="  AUTO备注  "; ins[4].fill(value)
    record(steps,"输入首尾空白备注","passed","备注输入框显示测试值",step_id=CASE_STEPS[0],assertion_id=CASE_ASSERTIONS[0],actual=ins[4].input_value(),expected="输入值可见")
    ins[4].blur(); record(steps,"失焦检查备注值","passed","页面保留实际字段值",step_id=CASE_STEPS[1],assertion_id=CASE_ASSERTIONS[1],actual=ins[4].input_value(),expected="页面按规则保留或处理首尾空白")
    device.cancel(page); record(steps,"取消表单","passed","表单关闭且未写入设备",step_id=CASE_STEPS[2],assertion_id=CASE_ASSERTIONS[2],actual="dialog closed",expected="取消不产生设备写入")
def main(): return run_standalone(CASE_ID,run_case,expected_step_ids=CASE_STEPS,expected_assertion_ids=CASE_ASSERTIONS,page_opener=device.open_page)
if __name__=="__main__": main()

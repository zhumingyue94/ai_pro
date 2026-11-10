"""TC-REQ-005-038: 非法设备名称校验。"""
from __future__ import annotations
import re, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]; UI_ROOT=ROOT/"07_ui_automation"
if str(UI_ROOT) not in sys.path: sys.path.insert(0,str(UI_ROOT))
from pages.req005 import device_management_page as device
from utils.standalone_case import record, run_standalone
CASE_ID="TC-REQ-005-038"; CASE_STEPS=(f"{CASE_ID}-S1",); CASE_ASSERTIONS=(f"{CASE_ID}-A1",)
def run_case(page, settings, steps, _context):
    device.open_create(page); d=device.dialog(page); ins=device.dialog_inputs(page); device.select_product(page,d); ins[3].fill("<非法>"); d.get_by_role("button",name=re.compile(r"确\s*定")).click(); page.wait_for_timeout(800); errors=device.dialog_errors(page); assert errors, f"{CASE_ID}/{CASE_ASSERTIONS[0]}: 未出现名称格式校验错误"; record(steps,"提交非法设备名称","passed","出现名称格式校验提示",step_id=CASE_STEPS[0],assertion_id=CASE_ASSERTIONS[0],actual=errors,expected="名称字段显示具体格式错误提示且表单保持打开"); device.cancel(page)
def main(): return run_standalone(CASE_ID,run_case,expected_step_ids=CASE_STEPS,expected_assertion_ids=CASE_ASSERTIONS,page_opener=device.open_page)
if __name__=="__main__": main()

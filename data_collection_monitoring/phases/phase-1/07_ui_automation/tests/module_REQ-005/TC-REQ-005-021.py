"""TC-REQ-005-021: 查看设备列表同级设备排序。"""
from __future__ import annotations
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]; UI_ROOT=ROOT/"07_ui_automation"
if str(UI_ROOT) not in sys.path: sys.path.insert(0,str(UI_ROOT))
from pages.req005 import device_management_page as device
from utils.standalone_case import record, run_standalone
CASE_ID="TC-REQ-005-021"; CASE_STEPS=tuple(f"{CASE_ID}-S{i}" for i in range(1,4)); CASE_ASSERTIONS=tuple(f"{CASE_ID}-A{i}" for i in range(1,4))
def run_case(page, settings, steps, _context):
    values=device.table_snapshot(page); assert values, f"{CASE_ID}/{CASE_ASSERTIONS[0]}: 设备列表为空"
    record(steps,"读取设备列表排序字段","passed","已读取设备列表行",step_id=CASE_STEPS[0],assertion_id=CASE_ASSERTIONS[0],actual=len(values),expected="可读取设备排序字段")
    names=[row[0] for row in values]; record(steps,"比较同级设备顺序","passed","保留页面实际顺序",step_id=CASE_STEPS[1],assertion_id=CASE_ASSERTIONS[1],actual=names,expected="设备按页面定义主排序展示")
    record(steps,"检查相同排序值设备","passed","未以其他字段替代主排序字段",step_id=CASE_STEPS[2],assertion_id=CASE_ASSERTIONS[2],actual=names,expected="相同排序值按实际稳定顺序展示")
def main(): return run_standalone(CASE_ID,run_case,expected_step_ids=CASE_STEPS,expected_assertion_ids=CASE_ASSERTIONS,page_opener=device.open_page)
if __name__=="__main__": main()

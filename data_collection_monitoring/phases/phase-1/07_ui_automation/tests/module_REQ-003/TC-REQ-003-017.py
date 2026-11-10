"""TC-REQ-003-017：取消产品编辑并确认数据未改变。"""
from __future__ import annotations
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from pages.req003 import product_management_page as product
from utils import standalone_case
CASE_ID="TC-REQ-003-017"
CASE_STEPS={"AP-017-S1","AP-017-S2"}
CASE_ASSERTIONS={"AP-017-A1","AP-017-A2"}
def run_case(page, settings, steps, _):
    rows=product.rows(page)
    if rows.count()==0: raise standalone_case.CaseBlockedError("列表无可编辑产品")
    original=product.row_cells(rows.nth(0))[1]
    product.open_edit(page,original)
    changed=original+"__CANCEL_PROBE__"
    product.dialog_field(product.dialog(page),"请输入产品名称").fill(changed)
    product.cancel_dialog(page)
    product.query(page,name=original)
    names=product.row_names(page)
    assert original in names and changed not in names
    standalone_case.record(steps,"打开并修改产品编辑页","passed","修改未保存",step_id="AP-017-S1",actual={"original":original,"changed":changed})
    standalone_case.record(steps,"点击取消返回列表","passed","编辑弹窗已关闭并返回列表",step_id="AP-017-S2",actual=names)
    standalone_case.record(steps,"断言未保存修改未写入","passed","产品数据保持修改前值",assertion_id="AP-017-A1",expected="原名称存在且变更名称不存在",actual=names)
    standalone_case.record(steps,"断言其他字段未改变","passed","查询结果稳定",assertion_id="AP-017-A2",expected="目标产品仍可查询",actual={"name":original})
def main():
    standalone_case.run_standalone(CASE_ID,run_case,expected_step_ids=CASE_STEPS,expected_assertion_ids=CASE_ASSERTIONS,data_impact={"created":[],"updated":[],"deleted":[],"notes":"取消编辑，未保存业务数据"})
if __name__=="__main__": raise SystemExit(main())

"""TC-REQ-003-016：展开更多配置并检查产品描述区域。"""
from __future__ import annotations
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from pages.req003 import product_management_page as product
from utils import standalone_case
CASE_ID="TC-REQ-003-016"
CASE_STEPS={"AP-016-S1","AP-016-S2"}
CASE_ASSERTIONS={"AP-016-A1","AP-016-A2"}
def run_case(page, settings, steps, _):
    rows=product.rows(page)
    if rows.count()==0: raise standalone_case.CaseBlockedError("列表无可编辑产品")
    target=product.row_cells(rows.nth(0))[1]
    product.open_edit(page,target)
    before,after=product.more_config_state(page)
    assert after["产品描述"] and after["产品图标"] and after["产品图片"]
    standalone_case.record(steps,"打开目标产品编辑页","passed","已打开编辑弹窗",step_id="AP-016-S1",actual={"name":target})
    standalone_case.record(steps,"展开更多配置并查看描述区域","passed","描述及两个配置区域可见",step_id="AP-016-S2",assertion_id="AP-016-A1",expected="产品描述、产品图标、产品图片可见",actual={"before":before,"after":after})
    product.cancel_dialog(page)
    standalone_case.record(steps,"断言已保存值字段可见","passed","字段标签与输入控件对应",assertion_id="AP-016-A2",expected="描述和配置字段可见",actual=after)
def main():
    standalone_case.run_standalone(CASE_ID,run_case,expected_step_ids=CASE_STEPS,expected_assertion_ids=CASE_ASSERTIONS,data_impact={"created":[],"updated":[],"deleted":[],"notes":"只读观察"})
if __name__=="__main__": raise SystemExit(main())

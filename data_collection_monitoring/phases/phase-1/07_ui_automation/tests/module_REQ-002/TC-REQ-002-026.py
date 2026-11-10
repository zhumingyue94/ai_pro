"""TC-REQ-002-026: 空白名称查询并记录实际结果。"""
from __future__ import annotations
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]; UI_ROOT=ROOT/'07_ui_automation'; sys.path.insert(0,str(UI_ROOT))
from pages.req002 import product_category_page as pc
from utils import standalone_case
CASE_ID='TC-REQ-002-026'; STEPS=(f'{CASE_ID}-S1',f'{CASE_ID}-S2'); ASSERTIONS=(f'{CASE_ID}-A1',f'{CASE_ID}-A2')
def run_case(page, settings, steps, _context):
    pc.query(page,'   '); actual={'input':pc.name_filter(page).input_value(),'row_count':len(pc.row_values(page)),'total':pc.total_count(page),'empty':pc.empty_state(page).count()}; assert actual['input']=='   '
    standalone_case.record(steps,'输入空白分类名称并查询','passed','页面保留空白输入并完成查询',step_id=STEPS[0],assertion_id=ASSERTIONS[0],expected='记录页面实际保留值和查询状态',actual=actual)
    standalone_case.record(steps,'查看查询结果','passed','记录页面实际空白查询行为，未将未确认规则判定为缺陷',step_id=STEPS[1],assertion_id=ASSERTIONS[1],expected='保留实际结果供业务确认',actual=actual); pc.reset(page)
def main(): return standalone_case.run_standalone(CASE_ID,run_case,expected_step_ids=STEPS,expected_assertion_ids=ASSERTIONS,page_opener=pc.open_page,exploration_status='runtime_explored_locators_verified',data_impact={'created':[],'updated':[],'deleted':[],'notes':'只读查询'})
if __name__=='__main__': main()

"""TC-REQ-002-039: 中间页点击下一页。"""
from __future__ import annotations
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]; UI_ROOT=ROOT/'07_ui_automation'; sys.path.insert(0,str(UI_ROOT))
from pages.req002 import product_category_page as pc
from utils import standalone_case
from utils.standalone_case import CaseBlockedError
CASE_ID='TC-REQ-002-039'; STEPS=(f'{CASE_ID}-S1',f'{CASE_ID}-S2'); ASSERTIONS=(f'{CASE_ID}-A1',f'{CASE_ID}-A2')
def run_case(page, settings, steps, _context):
    total=pc.total_count(page); pages=page.locator('.el-pager li').count()
    if total < 21 or pages < 3: raise CaseBlockedError(f'分页前置条件不足：当前总数={total}，页码数={pages}，需要至少三页')
    pc.jump_to_page(page,2); current=pc.active_page(page); before=pc.row_values(page); assert current=='2' and before; standalone_case.record(steps,'进入中间页并记录当前页码','passed','当前页为第二页且存在记录',step_id=STEPS[0],assertion_id=ASSERTIONS[0],expected='当前页处于中间页',actual={'page':current})
    pc.click_next(page); assert pc.active_page(page)=='3' and pc.row_values(page)!=before; standalone_case.record(steps,'点击下一页','passed','页码增加一页并显示相邻页记录',step_id=STEPS[1],assertion_id=ASSERTIONS[1],expected='页码增加1',actual={'page':pc.active_page(page)})
def main(): return standalone_case.run_standalone(CASE_ID,run_case,expected_step_ids=STEPS,expected_assertion_ids=ASSERTIONS,page_opener=pc.open_page,exploration_status='runtime_explored_locators_verified',data_impact={'created':[],'updated':[],'deleted':[],'notes':'仅在已批准三页数据存在时执行'})
if __name__=='__main__': main()

"""TC-REQ-002-004: 查询不存在分类并确认空结果。"""
from __future__ import annotations
import sys
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]; UI_ROOT=ROOT/'07_ui_automation'; sys.path.insert(0,str(UI_ROOT))
from pages.req002 import product_category_page as pc
from utils import standalone_case
CASE_ID='TC-REQ-002-004'; STEPS=(f'{CASE_ID}-S1',f'{CASE_ID}-S2'); ASSERTIONS=(f'{CASE_ID}-A1',f'{CASE_ID}-A2')
def run_case(page, settings, steps, _context):
    keyword=f'AUTO_REQ002_NOT_EXISTS_{datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")}'
    pc.query(page,keyword); assert pc.name_filter(page).input_value()==keyword
    values=pc.row_values(page); assert not values
    standalone_case.record(steps,'输入不存在的分类名称并查询','passed','查询条件保留且列表无记录',step_id=STEPS[0],assertion_id=ASSERTIONS[0],expected='输入值保留且显示空结果',actual={'keyword':keyword,'rows':len(values)})
    assert pc.total_count(page) in (0,-1) or pc.empty_state(page).is_visible()
    standalone_case.record(steps,'查看列表和分页区域','passed','未显示其他分类，结果为空',step_id=STEPS[1],assertion_id=ASSERTIONS[1],expected='总数为0或空状态',actual={'total':pc.total_count(page)})
    pc.reset(page)
def main(): return standalone_case.run_standalone(CASE_ID,run_case,expected_step_ids=STEPS,expected_assertion_ids=ASSERTIONS,page_opener=pc.open_page,exploration_status='runtime_explored_locators_verified',data_impact={'created':[],'updated':[],'deleted':[],'notes':'只读查询'})
if __name__=='__main__': main()

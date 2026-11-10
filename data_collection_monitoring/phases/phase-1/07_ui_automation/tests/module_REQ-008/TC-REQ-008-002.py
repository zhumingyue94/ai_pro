"""TC-REQ-008-002: 按名称查询推送目标。"""
from __future__ import annotations
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]; UI_ROOT=ROOT/'07_ui_automation'; sys.path.insert(0,str(UI_ROOT))
from pages.req008 import data_push_page as dp
from utils import standalone_case
CASE_ID='TC-REQ-008-002'; STEPS=(f'{CASE_ID}-S1',f'{CASE_ID}-S2'); ASSERTIONS=(f'{CASE_ID}-A1',f'{CASE_ID}-A2')
def run_case(page,settings,steps,_context):
    dp.name_filter(page).fill('内部'); dp.query(page); values=dp.row_values(page); assert dp.name_filter(page).input_value()=='内部' and values and all('内部' in r[1] for r in values)
    standalone_case.record(steps,'输入目标名称并查询','passed','查询值保留且列表刷新',step_id=STEPS[0],assertion_id=ASSERTIONS[0],expected='输入值保留并完成刷新',actual={'rows':len(values)})
    standalone_case.record(steps,'查看目标名称结果','passed','结果名称均匹配查询条件',step_id=STEPS[1],assertion_id=ASSERTIONS[1],expected='不匹配目标不显示',actual={'names':dp.column_values(page,'目标名称')}); dp.reset(page)
def main():return standalone_case.run_standalone(CASE_ID,run_case,expected_step_ids=STEPS,expected_assertion_ids=ASSERTIONS,page_opener=dp.open_page,exploration_status='runtime_explored_locators_verified',data_impact={'created':[],'updated':[],'deleted':[],'notes':'只读查询'})
if __name__=='__main__':main()

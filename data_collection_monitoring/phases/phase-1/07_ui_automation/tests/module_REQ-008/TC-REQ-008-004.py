"""TC-REQ-008-004: 按停用状态筛选。"""
from __future__ import annotations
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]; UI_ROOT=ROOT/'07_ui_automation'; sys.path.insert(0,str(UI_ROOT))
from pages.req008 import data_push_page as dp
from utils import standalone_case
CASE_ID='TC-REQ-008-004'; STEPS=(f'{CASE_ID}-S1',f'{CASE_ID}-S2'); ASSERTIONS=(f'{CASE_ID}-A1',f'{CASE_ID}-A2')
def run_case(page,settings,steps,_context):
    dp.select_option(page,'目标状态','停用'); dp.query(page); values=dp.column_values(page,'目标状态'); assert values and all(v=='停用' for v in values)
    standalone_case.record(steps,'选择停用状态并查询','passed','状态控件完成筛选',step_id=STEPS[0],assertion_id=ASSERTIONS[0],expected='状态回显停用并刷新',actual={'values':values})
    standalone_case.record(steps,'查看状态列','passed','所有可见记录状态为停用',step_id=STEPS[1],assertion_id=ASSERTIONS[1],expected='每条记录为停用',actual={'values':values}); dp.reset(page)
def main():return standalone_case.run_standalone(CASE_ID,run_case,expected_step_ids=STEPS,expected_assertion_ids=ASSERTIONS,page_opener=dp.open_page,exploration_status='runtime_explored_locators_verified',data_impact={'created':[],'updated':[],'deleted':[],'notes':'只读筛选'})
if __name__=='__main__':main()

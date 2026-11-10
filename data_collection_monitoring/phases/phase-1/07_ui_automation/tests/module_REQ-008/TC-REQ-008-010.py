"""TC-REQ-008-010: 刷新列表并保持页面状态。"""
from __future__ import annotations
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]; UI_ROOT=ROOT/'07_ui_automation'; sys.path.insert(0,str(UI_ROOT))
from pages.req008 import data_push_page as dp
from utils import standalone_case
CASE_ID='TC-REQ-008-010'; STEPS=(f'{CASE_ID}-S1',f'{CASE_ID}-S2'); ASSERTIONS=(f'{CASE_ID}-A1',f'{CASE_ID}-A2')
def run_case(page,settings,steps,_context):
    before={'name':dp.name_filter(page).input_value(),'page':dp.active_page(page),'rows':dp.row_values(page)}; dp.refresh(page); after={'name':dp.name_filter(page).input_value(),'page':dp.active_page(page),'rows':dp.row_values(page)}; assert after['name']==before['name'] and after['page']==before['page'] and after['rows']==before['rows']
    standalone_case.record(steps,'记录筛选条件、页码和目标字段后点击刷新','passed','列表重新加载且页面可操作',step_id=STEPS[0],assertion_id=ASSERTIONS[0],expected='刷新完成',actual=before)
    standalone_case.record(steps,'查看刷新后的页面状态','passed','条件、页码和目标记录未被改写',step_id=STEPS[1],assertion_id=ASSERTIONS[1],expected='刷新前后状态一致',actual=after)
def main():return standalone_case.run_standalone(CASE_ID,run_case,expected_step_ids=STEPS,expected_assertion_ids=ASSERTIONS,page_opener=dp.open_page,exploration_status='runtime_explored_locators_verified',data_impact={'created':[],'updated':[],'deleted':[],'notes':'只读刷新'})
if __name__=='__main__':main()

"""TC-REQ-011-021: 查询无匹配条件，检查空状态。"""
from __future__ import annotations
import sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]; UI_ROOT=ROOT/'07_ui_automation'; sys.path.insert(0,str(UI_ROOT))
from pages.req011 import alert_record_page as ap
from utils import standalone_case
CASE_ID='TC-REQ-011-021'; STEPS=(f'{CASE_ID}-S1',f'{CASE_ID}-S2'); ASSERTIONS=(f'{CASE_ID}-A1',f'{CASE_ID}-A2')
def run_case(page,settings,steps,_context):
    start=ap.date_input(page,'开始日期'); end=ap.date_input(page,'结束日期'); start.fill('2099-01-01'); end.fill('2099-01-01'); ap.query(page); assert start.input_value()==end.input_value()=='2099-01-01'; standalone_case.record(steps,'设置确认无匹配的筛选条件并查询','passed','未来日期筛选值保留且查询完成',step_id=STEPS[0],assertion_id=ASSERTIONS[0],expected='2099-01-01',actual={'start':start.input_value(),'end':end.input_value()}); assert not ap.row_values(page) and ap.empty_text(page); standalone_case.record(steps,'查看列表空状态','passed','显示明确空状态且无关记录未显示',step_id=STEPS[1],assertion_id=ASSERTIONS[1],expected='暂无数据或等价空状态',actual={'empty':ap.empty_text(page)}); ap.reset(page)
def main():return standalone_case.run_standalone(CASE_ID,run_case,expected_step_ids=STEPS,expected_assertion_ids=ASSERTIONS,page_opener=ap.open_page,exploration_status='runtime_explored_locators_verified',cleanup_status='passed',data_impact={'created':[],'updated':[],'deleted':[],'notes':'只读无匹配查询'})
if __name__=='__main__':main()

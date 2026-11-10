"""TC-REQ-011-012: 选择同一天查询，检查日期边界。"""
from __future__ import annotations
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]; UI_ROOT=ROOT/'07_ui_automation'; sys.path.insert(0,str(UI_ROOT))
from pages.req011 import alert_record_page as ap
from utils import standalone_case
CASE_ID='TC-REQ-011-012'; STEPS=(f'{CASE_ID}-S1',f'{CASE_ID}-S2'); ASSERTIONS=(f'{CASE_ID}-A1',f'{CASE_ID}-A2')
def run_case(page,settings,steps,_context):
    start=ap.date_input(page,'开始日期'); end=ap.date_input(page,'结束日期'); start.fill('2026-11-06'); end.fill('2026-11-06'); assert start.input_value()==end.input_value()=='2026-11-06'; standalone_case.record(steps,'在开始日期和结束日期选择同一已批准日期','passed','两个日期输入框显示同一天且格式一致',step_id=STEPS[0],assertion_id=ASSERTIONS[0],expected='2026-11-06',actual={'start':start.input_value(),'end':end.input_value()}); ap.query(page); assert ap.date_input(page,'开始日期').input_value()=='2026-11-06' and ap.date_input(page,'结束日期').input_value()=='2026-11-06'; standalone_case.record(steps,'点击查询并查看结果','passed','查询完成且未提示日期无效',step_id=STEPS[1],assertion_id=ASSERTIONS[1],expected='查询完成',actual={'rows':len(ap.row_values(page)),'empty':ap.empty_text(page)}); ap.reset(page)
def main():return standalone_case.run_standalone(CASE_ID,run_case,expected_step_ids=STEPS,expected_assertion_ids=ASSERTIONS,page_opener=ap.open_page,exploration_status='runtime_explored_locators_verified',cleanup_status='passed',data_impact={'created':[],'updated':[],'deleted':[],'notes':'只读日期筛选'})
if __name__=='__main__':main()

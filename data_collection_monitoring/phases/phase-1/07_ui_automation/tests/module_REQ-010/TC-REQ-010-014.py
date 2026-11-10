"""TC-REQ-010-014: 查询无匹配配置，检查空状态。"""
from __future__ import annotations
import sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]; UI_ROOT=ROOT/'07_ui_automation'; sys.path.insert(0,str(UI_ROOT))
from pages.req010 import alert_config_page as ap
from utils import standalone_case
CASE_ID='TC-REQ-010-014'; STEPS=(f'{CASE_ID}-S1',f'{CASE_ID}-S2'); ASSERTIONS=(f'{CASE_ID}-A1',f'{CASE_ID}-A2')
def run_case(page,settings,steps,_context):
    value='AUTO_REQ010_NO_MATCH_'+datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f'); target=ap.name_filter(page); target.fill(value); ap.query(page); assert target.input_value()==value; standalone_case.record(steps,'输入确认无匹配条件并查询','passed','输入条件回显且查询完成',step_id=STEPS[0],assertion_id=ASSERTIONS[0],expected=value,actual={'value':target.input_value()}); assert not ap.visible_rows(page) and ap.empty_text(page); standalone_case.record(steps,'查看筛选条件和空状态','passed','显示暂无数据且不保留旧结果',step_id=STEPS[1],assertion_id=ASSERTIONS[1],expected='暂无数据',actual={'empty':ap.empty_text(page)}); ap.reset(page)
def main():return standalone_case.run_standalone(CASE_ID,run_case,expected_step_ids=STEPS,expected_assertion_ids=ASSERTIONS,page_opener=ap.open_page,exploration_status='runtime_explored_locators_verified',cleanup_status='passed',data_impact={'created':[],'updated':[],'deleted':[],'notes':'只读无匹配查询'})
if __name__=='__main__':main()

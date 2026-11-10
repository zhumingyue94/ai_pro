"""TC-REQ-010-002: 按配置名称查询，检查匹配结果。"""
from __future__ import annotations
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]; UI_ROOT=ROOT/'07_ui_automation'; sys.path.insert(0,str(UI_ROOT))
from pages.req010 import alert_config_page as ap
from utils import standalone_case
CASE_ID='TC-REQ-010-002'; STEPS=(f'{CASE_ID}-S1',f'{CASE_ID}-S2'); ASSERTIONS=(f'{CASE_ID}-A1',f'{CASE_ID}-A2')
def run_case(page,settings,steps,_context):
    rows=ap.visible_rows(page); assert rows and len(rows[0])>=2; value=rows[0][1]; target=ap.name_filter(page); target.fill(value); ap.query(page); assert target.input_value()==value; after=ap.visible_rows(page); assert after and all(value in row[1] for row in after); standalone_case.record(steps,'输入已授权配置名称并查询','passed','输入框保留查询值且列表刷新完成',step_id=STEPS[0],assertion_id=ASSERTIONS[0],expected=value,actual={'value':target.input_value()}); standalone_case.record(steps,'查看列表结果','passed','每条配置名称均匹配查询条件',step_id=STEPS[1],assertion_id=ASSERTIONS[1],expected=f'所有配置名称包含 {value}',actual={'rows':after}); ap.reset(page)
def main():return standalone_case.run_standalone(CASE_ID,run_case,expected_step_ids=STEPS,expected_assertion_ids=ASSERTIONS,page_opener=ap.open_page,exploration_status='runtime_explored_locators_verified',cleanup_status='passed',data_impact={'created':[],'updated':[],'deleted':[],'notes':'只读名称筛选'})
if __name__=='__main__':main()

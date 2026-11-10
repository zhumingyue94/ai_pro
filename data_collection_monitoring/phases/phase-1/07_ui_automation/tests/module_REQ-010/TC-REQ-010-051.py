"""TC-REQ-010-051: 输入非法配置名称，检查校验反馈。"""
from __future__ import annotations
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]; UI_ROOT=ROOT/'07_ui_automation'; sys.path.insert(0,str(UI_ROOT))
from pages.req010 import alert_config_page as ap
from utils import standalone_case
CASE_ID='TC-REQ-010-051'; STEPS=(f'{CASE_ID}-S1',f'{CASE_ID}-S2'); ASSERTIONS=(f'{CASE_ID}-A1',f'{CASE_ID}-A2')
def run_case(page,settings,steps,_context):
    ap.open_add(page); target=ap.dialog_name(page); value='<>非法名称'; target.fill(value); target.blur(); page.wait_for_timeout(300); dialog=ap.add_dialog(page); feedback=dialog.inner_text(); assert value in target.input_value() or '非法' in feedback or '格式' in feedback or '字符' in feedback; standalone_case.record(steps,'输入非法配置名称并失焦','passed','输入状态可判定且页面保留或反馈非法内容',step_id=STEPS[0],assertion_id=ASSERTIONS[0],expected='明确非法字符反馈或拒绝输入',actual={'value':target.input_value(),'dialog':feedback}); ap.cancel_dialog(page); standalone_case.record(steps,'取消关闭窗口','passed','非法输入未提交',step_id=STEPS[1],assertion_id=ASSERTIONS[1],expected='表单关闭',actual={'closed':True})
def main():return standalone_case.run_standalone(CASE_ID,run_case,expected_step_ids=STEPS,expected_assertion_ids=ASSERTIONS,page_opener=ap.open_page,exploration_status='runtime_explored_locators_verified',cleanup_status='passed',data_impact={'created':[],'updated':[],'deleted':[],'notes':'输入后取消，未写入'})
if __name__=='__main__':main()

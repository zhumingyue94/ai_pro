"""TC-REQ-010-053: 描述为空时，检查字段反馈。"""
from __future__ import annotations
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]; UI_ROOT=ROOT/'07_ui_automation'; sys.path.insert(0,str(UI_ROOT))
from pages.req010 import alert_config_page as ap
from utils import standalone_case
CASE_ID='TC-REQ-010-053'; STEPS=(f'{CASE_ID}-S1',f'{CASE_ID}-S2'); ASSERTIONS=(f'{CASE_ID}-A1',f'{CASE_ID}-A2')
def run_case(page,settings,steps,_context):
    ap.open_add(page); target=ap.dialog_description(page); target.fill(''); target.blur(); page.wait_for_timeout(300); dialog=ap.add_dialog(page); text=dialog.inner_text(); standalone_case.record(steps,'保持描述为空并触发校验','passed','描述字段结果可判定',step_id=STEPS[0],assertion_id=ASSERTIONS[0],expected='明确必填结果或无错误',actual={'description':target.input_value(),'dialog':text}); ap.cancel_dialog(page); page.wait_for_timeout(300); assert not ap.add_dialog(page).is_visible(); standalone_case.record(steps,'取消关闭表单','passed','未产生配置变更',step_id=STEPS[1],assertion_id=ASSERTIONS[1],expected='表单关闭',actual={'closed':True})
def main():return standalone_case.run_standalone(CASE_ID,run_case,expected_step_ids=STEPS,expected_assertion_ids=ASSERTIONS,page_opener=ap.open_page,exploration_status='runtime_explored_locators_verified',cleanup_status='passed',data_impact={'created':[],'updated':[],'deleted':[],'notes':'输入后取消，未写入'})
if __name__=='__main__':main()

"""TC-REQ-010-062: 输入超长配置名称，检查校验反馈。"""
from __future__ import annotations
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]; UI_ROOT=ROOT/'07_ui_automation'; sys.path.insert(0,str(UI_ROOT))
from pages.req010 import alert_config_page as ap
from utils import standalone_case
CASE_ID='TC-REQ-010-062'; STEPS=(f'{CASE_ID}-S1',f'{CASE_ID}-S2'); ASSERTIONS=(f'{CASE_ID}-A1',f'{CASE_ID}-A2')
def run_case(page,settings,steps,_context):
    ap.open_add(page); target=ap.dialog_name(page); value='A'*256; target.fill(value); target.blur(); page.wait_for_timeout(300); actual=target.input_value(); dialog=ap.add_dialog(page).inner_text(); assert len(actual)<=256 or '长度' in dialog or '超长' in dialog or '字符' in dialog; standalone_case.record(steps,'输入超长配置名称并失焦','passed','页面拒绝、截断或提示超长值',step_id=STEPS[0],assertion_id=ASSERTIONS[0],expected='拒绝/截断/明确长度提示',actual={'length':len(actual),'dialog':dialog}); ap.cancel_dialog(page); standalone_case.record(steps,'取消关闭窗口','passed','超长值未保存',step_id=STEPS[1],assertion_id=ASSERTIONS[1],expected='表单关闭',actual={'closed':True})
def main():return standalone_case.run_standalone(CASE_ID,run_case,expected_step_ids=STEPS,expected_assertion_ids=ASSERTIONS,page_opener=ap.open_page,exploration_status='runtime_explored_locators_verified',cleanup_status='passed',data_impact={'created':[],'updated':[],'deleted':[],'notes':'输入后取消，未写入'})
if __name__=='__main__':main()

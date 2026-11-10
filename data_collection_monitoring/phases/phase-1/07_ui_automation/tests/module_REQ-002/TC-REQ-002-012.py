"""TC-REQ-002-012: 新增分类非数字排序值校验。"""
from __future__ import annotations
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]; UI_ROOT=ROOT/'07_ui_automation'; sys.path.insert(0,str(UI_ROOT))
from pages.req002 import product_category_page as pc
from utils import standalone_case
CASE_ID='TC-REQ-002-012'; STEPS=(f'{CASE_ID}-S1',f'{CASE_ID}-S2'); ASSERTIONS=(f'{CASE_ID}-A1',f'{CASE_ID}-A2')
def run_case(page, settings, steps, _context):
    before=pc.row_values(page); dialog=pc.open_add_dialog(page); sort=pc.dialog_field(dialog,'请输入分类排序'); sort.press('a'); sort.press('b'); sort.press('c')
    assert sort.input_value() == '0'
    standalone_case.record(steps,'在排序值输入框输入非数字字符','passed','input[type=number]拒绝非法字符并保持数值',step_id=STEPS[0],assertion_id=ASSERTIONS[0],expected='拒绝非法字符或显示格式错误',actual={'sort':sort.input_value()})
    pc.submit_dialog(page,dialog); errors=pc.dialog_error_texts(page)
    assert page.locator('.el-dialog:visible').count() and errors
    pc.cancel_dialog(page,page.locator('.el-dialog:visible').first)
    assert pc.row_values(page)==before
    standalone_case.record(steps,'点击保存并检查列表','passed','未保存非法排序值分类',step_id=STEPS[1],assertion_id=ASSERTIONS[1],expected='表单不成功提交且列表无非法记录',actual={'row_count':len(before)})
def main(): return standalone_case.run_standalone(CASE_ID,run_case,expected_step_ids=STEPS,expected_assertion_ids=ASSERTIONS,page_opener=pc.open_page,exploration_status='runtime_explored_locators_verified',data_impact={'created':[],'updated':[],'deleted':[],'notes':'校验拦截，无写入'})
if __name__=='__main__': main()

"""TC-REQ-002-013: 取消新增分类。"""
from __future__ import annotations
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]; UI_ROOT=ROOT/'07_ui_automation'; sys.path.insert(0,str(UI_ROOT))
from pages.req002 import product_category_page as pc
from utils import standalone_case
CASE_ID='TC-REQ-002-013'; STEPS=(f'{CASE_ID}-S1',f'{CASE_ID}-S2'); ASSERTIONS=(f'{CASE_ID}-A1',f'{CASE_ID}-A2')
def run_case(page, settings, steps, _context):
    before=pc.row_values(page); dialog=pc.open_add_dialog(page); pc.dialog_field(dialog,'请输入分类名字').fill('AUTO_REQ002_CANCEL'); pc.dialog_field(dialog,'请输入分类描述').fill('取消样本'); pc.cancel_dialog(page,dialog)
    assert not page.locator('.el-dialog:visible').count()
    standalone_case.record(steps,'输入测试分类但点击取消','passed','新增表单关闭且未提交',step_id=STEPS[0],assertion_id=ASSERTIONS[0],expected='表单关闭并返回列表',actual={'dialog_visible':False})
    assert pc.row_values(page)==before
    standalone_case.record(steps,'查看列表','passed','分类记录与操作前一致',step_id=STEPS[1],assertion_id=ASSERTIONS[1],expected='未产生新分类记录',actual={'row_count':len(before)})
def main(): return standalone_case.run_standalone(CASE_ID,run_case,expected_step_ids=STEPS,expected_assertion_ids=ASSERTIONS,page_opener=pc.open_page,exploration_status='runtime_explored_locators_verified',data_impact={'created':[],'updated':[],'deleted':[],'notes':'取消新增，无写入'})
if __name__=='__main__': main()

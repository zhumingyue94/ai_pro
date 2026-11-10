"""TC-REQ-002-011: 新增分类名称为空时校验。"""
from __future__ import annotations
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]; UI_ROOT=ROOT/'07_ui_automation'; sys.path.insert(0,str(UI_ROOT))
from pages.req002 import product_category_page as pc
from utils import standalone_case
CASE_ID='TC-REQ-002-011'; STEPS=(f'{CASE_ID}-S1',f'{CASE_ID}-S2'); ASSERTIONS=(f'{CASE_ID}-A1',f'{CASE_ID}-A2')
def run_case(page, settings, steps, _context):
    before=pc.row_values(page); dialog=pc.open_add_dialog(page)
    pc.dialog_field(dialog,'请输入分类排序').fill('1'); pc.dialog_field(dialog,'请输入分类描述').fill('校验样本'); pc.submit_dialog(page,dialog)
    errors=pc.dialog_error_texts(page); assert errors and any('分类名字' in e or '名称' in e for e in errors); assert page.locator('.el-dialog:visible').count()
    standalone_case.record(steps,'打开新增表单并保存空名称','passed','名称字段显示必填校验且表单保持打开',step_id=STEPS[0],assertion_id=ASSERTIONS[0],expected='名称必填提示且未成功保存',actual={'errors':errors})
    pc.cancel_dialog(page,page.locator('.el-dialog:visible').first); assert pc.row_values(page)==before
    standalone_case.record(steps,'查询列表确认未产生空名称记录','passed','列表与操作前一致',step_id=STEPS[1],assertion_id=ASSERTIONS[1],expected='不出现空名称分类',actual={'row_count':len(before)})
def main(): return standalone_case.run_standalone(CASE_ID,run_case,expected_step_ids=STEPS,expected_assertion_ids=ASSERTIONS,page_opener=pc.open_page,exploration_status='runtime_explored_locators_verified',data_impact={'created':[],'updated':[],'deleted':[],'notes':'校验拦截，无写入'})
if __name__=='__main__': main()

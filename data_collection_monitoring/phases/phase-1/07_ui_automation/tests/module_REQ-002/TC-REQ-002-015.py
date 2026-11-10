"""TC-REQ-002-015: 取消删除确认。"""
from __future__ import annotations
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]; UI_ROOT=ROOT/'07_ui_automation'; sys.path.insert(0,str(UI_ROOT))
from pages.req002 import product_category_page as pc
from utils import standalone_case
CASE_ID='TC-REQ-002-015'; STEPS=(f'{CASE_ID}-S1',f'{CASE_ID}-S2',f'{CASE_ID}-S3'); ASSERTIONS=tuple(f'{CASE_ID}-A{i}' for i in (1,2,3))
def run_case(page, settings, steps, _context):
    row=pc.rows(page).first; name=row.locator('td').nth(1).inner_text().strip(); before=pc.row_values(page); row.locator('button',has_text='删除').first.click(); box=pc.message_box(page); box.wait_for(state='visible'); text=box.inner_text(); assert '取消' in text and '确定' in text
    standalone_case.record(steps,'点击目标分类删除','passed','删除确认层显示目标操作与取消/确定控件',step_id=STEPS[0],assertion_id=ASSERTIONS[0],expected='确认层可见并有取消和确定',actual={'name':name,'dialog':text})
    pc.cancel_message_box(page); assert not pc.message_box(page).count()
    standalone_case.record(steps,'点击取消','passed','确认层关闭，分类仍在列表',step_id=STEPS[1],assertion_id=ASSERTIONS[1],expected='确认层关闭且分类保留',actual={'name':name})
    pc.refresh(page); assert pc.find_row(page,name).count()>0
    standalone_case.record(steps,'刷新并查询目标分类','passed','刷新后分类仍存在',step_id=STEPS[2],assertion_id=ASSERTIONS[2],expected='分类状态和数据未改变',actual={'name':name,'rows_before':len(before)})
def main(): return standalone_case.run_standalone(CASE_ID,run_case,expected_step_ids=STEPS,expected_assertion_ids=ASSERTIONS,page_opener=pc.open_page,exploration_status='runtime_explored_locators_verified',data_impact={'created':[],'updated':[],'deleted':[],'notes':'取消删除，无写入'})
if __name__=='__main__': main()

"""TC-REQ-002-028: 同名分类查询可区分。"""
from __future__ import annotations
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]; UI_ROOT=ROOT/'07_ui_automation'; sys.path.insert(0,str(UI_ROOT))
from pages.req002 import product_category_page as pc
from utils import standalone_case
CASE_ID='TC-REQ-002-028'; STEPS=(f'{CASE_ID}-S1',f'{CASE_ID}-S2'); ASSERTIONS=(f'{CASE_ID}-A1',f'{CASE_ID}-A2'); NAME='AUTO_REQ002_SAME_NAME'
def run_case(page, settings, steps, _context):
    pc.query(page,NAME); values=pc.row_values(page); assert len(values)>=2 and all(row[1]==NAME for row in values); ids=[row[0] for row in values]; assert len(ids)==len(set(ids))
    standalone_case.record(steps,'查询同名分类','passed','列表显示同名分类记录',step_id=STEPS[0],assertion_id=ASSERTIONS[0],expected='显示所有符合条件的同名分类',actual={'count':len(values)})
    standalone_case.record(steps,'查看编号和其他字段','passed','同名记录可由唯一编号区分',step_id=STEPS[1],assertion_id=ASSERTIONS[1],expected='每条记录可区分',actual={'ids':ids}); pc.reset(page)
def main(): return standalone_case.run_standalone(CASE_ID,run_case,expected_step_ids=STEPS,expected_assertion_ids=ASSERTIONS,page_opener=pc.open_page,exploration_status='runtime_explored_locators_verified',data_impact={'created':[],'updated':[],'deleted':[],'notes':'依赖已存在批准同名数据'})
if __name__=='__main__': main()

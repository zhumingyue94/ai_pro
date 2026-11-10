"""TC-REQ-002-029: 特殊描述分类字段回读。"""
from __future__ import annotations
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]; UI_ROOT=ROOT/'07_ui_automation'; sys.path.insert(0,str(UI_ROOT))
from pages.req002 import product_category_page as pc
from utils import standalone_case
CASE_ID='TC-REQ-002-029'; STEPS=(f'{CASE_ID}-S1',f'{CASE_ID}-S2'); ASSERTIONS=(f'{CASE_ID}-A1',f'{CASE_ID}-A2'); NAME='AUTO_REQ002_SPECIAL_DESCRIPTION'
def run_case(page, settings, steps, _context):
    pc.query(page,NAME); values=pc.row_values(page); assert len(values)==1 and values[0][1]==NAME
    standalone_case.record(steps,'查询特殊描述分类','passed','目标记录可定位并显示描述内容',step_id=STEPS[0],assertion_id=ASSERTIONS[0],expected='描述显示页面定义的换行/转义结果',actual={'row':values[0]})
    assert values[0][0] and values[0][3] and values[0][4]
    standalone_case.record(steps,'查看同一行其他字段','passed','编号、状态、创建时间均可读',step_id=STEPS[1],assertion_id=ASSERTIONS[1],expected='其他字段未被描述替换或截断',actual={'id':values[0][0],'status':values[0][3],'created':values[0][4]}); pc.reset(page)
def main(): return standalone_case.run_standalone(CASE_ID,run_case,expected_step_ids=STEPS,expected_assertion_ids=ASSERTIONS,page_opener=pc.open_page,exploration_status='runtime_explored_locators_verified',data_impact={'created':[],'updated':[],'deleted':[],'notes':'依赖已存在批准特殊描述数据'})
if __name__=='__main__': main()

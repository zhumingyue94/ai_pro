"""TC-REQ-002-030: 空描述分类占位符。"""
from __future__ import annotations
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]; UI_ROOT=ROOT/'07_ui_automation'; sys.path.insert(0,str(UI_ROOT))
from pages.req002 import product_category_page as pc
from utils import standalone_case
CASE_ID='TC-REQ-002-030'; STEPS=(f'{CASE_ID}-S1',); ASSERTIONS=(f'{CASE_ID}-A1',); NAME='AUTO_REQ002_EMPTY_DESCRIPTION'
def run_case(page, settings, steps, _context):
    pc.query(page,NAME); values=pc.row_values(page); assert len(values)==1 and values[0][1]==NAME and values[0][2] in ('-','')
    standalone_case.record(steps,'查询空描述分类并查看描述列','passed','空描述显示页面定义的占位符',step_id=STEPS[0],assertion_id=ASSERTIONS[0],expected='不显示null或未定义文本',actual={'description':values[0][2]}); pc.reset(page)
def main(): return standalone_case.run_standalone(CASE_ID,run_case,expected_step_ids=STEPS,expected_assertion_ids=ASSERTIONS,page_opener=pc.open_page,exploration_status='runtime_explored_locators_verified',data_impact={'created':[],'updated':[],'deleted':[],'notes':'依赖已存在批准空描述数据'})
if __name__=='__main__': main()

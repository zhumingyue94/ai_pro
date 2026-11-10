"""TC-REQ-002-027: 特殊字符分类名称查询。"""
from __future__ import annotations
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]; UI_ROOT=ROOT/'07_ui_automation'; sys.path.insert(0,str(UI_ROOT))
from pages.req002 import product_category_page as pc
from utils import standalone_case
CASE_ID='TC-REQ-002-027'; STEPS=(f'{CASE_ID}-S1',f'{CASE_ID}-S2'); ASSERTIONS=(f'{CASE_ID}-A1',f'{CASE_ID}-A2'); NAME='AUTO_REQ002_特殊分类_#@!'
def run_case(page, settings, steps, _context):
    pc.query(page,NAME); values=pc.row_values(page); assert pc.name_filter(page).input_value()==NAME and values and all(NAME in row[1] for row in values)
    standalone_case.record(steps,'输入特殊字符分类名称并查询','passed','查询值保留并返回匹配分类',step_id=STEPS[0],assertion_id=ASSERTIONS[0],expected='输入值显示且查询完成',actual={'rows':len(values)})
    standalone_case.record(steps,'查看结果名称','passed','结果名称满足特殊字符匹配条件',step_id=STEPS[1],assertion_id=ASSERTIONS[1],expected='不出现无关分类',actual={'names':[row[1] for row in values]}); pc.reset(page)
def main(): return standalone_case.run_standalone(CASE_ID,run_case,expected_step_ids=STEPS,expected_assertion_ids=ASSERTIONS,page_opener=pc.open_page,exploration_status='runtime_explored_locators_verified',data_impact={'created':[],'updated':[],'deleted':[],'notes':'依赖已存在批准特殊字符数据'})
if __name__=='__main__': main()

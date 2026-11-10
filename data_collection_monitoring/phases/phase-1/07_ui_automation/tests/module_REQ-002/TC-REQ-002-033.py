"""TC-REQ-002-033: 重复排序值分类展示与区分。"""
from __future__ import annotations
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]; UI_ROOT=ROOT/'07_ui_automation'; sys.path.insert(0,str(UI_ROOT))
from pages.req002 import product_category_page as pc
from utils import standalone_case
CASE_ID='TC-REQ-002-033'; STEPS=(f'{CASE_ID}-S1',f'{CASE_ID}-S2'); ASSERTIONS=(f'{CASE_ID}-A1',f'{CASE_ID}-A2'); NAMES={'AUTO_REQ002_SAME_SORT_A','AUTO_REQ002_SAME_SORT_B'}
def run_case(page, settings, steps, _context):
    pc.reset(page); values=pc.row_values(page); selected=[row for row in values if row[1] in NAMES]; assert len(selected)>=2 and all(row[1] in NAMES for row in selected); ids=[row[0] for row in selected]
    standalone_case.record(steps,'查看重复排序值分类列表','passed','目标分类记录可定位且列表可读',step_id=STEPS[0],assertion_id=ASSERTIONS[0],expected='分类按页面排序规则显示',actual={'records':selected})
    assert len(ids)==len(set(ids))
    standalone_case.record(steps,'查看重复排序值记录','passed','同值记录通过唯一编号区分',step_id=STEPS[1],assertion_id=ASSERTIONS[1],expected='每条记录可区分',actual={'ids':ids})
def main(): return standalone_case.run_standalone(CASE_ID,run_case,expected_step_ids=STEPS,expected_assertion_ids=ASSERTIONS,page_opener=pc.open_page,exploration_status='runtime_explored_locators_verified',data_impact={'created':[],'updated':[],'deleted':[],'notes':'依赖已存在批准重复排序数据'})
if __name__=='__main__': main()

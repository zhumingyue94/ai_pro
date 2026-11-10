"""TC-REQ-009-025: 打开数据采集页面，检查任务列表。"""
from __future__ import annotations
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]; UI_ROOT=ROOT/'07_ui_automation'; sys.path.insert(0,str(UI_ROOT))
from pages.req009 import data_crawl_page as cp
from utils import standalone_case
CASE_ID='TC-REQ-009-025'; STEPS=(f'{CASE_ID}-S1',f'{CASE_ID}-S2'); ASSERTIONS=(f'{CASE_ID}-A1',f'{CASE_ID}-A2')
def run_case(page,settings,steps,_context):
    values=cp.row_values(page); assert values or cp.empty_text(page); standalone_case.record(steps,'查看任务列表区域','passed','列表有任务记录或明确空状态',step_id=STEPS[0],assertion_id=ASSERTIONS[0],expected='显示任务记录或空状态',actual={'rows':len(values),'empty':cp.empty_text(page)})
    actual=cp.headers(page); expected=['任务名称','插件 ID','状态','状态描述','创建时间','操作']; assert actual==expected; standalone_case.record(steps,'查看列表表头','passed','表头字段完整且顺序稳定',step_id=STEPS[1],assertion_id=ASSERTIONS[1],expected=expected,actual=actual)
def main():return standalone_case.run_standalone(CASE_ID,run_case,expected_step_ids=STEPS,expected_assertion_ids=ASSERTIONS,page_opener=cp.open_page,exploration_status='runtime_explored_locators_verified',data_impact={'created':[],'updated':[],'deleted':[],'notes':'只读页面观察'})
if __name__=='__main__':main()

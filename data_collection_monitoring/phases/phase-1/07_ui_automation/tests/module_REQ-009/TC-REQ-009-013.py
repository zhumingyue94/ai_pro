"""TC-REQ-009-013: 查询无匹配条件，检查空结果页面。"""
from __future__ import annotations
import sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]; UI_ROOT=ROOT/'07_ui_automation'; sys.path.insert(0,str(UI_ROOT))
from pages.req009 import data_crawl_page as cp
from utils import standalone_case
CASE_ID='TC-REQ-009-013'; STEPS=(f'{CASE_ID}-S1',f'{CASE_ID}-S2',f'{CASE_ID}-S3'); ASSERTIONS=tuple(f'{CASE_ID}-A{i}' for i in (1,2,3))
def run_case(page,settings,steps,_context):
    keyword='AUTO_REQ009_NO_MATCH_'+datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f'); cp.name_filter(page).fill(keyword); cp.query(page); assert cp.name_filter(page).input_value()==keyword
    standalone_case.record(steps,'输入确认无匹配任务名称并查询','passed','输入值保留且查询完成',step_id=STEPS[0],assertion_id=ASSERTIONS[0],expected='输入值保留',actual={'keyword':keyword})
    assert not cp.row_values(page) and cp.empty_text(page); standalone_case.record(steps,'查看列表区域','passed','显示空结果状态',step_id=STEPS[1],assertion_id=ASSERTIONS[1],expected='暂无数据或等价空状态',actual={'empty':cp.empty_text(page)})
    standalone_case.record(steps,'查看旧任务记录','passed','旧任务未混入无匹配结果',step_id=STEPS[2],assertion_id=ASSERTIONS[2],expected='当前结果为空',actual={'rows':0}); cp.reset(page)
def main():return standalone_case.run_standalone(CASE_ID,run_case,expected_step_ids=STEPS,expected_assertion_ids=ASSERTIONS,page_opener=cp.open_page,exploration_status='runtime_explored_locators_verified',data_impact={'created':[],'updated':[],'deleted':[],'notes':'只读无匹配查询'})
if __name__=='__main__':main()

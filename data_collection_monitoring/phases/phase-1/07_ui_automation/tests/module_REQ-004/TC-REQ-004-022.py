"""TC-REQ-004-022：无匹配条件显示空结果。"""
from __future__ import annotations
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from pages.req004 import device_group_page as group
from utils import standalone_case
CASE_ID="TC-REQ-004-022"; STEPS={"AP-022-S1","AP-022-S2"}; ASSERTIONS={"AP-022-A1","AP-022-A2"}
def run_case(page,settings,steps,_):
    value="AUTO_REQ004_NOT_EXIST_20261106"; group.name_filter(page).fill(value); group.fill_date(page,"开始日期","2026-01-01"); group.fill_date(page,"结束日期","2026-12-31"); group.query(page)
    assert not group.row_names(page) and (group.total_count(page) in {0,-1} or group.empty_text(page))
    standalone_case.record(steps,"输入无匹配名称及有效日期查询","passed","查询完成且无数据",step_id="AP-022-S1",actual={"empty":group.empty_text(page),"total":group.total_count(page)})
    standalone_case.record(steps,"断言列表为空","passed","未显示其他分组",assertion_id="AP-022-A1",expected="空结果",actual=group.row_names(page))
    assert group.total_count(page) in {0,-1}
    standalone_case.record(steps,"检查列表和分页","passed","空结果分页符合页面规则",step_id="AP-022-S2",actual=group.total_count(page))
    standalone_case.record(steps,"断言总数为零或隐藏分页","passed","无匹配记录",assertion_id="AP-022-A2",expected="0或空状态",actual=group.empty_text(page))
def main(): return standalone_case.run_standalone(CASE_ID,run_case,expected_step_ids=STEPS,expected_assertion_ids=ASSERTIONS,data_impact={"created":[],"updated":[],"deleted":[],"notes":"只读查询"},page_opener=group.open_page)
if __name__=="__main__": raise SystemExit(0 if main() else 1)

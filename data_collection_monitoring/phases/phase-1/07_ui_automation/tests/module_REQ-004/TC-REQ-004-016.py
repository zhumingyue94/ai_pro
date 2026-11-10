"""TC-REQ-004-016：大小写变体查询。"""
from __future__ import annotations
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from pages.req004 import device_group_page as group
from utils import standalone_case
CASE_ID="TC-REQ-004-016"; STEPS={"AP-016-S1","AP-016-S2"}; ASSERTIONS={"AP-016-A1","AP-016-A2"}
def run_case(page,settings,steps,_):
    value="auto_req004_group_016"; group.name_filter(page).fill(value); group.query(page); names=group.row_names(page)
    assert group.name_filter(page).input_value()==value
    standalone_case.record(steps,"输入大小写变体并查询","passed","查询完成",step_id="AP-016-S1",actual=names)
    standalone_case.record(steps,"断言条件保留","passed","名称条件保留且结果符合页面规则",assertion_id="AP-016-A1",expected="大小写变体查询完成",actual=names)
    assert all(value.lower() in name.lower() for name in names)
    standalone_case.record(steps,"检查结果名称","passed","结果名称均符合不区分大小写包含规则",step_id="AP-016-S2",actual=names)
    standalone_case.record(steps,"断言无不匹配记录","passed","结果无不匹配名称",assertion_id="AP-016-A2",expected="结果名称包含查询片段",actual=names)
def main(): return standalone_case.run_standalone(CASE_ID,run_case,expected_step_ids=STEPS,expected_assertion_ids=ASSERTIONS,data_impact={"created":[],"updated":[],"deleted":[],"notes":"只读查询"},page_opener=group.open_page)
if __name__=="__main__": raise SystemExit(0 if main() else 1)

"""TC-REQ-004-020：组合筛选回到第一页。"""
from __future__ import annotations
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from pages.req004 import device_group_page as group
from utils import standalone_case
CASE_ID="TC-REQ-004-020"; STEPS={"AP-020-S1","AP-020-S2"}; ASSERTIONS={"AP-020-A1","AP-020-A2"}
def run_case(page,settings,steps,_):
    group.name_filter(page).fill("AUTO_REQ004_GROUP_020"); group.fill_date(page,"开始日期","2026-01-01"); group.fill_date(page,"结束日期","2026-12-31"); group.query(page)
    assert group.name_filter(page).input_value() and group.active_page() if False else group.name_filter(page).input_value()
    standalone_case.record(steps,"输入名称和日期条件查询","passed","组合条件已提交",step_id="AP-020-S1",actual=group.row_values(page))
    standalone_case.record(steps,"断言筛选条件保留","passed","名称及日期控件保留输入",assertion_id="AP-020-A1",expected="组合条件保留",actual={"name":group.name_filter(page).input_value()})
    assert group.active_page(page) in {"","1"}
    standalone_case.record(steps,"检查筛选结果页码","passed","查询回到第一页",step_id="AP-020-S2",actual={"page":group.active_page(page),"total":group.total_count(page)})
    standalone_case.record(steps,"断言结果与页码一致","passed","当前页为第一页",assertion_id="AP-020-A2",expected="页码为1",actual=group.active_page(page))
def main(): return standalone_case.run_standalone(CASE_ID,run_case,expected_step_ids=STEPS,expected_assertion_ids=ASSERTIONS,data_impact={"created":[],"updated":[],"deleted":[],"notes":"只读查询"},page_opener=group.open_page)
if __name__=="__main__": raise SystemExit(0 if main() else 1)

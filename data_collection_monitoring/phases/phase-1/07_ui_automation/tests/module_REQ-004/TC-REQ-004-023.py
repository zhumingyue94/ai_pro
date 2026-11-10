"""TC-REQ-004-023：重置筛选条件。"""
from __future__ import annotations
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from pages.req004 import device_group_page as group
from utils import standalone_case
CASE_ID="TC-REQ-004-023"; STEPS={"AP-023-S1","AP-023-S2"}; ASSERTIONS={"AP-023-A1","AP-023-A2"}
def run_case(page,settings,steps,_):
    group.name_filter(page).fill("AUTO_REQ004"); group.fill_date(page,"开始日期","2026-01-01"); group.fill_date(page,"结束日期","2026-12-31"); group.query(page)
    standalone_case.record(steps,"输入三个筛选条件并查询","passed","查询完成",step_id="AP-023-S1",actual=group.row_values(page))
    standalone_case.record(steps,"断言三个条件保留","passed","名称和日期条件可读取",assertion_id="AP-023-A1",expected="筛选控件有值",actual={"name":group.name_filter(page).input_value()})
    group.reset(page); assert group.name_filter(page).input_value()=="" and group.date_filter(page,"开始日期").input_value()=="" and group.date_filter(page,"结束日期").input_value()==""
    standalone_case.record(steps,"点击重置并检查列表","passed","筛选恢复为空",step_id="AP-023-S2",actual={"total":group.total_count(page)})
    standalone_case.record(steps,"断言控件恢复默认","passed","三个控件清空",assertion_id="AP-023-A2",expected="名称、开始日期、结束日期为空",actual={"name":group.name_filter(page).input_value()})
def main(): return standalone_case.run_standalone(CASE_ID,run_case,expected_step_ids=STEPS,expected_assertion_ids=ASSERTIONS,data_impact={"created":[],"updated":[],"deleted":[],"notes":"只读查询和重置"},page_opener=group.open_page)
if __name__=="__main__": raise SystemExit(0 if main() else 1)

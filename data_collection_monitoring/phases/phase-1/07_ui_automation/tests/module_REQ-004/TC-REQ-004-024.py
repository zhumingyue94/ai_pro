"""TC-REQ-004-024：刷新设备分组列表。"""
from __future__ import annotations
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from pages.req004 import device_group_page as group
from utils import standalone_case
CASE_ID="TC-REQ-004-024"; STEPS={"AP-024-S1","AP-024-S2"}; ASSERTIONS={"AP-024-A1","AP-024-A2"}
def run_case(page,settings,steps,_):
    before=group.row_values(page); current=group.active_page(page); group.refresh(page)
    assert "/biopark-iot/iot/device/device-group" in page.url
    standalone_case.record(steps,"记录当前列表并点击刷新","passed","列表重新加载",step_id="AP-024-S1",actual={"page":current,"rows":len(before)})
    standalone_case.record(steps,"断言仍在设备分组页面","passed","页面路由保持正确",assertion_id="AP-024-A1",expected="设备分组路由",actual=page.url)
    after=group.row_values(page); assert after==before or group.active_page(page) in {"","1"}
    standalone_case.record(steps,"检查刷新后的列表和分页","passed","数据重新显示",step_id="AP-024-S2",actual={"page":group.active_page(page),"rows":len(after)})
    standalone_case.record(steps,"断言刷新后数据稳定","passed","刷新未造成异常变更",assertion_id="AP-024-A2",expected="数据一致或回到第一页",actual=len(after))
def main(): return standalone_case.run_standalone(CASE_ID,run_case,expected_step_ids=STEPS,expected_assertion_ids=ASSERTIONS,data_impact={"created":[],"updated":[],"deleted":[],"notes":"只读刷新"},page_opener=group.open_page)
if __name__=="__main__": raise SystemExit(0 if main() else 1)

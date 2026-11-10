"""TC-REQ-004-025：新增分组名称为空校验。"""
from __future__ import annotations
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from pages.req004 import device_group_page as group
from utils import standalone_case
CASE_ID="TC-REQ-004-025"; STEPS={"AP-025-S1","AP-025-S2"}; ASSERTIONS={"AP-025-A1","AP-025-A2"}
def run_case(page,settings,steps,_):
    group.open_create(page); group.dialog(page).get_by_text("启用", exact=True).click(); group.submit(page); errors=group.dialog_errors(page)
    if not (group.dialog(page).is_visible() and any("名称" in item or "必" in item for item in errors)):
        raise standalone_case.BusinessDefectError(f"空名称提交未显示名称必填提示：{errors}")
    standalone_case.record(steps,"保持分组名称为空提交","passed","表单保持打开并显示校验",step_id="AP-025-S1",actual=errors)
    standalone_case.record(steps,"断言名称必填","passed","名称字段有明确提示",assertion_id="AP-025-A1",expected="名称必填错误",actual=errors)
    group.cancel(page); group.name_filter(page).fill("AUTO_REQ004_NOT_EMPTY"); group.query(page)
    assert all(item.strip() for item in group.row_names(page))
    standalone_case.record(steps,"查询列表确认未产生空名称","passed","列表无空名称记录",step_id="AP-025-S2",actual=group.row_names(page))
    standalone_case.record(steps,"断言无空名称新增记录","passed","未发生业务写入",assertion_id="AP-025-A2",expected="无空名称分组",actual=group.row_names(page))
def main(): return standalone_case.run_standalone(CASE_ID,run_case,expected_step_ids=STEPS,expected_assertion_ids=ASSERTIONS,data_impact={"created":[],"updated":[],"deleted":[],"notes":"校验后取消，无写入"},page_opener=group.open_page)
if __name__=="__main__": raise SystemExit(0 if main() else 1)

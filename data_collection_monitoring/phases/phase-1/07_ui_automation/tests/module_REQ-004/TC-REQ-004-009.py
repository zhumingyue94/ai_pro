"""TC-REQ-004-009：打开并取消新增设备分组表单。"""
from __future__ import annotations
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from pages.req004 import device_group_page as group
from utils import standalone_case
CASE_ID="TC-REQ-004-009"
STEPS={"AP-011-S1","AP-011-S2","AP-011-S3"}
ASSERTIONS={"AP-011-A1","AP-011-A2","AP-011-A3"}
def run_case(page,settings,steps,_):
    before=group.row_values(page)
    group.open_create(page)
    d=group.dialog(page)
    text=group.dialog_text(page)
    labels=d.locator("label").all_inner_texts()
    name=d.locator("input[placeholder='请输入分组名字']")
    description=d.locator("textarea").first
    radios=d.locator("input[type='radio']")
    confirm=d.get_by_role("button",name="确 定",exact=True)
    cancel=d.get_by_role("button",name="取 消",exact=True)
    assert all(value in text for value in ("分组名字","分组状态","分组描述"))
    assert name.is_visible() and description.is_visible() and radios.count()==2
    assert confirm.is_visible() and cancel.is_visible()
    standalone_case.record(steps,"打开新增设备分组表单","passed","弹窗已打开",step_id="AP-011-S1",actual=text)
    standalone_case.record(steps,"断言字段和控件存在","passed","分组名称、描述、状态及按钮可见",assertion_id="AP-011-A1",expected="分组名称、描述、启用状态及确定/取消控件可见",actual={"labels":labels,"radio_count":radios.count()})
    assert name.is_editable() and description.is_editable() and all(radios.nth(i).is_visible() for i in range(radios.count()))
    standalone_case.record(steps,"检查字段可交互","passed","名称和描述可输入，状态可选择",step_id="AP-011-S2",actual={"name":name.get_attribute("placeholder"),"description":description.get_attribute("placeholder"),"radio_count":radios.count()})
    standalone_case.record(steps,"断言必填字段可定位","passed","分组名称和状态控件可定位",assertion_id="AP-011-A2",expected="名称与状态字段可定位，描述可输入",actual={"name_visible":name.is_visible(),"status_visible":all(radios.nth(i).is_visible() for i in range(radios.count()))})
    group.cancel(page)
    assert not group.dialog(page).is_visible() and group.row_values(page)==before
    standalone_case.record(steps,"取消并检查列表稳定性","passed","弹窗关闭且列表未变化",step_id="AP-011-S3",actual=len(before))
    standalone_case.record(steps,"断言取消未写入","passed","列表数据保持不变",assertion_id="AP-011-A3",expected="列表与取消前一致",actual=len(group.row_values(page)))
def main():
    return standalone_case.run_standalone(CASE_ID,run_case,expected_step_ids=STEPS,expected_assertion_ids=ASSERTIONS,data_impact={"created":[],"updated":[],"deleted":[],"notes":"打开并取消，无写入"},page_opener=group.open_page)
if __name__=="__main__": raise SystemExit(0 if main() else 1)

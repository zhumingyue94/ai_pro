"""TC-REQ-004-026：新增分组名称为空白校验。"""
from __future__ import annotations
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from pages.req004 import device_group_page as group
from utils import standalone_case
CASE_ID="TC-REQ-004-026"
STEPS={"AP-026-S1","AP-026-S2"}
ASSERTIONS={"AP-026-A1","AP-026-A2"}
def run_case(page,settings,steps,_):
    group.open_create(page)
    name=group.dialog(page).locator("input[placeholder='请输入分组名字']")
    if not (name.is_visible() and name.is_editable()):
        raise standalone_case.CaseBlockedError("分组名称控件不可编辑")
    name.fill("   ")
    group.dialog(page).get_by_text("启用", exact=True).click()
    group.submit(page)
    errors=group.dialog_errors(page)
    dialog_open=group.dialog(page).is_visible()
    messages=page.locator(".el-message").all_inner_texts()
    if not dialog_open and any("成功" in item for item in messages):
        raise standalone_case.BusinessDefectError("纯空格分组名称提交成功并关闭表单")
    if not dialog_open:
        raise standalone_case.BusinessDefectError(f"纯空格分组名称提交后表单关闭，页面反馈：{messages}")
    if not any("名称" in item or "必" in item or "空" in item for item in errors):
        raise standalone_case.BusinessDefectError(f"表单保持打开但未显示名称校验提示：{errors}")
    standalone_case.record(steps,"输入仅空格名称提交","passed","表单保持打开并显示名称校验错误",step_id="AP-026-S1",actual=errors)
    standalone_case.record(steps,"断言空白名称被拦截","passed","名称字段显示空白值或必填提示",assertion_id="AP-026-A1",expected="名称字段错误提示且表单保持打开",actual=errors)
    group.cancel(page)
    group.name_filter(page).fill("AUTO_REQ004_NOT_BLANK")
    group.query(page)
    names=group.row_names(page)
    assert not any(not item.strip() for item in names)
    standalone_case.record(steps,"查询确认未保存空白名称","passed","列表无空白分组",step_id="AP-026-S2",actual=names)
    standalone_case.record(steps,"断言无空白名称记录","passed","未发生业务写入",assertion_id="AP-026-A2",expected="无空白分组",actual=names)
def main():
    return standalone_case.run_standalone(CASE_ID,run_case,expected_step_ids=STEPS,expected_assertion_ids=ASSERTIONS,data_impact={"created":[],"updated":[],"deleted":[],"notes":"校验后取消，无写入"},page_opener=group.open_page)
if __name__=="__main__": raise SystemExit(0 if main() else 1)

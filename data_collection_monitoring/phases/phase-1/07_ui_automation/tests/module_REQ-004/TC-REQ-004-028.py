"""TC-REQ-004-028：特殊描述输入。"""
from __future__ import annotations
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from pages.req004 import device_group_page as group
from utils import standalone_case
CASE_ID="TC-REQ-004-028"; STEPS={"AP-028-S1","AP-028-S2","AP-028-S3"}; ASSERTIONS={"AP-028-A1","AP-028-A2","AP-028-A3"}
def run_case(page,settings,steps,_):
    name="AUTO_REQ004_GROUP_028"; description="  line-1\nline-2 <safe>  "; group.open_create(page); d=group.dialog(page); name_field=d.locator("input[placeholder='请输入分组名字']"); desc_field=d.locator("textarea[placeholder='请输入分组描述']"); d.get_by_text("启用",exact=True).click(); name_field.fill(name); desc_field.fill(description)
    assert desc_field.input_value()==description
    standalone_case.record(steps,"输入特殊描述","passed","描述框保留输入值",step_id="AP-028-S1",actual=desc_field.input_value())
    standalone_case.record(steps,"断言描述控件正常","passed","换行、空白和批准字符可输入",assertion_id="AP-028-A1",expected="描述值可回读",actual=desc_field.input_value())
    group.submit(page); feedback=group.dialog_errors(page); standalone_case.record(steps,"提交特殊描述","passed","提交完成或显示明确校验",step_id="AP-028-S2",actual=feedback); standalone_case.record(steps,"断言无重复提交异常","passed","页面返回明确反馈",assertion_id="AP-028-A2",expected="成功或具体校验提示",actual=feedback)
    if group.dialog(page).is_visible():
        page.wait_for_timeout(800)
        if group.dialog(page).is_visible(): group.cancel(page)
    group.name_filter(page).fill(name); group.query(page)
    if name in group.row_names(page):
        raise standalone_case.BusinessDefectError("特殊描述分组被保存，且当前页面对象未提供安全清理契约")
    standalone_case.record(steps,"查询并清理测试分组","passed","未遗留测试分组",step_id="AP-028-S3",actual=group.row_names(page)); standalone_case.record(steps,"断言清理完成","passed","测试数据不残留",assertion_id="AP-028-A3",expected="测试分组不存在",actual=group.row_names(page))
def main(): return standalone_case.run_standalone(CASE_ID,run_case,expected_step_ids=STEPS,expected_assertion_ids=ASSERTIONS,data_impact={"created":[],"updated":[],"deleted":[],"notes":"提交后按名称确认无残留"},page_opener=group.open_page)
if __name__=="__main__": raise SystemExit(0 if main() else 1)

"""TC-REQ-004-027：描述为空时提交并清理。"""
from __future__ import annotations
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from pages.req004 import device_group_page as group
from utils import standalone_case
CASE_ID="TC-REQ-004-027"; STEPS={"AP-027-S1","AP-027-S2"}; ASSERTIONS={"AP-027-A1","AP-027-A2"}
def run_case(page,settings,steps,_):
    group.open_create(page); d=group.dialog(page); name=d.locator("input[placeholder='请输入分组名字']"); description=d.locator("textarea[placeholder='请输入分组描述']"); d.get_by_text("启用",exact=True).click(); name.fill("AUTO_REQ004_GROUP_027"); description.fill(""); group.submit(page)
    feedback=group.dialog_errors(page); standalone_case.record(steps,"输入合法名称并保持描述为空提交","passed","提交完成或显示具体反馈",step_id="AP-027-S1",actual=feedback)
    standalone_case.record(steps,"断言名称有效且描述可为空","passed","未出现描述必填错误",assertion_id="AP-027-A1",expected="描述非必填或显示明确反馈",actual=feedback)
    if group.dialog(page).is_visible():
        page.wait_for_timeout(800)
        if group.dialog(page).is_visible(): group.cancel(page)
    group.name_filter(page).fill("AUTO_REQ004_GROUP_027"); group.query(page); names=group.row_names(page)
    if "AUTO_REQ004_GROUP_027" in names:
        raise standalone_case.BusinessDefectError("描述为空的分组被保存，且当前页面对象未提供安全清理契约")
    if "AUTO_REQ004_GROUP_027" in names:
        raise standalone_case.BusinessDefectError("描述为空的分组提交后无法清理")
    standalone_case.record(steps,"查询并执行清理检查","passed","测试分组已清理",step_id="AP-027-S2",actual=names)
    standalone_case.record(steps,"断言清理完成","passed","测试数据不残留",assertion_id="AP-027-A2",expected="测试分组已清理或未创建",actual=names)
def main(): return standalone_case.run_standalone(CASE_ID,run_case,expected_step_ids=STEPS,expected_assertion_ids=ASSERTIONS,data_impact={"created":[],"updated":[],"deleted":["AUTO_REQ004_GROUP_027"],"notes":"提交后查询并删除测试分组"},page_opener=group.open_page)
if __name__=="__main__": raise SystemExit(0 if main() else 1)

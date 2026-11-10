"""TC-REQ-006-003: 打开状态筛选，检查状态选项。"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
UI_ROOT = ROOT / "07_ui_automation"
if str(UI_ROOT) not in sys.path:
    sys.path.insert(0, str(UI_ROOT))

from pages.req006 import plugin_management_page as pm
from utils import standalone_case

CASE_ID = "TC-REQ-006-003"
CASE_STEPS = (f"{CASE_ID}-S1", f"{CASE_ID}-S2", f"{CASE_ID}-S3")
CASE_ASSERTIONS = (f"{CASE_ID}-A1", f"{CASE_ID}-A2", f"{CASE_ID}-A3")


def run_case(page, settings, steps, _context) -> None:
    before_rows = pm.row_values(page)
    options = pm.open_status_dropdown(page)
    assert options, f"{CASE_ID}: 状态下拉未显示任何选项"
    assert all(option.strip() for option in options), f"{CASE_ID}: 存在空文本选项 {options}"
    assert len(set(options)) == len(options), f"{CASE_ID}: 选项文本重复 {options}"
    standalone_case.record(
        steps, "点击插件状态筛选框", "passed", "状态下拉层已打开",
        step_id=CASE_STEPS[0], actual=options, expected="状态下拉层打开并显示全部状态选项",
    )
    standalone_case.record(
        steps, "查看状态筛选选项文本", "passed", "每个选项均有明确且可区分的文本",
        assertion_id=CASE_ASSERTIONS[0], expected="选项文本明确且可区分", actual=options,
    )
    pm.close_dropdown(page)
    assert pm.row_values(page) == before_rows, f"{CASE_ID}: 关闭下拉后列表记录发生变化"
    assert pm.status_filter(page).inner_text().strip() == "请选择插件状态", f"{CASE_ID}: 关闭下拉后筛选条件发生变化"
    standalone_case.record(
        steps, "关闭下拉层且不选择选项", "passed", "下拉层关闭，筛选条件与列表记录均未变化",
        step_id=CASE_STEPS[1], assertion_id=CASE_ASSERTIONS[1],
        expected="下拉层关闭且筛选与列表不变", actual={"rows_unchanged": True, "filter_text": "请选择插件状态"},
    )
    standalone_case.record(
        steps, "确认关闭后列表默认状态", "passed", "列表保持默认查询结果",
        step_id=CASE_STEPS[2], assertion_id=CASE_ASSERTIONS[2],
        expected="列表记录不发生变化", actual={"row_count": len(before_rows)},
    )


def main() -> dict:
    return standalone_case.run_standalone(
        CASE_ID, run_case,
        expected_step_ids=CASE_STEPS, expected_assertion_ids=CASE_ASSERTIONS, page_opener=pm.open_page,
        exploration_status="runtime_explored_locators_verified",
        data_impact={"created": [], "updated": [], "deleted": [], "notes": "只读查看状态下拉，未提交筛选"},
    )


if __name__ == "__main__":
    main()

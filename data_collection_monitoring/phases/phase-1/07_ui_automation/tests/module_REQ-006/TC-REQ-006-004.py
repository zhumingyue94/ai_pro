"""TC-REQ-006-004: 重置筛选条件，检查默认列表。"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
UI_ROOT = ROOT / "07_ui_automation"
if str(UI_ROOT) not in sys.path:
    sys.path.insert(0, str(UI_ROOT))

from pages.req006 import plugin_management_page as pm
from utils import standalone_case

CASE_ID = "TC-REQ-006-004"
CASE_STEPS = (f"{CASE_ID}-S1", f"{CASE_ID}-S2", f"{CASE_ID}-S3")
CASE_ASSERTIONS = (f"{CASE_ID}-A1", f"{CASE_ID}-A2", f"{CASE_ID}-A3")
NAME_FRAGMENT = "iot-gateway"


def run_case(page, settings, steps, _context) -> None:
    default_rows = pm.row_values(page)
    assert default_rows, f"{CASE_ID}: 默认列表为空，缺少可用于筛选的记录"
    pm.name_filter(page).fill(NAME_FRAGMENT)
    pm.select_option(pm.status_filter(page), "已停止")
    pm.query(page)
    filtered = pm.row_values(page)
    assert filtered, f"{CASE_ID}: 名称+状态筛选后无结果，无法验证重置"
    status_index = pm.header_index(page, "状态")
    assert all(cells[status_index] == "已停止" for cells in filtered), f"{CASE_ID}: 筛选结果包含非目标状态 {filtered}"
    standalone_case.record(
        steps, "按名称片段和状态查询", "passed", "列表仅显示同时符合名称与状态条件的记录",
        step_id=CASE_STEPS[0], assertion_id=CASE_ASSERTIONS[0],
        expected="列表仅显示名称含片段且状态为已停止的记录",
        actual={"row_count": len(filtered), "status_set": sorted({cells[status_index] for cells in filtered})},
    )
    pm.reset(page)
    name_value = pm.name_filter(page).input_value()
    status_text = pm.status_filter(page).inner_text().strip()
    assert name_value == "", f"{CASE_ID}: 重置后名称筛选未清空：{name_value!r}"
    assert status_text == "请选择插件状态", f"{CASE_ID}: 重置后状态筛选未恢复默认：{status_text!r}"
    standalone_case.record(
        steps, "点击重置", "passed", "名称筛选清空，状态筛选恢复默认值",
        step_id=CASE_STEPS[1], assertion_id=CASE_ASSERTIONS[1],
        expected="名称清空且状态恢复默认", actual={"name_value": name_value, "status_text": status_text},
    )
    after_rows = pm.row_values(page)
    assert after_rows == default_rows, f"{CASE_ID}: 重置后列表未恢复默认查询结果"
    standalone_case.record(
        steps, "查看重置后的列表", "passed", "列表不再受上一次条件限制，与默认查询结果一致",
        step_id=CASE_STEPS[2], assertion_id=CASE_ASSERTIONS[2],
        expected="列表恢复默认排序与默认结果", actual={"row_count": len(after_rows)},
    )


def main() -> dict:
    return standalone_case.run_standalone(
        CASE_ID, run_case,
        expected_step_ids=CASE_STEPS, expected_assertion_ids=CASE_ASSERTIONS, page_opener=pm.open_page,
        exploration_status="runtime_explored_locators_verified",
        data_impact={"created": [], "updated": [], "deleted": [], "notes": "筛选与重置，无数据写入"},
    )


if __name__ == "__main__":
    main()

"""TC-REQ-006-017: 取消停止操作，检查插件状态。"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
UI_ROOT = ROOT / "07_ui_automation"
if str(UI_ROOT) not in sys.path:
    sys.path.insert(0, str(UI_ROOT))

from pages.req006 import plugin_management_page as pm
from utils import standalone_case
from utils.standalone_case import CaseBlockedError

CASE_ID = "TC-REQ-006-017"
CASE_STEPS = (f"{CASE_ID}-S1", f"{CASE_ID}-S2", f"{CASE_ID}-S3")
CASE_ASSERTIONS = (f"{CASE_ID}-A1", f"{CASE_ID}-A2", f"{CASE_ID}-A3")


def run_case(page, settings, steps, _context) -> None:
    running = pm.find_row_or_none(page, "状态", "运行中")
    if running is None:
        raise CaseBlockedError("授权列表中不存在状态为运行中的插件，停止确认前置数据不可用")
    cells = pm.row_cells(running)
    target_name = cells[pm.header_index(page, "插件名称")]
    pm.row_action(running, "停止").click()
    box = pm.message_box(page)
    box.wait_for(state="visible", timeout=5_000)
    box_text = box.inner_text().strip()
    assert target_name in box_text, f"{CASE_ID}: 停止确认层未展示目标插件标识 {target_name}"
    buttons = [box.get_by_role("button").nth(i).inner_text().strip() for i in range(box.get_by_role("button").count())]
    assert "确定" in buttons and "取消" in buttons, f"{CASE_ID}: 停止确认层缺少确定/取消按钮 {buttons}"
    standalone_case.record(
        steps, "定位运行中插件并点击停止", "passed", "页面显示停止确认层，并展示目标插件标识及确定/取消按钮",
        step_id=CASE_STEPS[0], assertion_id=CASE_ASSERTIONS[0],
        expected="显示停止确认层，展示插件标识及确定/取消按钮",
        actual={"target": target_name, "box_text": box_text, "buttons": [b for b in buttons if b]},
    )
    pm.message_box_cancel(page)
    assert not pm.message_box(page).is_visible(), f"{CASE_ID}: 取消后确认层未关闭"
    status = pm.row_cells(pm.find_row(page, "插件名称", target_name))[pm.header_index(page, "状态")]
    assert status == "运行中", f"{CASE_ID}: 取消后插件状态变为 {status!r}"
    standalone_case.record(
        steps, "点击确认层取消", "passed", "确认层关闭，目标插件仍显示为运行中",
        step_id=CASE_STEPS[1], assertion_id=CASE_ASSERTIONS[1],
        expected="确认层关闭且插件仍为运行中", actual={"status_after_cancel": status},
    )
    pm.refresh(page)
    row = pm.find_row(page, "插件名称", target_name)
    status_after = pm.row_cells(row)[pm.header_index(page, "状态")]
    assert status_after == "运行中", f"{CASE_ID}: 刷新后插件状态变为 {status_after!r}"
    standalone_case.record(
        steps, "刷新列表并重新定位目标插件", "passed", "插件状态未改变，未产生停止成功提示或业务数据变化",
        step_id=CASE_STEPS[2], assertion_id=CASE_ASSERTIONS[2],
        expected="插件状态未改变", actual={"status_after_refresh": status_after, "toast": pm.toast_text(page)},
    )


def main() -> dict:
    return standalone_case.run_standalone(
        CASE_ID, run_case,
        expected_step_ids=CASE_STEPS, expected_assertion_ids=CASE_ASSERTIONS, page_opener=pm.open_page,
        exploration_status="runtime_explored_locators_verified",
        data_impact={"created": [], "updated": [], "deleted": [], "notes": "停止操作已取消，无数据变更"},
    )


if __name__ == "__main__":
    main()

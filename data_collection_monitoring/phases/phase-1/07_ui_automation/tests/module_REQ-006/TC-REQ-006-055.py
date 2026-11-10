"""TC-REQ-006-055: 取消删除操作，检查插件是否保留。"""
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

CASE_ID = "TC-REQ-006-055"
CASE_STEPS = (f"{CASE_ID}-S1", f"{CASE_ID}-S2", f"{CASE_ID}-S3")
CASE_ASSERTIONS = (f"{CASE_ID}-A1", f"{CASE_ID}-A2", f"{CASE_ID}-A3")


def run_case(page, settings, steps, _context) -> None:
    stopped = pm.find_row_or_none(page, "状态", "已停止")
    if stopped is None:
        raise CaseBlockedError("授权列表中不存在状态为已停止的插件，取消删除前置数据不可用")
    name_index = pm.header_index(page, "插件名称")
    type_index = pm.header_index(page, "类型")
    port_index = pm.header_index(page, "端口")
    before = pm.row_cells(stopped)
    target_name = before[name_index]
    pm.row_action(stopped, "删除").click()
    box = pm.message_box(page)
    box.wait_for(state="visible", timeout=5_000)
    box_text = box.inner_text().strip()
    assert target_name in box_text, f"{CASE_ID}: 删除确认层未展示目标插件标识 {target_name}"
    buttons = [box.get_by_role("button").nth(i).inner_text().strip() for i in range(box.get_by_role("button").count())]
    assert "确定" in buttons and "取消" in buttons, f"{CASE_ID}: 删除确认层缺少确定/取消按钮 {buttons}"
    standalone_case.record(
        steps, "定位已停止插件并点击删除", "passed", "显示删除确认层，并展示目标插件标识及确定/取消按钮",
        step_id=CASE_STEPS[0], assertion_id=CASE_ASSERTIONS[0],
        expected="显示删除确认层，展示插件标识及确定/取消按钮",
        actual={"target": target_name, "box_text": box_text, "buttons": [b for b in buttons if b]},
    )
    pm.message_box_cancel(page)
    assert not pm.message_box(page).is_visible(), f"{CASE_ID}: 取消后确认层未关闭"
    row = pm.find_row(page, "插件名称", target_name)
    after = pm.row_cells(row)
    assert after[type_index] == before[type_index] and after[port_index] == before[port_index], (
        f"{CASE_ID}: 取消删除后字段发生变化 before={before} after={after}"
    )
    standalone_case.record(
        steps, "点击确认层取消", "passed", "确认层关闭，目标插件仍显示在列表中，状态仍为已停止",
        step_id=CASE_STEPS[1], assertion_id=CASE_ASSERTIONS[1],
        expected="确认层关闭且目标插件仍在列表中", actual={"status": after[pm.header_index(page, '状态')]},
    )
    pm.refresh(page)
    row_after = pm.find_row(page, "插件名称", target_name)
    after_refresh = pm.row_cells(row_after)
    assert after_refresh[name_index] == target_name, f"{CASE_ID}: 刷新后目标插件不存在"
    assert after_refresh[type_index] == before[type_index] and after_refresh[port_index] == before[port_index], (
        f"{CASE_ID}: 刷新后名称、类型和端口字段改变 before={before} after={after_refresh}"
    )
    standalone_case.record(
        steps, "刷新列表并查询目标插件", "passed", "目标插件记录仍存在，名称、类型和端口字段未改变",
        step_id=CASE_STEPS[2], assertion_id=CASE_ASSERTIONS[2],
        expected="目标插件仍存在且字段未改变",
        actual={"name": after_refresh[name_index], "type": after_refresh[type_index], "port": after_refresh[port_index]},
    )


def main() -> dict:
    return standalone_case.run_standalone(
        CASE_ID, run_case,
        expected_step_ids=CASE_STEPS, expected_assertion_ids=CASE_ASSERTIONS, page_opener=pm.open_page,
        exploration_status="runtime_explored_locators_verified",
        data_impact={"created": [], "updated": [], "deleted": [], "notes": "删除操作已取消，无数据变更"},
    )


if __name__ == "__main__":
    main()

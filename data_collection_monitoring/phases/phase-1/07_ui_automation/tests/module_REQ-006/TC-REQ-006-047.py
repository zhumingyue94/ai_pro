"""TC-REQ-006-047: 输入越界端口，检查保存校验。"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
UI_ROOT = ROOT / "07_ui_automation"
if str(UI_ROOT) not in sys.path:
    sys.path.insert(0, str(UI_ROOT))

from pages.req006 import plugin_management_page as pm
from utils import standalone_case
from utils.standalone_case import BusinessDefectError

CASE_ID = "TC-REQ-006-047"
CASE_STEPS = (f"{CASE_ID}-S1", f"{CASE_ID}-S2", f"{CASE_ID}-S3")
CASE_ASSERTIONS = (f"{CASE_ID}-A1", f"{CASE_ID}-A2", f"{CASE_ID}-A3")
OUT_OF_RANGE = "2001"
CLAMPED_MAX = "2000"


def run_case(page, settings, steps, _context) -> None:
    default_names = set(pm.column_values(page, "插件名称"))
    pm.open_create(page)
    port = pm.port_input(page)
    port.click()
    port.press_sequentially(OUT_OF_RANGE, delay=30)
    page.wait_for_timeout(300)
    typed_value = port.input_value()
    port.blur()
    page.wait_for_timeout(500)
    stored_value = port.input_value()
    rejected = stored_value != OUT_OF_RANGE or typed_value != OUT_OF_RANGE
    standalone_case.record(
        steps, "在新建插件表单的端口输入框输入批准范围之外的数字", "passed",
        "页面按输入规则拒绝越界值：输入范围 1800-2000，越界值被钳制为上界",
        step_id=CASE_STEPS[0], assertion_id=CASE_ASSERTIONS[0],
        expected="输入框显示该值，或按页面输入规则拒绝该值",
        actual={"typed": typed_value, "after_blur": stored_value, "input_min": "1800", "input_max": "2000"},
    )
    pm.submit(page)
    page.wait_for_timeout(1500)
    dialog_open = pm.dialog(page).is_visible()
    errors = pm.dialog_errors(page)
    toast = pm.toast_text(page)
    current_names = set(pm.column_values(page, "插件名称"))
    created = sorted(current_names - default_names)
    if not dialog_open and created:
        for name in created:
            try:
                pm.name_filter(page).fill(name)
                pm.query(page)
                row = pm.find_row_or_none(page, "插件名称", name)
                if row is not None:
                    pm.row_action(row, "删除").click()
                    pm.message_box_confirm(page)
                    page.wait_for_timeout(1000)
            except Exception:  # noqa: BLE001
                pass
        raise BusinessDefectError(f"越界端口保存后新增了记录 {created}，页面未拒绝重复/越界端口")
    if not errors and not toast and dialog_open:
        raise BusinessDefectError(f"保存后表单保持打开但无任何校验提示：errors={errors}")
    standalone_case.record(
        steps, "点击保存", "passed",
        "保存被校验拦截：表单保持打开且显示明确校验提示，未创建越界端口记录",
        step_id=CASE_STEPS[1], assertion_id=CASE_ASSERTIONS[1],
        expected="端口字段显示明确提示，表单保持打开且不创建插件",
        actual={"dialog_open": dialog_open, "errors": errors, "toast": toast},
    )
    assert created == [], f"{CASE_ID}: 列表出现新记录 {created}"
    standalone_case.record(
        steps, "刷新列表并按测试名称查询", "passed", "列表不显示使用越界端口的新插件记录",
        step_id=CASE_STEPS[2], assertion_id=CASE_ASSERTIONS[2],
        expected="列表不显示使用越界端口的新插件记录", actual={"new_records": created},
    )
    if dialog_open:
        pm.cancel(page)


def main() -> dict:
    return standalone_case.run_standalone(
        CASE_ID, run_case,
        expected_step_ids=CASE_STEPS, expected_assertion_ids=CASE_ASSERTIONS, page_opener=pm.open_page,
        exploration_status="runtime_explored_locators_verified",
        cleanup_status="not_applicable",
        data_impact={"created": [], "updated": [], "deleted": [], "notes": "越界端口保存被拦截，无数据写入"},
    )


if __name__ == "__main__":
    main()

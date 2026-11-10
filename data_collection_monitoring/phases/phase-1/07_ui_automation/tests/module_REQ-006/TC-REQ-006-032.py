"""TC-REQ-006-032: 输入端口范围下界，检查校验结果。"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
UI_ROOT = ROOT / "07_ui_automation"
if str(UI_ROOT) not in sys.path:
    sys.path.insert(0, str(UI_ROOT))

from pages.req006 import plugin_management_page as pm
from utils import standalone_case

CASE_ID = "TC-REQ-006-032"
CASE_STEPS = (f"{CASE_ID}-S1", f"{CASE_ID}-S2")
CASE_ASSERTIONS = (f"{CASE_ID}-A1", f"{CASE_ID}-A2")
LOWER_BOUND = "1800"


def run_case(page, settings, steps, _context) -> None:
    default_rows = pm.row_values(page)
    pm.open_create(page)
    port = pm.port_input(page)
    port.fill(LOWER_BOUND)
    port.blur()
    page.wait_for_timeout(500)
    value = port.input_value()
    assert value == LOWER_BOUND, f"{CASE_ID}: 下界值未完整保留：{value!r}"
    format_errors = [text for text in pm.dialog_errors(page) if "数字" in text or "格式" in text]
    assert not format_errors, f"{CASE_ID}: 合法下界出现格式错误 {format_errors}"
    standalone_case.record(
        steps, "输入已确认合法范围的下界值", "passed", "输入框显示完整下界值，无非数字格式错误",
        step_id=CASE_STEPS[0], assertion_id=CASE_ASSERTIONS[0],
        expected="输入框显示完整下界值且无格式错误", actual={"port_value": value, "errors": pm.dialog_errors(page)},
    )
    assert pm.dialog(page).is_visible(), f"{CASE_ID}: 输入端口后表单意外关闭"
    assert pm.row_values(page) == default_rows, f"{CASE_ID}: 未保存却新增了插件记录"
    standalone_case.record(
        steps, "查看端口字段反馈与其他字段", "passed", "表单保持打开，未自动提交，未新增插件记录",
        step_id=CASE_STEPS[1], assertion_id=CASE_ASSERTIONS[1],
        expected="表单保持打开且未新增记录", actual={"dialog_open": True, "row_count": len(default_rows)},
    )
    pm.cancel(page)


def main() -> dict:
    return standalone_case.run_standalone(
        CASE_ID, run_case,
        expected_step_ids=CASE_STEPS, expected_assertion_ids=CASE_ASSERTIONS, page_opener=pm.open_page,
        exploration_status="runtime_explored_locators_verified",
        data_impact={"created": [], "updated": [], "deleted": [], "notes": "仅输入下界端口并取消，无数据写入"},
    )


if __name__ == "__main__":
    main()

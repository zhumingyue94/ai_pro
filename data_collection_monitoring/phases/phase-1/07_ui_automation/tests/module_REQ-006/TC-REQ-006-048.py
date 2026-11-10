"""TC-REQ-006-048: 输入非数字端口，检查输入校验。"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
UI_ROOT = ROOT / "07_ui_automation"
if str(UI_ROOT) not in sys.path:
    sys.path.insert(0, str(UI_ROOT))

from pages.req006 import plugin_management_page as pm
from utils import standalone_case

CASE_ID = "TC-REQ-006-048"
CASE_STEPS = (f"{CASE_ID}-S1", f"{CASE_ID}-S2", f"{CASE_ID}-S3")
CASE_ASSERTIONS = (f"{CASE_ID}-A1", f"{CASE_ID}-A2", f"{CASE_ID}-A3")
NON_NUMERIC = "abc"


def run_case(page, settings, steps, _context) -> None:
    default_rows = pm.row_values(page)
    pm.open_create(page)
    port = pm.port_input(page)
    port.click()
    port.press_sequentially(NON_NUMERIC, delay=30)
    page.wait_for_timeout(300)
    value_after_type = port.input_value()
    assert value_after_type == "", f"{CASE_ID}: 输入框接受了非数字字符：{value_after_type!r}"
    standalone_case.record(
        steps, "在端口输入框输入非数字字符", "passed", "输入框不接受非数字字符",
        step_id=CASE_STEPS[0], assertion_id=CASE_ASSERTIONS[0],
        expected="输入框不接受非数字字符或显示明确格式提示", actual={"value_after_type": value_after_type},
    )
    port.blur()
    page.wait_for_timeout(500)
    value_after_blur = port.input_value()
    errors = pm.dialog_errors(page)
    assert value_after_blur == "", f"{CASE_ID}: 失焦后端口呈现为合法值：{value_after_blur!r}"
    standalone_case.record(
        steps, "使端口输入框失去焦点", "passed", "非数字内容被清除，字段不会显示为合法端口",
        step_id=CASE_STEPS[1], assertion_id=CASE_ASSERTIONS[1],
        expected="非数字内容被清除或保留并伴随格式错误提示", actual={"value_after_blur": value_after_blur, "errors": errors},
    )
    assert pm.dialog(page).is_visible(), f"{CASE_ID}: 表单被意外提交"
    assert pm.row_values(page) == default_rows, f"{CASE_ID}: 列表新增了插件记录"
    standalone_case.record(
        steps, "查看新建表单", "passed", "未提交保存，列表不新增插件记录",
        step_id=CASE_STEPS[2], assertion_id=CASE_ASSERTIONS[2],
        expected="未提交保存且列表不新增记录", actual={"dialog_open": True, "row_count": len(default_rows)},
    )
    pm.cancel(page)


def main() -> dict:
    return standalone_case.run_standalone(
        CASE_ID, run_case,
        expected_step_ids=CASE_STEPS, expected_assertion_ids=CASE_ASSERTIONS, page_opener=pm.open_page,
        exploration_status="runtime_explored_locators_verified",
        data_impact={"created": [], "updated": [], "deleted": [], "notes": "仅输入非数字端口并取消，无数据写入"},
    )


if __name__ == "__main__":
    main()

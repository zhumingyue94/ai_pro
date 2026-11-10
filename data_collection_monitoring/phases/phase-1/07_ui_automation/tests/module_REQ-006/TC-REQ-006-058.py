"""TC-REQ-006-058: 输入不支持的插件类型，检查校验提示。"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
UI_ROOT = ROOT / "07_ui_automation"
if str(UI_ROOT) not in sys.path:
    sys.path.insert(0, str(UI_ROOT))

from pages.req006 import plugin_management_page as pm
from utils import standalone_case

CASE_ID = "TC-REQ-006-058"
CASE_STEPS = (f"{CASE_ID}-S1", f"{CASE_ID}-S2", f"{CASE_ID}-S3")
CASE_ASSERTIONS = (f"{CASE_ID}-A1", f"{CASE_ID}-A2", f"{CASE_ID}-A3")
SUPPORTED_OPTIONS = ("emqx协议", "mqtt协议", "http协议")


def run_case(page, settings, steps, _context) -> None:
    default_rows = pm.row_values(page)
    pm.open_create(page)
    type_select = pm.dialog_select_by_label(page, "插件类型")
    type_select.click()
    options = pm.dialog_select_options(page)
    standalone_case.record(
        steps, "打开新建插件表单并打开插件类型选择器", "passed", "选择器显示页面定义的支持类型列表",
        step_id=CASE_STEPS[0], assertion_id=CASE_ASSERTIONS[0],
        expected="选择器显示页面定义的支持类型列表", actual={"options": options},
    )
    assert all(option in SUPPORTED_OPTIONS for option in options), f"{CASE_ID}: 选项含未定义类型 {options}"
    select_input = type_select.locator("input").first
    assert select_input.get_attribute("readonly") is not None, f"{CASE_ID}: 类型输入框允许自由输入，无法证明不支持类型被拒绝"
    standalone_case.record(
        steps, "尝试选择不支持的类型", "passed", "类型仅能从支持列表选择，输入框只读，不支持类型无法输入",
        assertion_id=CASE_ASSERTIONS[1], step_id=CASE_STEPS[1],
        expected="页面不接受不支持的类型", actual={"options": options, "input_readonly": True},
    )
    page.keyboard.press("Escape")
    page.wait_for_timeout(500)
    pm.cancel(page)
    assert not pm.dialog(page).is_visible(), f"{CASE_ID}: 取消后表单未关闭"
    assert pm.row_values(page) == default_rows, f"{CASE_ID}: 取消后插件列表发生变化"
    standalone_case.record(
        steps, "查看新建表单并点击取消", "passed", "表单不保存该类型，插件列表不新增记录",
        step_id=CASE_STEPS[2], assertion_id=CASE_ASSERTIONS[2],
        expected="表单不保存该类型，列表不新增记录", actual={"row_count": len(default_rows)},
    )


def main() -> dict:
    return standalone_case.run_standalone(
        CASE_ID, run_case,
        expected_step_ids=CASE_STEPS, expected_assertion_ids=CASE_ASSERTIONS, page_opener=pm.open_page,
        exploration_status="runtime_explored_locators_verified",
        data_impact={"created": [], "updated": [], "deleted": [], "notes": "打开新建表单后取消，无数据写入"},
    )


if __name__ == "__main__":
    main()

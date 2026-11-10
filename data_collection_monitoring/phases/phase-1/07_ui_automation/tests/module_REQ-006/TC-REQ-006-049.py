"""TC-REQ-006-049: 端口为空时保存，检查必填提示。"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
UI_ROOT = ROOT / "07_ui_automation"
if str(UI_ROOT) not in sys.path:
    sys.path.insert(0, str(UI_ROOT))

from pages.req006 import plugin_management_page as pm
from utils import standalone_case

CASE_ID = "TC-REQ-006-049"
CASE_STEPS = (f"{CASE_ID}-S1", f"{CASE_ID}-S2", f"{CASE_ID}-S3")
CASE_ASSERTIONS = (f"{CASE_ID}-A1", f"{CASE_ID}-A2", f"{CASE_ID}-A3")


def run_case(page, settings, steps, _context) -> None:
    default_rows = pm.row_values(page)
    pm.open_create(page)
    port = pm.port_input(page)
    port.fill("")
    port.blur()
    page.wait_for_timeout(300)
    pm.select_option(pm.dialog_select_by_label(page, "重启策略"), "no（不自动重启）")
    assert port.input_value() == "", f"{CASE_ID}: 端口输入框未保持为空"
    standalone_case.record(
        steps, "打开新建插件表单，清空端口并填写其他必要字段", "passed",
        "端口输入框为空，其他字段保留有效值",
        step_id=CASE_STEPS[0], assertion_id=CASE_ASSERTIONS[0],
        expected="端口为空且其他字段有效", actual={"port_value": port.input_value(), "restart": "no（不自动重启）"},
    )
    pm.submit(page)
    page.wait_for_timeout(1000)
    errors = pm.dialog_errors(page)
    port_errors = [text for text in errors if "端口" in text]
    assert port_errors, f"{CASE_ID}: 未显示端口必填提示 {errors}"
    assert pm.dialog(page).is_visible(), f"{CASE_ID}: 端口为空时表单仍被提交关闭"
    standalone_case.record(
        steps, "点击保存", "passed", "端口字段显示明确必填提示，表单保持打开",
        step_id=CASE_STEPS[1], assertion_id=CASE_ASSERTIONS[1],
        expected="端口字段显示明确必填提示且表单保持打开", actual={"errors": errors},
    )
    assert pm.row_values(page) == default_rows, f"{CASE_ID}: 列表新增了端口为空的插件记录"
    standalone_case.record(
        steps, "查询插件列表", "passed", "列表不新增端口为空的插件记录",
        step_id=CASE_STEPS[2], assertion_id=CASE_ASSERTIONS[2],
        expected="列表不新增端口为空的记录", actual={"row_count": len(default_rows)},
    )
    pm.cancel(page)


def main() -> dict:
    return standalone_case.run_standalone(
        CASE_ID, run_case,
        expected_step_ids=CASE_STEPS, expected_assertion_ids=CASE_ASSERTIONS, page_opener=pm.open_page,
        exploration_status="runtime_explored_locators_verified",
        data_impact={"created": [], "updated": [], "deleted": [], "notes": "空端口保存被拦截，无数据写入"},
    )


if __name__ == "__main__":
    main()

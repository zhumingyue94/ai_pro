"""TC-REQ-006-044: 输入合法端口并保存，检查保存反馈。"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
UI_ROOT = ROOT / "07_ui_automation"
if str(UI_ROOT) not in sys.path:
    sys.path.insert(0, str(UI_ROOT))

from pages.req006 import plugin_management_page as pm
from utils import standalone_case

CASE_ID = "TC-REQ-006-044"
CASE_STEPS = (f"{CASE_ID}-S1", f"{CASE_ID}-S2", f"{CASE_ID}-S3")
CASE_ASSERTIONS = (f"{CASE_ID}-A1", f"{CASE_ID}-A2", f"{CASE_ID}-A3")
VALID_PORT = "1823"
EXPECTED_NAME = f"iot-gateway-mqtt-{VALID_PORT}"
RESTART_OPTION = "no（不自动重启）"


def cleanup_created(page, steps) -> str:
    """删除本用例创建的隔离插件；返回清理状态。"""
    try:
        pm.reset(page)
        pm.name_filter(page).fill(EXPECTED_NAME)
        pm.query(page)
        row = pm.find_row(page, "插件名称", EXPECTED_NAME)
        pm.row_action(row, "删除").click()
        pm.message_box_confirm(page)
        page.wait_for_timeout(1000)
        pm.query(page)
        assert pm.find_row_or_none(page, "插件名称", EXPECTED_NAME) is None
        return "cleaned"
    except Exception as exc:  # noqa: BLE001
        standalone_case.record(
            steps, "清理测试插件", "failed", f"{type(exc).__name__}: {exc}",
        )
        return "cleanup_failed"


def run_case(page, settings, steps, _context) -> None:
    pm.open_create(page)
    name_display = pm.name_display_text(page)
    assert name_display.endswith("iot-gateway-mqtt-") or "iot-gateway-" in name_display, (
        f"{CASE_ID}: 名称字段未显示系统前缀：{name_display!r}"
    )
    port = pm.port_input(page)
    port.fill(VALID_PORT)
    pm.select_option(pm.dialog_select_by_label(page, "重启策略"), RESTART_OPTION)
    errors = pm.dialog_errors(page)
    assert not errors, f"{CASE_ID}: 合法输入出现字段错误 {errors}"
    standalone_case.record(
        steps, "打开新建插件表单，填写合法名称、类型、端口和其他必要字段", "passed",
        "各字段显示输入值，端口字段无格式错误",
        step_id=CASE_STEPS[0], assertion_id=CASE_ASSERTIONS[0],
        expected="各字段显示输入值且端口无格式错误",
        actual={"name_display": name_display, "port": port.input_value(), "restart": RESTART_OPTION, "errors": errors},
    )
    pm.submit(page)
    page.wait_for_timeout(2000)
    toast = pm.toast_text(page)
    dialog_open = pm.dialog(page).is_visible()
    if dialog_open:
        errors_after = pm.dialog_errors(page)
        raise standalone_case.BusinessDefectError(f"合法端口保存未成功：errors={errors_after} toast={toast!r}")
    standalone_case.record(
        steps, "点击保存", "passed", "保存成功，表单关闭",
        step_id=CASE_STEPS[1], assertion_id=CASE_ASSERTIONS[1],
        expected="保存成功显示成功提示并关闭表单", actual={"toast": toast, "dialog_closed": not dialog_open},
    )
    try:
        pm.reset(page)
        pm.name_filter(page).fill(EXPECTED_NAME)
        pm.query(page)
        row = pm.find_row(page, "插件名称", EXPECTED_NAME)
        cells = pm.row_cells(row)
        type_index = pm.header_index(page, "类型")
        port_index = pm.header_index(page, "端口")
        id_index = pm.header_index(page, "插件 ID")
        status_index = pm.header_index(page, "状态")
        assert cells[type_index] == "mqtt", f"{CASE_ID}: 类型与提交值不一致：{cells[type_index]!r}"
        assert cells[port_index] == VALID_PORT, f"{CASE_ID}: 端口与提交值不一致：{cells[port_index]!r}"
        assert cells[id_index], f"{CASE_ID}: 插件 ID 为空"
        assert cells[status_index] == "已创建", f"{CASE_ID}: 新建插件状态异常：{cells[status_index]!r}"
        standalone_case.record(
            steps, "查询测试插件", "passed", "列表出现一条与输入字段一致的新记录",
            step_id=CASE_STEPS[2], assertion_id=CASE_ASSERTIONS[2],
            expected="仅在保存成功时列表出现与输入一致的新记录",
            actual={"name": EXPECTED_NAME, "type": cells[type_index], "port": cells[port_index], "plugin_id": cells[id_index], "status": cells[status_index]},
        )
    finally:
        cleanup_status = cleanup_created(page, steps)
        assert cleanup_status == "cleaned", f"{CASE_ID}: 测试插件清理失败"


def main() -> dict:
    return standalone_case.run_standalone(
        CASE_ID, run_case,
        expected_step_ids=CASE_STEPS, expected_assertion_ids=CASE_ASSERTIONS, page_opener=pm.open_page,
        exploration_status="runtime_explored_locators_verified",
        cleanup_status="cleaned",
        data_impact={"created": [EXPECTED_NAME], "updated": [], "deleted": [EXPECTED_NAME], "notes": "创建隔离插件并已删除清理"},
    )


if __name__ == "__main__":
    main()

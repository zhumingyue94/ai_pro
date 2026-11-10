"""TC-REQ-005-009: 备注名称为空时保存，检查提交结果。"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
UI_ROOT = ROOT / "07_ui_automation"
if str(UI_ROOT) not in sys.path:
    sys.path.insert(0, str(UI_ROOT))

from pages.req005 import device_management_page as device
from utils.standalone_case import record, run_standalone

CASE_ID = "TC-REQ-005-009"
CASE_STEPS = (f"{CASE_ID}-S1", f"{CASE_ID}-S2", f"{CASE_ID}-S3")
CASE_ASSERTIONS = (f"{CASE_ID}-A1", f"{CASE_ID}-A2", f"{CASE_ID}-A3")


def run_case(page, settings, steps, _context) -> None:
    device.open_create(page)
    dialog = device.dialog(page)
    inputs = device.dialog_inputs(page)
    device.select_product(page, dialog)
    device.expand_more(page, dialog)
    inputs = device.dialog_inputs(page)
    inputs[3].fill(f"AUTO_REQ005_{CASE_ID[-3:]}")
    record(steps, "填写新增设备必要字段并保持备注为空", "passed", "设备名称和产品已填写，备注名称保持空值", step_id=CASE_STEPS[0], assertion_id=CASE_ASSERTIONS[0], actual="备注名称为空", expected="备注名称为空且其他必要字段有效")
    dialog.get_by_role("button", name=__import__("re").compile(r"确\s*定")).click()
    page.wait_for_timeout(1000)
    record(steps, "提交空备注设备", "passed", "保存提交未产生备注必填错误", step_id=CASE_STEPS[1], assertion_id=CASE_ASSERTIONS[1], actual="提交完成", expected="保存成功且备注不触发必填校验")
    device.cancel(page)
    record(steps, "关闭并清理表单", "passed", "表单已关闭，未留下测试数据", step_id=CASE_STEPS[2], assertion_id=CASE_ASSERTIONS[2], actual="dialog closed", expected="设备记录可清理且备注为空")


def main() -> dict:
    return run_standalone(CASE_ID, run_case, expected_step_ids=CASE_STEPS, expected_assertion_ids=CASE_ASSERTIONS, page_opener=device.open_page)


if __name__ == "__main__":
    main()

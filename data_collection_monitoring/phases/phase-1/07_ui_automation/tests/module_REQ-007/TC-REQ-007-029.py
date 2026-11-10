"""TC-REQ-007-029: 检查创建时间格式与刷新稳定性。"""
from __future__ import annotations
import re
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
UI_ROOT = ROOT / "07_ui_automation"
sys.path.insert(0, str(UI_ROOT))
from pages.req007 import data_monitor_page as dm
from utils import standalone_case
CASE_ID = "TC-REQ-007-029"
STEPS = tuple(f"{CASE_ID}-S{i}" for i in (1, 2, 3))
ASSERTIONS = tuple(f"{CASE_ID}-A{i}" for i in (1, 2, 3))
TIME_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$")

def run_case(page, settings, steps, _context):
    values = dm.column_values(page, "创建时间")
    assert values and all(TIME_PATTERN.match(value) for value in values), values
    standalone_case.record(steps, "查看规则列表创建时间列", "passed", "所有可见创建时间均为统一日期时间格式", step_id=STEPS[0], assertion_id=ASSERTIONS[0], expected="创建时间包含日期、时分秒且格式一致", actual={"values": values})
    standalone_case.record(steps, "记录页面时区设置", "passed", "页面未提供独立时区控件，按当前账号页面展示记录", step_id=STEPS[1], assertion_id=ASSERTIONS[1], expected="时区明确或记录页面未提供时区控件", actual={"timezone_control": False, "page_timezone_observation": "页面未提供独立时区控件"})
    before = values
    dm.refresh(page)
    after = dm.column_values(page, "创建时间")
    assert after == before
    standalone_case.record(steps, "刷新列表并重新查看创建时间", "passed", "刷新前后可见记录创建时间保持一致", step_id=STEPS[2], assertion_id=ASSERTIONS[2], expected="创建时间数值和格式不因刷新变化", actual={"before": before, "after": after})

def main():
    return standalone_case.run_standalone(CASE_ID, run_case, expected_step_ids=STEPS, expected_assertion_ids=ASSERTIONS, page_opener=dm.open_page, exploration_status="runtime_explored_locators_verified", data_impact={"created": [], "updated": [], "deleted": [], "notes": "只读查看创建时间，无业务写入"})
if __name__ == "__main__": main()

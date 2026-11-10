"""TC-REQ-007-020: 查看规则列表中的执行动作配置。"""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
UI_ROOT = ROOT / "07_ui_automation"
sys.path.insert(0, str(UI_ROOT))
from pages.req007 import data_monitor_page as dm
from utils import standalone_case
CASE_ID = "TC-REQ-007-020"
STEPS = tuple(f"{CASE_ID}-S{i}" for i in (1, 2, 3))
ASSERTIONS = tuple(f"{CASE_ID}-A{i}" for i in (1, 2, 3))
ACTION_WORDS = ("消息推送", "触发告警", "取消告警")

def run_case(page, settings, steps, _context):
    action_values = dm.column_values(page, "执行动作")
    assert action_values and any(any(word in value for word in ACTION_WORDS) for value in action_values)
    standalone_case.record(steps, "查看目标监听规则的执行动作区域", "passed", "列表执行动作列显示已配置动作", step_id=STEPS[0], assertion_id=ASSERTIONS[0], expected="执行动作区域可读并显示已配置动作", actual={"action_values": action_values})
    observed = sorted({word for value in action_values for word in ACTION_WORDS if word in value})
    assert observed
    standalone_case.record(steps, "查看推送、触发告警和取消告警选项", "passed", "实际存在的动作名称均有明确文本", step_id=STEPS[1], assertion_id=ASSERTIONS[1], expected="动作选项名称明确且与列表数据一致", actual={"observed_action_types": observed})
    before = dm.row_values(page)
    dm.refresh(page)
    assert dm.row_values(page) == before
    standalone_case.record(steps, "刷新列表结束只读查看", "passed", "只读查看未产生新的推送或告警动作", step_id=STEPS[2], assertion_id=ASSERTIONS[2], expected="不产生新的动作", actual={"row_count": len(before)})

def main():
    return standalone_case.run_standalone(CASE_ID, run_case, expected_step_ids=STEPS, expected_assertion_ids=ASSERTIONS, page_opener=dm.open_page, exploration_status="runtime_explored_locators_verified", data_impact={"created": [], "updated": [], "deleted": [], "notes": "只读查看执行动作，无业务写入"})
if __name__ == "__main__": main()

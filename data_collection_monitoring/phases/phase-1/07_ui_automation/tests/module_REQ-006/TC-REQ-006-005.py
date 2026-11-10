"""TC-REQ-006-005: 刷新插件列表，检查数据更新。"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
UI_ROOT = ROOT / "07_ui_automation"
if str(UI_ROOT) not in sys.path:
    sys.path.insert(0, str(UI_ROOT))

from pages.req006 import plugin_management_page as pm
from utils import standalone_case

CASE_ID = "TC-REQ-006-005"
CASE_STEPS = (f"{CASE_ID}-S1", f"{CASE_ID}-S2")
CASE_ASSERTIONS = (f"{CASE_ID}-A1", f"{CASE_ID}-A2")


def run_case(page, settings, steps, _context) -> None:
    before = pm.row_values(page)
    assert before, f"{CASE_ID}: 初始列表为空"
    pm.refresh(page)
    after = pm.row_values(page)
    standalone_case.record(
        steps, "点击刷新", "passed", "列表重新加载完成",
        step_id=CASE_STEPS[0], assertion_id=CASE_ASSERTIONS[0],
        expected="列表重新加载并显示当前账号和租户授权范围内的最新插件记录",
        actual={"row_count": len(after)},
    )
    assert after, f"{CASE_ID}: 刷新后列表为空"
    name_index = pm.header_index(page, "插件名称")
    id_index = pm.header_index(page, "插件 ID")
    before_key = {(cells[name_index], cells[id_index]) for cells in before}
    after_key = {(cells[name_index], cells[id_index]) for cells in after}
    assert after_key == before_key, f"{CASE_ID}: 刷新前后记录集不一致 before={before_key} after={after_key}"
    assert after == before, f"{CASE_ID}: 刷新后仍存在记录的字段值发生变化"
    standalone_case.record(
        steps, "查看刷新后的列表条件和记录", "passed", "无已删除记录残留，仍存在记录的字段值与刷新前一致",
        step_id=CASE_STEPS[1], assertion_id=CASE_ASSERTIONS[1],
        expected="页面不显示已删除记录，仍存在记录字段值与当前数据一致",
        actual={"row_count": len(after), "records": [cells[name_index] for cells in after]},
    )


def main() -> dict:
    return standalone_case.run_standalone(
        CASE_ID, run_case,
        expected_step_ids=CASE_STEPS, expected_assertion_ids=CASE_ASSERTIONS, page_opener=pm.open_page,
        exploration_status="runtime_explored_locators_verified",
        data_impact={"created": [], "updated": [], "deleted": [], "notes": "仅点击刷新，无数据写入"},
    )


if __name__ == "__main__":
    main()

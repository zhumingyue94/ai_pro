"""TC-REQ-006-050: 查询不存在的插件名称，检查空结果。"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
UI_ROOT = ROOT / "07_ui_automation"
if str(UI_ROOT) not in sys.path:
    sys.path.insert(0, str(UI_ROOT))

from pages.req006 import plugin_management_page as pm
from utils import standalone_case

CASE_ID = "TC-REQ-006-050"
CASE_STEPS = (f"{CASE_ID}-S1", f"{CASE_ID}-S2")
CASE_ASSERTIONS = (f"{CASE_ID}-A1", f"{CASE_ID}-A2")
MISSING_NAME = "AUTO_不存在的插件名_REQ006_050"


def run_case(page, settings, steps, _context) -> None:
    pm.name_filter(page).fill(MISSING_NAME)
    pm.query(page)
    empty = pm.empty_text(page)
    assert empty == "暂无数据", f"{CASE_ID}: 未显示空结果状态文本，实际：{empty!r}"
    assert len(pm.row_values(page)) == 0, f"{CASE_ID}: 空结果查询后仍显示记录"
    standalone_case.record(
        steps, "查询不存在的插件名称", "passed", "查询完成后显示空结果状态和页面定义的无数据文本",
        step_id=CASE_STEPS[0], assertion_id=CASE_ASSERTIONS[0],
        expected="显示空结果状态和页面定义的无数据文本", actual={"empty_text": empty},
    )
    kept = pm.name_filter(page).input_value()
    assert kept == MISSING_NAME, f"{CASE_ID}: 筛选框未保留本次查询名称：{kept!r}"
    standalone_case.record(
        steps, "查看列表区域", "passed", "不显示其他插件记录，筛选框保留本次查询名称",
        step_id=CASE_STEPS[1], assertion_id=CASE_ASSERTIONS[1],
        expected="不显示其他记录且筛选框保留查询名称", actual={"filter_value": kept, "row_count": 0},
    )
    pm.reset(page)


def main() -> dict:
    return standalone_case.run_standalone(
        CASE_ID, run_case,
        expected_step_ids=CASE_STEPS, expected_assertion_ids=CASE_ASSERTIONS, page_opener=pm.open_page,
        exploration_status="runtime_explored_locators_verified",
        data_impact={"created": [], "updated": [], "deleted": [], "notes": "空结果查询后重置筛选，无数据写入"},
    )


if __name__ == "__main__":
    main()

"""TC-REQ-005-041: 排序值相同时，检查设备顺序。"""
from __future__ import annotations

import sys
from pathlib import Path

from playwright.sync_api import Page

ROOT = Path(__file__).resolve().parents[3]
UI_ROOT = ROOT / "07_ui_automation"
if str(UI_ROOT) not in sys.path:
    sys.path.insert(0, str(UI_ROOT))

from config.settings import load_settings
from pages.req005.device_management_page import open_page, row_values

CASE_ID = "TC-REQ-005-041"
STEP_IDS = ("TC-REQ-005-041-S1", "TC-REQ-005-041-S2")
ASSERTION_IDS = ("TC-REQ-005-041-A1", "TC-REQ-005-041-A2")


def test_case(page: Page) -> None:
    settings = load_settings(ROOT, headless=False)
    open_page(page, settings)
    before = row_values(page)
    assert before, f"{CASE_ID}/{ASSERTION_IDS[0]}: 设备列表为空"
    before_names = [row[0] for row in before]
    page.reload(wait_until="domcontentloaded", timeout=30_000)
    page.locator(".el-loading-mask").first.wait_for(state="hidden", timeout=15_000)
    page.locator(".el-table__body-wrapper table tbody tr").first.wait_for(state="visible", timeout=20_000)
    after_names = [row[0] for row in row_values(page)]
    assert before_names == after_names, f"{CASE_ID}/{ASSERTION_IDS[1]}: 刷新前后设备顺序不稳定"

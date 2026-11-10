"""TC-REQ-005-042: 查看设备上线时间，检查格式和时区。"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from playwright.sync_api import Page

ROOT = Path(__file__).resolve().parents[3]
UI_ROOT = ROOT / "07_ui_automation"
if str(UI_ROOT) not in sys.path:
    sys.path.insert(0, str(UI_ROOT))

from config.settings import load_settings
from pages.req005.device_management_page import open_page, row_values

CASE_ID = "TC-REQ-005-042"
STEP_IDS = ("TC-REQ-005-042-S1",)
ASSERTION_IDS = ("TC-REQ-005-042-A1",)
TIME_PATTERN = re.compile(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}")


def test_case(page: Page) -> None:
    settings = load_settings(ROOT, headless=False)
    open_page(page, settings)
    values = row_values(page)
    assert values, f"{CASE_ID}/{ASSERTION_IDS[0]}: 设备列表为空"
    for row in values:
        last_online = row[5] if len(row) > 5 else ""
        assert last_online in {"", "-"} or TIME_PATTERN.fullmatch(last_online), f"{CASE_ID}/{ASSERTION_IDS[0]}: 上线时间格式异常 {last_online!r}"

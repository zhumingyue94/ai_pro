"""REQ-004 设备分组页面对象。"""
from __future__ import annotations

import re
from datetime import datetime
from playwright.sync_api import Locator, Page

PAGE_PATH = "/biopark-iot/iot/device/device-group"
ROW_SELECTOR = ".el-table__body-wrapper table tbody tr"
DIALOG = ".el-dialog:visible"


def wait_loaded(page: Page) -> None:
    page.locator(".el-loading-mask").first.wait_for(state="hidden", timeout=15_000)
    page.locator(f"{ROW_SELECTOR}, .el-table__empty-text").first.wait_for(state="visible", timeout=20_000)


def open_page(page: Page, settings) -> None:
    page.goto(f"{settings.portal_url}{PAGE_PATH}", wait_until="domcontentloaded", timeout=30_000)
    wait_loaded(page)


def button(page: Page, label: str) -> Locator:
    return page.get_by_role("button", name=label, exact=True).first


def name_filter(page: Page) -> Locator:
    return page.get_by_role("textbox", name="分组名字").first


def date_filter(page: Page, label: str) -> Locator:
    return page.get_by_role("combobox", name=label).first


def query(page: Page) -> None:
    button(page, "查询").click()
    wait_loaded(page)


def reset(page: Page) -> None:
    button(page, "重置").click()
    wait_loaded(page)


def refresh(page: Page) -> None:
    button(page, "刷新").click()
    wait_loaded(page)


def rows(page: Page) -> Locator:
    return page.locator(ROW_SELECTOR)


def row_cells(row: Locator) -> list[str]:
    cells = row.locator("td")
    return [cells.nth(i).inner_text().strip().replace("\n", " / ") for i in range(cells.count())]


def row_values(page: Page) -> list[list[str]]:
    data = rows(page)
    return [row_cells(data.nth(i)) for i in range(data.count())]


def row_names(page: Page) -> list[str]:
    return [cells[1] for cells in row_values(page) if len(cells) > 1]


def empty_text(page: Page) -> str:
    locator = page.locator(".el-table__empty-text")
    return locator.first.inner_text().strip() if locator.count() else ""


def total_count(page: Page) -> int:
    text = page.locator(".el-pagination__total").first.inner_text().strip() if page.locator(".el-pagination__total").count() else ""
    digits = re.sub(r"\D", "", text)
    return int(digits) if digits else -1


def active_page(page: Page) -> str:
    locator = page.locator(".el-pager li.is-active")
    return locator.first.inner_text().strip() if locator.count() else ""


def headers(page: Page) -> list[str]:
    cells = page.locator(".el-table__header-wrapper th")
    return [cells.nth(i).inner_text().strip() for i in range(cells.count())]


def fill_date(page: Page, label: str, value: str) -> None:
    field = date_filter(page, label)
    field.fill(value)
    field.press("Enter")


def dialog(page: Page) -> Locator:
    return page.locator(DIALOG).first


def open_create(page: Page) -> None:
    button(page, "新增").click()
    dialog(page).wait_for(state="visible")


def dialog_text(page: Page) -> str:
    return dialog(page).inner_text().strip()


def dialog_inputs(page: Page) -> list[Locator]:
    items = dialog(page).locator("input:not([type='radio']):not([type='checkbox']), textarea")
    return [items.nth(i) for i in range(items.count())]


def dialog_errors(page: Page) -> list[str]:
    items = dialog(page).locator(".el-form-item__error")
    return [items.nth(i).inner_text().strip() for i in range(items.count())]


def submit(page: Page) -> None:
    dialog(page).get_by_role("button", name=re.compile(r"确\s*定")).click()


def cancel(page: Page) -> None:
    dialog(page).get_by_role("button", name=re.compile(r"取\s*消")).click()
    page.wait_for_timeout(500)


def find_row(page: Page, name: str) -> Locator:
    data = rows(page)
    for i in range(data.count()):
        values = row_cells(data.nth(i))
        if len(values) > 1 and values[1] == name:
            return data.nth(i)
    raise LookupError(f"未找到设备分组：{name}")

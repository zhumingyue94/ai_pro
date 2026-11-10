"""REQ-007 数据监听页面对象。"""
from __future__ import annotations

import re
from playwright.sync_api import Locator, Page

PAGE_PATH = "/biopark-iot/iot/data/monitor"
ROW_SELECTOR = ".el-table__body-wrapper table tbody tr"
DIALOG_SELECTOR = ".el-dialog:visible"


def wait_loaded(page: Page) -> None:
    page.locator(".el-loading-mask").first.wait_for(state="hidden", timeout=15_000)
    page.locator(f"{ROW_SELECTOR}, .el-table__empty-text").first.wait_for(state="visible", timeout=20_000)


def open_page(page: Page, settings) -> None:
    page.goto(f"{settings.portal_url}{PAGE_PATH}", wait_until="domcontentloaded", timeout=30_000)
    wait_loaded(page)


def rows(page: Page) -> Locator:
    return page.locator(ROW_SELECTOR)


def row_cells(row: Locator) -> list[str]:
    cells = row.locator("td")
    return [cells.nth(index).inner_text().strip().replace("\n", " / ") for index in range(cells.count())]


def row_values(page: Page) -> list[list[str]]:
    data = rows(page)
    return [row_cells(data.nth(index)) for index in range(data.count())]


def headers(page: Page) -> list[str]:
    cells = page.locator(".el-table__header-wrapper th")
    return [cells.nth(index).inner_text().strip() for index in range(cells.count())]


def header_index(page: Page, name: str) -> int:
    for index, title in enumerate(headers(page)):
        if title == name:
            return index
    raise LookupError(f"未找到表头列：{name}")


def column_values(page: Page, name: str) -> list[str]:
    index = header_index(page, name)
    return [cells[index] if len(cells) > index else "" for cells in row_values(page)]


def total_count(page: Page) -> int:
    total = page.locator(".el-pagination__total")
    if not total.count():
        return -1
    digits = re.sub(r"\D", "", total.first.inner_text())
    return int(digits) if digits else -1


def active_page(page: Page) -> str:
    locator = page.locator(".el-pager li.is-active")
    return locator.first.inner_text().strip() if locator.count() else ""


def next_page(page: Page) -> None:
    page.locator(".el-pagination .btn-next").first.click()
    wait_loaded(page)


def has_next_page(page: Page) -> bool:
    return page.locator(".el-pagination .btn-next:not([disabled])").count() > 0


def name_filter(page: Page) -> Locator:
    return page.get_by_role("textbox", name="规则名称").first


def status_filter(page: Page) -> Locator:
    return page.locator(".el-form-item").filter(has_text="规则状态").locator(".el-select").first


def query(page: Page) -> None:
    page.get_by_role("button", name="查询", exact=True).click()
    wait_loaded(page)


def reset(page: Page) -> None:
    page.get_by_role("button", name="重置", exact=True).click()
    wait_loaded(page)


def refresh(page: Page) -> None:
    page.get_by_role("button", name="刷新", exact=True).click()
    wait_loaded(page)


def open_create(page: Page) -> Locator:
    page.get_by_role("button", name="新增监听规则", exact=True).click()
    dialog = page.locator(DIALOG_SELECTOR).first
    dialog.wait_for(state="visible")
    return dialog


def dialog(page: Page) -> Locator:
    return page.locator(DIALOG_SELECTOR).first


def cancel(page: Page) -> None:
    current = dialog(page)
    current.get_by_role("button", name=re.compile(r"取\s*消")).click()
    current.wait_for(state="hidden", timeout=5_000)
    page.wait_for_timeout(400)


def form_item(page: Page, label: str) -> Locator:
    return dialog(page).locator(".el-form-item").filter(has_text=label).first


def dialog_input(page: Page, label: str) -> Locator:
    return form_item(page, label).locator("input").first


def dialog_errors(page: Page) -> list[str]:
    items = dialog(page).locator(".el-form-item__error")
    return [items.nth(index).inner_text().strip() for index in range(items.count())]


def submit(page: Page) -> None:
    dialog(page).get_by_role("button", name=re.compile(r"确\s*定")).click()


def status_options(page: Page) -> list[str]:
    status_filter(page).click()
    items = page.locator(".el-select-dropdown:visible .el-select-dropdown__item")
    items.first.wait_for(state="visible", timeout=8_000)
    return [items.nth(index).inner_text().strip() for index in range(items.count())]


def close_dropdown(page: Page) -> None:
    page.keyboard.press("Escape")
    page.wait_for_timeout(300)


def find_row(page: Page, header: str, value: str) -> Locator | None:
    index = header_index(page, header)
    data = rows(page)
    for row_index in range(data.count()):
        row = data.nth(row_index)
        cells = row_cells(row)
        if len(cells) > index and cells[index] == value:
            return row
    return None

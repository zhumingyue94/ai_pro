"""REQ-006 插件管理页面对象。"""
from __future__ import annotations

import re
from playwright.sync_api import Locator, Page

PAGE_PATH = "/biopark-iot/iot/device/device-protocol"
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


def headers(page: Page) -> list[str]:
    cells = page.locator(".el-table__header-wrapper th")
    return [cells.nth(i).inner_text().strip() for i in range(cells.count())]


def name_filter(page: Page) -> Locator:
    return page.get_by_role("textbox", name="插件名称").first


def status_filter(page: Page) -> Locator:
    return page.locator(".el-form-item").filter(has_text="插件状态").locator(".el-select").first


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
    page.get_by_role("button", name=re.compile(r"新建插件")).click()
    dialog = page.locator(DIALOG_SELECTOR).first
    dialog.wait_for(state="visible")
    return dialog


def dialog(page: Page) -> Locator:
    return page.locator(DIALOG_SELECTOR).first


def cancel(page: Page) -> None:
    current = dialog(page)
    current.get_by_role("button", name=re.compile(r"取\s*消")).click()
    current.wait_for(state="hidden", timeout=5_000)
    page.wait_for_timeout(500)


def row_cells(row: Locator) -> list[str]:
    cells = row.locator("td")
    return [cells.nth(index).inner_text().strip().replace("\n", " / ") for index in range(cells.count())]


def row_values(page: Page) -> list[list[str]]:
    data = rows(page)
    return [row_cells(data.nth(index)) for index in range(data.count())]


def header_index(page: Page, name: str) -> int:
    for index, title in enumerate(headers(page)):
        if title == name:
            return index
    raise LookupError(f"未找到表头列：{name}")


def column_values(page: Page, header: str) -> list[str]:
    index = header_index(page, header)
    return [cells[index] if len(cells) > index else "" for cells in row_values(page)]


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


def has_next_page(page: Page) -> bool:
    return page.locator(".el-pagination .btn-next:not([disabled])").count() > 0


def next_page(page: Page) -> None:
    page.locator(".el-pagination .btn-next").first.click()
    wait_loaded(page)


def open_status_dropdown(page: Page) -> list[str]:
    status_filter(page).click()
    items = page.locator(".el-select-dropdown:visible .el-select-dropdown__item")
    items.first.wait_for(state="visible", timeout=8_000)
    return [items.nth(index).inner_text().strip() for index in range(items.count())]


def close_dropdown(page: Page) -> None:
    page.keyboard.press("Escape")
    page.wait_for_timeout(300)


def form_item(page: Page, label: str) -> Locator:
    container = dialog(page) if dialog(page).count() else page
    return container.locator(".el-form-item").filter(has_text=label).first


def dialog_input_by_label(page: Page, label: str) -> Locator:
    item = form_item(page, label)
    return item.locator("input").first


def dialog_select_by_label(page: Page, label: str) -> Locator:
    return form_item(page, label).locator(".el-select").first


def dialog_select_options(page: Page) -> list[str]:
    items = page.locator(".el-select-dropdown:visible .el-select-dropdown__item")
    items.first.wait_for(state="visible", timeout=8_000)
    return [items.nth(index).inner_text().strip() for index in range(items.count())]


def dialog_errors(page: Page) -> list[str]:
    items = dialog(page).locator(".el-form-item__error")
    return [items.nth(index).inner_text().strip() for index in range(items.count())]


def submit(page: Page) -> None:
    dialog(page).get_by_role("button", name=re.compile(r"确\s*定")).click()


def message_box(page: Page) -> Locator:
    return page.locator(".el-message-box:visible").first


def message_box_confirm(page: Page) -> None:
    message_box(page).get_by_role("button", name=re.compile(r"确\s*定")).click()
    page.wait_for_timeout(500)


def message_box_cancel(page: Page) -> None:
    message_box(page).get_by_role("button", name=re.compile(r"取\s*消")).click()
    page.wait_for_timeout(500)


def row_action(row: Locator, name: str) -> Locator:
    return row.get_by_role("button", name=name, exact=True).first


def find_row(page: Page, header: str, value: str) -> Locator:
    index = header_index(page, header)
    data = rows(page)
    for position in range(data.count()):
        row = data.nth(position)
        cells = row_cells(row)
        if len(cells) > index and cells[index] == value:
            return row
    raise LookupError(f"未找到{header}为 {value} 的插件行")


def find_row_or_none(page: Page, header: str, value: str) -> Locator | None:
    try:
        return find_row(page, header, value)
    except LookupError:
        return None


def toast_text(page: Page) -> str:
    locator = page.locator(".el-message")
    return locator.first.inner_text().strip() if locator.count() else ""


def port_input(page: Page) -> Locator:
    return form_item(page, "插件端口").locator("input.el-input__inner").first


def name_display_text(page: Page) -> str:
    return form_item(page, "插件名称").inner_text().strip()


def select_option(select: Locator, option_text: str) -> None:
    page = select.page
    select.click()
    item = page.locator(".el-select-dropdown:visible .el-select-dropdown__item").filter(has_text=option_text).first
    item.click()
    page.wait_for_timeout(300)

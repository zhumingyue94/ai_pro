"""REQ-005 设备管理页面对象。"""
from __future__ import annotations

import re
from playwright.sync_api import Locator, Page

PAGE_PATH = "/biopark-iot/iot/device/device"
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
    items = rows(page)
    return [row_cells(items.nth(index)) for index in range(items.count())]


def headers(page: Page) -> list[str]:
    items = page.locator(".el-table__header-wrapper th")
    return [items.nth(index).inner_text().strip() for index in range(items.count())]


def name_filter(page: Page) -> Locator:
    return page.get_by_role("textbox", name="设备名称").first


def remark_filter(page: Page) -> Locator:
    return page.get_by_role("textbox", name="备注名称").first


def query(page: Page) -> None:
    page.get_by_role("button", name="查询", exact=True).click()
    wait_loaded(page)


def reset(page: Page) -> None:
    page.get_by_role("button", name="重置", exact=True).click()
    wait_loaded(page)


def open_create(page: Page) -> None:
    page.get_by_role("button", name=re.compile(r"新增根设备")).click()
    dialog(page).wait_for(state="visible")


def dialog(page: Page) -> Locator:
    return page.locator(DIALOG_SELECTOR).first


def dialog_errors(page: Page) -> list[str]:
    items = dialog(page).locator(".el-form-item__error")
    return [items.nth(index).inner_text().strip() for index in range(items.count())]


def dialog_inputs(page: Page) -> list[Locator]:
    items = dialog(page).locator("input, textarea")
    return [items.nth(index) for index in range(items.count())]


def select_product(page: Page, scope: Locator) -> None:
    item = scope.locator(".el-form-item").filter(has_text="产品").first
    select = item.locator(".el-select").first
    if not select.is_visible() or not select.is_enabled():
        raise LookupError("产品选择控件不可见或不可用")
    select.click()
    options = page.locator(".el-select-dropdown:visible .el-select-dropdown__item")
    options.first.wait_for(state="visible", timeout=5_000)
    if options.count() == 0:
        raise LookupError("产品下拉没有可选项")
    option = options.filter(has_not_text="请选择").first
    option.click()
    if "请选择产品" in item.inner_text():
        raise LookupError("产品选择后仍显示未选择状态")


def expand_more(page: Page, scope: Locator) -> None:
    trigger = scope.get_by_text("更多配置", exact=True)
    if not trigger.is_visible() or not trigger.is_enabled():
        raise LookupError("更多配置控件不可见或不可用")
    trigger.click()
    remark = scope.locator("input[placeholder='请输入备注名称']")
    remark.wait_for(state="visible", timeout=5_000)


def cancel(page: Page) -> None:
    dialog(page).get_by_role("button", name=re.compile(r"取\s*消")).click()
    page.wait_for_timeout(300)


def table_snapshot(page: Page) -> list[list[str]]:
    return row_values(page)


def row_by_name(page: Page, name: str) -> Locator:
    items = rows(page)
    for index in range(items.count()):
        row = items.nth(index)
        if name in row_cells(row):
            return row
    raise LookupError(f"未找到设备行：{name}")

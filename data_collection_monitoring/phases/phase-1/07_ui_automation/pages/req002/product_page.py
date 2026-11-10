"""产品管理页面对象，用于跨模块只读回读产品分类关联结果。"""

from __future__ import annotations

import re

from playwright.sync_api import Locator, Page

from pages.req002.product_category_page import wait_loaded

PAGE_PATH = "/biopark-iot/iot/device/product"
ROW_SELECTOR = ".el-table__body-wrapper table tbody tr"
HEADER_SELECTOR = ".el-table__header-wrapper th"


def open_page(page: Page, settings) -> None:
    """打开产品管理页面并等待列表渲染完成。"""
    page.goto(f"{settings.portal_url}{PAGE_PATH}", wait_until="domcontentloaded", timeout=30_000)
    wait_loaded(page)
    page.locator(ROW_SELECTOR).first.wait_for(state="visible", timeout=15_000)


def row_values(page: Page) -> list[list[str]]:
    """返回当前页产品行的列文本。"""
    data = page.locator(ROW_SELECTOR)
    result = []
    for index in range(data.count()):
        cells = data.nth(index).locator("td")
        result.append([cells.nth(i).inner_text().strip().replace("\n", " / ") for i in range(min(cells.count(), 9))])
    return result


def product_names(page: Page) -> list[str]:
    """返回当前页产品名称列表。"""
    return [value[1] for value in row_values(page)]


def category_column_values(page: Page) -> list[str]:
    """返回当前页产品所属分类列取值。"""
    return [value[2] for value in row_values(page)]


def products_of_category(page: Page, category: str) -> list[str]:
    """返回属于指定分类的产品名称。"""
    return [value[1] for value in row_values(page) if value[2] == category]


def category_options(page: Page) -> list[str]:
    """打开新增产品表单并读取产品分类下拉选项，随后取消表单。"""
    page.get_by_role("button", name="新增").first.click()
    dialog = page.locator(".el-dialog:visible, .el-drawer:visible").first
    dialog.wait_for(state="visible", timeout=10_000)
    page.wait_for_timeout(800)
    dialog.locator(".el-select").first.click()
    page.wait_for_timeout(1200)
    options = page.locator(".el-select-dropdown:visible .el-select-dropdown__item")
    values = [options.nth(index).inner_text().strip() for index in range(options.count())]
    page.keyboard.press("Escape")
    page.wait_for_timeout(500)
    cancel_product_dialog(page, dialog)
    return values


def cancel_product_dialog(page: Page, dialog: Locator) -> None:
    """关闭新增产品表单，不产生任何业务写入。"""
    dialog.locator("button").filter(has_text=re.compile(r"取\s*消")).first.click()
    page.wait_for_timeout(1000)

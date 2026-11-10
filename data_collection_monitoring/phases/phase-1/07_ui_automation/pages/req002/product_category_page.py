"""产品分类页面对象，封装运行时已验证的稳定定位器与业务动作。"""

from __future__ import annotations

import re

from playwright.sync_api import Locator, Page

PAGE_PATH = "/biopark-iot/iot/device/product-category"
ROW_SELECTOR = ".el-table__body-wrapper table tbody tr"
HEADER_SELECTOR = ".el-table__header-wrapper th"
FILTER_INPUT_SELECTOR = "input[placeholder='请输入分类名字']"
PAGINATION_SELECTOR = ".el-pagination"
HEADER_SETTING_PANEL_SELECTOR = ".el-dropdown__popper"
DATA_PREFIX = "AUTO测试_勿用_"
EXPECTED_HEADERS = ["编号", "名称", "描述", "状态", "创建时间", "操作"]

_SUBMIT_PATTERN = re.compile(r"确\s*定")
_CANCEL_PATTERN = re.compile(r"取\s*消")


def open_page(page: Page, settings) -> None:
    """打开产品分类页面并等待列表渲染完成。"""
    page.goto(f"{settings.portal_url}{PAGE_PATH}", wait_until="domcontentloaded", timeout=30_000)
    wait_loaded(page)
    page.locator(".el-table, .el-empty, .el-table__body-wrapper").first.wait_for(state="visible", timeout=15_000)


def wait_loaded(page: Page, timeout: int = 15_000) -> None:
    """等待页面加载遮罩消失并留出渲染时间。"""
    try:
        page.wait_for_function("() => !document.querySelector('.el-loading-mask')", timeout=timeout)
    except Exception:  # noqa: BLE001
        pass
    page.wait_for_timeout(800)


def rows(page: Page) -> Locator:
    """返回列表数据行定位器。"""
    return page.locator(ROW_SELECTOR)


def headers(page: Page) -> list[str]:
    """返回列表表头文本。"""
    return [page.locator(HEADER_SELECTOR).nth(index).inner_text().strip() for index in range(page.locator(HEADER_SELECTOR).count())]


def empty_state(page: Page) -> Locator:
    """返回当前页面的空结果提示定位器。"""
    return page.get_by_text("暂无数据").first


def row_cells(row: Locator) -> list[str]:
    """返回单行六列文本。"""
    cells = row.locator("td")
    return [cells.nth(index).inner_text().strip().replace("\n", " / ") for index in range(min(cells.count(), 6))]


def row_values(page: Page) -> list[list[str]]:
    """返回当前页所有数据行的列文本。"""
    data = rows(page)
    return [row_cells(data.nth(index)) for index in range(data.count())]


def row_names(page: Page) -> list[str]:
    """返回当前页所有分类名称。"""
    return [value[1] for value in row_values(page)]


def name_filter(page: Page) -> Locator:
    """返回筛选区“分类名字”输入框。"""
    return page.locator(FILTER_INPUT_SELECTOR).first


def toolbar(page: Page, name: str) -> Locator:
    """返回工具区按钮定位器。"""
    return page.get_by_role("button", name=name).first


def query(page: Page, keyword: str) -> None:
    """在分类名字筛选框输入条件并点击查询。"""
    name_filter(page).fill(keyword)
    toolbar(page, "查询").click()
    wait_loaded(page)


def reset(page: Page) -> None:
    """点击重置并等待列表恢复。"""
    toolbar(page, "重置").click()
    wait_loaded(page)


def refresh(page: Page) -> None:
    """点击刷新并等待列表重新加载。"""
    toolbar(page, "刷新").click()
    wait_loaded(page)


def pagination_text(page: Page) -> str:
    """返回分页区域文本。"""
    return page.locator(PAGINATION_SELECTOR).first.inner_text().replace("\n", " ")


def active_page(page: Page) -> str:
    """返回当前激活页码文本。"""
    return page.locator(".el-pager li.is-active").first.inner_text().strip()


def total_count(page: Page) -> int:
    """返回分页总数文本中的记录条数。"""
    text = pagination_text(page)
    match = re.search(r"共\s*(\d+)\s*条", text)
    return int(match.group(1)) if match else -1


def click_prev(page: Page) -> None:
    """点击上一页按钮。"""
    page.locator(".btn-prev").first.click()
    wait_loaded(page)


def click_next(page: Page) -> None:
    """点击下一页按钮。"""
    page.locator(".btn-next").first.click()
    wait_loaded(page)


def prev_disabled(page: Page) -> bool:
    """返回上一页按钮是否不可用。"""
    button = page.locator(".btn-prev").first
    return button.is_disabled() or button.get_attribute("aria-disabled") == "true"


def jump_to_page(page: Page, number: int) -> None:
    """在页码输入框填写目标页码并回车提交。"""
    jump = page.locator(".el-pagination__jump input").first
    jump.fill(str(number))
    jump.press("Enter")
    wait_loaded(page)


def header_setting_panel(page: Page) -> Locator:
    """返回当前可见的表头设置面板定位器。"""
    return page.locator(f"{HEADER_SETTING_PANEL_SELECTOR}:visible").filter(has_text="编号").first


def open_add_dialog(page: Page) -> Locator:
    """点击新增并返回新增弹窗定位器。"""
    toolbar(page, "新增").click()
    dialog = page.locator(".el-dialog:visible").first
    dialog.wait_for(state="visible", timeout=10_000)
    page.wait_for_timeout(600)
    return dialog


def open_edit_dialog(page: Page, name: str) -> Locator:
    """按分类名称打开编辑弹窗。"""
    row = find_row(page, name)
    row.locator("button", has_text="编辑").first.click()
    dialog = page.locator(".el-dialog:visible").first
    dialog.wait_for(state="visible", timeout=10_000)
    page.wait_for_timeout(600)
    return dialog


def dialog_field(dialog: Locator, placeholder: str) -> Locator:
    """返回弹窗中指定 placeholder 的输入框。"""
    return dialog.locator(f"input[placeholder='{placeholder}'], textarea[placeholder='{placeholder}']").first


def dialog_status_radio(dialog: Locator, label: str) -> Locator:
    """返回弹窗中指定状态单选框。"""
    return dialog.locator(".el-radio", has_text=label).first


def checked_status(dialog: Locator) -> str:
    """返回弹窗中当前选中的状态文本。"""
    checked = dialog.locator(".el-radio.is-checked").first
    return checked.inner_text().strip()


def submit_dialog(page: Page, dialog: Locator) -> None:
    """点击弹窗确定按钮并等待响应。"""
    dialog.locator("button").filter(has_text=_SUBMIT_PATTERN).first.click()
    page.wait_for_timeout(1800)


def cancel_dialog(page: Page, dialog: Locator) -> None:
    """点击弹窗取消按钮并等待关闭。"""
    dialog.locator("button").filter(has_text=_CANCEL_PATTERN).first.click()
    page.wait_for_timeout(1000)


def dialog_error_texts(page: Page) -> list[str]:
    """返回当前可见的表单校验错误文本。"""
    errors = page.locator(".el-form-item__error:visible")
    return [errors.nth(index).inner_text().strip() for index in range(errors.count())]


def toasts(page: Page) -> list[str]:
    """返回当前可见的轻提示文本。"""
    messages = page.locator(".el-message:visible")
    return [messages.nth(index).inner_text().strip().replace("\n", " ") for index in range(messages.count())]


def message_box(page: Page) -> Locator:
    """返回删除确认弹层定位器。"""
    return page.locator(".el-message-box:visible").first


def confirm_message_box(page: Page) -> None:
    """在删除确认层点击确定并等待响应。"""
    page.locator(".el-message-box:visible button").filter(has_text=_SUBMIT_PATTERN).first.click()
    page.wait_for_timeout(1800)


def cancel_message_box(page: Page) -> None:
    """在删除确认层点击取消并等待关闭。"""
    page.locator(".el-message-box:visible button").filter(has_text=_CANCEL_PATTERN).first.click()
    page.wait_for_timeout(1000)


def find_row(page: Page, name: str) -> Locator:
    """按分类名称查找列表行。"""
    data = rows(page)
    for index in range(data.count()):
        if data.nth(index).locator("td").nth(1).inner_text().strip() == name:
            return data.nth(index)
    raise AssertionError(f"列表中未找到分类：{name}")


def create_category(page: Page, name: str, sort: str, description: str, status: str = "开启") -> str:
    """新增一条产品分类，返回提交后的提示文本。"""
    dialog = open_add_dialog(page)
    dialog_field(dialog, "请输入分类名字").fill(name)
    dialog_field(dialog, "请输入分类排序").fill(sort)
    dialog_field(dialog, "请输入分类描述").fill(description)
    dialog_status_radio(dialog, status).click()
    submit_dialog(page, dialog)
    if page.locator(".el-dialog:visible").count():
        raise RuntimeError(f"新增表单未关闭，校验错误：{dialog_error_texts(page)}")
    return " / ".join(toasts(page))


def edit_category(page: Page, name: str, new_name: str | None = None, sort: str | None = None, description: str | None = None, status: str | None = None) -> str:
    """编辑指定分类的字段，返回提交后的提示文本。"""
    dialog = open_edit_dialog(page, name)
    if new_name is not None:
        dialog_field(dialog, "请输入分类名字").fill(new_name)
    if sort is not None:
        dialog_field(dialog, "请输入分类排序").fill(sort)
    if description is not None:
        dialog_field(dialog, "请输入分类描述").fill(description)
    if status is not None:
        dialog_status_radio(dialog, status).click()
    submit_dialog(page, dialog)
    if page.locator(".el-dialog:visible").count():
        raise RuntimeError(f"编辑表单未关闭，校验错误：{dialog_error_texts(page)}")
    return " / ".join(toasts(page))


def delete_category(page: Page, name: str) -> str:
    """删除指定分类，返回提交后的提示文本。"""
    row = find_row(page, name)
    return delete_row(page, row)


def delete_row(page: Page, row: Locator) -> str:
    """删除指定列表行，返回提交后的提示文本。"""
    row.locator("button", has_text="删除").first.click()
    message_box(page).wait_for(state="visible", timeout=10_000)
    page.wait_for_timeout(600)
    confirm_message_box(page)
    return " / ".join(toasts(page))


def find_row_by_id(page: Page, category_id: str) -> Locator:
    """按唯一编号跨页查找列表行。"""
    for _ in range(10):
        data = rows(page)
        for index in range(data.count()):
            if data.nth(index).locator("td").first.inner_text().strip() == str(category_id):
                return data.nth(index)
        next_button = page.locator(".btn-next").first
        if next_button.is_disabled() or next_button.get_attribute("aria-disabled") == "true":
            break
        next_button.click()
        wait_loaded(page)
    raise LookupError(f"列表中未找到编号 {category_id} 的分类")


def delete_category_by_id(page: Page, category_id: str) -> str:
    """按唯一编号删除分类，返回提交后的提示文本。"""
    return delete_row(page, find_row_by_id(page, category_id))


def cleanup_prefix(page: Page, prefix: str) -> list[str]:
    """按前缀查询并删除本用例创建的分类，返回已清理名称。"""
    cleaned: list[str] = []
    for _ in range(20):
        query(page, prefix)
        data = rows(page)
        if data.count() == 0:
            break
        target = data.first.locator("td").nth(1).inner_text().strip()
        delete_category(page, target)
        cleaned.append(target)
    reset(page)
    return cleaned


def switch_tenant(page: Page, tenant: str) -> None:
    """展开顶部租户下拉并切换到目标租户，等待列表刷新。"""
    page.locator("span").filter(has_text=re.compile(r"^测试园区\w$")).first.click()
    page.wait_for_timeout(800)
    page.locator(".el-dropdown-menu__item", has_text=tenant).first.click()
    page.wait_for_timeout(2500)
    wait_loaded(page)


def current_tenant(page: Page) -> str:
    """返回顶部当前租户名称。"""
    return page.locator("span").filter(has_text=re.compile(r"^测试园区\w$")).first.inner_text().strip()

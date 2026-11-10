"""REQ-003 产品管理页面对象，封装运行时验证过的定位器与业务动作。"""

from __future__ import annotations

import re
import time

from playwright.sync_api import Locator, Page

PAGE_PATH = "/biopark-iot/iot/device/product"
ROW_SELECTOR = ".el-table__body-wrapper table tbody tr"
HEADER_SELECTOR = ".el-table__header-wrapper th"
EXPECTED_HEADERS = [
    "ProductKey",
    "产品名称",
    "产品分类",
    "设备类型",
    "产品图标",
    "产品图片",
    "状态",
    "创建时间",
    "操作",
]
NAME_FIELD = "input[placeholder='请输入产品名称']"
KEY_FIELD = "input[placeholder='请输入产品标识']"
DIALOG = ".el-dialog:visible"
PUBLISHED = "已发布"
UNPUBLISHED = "未发布"


def wait_loaded(page: Page, settle_ms: int = 900) -> None:
    """等待列表加载遮罩消失并留出渲染缓冲。"""
    mask = page.locator(".el-loading-mask")
    try:
        mask.first.wait_for(state="hidden", timeout=15_000)
    except Exception:  # noqa: BLE001
        pass
    page.wait_for_timeout(settle_ms)


def open_page(page: Page, settings) -> None:
    """打开产品管理页面并等待列表或空状态渲染完成。"""
    page.goto(f"{settings.portal_url}{PAGE_PATH}", wait_until="domcontentloaded", timeout=30_000)
    wait_loaded(page, 1500)
    page.locator(f"{ROW_SELECTOR}, .el-table__empty-text").first.wait_for(state="visible", timeout=20_000)


def toolbar(page: Page, label: str) -> Locator:
    """返回筛选/工具区按钮。"""
    return page.get_by_role("button", name=label, exact=True).first


def headers(page: Page) -> list[str]:
    """返回当前表头文本列表。"""
    items = page.locator(HEADER_SELECTOR)
    return [items.nth(index).inner_text().strip() for index in range(items.count())]


def rows(page: Page) -> Locator:
    """返回当前页数据行。"""
    return page.locator(ROW_SELECTOR)


def row_cells(row: Locator) -> list[str]:
    """返回单行列文本（换行折叠为斜杠）。"""
    cells = row.locator("td")
    return [cells.nth(index).inner_text().strip().replace("\n", " / ") for index in range(cells.count())]


def row_values(page: Page) -> list[list[str]]:
    """返回当前页全部数据行的列文本。"""
    data = rows(page)
    return [row_cells(data.nth(index)) for index in range(data.count())]


def row_names(page: Page) -> list[str]:
    """返回当前页产品名称。"""
    return [value[1] for value in row_values(page) if len(value) > 1]


def total_text(page: Page) -> str:
    """返回分页总数文本。"""
    total = page.locator(".el-pagination__total")
    return total.first.inner_text().strip() if total.count() else ""


def total_count(page: Page) -> int:
    """返回分页总数数值，无法解析时返回 -1。"""
    text = total_text(page)
    digits = re.sub(r"\D", "", text)
    return int(digits) if digits else -1


def empty_text(page: Page) -> str:
    """返回空数据占位文本。"""
    items = page.locator(".el-table__empty-text")
    return items.first.inner_text().strip() if items.count() else ""


def name_filter(page: Page) -> Locator:
    """返回产品名称筛选框。"""
    return page.locator(NAME_FIELD).first


def key_filter(page: Page) -> Locator:
    """返回 ProductKey 筛选框。"""
    return page.locator(KEY_FIELD).first


def query(page: Page, name: str = "", key: str = "") -> None:
    """按产品名称/ProductKey 条件执行查询。"""
    name_filter(page).fill(name)
    key_filter(page).fill(key)
    toolbar(page, "查询").click()
    wait_loaded(page)


def reset(page: Page) -> None:
    """重置筛选条件并恢复默认列表。"""
    toolbar(page, "重置").click()
    wait_loaded(page)


def refresh(page: Page) -> None:
    """点击刷新并等待列表重新加载。"""
    toolbar(page, "刷新").click()
    wait_loaded(page, 1500)


def toasts(page: Page) -> list[str]:
    """返回当前可见提示文本。"""
    items = page.locator(".el-message")
    return [items.nth(index).inner_text().strip() for index in range(items.count())]


def collect_toasts(page: Page, duration: float = 4.0) -> list[str]:
    """在时间窗内收集出现过的提示文本。"""
    seen: list[str] = []
    deadline = time.monotonic() + duration
    while time.monotonic() < deadline:
        try:
            items = page.locator(".el-message")
            for index in range(items.count()):
                text = items.nth(index).inner_text(timeout=1000).strip()
                if text and text not in seen:
                    seen.append(text)
        except Exception:  # noqa: BLE001
            pass
        page.wait_for_timeout(150)
    return seen


def message_box(page: Page) -> Locator:
    """返回当前可见消息框。"""
    return page.locator(".el-message-box:visible").first


def message_box_text(page: Page) -> str:
    """返回消息框文本。"""
    box = message_box(page)
    return box.inner_text().strip().replace("\n", " / ") if box.count() else ""


def confirm_message_box(page: Page) -> None:
    """确认消息框。"""
    box = message_box(page)
    box.locator("button").filter(has_text="确定").first.click()
    page.wait_for_timeout(2500)


def cancel_message_box(page: Page) -> None:
    """取消消息框。"""
    box = message_box(page)
    box.locator("button").filter(has_text="取消").first.click()
    page.wait_for_timeout(1200)


def active_page(page: Page) -> str:
    """返回当前激活页码。"""
    items = page.locator(".el-pager li.is-active")
    return items.first.inner_text().strip() if items.count() else ""


def prev_disabled(page: Page) -> bool:
    """返回上一页控件是否不可用。"""
    return page.locator(".btn-prev").first.is_disabled()


def click_next(page: Page) -> None:
    """点击下一页。"""
    page.locator(".btn-next").first.click()
    wait_loaded(page)


def set_page_size(page: Page, label: str) -> None:
    """选择每页条数。"""
    page.locator(".el-pagination .el-select").first.click()
    page.wait_for_timeout(1000)
    page.locator(".el-select-dropdown:visible .el-select-dropdown__item").filter(has_text=label).first.click()
    wait_loaded(page, 1500)


def jump_to_page(page: Page, number: int) -> None:
    """在跳页输入框输入页码并回车。"""
    field = page.locator(".el-pagination__jump input").first
    field.fill(str(number))
    field.press("Enter")
    wait_loaded(page, 1500)


def find_row(page: Page, name: str) -> Locator:
    """按产品名称定位列表行。"""
    data = rows(page)
    for index in range(data.count()):
        if row_cells(data.nth(index))[1] == name:
            return data.nth(index)
    raise LookupError(f"产品列表未找到名称：{name}")


def row_buttons(row: Locator) -> list[str]:
    """返回行内操作按钮文本。"""
    items = row.locator("button")
    return [items.nth(index).inner_text().strip() for index in range(items.count())]


def row_action(row: Locator, label: str) -> None:
    """点击行内操作按钮。"""
    row.locator("button", has_text=label).first.click()


def dialog(page: Page) -> Locator:
    """返回当前可见新增/编辑弹窗。"""
    return page.locator(DIALOG).first


def dialog_field(scope: Locator, placeholder: str) -> Locator:
    """返回弹窗内指定占位符输入框。"""
    return scope.locator(f"input[placeholder='{placeholder}']").first


def dialog_error_texts(page: Page) -> list[str]:
    """返回弹窗内校验错误文本。"""
    items = page.locator(f"{DIALOG} .el-form-item__error")
    return [items.nth(index).inner_text().strip() for index in range(items.count())]


def dialog_button(page: Page, label_pattern: str) -> Locator:
    """返回弹窗内按钮（兼容带空格文本）。"""
    scope = dialog(page)
    return scope.locator("button").filter(has_text=re.compile(label_pattern)).last


def submit_dialog(page: Page) -> None:
    """点击弹窗确定按钮。"""
    dialog_button(page, r"确\s*定").click()
    page.wait_for_timeout(1500)


def cancel_dialog(page: Page) -> None:
    """点击弹窗取消按钮。"""
    dialog_button(page, r"取\s*消").click()
    page.wait_for_timeout(1200)


def choose_category(page: Page, category: str) -> None:
    """在弹窗中选择产品分类。"""
    scope = dialog(page)
    scope.locator(".el-select").first.click()
    page.wait_for_timeout(1000)
    page.locator(".el-select-dropdown:visible .el-select-dropdown__item").filter(has_text=category).first.click()
    page.wait_for_timeout(600)


def choose_network(page: Page, network: str) -> None:
    """在弹窗中选择联网方式。"""
    scope = dialog(page)
    item = scope.locator(".el-form-item").filter(has_text="联网方式").first
    item.locator(".el-select").first.click()
    page.wait_for_timeout(1000)
    page.locator(".el-select-dropdown:visible .el-select-dropdown__item").filter(has_text=network).first.click()
    page.wait_for_timeout(600)


def choose_radio(page: Page, label: str) -> None:
    """在弹窗中选择单选项。"""
    dialog(page).locator(".el-radio").filter(has_text=label).first.click()
    page.wait_for_timeout(500)


def fill_required_fields(page: Page, name: str, category: str, description: str | None = None) -> str:
    """填写新增产品必填字段并返回自动生成的 ProductKey。"""
    scope = dialog(page)
    product_key = dialog_field(scope, "请输入 ProductKey").input_value().strip()
    dialog_field(scope, "请输入产品名称").fill(name)
    choose_category(page, category)
    choose_radio(page, "直连设备")
    choose_network(page, "Wi-Fi")
    choose_radio(page, "IP 定位")
    if description is not None:
        if not scope.locator(".el-form-item").filter(has_text="产品描述").first.is_visible():
            scope.get_by_text("更多配置").first.click()
            page.wait_for_timeout(1200)
        scope.locator("textarea").first.fill(description)
    return product_key


def create_product(page: Page, name: str, category: str, description: str | None = None) -> tuple[str, str]:
    """新增产品并返回（自动 ProductKey, 提示文本）。"""
    toolbar(page, "新增").click()
    page.wait_for_timeout(2000)
    product_key = fill_required_fields(page, name, category, description)
    submit_dialog(page)
    messages = collect_toasts(page, 4.0)
    return product_key, " / ".join(messages)


def open_edit(page: Page, name: str) -> None:
    """打开指定产品的编辑弹窗。"""
    row_action(find_row(page, name), "编辑")
    page.wait_for_timeout(2200)


def edit_product(page: Page, name: str, new_name: str | None = None, description: str | None = None) -> str:
    """编辑产品名称/描述并返回提示文本。"""
    open_edit(page, name)
    scope = dialog(page)
    if new_name is not None:
        dialog_field(scope, "请输入产品名称").fill(new_name)
    if description is not None:
        if not scope.locator(".el-form-item").filter(has_text="产品描述").first.is_visible():
            scope.get_by_text("更多配置").first.click()
            page.wait_for_timeout(1200)
        scope.locator("textarea").first.fill(description)
    submit_dialog(page)
    return " / ".join(collect_toasts(page, 4.0))


def delete_product(page: Page, name: str) -> str:
    """删除指定产品并返回（确认层文本 / 提示文本）。"""
    row_action(find_row(page, name), "删除")
    page.wait_for_timeout(1200)
    box_text = message_box_text(page)
    confirm_message_box(page)
    messages = collect_toasts(page, 4.0)
    return f"{box_text} => {' / '.join(messages)}"


def open_model_dialog(page: Page, name: str) -> Locator:
    """打开指定产品的物模型弹窗。"""
    row_action(find_row(page, name), "物模型")
    page.wait_for_timeout(2500)
    return page.locator(".el-dialog:visible").last


def model_buttons(page: Page) -> list[str]:
    """返回物模型弹窗按钮文本。"""
    scope = page.locator(".el-dialog:visible").last
    items = scope.locator("button")
    return [items.nth(index).inner_text().strip() for index in range(items.count())]


def close_model_dialog(page: Page) -> None:
    """关闭物模型弹窗。"""
    page.keyboard.press("Escape")
    page.wait_for_timeout(1200)


def publish_product(page: Page, name: str) -> str:
    """在物模型弹窗中发布。"""
    scope = open_model_dialog(page, name)
    scope.locator("button").filter(has_text="发布").first.click()
    messages = collect_toasts(page, 5.0)
    close_model_dialog(page)
    wait_loaded(page, 1200)
    return " / ".join(messages)


def revoke_product(page: Page, name: str) -> str:
    """在物模型弹窗中撤销发布。"""
    scope = open_model_dialog(page, name)
    scope.locator("button").filter(has_text="撤销发布").first.click()
    messages = collect_toasts(page, 5.0)
    close_model_dialog(page)
    wait_loaded(page, 1200)
    return " / ".join(messages)


def detail_text(page: Page, name: str) -> str:
    """打开查看弹窗并返回其文本。"""
    row_action(find_row(page, name), "查看")
    page.wait_for_timeout(2500)
    scope = page.locator(".el-dialog:visible").last
    text = scope.inner_text().strip().replace("\n", " / ")
    page.keyboard.press("Escape")
    page.wait_for_timeout(1000)
    return text


def more_config_state(page: Page) -> tuple[dict[str, bool], dict[str, bool]]:
    """读取更多配置展开前后的字段可见性。"""
    scope = dialog(page)

    def snapshot() -> dict[str, bool]:
        return {
            "产品描述": scope.locator(".el-form-item").filter(has_text="产品描述").first.is_visible(),
            "产品图标": scope.locator(".el-form-item").filter(has_text="产品图标").first.is_visible(),
            "产品图片": scope.locator(".el-form-item").filter(has_text="产品图片").first.is_visible(),
        }

    before = snapshot()
    scope.get_by_text("更多配置").first.click()
    page.wait_for_timeout(1500)
    after = snapshot()
    return before, after


def current_tenant(page: Page) -> str:
    """返回顶部当前租户名称。"""
    return page.locator("span").filter(has_text=re.compile(r"^测试园区\w$")).first.inner_text().strip()


def switch_tenant(page: Page, tenant: str) -> None:
    """切换顶部租户上下文。"""
    page.locator("span").filter(has_text=re.compile(r"^测试园区\w$")).first.click()
    page.wait_for_timeout(1200)
    page.locator(".el-dropdown-menu__item").filter(has_text=tenant).first.click()
    wait_loaded(page, 3000)


def preview_first_image(page: Page, row: Locator) -> str:
    """点击行内首张图片并在预览浮层中读取图片地址。"""
    row.locator("img").first.click()
    page.wait_for_timeout(1500)
    viewer = page.locator(".el-image-viewer__wrapper:visible")
    if not viewer.count():
        raise LookupError("未打开图片预览浮层")
    source = page.locator(".el-image-viewer__img").first.get_attribute("src")
    page.keyboard.press("Escape")
    page.wait_for_timeout(900)
    return str(source)

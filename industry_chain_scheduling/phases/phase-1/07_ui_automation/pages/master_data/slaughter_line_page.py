"""宰杀线管理页面对象：登录门户并导航至宰杀线管理页，封装查询/新增/编辑/启停/删除/批量等交互。

所有交互方法均假定 self.page 已处于宰杀线管理页（由 ensure_open 保证）。
"""

from __future__ import annotations

import re

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError

from config.settings import Settings
from pages.common.login_page import LoginPage


class SlaughterLinePage:
    """宰杀线管理业务页面对象，封装门户进入与全部 UI 交互。"""

    SUBMENU = "基础数据"
    MENU_ITEM = "宰杀线管理"
    ROUTE = "/biopark-apm/apm/bases/slaughter-line"
    EXPECTED_FILTERS = ["宰杀线编码", "宰杀线名称", "状态"]
    EXPECTED_HEADERS = ["", "宰杀线编码", "宰杀线名称", "单日产能(万只)", "排序", "状态", "备注",
                        "创建时间", "更新时间", "创建人", "更新人", "操作"]
    NEW_FORM_LABELS = ["宰杀线编码", "宰杀线名称", "单日产能(万只)", "排序", "状态", "备注"]

    def __init__(self, page: Page, settings: Settings) -> None:
        """初始化页面对象，绑定浏览器页面与运行配置。"""
        self.page = page
        self.settings = settings

    # ----- 导航 -----

    def open(self) -> Page:
        """登录门户并经由「基础数据 / 宰杀线管理」进入页面，返回应用页面对象。"""
        page = self.page
        page.goto(self.settings.portal_url, wait_until="domcontentloaded", timeout=20_000)
        try:
            page.wait_for_load_state("networkidle", timeout=15_000)
        except PlaywrightTimeoutError:
            pass
        LoginPage(page, self.settings).login_if_needed()
        page.wait_for_timeout(800)
        cards = page.locator("button.portal-home__card").filter(has_text="产业链生产排程系统")
        if not cards.count() or not cards.first.is_visible():
            raise RuntimeError("portal card for 产业链生产排程系统 was not found")
        try:
            with page.context.expect_page(timeout=10_000) as popup_info:
                cards.first.click()
            app = popup_info.value
        except PlaywrightTimeoutError:
            app = page
        app.set_default_timeout(12_000)
        try:
            app.wait_for_load_state("networkidle", timeout=20_000)
        except PlaywrightTimeoutError:
            pass
        app.wait_for_timeout(800)

        items = app.locator("li.el-menu-item")

        def _find_item() -> object | None:
            for j in range(items.count()):
                it = items.nth(j)
                if it.is_visible() and it.inner_text().strip() == self.MENU_ITEM:
                    return it
            return None

        if _find_item() is None:
            subs = app.locator("li.el-sub-menu")
            target_sub = None
            for i in range(subs.count()):
                if self.SUBMENU in subs.nth(i).inner_text():
                    target_sub = subs.nth(i)
                    break
            if target_sub is None:
                raise RuntimeError(f"{self.SUBMENU} submenu was not found")
            target_sub.click()
            app.wait_for_timeout(400)
        item = _find_item()
        if item is None:
            raise RuntimeError(f"{self.MENU_ITEM} menu item was not found")
        item.click()
        try:
            app.wait_for_url("**/bases/slaughter-line", timeout=20_000)
        except PlaywrightTimeoutError as exc:
            raise RuntimeError("slaughter line route did not become ready") from exc
        try:
            app.wait_for_load_state("networkidle", timeout=15_000)
        except PlaywrightTimeoutError:
            pass
        app.wait_for_timeout(800)
        self.page = app
        return app

    def ensure_open(self) -> Page:
        """若当前页面非宰杀线管理路由则导航进入，否则直接返回当前页面。"""
        if "slaughter-line" in self.page.url:
            return self.page
        return self.open()

    def reload(self) -> Page:
        """重新加载宰杀线管理页以复位查询/弹窗状态，返回应用页面。"""
        current_url = self.page.url
        # 若当前已在应用路由（URL 含 slaughter-line 且不含 portal 路径），直接刷新；否则重走门户进入流程。
        if "slaughter-line" in current_url and "portal" not in current_url.lower():
            self.page.reload(wait_until="domcontentloaded", timeout=20_000)
        else:
            return self.open()
        try:
            self.page.wait_for_load_state("networkidle", timeout=15_000)
        except PlaywrightTimeoutError:
            pass
        self.page.wait_for_timeout(600)
        return self.page

    # ----- 查询区 -----

    def get_query_filter_labels(self) -> list[str]:
        """读取查询区所有表单字段标签文本，返回去空白后的标签列表。"""
        labels = self.page.locator(".el-form-item__label")
        return [labels.nth(k).inner_text().strip() for k in range(labels.count())]

    def assert_filters_present(self, expected: list[str] | None = None) -> list[str]:
        """断言查询区包含预期筛选项，缺失时抛出 AssertionError 并返回实际标签。"""
        expected = expected or self.EXPECTED_FILTERS
        labels = self.get_query_filter_labels()
        missing = [name for name in expected if name not in labels]
        if missing:
            raise AssertionError(f"查询区缺少筛选字段 {missing}；实际标签：{labels}")
        return labels

    def get_status_options(self) -> list[str]:
        """打开状态下拉并读取其选项文本，读取后关闭下拉。"""
        sel = self.page.locator(".el-form-item").filter(has_text="状态").locator(".el-select")
        if not sel.count():
            return []
        sel.first.click()
        self.page.wait_for_timeout(400)
        opts = [o.inner_text().strip() for o in self.page.locator(".el-select-dropdown__item:visible").all()]
        self.page.keyboard.press("Escape")
        self.page.wait_for_timeout(300)
        return opts

    def fill_query(self, *, code: str | None = None, name: str | None = None, status: str | None = None) -> None:
        """按字段填充查询区；为 None 的字段不填。"""
        if code is not None:
            self._fill_form_input("宰杀线编码", code)
        if name is not None:
            self._fill_form_input("宰杀线名称", name)
        if status is not None:
            self._select_form_option("状态", status)

    def click_query(self) -> None:
        """点击查询按钮触发列表刷新。"""
        self.page.locator("button").filter(has_text=re.compile(r"查\s*询")).first.click()
        self.page.wait_for_timeout(600)

    def click_reset(self) -> None:
        """点击重置按钮清空查询条件并刷新列表。"""
        self.page.locator("button").filter(has_text=re.compile(r"重\s*置")).first.click()
        self.page.wait_for_timeout(600)

    def _fill_form_input(self, label: str, value: str) -> None:
        """在含指定标签的表单项中填写文本输入框。"""
        item = self.page.locator(".el-form-item").filter(has_text=label).first
        inp = item.locator(".el-input__inner, textarea").first
        inp.fill(value)

    def _select_form_option(self, label: str, option: str) -> None:
        """在含指定标签的表单项的下拉中选择指定选项。"""
        item = self.page.locator(".el-form-item").filter(has_text=label).first
        item.locator(".el-select").first.click()
        self.page.wait_for_timeout(300)
        self.page.locator(".el-select-dropdown__item:visible").filter(has_text=option).first.click()
        self.page.wait_for_timeout(300)

    # ----- 表格 -----

    def get_header_texts(self) -> list[str]:
        """读取表格表头文本列表。"""
        return [th.inner_text().strip() for th in self.page.locator(".el-table__header-wrapper th").all()]

    def assert_headers_order(self, expected: list[str] | None = None) -> list[str]:
        """断言表头顺序与预期一致，不一致时抛出 AssertionError。"""
        expected = expected or self.EXPECTED_HEADERS
        headers = self.get_header_texts()
        if headers != expected:
            raise AssertionError(f"表头顺序不符；期望 {expected}；实际 {headers}")
        return headers

    def get_row_count(self) -> int:
        """返回当前列表数据行数量。"""
        return self.page.locator(".el-table__body-wrapper tr.el-table__row").count()

    def get_row_texts(self, index: int = 0) -> list[str]:
        """读取指定数据行的单元格文本列表。"""
        row = self.page.locator(".el-table__body-wrapper tr.el-table__row").nth(index)
        return [c.inner_text().strip() for c in row.locator("td").all()]

    def get_row_status(self, index: int = 0) -> str:
        """读取指定数据行的状态列文本。"""
        cells = self.get_row_texts(index)
        return cells[5] if len(cells) > 5 else ""

    def get_row_name(self, index: int = 0) -> str:
        """读取指定数据行的宰杀线名称列文本。"""
        cells = self.get_row_texts(index)
        return cells[2] if len(cells) > 2 else ""

    def find_row_index_by_name(self, name: str) -> int:
        """在列表中查找名称匹配的行的索引，未找到时抛 AssertionError。"""
        rows = self.page.locator(".el-table__body-wrapper tr.el-table__row")
        for i in range(rows.count()):
            cells = [c.inner_text().strip() for c in rows.nth(i).locator("td").all()]
            if len(cells) > 2 and cells[2] == name:
                return i
        raise AssertionError(f"列表中未找到名称为 {name} 的行")

    def get_row_actions(self, index: int = 0) -> list[str]:
        """读取指定数据行操作列的按钮文本列表。"""
        row = self.page.locator(".el-table__body-wrapper tr.el-table__row").nth(index)
        return [b.inner_text().strip() for b in row.locator("td .el-button").all()]

    def get_empty_text(self) -> str:
        """读取空状态文本；无空状态时返回空字符串。"""
        loc = self.page.locator(".el-table__empty-text")
        return loc.inner_text().strip() if loc.count() else ""

    def get_pagination_text(self) -> str:
        """读取分页栏文本。"""
        loc = self.page.locator(".el-pagination")
        return loc.inner_text().strip() if loc.count() else ""

    # ----- 新增弹窗 -----

    def open_new_dialog(self) -> None:
        """点击新增按钮并等待新增弹窗出现。"""
        self.page.locator("button").filter(has_text=re.compile(r"新\s*增")).first.click()
        self.page.wait_for_selector(".el-dialog:visible", timeout=6000)
        self.page.wait_for_timeout(400)

    def close_dialog(self) -> None:
        """关闭当前可见弹窗（优先取消/关闭按钮，回退 Esc）。"""
        dlg = self.page.locator(".el-dialog:visible").first
        for sel in [dlg.locator("button").filter(has_text=re.compile(r"取\s*消")),
                    dlg.locator("button").filter(has_text=re.compile(r"关\s*闭")),
                    dlg.locator(".el-dialog__headerbtn"),
                    dlg.locator(".el-dialog__close")]:
            if sel.count() and sel.first.is_visible():
                sel.first.click()
                self.page.wait_for_timeout(400)
                return
        self.page.keyboard.press("Escape")
        self.page.wait_for_timeout(400)

    def get_new_dialog_labels(self) -> list[str]:
        """读取新增弹窗表单字段标签列表。"""
        dlg = self.page.locator(".el-dialog:visible").first
        return [li.inner_text().strip() for li in dlg.locator(".el-form-item__label").all()]

    def get_new_code_value(self) -> str:
        """读取新增弹窗宰杀线编码输入框的当前值。"""
        return self._dialog_input_value("请输入宰杀线编码")

    def is_new_code_readonly(self) -> bool:
        """返回新增弹窗宰杀线编码输入框是否只读/禁用。"""
        inp = self.page.locator(".el-dialog:visible").first.locator(".el-input__inner").first
        return inp.get_attribute("readonly") is not None or inp.is_disabled()

    def fill_new_form(self, *, name: str, capacity: str | None = None, sort: str | None = None,
                      status: str | None = None) -> None:
        """填写新增弹窗表单（编码由系统预填，不填）。"""
        self._fill_dialog_input("请输入宰杀线名称", name)
        if capacity is not None:
            self._fill_dialog_input_by_label("单日产能(万只)", capacity)
        if sort is not None:
            self._fill_dialog_input_by_label("排序", sort)
        if status is not None:
            self._select_dialog_option("状态", status)

    def submit_dialog(self) -> None:
        """点击弹窗中的确定按钮提交。"""
        self.page.locator(".el-dialog:visible").first.locator("button").filter(has_text=re.compile(r"确\s*定")).first.click()
        self.page.wait_for_timeout(700)

    def cancel_dialog(self) -> None:
        """点击弹窗中的取消按钮关闭。"""
        self.page.locator(".el-dialog:visible").first.locator("button").filter(has_text=re.compile(r"取\s*消")).first.click()
        self.page.wait_for_timeout(500)

    def _fill_dialog_input(self, placeholder: str, value: str) -> None:
        """在弹窗中按 placeholder 填写输入框。"""
        inp = self.page.locator(".el-dialog:visible").first.locator(f".el-input__inner[placeholder='{placeholder}'], "
                                                                  f"textarea[placeholder='{placeholder}']").first
        inp.fill(value)

    def _fill_dialog_input_by_label(self, label: str, value: str) -> None:
        """在弹窗中按表单项标签填写文本框。"""
        item = self.page.locator(".el-dialog:visible").first.locator(".el-form-item").filter(has_text=label).first
        item.locator(".el-input__inner, textarea").first.fill(value)

    def _dialog_input_value(self, placeholder: str) -> str:
        """读取弹窗中按 placeholder 定位的输入框值。"""
        inp = self.page.locator(".el-dialog:visible").first.locator(f".el-input__inner[placeholder='{placeholder}'], "
                                                                  f"textarea[placeholder='{placeholder}']").first
        return inp.input_value()

    def _select_dialog_option(self, label: str, option: str) -> None:
        """在弹窗中按表单项标签选择下拉选项。"""
        item = self.page.locator(".el-dialog:visible").first.locator(".el-form-item").filter(has_text=label).first
        item.locator(".el-select").first.click()
        self.page.wait_for_timeout(300)
        self.page.locator(".el-select-dropdown__item:visible").filter(has_text=option).first.click()
        self.page.wait_for_timeout(300)

    # ----- 编辑弹窗 -----

    def open_edit_dialog(self, index: int = 0) -> None:
        """点击指定行的编辑按钮并等待编辑弹窗出现。"""
        row = self.page.locator(".el-table__body-wrapper tr.el-table__row").nth(index)
        row.locator("td .el-button").filter(has_text=re.compile(r"编\s*辑")).first.click()
        self.page.wait_for_selector(".el-dialog:visible", timeout=6000)
        self.page.wait_for_timeout(400)

    def is_edit_code_readonly(self) -> bool:
        """返回编辑弹窗宰杀线编码输入框是否 disabled（只读）。"""
        inp = self.page.locator(".el-dialog:visible").first.locator(".el-input__inner").first
        return inp.is_disabled()

    def get_edit_dialog_values(self) -> dict[str, str]:
        """读取编辑弹窗各字段当前值，按键名返回。"""
        dlg = self.page.locator(".el-dialog:visible").first
        labels = [li.inner_text().strip() for li in dlg.locator(".el-form-item__label").all()]
        values = []
        for inp in dlg.locator(".el-input__inner, textarea").all():
            values.append(inp.input_value())
        return dict(zip(labels, values))

    def edit_fill(self, *, name: str | None = None, capacity: str | None = None, sort: str | None = None) -> None:
        """在编辑弹窗中修改可编辑字段。"""
        if name is not None:
            self._fill_dialog_input_by_label("宰杀线名称", name)
        if capacity is not None:
            self._fill_dialog_input_by_label("单日产能(万只)", capacity)
        if sort is not None:
            self._fill_dialog_input_by_label("排序", sort)

    # ----- 启停 / 删除 / 批量 -----

    def select_row(self, index: int = 0) -> None:
        """勾选指定数据行的复选框。"""
        row = self.page.locator(".el-table__body-wrapper tr.el-table__row").nth(index)
        row.locator(".el-checkbox").first.click()
        self.page.wait_for_timeout(300)

    def is_batch_button_disabled(self, name: str) -> bool:
        """返回工具栏批量按钮（删除/启用/停用）在未选/已选时的禁用状态。"""
        btn = self.page.locator("button").filter(has_text=name).first
        return btn.is_disabled()

    def click_batch(self, name: str) -> None:
        """点击工具栏批量按钮（删除/启用/停用）。"""
        self.page.locator("button").filter(has_text=name).first.click()
        self.page.wait_for_timeout(500)

    def click_row_action(self, index: int, action: str) -> None:
        """点击指定数据行操作列的按钮（编辑/停用/删除）。"""
        row = self.page.locator(".el-table__body-wrapper tr.el-table__row").nth(index)
        row.locator("td .el-button").filter(has_text=action).first.click()
        self.page.wait_for_timeout(500)

    def get_confirm_text(self) -> str:
        """读取当前确认框（MessageBox）的正文文本。"""
        loc = self.page.locator(".el-message-box__message")
        return loc.inner_text().strip() if loc.count() else ""

    def confirm_ok(self) -> None:
        """点击确认框的确定按钮。"""
        self.page.locator(".el-message-box__btns button").filter(has_text=re.compile(r"确\s*定")).first.click()
        self.page.wait_for_timeout(700)

    def confirm_cancel(self) -> None:
        """点击确认框的取消按钮。"""
        self.page.locator(".el-message-box__btns button").filter(has_text=re.compile(r"取\s*消")).first.click()
        self.page.wait_for_timeout(500)

    # ----- 反馈 -----

    def get_toast_text(self) -> str:
        """读取页面顶部消息（el-message）文本，无则空字符串。"""
        loc = self.page.locator(".el-message, .el-notification")
        return loc.inner_text().strip() if loc.count() else ""

"""目标制定页面对象：只提供真实页面的导航、定位、读取和证据截图能力。"""

from __future__ import annotations

from pathlib import Path

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError

from config.settings import Settings
from pages.common.portal_navigation import PortalNavigation


class TargetGoalReadinessError(RuntimeError):
    """目标制定页面、登录或门户导航未达到可执行状态。"""


class TargetGoalSelectorError(RuntimeError):
    """目标制定页面已打开，但已探查的 DOM 契约无法定位。"""


class TargetGoalPage:
    """封装目标制定查询区域的已探查 DOM 定位和读取操作。"""

    ROUTE = "/biopark-apm/apm/scheduling/goal"
    QUERY_FORM = "form.adaptive-form:visible"

    def __init__(self, page: Page, settings: Settings) -> None:
        """初始化页面对象。"""
        self.page = page
        self.settings = settings

    def ensure_open(self) -> Page:
        """确保当前页面位于目标制定路由，否则从门户重新导航。"""
        if self.ROUTE not in self.page.url:
            try:
                self.page = PortalNavigation(self.page, self.settings).open_target_goal_page()
            except Exception as exc:  # noqa: BLE001
                raise TargetGoalReadinessError(f"目标制定页面不可达：{exc}") from exc
        if self.ROUTE not in self.page.url:
            raise TargetGoalReadinessError(f"目标制定路由未就绪：{self.page.url}")
        return self.page

    def wait_ready(self) -> None:
        """等待目标页面 DOM、查询表单和列表表头稳定。"""
        try:
            try:
                self.page.wait_for_load_state("networkidle", timeout=15_000)
            except PlaywrightTimeoutError:
                pass
            self.page.locator(self.QUERY_FORM).first.wait_for(state="visible", timeout=8_000)
            self.page.locator(".el-table__header-wrapper:visible").first.wait_for(
                state="visible", timeout=8_000
            )
        except PlaywrightTimeoutError as exc:
            raise TargetGoalSelectorError("目标制定查询区域或表头未达到 DOM 就绪状态") from exc

    def query_form(self):
        """返回已探查的可见目标制定查询表单。"""
        form = self.page.locator(self.QUERY_FORM).first
        if not form.count() or not form.is_visible():
            raise TargetGoalSelectorError("未找到可见目标制定查询表单 form.adaptive-form")
        return form

    def get_query_labels(self) -> list[str]:
        """读取查询表单内可见字段标签。"""
        return [text.strip() for text in self.query_form().locator(".el-form-item__label:visible").all_inner_texts()]

    def get_query_field_state(self) -> dict[str, object]:
        """读取年度输入和状态下拉的已探查属性，不修改页面状态。"""
        form = self.query_form()
        year_item = form.locator(".el-form-item").filter(has_text="年度").first
        status_item = form.locator(".el-form-item").filter(has_text="状态").first
        year_input = year_item.locator('input[placeholder="请选择年份"]').first
        status_select = status_item.locator(".el-select").first
        return {
            "year_item_count": year_item.count(),
            "year_input_count": year_input.count(),
            "year_placeholder": year_input.get_attribute("placeholder") if year_input.count() else None,
            "year_value": year_input.input_value() if year_input.count() else None,
            "status_item_count": status_item.count(),
            "status_select_count": status_select.count(),
            "status_placeholder": status_item.locator(".el-select__placeholder").first.inner_text().strip()
            if status_item.locator(".el-select__placeholder").count()
            else None,
        }

    def get_table_years(self) -> list[int]:
        """读取当前可见目标表格第二列中的年度值。"""
        rows = self.page.locator(".el-table__body-wrapper:visible tbody tr")
        years: list[int] = []
        for index in range(rows.count()):
            cells = rows.nth(index).locator("td")
            if cells.count() < 2:
                continue
            value = cells.nth(1).inner_text().strip()
            if value.isdigit():
                years.append(int(value))
        return years

    def select_year(self, year: int) -> None:
        """在已探查的年度日期选择器中选择指定年度。"""
        form = self.query_form()
        year_input = form.locator('input[placeholder="请选择年份"]').first
        if not year_input.count():
            raise TargetGoalSelectorError("年度选择器输入框不可定位")
        year_input.click()
        panel = self.page.locator(".el-picker-panel:visible").first
        panel.wait_for(state="visible", timeout=5_000)
        for _ in range(20):
            option = panel.locator("td").filter(has_text=str(year)).first
            if option.count() and option.is_visible():
                option.click()
                return
            next_range = panel.locator("button.el-picker-panel__icon-btn.d-arrow-right:visible").first
            if not next_range.count() or not next_range.is_visible():
                break
            next_range.click()
        raise TargetGoalReadinessError(f"年度选择器未提供年度：{year}")

    def select_status(self, status: str) -> None:
        """在已探查的状态下拉中选择指定状态。"""
        form = self.query_form()
        status_item = form.locator(".el-form-item").filter(has_text="状态").first
        selector = status_item.locator(".el-select").first
        if not selector.count():
            raise TargetGoalSelectorError("状态下拉控件不可定位")
        selector.click()
        option = self.page.locator(".el-select-dropdown:visible .el-select-dropdown__item").filter(has_text=status).first
        option.wait_for(state="visible", timeout=5_000)
        option.click()

    def click_query(self) -> None:
        """点击查询按钮并等待目标表格刷新稳定。"""
        button = self.page.get_by_role("button", name="查询", exact=True)
        if not button.count() or not button.first.is_visible():
            raise TargetGoalSelectorError("查询按钮不可定位")
        button.first.click()
        self.wait_table_ready()

    def refresh_table(self) -> list[int]:
        """点击表格刷新按钮，并返回连续两次读取一致的年份列表。"""
        button = self.page.get_by_role("button", name="刷新", exact=True)
        if not button.count() or not button.first.is_visible():
            raise TargetGoalSelectorError("表格刷新按钮不可定位")
        button.first.click()
        self.wait_table_ready()

        previous: tuple[int, ...] | None = None
        for _ in range(20):
            years = tuple(self.get_table_years())
            if years == previous:
                return sorted(set(years))
            previous = years
            self.page.wait_for_timeout(250)
        raise TargetGoalReadinessError("刷新后目标表格年份数据未达到稳定状态")

    def collect_years_across_pages(self) -> list[int]:
        """点击刷新并遍历表格全部分页，返回升序去重的全部目标年度。"""
        self.refresh_table()
        prev_btn = self.page.locator(".el-pagination .btn-prev")
        for _ in range(200):
            if prev_btn.count() == 0 or prev_btn.first.is_disabled():
                break
            prev_btn.first.click()
            self.wait_table_ready()
        years: set[int] = set()
        next_btn = self.page.locator(".el-pagination .btn-next")
        for _ in range(200):
            years.update(self.get_table_years())
            if next_btn.count() == 0 or next_btn.first.is_disabled():
                break
            next_btn.first.click()
            self.wait_table_ready()
        for _ in range(200):
            if prev_btn.count() == 0 or prev_btn.first.is_disabled():
                break
            prev_btn.first.click()
            self.wait_table_ready()
        return sorted(years)

    def wait_table_ready(self) -> None:
        """等待目标表格表头和表体稳定。"""
        try:
            self.page.locator(".el-table__header-wrapper:visible").first.wait_for(state="visible", timeout=8_000)
            self.page.locator(".el-table__body-wrapper:visible").first.wait_for(state="visible", timeout=8_000)
        except PlaywrightTimeoutError as exc:
            raise TargetGoalSelectorError("目标表格未达到稳定状态") from exc

    def get_visible_row_years(self) -> list[int]:
        """读取查询完成后的目标表格年度，用于结果断言。"""
        return self.get_table_years()

    def get_row_by_year(self, year: int):
        """按表格第二列年度读取唯一目标行。"""
        rows = self.page.locator(".el-table__body-wrapper:visible tbody tr")
        for index in range(rows.count()):
            cells = rows.nth(index).locator("td")
            if cells.count() >= 2 and cells.nth(1).inner_text().strip() == str(year):
                return rows.nth(index)
        return None

    def get_row_status(self, year: int) -> str:
        """读取指定年度行的状态列。"""
        row = self.get_row_by_year(year)
        if row is None:
            raise TargetGoalReadinessError(f"目标列表不存在年度：{year}")
        cells = row.locator("td")
        if cells.count() < 5:
            raise TargetGoalSelectorError("目标表格状态列不可定位")
        return cells.nth(4).inner_text().strip()

    def reset_query(self) -> None:
        """点击重置并等待查询表格稳定。"""
        button = self.page.get_by_role("button", name="重置", exact=True)
        if not button.count() or not button.first.is_visible():
            raise TargetGoalSelectorError("重置按钮不可定位")
        button.first.click()
        self.wait_table_ready()

    def get_query_values(self) -> dict[str, str | None]:
        """读取年度和状态查询控件当前值。"""
        form = self.query_form()
        year = form.locator('input[placeholder="请选择年份"]').first
        status = form.locator(".el-form-item").filter(has_text="状态").first
        placeholder = status.locator(".el-select__placeholder").first
        return {
            "year": year.input_value() if year.count() else None,
            "status": placeholder.inner_text().strip() if placeholder.count() else None,
        }

    def open_new_dialog(self) -> None:
        """点击真实新增按钮并等待新增目标弹窗出现。"""
        button = self.page.get_by_role("button", name="新增", exact=True)
        if not button.count() or not button.first.is_visible():
            raise TargetGoalSelectorError("新增按钮不可定位")
        button.first.click()
        self.dialog().wait_for(state="visible", timeout=8_000)

    def open_edit_dialog(self, year: int) -> None:
        """在指定年度行点击编辑并等待编辑弹窗出现。"""
        row = self.get_row_by_year(year)
        if row is None:
            raise TargetGoalReadinessError(f"目标列表不存在年度：{year}")
        button = row.get_by_role("button", name="编辑", exact=True)
        if not button.count() or not button.first.is_visible():
            raise TargetGoalReadinessError(f"年度 {year} 没有可用编辑入口")
        button.first.click()
        self.dialog().wait_for(state="visible", timeout=8_000)

    def open_review_dialog(self, year: int) -> None:
        """在指定年度行点击审核并等待审核弹窗出现。"""
        row = self.get_row_by_year(year)
        if row is None:
            raise TargetGoalReadinessError(f"目标列表不存在年度：{year}")
        button = row.get_by_role("button", name="审核", exact=True)
        if not button.count() or not button.first.is_visible():
            raise TargetGoalReadinessError(f"年度 {year} 没有可用审核入口")
        button.first.click()
        self.dialog().wait_for(state="visible", timeout=8_000)

    def open_delete_confirmation(self, year: int) -> None:
        """在指定年度行点击删除并等待真实确认框出现。"""
        row = self.get_row_by_year(year)
        if row is None:
            raise TargetGoalReadinessError(f"目标列表不存在年度：{year}")
        button = row.get_by_role("button", name="删除", exact=True)
        if not button.count() or not button.first.is_visible():
            raise TargetGoalReadinessError(f"年度 {year} 没有可用删除入口")
        button.first.click()
        self.page.locator(".el-message-box:visible").wait_for(state="visible", timeout=8_000)

    def dialog(self):
        """返回当前最上层可见业务弹窗。"""
        dialogs = self.page.locator(".el-dialog:visible")
        if not dialogs.count():
            raise TargetGoalSelectorError("当前没有可见目标制定弹窗")
        return dialogs.last

    def fill_goal_form(self, year: int, annual: str = "120.0000", monthly: str = "10.0000") -> None:
        """在新增/编辑弹窗填写年度和年度宰杀量，并通过真实按钮生成月度分配。"""
        dialog = self.dialog()
        year_input = dialog.locator('input[placeholder="请选择年份"]').first
        if not year_input.count():
            raise TargetGoalSelectorError("目标弹窗年度输入不可定位")
        self._select_year_in_input(year_input, year)
        numbers = dialog.locator('input[type="number"]:visible')
        if numbers.count() < 1:
            raise TargetGoalSelectorError("目标弹窗年度或月度数量输入不完整")
        numbers.nth(0).fill(annual)
        average_button = dialog.get_by_role("button", name="按月平均分配", exact=True)
        if not average_button.count() or not average_button.first.is_visible():
            raise TargetGoalSelectorError("按月平均分配按钮不可定位")
        average_button.first.click()
        try:
            dialog.locator('input[type="number"]:visible').nth(1).wait_for(state="visible", timeout=5_000)
        except PlaywrightTimeoutError as exc:
            raise TargetGoalSelectorError("月度分配输入未在平均分配动作后稳定") from exc

    def get_monthly_values(self) -> list[str]:
        """读取目标弹窗中十二个月度数量输入的当前值。"""
        numbers = self.dialog().locator('input[type="number"]:visible')
        if numbers.count() < 13:
            raise TargetGoalSelectorError("目标弹窗月度数量输入不完整")
        return [numbers.nth(index).input_value() for index in range(1, 13)]

    def _select_year_in_input(self, year_input, year: int) -> None:
        """在目标弹窗年度日期选择器中选择指定年度。"""
        year_input.click()
        panel = self.page.locator(".el-picker-panel:visible").first
        panel.wait_for(state="visible", timeout=5_000)
        for _ in range(20):
            option = panel.locator("td").filter(has_text=str(year)).first
            if option.count() and option.is_visible():
                option.click()
                return
            next_range = panel.locator("button.el-picker-panel__icon-btn.d-arrow-right:visible").first
            if not next_range.count():
                break
            next_range.click()
        raise TargetGoalReadinessError(f"年度选择器未提供年度：{year}")

    def save_dialog(self) -> None:
        """点击目标弹窗保存按钮并等待弹窗关闭。"""
        self.dialog().get_by_role("button", name="保存", exact=True).click()
        self.page.locator(".el-dialog:visible").last.wait_for(state="hidden", timeout=10_000)
        self.wait_table_ready()

    def save_and_submit_dialog(self) -> None:
        """点击保存并提交按钮，在新弹窗中点击确认提交按钮完成提交。"""
        self.dialog().get_by_role("button", name="保存并提交", exact=True).click()
        confirm_button = self.page.get_by_role("button", name="确认提交", exact=True)
        confirm_button.first.wait_for(state="visible", timeout=8_000)
        confirm_button.first.click()
        self.page.locator(".el-dialog:visible").last.wait_for(state="hidden", timeout=10_000)
        self.wait_table_ready()

    def cancel_dialog(self) -> None:
        """关闭当前目标弹窗且不保存业务数据。"""
        self.dialog().get_by_role("button", name="取消", exact=True).click()
        self.page.locator(".el-dialog:visible").last.wait_for(state="hidden", timeout=8_000)

    def capture_scope(self, path: Path) -> None:
        """截取当前查询表单区域，供断言时刻证据使用。"""
        self.query_form().screenshot(path=str(path))

    def capture_full(self, path: Path) -> None:
        """截取当前完整页面，供断言时刻证据使用。"""
        self.page.screenshot(path=str(path), full_page=True)

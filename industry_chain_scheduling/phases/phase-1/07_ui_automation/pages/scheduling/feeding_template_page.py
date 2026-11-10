"""分段养殖模版页面对象：封装查询、新增、快速分配、保存、提交、审核、驳回、复制、删除等交互。

所有交互方法均假定 self.page 已处于分段养殖模版页（由 ensure_open 保证）。
选择器来源：2026-08-25 页面侦察 dump 的真实 DOM。
"""

from __future__ import annotations

import re
from pathlib import Path

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError

from config.settings import Settings
from pages.common.portal_navigation import PortalNavigation


class FeedingTemplateReadinessError(RuntimeError):
    """分段养殖模版页面、登录或门户导航未达到可执行状态。"""


class FeedingTemplateSelectorError(RuntimeError):
    """分段养殖模版页面已打开，但已探查的 DOM 契约无法定位。"""


_STATUS_VALUES = ("审核通过", "暂存", "待审核", "驳回")


class FeedingTemplatePage:
    """封装分段养殖模版页面的已探查 DOM 定位和交互操作。"""

    ROUTE = "/biopark-apm/apm/scheduling/feeding-template"
    QUERY_FORM = "form.adaptive-form:visible"

    def __init__(self, page: Page, settings: Settings) -> None:
        """初始化页面对象。"""
        self.page = page
        self.settings = settings

    # ----- 导航与就绪 -----

    def ensure_open(self) -> Page:
        """确保当前页面位于分段养殖模版路由，否则从门户重新导航。"""
        if self.ROUTE not in self.page.url:
            try:
                self.page = PortalNavigation(self.page, self.settings).open_feeding_template_page()
            except Exception as exc:
                raise FeedingTemplateReadinessError(f"分段养殖模版页面不可达：{exc}") from exc
        if self.ROUTE not in self.page.url:
            raise FeedingTemplateReadinessError(f"分段养殖模版路由未就绪：{self.page.url}")
        return self.page

    def wait_ready(self) -> None:
        """等待页面 DOM、查询表单和列表表头稳定。"""
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
            raise FeedingTemplateSelectorError("分段养殖模版查询区域或表头未达到 DOM 就绪状态") from exc

    def reload(self) -> Page:
        """重新加载页面以复位查询/弹窗状态。"""
        if self.ROUTE in self.page.url and "portal" not in self.page.url.lower():
            self.page.reload(wait_until="domcontentloaded", timeout=20_000)
        else:
            return self.ensure_open()
        try:
            self.page.wait_for_load_state("networkidle", timeout=15_000)
        except PlaywrightTimeoutError:
            pass
        self.page.wait_for_timeout(600)
        return self.page

    # ----- 查询表单 -----

    def query_form(self):
        """返回已探查的可见查询表单。"""
        form = self.page.locator(self.QUERY_FORM).first
        if not form.count() or not form.is_visible():
            raise FeedingTemplateSelectorError("未找到可见查询表单 form.adaptive-form")
        return form

    def get_query_labels(self) -> list[str]:
        """读取查询表单内可见字段标签。"""
        return [text.strip() for text in self.query_form().locator(".el-form-item__label:visible").all_inner_texts()]

    def get_query_field_state(self) -> dict[str, object]:
        """读取模版名称输入和品种/补栏月份/状态下拉的已探查属性，不修改页面状态。"""
        form = self.query_form()
        name_item = form.locator(".el-form-item").filter(has_text="模版名称").first
        breed_item = form.locator(".el-form-item").filter(has_text="品种").first
        month_item = form.locator(".el-form-item").filter(has_text="补栏月份").first
        status_item = form.locator(".el-form-item").filter(has_text="状态").first
        name_input = name_item.locator('input[placeholder="请输入模版名称"]').first
        return {
            "name_item_count": name_item.count(),
            "name_input_count": name_input.count(),
            "name_placeholder": name_input.get_attribute("placeholder") if name_input.count() else None,
            "breed_select_count": breed_item.locator(".el-select").count(),
            "month_select_count": month_item.locator(".el-select").count(),
            "status_select_count": status_item.locator(".el-select").count(),
        }

    def fill_name(self, keyword: str) -> None:
        """在查询区「模版名称」输入关键字。"""
        form = self.query_form()
        name_item = form.locator(".el-form-item").filter(has_text="模版名称").first
        name_input = name_item.locator('input[placeholder="请输入模版名称"]').first
        if not name_input.count():
            raise FeedingTemplateSelectorError("模版名称输入框不可定位")
        name_input.fill(keyword)

    def _select_dropdown(self, field_label: str, option_text: str) -> None:
        """在查询区指定字段下拉中选择指定选项文本。"""
        form = self.query_form()
        item = form.locator(".el-form-item").filter(has_text=field_label).first
        selector = item.locator(".el-select").first
        if not selector.count():
            raise FeedingTemplateSelectorError(f"{field_label} 下拉控件不可定位")
        selector.click()
        # 下拉面板 teleport 到 body，可能延迟渲染；轮询等待第一个选项可见
        dropdown = None
        for _ in range(10):
            dropdowns = self.page.locator(".el-select-dropdown:visible")
            if dropdowns.count():
                dropdown = dropdowns.last
                # 等待至少一个选项可见
                first_opt = dropdown.locator(".el-select-dropdown__item").first
                if first_opt.count():
                    try:
                        first_opt.wait_for(state="visible", timeout=1_000)
                        break
                    except PlaywrightTimeoutError:
                        pass
            self.page.wait_for_timeout(200)
        if dropdown is None:
            self.page.keyboard.press("Escape")
            raise FeedingTemplateSelectorError(f"{field_label} 下拉面板未出现")
        option = dropdown.locator(".el-select-dropdown__item").filter(has_text=option_text).first
        if not option.count():
            # 尝试模糊匹配（选项文本可能含额外空格或格式）
            option = dropdown.locator(".el-select-dropdown__item").filter(has_text=option_text.replace("月", "")).first
        if not option.count() or not option.is_visible():
            # 列出实际选项供调试
            all_opts = dropdown.locator(".el-select-dropdown__item").all_inner_texts()
            self.page.keyboard.press("Escape")
            raise FeedingTemplateSelectorError(
                f"{field_label} 下拉未提供选项：{option_text}；实际选项：{[o.strip() for o in all_opts[:20]]}"
            )
        option.click()

    def select_breed(self, breed: str) -> None:
        """在查询区「品种」下拉选择指定品种。"""
        self._select_dropdown("品种", breed)

    def select_restock_month(self, month: str) -> None:
        """在查询区「补栏月份」下拉选择指定月份（如「3月」）。"""
        self._select_dropdown("补栏月份", month)

    def select_status(self, status: str) -> None:
        """在查询区「状态」下拉选择指定状态。"""
        self._select_dropdown("状态", status)

    def click_query(self) -> None:
        """点击查询按钮并等待表格数据刷新稳定。"""
        button = self.page.get_by_role("button", name="查询", exact=True)
        if not button.count() or not button.first.is_visible():
            raise FeedingTemplateSelectorError("查询按钮不可定位")
        button.first.click()
        self.wait_table_ready()
        self._wait_data_stable()

    def _wait_data_stable(self) -> None:
        """等待表格行数连续两次读取一致，避免查询后读到过渡态旧数据。"""
        try:
            self.page.wait_for_load_state("networkidle", timeout=8_000)
        except PlaywrightTimeoutError:
            pass
        previous: tuple[int, ...] | None = None
        for _ in range(20):
            rows = self._body_rows()
            count = rows.count()
            names = tuple(self.get_table_names()[:count])
            snapshot = (count, names)
            if snapshot == previous:
                return
            previous = snapshot
            self.page.wait_for_timeout(250)
        # 末次快照已稳定即返回，不抛错（某些场景行数本就波动）

    def reset_query(self) -> None:
        """点击重置按钮并等待表格稳定。"""
        button = self.page.get_by_role("button", name="重置", exact=True)
        if not button.count() or not button.first.is_visible():
            raise FeedingTemplateSelectorError("重置按钮不可定位")
        button.first.click()
        self.wait_table_ready()

    def get_query_values(self) -> dict[str, str | None]:
        """读取当前查询控件值，用于重置后验证。"""
        form = self.query_form()
        name = form.locator('input[placeholder="请输入模版名称"]').first
        name_value = name.input_value() if name.count() else None
        breed_text = self._read_select_text("品种")
        month_text = self._read_select_text("补栏月份")
        status_text = self._read_select_text("状态")
        return {"name": name_value, "breed": breed_text, "month": month_text, "status": status_text}

    def _read_select_text(self, field_label: str) -> str | None:
        """读取查询区指定下拉当前已选文本（不展开下拉）。"""
        form = self.query_form()
        item = form.locator(".el-form-item").filter(has_text=field_label).first
        selector = item.locator(".el-select").first
        if not selector.count():
            return None
        placeholder = selector.locator(".el-select__placeholder").first
        if placeholder.count():
            return placeholder.inner_text().strip()
        selected = selector.locator(".el-select__selected-item").first
        if selected.count():
            return selected.inner_text().strip()
        return None

    def clear_query_inputs(self) -> None:
        """清空模版名称输入（用于组合查询前确保单条件）。"""
        form = self.query_form()
        name_input = form.locator('input[placeholder="请输入模版名称"]').first
        if name_input.count():
            name_input.fill("")

    # ----- 表格读取 -----

    def wait_table_ready(self) -> None:
        """等待表格表头和表体稳定。"""
        try:
            self.page.locator(".el-table__header-wrapper:visible").first.wait_for(state="visible", timeout=8_000)
            self.page.locator(".el-table__body-wrapper:visible").first.wait_for(state="visible", timeout=8_000)
        except PlaywrightTimeoutError as exc:
            raise FeedingTemplateSelectorError("分段养殖模版表格未达到稳定状态") from exc

    def _body_rows(self):
        """返回表格主体可见主行（排除展开行，用 el-table__row class 区分）。"""
        rows = self.page.locator(".el-table__body-wrapper:visible tbody tr.el-table__row")
        if not rows.count():
            rows = self.page.locator(".el-table__body-wrapper:visible tbody tr")
        return rows

    def _row_cells(self, row) -> list[str]:
        """读取一行所有可见单元格文本。"""
        return [c.strip() for c in row.locator("td").all_inner_texts()]

    def _extract_status(self, cells: list[str]) -> str:
        """从行的单元格文本中提取状态值（审核通过/暂存/待审核/驳回）。"""
        for cell in cells:
            for status in _STATUS_VALUES:
                if cell == status:
                    return status
        return ""

    def get_table_rows(self) -> list[dict[str, str]]:
        """读取当前表格全部可见行的模版名称/品种/补栏月份/状态。"""
        rows = self._body_rows()
        out: list[dict[str, str]] = []
        for i in range(rows.count()):
            cells = self._row_cells(rows.nth(i))
            if not cells:
                continue
            out.append({
                "name": cells[3] if len(cells) > 3 else "",
                "breed": cells[1] if len(cells) > 1 else "",
                "month": cells[2] if len(cells) > 2 else "",
                "status": self._extract_status(cells),
            })
        return out

    def get_row_count(self) -> int:
        """返回当前表格可见行数。"""
        return self._body_rows().count()

    def get_table_names(self) -> list[str]:
        """读取当前表格模版名称列。"""
        return [r["name"] for r in self.get_table_rows() if r["name"]]

    def get_table_breeds(self) -> list[str]:
        """读取当前表格品种列。"""
        return [r["breed"] for r in self.get_table_rows() if r["breed"]]

    def get_table_months(self) -> list[str]:
        """读取当前表格补栏月份列。"""
        return [r["month"] for r in self.get_table_rows() if r["month"]]

    def get_table_statuses(self) -> list[str]:
        """读取当前表格状态列。"""
        return [r["status"] for r in self.get_table_rows() if r["status"]]

    def has_empty_state(self) -> bool:
        """判断表格是否为空状态（无数据）。"""
        empty = self.page.locator(".el-table__empty-text:visible")
        return empty.count() > 0 and self.get_row_count() == 0

    # ----- 操作列与行定位 -----

    def get_row_by_name(self, name: str):
        """按模版名称列定位行，返回行 locator 或 None。"""
        rows = self._body_rows()
        for i in range(rows.count()):
            cells = self._row_cells(rows.nth(i))
            if len(cells) > 3 and cells[3] == name:
                return rows.nth(i)
        return None

    def get_row_status_by_name(self, name: str) -> str:
        """按模版名称读取该行状态。"""
        row = self.get_row_by_name(name)
        if row is None:
            raise FeedingTemplateReadinessError(f"列表不存在模版：{name}")
        cells = self._row_cells(row)
        return self._extract_status(cells)

    # ----- 弹窗（新增/编辑/审核/查看） -----

    def dialog(self):
        """返回当前最上层可见业务弹窗。"""
        dialogs = self.page.locator(".el-dialog:visible")
        if not dialogs.count():
            raise FeedingTemplateSelectorError("当前没有可见业务弹窗")
        return dialogs.last

    def dialog_title(self) -> str:
        """读取当前可见弹窗的标题文本（标题在 .el-dialog__header 内）。"""
        dlg = self.dialog()
        header = dlg.locator(".el-dialog__header").first
        if header.count():
            return header.inner_text().strip()
        title = dlg.locator(".el-dialog__title").first
        if title.count():
            return title.inner_text().strip()
        return ""

    def wait_dialog_closed(self) -> None:
        """等待业务弹窗关闭。"""
        self.page.locator(".el-dialog:visible").last.wait_for(state="hidden", timeout=10_000)

    # ----- 新增弹窗 -----

    def click_new(self) -> None:
        """点击新增按钮并等待新增弹窗出现。"""
        button = self.page.get_by_role("button", name="新增", exact=True)
        if not button.count() or not button.first.is_visible():
            raise FeedingTemplateSelectorError("新增按钮不可定位")
        button.first.click()
        self.dialog().wait_for(state="visible", timeout=10_000)

    def fill_template_form(self, name: str, breed: str, month: str) -> None:
        """在新增弹窗填写模版名称、品种、补栏月份（触发参考值带出）。"""
        dlg = self.dialog()
        name_input = dlg.locator('input[placeholder="请输入模版名称"]').first
        if not name_input.count():
            raise FeedingTemplateSelectorError("新增弹窗模版名称输入不可定位")
        name_input.fill(name)
        self._select_dialog_dropdown(dlg, "品种", breed)
        self._select_dialog_dropdown(dlg, "补栏月份", month)
        try:
            self.page.wait_for_load_state("networkidle", timeout=5_000)
        except PlaywrightTimeoutError:
            pass
        self.page.wait_for_timeout(500)

    def _select_dialog_dropdown(self, dlg, field_label: str, option_text: str) -> None:
        """在弹窗内的 el-select 中选择指定选项。

        新版 Element Plus el-select 用 Tooltip 包裹。品种可输入过滤（fillable），
        补栏月份 input 是 readonly 不可输入。统一用 get_by_role("option") 定位选项。
        """
        item = dlg.locator(".el-form-item").filter(has_text=field_label).first
        wrapper = item.locator(".el-select__wrapper").first
        if not wrapper.count():
            wrapper = item.locator(".el-select").first
        if not wrapper.count():
            raise FeedingTemplateSelectorError(f"弹窗内 {field_label} 下拉控件不可定位")
        select_input = item.locator(".el-select__input").first
        is_readonly = False
        if select_input.count():
            is_readonly = select_input.get_attribute("readonly") is not None
        # 点击展开下拉
        wrapper.click()
        self.page.wait_for_timeout(400)
        # 方案1：filterable input 输入过滤后用 Enter
        if not is_readonly and select_input.count():
            try:
                select_input.fill(option_text)
                self.page.wait_for_timeout(500)
                self.page.keyboard.press("Enter")
                self.page.wait_for_timeout(300)
                selected = select_input.input_value()
                if selected and option_text in selected:
                    return
            except PlaywrightTimeoutError:
                pass
        # 方案2：用 get_by_role("option") 定位并点击
        option = self.page.get_by_role("option", name=option_text, exact=False).last
        for _ in range(10):
            if option.count():
                try:
                    option.wait_for(state="visible", timeout=1_000)
                    option.click()
                    self.page.wait_for_timeout(300)
                    return
                except PlaywrightTimeoutError:
                    pass
            # 重新点击展开
            wrapper.click()
            self.page.wait_for_timeout(300)
        # 方案3：用文本匹配定位（兜底）
        text_locator = self.page.locator(f".el-select-dropdown__item:visible, li[role='option']:visible").filter(has_text=option_text).last
        if text_locator.count():
            try:
                text_locator.click()
                self.page.wait_for_timeout(300)
                return
            except PlaywrightTimeoutError:
                pass
        self.page.keyboard.press("Escape")
        raise FeedingTemplateSelectorError(
            f"弹窗内 {field_label} 下拉未选中 {option_text}（readonly={is_readonly}）"
        )

    def open_quick_assign(self) -> None:
        """点击快速分配按钮并等待快速分配弹窗出现。"""
        dlg = self.dialog()
        button = dlg.get_by_role("button", name="快速分配", exact=True)
        if not button.count() or not button.first.is_visible():
            raise FeedingTemplateSelectorError("快速分配按钮不可定位")
        button.first.click()
        # 快速分配弹窗作为第二个可见 .el-dialog
        quick = self.page.locator(".el-dialog:visible").last
        quick.wait_for(state="visible", timeout=8_000)

    def fill_quick_assign(self, segment1_days: str, segment1_empty: str,
                          segment2_days: str, segment2_empty: str,
                          segment3_empty: str) -> None:
        """在快速分配弹窗填写整批与各段养殖/空栏天数并点击确认。

        3段养殖天数为自动计算，不填写。
        """
        quick = self.page.locator(".el-dialog:visible").last
        numbers = quick.locator('input[type="number"]:visible')
        if numbers.count() < 6:
            raise FeedingTemplateSelectorError(f"快速分配弹窗数字输入不足：{numbers.count()}")
        # 顺序按 DOM：整批养殖天数/整批空栏天数/1段养殖/1段空栏/2段养殖/2段空栏/3段养殖(只读)/3段空栏
        # 实际顺序需根据 dump 确认；按 placeholder=请输入 的可编辑项填写
        editable = [numbers.nth(i) for i in range(numbers.count())
                    if numbers.nth(i).get_attribute("placeholder") == "请输入"
                    and not numbers.nth(i).get_attribute("disabled")]
        if len(editable) < 6:
            raise FeedingTemplateSelectorError(f"快速分配弹窗可编辑数字输入不足：{len(editable)}")
        editable[0].fill(segment1_days)
        editable[1].fill(segment1_empty)
        editable[2].fill(segment2_days)
        editable[3].fill(segment2_empty)
        editable[4].fill(segment3_empty)
        # 确认按钮
        confirm = quick.get_by_role("button", name="确认", exact=True)
        if not confirm.count():
            confirm = quick.get_by_role("button", name="确定", exact=True)
        if not confirm.count():
            raise FeedingTemplateSelectorError("快速分配弹窗确认按钮不可定位")
        confirm.first.click()
        self.page.locator(".el-dialog:visible").last.wait_for(state="hidden", timeout=10_000)

    def get_segment_days(self) -> list[str]:
        """读取新增弹窗三段养殖天数输入框当前值。"""
        dlg = self.dialog()
        numbers = dlg.locator('input[type="number"][placeholder="自动计算"]:visible')
        if numbers.count() < 3:
            raise FeedingTemplateSelectorError(f"新增弹窗三段养殖天数输入不足：{numbers.count()}")
        return [numbers.nth(i).input_value() for i in range(3)]

    def get_daily_feed_plans(self) -> list[dict[str, str]]:
        """读取日龄采食计划列表中每条方案的起/止输入值。"""
        dlg = self.dialog()
        plans: list[dict[str, str]] = []
        scheme_boxes = dlg.locator(".scheme-box")
        for i in range(scheme_boxes.count()):
            box = scheme_boxes.nth(i)
            start = box.locator(".feed-plan-form-item.start-day-form-item input").first
            end = box.locator(".feed-plan-form-item.end-day-form-item input").first
            if start.count() and end.count():
                plans.append({"start": start.input_value(), "end": end.input_value()})
        return plans

    def save_dialog(self) -> None:
        """点击保存按钮并等待弹窗关闭（处理可能的确认框）。"""
        self.dialog().get_by_role("button", name="保存", exact=True).first.click()
        # 保存后可能出现确认框或成功提示
        self._handle_post_save_confirm()
        self.wait_dialog_closed()
        self.wait_table_ready()

    def submit_dialog(self) -> None:
        """点击保存并提交按钮，在确认框点确定。"""
        self.dialog().get_by_role("button", name="保存并提交", exact=True).first.click()
        self._handle_post_save_confirm()
        self.wait_dialog_closed()
        self.wait_table_ready()

    def _handle_post_save_confirm(self) -> None:
        """保存/提交后处理可能出现的确认框（.el-message-box 或 .el-dialog）。"""
        for _ in range(3):
            self.page.wait_for_timeout(500)
            box = self.page.locator(".el-message-box:visible")
            if box.count():
                text = box.inner_text()
                if "确定" in text or "确认" in text or "提交" in text:
                    box.get_by_role("button", name="确定", exact=True).first.click()
                    self.page.wait_for_timeout(300)
                    continue
                # 其它确认框点取消
                cancel = box.get_by_role("button", name="取消", exact=True)
                if cancel.count():
                    cancel.first.click()
                break
            # 也可能是 .el-dialog 确认框
            confirm_dlg = self.page.locator(".el-dialog:visible .el-dialog__footer button:visible")
            if confirm_dlg.count() >= 2:
                # 最后一个按钮通常是确定
                confirm_dlg.last.click()
                self.page.wait_for_timeout(300)
                continue
            break

    def cancel_dialog(self) -> None:
        """点击取消按钮关闭弹窗且不保存。"""
        self.dialog().get_by_role("button", name="取消", exact=True).first.click()
        self.wait_dialog_closed()

    # ----- 行操作（提交/审核/查看/编辑/删除/复制） -----

    def _click_row_action(self, name: str, action: str) -> None:
        """在指定模版名称行点击操作列按钮。"""
        row = self.get_row_by_name(name)
        if row is None:
            raise FeedingTemplateReadinessError(f"列表不存在模版：{name}")
        button = row.get_by_role("button", name=action, exact=True)
        if not button.count() or not button.first.is_visible():
            raise FeedingTemplateReadinessError(f"模版 {name} 没有可用 {action} 入口")
        button.first.click()

    def click_submit(self, name: str) -> None:
        """点击行提交按钮。"""
        self._click_row_action(name, "提交")

    def click_review(self, name: str) -> None:
        """点击行审核按钮并等待审核弹窗。"""
        self._click_row_action(name, "审核")
        self.dialog().wait_for(state="visible", timeout=8_000)

    def click_view(self, name: str) -> None:
        """点击行查看按钮并等待查看弹窗。"""
        self._click_row_action(name, "查看")
        self.dialog().wait_for(state="visible", timeout=8_000)

    def click_edit(self, name: str) -> None:
        """点击行编辑按钮并等待编辑弹窗。"""
        self._click_row_action(name, "编辑")
        self.dialog().wait_for(state="visible", timeout=8_000)

    def click_delete(self, name: str) -> None:
        """点击行删除按钮并等待确认框。"""
        self._click_row_action(name, "删除")
        self.page.locator(".el-message-box:visible").wait_for(state="visible", timeout=8_000)

    def click_copy(self, name: str) -> None:
        """点击行复制按钮并等待确认框。"""
        self._click_row_action(name, "复制")
        self.page.locator(".el-message-box:visible").wait_for(state="visible", timeout=8_000)

    # ----- 确认框 -----

    def confirm_message_box(self) -> str:
        """读取当前可见确认框文本并点击确定。返回确认框文案。"""
        box = self.page.locator(".el-message-box:visible")
        box.wait_for(state="visible", timeout=5_000)
        text = box.inner_text()
        box.get_by_role("button", name="确定", exact=True).first.click()
        self.page.wait_for_timeout(500)
        return text

    def cancel_message_box(self) -> str:
        """读取当前可见确认框文本并点击取消。返回确认框文案。"""
        box = self.page.locator(".el-message-box:visible")
        box.wait_for(state="visible", timeout=5_000)
        text = box.inner_text()
        box.get_by_role("button", name="取消", exact=True).first.click()
        self.page.wait_for_timeout(500)
        return text

    # ----- 审核/驳回 -----

    def review_reject(self, reason: str) -> None:
        """在审核弹窗点击驳回，填写原因后确认。"""
        dlg = self.dialog()
        reject_btn = dlg.get_by_role("button", name="驳回", exact=True)
        if not reject_btn.count():
            raise FeedingTemplateSelectorError("审核弹窗驳回按钮不可定位")
        reject_btn.first.click()
        confirm = self.page.locator(".el-dialog:visible").last
        confirm.wait_for(state="visible", timeout=8_000)
        reason_input = confirm.locator("textarea").first
        if not reason_input.count():
            reason_input = confirm.locator('input[placeholder*="原因"]').first
        if not reason_input.count():
            raise FeedingTemplateSelectorError("驳回确认框原因输入不可定位")
        reason_input.fill(reason)
        confirm.get_by_role("button", name="确定", exact=True).first.click()
        self.wait_dialog_closed()
        self.wait_table_ready()

    def review_approve(self) -> str:
        """在审核弹窗点击审核通过，处理二次确认框后返回确认框文案。"""
        dlg = self.dialog()
        approve_btn = dlg.get_by_role("button", name="审核通过", exact=True)
        if not approve_btn.count():
            approve_btn = dlg.get_by_role("button", name="通过", exact=True)
        if not approve_btn.count():
            raise FeedingTemplateSelectorError("审核弹窗通过按钮不可定位")
        approve_btn.first.click()
        box = self.page.locator(".el-message-box:visible")
        box_text = ""
        if box.count():
            box.wait_for(state="visible", timeout=5_000)
            box_text = box.inner_text()
            box.get_by_role("button", name="确定", exact=True).first.click()
            self.page.wait_for_timeout(500)
        self.wait_dialog_closed()
        self.wait_table_ready()
        return box_text

    # ----- 证据截图 -----

    def capture_scope(self, path: Path) -> None:
        """截取当前查询表单区域。"""
        self.query_form().screenshot(path=str(path))

    def capture_full(self, path: Path) -> None:
        """截取当前完整页面。"""
        self.page.screenshot(path=str(path), full_page=True)

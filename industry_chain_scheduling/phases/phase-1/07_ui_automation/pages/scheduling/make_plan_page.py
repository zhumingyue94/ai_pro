"""制定排程页面对象：封装列表查询、制定月度排程编辑、智能推荐栋舍抽屉、保存/提交/删除等交互。

所有交互方法均假定页面由 ensure_open / open_create_editor 保证处于目标路由。
选择器来源：2026-08-25 页面侦查 dump 的真实 DOM。
"""

from __future__ import annotations

import re
from pathlib import Path

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError

from config.settings import Settings
from pages.common.portal_navigation import PortalNavigation

STATUS_VALUES = ("暂存", "待审核", "审核通过", "驳回")
MONTH_CN = ("一月", "二月", "三月", "四月", "五月", "六月", "七月", "八月", "九月", "十月", "十一月", "十二月")
JH_CODE_RE = re.compile(r"JH-\d{8}-\d{2}")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
SCORE_RE = re.compile(r"匹配度\s*(\d+)\s*分")
HOUSE_RE = re.compile(r"(\d+)\s*栋")
MIN_IDLE_RE = re.compile(r"三段最小空闲\s*(\d+)\s*天")


class MakePlanReadinessError(RuntimeError):
    """制定排程页面、登录或门户导航未达到可执行状态。"""


class MakePlanSelectorError(RuntimeError):
    """制定排程页面已打开，但已探查的 DOM 契约无法定位。"""


class MakePlanPage:
    """封装制定排程列表页与制定月度排程编辑页的已探查 DOM 定位和交互操作。"""

    ROUTE = "/biopark-apm/apm/scheduling/make-schedule"
    CREATE_ROUTE = "/biopark-apm/apm/scheduling/makeschedule/form/create"
    QUERY_FORM = "form.adaptive-form:visible"

    def __init__(self, page: Page, settings: Settings) -> None:
        """初始化页面对象。"""
        self.page = page
        self.settings = settings

    # ----- 导航与就绪 -----

    def ensure_open(self) -> Page:
        """确保当前页面位于制定排程列表路由，否则从门户重新导航。"""
        if self.ROUTE not in self.page.url or self.CREATE_ROUTE in self.page.url or "/form/edit/" in self.page.url:
            try:
                self.page = PortalNavigation(self.page, self.settings).open_make_plan_page()
            except Exception as exc:
                raise MakePlanReadinessError(f"制定排程列表页不可达：{exc}") from exc
        if self.ROUTE not in self.page.url or "makeschedule/form" in self.page.url:
            raise MakePlanReadinessError(f"制定排程列表路由未就绪：{self.page.url}")
        return self.page

    def wait_ready(self) -> None:
        """等待列表页查询表单和表格表头稳定。"""
        try:
            try:
                self.page.wait_for_load_state("networkidle", timeout=15_000)
            except PlaywrightTimeoutError:
                pass
            self.page.locator(self.QUERY_FORM).first.wait_for(state="visible", timeout=10_000)
            self.page.locator(".el-table__header-wrapper:visible").first.wait_for(state="visible", timeout=10_000)
        except PlaywrightTimeoutError as exc:
            raise MakePlanSelectorError("制定排程查询区域或表头未达到 DOM 就绪状态") from exc

    # ----- 列表查询表单 -----

    def query_form(self):
        """返回已探查的可见查询表单。"""
        form = self.page.locator(self.QUERY_FORM).first
        if not form.count() or not form.is_visible():
            raise MakePlanSelectorError("未找到可见查询表单 form.adaptive-form")
        return form

    def _pick_month_panel(self, month_cn: str) -> None:
        """在已打开的月份面板中选择指定中文月份。"""
        panel = self.page.locator(".el-picker-panel:visible").last
        if not panel.count():
            raise MakePlanSelectorError("月份选择面板未出现")
        cells = panel.locator(".el-month-table td")
        for i in range(cells.count()):
            if cells.nth(i).inner_text().strip() == month_cn:
                cells.nth(i).click()
                self.page.wait_for_timeout(800)
                return
        self.page.keyboard.press("Escape")
        raise MakePlanSelectorError(f"月份面板未提供月份：{month_cn}")

    def pick_query_month(self, month: int) -> None:
        """在查询区「计划月份」选择指定月份（1-12）。"""
        form = self.query_form()
        item = form.locator(".el-form-item").filter(has_text="计划月份").first
        inp = item.locator("input").first
        if not inp.count():
            raise MakePlanSelectorError("计划月份输入框不可定位")
        inp.click(force=True)
        self.page.wait_for_timeout(800)
        self._pick_month_panel(MONTH_CN[month - 1])

    def _select_dropdown(self, field_label: str, option_text: str) -> None:
        """在查询区指定字段下拉中选择指定选项文本。"""
        form = self.query_form()
        item = form.locator(".el-form-item").filter(has_text=field_label).first
        selector = item.locator(".el-select").first
        if not selector.count():
            raise MakePlanSelectorError(f"{field_label} 下拉控件不可定位")
        selector.click()
        dropdown = None
        for _ in range(10):
            dropdowns = self.page.locator(".el-select-dropdown:visible")
            if dropdowns.count():
                dropdown = dropdowns.last
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
            raise MakePlanSelectorError(f"{field_label} 下拉面板未出现")
        option = dropdown.locator(".el-select-dropdown__item").filter(has_text=option_text).first
        if not option.count() or not option.is_visible():
            all_opts = dropdown.locator(".el-select-dropdown__item").all_inner_texts()
            self.page.keyboard.press("Escape")
            raise MakePlanSelectorError(f"{field_label} 下拉未提供选项：{option_text}；实际：{[o.strip() for o in all_opts[:10]]}")
        option.click()
        self.page.wait_for_timeout(400)

    def select_status(self, status: str) -> None:
        """在查询区「计划状态」下拉选择指定状态。"""
        self._select_dropdown("计划状态", status)

    def select_line(self, line: str) -> None:
        """在查询区「宰杀线」下拉选择指定宰杀线。"""
        self._select_dropdown("宰杀线", line)

    def click_query(self) -> None:
        """点击查询按钮并等待表格数据刷新稳定。"""
        button = self.page.get_by_role("button", name="查询", exact=True)
        if not button.count() or not button.first.is_visible():
            raise MakePlanSelectorError("查询按钮不可定位")
        button.first.click()
        self.wait_table_ready()
        self._wait_data_stable()

    def _wait_data_stable(self) -> None:
        """等待表格行内容连续三次读取一致，避免读到过渡态旧数据或加载中状态。"""
        try:
            self.page.wait_for_load_state("networkidle", timeout=8_000)
        except PlaywrightTimeoutError:
            pass
        try:
            self.page.locator(".el-loading-mask:visible").first.wait_for(state="hidden", timeout=8_000)
        except PlaywrightTimeoutError:
            pass
        same_count = 0
        previous: tuple | None = None
        for _ in range(30):
            snapshot = tuple(r.get("code", "") for r in self.get_table_rows()) + (self._body_rows().count(),)
            if snapshot == previous:
                same_count += 1
                if same_count >= 2:
                    return
            else:
                same_count = 0
            previous = snapshot
            self.page.wait_for_timeout(300)

    def reset_query(self) -> None:
        """点击重置按钮并等待表格稳定。"""
        button = self.page.get_by_role("button", name="重置", exact=True)
        if not button.count() or not button.first.is_visible():
            raise MakePlanSelectorError("重置按钮不可定位")
        button.first.click()
        self.wait_table_ready()
        self._wait_data_stable()

    def get_query_values(self) -> dict[str, str | None]:
        """读取当前查询控件值，用于重置后验证。"""
        form = self.query_form()
        month_item = form.locator(".el-form-item").filter(has_text="计划月份").first
        month_input = month_item.locator("input").first
        month_value = month_input.input_value() if month_input.count() else None
        return {
            "month": month_value,
            "status": self._read_select_text("计划状态"),
            "line": self._read_select_text("宰杀线"),
        }

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

    # ----- 列表表格读取 -----

    def wait_table_ready(self) -> None:
        """等待表格表头和表体稳定。"""
        try:
            self.page.locator(".el-table__header-wrapper:visible").first.wait_for(state="visible", timeout=10_000)
            self.page.locator(".el-table__body-wrapper:visible").first.wait_for(state="visible", timeout=10_000)
        except PlaywrightTimeoutError as exc:
            raise MakePlanSelectorError("制定排程表格未达到稳定状态") from exc

    def _body_rows(self):
        """返回表格主体可见行。"""
        rows = self.page.locator(".el-table__body-wrapper:visible tbody tr.el-table__row")
        if not rows.count():
            rows = self.page.locator(".el-table__body-wrapper:visible tbody tr")
        return rows

    def get_table_rows(self) -> list[dict[str, str]]:
        """读取当前表格全部可见行，兼容按宰杀日期 rowspan 分组的单元格位移。

        返回每行的 code(计划编号)/line(宰杀线)/status(状态)/date(宰杀日期，组内继承)。
        """
        rows = self._body_rows()
        out: list[dict[str, str]] = []
        last_date = ""
        last_status = ""
        for i in range(rows.count()):
            cells = [c.strip() for c in rows.nth(i).locator("td").all_inner_texts()]
            if not cells:
                continue
            code = next((c for c in cells if JH_CODE_RE.fullmatch(c)), "")
            line = next((c for c in cells if c.endswith("宰杀线")), "")
            status = next((c for c in cells if c in STATUS_VALUES), "")
            # 已探查 DOM 契约：按宰杀日期分组的行，日期与状态单元格采用 rowspan 合并，
            # 组内续行 DOM 中不含这两个单元格，需从组首行继承。
            if status:
                last_status = status
            else:
                status = last_status
            code_index = cells.index(code) if code else -1
            date = ""
            for c in cells[:code_index if code_index >= 0 else len(cells)]:
                if DATE_RE.match(c):
                    date = c
            if date:
                last_date = date
            else:
                date = last_date
            out.append({"code": code, "line": line, "status": status, "date": date, "cells": cells})
        return out

    def get_row_count(self) -> int:
        """返回当前表格可见行数。"""
        return self._body_rows().count()

    def get_pagination_total(self) -> int | None:
        """读取分页总条数（共 N 条），无分页返回 None。"""
        total = self.page.locator(".el-pagination__total").first
        if not total.count():
            return None
        match = re.search(r"(\d+)", total.inner_text())
        return int(match.group(1)) if match else None

    def get_all_rows_paged(self) -> list[dict[str, str]]:
        """翻页读取当前查询结果的全部行。"""
        rows = list(self.get_table_rows())
        for _ in range(10):
            next_btn = self.page.locator(".el-pagination .btn-next").first
            if not next_btn.count():
                break
            classes = next_btn.get_attribute("class") or ""
            if next_btn.get_attribute("disabled") is not None or "disabled" in classes:
                break
            next_btn.click()
            self._wait_data_stable()
            rows.extend(self.get_table_rows())
        return rows

    def find_row_by_code(self, code: str):
        """按计划编号定位行 locator，未找到返回 None。"""
        rows = self._body_rows()
        for i in range(rows.count()):
            cells = [c.strip() for c in rows.nth(i).locator("td").all_inner_texts()]
            if code in cells:
                return rows.nth(i)
        return None

    def get_row_status_by_code(self, code: str) -> str:
        """按计划编号读取该行状态。"""
        row = self.find_row_by_code(code)
        if row is None:
            raise MakePlanReadinessError(f"列表不存在计划：{code}")
        cells = [c.strip() for c in row.locator("td").all_inner_texts()]
        return next((c for c in cells if c in STATUS_VALUES), "")

    def click_row_action(self, code: str, action: str) -> None:
        """在指定计划编号行点击操作列按钮。"""
        row = self.find_row_by_code(code)
        if row is None:
            raise MakePlanReadinessError(f"列表不存在计划：{code}")
        button = row.get_by_role("button", name=action, exact=True)
        if not button.count() or not button.first.is_visible():
            raise MakePlanReadinessError(f"计划 {code} 没有可用 {action} 入口")
        button.first.click()

    # ----- 确认框 -----

    def message_box(self):
        """返回当前可见 el-message-box，无则抛错。"""
        box = self.page.locator(".el-message-box:visible")
        try:
            box.first.wait_for(state="visible", timeout=6_000)
        except PlaywrightTimeoutError as exc:
            raise MakePlanSelectorError("确认框 el-message-box 未出现") from exc
        return box.first

    def confirm_message_box(self) -> str:
        """读取当前可见确认框文本并点击确定。返回确认框文案。"""
        box = self.message_box()
        text = box.inner_text()
        box.get_by_role("button", name="确定", exact=True).first.click()
        self.page.wait_for_timeout(800)
        return text

    def cancel_message_box(self) -> str:
        """读取当前可见确认框文本并点击取消。返回确认框文案。"""
        box = self.message_box()
        text = box.inner_text()
        box.get_by_role("button", name="取消", exact=True).first.click()
        self.page.wait_for_timeout(800)
        return text

    def wait_success_message(self, keyword: str, timeout: int = 10_000) -> str:
        """等待包含指定关键字的 el-message 成功提示并返回其文本。"""
        deadline = timeout // 250
        for _ in range(deadline):
            msgs = self.page.locator(".el-message:visible")
            for i in range(msgs.count()):
                text = msgs.nth(i).inner_text().strip()
                if keyword in text:
                    return text
            self.page.wait_for_timeout(250)
        raise MakePlanSelectorError(f"成功提示未出现：{keyword}")

    # ----- 制定月度排程编辑页 -----

    def open_create_editor(self) -> None:
        """在列表页点击「制定月度排程」进入编辑页并等待就绪。"""
        button = self.page.get_by_role("button", name="制定月度排程", exact=True)
        if not button.count() or not button.first.is_visible():
            raise MakePlanSelectorError("制定月度排程按钮不可定位")
        button.first.click()
        try:
            self.page.wait_for_url("**/makeschedule/form/create**", timeout=15_000)
        except PlaywrightTimeoutError as exc:
            raise MakePlanReadinessError("制定月度排程编辑页路由未就绪") from exc
        try:
            self.page.wait_for_load_state("networkidle", timeout=15_000)
        except PlaywrightTimeoutError:
            pass
        self.page.wait_for_timeout(1_500)

    def reload_create_editor(self) -> None:
        """重新加载编辑页以复位未保存的日计划编辑状态。"""
        self.page.reload(wait_until="domcontentloaded", timeout=20_000)
        try:
            self.page.wait_for_load_state("networkidle", timeout=15_000)
        except PlaywrightTimeoutError:
            pass
        self.page.wait_for_timeout(1_500)

    def pick_editor_month(self, month: int) -> None:
        """在编辑页顶部月份控件选择指定月份（1-12）。"""
        month_input = self.page.locator('input[placeholder="请选择月份"]').first
        if not month_input.count():
            raise MakePlanSelectorError("编辑页月份输入框不可定位")
        month_input.click(force=True)
        self.page.wait_for_timeout(800)
        self._pick_month_panel(MONTH_CN[month - 1])
        self.page.wait_for_timeout(1_500)

    def pick_pending_day(self, index: int = 0) -> bool:
        """点击月度看板中第 index 个可见「待排」日期，成功返回 True。"""
        pending = self.page.locator("text=待排")
        visible = [pending.nth(i) for i in range(pending.count()) if pending.nth(i).is_visible()]
        if index >= len(visible):
            return False
        visible[index].click()
        self.page.wait_for_timeout(1_500)
        return True

    def current_edit_date(self) -> str:
        """读取日计划编辑区当前日期文本（YYYY年MM月DD日）。"""
        body = self.page.locator("body").inner_text()
        match = re.search(r"日计划编辑\s*(\d{4})年(\d{2})月(\d{2})日", body)
        if not match:
            raise MakePlanSelectorError("日计划编辑日期区域未出现")
        return f"{match.group(1)}-{match.group(2)}-{match.group(3)}"

    def editor_form(self):
        """返回编辑页可见业务表单。"""
        form = self.page.locator("form:visible").last
        if not form.count():
            raise MakePlanSelectorError("编辑页业务表单不可定位")
        return form

    def select_editor_line(self, option_index: int = 0) -> str:
        """在编辑区「宰杀线」下拉选择指定序号选项，返回所选文本。"""
        form = self.editor_form()
        item = form.locator(".el-form-item").filter(has_text="宰杀线").first
        selector = item.locator(".el-select").first
        if not selector.count():
            raise MakePlanSelectorError("编辑区宰杀线下拉不可定位")
        selector.click()
        self.page.wait_for_timeout(700)
        dropdown = self.page.locator(".el-select-dropdown:visible").last
        if not dropdown.count():
            self.page.keyboard.press("Escape")
            raise MakePlanSelectorError("编辑区宰杀线下拉面板未出现")
        options = dropdown.locator(".el-select-dropdown__item")
        if option_index >= options.count():
            self.page.keyboard.press("Escape")
            raise MakePlanSelectorError("编辑区宰杀线选项不足")
        text = options.nth(option_index).inner_text().strip()
        options.nth(option_index).click()
        self.page.wait_for_timeout(500)
        return text

    def open_template_dialog(self):
        """点击「养殖品种」输入框打开选择养殖模版弹窗。"""
        form = self.editor_form()
        item = form.locator(".el-form-item").filter(has_text="养殖品种").first
        inp = item.locator("input").first
        if not inp.count():
            raise MakePlanSelectorError("养殖品种输入框不可定位")
        inp.click()
        dialog = self.page.locator(".el-dialog:visible").last
        try:
            dialog.wait_for(state="visible", timeout=8_000)
        except PlaywrightTimeoutError as exc:
            raise MakePlanSelectorError("选择养殖模版弹窗未出现") from exc
        return dialog

    def select_template(self, dialog, name_keyword: str | None = None) -> dict[str, str]:
        """在模版弹窗选择一条可用模版并确定，返回所选模版行信息。

        默认选择第一条名称不含「勿用」的模版；提供关键字时按名称过滤。
        """
        rows = dialog.locator(".el-table__body-wrapper tbody tr")
        try:
            rows.first.wait_for(state="visible", timeout=10_000)
        except PlaywrightTimeoutError as exc:
            raise MakePlanReadinessError("选择养殖模版弹窗表格数据未加载") from exc
        self.page.wait_for_timeout(500)
        names = []
        for i in range(rows.count()):
            cells = [c.strip() for c in rows.nth(i).locator("td").all_inner_texts()]
            if len(cells) > 1 and cells[1]:
                names.append(cells[1])
        for i in range(rows.count()):
            cells = [c.strip() for c in rows.nth(i).locator("td").all_inner_texts()]
            name = cells[1] if len(cells) > 1 else ""
            if not name or "勿用" in name:
                continue
            if name_keyword and name_keyword not in name:
                continue
            radio = rows.nth(i).locator(".el-radio, input[type=radio], .el-checkbox").first
            if not radio.count():
                raise MakePlanSelectorError("模版行单选控件不可定位")
            radio.click()
            self.page.wait_for_timeout(400)
            dialog.get_by_role("button", name="确定", exact=True).first.click()
            self.page.wait_for_timeout(1_500)
            return {
                "name": name,
                "breed": cells[2] if len(cells) > 2 else "",
                "total_days": cells[4] if len(cells) > 4 else "",
                "seg1_days": cells[5] if len(cells) > 5 else "",
                "seg2_days": cells[6] if len(cells) > 6 else "",
                "seg3_days": cells[7] if len(cells) > 7 else "",
                "cells": cells,
            }
        raise MakePlanReadinessError(f"模版弹窗无可用（非勿用）模版；当前可见模版：{names[:10]}")

    def fill_editor_field(self, field_label: str, value: str) -> None:
        """填写编辑区字段（兼容 el-input-number 残留 aria-disabled 的已探查行为）。"""
        form = self.editor_form()
        item = form.locator(".el-form-item").filter(has_text=field_label).first
        inp = item.locator("input").first
        if not inp.count():
            raise MakePlanSelectorError(f"编辑区 {field_label} 输入框不可定位")
        inp.click(force=True)
        self.page.keyboard.press("ControlOrMeta+a")
        self.page.keyboard.type(str(value))
        self.page.keyboard.press("Tab")
        self.page.wait_for_timeout(400)

    def read_editor_field(self, field_label: str) -> str:
        """读取编辑区指定标签输入框当前值。"""
        form = self.editor_form()
        item = form.locator(".el-form-item").filter(has_text=field_label).first
        if not item.count():
            raise MakePlanSelectorError(f"编辑区 {field_label} 表单项不可定位")
        inp = item.locator("input").first
        if not inp.count():
            raise MakePlanSelectorError(f"编辑区 {field_label} 输入框不可定位")
        return inp.input_value()

    def read_segment_standards(self) -> list[dict[str, str]]:
        """读取编辑区三段养殖/空栏天数标准。"""
        form = self.editor_form()
        days_items = form.locator(".el-form-item").filter(has_text="养殖天数")
        empty_items = form.locator(".el-form-item").filter(has_text="空栏天数")
        segments: list[dict[str, str]] = []
        for i in range(min(days_items.count(), empty_items.count())):
            days_inp = days_items.nth(i).locator("input").first
            empty_inp = empty_items.nth(i).locator("input").first
            segments.append({
                "days": days_inp.input_value() if days_inp.count() else "",
                "empty": empty_inp.input_value() if empty_inp.count() else "",
            })
        return segments

    def click_save_day(self) -> str:
        """点击「保存当日计划」并等待成功提示，返回提示文本。"""
        button = self.page.get_by_role("button", name="保存当日计划", exact=True)
        if not button.count() or not button.first.is_visible():
            raise MakePlanSelectorError("保存当日计划按钮不可定位")
        button.first.click()
        return self.wait_success_message("成功")

    # ----- 提交月度审核 -----

    def click_submit_month_review(self):
        """在编辑页点击「提交月度审核」并等待提交审核弹窗，返回弹窗 locator。"""
        button = self.page.get_by_role("button", name="提交月度审核", exact=True)
        if not button.count() or not button.first.is_visible():
            raise MakePlanSelectorError("提交月度审核按钮不可定位")
        button.first.click()
        dialog = self.page.locator(".el-dialog:visible").last
        try:
            dialog.wait_for(state="visible", timeout=8_000)
        except PlaywrightTimeoutError as exc:
            raise MakePlanSelectorError("提交审核弹窗未出现") from exc
        return dialog

    # ----- 智能推荐栋舍抽屉 -----

    def open_recommend_drawer(self):
        """点击「推荐栋舍」打开智能推荐栋舍抽屉。"""
        button = self.page.get_by_role("button", name="推荐栋舍", exact=True)
        if not button.count() or not button.first.is_visible():
            raise MakePlanSelectorError("推荐栋舍按钮不可定位")
        button.first.click(force=True)
        drawer = self.page.locator(".el-drawer:visible").last
        try:
            drawer.wait_for(state="visible", timeout=8_000)
        except PlaywrightTimeoutError as exc:
            raise MakePlanSelectorError("智能推荐栋舍抽屉未出现") from exc
        self.page.wait_for_timeout(2_500)
        return drawer

    def close_drawer(self, drawer) -> None:
        """关闭智能推荐栋舍抽屉。"""
        close = drawer.locator(".el-drawer__close-btn").first
        if close.count():
            close.click()
        else:
            self.page.keyboard.press("Escape")
        self.page.wait_for_timeout(1_000)

    def read_drawer_summary(self, drawer) -> dict[str, int | str | None]:
        """读取抽屉摘要：全周期可分配数量、存在冲突数量、最优推荐。"""
        text = drawer.inner_text()
        assignable = re.search(r"全周期可分配\s*\n\s*(\d+)", text)
        conflict = re.search(r"存在冲突\s*\n\s*(\d+)", text)
        best = re.search(r"最优推荐\s*\n\s*([^\n]+)", text)
        return {
            "assignable": int(assignable.group(1)) if assignable else None,
            "conflict": int(conflict.group(1)) if conflict else None,
            "best": best.group(1).strip() if best else None,
        }

    def switch_strategy(self, drawer, strategy: str) -> None:
        """在抽屉中切换推荐策略（栋舍顺序优先/最小空闲优先）。

        已探查 DOM：策略切换为 el-radio-button 单选组（label.el-radio-button），非原生 button。
        """
        item = drawer.locator("label.el-radio-button").filter(has_text=strategy).first
        if not item.count():
            raise MakePlanSelectorError(f"推荐策略控件不可定位：{strategy}")
        item.click()
        self.page.wait_for_timeout(2_500)

    def read_candidates(self, drawer) -> list[dict[str, object]]:
        """读取抽屉候选栋舍卡片：栋号、匹配度分数、是否可分配、三段最小空闲天数。"""
        cards = drawer.locator("button").filter(has_text="养殖栋舍")
        out: list[dict[str, object]] = []
        for i in range(cards.count()):
            text = cards.nth(i).inner_text()
            house = HOUSE_RE.search(text)
            score = SCORE_RE.search(text)
            idle = MIN_IDLE_RE.search(text.replace("\n", " "))
            # 已探查文案：最优推荐且完全无占用的栋舍显示「空档充足」，等效最小空闲 0 天
            min_idle = int(idle.group(1)) if idle else (0 if "空档充足" in text else None)
            out.append({
                "house": house.group(1) if house else "",
                "score": int(score.group(1)) if score else None,
                "assignable": "不可分配" not in text and score is not None,
                "min_idle_days": min_idle,
                "text": text.replace("\n", " ")[:200],
                "index": i,
            })
        return out

    def click_candidate(self, drawer, house: str) -> None:
        """在抽屉中点击指定栋号的候选卡片。"""
        cards = drawer.locator("button").filter(has_text=f"养殖栋舍\n{house}栋")
        if not cards.count():
            cards = drawer.locator("button").filter(has_text=f"{house}栋")
        if not cards.count():
            raise MakePlanSelectorError(f"候选栋舍卡片不可定位：{house}栋")
        cards.first.click()
        self.page.wait_for_timeout(1_500)

    def click_drawer_select_confirm(self, drawer) -> str:
        """点击抽屉中「选择 X 栋」确认按钮，返回按钮文本。"""
        button = drawer.locator("button").filter(has_text=re.compile(r"选择\s*\d+\s*栋"))
        if not button.count():
            raise MakePlanSelectorError("抽屉「选择 X 栋」确认按钮不可定位")
        text = button.first.inner_text().strip()
        button.first.click()
        self.page.wait_for_timeout(2_000)
        return text

    # ----- 编辑页（行「编辑」进入） -----

    def click_save_and_submit(self) -> None:
        """在编辑页点击「保存并提交」并处理确认框；成功提示可选，状态以列表复核为准。"""
        button = self.page.get_by_role("button", name="保存并提交", exact=True)
        if not button.count() or not button.first.is_visible():
            raise MakePlanSelectorError("保存并提交按钮不可定位")
        button.first.click()
        self.page.wait_for_timeout(1_000)
        box = self.page.locator(".el-message-box:visible")
        if box.count():
            box.get_by_role("button", name="确定", exact=True).first.click()
            self.page.wait_for_timeout(1_000)
        try:
            self.wait_success_message("成功", timeout=5_000)
        except MakePlanSelectorError:
            pass

    # ----- 证据截图 -----

    def capture_scope(self, path: Path) -> None:
        """截取当前查询表单区域。"""
        self.query_form().screenshot(path=str(path))

    def capture_full(self, path: Path) -> None:
        """截取当前完整页面。"""
        self.page.screenshot(path=str(path), full_page=True)

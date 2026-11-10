"""通用日期范围控件交互工具。"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from playwright.sync_api import Locator, Page


@dataclass(frozen=True)
class DateRangePickerConfig:
    """日期范围控件的可访问名称配置。"""

    start_name: str = "开始日期"
    end_name: str = "结束日期"
    previous_month_name: str = "上个月"
    submit_name: str = "查询"


class DateRangePicker:
    """按调用方提供的日期范围操作日期选择控件。"""

    def __init__(self, page: Page, config: DateRangePickerConfig | None = None) -> None:
        self.page = page
        self.config = config or DateRangePickerConfig()

    def select(
        self,
        start_date: date,
        end_date: date,
        *,
        month_steps: int,
    ) -> tuple[str, str]:
        """先选结束日期，再向前切换月份并选择开始日期。"""
        if start_date > end_date:
            raise ValueError("日期范围的开始日期不能晚于结束日期")
        if month_steps < 0:
            raise ValueError("月份切换次数不能为负数")

        start_picker, end_picker = self._date_inputs()
        start_picker.scroll_into_view_if_needed()
        start_picker.click()
        self._select_visible_day(end_date)

        previous = self.page.get_by_role(
            "button", name=self.config.previous_month_name, exact=True
        )
        if previous.count() == 0:
            raise LookupError(f"未找到上一月按钮：{self.config.previous_month_name}")
        for _ in range(month_steps):
            previous.click()

        self._select_visible_day(start_date)
        submit = self.page.get_by_role("button", name=self.config.submit_name, exact=True)
        if submit.count() == 0:
            raise LookupError(f"未找到查询按钮：{self.config.submit_name}")
        submit.click()

        actual = (self._read_value(start_picker), self._read_value(end_picker))
        if not all(actual):
            raise LookupError(
                f"日期范围设置后输入框为空，目标值：{start_date.isoformat()}~{end_date.isoformat()}，"
                f"实际值：{actual}"
            )
        return start_date.isoformat(), end_date.isoformat()

    def _date_inputs(self) -> tuple[Locator, Locator]:
        start = self.page.get_by_role("combobox", name=self.config.start_name, exact=True)
        end = self.page.get_by_role("combobox", name=self.config.end_name, exact=True)
        if not start.count() or not end.count():
            raise LookupError(
                f"未找到日期控件：{self.config.start_name}、{self.config.end_name}"
            )
        return start.first, end.first

    def _select_visible_day(self, target: date) -> None:
        candidates = self.page.get_by_text(str(target.day), exact=True)
        for index in range(candidates.count()):
            candidate = candidates.nth(index)
            if candidate.is_visible():
                candidate.click()
                return
        raise LookupError(f"日期弹窗未找到可见日期：{target.isoformat()}")

    @staticmethod
    def _read_value(picker: Locator) -> str:
        return (picker.input_value() or "").strip()

"""公共雏苗发货列表页流程。"""

from __future__ import annotations

from calendar import monthrange
from datetime import date

from playwright.sync_api import Page

from pages.common.portal_navigation import PortalNavigation
from utils.date_range_picker import DateRangePicker, DateRangePickerConfig


class ChickDeliveryPage:
    """进入雏苗发货列表并设置发货日期范围。"""

    def __init__(self, page: Page) -> None:
        self.page = page

    def open_and_set_recent_half_year(
        self, navigation: PortalNavigation
    ) -> tuple[str, str]:
        """进入雏苗发货列表页，将发货日期设置为最近半年并校验。"""
        navigation.open_plan_menu_item("雏苗发货")
        return self.set_recent_half_year()

    def set_recent_half_year(self) -> tuple[str, str]:
        """按已录制流程设置“今天往前六个月”的发货日期范围。"""
        end_date = date.today()
        start_date = self._subtract_months(end_date, 6)
        return DateRangePicker(
            self.page,
            DateRangePickerConfig(
                start_name="开始日期",
                end_name="结束日期",
                previous_month_name="上个月",
                submit_name="查询",
            ),
        ).select(start_date, end_date, month_steps=6)

    @staticmethod
    def _subtract_months(value: date, months: int) -> date:
        month_index = value.year * 12 + value.month - 1 - months
        year, month_zero = divmod(month_index, 12)
        month = month_zero + 1
        return value.replace(day=min(value.day, monthrange(year, month)[1]), year=year, month=month)


"""REQ-PC-043 上孵计划列表的运行时探索对象。"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime

from playwright.sync_api import Page

from utils.table_explorer import TableExplorer


@dataclass(frozen=True)
class PlanBaseline:
    """从表格行提取的最小计划基线。"""

    demand_number: str
    plan_number: str
    values: dict[str, str]


class IncubationPlanPage:
    """通过公共表格遍历器运行时发现上孵计划数据。"""

    _TABLE_SELECTOR = ".ant-table, .el-table"
    _ROW_SELECTOR = "tbody tr:visible, .el-table__body tr:visible"

    def __init__(self, page: Page) -> None:
        self.page = page
        self.table_explorer = TableExplorer(page, self._TABLE_SELECTOR)

    def discover_baseline(self) -> PlanBaseline:
        """遍历所有分页、纵向滚动和横向字段后选择有效计划。"""
        def match(row) -> bool:
            values = self._row_values(row)
            demand = self._value(values, ("孵化需求号", "需求号"))
            plan = self._value(values, ("上孵计划号", "计划号", "上孵计划"))
            hatch_date = self._value(values, ("出雏日期", "出雏日", "出雏时间"))
            return bool(demand and plan and self._on_or_before_today(hatch_date))

        row = self.table_explorer.find(match, row_selector=self._ROW_SELECTOR)
        if row is None:
            raise LookupError(
                "上孵计划页面遍历所有滚动区域和分页后仍未发现出雏日期不晚于今天且同时包含孵化需求号和上孵计划号的有效数据"
            )
        values = self._row_values(row)
        return PlanBaseline(
            demand_number=self._value(values, ("孵化需求号", "需求号")),
            plan_number=self._value(values, ("上孵计划号", "计划号", "上孵计划")),
            values=values,
        )

    @staticmethod
    def _row_values(row) -> dict[str, str]:
        """按表格 DOM 结构解析表头；表头不在祖先节点时回退到页面表格。"""
        tables = row.locator(
            "xpath=ancestor::*[contains(@class, 'ant-table') or contains(@class, 'el-table')][1]"
        )
        table = tables.first if tables.count() else row.locator("xpath=ancestor::table[1]")
        headers = [
            text.strip()
            for text in table.locator("thead th, .el-table__header th").all_inner_texts()
        ]
        if not headers:
            headers = [
                text.strip()
                for text in row.page.locator(
                    ".ant-table:visible thead th, .el-table:visible .el-table__header th"
                ).all_inner_texts()
            ]
        cells = [text.strip() for text in row.locator("td").all_inner_texts()]
        return {headers[index]: cells[index] for index in range(min(len(headers), len(cells)))}

    @staticmethod
    def _on_or_before_today(value: str) -> bool:
        if not value:
            return False
        raw = value.strip().replace("/", "-")
        for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"):
            try:
                parsed = datetime.strptime(raw[:19], fmt).date()
                return parsed <= date.today()
            except ValueError:
                continue
        return False

    @staticmethod
    def _value(values: dict[str, str], names: tuple[str, ...]) -> str:
        for name in names:
            for key, value in values.items():
                if name in key and value and value not in {"-", "暂无数据"}:
                    return value
        return ""

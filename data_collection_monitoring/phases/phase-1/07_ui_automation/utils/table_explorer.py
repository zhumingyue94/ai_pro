"""可注入的表格纵向、横向滚动及分页遍历工具。"""

from __future__ import annotations

from collections.abc import Callable, Iterator
from typing import Any


class TableExplorer:
    """只负责遍历机制，调用方通过回调注入定位和匹配规则。"""

    TABLE_SELECTOR = ".ant-table, .el-table"
    ROW_SELECTOR = "tbody tr:visible, .el-table__body tr:visible"
    SCROLL_SELECTOR = (
        ".el-table__body-wrapper, .el-scrollbar__wrap, .ant-table-body, "
        "[style*='overflow']"
    )
    NEXT_PAGE_SELECTOR = (
        ".ant-pagination-next, .el-pagination .btn-next, "
        "button[aria-label*='下一页'], button[title*='下一页']"
    )

    def __init__(self, page, table_selector: str | None = None) -> None:
        self.page = page
        self.table_selector = table_selector or self.TABLE_SELECTOR

    def find(
        self,
        matches: Callable[[Any], bool],
        *,
        table_selector: str | None = None,
        row_selector: str | None = None,
        target_description: str = "目标数据",
    ) -> Any | None:
        """遍历所有分页、纵向位置和横向位置，返回首个匹配行。"""
        table_selector = table_selector or self.table_selector
        row_selector = row_selector or self.ROW_SELECTOR
        visited_pages: set[str] = set()
        for _ in range(100):
            table = self._find_table(table_selector)
            page_signature = self._page_signature(table, row_selector)
            if page_signature in visited_pages:
                break
            visited_pages.add(page_signature)
            for row in self.iter_rows(table, row_selector=row_selector):
                if matches(row):
                    return row
            if not self._go_to_next_page(page_signature, table_selector, row_selector):
                break
        return None

    def iter_rows(self, table, *, row_selector: str | None = None) -> Iterator[Any]:
        """按完整列、完整行边界增量读取，生成器关闭即可停止后续滚动。"""
        row_selector = row_selector or self.ROW_SELECTOR
        horizontal_positions = self._horizontal_positions(table)
        vertical_positions = self._vertical_positions(table, row_selector=row_selector)
        seen_by_horizontal: dict[int, set[str]] = {}

        for horizontal in horizontal_positions:
            for vertical in vertical_positions:
                self._set_horizontal(table, horizontal)
                self._set_vertical(table, vertical)
                rows = table.locator(row_selector)
                seen = seen_by_horizontal.setdefault(horizontal, set())
                for index in range(min(rows.count(), 100)):
                    row = rows.nth(index)
                    text = row.inner_text().strip()
                    if not text:
                        continue
                    key = self._row_key(row, text)
                    if key in seen:
                        continue
                    seen.add(key)
                    yield row

    def _find_table(self, selector: str):
        tables = self.page.locator(selector)
        for index in range(tables.count()):
            table = tables.nth(index)
            if table.is_visible():
                return table
        raise LookupError(f"页面未发现可见表格（当前 URL：{self.page.url}）")

    def _scroll_containers(self, table, *, horizontal: bool = False):
        candidates = table.locator(self.SCROLL_SELECTOR)
        result = []
        for index in range(candidates.count()):
            candidate = candidates.nth(index)
            if not candidate.is_visible():
                continue
            metrics = candidate.evaluate(
                "el => ({scrollWidth: el.scrollWidth, clientWidth: el.clientWidth, "
                "scrollHeight: el.scrollHeight, clientHeight: el.clientHeight})"
            )
            dimension = "scrollWidth" if horizontal else "scrollHeight"
            client = "clientWidth" if horizontal else "clientHeight"
            if int(metrics[dimension]) > int(metrics[client]) + 1:
                result.append(candidate)
        return result

    def _horizontal_positions(self, table) -> list[int]:
        """返回连续列左边界，确保每个横向窗口从完整字段开始。"""
        positions: set[int] = {0}
        for container in self._scroll_containers(table, horizontal=True):
            measurements = container.evaluate(
                """el => {
                    const root = el.getBoundingClientRect();
                    const cells = [...el.querySelectorAll(
                        'thead th, .ant-table-thead th, .el-table__header th'
                    )];
                    const max = Math.max(0, el.scrollWidth - el.clientWidth);
                    return {
                        max,
                        lefts: cells.map(cell => {
                            const rect = cell.getBoundingClientRect();
                            return rect.left - root.left + el.scrollLeft;
                        }).filter(value => Number.isFinite(value) && value >= 0)
                    };
                }"""
            )
            maximum = int(measurements["max"])
            positions.update(
                max(0, min(maximum, round(float(left))))
                for left in measurements["lefts"]
            )
            positions.add(maximum)
        return sorted(positions)

    def _vertical_positions(self, table, *, row_selector: str) -> list[int]:
        """返回完整行顶部位置，逐行推进并保留相邻窗口重叠。"""
        positions: set[int] = {0}
        for container in self._scroll_containers(table):
            measurements = container.evaluate(
                """(el, selector) => {
                    const root = el.getBoundingClientRect();
                    const max = Math.max(0, el.scrollHeight - el.clientHeight);
                    const rows = [...el.querySelectorAll(
                        selector.replace(/:visible/g, '')
                    )].filter(row => {
                        const style = getComputedStyle(row);
                        return style.display !== 'none' && style.visibility !== 'hidden';
                    });
                    return {
                        max,
                        tops: rows.map(row => {
                            const rect = row.getBoundingClientRect();
                            return rect.top - root.top + el.scrollTop;
                        }).filter(value => Number.isFinite(value) && value >= 0)
                    };
                }""",
                row_selector,
            )
            maximum = int(measurements["max"])
            positions.update(
                max(0, min(maximum, round(float(top))))
                for top in measurements["tops"]
            )
            positions.add(maximum)
        return sorted(positions)

    def _row_key(self, row, text: str) -> str:
        """优先使用 DOM 行标识，缺失时回退到文本，避免同一窗口重复匹配。"""
        return (
            row.get_attribute("data-row-key")
            or row.get_attribute("data-key")
            or row.get_attribute("data-id")
            or text
        )

    def _set_horizontal(self, table, position: int) -> None:
        for container in self._scroll_containers(table, horizontal=True):
            container.evaluate("(el, value) => { el.scrollLeft = value; }", position)

    def _set_vertical(self, table, position: int) -> None:
        for container in self._scroll_containers(table):
            container.evaluate("(el, value) => { el.scrollTop = value; }", position)

    def _page_signature(self, table, row_selector: str) -> str:
        rows = table.locator(row_selector)
        return "|".join(
            rows.nth(index).inner_text().strip()
            for index in range(min(rows.count(), 5))
        )

    def _go_to_next_page(
        self,
        old_signature: str,
        table_selector: str,
        row_selector: str,
    ) -> bool:
        candidates = self.page.locator(self.NEXT_PAGE_SELECTOR)
        for index in range(candidates.count()):
            button = candidates.nth(index)
            if not button.is_visible():
                continue
            if (
                button.is_disabled()
                or button.get_attribute("aria-disabled") == "true"
                or "disabled" in (button.get_attribute("class") or "")
            ):
                return False
            button.click()
            self.page.wait_for_timeout(300)
            return self._page_signature(
                self._find_table(table_selector), row_selector
            ) != old_signature
        return False

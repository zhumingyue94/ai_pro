"""REQ-PC-043 雏苗发货列表的运行时探索对象。"""

from __future__ import annotations

from playwright.sync_api import Page

from utils.table_explorer import TableExplorer


class DeliveryListPage:
    """在发货列表中探索筛选控件、目标行和详情入口。"""

    _ROW_SELECTOR = "tbody tr:visible, .el-table__body tr:visible"
    _TABLE_SELECTOR = ".ant-table, .el-table"

    def __init__(self, page: Page) -> None:
        self.page = page
        self.table_explorer = TableExplorer(page, self._TABLE_SELECTOR)

    def find_and_open_detail(self, baseline) -> Page:
        """遍历全部滚动区域和分页后，在目标行打开明细。"""
        keyword = self._find_search_input()
        keyword.fill(baseline.demand_number)
        query = self.page.get_by_role("button", name="查询", exact=True)
        if query.count() and query.first.is_visible():
            query.first.click()
        else:
            keyword.press("Enter")
        self.page.wait_for_timeout(800)

        row = self.table_explorer.find(
            lambda candidate: baseline.demand_number in candidate.inner_text(),
            row_selector=self._ROW_SELECTOR,
            target_description=f"孵化需求号 {baseline.demand_number}",
        )
        if row is None:
            raise LookupError(
                f"雏苗发货列表遍历所有滚动区域和分页后仍未找到孵化需求号：{baseline.demand_number}"
            )
        action = self._detail_action(row)
        if action is None:
            raise LookupError(f"目标行未找到明细入口：{baseline.demand_number}")
        action.click()
        self.page.wait_for_load_state("domcontentloaded")
        return self.page

    @staticmethod
    def _detail_action(row):
        actions = row.locator("button, a, [role='button']")
        for index in range(actions.count()):
            action = actions.nth(index)
            if not action.is_visible():
                continue
            label = (action.inner_text() or "").strip()
            title = action.get_attribute("title") or ""
            if any(word in f"{label}{title}" for word in ("明细", "查看", "详情")):
                return action
        return None

    def _find_search_input(self):
        for label in ("孵化需求号", "关键字", "搜索"):
            locator = self.page.get_by_placeholder(label)
            if locator.count() and locator.first.is_visible():
                return locator.first
        inputs = self.page.locator("input:visible")
        if inputs.count() == 1:
            return inputs.first
        raise LookupError("雏苗发货页面未发现唯一可交互查询输入框")

"""REQ-PC-043 发货单明细页面对象。"""

from __future__ import annotations

from playwright.sync_api import Page


EXPECTED_FIELDS = (
    "孵化需求号", "上孵计划号", "计划进度", "发货状态", "发货进度", "待发货数",
    "实际苗重", "种禽养殖场", "养殖批次", "周龄", "平均蛋重", "蛋重类型",
    "产蛋日期", "出雏时间", "备注",
)


class DeliveryDetailPage:
    """仅暴露 page inventory 已确认的稳定定位器。"""

    def __init__(self, page: Page) -> None:
        self.page = page

    @property
    def page_root(self):
        return self.page.locator("main")

    @property
    def incubation_table(self):
        return self.page.locator(".ant-table, .el-table")

    def assert_readonly_shell(self) -> None:
        self.page_root.wait_for(state="visible")
        self.incubation_table.wait_for(state="visible")

    def assert_baseline(self, baseline) -> None:
        """在可见表格中定位计划号并核对可比对字段。"""
        self.assert_readonly_shell()
        if self.page.get_by_text(baseline.plan_number, exact=True).count() == 0:
            raise AssertionError(f"详情页未显示目标上孵计划号：{baseline.plan_number}")
        text = self.incubation_table.first.inner_text()
        for field, value in baseline.values.items():
            if field in EXPECTED_FIELDS and value and value not in {"-", "暂无数据"} and value not in text:
                raise AssertionError(f"详情页字段值不一致：{field}={value}")
        operation_words = ("发货", "确认发货", "新增发货")
        if any(self.page.get_by_role("button", name=word, exact=True).count() for word in operation_words):
            raise AssertionError("详情页出现发货操作入口")

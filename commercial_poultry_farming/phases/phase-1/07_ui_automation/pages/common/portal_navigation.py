"""通用门户应用进入页面对象。"""

from __future__ import annotations

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError

from config.settings import ConfigurationError, Settings
from pages.common.login_page import LoginPage


class PortalNavigation:
    """登录共享测试门户并进入配置指定的应用。"""

    def __init__(self, page: Page, settings: Settings) -> None:
        """绑定页面对象和运行配置。"""
        self.page = page
        self.settings = settings

    def open_portal_app(self) -> Page:
        """从门户进入应用并返回应用页面。"""
        app_name = self.settings.portal_app_name
        if not app_name or app_name == "待确认" or app_name.startswith("<"):
            raise ConfigurationError("testcase.portal_app_name 尚未确认")
        self.page.goto(self.settings.portal_url, wait_until="domcontentloaded", timeout=20_000)
        try:
            self.page.wait_for_load_state("networkidle", timeout=15_000)
        except PlaywrightTimeoutError:
            pass
        LoginPage(self.page, self.settings).login_if_needed()
        self.page.wait_for_timeout(800)
        cards = self.page.locator("button.portal-home__card").filter(has_text=app_name)
        if not cards.count() or not cards.first.is_visible():
            raise RuntimeError("未找到配置的门户应用卡片")
        try:
            with self.page.context.expect_page(timeout=10_000) as popup_info:
                cards.first.click()
            app_page = popup_info.value
        except PlaywrightTimeoutError:
            app_page = self.page
        app_page.set_default_timeout(12_000)
        try:
            app_page.wait_for_load_state("networkidle", timeout=20_000)
        except PlaywrightTimeoutError:
            pass
        app_page.wait_for_timeout(800)
        return app_page

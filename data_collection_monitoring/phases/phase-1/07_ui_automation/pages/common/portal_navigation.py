"""通用门户应用进入页面对象。"""

from __future__ import annotations

from urllib.parse import urljoin

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
            with self.page.context.expect_page(timeout=30_000) as popup_info:
                cards.first.click()
            app_page = popup_info.value
        except PlaywrightTimeoutError as exc:
            raise RuntimeError("门户应用卡片未在可视浏览器中打开业务页面") from exc
        expected_host = self.settings.portal_url.split("/", 3)[2]
        if expected_host not in app_page.url:
            raise RuntimeError(f"门户应用打开了非目标业务页面：{app_page.url}")
        app_page.set_default_timeout(12_000)
        try:
            app_page.wait_for_load_state("networkidle", timeout=20_000)
        except PlaywrightTimeoutError:
            pass
        app_page.wait_for_timeout(800)
        return app_page

    def open_menu_item(self, menu_name: str, item_name: str) -> Page:
        """展开指定一级菜单并点击可见、可交互的业务菜单项。"""
        menu_candidates = self.page.get_by_text(menu_name, exact=True)
        menu = None
        for index in range(menu_candidates.count()):
            candidate = menu_candidates.nth(index)
            if candidate.is_visible():
                menu = candidate
                break
        if menu is None:
            raise PermissionError(f"当前账号未发现可见的一级菜单：{menu_name}")

        def find_target():
            labels = self.page.get_by_text(item_name, exact=True)
            for index in range(labels.count()):
                label = labels.nth(index)
                if not label.is_visible():
                    continue
                parent = label.locator(
                    "xpath=ancestor::*[self::a or self::button or self::li or "
                    "@role='menuitem' or contains(@class, 'menu-item')][1]"
                )
                if parent.count() and parent.is_visible():
                    return parent
            return None

        target = find_target()
        if target is None:
            menu.click()
            target = find_target()
        if target is None:
            raise PermissionError(f"当前账号未发现可交互的菜单项：{item_name}")
        href = target.get_attribute("href")
        target.click()
        if href and href.startswith("/") and self.page.url.rstrip("/") != urljoin(self.page.url, href).rstrip("/"):
            self.page.goto(urljoin(self.page.url, href), wait_until="domcontentloaded", timeout=20_000)
        try:
            self.page.wait_for_load_state("networkidle", timeout=15_000)
        except PlaywrightTimeoutError:
            pass
        self.page.wait_for_timeout(500)
        return self.page

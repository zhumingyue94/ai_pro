"""门户导航模块：在登录后从产业链生产排程系统门户进入目标制定/分段养殖模版页面。

"""

from __future__ import annotations

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError

from config.settings import Settings
from pages.common.login_page import LoginPage


class PortalNavigation:
    APP_NAME = "产业链生产排程系统"

    def __init__(self, page: Page, settings: Settings) -> None:
        """初始化门户导航器，绑定 Playwright 页面对象与运行配置。"""
        self.page = page
        self.settings = settings

    def _open_portal_app(self) -> Page:
        """登录门户并点击应用卡片进入应用首页，返回应用页面对象。"""
        self.page.goto(self.settings.portal_url, wait_until="domcontentloaded", timeout=20_000)
        try:
            self.page.wait_for_load_state("networkidle", timeout=15_000)
        except PlaywrightTimeoutError:
            pass
        LoginPage(self.page, self.settings).login_if_needed()
        self.page.wait_for_timeout(800)
        cards = self.page.locator("button.portal-home__card").filter(has_text=self.APP_NAME)
        if not cards.count() or not cards.first.is_visible():
            raise RuntimeError("target application card was not found in the portal")
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

    def _click_menu_item(self, app_page: Page, submenu_text: str, item_text: str) -> None:
        """在应用页展开指定子菜单并点击指定菜单项。"""
        subs = app_page.locator("li.el-sub-menu")
        target_sub = None
        for i in range(subs.count()):
            if submenu_text in subs.nth(i).inner_text() and subs.nth(i).is_visible():
                target_sub = subs.nth(i)
                break
        if target_sub is None:
            raise RuntimeError(f"{submenu_text} submenu was not found")
        target_sub.click()
        app_page.wait_for_timeout(400)
        items = app_page.locator("li.el-menu-item")
        for i in range(items.count()):
            it = items.nth(i)
            if it.is_visible() and it.inner_text().strip() == item_text:
                it.click()
                return
        raise RuntimeError(f"{item_text} menu item was not found")

    def open_target_goal_page(self) -> Page:
        """从门户首页导航进入目标制定页面，返回加载完成的应用页面对象。"""
        app_page = self._open_portal_app()
        self._click_menu_item(app_page, "排程管理", "目标制定")
        try:
            app_page.wait_for_url("**/biopark-apm/apm/scheduling/goal", timeout=20_000)
        except PlaywrightTimeoutError as exc:
            raise RuntimeError("target goal route did not become ready") from exc
        try:
            app_page.wait_for_load_state("networkidle", timeout=15_000)
        except PlaywrightTimeoutError:
            pass
        app_page.wait_for_timeout(800)
        return app_page

    def open_make_plan_page(self) -> Page:
        """从门户首页导航进入制定排程页面，返回加载完成的应用页面对象。"""
        app_page = self._open_portal_app()
        self._click_menu_item(app_page, "排程管理", "制定排程")
        try:
            app_page.wait_for_url("**/biopark-apm/apm/scheduling/make-schedule", timeout=20_000)
        except PlaywrightTimeoutError as exc:
            raise RuntimeError("make plan route did not become ready") from exc
        try:
            app_page.wait_for_load_state("networkidle", timeout=15_000)
        except PlaywrightTimeoutError:
            pass
        app_page.wait_for_timeout(800)
        return app_page

    def open_feeding_template_page(self) -> Page:
        """从门户首页导航进入分段养殖模版页面，返回加载完成的应用页面对象。"""
        app_page = self._open_portal_app()
        self._click_menu_item(app_page, "排程管理", "分段养殖模版")
        try:
            app_page.wait_for_url("**/feeding-template", timeout=20_000)
        except PlaywrightTimeoutError as exc:
            raise RuntimeError("feeding template route did not become ready") from exc
        try:
            app_page.wait_for_load_state("networkidle", timeout=15_000)
        except PlaywrightTimeoutError:
            pass
        app_page.wait_for_timeout(800)
        return app_page

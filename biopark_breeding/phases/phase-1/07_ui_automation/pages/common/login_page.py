"""通用门户登录页面对象。"""

from __future__ import annotations

from playwright.sync_api import Page

from config.settings import Settings


class LoginPage:
    """在可见登录页填写运行配置并进入门户。"""

    def __init__(self, page: Page, settings: Settings) -> None:
        """绑定页面对象和运行配置。"""
        self.page = page
        self.settings = settings

    def login_if_needed(self) -> None:
        """仅在当前页面需要登录时完成登录并等待门户稳定。"""
        inputs = self.page.locator("input:visible")
        if "/login" not in self.page.url and inputs.count() < 3:
            return
        if inputs.count() < 3:
            raise RuntimeError("登录表单未提供租户、账号和密码输入框")
        visible_inputs = [inputs.nth(index) for index in range(inputs.count())]
        if self.settings.tenant:
            visible_inputs[0].fill(self.settings.tenant)
        visible_inputs[1].fill(self.settings.username)
        visible_inputs[2].fill(self.settings.password)
        submit = self.page.get_by_role("button", name="登录", exact=True)
        if submit.count() and submit.first.is_visible():
            submit.first.click()
        else:
            buttons = self.page.locator("button")
            visible_buttons = [buttons.nth(index) for index in range(buttons.count()) if buttons.nth(index).is_visible()]
            if not visible_buttons:
                raise RuntimeError("未找到可见的登录按钮")
            visible_buttons[0].click()
        try:
            self.page.wait_for_url("**/portal", timeout=20_000)
        except Exception:
            if not self.page.locator("button.portal-home__card:visible").count():
                raise
        self.page.locator("button.portal-home__card:visible").first.wait_for(state="visible", timeout=20_000)

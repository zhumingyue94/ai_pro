"""登录页面交互模块：在登录页自动填写租户、账号、密码并提交，进入门户。

"""

from __future__ import annotations

from playwright.sync_api import Page

from config.settings import Settings


class LoginPage:
    def __init__(self, page: Page, settings: Settings) -> None:
        """
        初始化 LoginPage 实例，绑定浏览器页面对象与登录配置。
        """
        self.page = page
        self.settings = settings

    def login_if_needed(self) -> None:
        """
        在处于登录页时自动完成登录并跳转门户；已在门户内则直接返回。
        """
        inputs = self.page.locator("input:visible")
        visible_input_count = inputs.count()
        if "/login" not in self.page.url and visible_input_count < 3:
            return
        visible_inputs = [inputs.nth(i) for i in range(visible_input_count)]
        if len(visible_inputs) < 3:
            raise RuntimeError("login form did not expose the expected tenant/username/password fields")
        # Respect a pre-filled default tenant only when the runtime config leaves it empty;
        # otherwise the runtime tenant (env/.env) takes precedence.
        if self.settings.tenant:
            visible_inputs[0].fill(self.settings.tenant)
        visible_inputs[1].fill(self.settings.username)
        visible_inputs[2].fill(self.settings.password)
        # Click the explicit 登录 submit control, not the first visible (icon) button.
        submit = self.page.get_by_role("button", name="登录", exact=True)
        if submit.count() and submit.first.is_visible():
            submit.first.click()
        else:
            buttons = self.page.locator("button")
            visible_buttons = [buttons.nth(i) for i in range(buttons.count()) if buttons.nth(i).is_visible()]
            if not visible_buttons:
                raise RuntimeError("visible login button was not found")
            visible_buttons[0].click()
        try:
            self.page.wait_for_url("**/portal", timeout=20_000)
        except Exception:
            if not self.page.locator("button.portal-home__card:visible").count():
                raise
        self.page.locator("button.portal-home__card:visible").first.wait_for(state="visible", timeout=20_000)

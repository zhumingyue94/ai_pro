"""通用门户登录页面对象。"""

from __future__ import annotations

from playwright.sync_api import Page

from config.settings import Settings


class LoginPage:
    """使用可配置定位策略完成登录并检查认证状态。"""

    def __init__(self, page: Page, settings: Settings) -> None:
        self.page = page
        self.settings = settings

    def is_authenticated(self) -> bool:
        """根据认证后路径或门户应用卡片判断是否已登录。"""
        path = self.settings.authenticated_path
        return (path and path in self.page.url) or bool(
            self.page.locator(f"{self.settings.app_card_selector}:visible").count()
        )

    def wait_until_authenticated(self, timeout_ms: int | None = None) -> None:
        """等待认证完成，不自动绕过人工安全验证。"""
        timeout = timeout_ms or self.settings.auth_check_timeout_ms
        self.page.wait_for_function(
            "({path, selector}) => location.pathname.includes(path) || !!document.querySelector(selector)",
            {"path": self.settings.authenticated_path, "selector": self.settings.app_card_selector},
            timeout=timeout,
        )

    def ensure_authenticated(self) -> None:
        """复用有效登录态；失效时登录并在安全验证处明确阻塞。"""
        if self.is_authenticated():
            return
        self.login_if_needed()

    def login_if_needed(self) -> None:
        """仅在当前页面需要登录时完成登录并等待门户稳定。"""
        login_path = self.settings.login_path
        if login_path and login_path not in self.page.url and self.is_authenticated():
            return
        inputs = self.page.locator("input:visible")
        expected_inputs = 3 if self.settings.tenant_required else 2
        if inputs.count() < expected_inputs:
            raise RuntimeError(f"登录表单未提供足够的输入框，期望至少 {expected_inputs} 个")
        values = [self.settings.username, self.settings.password]
        if self.settings.tenant_required:
            values.insert(0, self.settings.tenant)
        for index, value in enumerate(values):
            inputs.nth(index).fill(value)
        submit = self.page.get_by_role("button", name=self.settings.login_button_name, exact=True)
        if submit.count() and submit.first.is_visible():
            submit.first.click()
        else:
            buttons = self.page.locator("button:visible")
            if not buttons.count():
                raise RuntimeError("未找到可见的登录按钮")
            buttons.first.click()
        try:
            self.wait_until_authenticated()
        except Exception as exc:
            if self._security_verification_visible():
                self.page.screenshot(path="test-results/security-verification.png", full_page=True)
                raise RuntimeError("blocked: 登录需要人工完成安全验证") from exc
            raise RuntimeError("登录后未达到配置的认证完成条件") from exc

    def _security_verification_visible(self) -> bool:
        """只检测验证现场，不识别图片或自动拖动滑块。"""
        markers = self.page.locator(
            "[class*='captcha']:visible, [class*='slider']:visible, "
            "[class*='verify']:visible, [aria-label*='验证']:visible"
        )
        return markers.count() > 0

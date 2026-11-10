"""通用门户登录页面对象。"""

from __future__ import annotations

from urllib.parse import urlparse

from playwright.sync_api import Page

from config.settings import Settings


class LoginPage:
    """在可见登录页填写运行配置并进入门户。"""

    def __init__(self, page: Page, settings: Settings) -> None:
        """绑定页面对象和运行配置。"""
        self.page = page
        self.settings = settings

    def is_portal_url(self) -> bool:
        """判断当前页面是否已跳转到门户路径，不绑定主机和端口。"""
        try:
            path = urlparse(self.page.url).path.rstrip("/") or "/"
        except ValueError:
            return False
        return path == "/portal"

    def is_authenticated(self) -> bool:
        """只读判断当前页面是否已进入认证后的门户。"""
        if "/login" in self.page.url or self._security_verification_visible():
            return False
        if self.is_portal_url():
            return True
        return self.page.locator("button.portal-home__card:visible").count() > 0

    def wait_until_authenticated(self, timeout_ms: int = 20_000) -> None:
        """等待门户跳转或门户导航完成，避免异步渲染造成误判。"""
        self.page.wait_for_function(
            """() => {
                const path = window.location.pathname.replace(/\\/+$/, '') || '/';
                const portal = path === '/portal';
                const card = !!document.querySelector('button.portal-home__card');
                const login = path.includes('/login');
                const security = [...document.querySelectorAll('[class*="captcha"], [class*="slider"], [class*="verify"], [aria-label*="验证"]')]
                    .some((element) => !!(element.offsetWidth || element.offsetHeight || element.getClientRects().length));
                return document.readyState !== 'loading' && !login && !security && (portal || card);
            }""",
            timeout=timeout_ms,
        )

    def assert_authenticated(self) -> None:
        """确认当前页面已认证，否则抛出认证异常。"""
        self.wait_until_authenticated()
        if not self.is_authenticated():
            raise RuntimeError(f"当前页面未通过已认证门户检查：url={self.page.url}")

    def ensure_authenticated(self) -> None:
        """复用有效登录态；失效时登录并在安全验证处明确阻塞。"""
        if self.is_authenticated():
            return
        self.login_if_needed()
        self.assert_authenticated()

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
            self.wait_until_authenticated()
        except Exception as exc:
            if self._security_verification_visible():
                raise RuntimeError("blocked: 登录需要人工完成滑动拼图安全验证") from exc
            raise RuntimeError(f"登录后未进入门户：url={self.page.url}") from exc

    def _security_verification_visible(self) -> bool:
        """只检测验证现场，不识别图片或自动拖动滑块。"""
        markers = self.page.locator(
            "[class*='captcha']:visible, [class*='slider']:visible, "
            "[class*='verify']:visible, [aria-label*='验证']:visible"
        )
        return markers.count() > 0

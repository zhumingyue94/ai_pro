"""通过可见 Chromium 完成一次禅道登录。

凭据只从当前进程环境变量读取，不加载 .env，不保存 storage state，
也不读取或修改禅道业务数据。
"""

from __future__ import annotations

import argparse
import os
import sys
from dataclasses import dataclass
from urllib.parse import urlsplit

from playwright.sync_api import Frame, Locator, Page, TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import sync_playwright


DEFAULT_TIMEOUT_MS = 30_000
CHALLENGE_KEYWORDS = (
    "验证码",
    "图形验证",
    "短信验证",
    "二次验证",
    "动态口令",
    "captcha",
    "verification code",
    "two-factor",
    "two factor",
    "mfa",
    "otp",
)
LOGIN_KEYWORDS = ("登录", "登入", "sign in", "log in", "login")
ACCOUNT_KEYWORDS = (
    "账号",
    "帐号",
    "用户名",
    "用户",
    "username",
    "user name",
    "account",
    "login",
    "email",
    "邮箱",
)
AUTH_MARKERS = ("退出", "注销", "logout", "log out", "sign out", "个人中心")
FAILURE_MARKERS = (
    "用户名或密码错误",
    "账号或密码错误",
    "登录失败",
    "密码错误",
    "invalid username",
    "invalid password",
    "authentication failed",
)


@dataclass(frozen=True)
class LoginControls:
    root: Page | Frame
    account: Locator
    password: Locator
    submit: Locator


def _build_parser() -> argparse.ArgumentParser:
    """构建命令行参数解析器，提供 --timeout-ms 选项。"""
    parser = argparse.ArgumentParser(
        description="使用系统环境变量登录禅道；浏览器固定以有头模式运行。"
    )
    parser.add_argument(
        "--timeout-ms",
        type=int,
        default=DEFAULT_TIMEOUT_MS,
        help="页面和控件操作超时时间，默认 30000 毫秒。",
    )
    return parser


def _read_environment() -> tuple[str, str, str] | None:
    """从环境变量读取并校验禅道登录凭据。"""
    required = ("ZENTAO_URL", "ZENTAO_ACCOUNT", "ZENTAO_PASSWORD")
    missing = [name for name in required if not os.environ.get(name, "").strip()]
    if missing:
        print(f"status=blocked reason=missing_environment_variables variables={','.join(missing)}")
        return None

    url = os.environ["ZENTAO_URL"].strip()
    parsed = urlsplit(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        print("status=blocked reason=invalid_zentao_url")
        return None

    return url, os.environ["ZENTAO_ACCOUNT"], os.environ["ZENTAO_PASSWORD"]


def _safe_location(url: str) -> str:
    """只保留 URL 的非敏感部分，避免输出 query、fragment 或 userinfo。"""

    parsed = urlsplit(url)
    host = parsed.hostname or "unknown-host"
    if parsed.port is not None:
        host = f"{host}:{parsed.port}"
    path = parsed.path or "/"
    return f"{parsed.scheme}://{host}{path}"


def _roots(page: Page) -> list[Page | Frame]:
    """返回页面主框架与全部子框架，供跨 iframe 探测遍历。"""
    return [page, *[frame for frame in page.frames if frame is not page.main_frame]]


def _visible(locator: Locator) -> bool:
    """安全判断元素是否可见且可操作，异常时视为不可用。"""
    try:
        return locator.is_visible() and locator.is_enabled()
    except PlaywrightError:
        return False


def _attribute_signature(element: Locator, attributes: tuple[str, ...]) -> str:
    """拼接元素指定属性的小写特征串，用于控件类型识别。"""
    values: list[str] = []
    for attribute in attributes:
        try:
            value = element.get_attribute(attribute)
        except PlaywrightError:
            value = None
        if value:
            values.append(value.lower())
    return " ".join(values)


def _score_account(element: Locator) -> int:
    """按账号语义关键词命中数为账号输入框候选打分。"""
    signature = _attribute_signature(
        element,
        ("type", "name", "id", "placeholder", "aria-label", "autocomplete"),
    )
    return sum(1 for keyword in ACCOUNT_KEYWORDS if keyword in signature)


def _score_submit(element: Locator) -> int:
    """按登录语义关键词命中数为提交按钮候选打分。"""
    signature = _attribute_signature(
        element,
        ("type", "name", "id", "aria-label", "title", "value"),
    )
    try:
        text = element.inner_text(timeout=500).lower()
    except PlaywrightError:
        text = ""
    signature = f"{signature} {text}"
    return sum(1 for keyword in LOGIN_KEYWORDS if keyword in signature)


def _choose_unique(candidates: list[tuple[int, Locator]], minimum_score: int) -> Locator | None:
    """从候选中选取唯一且达标的最高分元素，避免误选。"""
    if not candidates:
        return None
    highest = max(score for score, _ in candidates)
    best = [locator for score, locator in candidates if score == highest]
    if highest < minimum_score or len(best) != 1:
        return None
    return best[0]


def _discover_controls(page: Page) -> LoginControls | None:
    """从 DOM 探测并确认账号框、密码框与登录按钮三件套。"""
    for root in _roots(page):
        inputs = root.locator("input")
        visible_inputs: list[Locator] = []
        for index in range(inputs.count()):
            element = inputs.nth(index)
            if _visible(element):
                visible_inputs.append(element)

        password_indices = [
            index
            for index, element in enumerate(visible_inputs)
            if _attribute_signature(element, ("type",)) == "password"
        ]
        if len(password_indices) != 1:
            continue

        account_candidates = [
            (score, element)
            for index, element in enumerate(visible_inputs)
            if index != password_indices[0]
            and (_attribute_signature(element, ("type",)) or "text")
            in {"text", "email", "tel"}
            for score in [_score_account(element)]
        ]
        account = _choose_unique(account_candidates, minimum_score=1)
        if account is None:
            continue

        button_locator = root.locator(
            "button, input[type='submit'], input[type='button'], [role='button']"
        )
        submit_candidates = [
            (_score_submit(button_locator.nth(index)), button_locator.nth(index))
            for index in range(button_locator.count())
            if _visible(button_locator.nth(index))
        ]
        submit = _choose_unique(submit_candidates, minimum_score=1)
        if submit is not None:
            return LoginControls(
                root=root,
                account=account,
                password=visible_inputs[password_indices[0]],
                submit=submit,
            )
    return None


def _visible_body_text(page: Page) -> str:
    """聚合各框架可见正文文本，供关键字检测使用。"""
    chunks: list[str] = []
    for root in _roots(page):
        try:
            chunks.append(root.locator("body").inner_text(timeout=500).lower())
        except PlaywrightError:
            continue
    return " ".join(chunks)


def _has_challenge(page: Page) -> bool:
    """检测页面是否出现验证码或二次验证等挑战。"""
    body_text = _visible_body_text(page)
    if any(keyword in body_text for keyword in CHALLENGE_KEYWORDS):
        return True

    for root in _roots(page):
        inputs = root.locator("input")
        for index in range(inputs.count()):
            element = inputs.nth(index)
            if not _visible(element):
                continue
            signature = _attribute_signature(
                element, ("name", "id", "placeholder", "aria-label", "autocomplete")
            )
            if any(keyword in signature for keyword in CHALLENGE_KEYWORDS):
                return True
    return False


def _has_visible_password(page: Page) -> bool:
    """检测是否仍存在可见密码框，用于判断是否停留在登录页。"""
    for root in _roots(page):
        passwords = root.locator("input[type='password']")
        if any(_visible(passwords.nth(index)) for index in range(passwords.count())):
            return True
    return False


def _has_visible_login_button(page: Page) -> bool:
    """检测是否仍存在可见登录按钮，用于推断登录结果。"""
    for root in _roots(page):
        buttons = root.locator(
            "button, input[type='submit'], input[type='button'], [role='button']"
        )
        for index in range(buttons.count()):
            element = buttons.nth(index)
            if _visible(element) and _score_submit(element) >= 1:
                return True
    return False


def _login_succeeded(page: Page, initial_url: str) -> bool:
    """依据密码框消失、URL 变化与登录按钮消失综合判断登录是否成功。"""
    if _has_visible_password(page):
        return False

    # 保留查询参数供内部比较。ZenTao 常会在保留相同路径的情况下，
    # 将任务 URL 重定向到 /index.php；查询参数变化是可靠信号。
    # 该值不会被打印，因此凭据或 Token 不会通过此检查泄露。
    if page.url != initial_url:
        return True

    if not _has_visible_login_button(page):
        # 某些 ZenTao 部署会保留原任务 URL，且不会渲染稳定的退出/个人资料标记。
        # 密码输入框和登录语义控件消失，是当前可用的 DOM 证据，表示登录页已离开。
        return True
    return False


def _run(url: str, account: str, password: str, timeout_ms: int) -> int:
    """启动有头 Chromium 执行完整登录流程，并输出 status 与退出码。"""
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.set_default_timeout(timeout_ms)

        try:
            page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
            try:
                page.wait_for_load_state("networkidle", timeout=timeout_ms)
            except PlaywrightTimeoutError:
                # 长连接应用可能不会进入 networkidle；继续以已渲染 DOM 作为依据。
                pass

            if _has_challenge(page):
                print("status=blocked reason=verification_or_second_factor_detected")
                return 2

            controls = _discover_controls(page)
            if controls is None:
                print("status=blocked reason=login_controls_not_confirmed_from_dom")
                return 2

            initial_url = page.url
            controls.account.fill(account)
            controls.password.fill(password)
            controls.submit.click()

            try:
                page.wait_for_load_state("networkidle", timeout=timeout_ms)
            except PlaywrightTimeoutError:
                pass
            page.wait_for_timeout(500)

            if _has_challenge(page):
                print("status=blocked reason=verification_or_second_factor_detected")
                return 2
            if _login_succeeded(page, initial_url):
                print(f"status=passed location={_safe_location(page.url)}")
                return 0

            if any(marker in _visible_body_text(page) for marker in FAILURE_MARKERS):
                print("status=failed reason=login_rejected")
                return 1

            print("status=blocked reason=login_result_not_confirmed_from_dom")
            return 2
        except PlaywrightTimeoutError:
            print("status=blocked reason=page_or_control_timeout")
            return 2
        except PlaywrightError:
            print("status=blocked reason=playwright_operation_failed")
            return 2
        finally:
            context.close()
            browser.close()


def main(argv: list[str] | None = None) -> int:
    """脚本入口，解析参数与环境后调用 _run 并返回退出码。"""
    args = _build_parser().parse_args(argv)
    if args.timeout_ms <= 0:
        print("status=blocked reason=invalid_timeout")
        return 2

    environment = _read_environment()
    if environment is None:
        return 2
    return _run(*environment, timeout_ms=args.timeout_ms)


if __name__ == "__main__":
    sys.exit(main())

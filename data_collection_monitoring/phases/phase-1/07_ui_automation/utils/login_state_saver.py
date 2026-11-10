"""使用有头 Chromium 保存共享登录态。"""

from __future__ import annotations

import sys
import time
from dataclasses import dataclass
from pathlib import Path

from playwright.sync_api import BrowserContext, Page, Playwright, sync_playwright

ROOT = Path(__file__).resolve().parents[2]
UI_ROOT = ROOT / "07_ui_automation"
if str(UI_ROOT) not in sys.path:
    sys.path.insert(0, str(UI_ROOT))

from config.settings import ConfigurationError, Settings, load_settings
from pages.common.login_page import LoginPage


@dataclass(frozen=True)
class SaveLoginStateResult:
    status: str
    detail: str
    auth_state_path: Path | None = None


def _launch_context(playwright: Playwright, settings: Settings) -> BrowserContext:
    settings.browser_profile_dir.mkdir(parents=True, exist_ok=True)
    return playwright.chromium.launch_persistent_context(
        user_data_dir=str(settings.browser_profile_dir),
        headless=False,
        viewport={"width": 1440, "height": 900},
    )


def _wait_for_manual_verification(page: Page, settings: Settings) -> None:
    """保持浏览器可见，定时检测人工登录完成，不依赖 stdin。"""
    deadline = time.monotonic() + settings.auth_refresh_timeout_seconds
    last_url = page.url
    while time.monotonic() < deadline:
        if LoginPage(page, settings).is_authenticated():
            return
        try:
            page.wait_for_timeout(1000)
        except Exception as exc:
            raise RuntimeError(f"人工登录检测失败：{type(exc).__name__}: {exc}") from exc
        if page.url != last_url:
            last_url = page.url
    raise TimeoutError(f"等待人工登录或安全验证超时（{settings.auth_refresh_timeout_seconds} 秒）")


def save_login_state(settings: Settings | None = None) -> SaveLoginStateResult:
    """认证并原子更新共享 storage state；不会切换到无头模式。"""
    try:
        settings = settings or load_settings(ROOT, headless=False)
    except ConfigurationError as exc:
        return SaveLoginStateResult("blocked", str(exc))

    playwright = sync_playwright().start()
    context: BrowserContext | None = None
    try:
        context = _launch_context(playwright, settings)
        page = context.pages[0] if context.pages else context.new_page()
        page.goto(settings.portal_url, wait_until="domcontentloaded")
        try:
            LoginPage(page, settings).ensure_authenticated()
        except RuntimeError:
            _wait_for_manual_verification(page, settings)
            LoginPage(page, settings).assert_authenticated()

        settings.auth_state_path.parent.mkdir(parents=True, exist_ok=True)
        temporary = settings.auth_state_path.with_suffix(".json.tmp")
        context.storage_state(path=str(temporary))
        temporary.replace(settings.auth_state_path)
        return SaveLoginStateResult("success", "登录态已保存", settings.auth_state_path)
    except Exception as exc:
        return SaveLoginStateResult("blocked", f"登录态保存失败：{type(exc).__name__}: {exc}")
    finally:
        if context is not None:
            context.close()
        playwright.stop()


def main() -> int:
    result = save_login_state()
    output = result.detail
    if result.auth_state_path:
        output += f"；Auth state：{result.auth_state_path}"
    print(output, file=sys.stderr if result.status != "success" else sys.stdout)
    return 0 if result.status == "success" else 1


if __name__ == "__main__":
    raise SystemExit(main())

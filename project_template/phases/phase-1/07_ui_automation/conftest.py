"""跨模块共享的可视 Chromium 登录态。"""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path

import pytest
from playwright.sync_api import BrowserContext, Page, Playwright, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config.settings import ConfigurationError, load_settings
from pages.common.login_page import LoginPage


@pytest.fixture(scope="session")
def persistent_context() -> BrowserContext:
    """串行复用共享 Profile；不支持多个进程同时占用该目录。"""
    try:
        settings = load_settings(ROOT, headless=False)
    except ConfigurationError as exc:
        pytest.skip(f"blocked: {exc}")

    settings.browser_profile_dir.mkdir(parents=True, exist_ok=True)
    playwright = sync_playwright().start()
    context = _launch_context(playwright, settings.browser_profile_dir)
    try:
        yield context
    finally:
        context.close()
        playwright.stop()


def _launch_context(playwright: Playwright, profile_dir: Path) -> BrowserContext:
    """以可视模式启动持久化 Chromium，不在失败时切换无头模式。"""
    try:
        return playwright.chromium.launch_persistent_context(
            user_data_dir=str(profile_dir),
            headless=False,
            viewport={"width": 1440, "height": 900},
        )
    except Exception as exc:
        raise RuntimeError(f"blocked: 无法启动可视 Chromium 或共享 Profile 被占用：{exc}") from exc


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo[object]):
    """保存测试阶段结果，供阻塞保留浏览器现场使用。"""
    outcome = yield
    item.rep_call = outcome.get_result() if call.when == "call" else getattr(item, "rep_call", None)


@pytest.fixture
def page(request: pytest.FixtureRequest, persistent_context: BrowserContext) -> Page:
    """为任意模块提供复用登录态的页面。"""
    page = persistent_context.pages[0] if persistent_context.pages else persistent_context.new_page()
    try:
        settings = load_settings(ROOT, headless=False)
        page.goto(settings.portal_url, wait_until="domcontentloaded")
        LoginPage(page, settings).ensure_authenticated()
    except ConfigurationError as exc:
        pytest.skip(f"blocked: {exc}")
    yield page
    keep_open = os.getenv("UI_TEST_KEEP_BROWSER_OPEN_ON_BLOCKED", "0").lower() in {"1", "true", "yes"}
    failed = bool(getattr(getattr(request, "node", None), "rep_call", None) and request.node.rep_call.failed)
    if keep_open and failed:
        print("BLOCKED_BROWSER_OPEN: 浏览器现场已保留；按 Ctrl+C 结束 pytest。", flush=True)
        while True:
            time.sleep(1)
    if not page.is_closed():
        page.goto("about:blank")

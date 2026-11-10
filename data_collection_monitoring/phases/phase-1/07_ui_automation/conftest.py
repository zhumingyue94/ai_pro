"""跨模块共享的有头认证浏览器 Fixture。"""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path

import pytest
from playwright.sync_api import Browser, BrowserContext, Page, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config.settings import ConfigurationError, load_settings
from utils.auth_state import AuthBlockedError, ensure_authenticated_context


@pytest.fixture(scope="session")
def browser() -> Browser:
    """以有头模式启动共享浏览器；不可视启动不降级为无头。"""
    try:
        load_settings(ROOT, headless=False)
    except ConfigurationError as exc:
        pytest.skip(f"blocked: {exc}")
    playwright = sync_playwright().start()
    try:
        instance = playwright.chromium.launch(headless=False)
    except Exception as exc:
        playwright.stop()
        pytest.skip(f"blocked: 无法启动可视 Chromium：{exc}")
    yield instance
    instance.close()
    playwright.stop()


@pytest.fixture
def persistent_context(browser: Browser) -> BrowserContext:
    """为单条测试创建独立认证上下文，避免复用过期上下文。"""
    settings = load_settings(ROOT, headless=False)
    try:
        context, _ = ensure_authenticated_context(browser, settings)
    except AuthBlockedError as exc:
        pytest.skip(f"blocked: {exc}")
    yield context
    if not context.is_closed():
        context.close()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo[object]):
    """保存测试阶段结果，供阻塞保留浏览器现场使用。"""
    outcome = yield
    item.rep_call = outcome.get_result() if call.when == "call" else getattr(item, "rep_call", None)


@pytest.fixture
def page(request: pytest.FixtureRequest, persistent_context: BrowserContext) -> Page:
    """为任意模块提供经过认证的页面。"""
    page = persistent_context.pages[0] if persistent_context.pages else persistent_context.new_page()
    yield page
    keep_open = os.getenv("UI_TEST_KEEP_BROWSER_OPEN_ON_BLOCKED", "0").lower() in {"1", "true", "yes"}
    failed = bool(getattr(getattr(request, "node", None), "rep_call", None) and request.node.rep_call.failed)
    if keep_open and failed:
        print("BLOCKED_BROWSER_OPEN: 浏览器现场已保留；按 Ctrl+C 结束 pytest。", flush=True)
        while True:
            time.sleep(1)
    if not page.is_closed():
        page.goto("about:blank")

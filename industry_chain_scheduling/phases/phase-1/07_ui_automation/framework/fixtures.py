"""pytest 夹具：配置、浏览器、上下文、页面、证据目录与用例契约。

浏览器生命周期采用 session 级共享：context 内持有登录后的 cookie，
89 个用例通过 function 级的新 page 复用登录态，避免每条用例重复登录。
这是本项目不使用 pytest-playwright 原生 fixture 的核心原因。

headless 恒为 False（固定可视浏览器）；无法启动时记录 blocked，禁止切换无头模式。
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterator

import pytest
from playwright.sync_api import Page, sync_playwright

from config.settings import ConfigurationError, Settings, load_settings

from . import case_source, options, registry as registry_mod
from .orchestrator import get_orch

DEFAULT_TIMEOUT_MS = 15_000


@pytest.fixture(scope="session")
def settings(request) -> Settings:
    """加载 UI 自动化运行配置；headless 恒为 False。"""
    orch = get_orch(request.config)
    try:
        loaded = load_settings(registry_mod.ROOT, headless=options.HEADLESS)
    except ConfigurationError as exc:
        orch.config_error = f"configuration_error: {exc}"
        pytest.skip(f"UI 配置缺失，本次 RUN 全部记为 blocked：{exc}")
    orch.settings_snapshot = loaded.safe_environment
    return loaded


@pytest.fixture(scope="session")
def playwright_instance():
    """启动 Playwright 驱动，会话级复用。"""
    with sync_playwright() as instance:
        yield instance


@pytest.fixture(scope="session")
def browser(request, playwright_instance, settings):
    """以固定可视模式启动 Chromium；启动失败时记录阻塞原因而非降级为无头。"""
    orch = get_orch(request.config)
    if orch.dry_run or orch.collect_only or orch.self_test:
        yield None
        return
    try:
        launched = playwright_instance.chromium.launch(headless=options.HEADLESS)
    except Exception as exc:  # noqa: BLE001 - 启动失败必须转成 blocked 而非让会话崩溃
        orch.config_error = f"browser_launch_failed: {exc!r}"
        pytest.skip(f"无法启动可视浏览器，本次 RUN 全部记为 blocked：{exc}")
    orch.browser_started = True
    yield launched
    launched.close()
    orch.browser_closed = True


@pytest.fixture(scope="session")
def context(request, browser):
    """新建浏览器上下文并共享登录态；首个用例登录后 cookie 即写入此处。"""
    if browser is None:
        yield None
        return
    created = browser.new_context(ignore_https_errors=True)
    created.set_default_timeout(DEFAULT_TIMEOUT_MS)
    yield created
    created.close()


@pytest.fixture
def page(request, context) -> Iterator[Page]:
    """从共享上下文新建页面，用例结束后关闭，保证用例之间的页面状态隔离。"""
    if context is None:
        yield None
        return
    new_page = context.new_page()
    new_page.set_default_timeout(DEFAULT_TIMEOUT_MS)
    yield new_page
    new_page.close()


@pytest.fixture(scope="session")
def evidence_dir(request) -> Path:
    """返回本次 RUN 的截图目录；collect-only 时返回不落盘的兜底目录。"""
    orch = get_orch(request.config)
    if orch.screenshots_dir is not None:
        return orch.screenshots_dir
    fallback = registry_mod.AUTO_DIR / "reports" / ".collect_only_evidence"
    return fallback


@pytest.fixture
def case_meta(request) -> dict:
    """按当前测试函数反查注册表，构造用例断言契约。

    必需键为 case_id、zentao_case_id、check_id、assertion_scope；
    req_id、module_name、run_id、expected、steps、started_at 为向后兼容补充项，
    原有用例通过 ``.get()`` 访问，不受影响。
    """
    orch = get_orch(request.config)
    entry = registry_mod.load_registry().entry_for_item(request.node)
    if entry is None:
        pytest.skip(f"module_case_map.json 未登记该用例：{request.node.nodeid}")
    req_id = str(entry.get("req_id") or "")
    zentao_id = int(entry.get("zentao_case_id") or -1)
    local_case = case_source.load_testcases(req_id).get(zentao_id) or {}
    steps = local_case.get("steps") or []
    return {
        "case_id": entry.get("case_id"),
        "zentao_case_id": zentao_id,
        "title": local_case.get("title") or entry.get("title") or "",
        "check_id": entry.get("check_id"),
        "assertion_scope": entry.get("assertion_scope"),
        "req_id": req_id,
        "module_name": (entry.get("module") or {}).get("name") or "",
        "run_id": orch.run_id,
        "data_prefix": f"{options.TEST_DATA_PREFIX}{orch.run_id}_",
        "expected": "\n".join(str(step.get("expected", "")) for step in steps if isinstance(step, dict)),
        "steps": steps,
        "started_at": orch.started_at_of(request.node.nodeid),
    }

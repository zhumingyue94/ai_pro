"""业务无关的认证状态检查、刷新和上下文创建工具。"""

from __future__ import annotations

import subprocess
import sys
import time
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

from playwright.sync_api import Browser, BrowserContext, Page

from config.settings import Settings
from pages.common.login_page import LoginPage


class AuthBlockedError(RuntimeError):
    """认证环境不可用，应分类为 blocked。"""


@dataclass(frozen=True)
class AuthRefreshResult:
    status: str
    detail: str


@contextmanager
def refresh_lock(path: Path, timeout_seconds: int) -> Iterator[None]:
    """用独占文件创建实现跨进程刷新锁。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    deadline = time.monotonic() + timeout_seconds
    handle = None
    try:
        while handle is None:
            try:
                handle = path.open("x", encoding="utf-8")
            except FileExistsError:
                if time.monotonic() >= deadline:
                    raise AuthBlockedError("等待认证状态刷新锁超时")
                time.sleep(0.25)
        handle.write(str(time.time()))
        handle.close()
        yield
    finally:
        if handle is not None:
            path.unlink(missing_ok=True)


def is_authenticated(page: Page, settings: Settings) -> bool:
    """使用页面对象的配置化认证判定。"""
    login_page = LoginPage(page, settings)
    return login_page.is_authenticated()


def refresh_auth_state(settings: Settings) -> AuthRefreshResult:
    """通过项目注入的保存脚本刷新认证状态，不保存真实凭据到模板。"""
    lock_path = settings.auth_refresh_lock_path
    started_at = time.time()
    with refresh_lock(lock_path, settings.auth_refresh_timeout_seconds):
        if settings.auth_state_path.is_file() and settings.auth_state_path.stat().st_mtime >= started_at:
            return AuthRefreshResult("success", "已复用其他进程刚刚刷新的认证状态")
        command = [sys.executable, str(settings.login_state_saver_path)]
        try:
            completed = subprocess.run(
                command,
                cwd=str(settings.root),
                check=False,
                timeout=settings.auth_refresh_timeout_seconds,
                capture_output=True,
                text=True,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            return AuthRefreshResult("blocked", f"认证状态保存脚本不可用：{type(exc).__name__}: {exc}")
        if completed.returncode != 0:
            detail = (completed.stderr or completed.stdout or "认证状态保存脚本失败").strip()
            return AuthRefreshResult("blocked", detail)
        if not settings.auth_state_path.is_file():
            return AuthRefreshResult("blocked", "认证状态保存脚本未生成配置的状态文件")
        return AuthRefreshResult("success", "认证状态已刷新")


def create_context(browser: Browser, settings: Settings, video_dir: Path | None = None) -> BrowserContext:
    kwargs = {"storage_state": str(settings.auth_state_path), "viewport": {"width": 1440, "height": 900}}
    if video_dir is not None:
        kwargs["record_video_dir"] = str(video_dir)
    return browser.new_context(**kwargs)


def ensure_authenticated_context(
    browser: Browser,
    settings: Settings,
    video_dir: Path | None = None,
    old_context: BrowserContext | None = None,
) -> tuple[BrowserContext, Page]:
    """验证认证；失效时刷新并返回全新的 Context/Page。"""
    if not settings.auth_state_path.is_file():
        result = refresh_auth_state(settings)
        if result.status != "success":
            raise AuthBlockedError(result.detail)
    context = old_context or create_context(browser, settings, video_dir)
    page = context.pages[0] if context.pages else context.new_page()
    page.set_default_timeout(settings.auth_check_timeout_ms)
    try:
        page.goto(settings.portal_url, wait_until="domcontentloaded")
        if is_authenticated(page, settings):
            return context, page
    except Exception as exc:
        if old_context is None:
            context.close()
        raise AuthBlockedError(f"认证页面检查失败：{type(exc).__name__}: {exc}") from exc

    if old_context is not None:
        old_context.close()
    result = refresh_auth_state(settings)
    if result.status != "success":
        raise AuthBlockedError(result.detail)
    context = create_context(browser, settings, video_dir)
    page = context.new_page()
    page.goto(settings.portal_url, wait_until="domcontentloaded")
    if not is_authenticated(page, settings):
        context.close()
        raise AuthBlockedError("刷新认证状态后仍未通过认证检查")
    return context, page

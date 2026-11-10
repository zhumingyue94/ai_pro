"""跨模块认证状态检测、刷新和上下文重建。"""

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
                    raise AuthBlockedError("等待登录态刷新锁超时")
                time.sleep(0.25)
        handle.write(str(time.time()))
        handle.close()
        yield
    finally:
        if handle is not None:
            path.unlink(missing_ok=True)


def _capture_auth_diagnostics(page: Page, video_dir: Path | None, detail: str) -> None:
    """保存认证失败的最小诊断信息，不保存 Cookie 或 storage state。"""
    if video_dir is None:
        return
    run_dir = video_dir.parent
    screenshots = run_dir / "screenshots"
    screenshots.mkdir(parents=True, exist_ok=True)
    try:
        page.screenshot(path=str(screenshots / "authentication-failure.png"), full_page=True)
    except Exception:
        return


def is_authenticated(page: Page, settings: Settings) -> bool:
    """等待并检查认证页面，保留页面运行时错误而不静默吞掉。"""
    login_page = LoginPage(page, settings)
    try:
        login_page.wait_until_authenticated(settings.auth_check_timeout_ms)
    except Exception:
        if login_page.is_authenticated():
            return True
        raise
    return login_page.is_authenticated()


def _auth_state_is_fresh(settings: Settings, started_at: float) -> bool:
    """判断其他刷新进程是否已在本轮写入新的登录态文件。"""
    try:
        return settings.auth_state_path.is_file() and settings.auth_state_path.stat().st_mtime >= started_at
    except OSError:
        return False


def refresh_auth_state(settings: Settings) -> AuthRefreshResult:
    """通过唯一公共保存模块刷新登录态，并避免重复启动可视浏览器。"""
    lock_path = settings.auth_refresh_lock_path or settings.auth_state_path.with_suffix(".refresh.lock")
    refresh_started_at = time.time()
    with refresh_lock(lock_path, settings.auth_refresh_timeout_seconds):
        if _auth_state_is_fresh(settings, refresh_started_at):
            return AuthRefreshResult("success", "已复用其他进程刚刚刷新的登录态")
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
        except subprocess.TimeoutExpired:
            return AuthRefreshResult("blocked", "登录态保存脚本超时，人工验证未在规定时间内完成")
        except OSError as exc:
            return AuthRefreshResult("blocked", f"无法启动登录态保存脚本：{type(exc).__name__}: {exc}")
        if completed.returncode != 0:
            detail = (completed.stderr or completed.stdout or "登录态保存脚本失败").strip()
            return AuthRefreshResult("blocked", detail)
        if not settings.auth_state_path.is_file():
            return AuthRefreshResult("blocked", "登录态保存脚本未生成 auth-state.json")
        return AuthRefreshResult("success", "登录态已刷新")


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
    except Exception as exc:
        detail = f"认证页面加载异常：url={page.url}; error={type(exc).__name__}: {exc}"
        _capture_auth_diagnostics(page, video_dir, detail)
        if old_context is None:
            context.close()
        raise AuthBlockedError(detail) from exc
    try:
        if is_authenticated(page, settings):
            return context, page
    except Exception as exc:
        detail = f"认证检查异常：url={page.url}; title={page.title()!r}; error={type(exc).__name__}: {exc}"
        _capture_auth_diagnostics(page, video_dir, detail)
        raise AuthBlockedError(detail) from exc

    if old_context is not None:
        old_context.close()
    result = refresh_auth_state(settings)
    if result.status != "success":
        raise AuthBlockedError(result.detail)
    context = create_context(browser, settings, video_dir)
    page = context.new_page()
    page.set_default_timeout(settings.auth_check_timeout_ms)
    try:
        page.goto(settings.portal_url, wait_until="domcontentloaded")
    except Exception as exc:
        detail = f"刷新后认证页面加载异常：url={page.url}; error={type(exc).__name__}: {exc}"
        _capture_auth_diagnostics(page, video_dir, detail)
        context.close()
        raise AuthBlockedError(detail) from exc
    try:
        authenticated = is_authenticated(page, settings)
    except Exception as exc:
        detail = f"刷新后认证检查异常：url={page.url}; title={page.title()!r}; error={type(exc).__name__}: {exc}"
        _capture_auth_diagnostics(page, video_dir, detail)
        context.close()
        raise AuthBlockedError(detail) from exc
    if not authenticated:
        context.close()
        raise AuthBlockedError(f"刷新登录态后仍未通过认证检查：url={page.url}; title={page.title()!r}")
    return context, page

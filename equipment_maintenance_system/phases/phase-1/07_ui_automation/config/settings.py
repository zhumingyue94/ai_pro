"""UI 自动化运行配置模块。"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlsplit

import yaml
from dotenv import dotenv_values


REQUIRED_KEYS = ("UI_TEST_URL", "UI_TEST_USERNAME", "UI_TEST_PASSWORD")


class ConfigurationError(RuntimeError):
    """在浏览器启动前报告缺失或无效的运行配置。"""


@dataclass(frozen=True)
class Settings:
    """保存 UI 自动化运行时的非持久化配置。"""

    root: Path
    ui_test_url: str
    username: str
    password: str
    tenant: str
    portal_app_name: str
    portal_entry_path: str
    browser_profile_dir: Path
    auth_state_path: Path
    auth_refresh_lock_path: Path
    login_state_saver_path: Path
    login_path: str = "/login"
    authenticated_path: str = "/portal"
    login_button_name: str = "登录"
    app_card_selector: str = "button.portal-home__card"
    tenant_required: bool = False
    auth_check_timeout_ms: int = 20_000
    auth_refresh_timeout_seconds: int = 180
    headless: bool = False

    @property
    def portal_url(self) -> str:
        """返回去除末尾斜杠的测试环境地址。"""
        return self.ui_test_url.rstrip("/") + self.portal_entry_path

    @property
    def app_route(self) -> str:
        """返回项目通过页面适配器注入的业务路由。"""
        return ""

    @property
    def safe_environment(self) -> dict[str, str]:
        """返回不包含敏感值的环境摘要。"""
        parsed = urlsplit(self.ui_test_url)
        return {"base_host": parsed.netloc or "unresolved-host", "headless": str(self.headless).lower()}


def _find_env_file(start: Path) -> Path | None:
    """从 start 向上查找最近的 .env 文件。"""
    for candidate in (start, *start.parents):
        env = candidate / ".env"
        if env.is_file():
            return env
    return None


def _as_bool(value: object, default: bool = False) -> bool:
    if value is None or value == "":
        return default
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def load_settings(root: Path, *, headless: bool = False) -> Settings:
    """从 config.yaml 和环境变量读取运行配置。"""
    root = Path(root).resolve()
    env_path = _find_env_file(root)
    env_file = dotenv_values(env_path) if env_path else {}
    config = yaml.safe_load((root / "config.yaml").read_text(encoding="utf-8-sig")) or {}
    testcase = config.get("testcase") or {}
    ui_config = testcase.get("ui") or {}

    def value(key: str, default: str = "") -> str:
        return str(os.getenv(key) or env_file.get(key) or default).strip()

    tenant_required = _as_bool(value("UI_TEST_TENANT_REQUIRED", ui_config.get("tenant_required", False)))
    required = list(REQUIRED_KEYS) + (["UI_TEST_TENANT"] if tenant_required else [])
    missing = [key for key in required if not value(key)]
    if missing:
        raise ConfigurationError("缺少必需的 UI 运行变量：" + ", ".join(missing))

    runtime_dir = root / "07_ui_automation" / "data"
    profile = Path(value("UI_TEST_BROWSER_PROFILE_DIR")) if value("UI_TEST_BROWSER_PROFILE_DIR") else runtime_dir / "browser-profile"
    auth_state = Path(value("UI_TEST_AUTH_STATE_PATH")) if value("UI_TEST_AUTH_STATE_PATH") else runtime_dir / "auth-state.json"
    lock_path = Path(value("UI_TEST_AUTH_REFRESH_LOCK")) if value("UI_TEST_AUTH_REFRESH_LOCK") else auth_state.with_suffix(".refresh.lock")
    saver = Path(value("UI_TEST_AUTH_SAVER")) if value("UI_TEST_AUTH_SAVER") else root / "07_ui_automation" / "scripts" / "save_auth_state.py"
    entry_path = value("UI_TEST_PORTAL_ENTRY_PATH", str(testcase.get("portal_entry_path") or ""))
    if entry_path and not entry_path.startswith("/"):
        entry_path = "/" + entry_path
    return Settings(
        root=root,
        ui_test_url=value("UI_TEST_URL").rstrip("/"),
        username=value("UI_TEST_USERNAME"),
        password=value("UI_TEST_PASSWORD"),
        tenant=value("UI_TEST_TENANT"),
        portal_app_name=value("UI_TEST_PORTAL_APP_NAME", str(testcase.get("portal_app_name") or "")),
        portal_entry_path=entry_path,
        browser_profile_dir=profile,
        auth_state_path=auth_state,
        auth_refresh_lock_path=lock_path,
        login_state_saver_path=saver,
        login_path=value("UI_TEST_LOGIN_PATH", "/login"),
        authenticated_path=value("UI_TEST_AUTHENTICATED_PATH", "/portal"),
        login_button_name=value("UI_TEST_LOGIN_BUTTON_NAME", "登录"),
        app_card_selector=value("UI_TEST_APP_CARD_SELECTOR", "button.portal-home__card"),
        tenant_required=tenant_required,
        auth_check_timeout_ms=int(value("UI_TEST_AUTH_CHECK_TIMEOUT_MS", "20000")),
        auth_refresh_timeout_seconds=int(value("UI_TEST_AUTH_REFRESH_TIMEOUT_SECONDS", "180")),
        headless=headless,
    )

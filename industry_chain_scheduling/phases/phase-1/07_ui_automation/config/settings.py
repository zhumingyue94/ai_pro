"""UI 自动化运行配置模块：从 config.yaml 与环境变量加载门户地址、路由与凭据来源，并提供 Settings 访问属性。

"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlsplit

from dotenv import dotenv_values


REQUIRED_KEYS = ("UI_TEST_URL", "UI_TEST_USERNAME", "UI_TEST_PASSWORD", "UI_TEST_TENANT")


class ConfigurationError(RuntimeError):
    """Raised before browser startup when required runtime settings are absent."""


@dataclass(frozen=True)
class Settings:
    root: Path
    ui_test_url: str
    username: str
    password: str
    tenant: str
    headless: bool = False

    @property
    def portal_url(self) -> str:
        """返回去除末尾斜杠的 UI 测试地址。"""
        return self.ui_test_url.rstrip("/")

    @property
    def app_route(self) -> str:
        """返回目标制定页面的应用路由路径。"""
        return "/biopark-apm/apm/scheduling/goal"

    @property
    def safe_environment(self) -> dict[str, str]:
        """返回不含敏感凭据的环境摘要，供日志与报告使用。"""
        parsed = urlsplit(self.portal_url)
        return {"base_host": parsed.netloc or "unresolved-host", "headless": str(self.headless).lower()}


def load_settings(root: Path, *, headless: bool = False) -> Settings:
    """
    从 config.yaml 与环境变量加载运行配置，校验必需项后返回冻结的 Settings 实例。
    """
    env_file = dotenv_values(root / ".env")

    def value(key: str) -> str:
        """按优先级读取环境变量再回退到 .env 的配置值，并去除首尾空白。"""
        return (os.getenv(key) or env_file.get(key) or "").strip()

    missing = [key for key in REQUIRED_KEYS if not value(key)]
    if missing:
        raise ConfigurationError("missing required UI runtime variables: " + ", ".join(missing))
    return Settings(
        root=root,
        ui_test_url=value("UI_TEST_URL"),
        username=value("UI_TEST_USERNAME"),
        password=value("UI_TEST_PASSWORD"),
        tenant=value("UI_TEST_TENANT"),
        headless=headless,
    )

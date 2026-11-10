"""UI 自动化运行配置模块。"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlsplit

import yaml
from dotenv import dotenv_values


REQUIRED_KEYS = ("UI_TEST_URL", "UI_TEST_USERNAME", "UI_TEST_PASSWORD", "UI_TEST_TENANT")


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
    headless: bool = False

    @property
    def portal_url(self) -> str:
        """返回去除末尾斜杠的测试环境地址。"""
        return self.ui_test_url.rstrip("/")

    @property
    def app_route(self) -> str:
        """返回待项目确认的业务应用路由。"""
        return ""

    @property
    def safe_environment(self) -> dict[str, str]:
        """返回不包含敏感值的环境摘要。"""
        parsed = urlsplit(self.portal_url)
        return {"base_host": parsed.netloc or "unresolved-host", "headless": str(self.headless).lower()}


def _find_env_file(start: Path) -> Path | None:
    """从 start 向上查找最近的 .env 文件（一期/二期共用项目根目录配置）。"""
    for candidate in (start, *start.parents):
        env = candidate / ".env"
        if env.is_file():
            return env
    return None


def load_settings(root: Path, *, headless: bool = False) -> Settings:
    """从 config.yaml 和环境变量读取运行配置。"""
    env_path = _find_env_file(root)
    env_file = dotenv_values(env_path) if env_path else {}
    config = yaml.safe_load((root / "config.yaml").read_text(encoding="utf-8-sig")) or {}
    portal_app_name = str((config.get("testcase") or {}).get("portal_app_name") or "").strip()

    def value(key: str) -> str:
        """按环境变量优先、.env 回退的顺序读取配置。"""
        return (os.getenv(key) or env_file.get(key) or "").strip()

    missing = [key for key in REQUIRED_KEYS if not value(key)]
    if missing:
        raise ConfigurationError("缺少必需的 UI 运行变量：" + ", ".join(missing))
    return Settings(
        root=root,
        ui_test_url=value("UI_TEST_URL"),
        username=value("UI_TEST_USERNAME"),
        password=value("UI_TEST_PASSWORD"),
        tenant=value("UI_TEST_TENANT"),
        portal_app_name=portal_app_name,
        headless=headless,
    )

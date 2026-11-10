"""唯一注册表读取：module_case_map.json。

注册表是禅道用例 ID 到测试函数、页面对象和数据契约的**唯一**映射来源，
本模块只做只读访问，并在进程内惰性解析一次（原实现在 conftest 导入时即读取
673KB JSON，导致 ``--collect-only`` 也要付出解析代价）。
"""

from __future__ import annotations

import importlib.util
import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

# 一期根目录：framework/registry.py -> parents[0]=framework, [1]=07_ui_automation, [2]=一期
ROOT = Path(__file__).resolve().parents[2]
AUTO_DIR = ROOT / "07_ui_automation"
REGISTRY_PATH = ROOT / "module_case_map.json"

# 历史修复过的映射条目（禅道用例 ID），仅用于 selection.yaml 的 fixed_mapping_count 统计。
# 这些 ID 来自 06_zentao_sync 阶段对既有映射的纠正记录，非本次自动化判定依据。
FIXED_MAPPING_IDS: frozenset[int] = frozenset(
    {
        47486, 47487, 47489, 47501, 47508, 47509,
        47556, 47558, 47565, 47566, 47567, 47568, 47569, 47571,
    }
)


@dataclass(frozen=True)
class Registry:
    """注册表的只读快照，含按 handler 与按函数名后缀建立的两级索引。"""

    path: Path
    document: dict
    cases: tuple[dict, ...]
    by_handler: dict[str, dict]
    by_func_suffix: dict[str, dict]

    @property
    def summary(self) -> dict:
        """返回注册表的 summary 段落，缺失时返回空字典。"""
        return self.document.get("summary") or {}

    @property
    def pending_registry_count(self) -> int:
        """返回 summary 中声明的未登记用例数。"""
        return int(self.summary.get("pending_registry", 0) or 0)

    def entry_for_item(self, item) -> dict | None:
        """按『模块点分路径:函数名』反查用例条目；未命中再回退函数名后缀匹配。"""
        key = f"{getattr(item.module, '__name__', '')}:{item.name}"
        return self.by_handler.get(key) or self.by_func_suffix.get(item.name)

    def handler_importable(self, entry: dict) -> bool:
        """判断 handler 指向的模块文件是否存在；不做 import，避免导入副作用。"""
        handler = entry.get("handler") or ""
        module_name = handler.split(":", 1)[0] if ":" in handler else handler
        if not module_name:
            return False
        try:
            return importlib.util.find_spec(module_name) is not None
        except (ImportError, ValueError, ModuleNotFoundError):
            return False


def _build_index(cases: list[dict]) -> tuple[dict[str, dict], dict[str, dict]]:
    """构建 handler 精确索引与函数名后缀索引；后缀冲突时以首个为准并记录。"""
    by_handler: dict[str, dict] = {}
    by_suffix: dict[str, dict] = {}
    for entry in cases:
        handler = entry.get("handler")
        if isinstance(handler, str) and ":" in handler:
            by_handler.setdefault(handler, entry)
            by_suffix.setdefault(handler.rsplit(":", 1)[-1], entry)
    return by_handler, by_suffix


@lru_cache(maxsize=1)
def load_registry() -> Registry:
    """惰性加载并解析注册表，进程内只解析一次。"""
    if not REGISTRY_PATH.is_file():
        raise FileNotFoundError(f"REGISTRY_NOT_FOUND: {REGISTRY_PATH}")
    document: dict[str, Any] = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    cases = tuple(document.get("cases") or [])
    by_handler, by_suffix = _build_index(list(cases))
    return Registry(
        path=REGISTRY_PATH,
        document=document,
        cases=cases,
        by_handler=by_handler,
        by_func_suffix=by_suffix,
    )


def is_framework_item(item, registry: Registry | None = None) -> bool:
    """判断一个 pytest 条目是否属于本框架（注册表中存在对应映射条目）。"""
    reg = registry or load_registry()
    return reg.entry_for_item(item) is not None


def module_name_of(entry: dict) -> str:
    """返回注册表条目所属模块名，缺失时返回 unknown。"""
    return str((entry.get("module") or {}).get("name") or "unknown")

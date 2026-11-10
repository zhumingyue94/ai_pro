"""docstring 覆盖自检：AST 扫描 Python 文件，报告缺少 docstring 的函数与类。

项目 AGENTS.md 硬性要求：仓库内所有 Python 函数（``def``，含模块级函数与类方法）
必须提供 docstring，无 docstring 的函数视为未达标。

运行：``python scripts/check_docstrings.py``
      ``python scripts/check_docstrings.py --all``（额外扫描 pages/ 与 tests/）
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# 默认只扫描本次重构新增或改动的文件；--all 追加既有业务代码。
DEFAULT_TARGETS = ("framework", "conftest.py", "scripts")
EXTRA_TARGETS = ("config", "pages", "tests")
SKIP_NAMES = {"__init__"}


def iter_python_files(targets: tuple[str, ...]) -> list[Path]:
    """按目标收集待扫描的 Python 文件，跳过缓存目录。"""
    files: list[Path] = []
    for target in targets:
        path = ROOT / target
        if path.is_file() and path.suffix == ".py":
            files.append(path)
            continue
        if not path.is_dir():
            continue
        files.extend(
            item
            for item in path.rglob("*.py")
            if "__pycache__" not in item.parts and "reports" not in item.parts
        )
    return sorted(set(files))


def missing_docstrings(path: Path) -> list[str]:
    """返回文件中缺少 docstring 的函数/类/模块的限定名列表。"""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except SyntaxError as exc:
        return [f"<syntax-error> {exc}"]
    problems: list[str] = []
    if ast.get_docstring(tree) is None:
        problems.append("<module>")
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name in SKIP_NAMES:
                continue
            if ast.get_docstring(node) is None:
                problems.append(f"{node.name} (行 {node.lineno})")
        elif isinstance(node, ast.ClassDef):
            if ast.get_docstring(node) is None:
                problems.append(f"class {node.name} (行 {node.lineno})")
    return problems


def main() -> int:
    """扫描并打印缺失 docstring 的清单，全部达标返回 0。"""
    targets = DEFAULT_TARGETS + (EXTRA_TARGETS if "--all" in sys.argv else ())
    files = iter_python_files(targets)
    total = 0
    reported = 0
    for file in files:
        problems = missing_docstrings(file)
        total += 1
        if problems:
            reported += 1
            relative = file.relative_to(ROOT).as_posix()
            print(f"MISSING {relative}")
            for item in problems:
                print(f"    - {item}")
    print(f"扫描 {total} 个文件，缺失 {reported} 个文件")
    return 1 if reported else 0


if __name__ == "__main__":
    raise SystemExit(main())

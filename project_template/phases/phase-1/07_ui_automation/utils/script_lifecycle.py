"""独立测试脚本的静态校验和安全落盘工具。"""

from __future__ import annotations

import ast
import os
import py_compile
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class ScriptCheck:
    path: Path
    valid: bool
    errors: tuple[str, ...] = field(default_factory=tuple)


def validate_script(
    path: Path,
    case_id: str,
    *,
    forbidden_tokens: Iterable[str] = (),
    required_tokens: Iterable[str] = (),
) -> ScriptCheck:
    """校验脚本语法、独立入口、步骤断言结构和禁止依赖。"""
    path = Path(path)
    errors: list[str] = []
    if not path.is_file():
        return ScriptCheck(path, False, (f"脚本不存在：{path}",))
    source = path.read_text(encoding="utf-8")
    if not source.strip():
        return ScriptCheck(path, False, ("脚本为空",))
    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError as exc:
        return ScriptCheck(path, False, (f"语法错误：{exc}",))
    if case_id not in source:
        errors.append(f"缺少 case_id：{case_id}")
    names = {node.name for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}
    if "run_case" not in names:
        errors.append("缺少 run_case() 入口")
    if "main" not in names:
        errors.append("缺少 main() 入口")
    if "__main__" not in source:
        errors.append("缺少直接执行入口")
    if not any(isinstance(node, ast.Assert) for node in ast.walk(tree)) and "expect(" not in source:
        errors.append("缺少业务断言")
    if "CASE_STEPS" not in source:
        errors.append("缺少 CASE_STEPS")
    if "CASE_ASSERTIONS" not in source:
        errors.append("缺少 CASE_ASSERTIONS")
    for token in (*forbidden_tokens,):
        if token in source:
            errors.append(f"包含禁止依赖：{token}")
    for token in required_tokens:
        if token not in source:
            errors.append(f"缺少必需结构：{token}")
    return ScriptCheck(path, not errors, tuple(errors))


def syntax_check(path: Path) -> None:
    """执行 Python 编译检查，不导入或运行脚本。"""
    py_compile.compile(str(path), doraise=True)


def stage_script(content: str, destination: Path, case_id: str, **kwargs: Iterable[str]) -> ScriptCheck:
    """将候选脚本写入同目录临时文件并完成静态校验。"""
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{case_id}.", suffix=".py.tmp", dir=destination.parent)
    staged = Path(temp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        check = validate_script(staged, case_id, **kwargs)
        if not check.valid:
            staged.unlink(missing_ok=True)
            return ScriptCheck(destination, False, check.errors)
        syntax_check(staged)
        return ScriptCheck(staged, True)
    except Exception as exc:  # noqa: BLE001
        staged.unlink(missing_ok=True)
        return ScriptCheck(destination, False, (f"候选脚本检查失败：{type(exc).__name__}: {exc}",))


def commit_script(staged: Path, destination: Path, *, allow_replace: bool = False) -> Path:
    """将已校验候选脚本写入最终路径，默认拒绝覆盖已有文件。"""
    staged = Path(staged)
    destination = Path(destination)
    if not staged.is_file():
        raise FileNotFoundError(staged)
    if destination.exists() and not allow_replace:
        raise FileExistsError(f"目标脚本已存在，拒绝覆盖：{destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    os.replace(staged, destination)
    return destination

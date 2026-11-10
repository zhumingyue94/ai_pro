"""独立用例脚本的静态校验、临时写入和原子落盘工具。"""

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


SCRIPT_REUSE_REASONS = {
    "SCRIPT_MISSING",
    "SCRIPT_EMPTY",
    "CASE_ID_MISMATCH",
    "CASE_VERSION_MISMATCH",
    "STEP_ASSERTION_MISMATCH",
    "DEPENDENCY_INVALID",
    "SYNTAX_ERROR",
    "DIRECT_ENTRY_INVALID",
    "BUSINESS_EXECUTION_FAILED",
    "REVERIFICATION_FAILED",
    "EVIDENCE_INCOMPLETE",
    "RESULT_SCHEMA_INVALID",
    "SCRIPT_STALE",
}


def _tree(path: Path) -> tuple[ast.AST | None, list[str]]:
    errors: list[str] = []
    if not path.is_file():
        return None, [f"脚本不存在：{path}"]
    if not path.read_text(encoding="utf-8").strip():
        return None, ["脚本为空"]
    try:
        return ast.parse(path.read_text(encoding="utf-8"), filename=str(path)), errors
    except SyntaxError as exc:
        return None, [f"语法错误：{exc}"]


def validate_script(path: Path, case_id: str, *, required_tokens: Iterable[str] = (), expected_steps: Iterable[str] = (), expected_assertions: Iterable[str] = ()) -> ScriptCheck:
    """校验脚本可独立启动且没有依赖批量 runner。"""
    path = Path(path)
    tree, errors = _tree(path)
    if tree is None:
        return ScriptCheck(path, False, tuple(errors))
    source = path.read_text(encoding="utf-8")
    if case_id not in source:
        errors.append(f"缺少 case_id：{case_id}")
    if "runner.run_req002" in source or "run_req002" in source and "runner" in source:
        errors.append("独立脚本不得依赖 runner/run_req002.py")
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
        errors.append("缺少原始用例步骤 CASE_STEPS")
    if "CASE_ASSERTIONS" not in source:
        errors.append("缺少用例预期断言 CASE_ASSERTIONS")
    weak_assertions = (">= 0", "<= -1", "in (0, -1)", "or True", "and True")
    if any(token in source for token in weak_assertions):
        errors.append("存在缺乏业务约束力的弱断言")
    for token in required_tokens:
        if token not in source:
            errors.append(f"缺少必需结构：{token}")
    for step in expected_steps:
        if step and step not in source:
            errors.append(f"缺少用例步骤：{step}")
    for assertion in expected_assertions:
        if assertion and assertion not in source:
            errors.append(f"缺少用例断言：{assertion}")
    return ScriptCheck(path, not errors, tuple(errors))


def syntax_check(path: Path) -> None:
    """执行 Python 编译检查，不导入或运行脚本。"""
    py_compile.compile(str(path), doraise=True)


def stage_script(content: str, destination: Path, case_id: str, *, required_tokens: Iterable[str] = (), expected_steps: Iterable[str] = (), expected_assertions: Iterable[str] = ()) -> ScriptCheck:
    """将候选脚本写入同目录临时文件并完成静态校验。"""
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{case_id}.", suffix=".py.tmp", dir=destination.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        staged = Path(temp_name)
        check = validate_script(staged, case_id, required_tokens=required_tokens, expected_steps=expected_steps, expected_assertions=expected_assertions)
        if not check.valid:
            Path(temp_name).unlink(missing_ok=True)
            return ScriptCheck(destination, False, check.errors)
        syntax_check(staged)
        return ScriptCheck(staged, True)
    except Exception as exc:  # noqa: BLE001
        Path(temp_name).unlink(missing_ok=True)
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

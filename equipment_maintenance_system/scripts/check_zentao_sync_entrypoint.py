"""检查项目级禅道同步脚本是否绕过公共入口。"""

from __future__ import annotations

import argparse
import ast
from pathlib import Path


FORBIDDEN_TEXT = (
    "zentao.cmd",
    "zentao.js",
    "shutil.which(\"zentao\")",
    "run_zentao_cli",
    "testcase create",
    "testcase update",
    "testcase delete",
    "'moudule'",
    '"moudule"',
)
def project_files(root: Path) -> list[Path]:
    """返回项目同步目录中的 Python 文件。"""
    return sorted(root.glob("projects/**/06_zentao_sync/**/*.py"))


def check_file(path: Path) -> list[str]:
    """检查单个项目同步脚本的旁路调用和明显载荷字段。"""
    text = path.read_text(encoding="utf-8-sig")
    if path.parts[-1] == "_common.py" and "project-level ZenTao CLI is disabled" in text:
        return []
    findings = [f"{path}: forbidden text: {token}" for token in FORBIDDEN_TEXT if token in text]
    try:
        ast.parse(text, filename=str(path))
    except SyntaxError as exc:
        findings.append(f"{path}: syntax error: {exc}")
    return findings


def main() -> int:
    """执行项目级禅道同步旁路检查。"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    findings = [finding for path in project_files(args.root) for finding in check_file(path)]
    if findings:
        print("\n".join(findings))
        return 1
    print("zentao_sync_entrypoint_check: passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

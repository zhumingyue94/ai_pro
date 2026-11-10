"""从纯净一期模板创建新的 QA 项目。"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
import tempfile
from pathlib import Path


PROJECT_NAME_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9_-]*$")


def workspace_root(script_path: Path | None = None) -> Path:
    """根据脚本位置返回仓库工作区根目录。"""
    current_script = (script_path or Path(__file__)).resolve()
    return current_script.parent.parent


def validate_project_name(project_name: str) -> str:
    """校验并返回安全的英文项目目录名。"""
    if not PROJECT_NAME_PATTERN.fullmatch(project_name):
        raise ValueError(
            "项目名称必须以英文字母开头，且只能包含英文字母、数字、下划线或连字符"
        )
    return project_name


def create_project(
    project_name: str,
    projects_dir: Path | None = None,
    template_dir: Path | None = None,
) -> Path:
    """复制一期模板创建项目，并将配置中的项目名称替换为实际名称。"""
    name = validate_project_name(project_name)
    root = workspace_root()
    target_root = (projects_dir or root / "projects").resolve()
    source = (template_dir or root / "projects" / "project_template" / "phase-1").resolve()
    target = target_root / name
    if not source.is_dir():
        raise FileNotFoundError(f"一期模板不存在：{source}")
    if target.exists():
        raise FileExistsError(f"项目目录已存在，拒绝覆盖：{target}")

    target_root.mkdir(parents=True, exist_ok=True)
    staging_root = Path(tempfile.mkdtemp(prefix=f".{name}.", dir=target_root))
    staging_phase = staging_root / "phase-1"
    try:
        shutil.copytree(source, staging_phase)
        config_path = staging_phase / "config.yaml"
        config_text = config_path.read_text(encoding="utf-8")
        config_path.write_text(
            config_text.replace("<PROJECT_NAME>", name), encoding="utf-8"
        )
        if target.exists():
            raise FileExistsError(f"项目目录已存在，拒绝覆盖：{target}")
        staging_root.replace(target)
    except Exception:
        shutil.rmtree(staging_root, ignore_errors=True)
        raise
    return target


def build_parser() -> argparse.ArgumentParser:
    """构建项目创建脚本的命令行解析器。"""
    parser = argparse.ArgumentParser(
        description="从一期模板创建一个新的 QA 项目（默认位于 projects/）。"
    )
    parser.add_argument("project_name", help="英文项目目录名，例如 biopark_breeding")
    parser.add_argument(
        "--projects-dir",
        type=Path,
        help="项目父目录，默认使用工作区 projects/",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """解析参数、创建项目并输出结果。"""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        target = create_project(args.project_name, args.projects_dir)
    except (FileExistsError, FileNotFoundError, ValueError, OSError) as error:
        parser.error(str(error))
    print(f"项目创建成功：{target}")
    print(f"默认阶段目录：{target / 'phase-1'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

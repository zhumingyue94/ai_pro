"""新建项目脚本的单元测试。"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.create_project import create_project


class CreateProjectTests(unittest.TestCase):
    """验证新建项目脚本的核心行为。"""

    def make_template(self, root: Path) -> Path:
        """创建最小一期模板用于测试。"""
        template = root / "template" / "phase-1"
        template.mkdir(parents=True)
        (template / "config.yaml").write_text(
            'project:\n  name: "<PROJECT_NAME>"\n', encoding="utf-8"
        )
        (template / "marker.txt").write_text("phase one", encoding="utf-8")
        return template

    def test_creates_only_phase_one_and_replaces_name(self) -> None:
        """成功创建时只生成一期目录并替换项目名称。"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = create_project(
                "demo_project", root / "projects", self.make_template(root)
            )
            self.assertEqual(target, (root / "projects" / "demo_project").resolve())
            self.assertTrue((target / "phase-1" / "marker.txt").is_file())
            self.assertFalse((target / "phase-2").exists())
            config = (target / "phase-1" / "config.yaml").read_text(encoding="utf-8")
            self.assertIn('name: "demo_project"', config)
            self.assertNotIn("<PROJECT_NAME>", config)

    def test_rejects_invalid_name(self) -> None:
        """非法项目名不得创建目录。"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with self.assertRaises(ValueError):
                create_project("../bad", root / "projects", self.make_template(root))

    def test_rejects_existing_project(self) -> None:
        """目标项目已存在时不得覆盖。"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            projects = root / "projects"
            existing = projects / "existing_project"
            existing.mkdir(parents=True)
            marker = existing / "keep.txt"
            marker.write_text("keep", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                create_project("existing_project", projects, self.make_template(root))
            self.assertEqual(marker.read_text(encoding="utf-8"), "keep")

    def test_failed_staging_does_not_leave_new_target(self) -> None:
        """暂存阶段失败时不得留下半成品目标目录。"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            projects = root / "projects"
            template = self.make_template(root)
            (template / "config.yaml").unlink()
            with self.assertRaises(FileNotFoundError):
                create_project("failed_project", projects, template)
            self.assertFalse((projects / "failed_project").exists())

    def test_existing_target_remains_untouched_after_rejection(self) -> None:
        """目标目录已存在时拒绝操作且保留原文件。"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            projects = root / "projects"
            existing = projects / "race_project"
            existing.mkdir(parents=True)
            marker = existing / "keep.txt"
            marker.write_text("keep", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                create_project("race_project", projects, self.make_template(root))
            self.assertEqual(marker.read_text(encoding="utf-8"), "keep")


if __name__ == "__main__":
    unittest.main()

"""独立脚本生命周期的覆盖保护测试。"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from .script_lifecycle import commit_script


class ScriptLifecycleTests(unittest.TestCase):
    def test_commit_rejects_existing_destination_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            staged = root / "candidate.py"
            destination = root / "existing.py"
            staged.write_text("candidate", encoding="utf-8")
            destination.write_text("original", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                commit_script(staged, destination)
            self.assertEqual(destination.read_text(encoding="utf-8"), "original")
            self.assertTrue(staged.exists())

    def test_commit_can_replace_only_when_explicitly_allowed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            staged = root / "candidate.py"
            destination = root / "existing.py"
            staged.write_text("candidate", encoding="utf-8")
            destination.write_text("original", encoding="utf-8")
            commit_script(staged, destination, allow_replace=True)
            self.assertEqual(destination.read_text(encoding="utf-8"), "candidate")
            self.assertFalse(staged.exists())


if __name__ == "__main__":
    unittest.main()

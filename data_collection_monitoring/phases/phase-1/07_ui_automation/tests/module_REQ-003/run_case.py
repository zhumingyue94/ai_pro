"""REQ-003 单条用例执行入口；不负责批量执行。"""
from __future__ import annotations

import argparse
import runpy
from pathlib import Path

CASES = [
    "TC-REQ-003-005",
    "TC-REQ-003-016",
    "TC-REQ-003-017",
    "TC-REQ-003-020",
    "TC-REQ-003-039",
    "TC-REQ-003-040",
]


def run_case(case_id: str) -> None:
    """在当前进程中启动指定独立脚本。"""
    if case_id not in CASES:
        raise ValueError(f"不支持的用例：{case_id}")
    runpy.run_path(str(Path(__file__).with_name(f"{case_id}.py")), run_name="__main__")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("case_id", choices=CASES)
    args = parser.parse_args()
    run_case(args.case_id)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

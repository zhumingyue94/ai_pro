"""REQ-004 单条用例入口；不执行批量入口。"""
from __future__ import annotations
import argparse
import runpy
from pathlib import Path

CASES = ["TC-REQ-004-009", "TC-REQ-004-016", "TC-REQ-004-020", "TC-REQ-004-022", "TC-REQ-004-023", "TC-REQ-004-024", "TC-REQ-004-025", "TC-REQ-004-026", "TC-REQ-004-027", "TC-REQ-004-028"]

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("case_id", choices=CASES)
    case_id = parser.parse_args().case_id
    runpy.run_path(str(Path(__file__).with_name(f"{case_id}.py")), run_name="__main__")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

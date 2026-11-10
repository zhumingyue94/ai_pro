"""通过公共禅道入口执行产业链测试用例更新。"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from _common import ROOT, all_tc_cases, load_config, write_operation_log


PUBLIC_ENTRYPOINT = ROOT.parents[2] / "scripts" / "zentao_create_testcase.py"
MODULE_FILE = ROOT / "01_requirements" / "模块拆分清单.md"
MODULE_TREE = ROOT / "01_requirements" / "禅道模块id.md"
REGISTRY = ROOT / "module_case_map.json"


def run_shared_entrypoint(case_ids: set[str] | None, *, dry_run: bool) -> dict:
    """调用公共同步入口并返回结构化结果。"""
    config = load_config()
    req = ""
    cases = all_tc_cases()
    if case_ids:
        cases = [case for case in cases if str(case.get("id")) in case_ids]
    if not cases:
        raise RuntimeError("no testcase matched the requested IDs")
    req = str(cases[0].get("_req_id") or "")
    source = Path(str(cases[0]["_source_path"]))
    review = ROOT / "05_case_review" / f"REV_CASE_{req}.yaml"
    if not review.is_file():
        raise RuntimeError(f"review file missing: {review}")
    module_id = next(
        int(item.get("module", {}).get("id"))
        for item in json.loads(REGISTRY.read_text(encoding="utf-8-sig")).get("cases", [])
        if str(item.get("case_id")) in {str(case.get("id")) for case in cases} and item.get("module", {}).get("id")
    )
    args = [
        sys.executable,
        str(PUBLIC_ENTRYPOINT),
        "--project", str(ROOT),
        "--review", str(review),
        "--testcases", str(source),
        "--module-file", str(MODULE_FILE),
        "--module-tree", str(MODULE_TREE),
        "--registry", str(REGISTRY),
        "--product-id", str(config.get("zentao_product_id")),
        "--module-id", str(module_id),
        "--limit", str(len(cases)),
    ]
    if case_ids:
        args.extend(["--case-ids", ",".join(sorted(case_ids))])
    if dry_run:
        args.append("--dry-run")
    completed = subprocess.run(args, cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or completed.stdout.strip())
    return json.loads(completed.stdout)


def main() -> int:
    """按参数选择用例，通过公共入口执行或生成 dry-run 结果。"""
    parser = argparse.ArgumentParser(description="按公共入口检查或更新禅道用例")
    parser.add_argument("--req")
    parser.add_argument("--ids", help="逗号分隔的本地禅道数字用例 ID")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    selected_remote_ids = {int(value) for value in (args.ids or "").split(",") if value.strip().isdigit()}
    cases = [case for case in all_tc_cases(args.req) if not selected_remote_ids or case.get("zentao_case_id") in selected_remote_ids]
    case_ids = {str(case.get("id")) for case in cases if case.get("id")}
    result = run_shared_entrypoint(case_ids or None, dry_run=args.dry_run)
    records = result.get("records", [])
    log_path = write_operation_log("update_zentao_from_tc", records, status="dry_run" if args.dry_run else "completed")
    print(json.dumps({"status": result.get("status"), "cases": len(records), "operation_log": log_path.relative_to(ROOT).as_posix()}, ensure_ascii=False))
    return 0 if result.get("status") in {"validated", "dry_run"} else 2


if __name__ == "__main__":
    raise SystemExit(main())

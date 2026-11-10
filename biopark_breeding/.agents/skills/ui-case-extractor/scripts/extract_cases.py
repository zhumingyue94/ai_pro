#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ui-case-extractor — 提取本次 UI 自动化执行的用例清单为 testcase.csv。

在 <root>/07_ui_automation/reports/ 下新建 RUN_{时间戳}/，生成 testcase.csv
（10 列：用例编号、所属模块、用例函数名称、标题、前置条件、预期、步骤、
结果、错误原因、截图路径），用例按 zentao_case_id 升序预填。

独立于 pytest：不依赖 conftest 的 collection，仅用于按需预览/导出某次执行的用例清单。
执行结果回填（failed/error/blocked 等）由 07_ui_automation/tests/conftest.py 负责，
本脚本的「结果/错误原因/截图路径」列在提取阶段留空（auto:no 除外）。

数据源（只读）：
- <root>/module_case_map.json  —— entry: case_id/req_id/module.name/zentao_case_id/handler/title
- <root>/04_testcases/TC_{req_id}.yaml —— ycase: id/title/preconditions/steps[{action,expected}]/auto/zentao_case_id

用法示例：
  python extract_cases.py --module "{业务维度}管理"
  python extract_cases.py --req REQ-xxx
  python extract_cases.py --case TC-xxx-07 TC-xxx-09
  python extract_cases.py --handler tests.modules.master_data.test_slaughter_line
  python extract_cases.py --module "{业务维度}管理" --out D:/tmp/myrun
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.stderr.write(
        "缺少 PyYAML，请使用含 yaml 的 venv 运行，例如：\n"
        '  C:/Users/zhumi/.workbuddy/binaries/python/envs/ui_auto/Scripts/python.exe extract_cases.py\n'
    )
    raise

# 10 列（顺序固定，与 conftest.py 的 testcase.csv 一致）
FIELDNAMES = [
    "用例编号",
    "所属模块",
    "用例函数名称",
    "标题",
    "前置条件",
    "预期",
    "步骤",
    "结果",
    "错误原因",
    "截图路径",
]

_MAP_FILE = "module_case_map.json"
_YAML_CACHE: Dict[str, Dict[int, dict]] = {}


# ---------------------------------------------------------------- 定位项目根
def find_root(explicit: Optional[str]) -> Path:
    """返回项目根（含 module_case_map.json）。显式 root 优先，否则从 cwd 向上搜索。"""
    if explicit:
        root = Path(explicit).resolve()
        if not (root / _MAP_FILE).exists():
            sys.exit(f"[ui-case-extractor] 错误：{root / _MAP_FILE} 不存在，请检查 --root")
        return root
    cwd = Path.cwd().resolve()
    for parent in [cwd, *cwd.parents]:
        if (parent / _MAP_FILE).exists():
            return parent
    sys.exit(
        f"[ui-case-extractor] 错误：从 {cwd} 向上未找到 {_MAP_FILE}，"
        "请用 --root 显式指定项目根"
    )


# ---------------------------------------------------------------- 数据加载
def load_map(root: Path) -> List[dict]:
    """读 module_case_map.json 的顶层 cases 列表。"""
    with open(root / _MAP_FILE, encoding="utf-8") as f:
        data = json.load(f)
    cases = data.get("cases", data) if isinstance(data, dict) else data
    if not isinstance(cases, list):
        sys.exit("[ui-case-extractor] 错误：module_case_map.json 中未找到 cases 列表")
    return cases


def load_yaml_cases(root: Path, req_id: str) -> Dict[int, dict]:
    """读取 04_testcases/TC_{req_id}.yaml，按 zentao_case_id 索引用例。"""
    if req_id in _YAML_CACHE:
        return _YAML_CACHE[req_id]
    yaml_path = root / "04_testcases" / f"TC_{req_id}.yaml"
    if not yaml_path.exists():
        sys.exit(f"[ui-case-extractor] 错误：{yaml_path} 不存在")
    with open(yaml_path, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    cases = data.get("cases") or []
    by_zid = {}
    for c in cases:
        zid = c.get("zentao_case_id")
        if zid is not None:
            by_zid[int(zid)] = c
    _YAML_CACHE[req_id] = by_zid
    return by_zid


# ---------------------------------------------------------------- 选择器
def select_entries(entries: List[dict], args: argparse.Namespace) -> List[dict]:
    """按 --req / --module / --case / --handler 过滤 entry；选择器可组合（并集取交集）。"""
    selected = list(entries)
    if args.req:
        reqs = set(args.req)
        selected = [e for e in selected if e.get("req_id") in reqs]
    if args.module:
        mods = set(args.module)
        selected = [
            e
            for e in selected
            if e.get("module", {}).get("name") in mods
            or any(m in (e.get("module", {}).get("path") or "") for m in mods)
        ]
    if args.case:
        cases = set(args.case)
        selected = [e for e in selected if e.get("case_id") in cases]
    if args.handler:
        hdls = tuple(args.handler)
        selected = [
            e for e in selected if (e.get("handler") or "").startswith(hdls)
        ]
    return selected


# ---------------------------------------------------------------- 行构建
def _join_numbered(seq: Optional[List]) -> str:
    """多行合并为 Excel 单元格内换行："1. xxx\n2. yyy"。"""
    if not seq:
        return ""
    return "\n".join(f"{i + 1}. {item}" for i, item in enumerate(seq))


def _func_name(handler: Optional[str]) -> str:
    """从 handler（模块路径:函数名）取函数名；无 handler 返回空串。"""
    if not handler or ":" not in handler:
        return ""
    return handler.rsplit(":", 1)[-1]


def build_row(entry: dict, ycase: Optional[dict]) -> dict:
    """拼一行 10 列。ycase 缺失时回退到 entry.title。"""
    steps = (ycase or {}).get("steps") or []
    auto = (ycase or {}).get("auto", "auto")
    is_no = auto == "no"
    is_pending = entry.get("mapping_status") != "registered"
    return {
        "用例编号": entry.get("case_id", ""),
        "所属模块": (entry.get("module") or {}).get("name", ""),
        "用例函数名称": _func_name(entry.get("handler")),
        "标题": ((ycase or {}).get("title") or entry.get("title") or ""),
        "前置条件": _join_numbered((ycase or {}).get("preconditions")),
        "预期": _join_numbered([s.get("expected", "") for s in steps]),
        "步骤": _join_numbered([s.get("action", "") for s in steps]),
        "结果": "excluded" if (is_no or is_pending) else "",
        "错误原因": (
            "mapping_status: pending_registry，未完成禅道回读，不执行"
            if is_pending
            else "automation: no，按规则 excluded 不执行"
            if is_no
            else ""
        ),
        "截图路径": "",
    }


# ---------------------------------------------------------------- 主流程
def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="提取本次 UI 自动化执行的用例清单为 reports/RUN_{时间戳}/testcase.csv"
    )
    parser.add_argument("--root", help="项目根（含 module_case_map.json）；缺省自动向上搜索")
    parser.add_argument("--req", nargs="+", help="按需求筛选，如 --req REQ-xxx")
    parser.add_argument("--module", nargs="+", help="按模块名筛选，如 --module {业务维度}管理")
    parser.add_argument("--case", nargs="+", help="按用例编号筛选，如 --case TC-xxx-07 TC-xxx-09")
    parser.add_argument(
        "--handler",
        nargs="+",
        help="按 handler 前缀筛选（测试文件模块路径），如 --handler tests.modules.master_data.test_slaughter_line",
    )
    parser.add_argument("--out", help="覆盖输出目录（默认 <root>/07_ui_automation/reports/RUN_{ts}）")
    args = parser.parse_args(argv)

    if not (args.req or args.module or args.case or args.handler):
        parser.error("至少指定一个选择器：--req / --module / --case / --handler")

    root = find_root(args.root)
    entries = load_map(root)
    selected = select_entries(entries, args)

    if not selected:
        sys.exit("[ui-case-extractor] 未匹配到任何用例，请检查选择器参数")

    # 按 zentao_case_id 升序
    selected.sort(key=lambda e: (e.get("zentao_case_id") is None, e.get("zentao_case_id") or 0))

    # 按 req_id 批量加载 YAML（缓存）
    req_ids = sorted({e.get("req_id") for e in selected if e.get("req_id")})
    yaml_pool = {rid: load_yaml_cases(root, rid) for rid in req_ids}

    rows = []
    for e in selected:
        ycase = yaml_pool.get(e.get("req_id"), {}).get(int(e.get("zentao_case_id") or 0))
        rows.append(build_row(e, ycase))

    # 输出目录：RUN_{时间戳}/ + screenshots/
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    if args.out:
        out_dir = Path(args.out).resolve()
    else:
        out_dir = root / "07_ui_automation" / "reports" / f"RUN_{ts}"
    (out_dir / "screenshots").mkdir(parents=True, exist_ok=True)

    csv_path = out_dir / "testcase.csv"
    with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)

    print(f"[ui-case-extractor] 共提取 {len(rows)} 条用例")
    print(f"[ui-case-extractor] 输出: {csv_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

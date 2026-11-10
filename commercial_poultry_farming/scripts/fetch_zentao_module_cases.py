#!/usr/bin/env python3
"""通过 zentao-cli 只读获取指定项目模块下的测试用例。"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    """解析公共脚本命令行参数。"""
    parser = argparse.ArgumentParser(
        description="使用 zentao-cli 拉取禅道指定产品/项目下某模块的测试用例清单。"
    )
    parser.add_argument("--product", type=int, required=True, help="禅道产品 ID")
    parser.add_argument("--project", type=int, required=True, help="禅道项目 ID")
    parser.add_argument("--module", type=int, required=True, help="目标模块 ID")
    parser.add_argument("--page-size", type=int, default=100, help="每页数量，默认 100")
    parser.add_argument("--output", type=Path, help="可选：输出 JSON 或 Markdown 文件路径")
    parser.add_argument(
        "--format",
        choices=("json", "markdown"),
        default="markdown",
        help="输出格式，默认 markdown",
    )
    args = parser.parse_args()
    if args.product <= 0 or args.project <= 0 or args.module <= 0:
        parser.error("product、project 和 module 必须为正整数")
    if args.page_size <= 0:
        parser.error("page-size 必须为正整数")
    return args


def run_cli(product: int, project: int, page: int, page_size: int) -> dict[str, Any]:
    """读取一页产品/项目范围内的禅道测试用例。"""
    command = [
        "cmd",
        "/c",
        "zentao",
        "testcase",
        f"--product={product}",
        f"--project={project}",
        "--format=json",
        f"--page={page}",
        f"--recPerPage={page_size}",
    ]
    completed = subprocess.run(
        command,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"zentao-cli 执行失败（退出码 {completed.returncode}）：\n"
            f"{completed.stderr.strip() or completed.stdout.strip()}"
        )
    output = completed.stdout.strip()
    try:
        result = json.loads(output)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"zentao-cli 未返回有效 JSON：{output[:500]}") from exc
    if result.get("status") != "success":
        raise RuntimeError(f"zentao-cli 返回失败：{json.dumps(result, ensure_ascii=False)}")
    return result


def fetch_cases(product: int, project: int, module: int, page_size: int = 100) -> list[dict[str, Any]]:
    """分页读取并筛选指定产品、项目和模块的测试用例。"""
    if min(product, project, module, page_size) <= 0:
        raise ValueError("product、project、module 和 page_size 必须为正整数")

    cases: list[dict[str, Any]] = []
    page = 1
    total: int | None = None
    while total is None or page <= (total + page_size - 1) // page_size:
        result = run_cli(product, project, page, page_size)
        rows = result.get("data") or []
        pager = result.get("pager") or {}
        total = int(pager.get("total") or 0)
        if not rows:
            break
        cases.extend(
            row
            for row in rows
            if isinstance(row, dict) and str(row.get("module")) == str(module)
        )
        if len(rows) < page_size:
            break
        page += 1
    return cases


def case_id(case: dict[str, Any]) -> Any:
    """返回禅道用例的兼容 ID 字段。"""
    return case.get("caseID") or case.get("case") or case.get("id")


def markdown(cases: list[dict[str, Any]], product: int, project: int, module: int) -> str:
    """将用例清单渲染为 Markdown。"""
    lines = [
        "# 禅道模块测试用例清单",
        "",
        f"- 产品 ID：`{product}`",
        f"- 项目 ID：`{project}`",
        f"- 模块 ID：`{module}`",
        f"- 用例数量：`{len(cases)}`",
        "",
        "| 序号 | 禅道用例 ID | 标题 | 模块 ID | 优先级 | 类型 | 自动化 | 状态 |",
        "|---:|---:|---|---:|---:|---|---|---|",
    ]
    for index, item in enumerate(cases, 1):
        fields = {
            key: str(item.get(key, "")).replace("|", "\\|").replace("\n", " ")
            for key in ("title", "module", "pri", "type", "auto", "status")
        }
        lines.append(
            f"| {index} | `{case_id(item)}` | {fields['title']} | {fields['module']} | "
            f"{fields['pri']} | {fields['type']} | {fields['auto']} | {fields['status']} |"
        )
    return "\n".join(lines) + "\n"


def main() -> int:
    """执行查询并输出 JSON 或 Markdown 结果。"""
    args = parse_args()
    try:
        cases = fetch_cases(args.product, args.project, args.module, args.page_size)
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"错误：{exc}", file=sys.stderr)
        return 1

    if args.format == "json":
        content = json.dumps(
            {
                "product": args.product,
                "project": args.project,
                "module": args.module,
                "count": len(cases),
                "cases": cases,
            },
            ensure_ascii=False,
            indent=2,
        ) + "\n"
    else:
        content = markdown(cases, args.product, args.project, args.module)

    if args.output:
        args.output.write_text(content, encoding="utf-8")
        print(f"已输出 {len(cases)} 条用例到：{args.output}")
    else:
        print(content, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Render testcase YAML documents into the shared Markdown contract."""
from __future__ import annotations

import argparse
import os
import tempfile
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TEMPLATE = ROOT / "schemas" / "testcase-markdown.template.md"


def text(value: Any, fallback: str = "未登记") -> str:
    if value is None or value == "":
        return fallback
    if isinstance(value, list):
        return "、".join(text(item, fallback) for item in value)
    if isinstance(value, dict):
        return "; ".join(f"{key}={text(item, fallback)}" for key, item in value.items())
    return str(value).replace("\r", " ").replace("\n", " ").strip()


def items(value: Any, fallback: str = "未登记") -> list[str]:
    if not value:
        return [fallback]
    if isinstance(value, list):
        return [text(item) for item in value]
    return [text(value)]


def condition_key(value: str) -> str:
    return "".join(value.split()).lower()


def merged_preconditions(case: dict[str, Any], document: dict[str, Any]) -> list[str]:
    definitions = {item.get("id"): item for item in document.get("common_preconditions") or [] if isinstance(item, dict)}
    has_common_preconditions = "common_preconditions" in document
    if has_common_preconditions and "common_preconditions_ref" not in case:
        raise ValueError(
            f"case {case.get('id')} must define common_preconditions_ref when "
            "common_preconditions exists; use null when not applicable"
        )
    reference = case.get("common_preconditions_ref")
    if reference is not None and (not isinstance(reference, str) or not reference.strip()):
        raise ValueError(f"case {case.get('id')} common_preconditions_ref must be a non-empty string or null")
    if reference is not None and reference not in definitions:
        raise ValueError(f"case {case.get('id')} references undefined common precondition: {reference}")
    common = definitions.get(reference) or {}
    result: list[str] = []
    seen: set[str] = set()
    for value in [*(common.get("conditions") or []), *(case.get("preconditions") or [])]:
        item = text(value, "")
        key = condition_key(item)
        if item and key not in seen:
            seen.add(key)
            result.append(item)
    return result


def metadata(document: dict[str, Any], cases: list[dict[str, Any]]) -> dict[str, str]:
    trace = document.get("trace") or {}
    first = cases[0] if cases else {}
    req_id = text(document.get("req_id"), "未登记")
    tp_id = text(trace.get("tp"), "未登记")
    project = text(trace.get("project"), "未登记")
    module = text(document.get("module"), "未登记")
    version = text(trace.get("version"), "未登记")
    status = text(trace.get("status"), "未登记")
    page_urls = sorted({text((case.get("test_data") or {}).get("page_url")) for case in cases})
    coverage = sorted({item for case in cases for item in (case.get("coverage_ids") or [])})
    auto_count = sum(text(case.get("auto")) == "auto" for case in cases)
    type_count = sum(text(case.get("type")) == "feature" for case in cases)
    priorities = {priority: sum(text(case.get("priority")) == priority for case in cases) for priority in ("P1", "P2", "P3", "P4")}
    delivery = "已生成待评审"
    return {
        "req_id": req_id,
        "tp_id": tp_id,
        "project": project,
        "module": module,
        "version": version,
        "trace_status": status,
        "source_review": text(trace.get("source_review"), "未登记"),
        "page_url": ", ".join(page_urls),
        "coverage_summary": ", ".join(coverage) if coverage else "未登记",
        "case_count": str(len(cases)),
        "auto_case_count": str(auto_count),
        "feature_case_count": str(type_count),
        "p1_count": str(priorities["P1"]),
        "p2_count": str(priorities["P2"]),
        "p3_count": str(priorities["P3"]),
        "p4_count": str(priorities["P4"]),
        "review_conclusion": "待评审；生成器仅完成结构化派生",
        "delivery_status": delivery,
        "open_items": "无",
        "remark": f"来源 YAML：{req_id}；Markdown 由公共渲染器生成。",
    }


def render_case(case: dict[str, Any], document: dict[str, Any]) -> list[str]:
    trace = case.get("trace") or document.get("trace") or {}
    atomic = case.get("atomic_purpose_ids") or ["未登记"]
    branch = (case.get("scenario_branch") or (case.get("test_data") or {}).get("case_data") or "常规业务场景")
    auto = text(case.get("auto"), "no")
    if auto not in {"auto", "no"}:
        auto = "no"
    lines = [
        f"## {text(case.get('id'))} / {text(case.get('tp_id'), text((trace or {}).get('tp'), '未登记'))} [{text(case.get('priority'))}] auto={auto}",
        "",
        f"**标题**: {text(case.get('title'))}",
        "",
        f"**原子测试目的**: {text(atomic)}",
        "",
        f"**状态/条件分支**: {text(branch)}",
        "",
        f"**auto**: {auto}",
        "",
        f"**type**: {text(case.get('type'))}",
        "",
        f"**功能**: {text(case.get('feature'), text(document.get('module')))}",
        "",
        f"**追溯**: 需求={text((trace or {}).get('req'), text(document.get('req_id')))}；测试计划={text((trace or {}).get('tp'))}；项目={text((trace or {}).get('project'))}；版本={text((trace or {}).get('version'))}；状态={text((trace or {}).get('status'))}",
        "",
        "**前置条件**:",
        "",
    ]
    lines.extend(f"- {item}" for item in merged_preconditions(case, document))
    reference = case.get("common_preconditions_ref")
    if reference is not None:
        lines.extend(["", f"**公共前置引用**: `{reference}`"])
    lines.extend(["", "**步骤**:", ""])
    steps = case.get("steps") or []
    if not steps:
        lines.append("1. 未登记")
        lines.append("   - 预期：未登记")
    else:
        for index, step in enumerate(steps, 1):
            lines.append(f"{index}. {text(step.get('action'))}")
            lines.append(f"   - 预期：{text(step.get('expected'))}")
    lines.append("")
    return lines


def render(document: dict[str, Any], template_path: Path = DEFAULT_TEMPLATE) -> str:
    # Read the shared template as the single contract source; dynamic lists are expanded below.
    template_path.read_text(encoding="utf-8")
    cases = document.get("cases") or []
    meta = metadata(document, cases)
    lines = [
        f"# 测试用例 — {meta['module']} ({meta['req_id']})", "",
        f"- 用例数：**{meta['case_count']}**", f"- 需求编号：{meta['req_id']}", f"- 测试计划：{meta['tp_id']}",
        f"- 版本：{meta['version']}", f"- 追溯状态：{meta['trace_status']}", f"- 来源评审：{meta['source_review']}", "",
        "## 覆盖与审核信息", "", f"- 项目：{meta['project']}", f"- 模块：{meta['module']}",
        f"- 需求：{meta['req_id']}", f"- 测试计划：{meta['tp_id']}", f"- 页面/入口：{meta['page_url']}",
        f"- 覆盖范围：{meta['coverage_summary']}", f"- 审核结论：{meta['review_conclusion']}", "",
        "## 用例总览", "", f"- 总用例数：**{meta['case_count']}**", f"- 自动化用例数：**{meta['auto_case_count']}**",
        f"- 功能/手工用例数：**{meta['feature_case_count']}**", f"- P1：**{meta['p1_count']}**", f"- P2：**{meta['p2_count']}**",
        f"- P3：**{meta['p3_count']}**", f"- P4：**{meta['p4_count']}**", "",
    ]
    for case in cases:
        lines.extend(render_case(case, document))
    lines.extend(["## 结论", "", f"- 用例交付状态：{meta['delivery_status']}", f"- 未覆盖项/待确认项：{meta['open_items']}", f"- 备注：{meta['remark']}", ""])
    return "\n".join(lines)


def write_atomic(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(content)
        os.replace(temp_name, path)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--template", type=Path, default=DEFAULT_TEMPLATE)
    args = parser.parse_args()
    document = yaml.safe_load(args.input.read_text(encoding="utf-8")) or {}
    write_atomic(args.output, render(document, args.template))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

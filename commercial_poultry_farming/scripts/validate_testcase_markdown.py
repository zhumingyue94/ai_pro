"""Validate testcase Markdown against the shared contract and its source YAML."""
from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Any

import yaml

from validate_case_atomicity import validate as validate_atomicity

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "schemas" / "testcase-markdown.template.md"
REQUIRED_SECTIONS = ("## 覆盖与审核信息", "## 用例总览", "## 结论")
ALLOWED_CASE_TYPES = {
    "interface",
    "feature",
    "install",
    "config",
    "performance",
    "security",
}
CASE_RE = re.compile(r"^## (TC-\S+) / (\S+) \[(P[1-4])\] auto=(\S+)$", re.MULTILINE)
PLACEHOLDER_RE = re.compile(r"\{(?:module|req_id|tp_id|version|trace_status|source_review|project|page_url|coverage_summary|review_conclusion|case_count|auto_case_count|feature_case_count|p1_count|p2_count|p3_count|p4_count|delivery_status|open_items|remark|case_id|tp_case_id|priority|auto|title|atomic_purpose_id|scenario_branch|type|feature|precondition_1|precondition_2|action_1|action_2|expected_result_1|expected_result_2)\}")


def value(value: Any, default: str = "未登记") -> str:
    if value is None or value == "":
        return default
    return str(value)


def normalized(raw_value: Any, default: str = "未登记") -> str:
    if isinstance(raw_value, list):
        return "、".join(normalized(item) for item in raw_value)
    return re.sub(r"\s+", " ", value(raw_value, default)).strip()


def case_block(markdown: str, case_id: str) -> str:
    start = markdown.find(f"## {case_id} /")
    if start < 0:
        return ""
    next_start = markdown.find("\n## ", start + 1)
    return markdown[start: next_start if next_start >= 0 else len(markdown)]


def validate(markdown: str, document: dict[str, Any], template_path: Path = TEMPLATE):
    errors: list[str] = []
    template = template_path.read_text(encoding="utf-8")
    for section in REQUIRED_SECTIONS:
        if section not in markdown:
            errors.append(f"缺少必需章节：{section}")
    if "CASE INDEX" in markdown:
        errors.append("禁止使用旧版 CASE INDEX 索引格式")
    if PLACEHOLDER_RE.search(markdown):
        errors.append("Markdown 仍包含模板占位符")
    if "<!-- 复制以上“单条用例”区块" in markdown:
        errors.append("Markdown 仍包含模板说明注释")
    if "## 覆盖与审核信息" in template and "## 覆盖与审核信息" not in markdown:
        errors.append("未按公共模板生成覆盖与审核信息")

    yaml_cases = document.get("cases") or []
    has_common_preconditions = "common_preconditions" in document
    errors.extend(validate_atomicity(document))
    markdown_cases = CASE_RE.findall(markdown)
    if len(markdown_cases) != len(yaml_cases):
        errors.append(f"用例数量不一致：YAML={len(yaml_cases)}，Markdown={len(markdown_cases)}")
    yaml_by_id = {value(case.get("id")): case for case in yaml_cases}
    markdown_ids = [item[0] for item in markdown_cases]
    if len(markdown_ids) != len(set(markdown_ids)):
        errors.append("Markdown 用例编号重复")
    if set(markdown_ids) != set(yaml_by_id):
        errors.append(f"YAML/Markdown 用例编号不一致：YAML={sorted(yaml_by_id)}，Markdown={sorted(markdown_ids)}")

    for case_id, _tp_case_id, priority, auto in markdown_cases:
        case = yaml_by_id.get(case_id)
        if not case:
            continue
        if priority != value(case.get("priority")):
            errors.append(f"{case_id} 优先级不一致：YAML={case.get('priority')}，Markdown={priority}")
        case_type = case.get("type")
        if not isinstance(case_type, str) or case_type not in ALLOWED_CASE_TYPES:
            errors.append(
                f"{case_id} type非法：{case_type!r}；允许值为 {sorted(ALLOWED_CASE_TYPES)!r}"
            )
        expected_auto = value(case.get("auto"), "no")
        if expected_auto != "auto":
            expected_auto = "no"
        if auto != expected_auto:
            errors.append(f"{case_id} 自动化标记不一致：YAML={case.get('auto')}，Markdown={auto}")
        block = case_block(markdown, case_id)
        if has_common_preconditions and "common_preconditions_ref" not in case:
            errors.append(f"{case_id} 缺少字段：common_preconditions_ref")
        for marker in ("**标题**:", "**原子测试目的**:", "**状态/条件分支**:", "**前置条件**:", "**步骤**:"):
            if marker not in block:
                errors.append(f"{case_id} 缺少字段：{marker}")
        fields = {
            "标题": r"\*\*标题\*\*: (.+)",
            "原子测试目的": r"\*\*原子测试目的\*\*: (.+)",
            "type": r"\*\*type\*\*: (.+)",
            "追溯": r"\*\*追溯\*\*: (.+)",
        }
        expected_fields = {
            "标题": normalized(case.get("title")),
            "原子测试目的": normalized(case.get("atomic_purpose_ids")),
            "type": normalized(case.get("type")),
        }
        for field, pattern in fields.items():
            match = re.search(pattern, block)
            if not match:
                errors.append(f"{case_id} 缺少字段：{field}")
            elif field in expected_fields and normalized(match.group(1)) != expected_fields[field]:
                errors.append(f"{case_id} {field}不一致：YAML={expected_fields[field]}，Markdown={normalized(match.group(1))}")
        trace = case.get("trace") or document.get("trace") or {}
        trace_match = re.search(fields["追溯"], block)
        if trace_match:
            trace_text = normalized(trace_match.group(1))
            for label, expected in (("需求", trace.get("req", document.get("req_id"))), ("测试计划", trace.get("tp")), ("项目", trace.get("project")), ("版本", trace.get("version")), ("状态", trace.get("status"))):
                if f"{label}={normalized(expected)}" not in trace_text:
                    errors.append(f"{case_id} 追溯字段不一致：缺少 {label}={normalized(expected)}")
        expected_steps = case.get("steps") or []
        actual_steps = re.findall(r"^(\d+)\. (.+?)\n\s+- 预期：(.+)$", block, re.MULTILINE)
        if len(actual_steps) != len(expected_steps):
            errors.append(f"{case_id} 步骤数量不一致：YAML={len(expected_steps)}，Markdown={len(actual_steps)}")
        for index, step in enumerate(expected_steps):
            if index >= len(actual_steps):
                break
            _, action, expected = actual_steps[index]
            if normalized(action) != normalized(step.get("action")):
                errors.append(f"{case_id} 第{index + 1}步 action 不一致")
            if normalized(expected) != normalized(step.get("expected")):
                errors.append(f"{case_id} 第{index + 1}步 expected 不一致")
        for key in ("title", "type", "priority"):
            if case.get(key) in (None, ""):
                errors.append(f"{case_id} YAML 缺少字段：{key}")

    expected_count = len(yaml_cases)
    overview = re.search(r"## 用例总览(?P<body>.*?)(?=\n## )", markdown, re.DOTALL)
    if overview:
        body = overview.group("body")
        count_match = re.search(r"总用例数：\*\*(\d+)\*\*", body)
        if not count_match or int(count_match.group(1)) != expected_count:
            errors.append("用例总览总数与 YAML 不一致")
        auto_count = sum(value(case.get("auto"), "no") == "auto" for case in yaml_cases)
        auto_match = re.search(r"自动化用例数：\*\*(\d+)\*\*", body)
        if not auto_match or int(auto_match.group(1)) != auto_count:
            errors.append("用例总览自动化数量与 YAML 不一致")
        for priority in ("P1", "P2", "P3", "P4"):
            expected = sum(value(case.get("priority")) == priority for case in yaml_cases)
            match = re.search(rf"{priority}：\*\*(\d+)\*\*", body)
            if not match or int(match.group(1)) != expected:
                errors.append(f"用例总览 {priority} 数量与 YAML 不一致")
        feature_count = sum(value(case.get("type")) == "feature" for case in yaml_cases)
        feature_match = re.search(r"功能/手工用例数：\*\*(\d+)\*\*", body)
        if not feature_match or int(feature_match.group(1)) != feature_count:
            errors.append("用例总览功能/手工数量与 YAML 不一致")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("yaml_file", type=Path)
    parser.add_argument("markdown_file", type=Path)
    parser.add_argument("--template", type=Path, default=TEMPLATE)
    args = parser.parse_args()
    document = yaml.safe_load(args.yaml_file.read_text(encoding="utf-8")) or {}
    errors = validate(args.markdown_file.read_text(encoding="utf-8"), document, args.template)
    if errors:
        print("Markdown contract validation failed:")
        print("\n".join(f"- {error}" for error in errors))
        return 1
    print(f"PASS: {args.markdown_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

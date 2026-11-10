#!/usr/bin/env python3
"""校验符合公共 testcase YAML/Markdown 模板的测试用例文档。"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCHEMA_DIR = ROOT / "schemas"
REQUIRED_DOCUMENT_KEYS = {"req_id", "module", "trace", "cases"}
REQUIRED_CASE_KEYS = {
    "id", "coverage_ids", "atomic_purpose_ids", "title", "type", "auto",
    "priority", "feature", "preconditions", "steps",
}
OPTIONAL_CASE_KEYS = {
    "tp_id", "plan_item_ids", "scenario_branch", "common_preconditions_ref",
    "test_data", "trace", "ui_source",
}
ALLOWED_CASE_TYPES = {"interface", "feature", "install", "config", "performance", "security"}
ALLOWED_AUTO_VALUES = {"auto", "no"}
ALLOWED_PRIORITIES = {"P1", "P2", "P3", "P4"}


class ValidationError(Exception):
    pass


def fail(message: str) -> None:
    raise ValidationError(message)


def require_mapping(value: Any, path: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        fail(f"{path} must be a mapping")
    return value


def non_empty_string(value: Any, path: str) -> None:
    if not isinstance(value, str) or not value.strip():
        fail(f"{path} must be a non-empty string")


def string_list(value: Any, path: str, *, required: bool = True) -> None:
    if value is None and not required:
        return
    if not isinstance(value, list) or (required and not value):
        fail(f"{path} must be a non-empty list" if required else f"{path} must be a list")
    if not all(isinstance(item, str) and item.strip() for item in value):
        fail(f"{path} must contain non-empty strings")


def validate_common_preconditions(document: dict[str, Any]) -> dict[str, dict[str, Any]]:
    raw = document.get("common_preconditions", [])
    if raw is None:
        raw = []
    if not isinstance(raw, list):
        fail("common_preconditions must be a list when present")
    definitions: dict[str, dict[str, Any]] = {}
    for index, item in enumerate(raw):
        path = f"common_preconditions[{index}]"
        entry = require_mapping(item, path)
        identifier = entry.get("id")
        non_empty_string(identifier, f"{path}.id")
        if identifier in definitions:
            fail(f"{path}.id duplicates common_preconditions id {identifier!r}")
        non_empty_string(entry.get("name"), f"{path}.name")
        conditions = entry.get("conditions", [])
        string_list(conditions, f"{path}.conditions", required=False)
        steps = entry.get("steps", [])
        if steps is None:
            steps = []
        if not isinstance(steps, list):
            fail(f"{path}.steps must be a list")
        for step_index, step in enumerate(steps):
            step_path = f"{path}.steps[{step_index}]"
            step_mapping = require_mapping(step, step_path)
            non_empty_string(step_mapping.get("action"), f"{step_path}.action")
            non_empty_string(step_mapping.get("expected"), f"{step_path}.expected")
        definitions[identifier] = entry
    return definitions


def validate_step(step: Any, path: str) -> None:
    entry = require_mapping(step, path)
    non_empty_string(entry.get("action"), f"{path}.action")
    non_empty_string(entry.get("expected"), f"{path}.expected")
    for key in ("state_id", "target_element_id"):
        if key in entry and entry[key] is not None:
            non_empty_string(entry[key], f"{path}.{key}")
    if "locator_ref" in entry and entry["locator_ref"] is not None:
        locator = require_mapping(entry["locator_ref"], f"{path}.locator_ref")
        for key in ("element_id", "strategy", "value"):
            non_empty_string(locator.get(key), f"{path}.locator_ref.{key}")


def validate_yaml(path: Path) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    try:
        document = yaml.safe_load(path.read_text(encoding="utf-8-sig"))
    except (OSError, yaml.YAMLError) as error:
        fail(f"{path}: cannot read YAML: {error}")
    document = require_mapping(document, str(path))
    missing = REQUIRED_DOCUMENT_KEYS - document.keys()
    if missing:
        fail(f"{path}: missing document keys: {', '.join(sorted(missing))}")
    non_empty_string(document.get("req_id"), f"{path}.req_id")
    non_empty_string(document.get("module"), f"{path}.module")
    require_mapping(document.get("trace"), f"{path}.trace")
    cases = document["cases"]
    if not isinstance(cases, list) or not cases:
        fail(f"{path}.cases must be a non-empty list")

    definitions = validate_common_preconditions(document)
    has_common_preconditions = "common_preconditions" in document
    ids: set[str] = set()
    allowed_keys = REQUIRED_CASE_KEYS | OPTIONAL_CASE_KEYS
    for index, raw_case in enumerate(cases):
        case_path = f"{path}.cases[{index}]"
        case = require_mapping(raw_case, case_path)
        unknown = set(case) - allowed_keys
        if unknown:
            fail(f"{case_path}: unknown keys: {', '.join(sorted(unknown))}")
        if "zentao_status" in case:
            fail(f"{case_path}.zentao_status must be maintained in module_case_map.json, not testcase YAML")
        missing_case = REQUIRED_CASE_KEYS - case.keys()
        if missing_case:
            fail(f"{case_path}: missing keys: {', '.join(sorted(missing_case))}")
        case_id = case.get("id")
        non_empty_string(case_id, f"{case_path}.id")
        if not re.fullmatch(r"TC-[A-Za-z0-9_-]+", case_id):
            fail(f"{case_path}.id must match TC-[A-Za-z0-9_-]+")
        if case_id in ids:
            fail(f"{case_path}.id duplicates case id {case_id!r}")
        ids.add(case_id)
        non_empty_string(case.get("title"), f"{case_path}.title")
        if case.get("type") not in ALLOWED_CASE_TYPES:
            fail(f"{case_path}.type must be one of {sorted(ALLOWED_CASE_TYPES)!r}")
        if case.get("auto") not in ALLOWED_AUTO_VALUES:
            fail(f"{case_path}.auto must be 'auto' or 'no'")
        if case.get("priority") not in ALLOWED_PRIORITIES:
            fail(f"{case_path}.priority must be one of {sorted(ALLOWED_PRIORITIES)!r}")
        for key in ("feature",):
            if case[key] is not None:
                non_empty_string(case[key], f"{case_path}.{key}")
        for key in ("coverage_ids", "atomic_purpose_ids"):
            string_list(case[key], f"{case_path}.{key}")
        if len(case["atomic_purpose_ids"]) != 1:
            fail(f"{case_path}.atomic_purpose_ids must contain exactly one item")
        string_list(case["preconditions"], f"{case_path}.preconditions", required=False)
        if not isinstance(case["steps"], list) or not case["steps"]:
            fail(f"{case_path}.steps must be a non-empty list")
        for step_index, step in enumerate(case["steps"]):
            validate_step(step, f"{case_path}.steps[{step_index}]")
        if has_common_preconditions and "common_preconditions_ref" not in case:
            fail(f"{case_path}: common_preconditions_ref is required when common_preconditions exists")
        reference = case.get("common_preconditions_ref")
        if reference is not None:
            non_empty_string(reference, f"{case_path}.common_preconditions_ref")
            if reference not in definitions:
                fail(f"{case_path}.common_preconditions_ref references undefined id {reference!r}")
    return document, definitions


def validate_markdown(path: Path, yaml_ids: set[str], yaml_references: dict[str, str | None], template_path: Path) -> None:
    try:
        content = path.read_text(encoding="utf-8")
        template = template_path.read_text(encoding="utf-8")
    except OSError as error:
        fail(f"cannot read Markdown/template: {error}")
    for section in ("## 覆盖与审核信息", "## 用例总览", "## 结论"):
        if section not in content:
            fail(f"{path}: missing Markdown section {section}")
    if "CASE INDEX" in content or "{case_id}" in content:
        fail(f"{path}: Markdown contains obsolete format or template placeholders")
    if "## 覆盖与审核信息" in template and "## 覆盖与审核信息" not in content:
        fail(f"{path}: Markdown does not follow shared template")
    headings = re.findall(r"^##\s+(TC-[^/\s]+)\s*/\s*[^\n]+", content, flags=re.MULTILINE)
    markdown_ids = set(headings)
    if len(headings) != len(markdown_ids):
        fail(f"{path}: duplicate Markdown case headings detected")
    if markdown_ids != yaml_ids:
        fail(f"{path}: Markdown/YAML case IDs differ; markdown-only={sorted(markdown_ids - yaml_ids)}, yaml-only={sorted(yaml_ids - markdown_ids)}")
    blocks = re.split(r"(?=^##\s+TC-[^/\s]+\s*/\s*[^\n]+)", content, flags=re.MULTILINE)
    for block in blocks:
        match = re.match(r"^##\s+(TC-[^/\s]+)\s*/", block)
        if not match:
            continue
        case_id = match.group(1)
        reference_match = re.search(r"^\*\*公共前置引用\*\*:\s*`([^`]+)`\s*$", block, flags=re.MULTILINE)
        reference = reference_match.group(1) if reference_match else None
        if reference != yaml_references.get(case_id):
            fail(f"{path}: {case_id} common precondition reference differs from YAML")
        if "**公共前置引用**:" in block and reference is None:
            fail(f"{path}: {case_id} has an empty public precondition reference")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("yaml_file", type=Path)
    parser.add_argument("markdown_file", type=Path)
    parser.add_argument("--schema-dir", type=Path, default=DEFAULT_SCHEMA_DIR, help="共享 schemas 目录")
    args = parser.parse_args()
    try:
        document, _ = validate_yaml(args.yaml_file)
        cases = document["cases"]
        yaml_ids = {case["id"] for case in cases}
        yaml_references = {case["id"]: case.get("common_preconditions_ref") for case in cases}
        validate_markdown(args.markdown_file, yaml_ids, yaml_references, args.schema_dir / "testcase-markdown.template.md")
    except ValidationError as error:
        print(f"INVALID: {error}", file=sys.stderr)
        return 1
    print(f"VALID: {len(yaml_ids)} cases; shared testcase templates accepted")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

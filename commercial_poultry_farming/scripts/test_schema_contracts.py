"""公共页面和测试用例 Schema 的契约测试。"""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import jsonschema
import pytest
import yaml


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from validate_testcase_template import ValidationError, validate_yaml


def load_schema(name: str) -> dict[str, object]:
    """读取并检查指定公共 JSON Schema。"""
    schema = json.loads((ROOT / "schemas" / name).read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator.check_schema(schema)
    return schema


def valid_page_document() -> dict[str, object]:
    """返回不含业务值的最小有效 page.json 文档。"""
    return {
        "schema_version": "1.0",
        "capture_id": "PAGE-fixture",
        "captured_at": "2026-08-28T00:00:00+00:00",
        "capture": {
            "collector": "fixture",
            "browser": "chromium/fixture",
            "headless": False,
            "environment": {"id": "fixture", "os": "test", "browser": "chromium"},
            "scope": ["/fixture"],
            "status": "captured",
            "evidence": {
                "status": "not_collected",
                "screenshot_paths": [],
                "log_paths": ["capture.log"],
                "trace_paths": [],
            },
        },
        "sanitization": {"status": "applied", "redacted_fields": ["input.value"]},
        "pages": [
            {
                "page_id": "page-fixture",
                "route": "/fixture",
                "title": "Fixture page",
                "menu_path": [],
                "states": [
                    {
                        "state_id": "state-0001",
                        "parent_state_id": None,
                        "elements": [],
                        "forms": [],
                        "tables": [],
                        "interactions": [],
                        "dom_snapshot": {
                            "html": "<html><body></body></html>",
                            "accessibility_snapshot": None,
                            "sha256": "a" * 64,
                            "captured_at": "2026-08-28T00:00:00+00:00",
                        },
                        "evidence": {
                            "status": "not_collected",
                            "screenshot_paths": [],
                            "log_paths": ["capture.log"],
                            "trace_paths": [],
                        },
                    }
                ],
            }
        ],
    }


def valid_design_document() -> dict[str, object]:
    """返回不含业务实例值的最小蓝湖设计文档。"""
    node = {
        "element_id": "design-fixture-node-0",
        "kind": "container",
        "name": "Fixture root",
        "original_type": "container",
        "classification": "container",
        "tag": None,
        "role": None,
        "text": None,
        "rect": {"width": 100, "height": 80},
        "rect_source": "node.class",
        "style": None,
        "class": "w-100px h-80px",
        "image_ref": None,
        "parent_element_id": None,
        "child_element_ids": [],
        "depth": 1,
        "path": "0",
        "raw_node": {"type": "container", "name": "Fixture root"},
    }
    return {
        "schema_version": "1.0",
        "design_id": "design-fixture",
        "design_name": "Fixture design",
        "source": {
            "source_file": "fixture.json",
            "source_format": "Lanhu/Figma node tree",
            "slice_scale": 2,
            "is_figma": True,
            "coordinate_policy": "fixture policy",
        },
        "capture": {
            "collector": "fixture",
            "captured_at": "2026-08-28T00:00:00+00:00",
            "source_node_count": 1,
        },
        "pages": [{
            "page_id": "design-fixture-page",
            "title": "Fixture page",
            "roots": ["design-fixture-node-0"],
            "node_count": 1,
            "max_depth": 1,
            "nodes": [node],
        }],
    }


def valid_testcase() -> dict[str, object]:
    """返回最小有效测试用例。"""
    return {
        "id": "TC-FIXTURE",
        "title": "Fixture UI action",
        "type": "feature",
        "auto": "auto",
        "priority": "P2",
        "coverage_ids": ["CV-FIXTURE"],
        "plan_item_ids": ["PI-FIXTURE"],
        "atomic_purpose_ids": ["AP-FIXTURE"],
        "preconditions": [],
        "steps": [
            {
                "action": "点击 Fixture button",
                "expected": "观察 Fixture state",
                "state_id": "state-0001",
                "target_element_id": "element-0001",
                "locator_ref": {
                    "element_id": "element-0001",
                    "strategy": "role",
                    "value": "button",
                },
            }
        ],
        "ui_source": {"page_json": "02_analysis/page.json", "capture_id": "PAGE-fixture"},
        "trace": {"req": "REQ-FIXTURE"},
    }


def test_design_schema_accepts_minimal_fixture() -> None:
    """design.schema.json 必须接受最小通用蓝湖设计文档。"""
    schema = load_schema("design.schema.json")
    jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker()).validate(
        valid_design_document()
    )


def test_design_schema_rejects_unknown_node_kind() -> None:
    """design.schema.json 必须拒绝未定义的节点分类。"""
    schema = load_schema("design.schema.json")
    invalid = copy.deepcopy(valid_design_document())
    invalid["pages"][0]["nodes"][0]["kind"] = "widget"  # type: ignore[index]
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(schema).validate(invalid)


def test_design_schema_accepts_annotation_channel() -> None:
    """design.schema.json 必须接受标注模式通道的扁平节点。"""
    schema = load_schema("design.schema.json")
    document = copy.deepcopy(valid_design_document())
    node = document["pages"][0]["nodes"][0]  # type: ignore[index]
    node["rect_source"] = "annotation.css"
    node["parent_element_id"] = None
    node["child_element_ids"] = []
    jsonschema.Draft202012Validator(schema).validate(document)


def test_design_schema_rejects_unknown_rect_source() -> None:
    """design.schema.json 必须拒绝未定义的坐标来源。"""
    schema = load_schema("design.schema.json")
    invalid = copy.deepcopy(valid_design_document())
    invalid["pages"][0]["nodes"][0]["rect_source"] = "guessed"  # type: ignore[index]
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(schema).validate(invalid)


def test_page_schema_is_draft_2020_12_and_accepts_headed_fixture() -> None:
    """page.schema.json 必须接受可视浏览器采集结果。"""
    schema = load_schema("page.schema.json")
    jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker()).validate(
        valid_page_document()
    )


def test_page_schema_rejects_headless_capture() -> None:
    """page.schema.json 必须拒绝 headless=true。"""
    schema = load_schema("page.schema.json")
    invalid = valid_page_document()
    invalid["capture"]["headless"] = True  # type: ignore[index]
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(schema).validate(invalid)


def test_testcase_schema_accepts_all_local_case_types() -> None:
    """testcase.schema.json 必须接受完整的六个本地用例类型。"""
    schema = load_schema("testcase.schema.json")
    validator = jsonschema.Draft202012Validator(schema)
    for case_type in ("interface", "feature", "install", "config", "performance", "security"):
        document = valid_testcase()
        document["type"] = case_type
        validator.validate(document)


def test_testcase_schema_rejects_invalid_local_case_types() -> None:
    """testcase.schema.json 必须拒绝场景标签和远程映射值作为本地type。"""
    schema = load_schema("testcase.schema.json")
    validator = jsonschema.Draft202012Validator(schema)
    for case_type in ("auto", "other", "negative", "boundary", "functional", "data_consistency", "permission", "unknown", "", True, None):
        document = valid_testcase()
        document["type"] = case_type
        with pytest.raises(jsonschema.ValidationError):
            validator.validate(document)


def test_testcase_schema_accepts_dom_reference() -> None:
    """testcase.schema.json 必须接受步骤级 DOM 定位引用。"""
    schema = load_schema("testcase.schema.json")
    jsonschema.Draft202012Validator(schema).validate(valid_testcase())


def test_testcase_schema_accepts_common_preconditions_reference() -> None:
    """testcase.schema.json 必须接受公共前置引用字段。"""
    schema = load_schema("testcase.schema.json")
    document = valid_testcase()
    document["common_preconditions_ref"] = "CP-FIXTURE"
    jsonschema.Draft202012Validator(schema).validate(document)


def test_testcase_schema_accepts_null_common_preconditions_reference() -> None:
    """testcase.schema.json 必须接受 null 公共前置引用。"""
    schema = load_schema("testcase.schema.json")
    document = valid_testcase()
    document["common_preconditions_ref"] = None
    jsonschema.Draft202012Validator(schema).validate(document)


def test_testcase_schema_rejects_empty_common_preconditions_reference() -> None:
    """testcase.schema.json 必须拒绝空公共前置引用。"""
    schema = load_schema("testcase.schema.json")
    document = valid_testcase()
    document["common_preconditions_ref"] = ""
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(schema).validate(document)


def test_testcase_schema_rejects_unknown_locator_strategy() -> None:
    """testcase.schema.json 必须拒绝未定义的定位器策略。"""
    schema = load_schema("testcase.schema.json")
    invalid = copy.deepcopy(valid_testcase())
    invalid["steps"][0]["locator_ref"]["strategy"] = "xpath"  # type: ignore[index]
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(schema).validate(invalid)


def _common_precondition_document(reference_marker: object = "missing") -> dict[str, object]:
    case = {
        "id": "TC-FIXTURE-CP",
        "coverage_ids": ["CV-FIXTURE"],
        "atomic_purpose_ids": ["AP-FIXTURE"],
        "title": "Fixture public precondition",
        "type": "feature",
        "auto": "no",
        "priority": "P2",
        "feature": "Fixture",
        "preconditions": [],
        "steps": [{"action": "观察页面", "expected": "页面可见"}],
        "trace": {"req": "REQ-FIXTURE"},
    }
    if reference_marker != "missing":
        case["common_preconditions_ref"] = reference_marker
    return {
        "req_id": "REQ-FIXTURE",
        "module": "Fixture",
        "trace": {"req": "REQ-FIXTURE"},
        "common_preconditions": [
            {"id": "CP-FIXTURE", "name": "Fixture access", "conditions": [], "steps": []}
        ],
        "cases": [case],
    }


def _write_document(tmp_path: Path, document: dict[str, object]) -> Path:
    path = tmp_path / "testcases.yaml"
    path.write_text(yaml.safe_dump(document, allow_unicode=True), encoding="utf-8")
    return path


def test_document_preconditions_require_reference_field(tmp_path: Path) -> None:
    """顶层有公共前置时，用例必须保留引用字段。"""
    with pytest.raises(ValidationError, match="common_preconditions_ref is required"):
        validate_yaml(_write_document(tmp_path, _common_precondition_document()))


def test_document_preconditions_allow_null_reference(tmp_path: Path) -> None:
    """公共前置引用字段可以显式为 null。"""
    document = _common_precondition_document(None)
    validate_yaml(_write_document(tmp_path, document))


def test_document_preconditions_accept_valid_reference(tmp_path: Path) -> None:
    """公共前置引用字段可以引用已定义 ID。"""
    validate_yaml(_write_document(tmp_path, _common_precondition_document("CP-FIXTURE")))


def test_document_preconditions_reject_undefined_reference(tmp_path: Path) -> None:
    """公共前置引用必须指向已定义 ID。"""
    with pytest.raises(ValidationError, match="references undefined id"):
        validate_yaml(_write_document(tmp_path, _common_precondition_document("CP-UNKNOWN")))


def test_document_without_preconditions_keeps_reference_optional(tmp_path: Path) -> None:
    """没有顶层公共前置时，引用字段继续可选。"""
    document = _common_precondition_document()
    document.pop("common_preconditions")
    validate_yaml(_write_document(tmp_path, document))

from pathlib import Path
import sys

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from render_testcase_markdown import render
from validate_testcase_markdown import validate


@pytest.fixture
def document():
    return {
        "req_id": "REQ-TEST-001",
        "module": "示例模块",
        "trace": {"tp": "TP-001", "project": "示例项目", "version": "v1", "status": "ready"},
        "cases": [
            {
                "id": "TC-TEST-001-001",
                "title": "正常提交",
                "type": "feature",
                "auto": "auto",
                "priority": "P1",
                "atomic_purpose_ids": ["AP-1"],
                "preconditions": ["存在可提交数据"],
                "steps": [{"action": "打开页面", "expected": "页面显示"}],
                "trace": {"req": "REQ-TEST-001", "tp": "TP-001", "project": "示例项目", "version": "v1", "status": "ready"},
            },
            {
                "id": "TC-TEST-001-002",
                "title": "空数据提交",
                "type": "feature",
                "auto": "no",
                "priority": "P2",
                "atomic_purpose_ids": ["AP-2"],
                "preconditions": ["页面可访问"],
                "steps": [
                    {"action": "不填写数据并提交", "expected": "页面提示必填项"},
                    {"action": "关闭提示", "expected": "提示消失"},
                ],
            },
        ],
    }


def test_render_and_validate(document, tmp_path):
    markdown = render(document)
    assert validate(markdown, document) == []
    assert "CASE INDEX" not in markdown
    assert markdown.count("## TC-") == 2
    assert "总用例数：**2**" in markdown
    assert "自动化用例数：**1**" in markdown
    assert "P1：**1**" in markdown
    assert "P2：**1**" in markdown


def test_validator_rejects_placeholder_and_mismatch(document):
    markdown = render(document).replace("总用例数：**2**", "总用例数：**3**", 1) + "\n{case_count}"
    errors = validate(markdown, document)
    assert any("占位符" in error for error in errors)
    assert any("总数" in error for error in errors)


def test_validator_rejects_legacy_index(document):
    markdown = render(document) + "\n## CASE INDEX\n"
    assert any("CASE INDEX" in error for error in validate(markdown, document))


def test_validator_rejects_invalid_case_type(document):
    invalid = dict(document)
    invalid["cases"] = [dict(case) for case in document["cases"]]
    invalid["cases"][0]["type"] = "negative"
    markdown = render(invalid)
    assert any("type非法" in error for error in validate(markdown, invalid))


def test_yaml_fixture_is_parseable(document, tmp_path):
    path = tmp_path / "cases.yaml"
    path.write_text(yaml.safe_dump(document, allow_unicode=True), encoding="utf-8")
    assert yaml.safe_load(path.read_text(encoding="utf-8"))["req_id"] == "REQ-TEST-001"

from __future__ import annotations

import importlib.util
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "case_results_reporter.py"
_spec = importlib.util.spec_from_file_location("case_results_reporter", SCRIPT)
assert _spec and _spec.loader
reporter = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(reporter)


def test_normalize_preserves_case_order_and_excludes_manual() -> None:
    metadata = {
        "TC-1": {"auto": "auto"},
        "TC-2": {"auto": "no"},
        "TC-3": {"auto": "auto"},
    }
    result = reporter._normalize_results(
        ["TC-1", "TC-2", "TC-3"],
        metadata,
        [{"case_id": "TC-3", "result": "passed"}, {"case_id": "TC-1", "result": "blocked"}],
        "RUN_TEST",
    )
    assert [item["case_id"] for item in result] == ["TC-1", "TC-2", "TC-3"]
    assert [item["result"] for item in result] == ["blocked", "excluded", "passed"]


def test_normalize_marks_missing_and_invalid_results_as_test_case_error() -> None:
    metadata = {"TC-1": {"auto": "auto"}, "TC-2": {"auto": "auto"}}
    result = reporter._normalize_results(
        ["TC-1", "TC-2"],
        metadata,
        [{"case_id": "TC-1", "result": "not-a-result"}],
        "RUN_TEST",
    )
    assert result[0]["result"] == "test_case_error"
    assert "非法结果分类：not-a-result" in result[0]["reason"]
    assert result[1]["result"] == "test_case_error"
    assert "缺少该 auto 用例" in result[1]["reason"]


def test_normalize_marks_duplicate_and_unknown_case_ids() -> None:
    metadata = {"TC-1": {"auto": "auto"}}
    result = reporter._normalize_results(
        ["TC-1"],
        metadata,
        [
            {"case_id": "TC-1", "result": "passed"},
            {"case_id": "TC-1", "result": "blocked"},
            {"case_id": "TC-UNKNOWN", "result": "passed"},
        ],
        "RUN_TEST",
    )
    assert result[0]["result"] == "test_case_error"
    assert "case_id 重复" in result[0]["reason"]
    assert result[1]["case_id"] == "TC-UNKNOWN"
    assert result[1]["result"] == "test_case_error"


def test_load_results_accepts_list_and_cases_object(tmp_path: Path) -> None:
    list_path = tmp_path / "list.yaml"
    list_path.write_text("- case_id: TC-1\n  result: passed\n", encoding="utf-8")
    assert len(reporter._load_results_file(list_path)["cases"]) == 1

    object_path = tmp_path / "object.json"
    object_path.write_text('{"cases": [{"case_id": "TC-1", "result": "passed"}]}', encoding="utf-8")
    assert len(reporter._load_results_file(object_path)["cases"]) == 1

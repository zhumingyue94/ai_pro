from __future__ import annotations

from pathlib import Path

import pytest

from utils.case_runtime import prepare_run
from utils.script_lifecycle import validate_script
from utils.test_data_factory import TestDataFactory as DataFactory


ROOT = Path(__file__).resolve().parents[2]


def test_test_data_factory_is_unique_and_declares_cleanup() -> None:
    with pytest.raises(ValueError):
        DataFactory.for_run("<test_data_prefix>", "RUN_TEST", "tenant-a")

    configured = DataFactory.for_run("AUTO", "RUN_TEST", "tenant-a")
    first = configured.unique_name("entity")
    second = configured.unique_name("entity")
    assert first != second
    assert "RUN_TEST" in first
    assert configured.impact(action="create", resource="entity")["cleanup_status"] == "pending"


def test_prepare_run_creates_isolated_evidence_directories(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TEST_RUN_ID", "RUN_TEST")
    run_id, run_dir, screenshots, videos = prepare_run("CASE-1", tmp_path)
    assert run_id == "RUN_TEST"
    assert run_dir == tmp_path / "RUN_TEST"
    assert screenshots.is_dir()
    assert videos.is_dir()


def test_script_validator_has_no_requirement_specific_runner(tmp_path: Path) -> None:
    script = tmp_path / "case.py"
    script.write_text(
        """CASE_ID = 'CASE-1'\nCASE_STEPS = ['open']\nCASE_ASSERTIONS = ['visible']\ndef run_case():\n    assert True\ndef main():\n    run_case()\nif __name__ == '__main__':\n    main()\n""",
        encoding="utf-8",
    )
    check = validate_script(script, "CASE-1")
    assert check.valid, check.errors


def test_template_config_keeps_placeholders() -> None:
    text = (ROOT / "config.yaml").read_text(encoding="utf-8")
    assert "<PROJECT_NAME>" in text
    assert "<PORTAL_APP_NAME>" in text
    assert "<test_data_prefix>" in text

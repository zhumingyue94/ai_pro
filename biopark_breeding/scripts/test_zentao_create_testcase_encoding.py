import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from zentao_create_testcase import (
    SyncError,
    build_common_preconditions_index,
    build_create_command,
    build_create_payload,
    build_precondition_text,
    build_update_command,
    run_json,
    validate_readback,
)


def test_payload_preserves_utf8_newlines_and_special_characters() -> None:
    case = {
        "id": "TC-UTF8",
        "title": "雏苗发货：中文、引号\"与反斜杠\\",
        "preconditions": ["前置条件第一行", "第二行||ZTC_STEP||保留"],
        "priority": "P2",
        "auto": "auto",
        "steps": [
            {"action": "打开“计划管理”页面", "expected": "页面显示中文列表\n且无乱码"},
            {"action": "输入 A\\B ||ZTC_STEP|| C", "expected": "保存成功，数量为 2"},
        ],
    }
    payload = build_create_payload(case, 1, 711)
    assert payload == {
        "productID": 1,
        "title": case["title"],
        "module": 711,
        "pri": 2,
        "type": "other",
        "precondition": "前置准备：\n1、前置条件第一行\n2、第二行||ZTC_STEP||保留",
        "steps": ["打开“计划管理”页面", "输入 A\\B ||ZTC_STEP|| C"],
        "expects": ["页面显示中文列表\n且无乱码", "保存成功，数量为 2"],
        "stepType": ["step", "step"],
    }
    command = build_create_command(case, 1, 711)
    assert command[command.index("--data") + 1] == json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    assert "--steps" not in command
    assert "--expects" not in command


def test_common_preconditions_are_merged_into_payload() -> None:
    document = {
        "common_preconditions": [
            {
                "id": "delivery_execution_page",
                "conditions": ["账号已授权", "目标发货单已准备"],
                "steps": [
                    {"action": "进入雏苗发货", "expected": "列表页显示"},
                ],
            }
        ]
    }
    common = build_common_preconditions_index(document)
    case = {
        "id": "TC-COMMON",
        "title": "公共前置合并",
        "preconditions": ["专属数据已准备"],
        "common_preconditions_ref": "delivery_execution_page",
        "steps": [{"action": "点击发货", "expected": "进入执行页"}],
    }
    expected = "前置准备：\n1、专属数据已准备\n\n前置步骤：\n1、进入雏苗发货；列表页显示"
    assert build_precondition_text(case, common) == expected
    assert build_create_payload(case, 1, 737, common_preconditions=common)["precondition"] == expected


def test_duplicate_generic_access_data_condition_is_removed() -> None:
    document = {"common_preconditions": [{"id": "page", "conditions": ["具备页面访问权限和授权脱敏测试数据"]}]}
    common = build_common_preconditions_index(document)
    case = {"id": "TC-DUP", "common_preconditions_ref": "page", "preconditions": ["已准备与本场景匹配的测试账号和授权脱敏测试数据"]}
    result = build_precondition_text(case, common)
    assert result.count("前置准备：") == 1
    assert result.count("授权脱敏测试数据") == 1


def test_common_precondition_reference_errors() -> None:
    case = {"id": "TC-INVALID", "common_preconditions_ref": "missing"}
    try:
        build_precondition_text(case, {})
    except SyncError as error:
        assert "references undefined common precondition" in str(error)
    else:
        raise AssertionError("undefined reference must fail")


def test_common_precondition_definition_is_validated() -> None:
    try:
        build_common_preconditions_index({"common_preconditions": [{"id": "bad", "steps": [{"action": ""}]}]})
    except SyncError as error:
        assert "invalid step" in str(error)
    else:
        raise AssertionError("invalid definition must fail")


def test_run_json_decodes_utf8_and_bom(monkeypatch) -> None:
    class Completed:
        returncode = 0
        stdout = b"\xef\xbb\xbf" + '{"status":"success","message":"创建成功"}'.encode("utf-8")
        stderr = b""

    monkeypatch.setattr("zentao_create_testcase.subprocess.run", lambda *args, **kwargs: Completed())
    assert run_json(["fake"]) == {"status": "success", "message": "创建成功"}


def _priority_case(priority: str = "P3") -> dict:
    return {
        "id": "TC-PRIORITY",
        "title": "优先级回读校验",
        "priority": priority,
        "preconditions": ["测试数据已准备"],
        "steps": [{"action": "打开页面", "expected": "页面显示"}],
    }


def test_update_command_contains_remote_id_and_priority() -> None:
    command = build_update_command(_priority_case(), 51620, 732, 46)
    payload = json.loads(command[command.index("--data") + 1])
    assert payload["id"] == 51620
    assert payload["pri"] == 3
    assert "productID" not in payload


def test_validate_readback_rejects_priority_mismatch() -> None:
    remote = {
        "id": 51620,
        "product": 8,
        "project": 46,
        "module": 732,
        "pri": 2,
        "title": "优先级回读校验",
        "type": "feature",
        "precondition": "前置准备：\n1、测试数据已准备",
        "steps": [{"step": "打开页面", "expect": "页面显示"}],
    }
    assert "pri" in validate_readback(remote, _priority_case(), 8, 732, 46)


def test_validate_readback_accepts_matching_priority() -> None:
    remote = {
        "id": 51620,
        "product": 8,
        "project": 46,
        "module": 732,
        "pri": 3,
        "title": "优先级回读校验",
        "type": "feature",
        "precondition": "前置准备：\n1、测试数据已准备",
        "steps": [{"step": "打开页面", "expect": "页面显示"}],
    }
    assert "pri" not in validate_readback(remote, _priority_case(), 8, 732, 46)

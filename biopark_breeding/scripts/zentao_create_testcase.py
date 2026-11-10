#!/usr/bin/env python3
"""按评审 YAML 串行创建并校验禅道测试用例，写入 config 中的项目用例库。"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml


class SyncError(RuntimeError):
    """可安全记录到同步证据的流程错误。"""


ALLOWED_CASE_TYPES = {
    "interface",
    "feature",
    "install",
    "config",
    "performance",
    "security",
}
ALLOWED_AUTO_VALUES = {"auto", "no"}


def resolve_type_fields(case: dict[str, Any]) -> tuple[str, str]:
    """校验本地type并返回(禅道type, 本地auto)，保持既有映射。"""
    case_id = case.get("id")
    case_type = case.get("type")
    auto = case.get("auto")
    if not isinstance(case_type, str) or case_type not in ALLOWED_CASE_TYPES:
        raise SyncError(
            f"invalid local type for {case_id}: {case_type!r}; "
            f"allowed={sorted(ALLOWED_CASE_TYPES)!r}"
        )
    if not isinstance(auto, str) or auto not in ALLOWED_AUTO_VALUES:
        raise SyncError(f"invalid auto for {case_id}: {auto!r}; allowed={sorted(ALLOWED_AUTO_VALUES)!r}")
    return ("other" if auto == "auto" else case_type), auto


def sha256_file(path: Path) -> str:
    """计算文件 SHA256 十六进制摘要。"""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_yaml(path: Path) -> dict[str, Any]:
    """读取 UTF-8 YAML 并要求根节点为对象。"""
    if not path.is_file():
        raise SyncError(f"missing YAML: {path}")
    value = yaml.safe_load(path.read_text(encoding="utf-8-sig")) or {}
    if not isinstance(value, dict):
        raise SyncError(f"YAML root must be an object: {path}")
    return value


def validate_shared_sync_config(config: dict[str, Any], project: Path) -> None:
    """校验项目是否声明并强制使用公共禅道同步入口。"""
    settings = config.get("zentao_sync")
    if not isinstance(settings, dict):
        raise SyncError(f"missing zentao_sync config: {project / 'config.yaml'}")
    if settings.get("implementation") != "shared" or settings.get("allow_project_cli") is not False:
        raise SyncError("project CLI bypass is not allowed")
    required = ("require_readback", "require_registry_update", "require_source_hash")
    if any(settings.get(key) is not True for key in required):
        raise SyncError("shared sync safety requirements are not enabled")
    entrypoint = Path(str(settings.get("entrypoint", "")))
    expected = (project / entrypoint).resolve()
    if expected != Path(__file__).resolve():
        raise SyncError(f"sync entrypoint must resolve to {Path(__file__).resolve()}")


def parse_module_reference(path: Path) -> dict[int, dict[str, Any]]:
    """按模块 ID 建索引：模块树存在同名分支（如 雏苗发货 711/712），按名称建索引会互相覆盖。"""
    text = path.read_text(encoding="utf-8-sig")
    modules: dict[int, dict[str, Any]] = {}
    pattern = re.compile(r"^\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*(\d+)\s*\|")
    for line in text.splitlines():
        match = pattern.match(line)
        if match:
            module_path, name, module_id = match.groups()
            if name.strip() not in {"模块名称", "---"}:
                modules[int(module_id)] = {"name": name.strip(), "id": int(module_id), "path": module_path.strip()}
    return modules


def resolve_module(root: Path, req_id: str, module_file: Path, tree_file: Path) -> dict[str, Any]:
    """从模块拆分清单解析需求所属禅道模块。"""
    if not module_file.is_file():
        module_file = root / "01_requirements" / "pc" / "模块拆分清单.md"
    if not tree_file.is_file():
        tree_file = root / "01_requirements" / "禅道模块id.md"
    if not module_file.is_file() or not tree_file.is_file():
        raise SyncError(f"module reference files are missing: {module_file}, {tree_file}")
    text = module_file.read_text(encoding="utf-8-sig")
    row = next(
        (line for line in text.splitlines() if re.match(r"^\|\s*" + re.escape(req_id) + r"\s*\|", line)),
        "",
    )
    match = re.match(r"^\|\s*" + re.escape(req_id) + r"\s*\|.*?ID\s*=\s*(\d+)", row)
    if not match:
        raise SyncError(f"cannot resolve assigned module for {req_id}")
    module_id = int(match.group(1))
    modules = parse_module_reference(tree_file)
    resolved = modules.get(module_id)
    if not resolved:
        raise SyncError(f"module {module_id} is absent from module tree")
    return resolved


def selected_cases(review: dict[str, Any], testcase_document: dict[str, Any], limit: int) -> list[dict[str, Any]]:
    """按评审清单或源 YAML 截取待同步用例。"""
    review_queue = review.get("待同步清单") or {}
    cases = review.get("sync_items") or review_queue.get("sync_items")
    if not isinstance(cases, list):
        cases = [
            {"case_id": case.get("id")}
            for case in testcase_document.get("cases", [])
            if isinstance(case, dict) and case.get("id")
        ]
    result = []
    for item in cases[:limit]:
        if not isinstance(item, dict) or not item.get("case_id"):
            raise SyncError("invalid sync item")
        result.append(item)
    if len(result) != limit:
        raise SyncError(f"review YAML contains fewer than {limit} cases")
    return result


def load_case_details(testcase_file: Path, case_ids: set[str], registry_file: Path) -> dict[str, dict[str, Any]]:
    """按用例 ID 加载 YAML 明细并合并注册表禅道 ID。"""
    document = load_yaml(testcase_file)
    registry = json.loads(registry_file.read_text(encoding="utf-8-sig"))
    registry_cases = {}
    for req_group in (registry.get("modules_by_req_id") or {}).values():
        for item in (req_group.get("cases") or {}).values():
            if isinstance(item, dict):
                registry_cases[str(item.get("case_id"))] = item
    for item in registry.get("cases", []):
        if isinstance(item, dict):
            registry_cases[str(item.get("case_id"))] = item
    details = {}
    for case in document.get("cases", []):
        if isinstance(case, dict) and case.get("id") in case_ids:
            detail = dict(case)
            registered_id = registry_cases.get(str(case["id"]), {}).get("zentao_case_id")
            if isinstance(registered_id, int) and registered_id > 0:
                detail["zentao_case_id"] = registered_id
            details[str(case["id"])] = detail
    missing = case_ids - details.keys()
    if missing:
        raise SyncError(f"missing case details: {sorted(missing)}")
    return details


def relative_to_project(root: Path, path: Path) -> str:
    """把绝对路径收成相对项目根的 POSIX 路径。"""
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def update_registry(
    registry_file: Path,
    case: dict[str, Any],
    module: dict[str, Any],
    remote_id: int,
    source_paths: dict[str, str] | None = None,
) -> None:
    """将通过回读的禅道数字 ID 写入唯一注册表。"""
    registry = json.loads(registry_file.read_text(encoding="utf-8-sig"))
    case_id = str(case["id"])
    source_paths = source_paths or {}
    req_id = str(case.get("trace", {}).get("req") or source_paths.get("req_id") or "")
    testcase_path = source_paths.get("testcase") or ""
    review_path = source_paths.get("case_review") or ""
    groups = registry.setdefault("modules_by_req_id", {})
    group = groups.get(req_id)
    if not isinstance(group, dict):
        group = {"req_id": req_id, "module": {"name": module["name"], "id": module["id"], "path": module["path"]}, "source_yaml_module_id": module["id"], "source": {"testcase": testcase_path, "case_review": review_path}, "cases": {}}
        groups[req_id] = group
    cases = group.setdefault("cases", {})
    item = cases.get(case_id)
    if not isinstance(item, dict):
        item = {"case_id": case_id, "title": case.get("title") or "", "zentao_case_id": None, "mapping_status": "pending_registry", "automation_status": "pending_implementation", "handler": None, "page_object": None, "data_contract": None, "check_id": None, "assertion_scope": None}
        cases[case_id] = item
    item["zentao_case_id"] = remote_id
    item["mapping_status"] = "registered"
    all_cases = [entry for current in groups.values() for entry in (current.get("cases") or {}).values() if isinstance(entry, dict)]
    registry["summary"]["total_cases"] = len(all_cases)
    registry["summary"]["registered_cases"] = sum(entry.get("zentao_case_id") is not None for entry in all_cases)
    registry["summary"]["pending_registry"] = sum(entry.get("zentao_case_id") is None for entry in all_cases)
    registry["summary"]["unique_zentao_case_ids"] = len({entry["zentao_case_id"] for entry in all_cases if entry.get("zentao_case_id") is not None})
    registry["summary"]["automation_pending_implementation"] = sum(entry.get("automation_status") == "pending_implementation" for entry in all_cases)
    registry["summary"]["automation_implemented"] = sum(entry.get("automation_status") == "implemented" for entry in all_cases)
    registry_file.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build_common_preconditions_index(document: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """校验并索引文档级公共前置定义。"""
    definitions = document.get("common_preconditions") or []
    if not isinstance(definitions, list):
        raise SyncError("common_preconditions must be a list")
    indexed: dict[str, dict[str, Any]] = {}
    for definition in definitions:
        if not isinstance(definition, dict):
            raise SyncError("common_preconditions contains a non-object definition")
        definition_id = definition.get("id")
        if not isinstance(definition_id, str) or not definition_id.strip():
            raise SyncError("common_preconditions definition requires a non-empty id")
        if definition_id in indexed:
            raise SyncError(f"duplicate common_preconditions id: {definition_id}")
        conditions = definition.get("conditions") or []
        steps = definition.get("steps") or []
        if not isinstance(conditions, list) or not all(isinstance(item, (str, int, float)) for item in conditions):
            raise SyncError(f"invalid conditions for common precondition: {definition_id}")
        if not isinstance(steps, list):
            raise SyncError(f"invalid steps for common precondition: {definition_id}")
        for step in steps:
            if not isinstance(step, dict) or not str(step.get("action", "")) or not str(step.get("expected", "")):
                raise SyncError(f"invalid step for common precondition: {definition_id}")
        indexed[definition_id] = definition
    return indexed


def _condition_key(value: str) -> str:
    """生成用于前置条件去重的稳定比较键，不改变最终展示文本。"""
    return re.sub(r"[\\s，。；、：:（）()「」『』<>《》/]+", "", value).lower()


def _is_generic_access_data_condition(value: str) -> bool:
    """识别会与公共账号、权限、授权数据条件重复的泛化专属条件。"""
    has_access = any(token in value for token in ("测试账号", "账号", "页面访问权限", "访问权限"))
    has_data = any(token in value for token in ("测试数据", "授权脱敏", "发货单", "关联数据"))
    specific_fixture = any(token in value for token in ("两个", "两次", "不同", "唯一", "并发", "具体", "失败", "不具备"))
    return has_access and has_data and not specific_fixture


def merge_precondition_items(common_items: list[str], own_items: list[str]) -> list[str]:
    """合并公共与专属条件，保留首次出现项并消除已知泛化账号/数据重复。"""
    result: list[str] = []
    seen: set[str] = set()
    common_has_access_data = any(_is_generic_access_data_condition(item) for item in common_items)
    for item in [*common_items, *own_items]:
        value = str(item).strip()
        if not value:
            continue
        key = _condition_key(value)
        if key in seen:
            continue
        if common_has_access_data and _is_generic_access_data_condition(value) and any(
            _is_generic_access_data_condition(existing) for existing in result
        ):
            continue
        seen.add(key)
        result.append(value)
    return result


def build_precondition_text(
    case: dict[str, Any], common_preconditions: dict[str, dict[str, Any]] | None = None
) -> str:
    """生成禅道前置条件字段值，仅包含前置准备和前置步骤两个分区。"""
    preparation: list[str] = [str(condition) for condition in case.get("preconditions") or []]
    steps: list[str] = []
    reference = case.get("common_preconditions_ref")
    if reference is not None:
        references = [reference] if isinstance(reference, str) else reference
        if not isinstance(references, list) or not references or any(not isinstance(item, str) or not item.strip() for item in references):
            raise SyncError(f"invalid common_preconditions_ref: {case.get('id')}")
        for reference_id in references:
            definition = (common_preconditions or {}).get(reference_id)
            if definition is None:
                raise SyncError(f"case {case.get('id')} references undefined common precondition: {reference_id}")
            steps.extend(f"{step['action']}；{step['expected']}" for step in definition.get("steps") or [])
    sections: list[tuple[str, list[str]]] = []
    if preparation:
        sections.append(("前置准备", preparation))
    if steps:
        sections.append(("前置步骤", steps))
    lines: list[str] = []
    for title, items in sections:
        if lines:
            lines.append("")
        lines.append(f"{title}：")
        lines.extend(f"{index}、{item}" for index, item in enumerate(items, start=1))
    result = "\n".join(lines)
    if not result:
        raise SyncError(f"case {case.get('id')} produced an empty precondition")
    return result


def build_create_payload(
    case: dict[str, Any], product_id: int, module_id: int, project_id: int | None = None,
    common_preconditions: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """组装 zentao testcase create --data 所需字段，步骤写入 JSON 数组。"""
    steps = case.get("steps") or []
    if not steps:
        raise SyncError(f"case has no steps: {case.get('id')}")
    actions = [str(step.get("action", "")) for step in steps]
    expects = [str(step.get("expected", "")) for step in steps]
    if any(not value for value in actions + expects):
        raise SyncError(f"case has empty action/expected: {case.get('id')}")
    priority = {"P1": 1, "P2": 2, "P3": 3, "P4": 4}.get(str(case.get("priority", "P3")), 3)
    payload = {
        "productID": product_id,
        "title": str(case.get("title", "")),
        "module": module_id,
        "pri": priority,
        "type": resolve_type_fields(case)[0],
        "precondition": build_precondition_text(case, common_preconditions),
        "steps": actions,
        "expects": expects,
        "stepType": ["step"] * len(actions),
    }
    if project_id:
        payload["project"] = project_id
    return payload


def build_create_command(
    case: dict[str, Any], product_id: int, module_id: int, project_id: int | None = None,
    common_preconditions: dict[str, dict[str, Any]] | None = None,
) -> list[str]:
    """生成仅使用 --data JSON 的禅道创建命令。"""
    payload = json.dumps(
        build_create_payload(case, product_id, module_id, project_id, common_preconditions),
        ensure_ascii=False,
        separators=(",", ":"),
    )
    return zentao_command() + ["--format=json", "--machine-readable", "testcase", "create", "--data", payload]


def build_update_command(
    case: dict[str, Any], remote_id: int, module_id: int, project_id: int | None = None,
    common_preconditions: dict[str, dict[str, Any]] | None = None,
) -> list[str]:
    """生成仅使用 --data JSON 的禅道更新命令。"""
    payload = build_create_payload(case, 0, module_id, project_id, common_preconditions)
    payload.pop("productID", None)
    payload["id"] = remote_id
    if "pri" not in payload:
        raise SyncError(f"update payload missing pri: {remote_id}")
    return zentao_command() + [
        "--format=json",
        "--machine-readable",
        "testcase",
        "update",
        "--id",
        str(remote_id),
        "--data",
        json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
    ]


def run_json(command: list[str]) -> Any:
    """执行禅道命令并解析 JSON 输出。"""
    try:
        result = subprocess.run(command, capture_output=True)
    except FileNotFoundError as exc:
        raise SyncError(f"executable or wrapper not found: {command[:10]}") from exc
    output = result.stdout.decode("utf-8-sig", errors="strict").strip()
    error_output = result.stderr.decode("utf-8-sig", errors="replace").strip()
    if result.returncode:
        raise SyncError(error_output or output or f"command failed: {result.returncode}")
    try:
        value = json.loads(output)
    except json.JSONDecodeError as exc:
        raise SyncError(f"invalid JSON response: {output[:500]}") from exc
    if isinstance(value, dict) and value.get("status") not in (None, "success") and "id" not in value:
        raise SyncError(f"zentao operation failed: {json.dumps(value, ensure_ascii=False)[:500]}")
    return value


def zentao_command() -> list[str]:
    """定位本机 zentao-cli 可执行入口。"""
    global_dir = Path(r"C:\Users\zhumi\AppData\Local\Programs\nodejs\node_global")
    cli_script = global_dir / "node_modules" / "zentao-cli" / "bin" / "zentao.js"
    node_candidates = [Path(sys.executable).with_name("node.exe"), Path(r"D:\tools\nodejs\node.exe")]
    for node in node_candidates:
        if node.is_file() and cli_script.is_file():
            return [str(node), str(cli_script)]
    zentao = global_dir / "zentao.cmd"
    if zentao.is_file():
        return [str(zentao)]
    raise SyncError("zentao CLI executable not found")


def remote_readback(case_id: int) -> dict[str, Any]:
    """按禅道用例 ID 回读详情。"""
    return run_json(zentao_command() + ["--format=json", "--machine-readable", "testcase", str(case_id)])


def build_delete_command(remote_id: int) -> list[str]:
    """生成指定禅道测试用例的删除命令，不接受标题或模糊条件。"""
    if remote_id <= 0:
        raise SyncError(f"invalid remote testcase ID: {remote_id}")
    return zentao_command() + [
        "--format=json",
        "--machine-readable",
        "testcase",
        "delete",
        "--id",
        str(remote_id),
    ]


def registry_delete_entry(registry_file: Path, remote_id: int) -> dict[str, str]:
    """从唯一注册表移除已确认删除的当前映射，并返回历史定位信息。"""
    registry = json.loads(registry_file.read_text(encoding="utf-8-sig"))
    found: tuple[dict[str, Any], str, str] | None = None
    for req_id, group in (registry.get("modules_by_req_id") or {}).items():
        for case_id, entry in (group.get("cases") or {}).items():
            if isinstance(entry, dict) and entry.get("zentao_case_id") == remote_id:
                found = (group["cases"], str(req_id), str(case_id))
                break
        if found:
            break
    if found is None:
        for case_id, entry in (registry.get("cases") or {}).items():
            if isinstance(entry, dict) and entry.get("zentao_case_id") == remote_id:
                found = (registry["cases"], "", str(case_id))
                break
    if found is None:
        return {"req_id": "", "case_id": "", "action": "no_registered_mapping"}
    cases, req_id, case_id = found
    del cases[case_id]
    all_cases = [
        entry
        for group in (registry.get("modules_by_req_id") or {}).values()
        for entry in (group.get("cases") or {}).values()
        if isinstance(entry, dict)
    ]
    if not all_cases and isinstance(registry.get("cases"), list):
        all_cases = [entry for entry in registry["cases"] if isinstance(entry, dict)]
    summary = registry.setdefault("summary", {})
    summary["total_cases"] = len(all_cases)
    summary["registered_cases"] = sum(entry.get("zentao_case_id") is not None for entry in all_cases)
    summary["pending_registry"] = sum(entry.get("zentao_case_id") is None for entry in all_cases)
    summary["unique_zentao_case_ids"] = len({entry["zentao_case_id"] for entry in all_cases if entry.get("zentao_case_id") is not None})
    summary["automation_pending_implementation"] = sum(entry.get("automation_status") == "pending_implementation" for entry in all_cases)
    summary["automation_implemented"] = sum(entry.get("automation_status") == "implemented" for entry in all_cases)
    registry_file.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"req_id": req_id, "case_id": case_id, "action": "removed"}


def is_remote_not_found(error: SyncError) -> bool:
    """仅识别禅道明确的目标不存在响应，避免把网络错误误判为删除成功。"""
    message = str(error).lower()
    return any(marker in message for marker in ("404", "not found", "不存在", "未找到", "case not exist", "case does not exist"))


def confirm_remote_deleted(remote_id: int) -> dict[str, Any]:
    """删除后回读并确认目标明确不存在。"""
    try:
        remote_readback(remote_id)
    except SyncError as exc:
        if is_remote_not_found(exc):
            return {"status": "confirmed_not_found", "error": str(exc)}
        raise SyncError(f"delete post-readback failed for {remote_id}: {exc}") from exc
    raise SyncError(f"remote testcase still exists after delete: {remote_id}")


def validate_delete_context(remote: dict[str, Any], product_id: int, module_id: int, project_id: int) -> list[str]:
    """校验待删除用例仍属于指定产品、项目和模块。"""
    defects = []
    if int(remote.get("product", -1)) != product_id:
        defects.append("product")
    if int(remote.get("project", -1)) != project_id:
        defects.append("project")
    if int(remote.get("module", -1)) != module_id:
        defects.append("module")
    return defects


def validate_readback(
    remote: dict[str, Any],
    case: dict[str, Any],
    product_id: int,
    module_id: int,
    project_id: int | None = None,
    common_preconditions: dict[str, dict[str, Any]] | None = None,
) -> list[str]:
    """回读校验产品、项目库、模块、标题、步骤、类型和前置条件。"""
    defects = []
    if int(remote.get("product", -1)) != product_id:
        defects.append("product")
    if project_id is not None and int(remote.get("project", -1)) != project_id:
        defects.append("project")
    if int(remote.get("module", -1)) != module_id:
        defects.append("module")
    expected_priority = {"P1": 1, "P2": 2, "P3": 3, "P4": 4}.get(
        str(case.get("priority", "P3")),
        3,
    )
    try:
        actual_priority = int(remote.get("pri", -1))
    except (TypeError, ValueError):
        actual_priority = -1
    if actual_priority != expected_priority:
        defects.append("pri")
    for field in ("title",):
        if remote.get(field) != case.get(field):
            defects.append(field)
    expected_steps = case.get("steps") or []
    actual_steps = remote.get("steps") or []
    if len(actual_steps) != len(expected_steps):
        defects.append("steps_count")
    for actual, expected in zip(actual_steps, expected_steps):
        actual_step = html.unescape(str(actual.get("step") or ""))
        actual_expect = html.unescape(str(actual.get("expect") or ""))
        if actual_step != str(expected.get("action") or "") or actual_expect != str(expected.get("expected") or ""):
            defects.append("steps_content")
            break
    expected_type = resolve_type_fields(case)[0]
    if remote.get("type") != expected_type:
        defects.append("type")
    expected_precondition = build_precondition_text(case, common_preconditions)
    if html.unescape(str(remote.get("precondition") or "")) != expected_precondition:
        defects.append("precondition")
    return defects


def main(argv: list[str] | None = None) -> int:
    """串行创建或更新用例，回读校验后更新注册表。"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--review", type=Path, required=True)
    parser.add_argument("--testcases", type=Path, required=True)
    parser.add_argument("--module-file", type=Path, required=True)
    parser.add_argument("--module-tree", type=Path, required=True)
    parser.add_argument("--registry", type=Path, required=True, help="项目根目录唯一 module_case_map.json")
    parser.add_argument("--wrapper", type=Path, default=Path(__file__).with_name("zentao_create_testcase.ps1"), help="兼容旧入口；创建命令直接调用 zentao-cli")
    parser.add_argument("--limit", type=int, default=2)
    parser.add_argument("--start-index", type=int, default=0, help="从源用例集合的零基索引开始同步")
    parser.add_argument("--all-source", action="store_true", help="同步测试用例源 YAML 中的全部用例，忽略评审清单截取范围")
    parser.add_argument("--case-ids", help="仅同步指定的源用例 ID，逗号分隔")
    parser.add_argument("--product-id", type=int, required=True)
    parser.add_argument("--module-id", type=int, required=True)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--dry-run", action="store_true", help="仅生成并校验载荷，不执行禅道远程写入")
    parser.add_argument("--delete", action="store_true", help="删除明确指定的禅道测试用例")
    parser.add_argument("--delete-case-ids", help="明确的禅道用例数字 ID 清单，逗号分隔")
    parser.add_argument("--confirm-delete", action="store_true", help="确认执行真实远程删除；与 --dry-run 互斥")
    args = parser.parse_args(argv)
    if args.delete and not args.delete_case_ids:
        parser.error("--delete requires --delete-case-ids")
    if args.delete and not args.confirm_delete:
        parser.error("--delete requires --confirm-delete")
    if args.delete and args.dry_run and args.confirm_delete:
        parser.error("--dry-run cannot be combined with --confirm-delete")
    if sys.platform == "win32":
        for path_name in ("project", "review", "testcases", "module_file", "module_tree", "registry", "wrapper"):
            path_value = getattr(args, path_name)
            normalized = re.sub(r"\\+", "/", str(path_value))
            setattr(args, path_name, Path(normalized))
    args.project = args.project.resolve()
    for path_name in ("review", "testcases", "module_file", "module_tree"):
        path_value = getattr(args, path_name)
        if not path_value.is_absolute():
            setattr(args, path_name, args.project / path_value)
    if not args.wrapper.is_absolute():
        args.wrapper = (args.project / args.wrapper).resolve()
    if not args.registry.is_absolute():
        args.registry = (args.project / args.registry).resolve()
    try:
        config = load_yaml(args.project / "config.yaml")
        validate_shared_sync_config(config, args.project)
        configured_product = config.get("zentao_product_id")
        configured_project = config.get("zentao_project_id")
        if configured_product != args.product_id or not isinstance(configured_project, int) or configured_project <= 0:
            raise SyncError("config target does not match requested product or project context")
        review = load_yaml(args.review)
        testcase_document = load_yaml(args.testcases)
        common_preconditions = build_common_preconditions_index(testcase_document)
        if args.delete:
            requested_delete_ids = [value.strip() for value in args.delete_case_ids.split(",") if value.strip()]
            if not requested_delete_ids or any(not value.isdigit() or int(value) <= 0 for value in requested_delete_ids):
                raise SyncError("--delete-case-ids must contain positive numeric IDs only")
            if len(set(requested_delete_ids)) != len(requested_delete_ids):
                raise SyncError("--delete-case-ids contains duplicate IDs")
            cases = []
        elif args.all_source:
            source_cases = testcase_document.get("cases") or []
            if not isinstance(source_cases, list) or not source_cases:
                raise SyncError("testcase source contains no cases")
            cases = [{"case_id": case.get("id")} for case in source_cases if isinstance(case, dict) and case.get("id")]
            if len(cases) != len(source_cases):
                raise SyncError("testcase source contains an invalid case")
            cases = cases[args.start_index:args.start_index + args.limit]
        else:
            cases = selected_cases(review, testcase_document, args.limit)
        if args.case_ids:
            requested_ids = {value.strip() for value in args.case_ids.split(",") if value.strip()}
            cases = [item for item in cases if str(item.get("case_id")) in requested_ids]
            if not cases:
                raise SyncError("case-ids did not match selected source cases")
        details = {} if args.delete else load_case_details(args.testcases, {str(item["case_id"]) for item in cases}, args.registry)
        req_id = str(review.get("req_id") or testcase_document.get("req_id") or (review.get("review") or {}).get("req_id") or "")
        module = resolve_module(args.project, req_id, args.module_file, args.module_tree)
        if module["id"] != args.module_id:
            raise SyncError(f"module mismatch: expected {args.module_id}, resolved {module['id']}")
        snapshot = {str(path): sha256_file(path) for path in (args.review, args.testcases, args.project / "config.yaml", args.module_file, args.module_tree)}
        source_paths = {
            "req_id": req_id,
            "testcase": relative_to_project(args.project, args.testcases),
            "case_review": relative_to_project(args.project, args.review),
        }
        result = {
            "status": "started",
            "product_id": args.product_id,
            "project_id": configured_project,
            "project_context_id": configured_project,
            "module": module,
            "source_hashes_before": snapshot,
            "records": [],
        }
        if args.delete:
            for value in requested_delete_ids:
                remote_id = int(value)
                record = {"operation": "delete", "remote_case_id": remote_id, "command": build_delete_command(remote_id)}
                try:
                    remote = remote_readback(remote_id)
                    record["readback_before"] = remote
                    defects = validate_delete_context(remote, args.product_id, args.module_id, configured_project)
                    if defects:
                        raise SyncError(f"delete target context mismatch for {remote_id}: {', '.join(defects)}")
                    if args.dry_run:
                        record.update({"status": "not_executed", "reason": "dry-run delete plan; remote delete was not called"})
                    else:
                        delete_response = run_json(record["command"])
                        record["delete_response"] = delete_response
                        post_readback = confirm_remote_deleted(remote_id)
                        record["readback_after"] = post_readback
                        record["registry"] = registry_delete_entry(args.registry, remote_id)
                        record["status"] = "validated"
                except SyncError as exc:
                    record.update({"status": "blocked", "reason": str(exc)})
                    result["records"].append(record)
                    result["status"] = "blocked"
                    break
                result["records"].append(record)
            if result["status"] != "blocked":
                result["status"] = "not_executed" if args.dry_run else "validated"
        for item in cases:
            case_id = str(item["case_id"])
            case = details[case_id]
            existing_id = case.get("zentao_case_id")
            if args.dry_run:
                payload = build_create_payload(
                    case, args.product_id, args.module_id, configured_project, common_preconditions
                )
                result["records"].append({
                    "case_id": case_id,
                    "operation": "update" if isinstance(existing_id, int) and existing_id > 0 else "create",
                    "remote_case_id": existing_id if isinstance(existing_id, int) and existing_id > 0 else None,
                    "payload": payload,
                    "status": "dry_run",
                })
                continue
            if isinstance(existing_id, int) and existing_id > 0:
                try:
                    remote_readback(existing_id)
                except SyncError as exc:
                    raise SyncError(f"registered zentao_case_id is invalid for {case_id}: {existing_id}: {exc}") from exc
                response = run_json(
                    build_update_command(case, existing_id, args.module_id, configured_project, common_preconditions)
                )
                remote_id = existing_id
                operation = "update"
            if existing_id is None or existing_id == "" or (isinstance(existing_id, int) and existing_id <= 0):
                payload = build_create_command(
                    case, args.product_id, args.module_id, configured_project, common_preconditions
                )
                response = run_json(payload)
                if not isinstance(response, dict) or not isinstance(response.get("data"), dict) or not response["data"].get("id"):
                    raise SyncError(f"create response missing data.id: {json.dumps(response, ensure_ascii=False)[:800]}")
                remote_id = int(response["data"]["id"])
                operation = "create"
            elif not (isinstance(existing_id, int) and existing_id > 0 and operation == "update"):
                raise SyncError(f"invalid zentao_case_id: {case_id}")
            readback = remote_readback(remote_id)
            defects = validate_readback(
                readback, case, args.product_id, args.module_id, configured_project, common_preconditions
            )
            record = {"case_id": case_id, "operation": operation, "remote_case_id": remote_id if not defects else None, "readback": readback, "defects": defects, "status": "validated" if not defects else "blocked"}
            result["records"].append(record)
            if defects:
                result["status"] = "blocked"
                break
            update_registry(args.registry, case, module, remote_id, source_paths)
            record["registry"] = "registered"
        if not args.delete and result["status"] == "started":
            result["status"] = "dry_run" if args.dry_run else "validated"
        after_hashes = {path: sha256_file(Path(path)) for path in snapshot}
        result["source_hashes_after"] = after_hashes
        if after_hashes != snapshot:
            raise SyncError("source hash changed during execution")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["status"] in {"validated", "dry_run", "not_executed"} else 2
    except (OSError, SyncError, KeyError, ValueError) as exc:
        print(json.dumps({"status": "blocked", "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

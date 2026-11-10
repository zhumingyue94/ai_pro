from __future__ import annotations

import argparse
import copy
import json
import os
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

VALID_MAPPING_STATUS = {"registered", "pending_registry"}
VALID_ZENTAO_STATUS = {"normal", "investigate", "deprecated", "blocked", "wait"}
REQUIRED_CASE_FIELDS = {"case_id", "title", "zentao_case_id", "mapping_status", "automation_status", "handler", "page_object", "data_contract", "check_id", "assertion_scope"}
COMMON_CASE_FIELDS = {"req_id", "module", "source_yaml_module_id", "source"}


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def dump_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def modules(registry: dict[str, Any]) -> dict[str, dict[str, Any]]:
    value = registry.get("modules_by_req_id")
    if not isinstance(value, dict):
        raise ValueError("registry must use modules_by_req_id; migrate the legacy file first")
    return value


def all_cases(registry: dict[str, Any]):
    for req_id, module in modules(registry).items():
        if module.get("req_id") != req_id:
            raise ValueError(f"module req_id mismatch: {req_id}")
        cases = module.get("cases")
        if not isinstance(cases, dict):
            raise ValueError(f"cases must be an object: {req_id}")
        for case_id, case in cases.items():
            if not isinstance(case, dict) or case_id != case.get("case_id"):
                raise ValueError(f"case key mismatch: {req_id}/{case_id}")
            if COMMON_CASE_FIELDS & set(case):
                raise ValueError(f"case contains module-level fields: {req_id}/{case_id}")
            yield req_id, case_id, case


def refresh_summary(registry: dict[str, Any]) -> None:
    records = list(all_cases(registry))
    remote_ids = [case["zentao_case_id"] for _, _, case in records if case.get("zentao_case_id") is not None]
    registry["summary"] = {
        "total_cases": len(records),
        "registered_cases": sum(case.get("zentao_case_id") is not None for _, _, case in records),
        "pending_registry": sum(case.get("mapping_status") == "pending_registry" for _, _, case in records),
        "unique_zentao_case_ids": len(set(remote_ids)),
        "automation_pending_implementation": sum(case.get("automation_status") == "pending_implementation" for _, _, case in records),
        "automation_implemented": sum(case.get("automation_status") == "implemented" for _, _, case in records),
    }


def validate_registry(registry: dict[str, Any]) -> None:
    remote_ids: dict[int, tuple[str, str]] = {}
    for req_id, case_id, case in all_cases(registry):
        if set(REQUIRED_CASE_FIELDS) - set(case):
            raise ValueError(f"missing case fields: {req_id}/{case_id}")
        remote_id = case.get("zentao_case_id")
        if remote_id is not None:
            if remote_id in remote_ids and remote_ids[remote_id] != (req_id, case_id):
                raise ValueError(f"duplicate zentao_case_id {remote_id}")
            remote_ids[remote_id] = (req_id, case_id)
        if case.get("mapping_status") not in VALID_MAPPING_STATUS:
            raise ValueError(f"invalid mapping_status: {req_id}/{case_id}")
        if case.get("zentao_status") not in VALID_ZENTAO_STATUS:
            raise ValueError(f"invalid zentao_status: {req_id}/{case_id}")
    expected = copy.deepcopy(registry.get("summary", {}))
    refresh_summary(registry)
    if registry["summary"] != expected:
        raise ValueError(f"summary mismatch: expected {registry['summary']}, actual {expected}")


def validate_case(req_id: str, case_id: str, case: dict[str, Any]) -> None:
    if case.get("case_id") != case_id:
        raise ValueError(f"case key mismatch: {req_id}/{case_id}")
    common_fields = COMMON_CASE_FIELDS & set(case)
    if common_fields:
        raise ValueError(f"case contains module-level fields: {req_id}/{case_id}: {sorted(common_fields)}")
    missing = REQUIRED_CASE_FIELDS - set(case)
    if missing:
        raise ValueError(f"case missing fields: {sorted(missing)}")


def payload_cases(payload: dict[str, Any]) -> list[dict[str, Any]]:
    records = payload.get("cases")
    if not isinstance(records, list):
        raise ValueError("payload.cases must be an array")
    seen: set[str] = set()
    for case in records:
        if not isinstance(case, dict) or not case.get("case_id"):
            raise ValueError("each case must be an object with case_id")
        case_id = case["case_id"]
        if case_id in seen:
            raise ValueError(f"duplicate case_id in payload: {case_id}")
        seen.add(case_id)
    return records


def check_isolation(before: dict[str, Any], after: dict[str, Any], req_id: str | None, case_id: str | None) -> None:
    before_modules, after_modules = modules(before), modules(after)
    for rid, old_module in before_modules.items():
        if rid != req_id:
            if after_modules.get(rid) != old_module:
                raise ValueError(f"non-target module changed: {rid}")
            continue
        if case_id is not None:
            old_cases = old_module["cases"]
            new_cases = after_modules[rid]["cases"]
            for cid, old_case in old_cases.items():
                if cid != case_id and new_cases.get(cid) != old_case:
                    raise ValueError(f"non-target case changed: {rid}/{cid}")


def apply_operation(registry: dict[str, Any], operation: str, req_id: str, case_id: str | None, payload: dict[str, Any], replace: bool) -> tuple[dict[str, Any], dict[str, Any]]:
    before = copy.deepcopy(registry)
    updated = copy.deepcopy(registry)
    grouped = modules(updated)
    exists = req_id in grouped
    if operation == "create-module":
        if exists:
            raise ValueError(f"module already exists: {req_id}")
        module = payload.get("module")
        if not isinstance(module, dict):
            raise ValueError("payload.module is required")
        cases = {case["case_id"]: case for case in payload_cases(payload)}
        for cid, case in cases.items():
            validate_case(req_id, cid, case)
        source_yaml_module_id = payload.get("source_yaml_module_id")
        source = payload.get("source")
        if source_yaml_module_id is None or not isinstance(source, dict):
            raise ValueError("payload.source_yaml_module_id and payload.source are required")
        grouped[req_id] = {"req_id": req_id, "module": module, "source_yaml_module_id": source_yaml_module_id, "source": source, "cases": cases}
    elif operation == "delete-module":
        if not exists:
            raise ValueError(f"module not found: {req_id}")
        del grouped[req_id]
    elif operation in {"update-module", "create-case", "update-case", "delete-case"}:
        if not exists:
            raise ValueError(f"module not found: {req_id}")
        target = grouped[req_id]["cases"]
        if operation == "update-module":
            incoming = payload_cases(payload)
            for case in incoming:
                validate_case(req_id, case["case_id"], case)
            if replace:
                grouped[req_id]["cases"] = {case["case_id"]: case for case in incoming}
            else:
                for case in incoming:
                    if case["case_id"] not in target:
                        raise ValueError(f"update-module cannot create case: {case['case_id']}")
                    target[case["case_id"]] = case
        else:
            if not case_id:
                raise ValueError("case_id is required")
            if operation == "create-case":
                if case_id in target:
                    raise ValueError(f"case already exists: {req_id}/{case_id}")
                case = payload.get("case")
                if not isinstance(case, dict):
                    raise ValueError("payload.case is required")
                validate_case(req_id, case_id, case)
                target[case_id] = case
            elif operation == "update-case":
                if case_id not in target:
                    raise ValueError(f"case not found: {req_id}/{case_id}")
                case = payload.get("case")
                if not isinstance(case, dict):
                    raise ValueError("payload.case is required")
                validate_case(req_id, case_id, case)
                target[case_id] = case
            else:
                if case_id not in target:
                    raise ValueError(f"case not found: {req_id}/{case_id}")
                del target[case_id]
    else:
        raise ValueError(f"unsupported operation: {operation}")
    check_isolation(before, updated, req_id, case_id if operation.endswith("case") else None)
    refresh_summary(updated)
    validate_registry(updated)
    return updated, {"operation": operation, "req_id": req_id, "case_id": case_id, "replace": replace}


def persist(registry_path: Path, before: dict, updated: dict, audit: dict, apply: bool, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    audit_path = output_dir / f"registry_operation_audit_{stamp}.json"
    audit["status"] = "applied" if apply else "dry_run_validated"
    audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if not apply:
        return
    backup = output_dir / f"module_case_map.json.bak.{stamp}"
    shutil.copy2(registry_path, backup)
    fd, name = tempfile.mkstemp(prefix="module_case_map.", suffix=".tmp", dir=registry_path.parent)
    os.close(fd)
    temp = Path(name)
    try:
        dump_json(temp, updated)
        validate_registry(load_json(temp))
        os.replace(temp, registry_path)
    finally:
        if temp.exists():
            temp.unlink()
    audit["backup"] = str(backup)
    audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="按 req_id 隔离维护模块用例注册表")
    parser.add_argument("operation", choices=["create-module", "update-module", "delete-module", "create-case", "update-case", "delete-case"])
    parser.add_argument("--req-id", required=True)
    parser.add_argument("--case-id")
    parser.add_argument("--payload", type=Path, required=False)
    parser.add_argument("--registry", type=Path, default=Path("module_case_map/module_case_map.json"))
    parser.add_argument("--output-dir", type=Path, default=Path("module_case_map"))
    parser.add_argument("--replace", action="store_true")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    registry = load_json(args.registry)
    payload = load_json(args.payload) if args.payload else {}
    updated, change = apply_operation(registry, args.operation, args.req_id, args.case_id, payload, args.replace)
    persist(args.registry, registry, updated, {"change": change, "summary_before": registry.get("summary"), "summary_after": updated.get("summary")}, args.apply, args.output_dir)
    print(json.dumps({"status": "applied" if args.apply else "dry_run_validated", **change}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

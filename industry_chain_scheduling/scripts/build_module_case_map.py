"""根据已评审的测试用例 YAML 构建项目级禅道用例注册表。

本脚本与具体项目无关，从目标项目的 config.yaml 读取项目元数据和模块别名，
不会访问禅道远程接口。
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


ZENTAO_STATUSES = {"normal", "investigate", "deprecated", "blocked", "wait"}
DEFAULT_ZENTAO_STATUS = "normal"


def _load_project_config(root: Path) -> tuple[dict[str, Any], dict[str, str]]:
    """读取项目元数据和项目专属模块别名。"""
    config_path = root / "config.yaml"
    if not config_path.is_file():
        raise FileNotFoundError(config_path)
    config = yaml.safe_load(config_path.read_text(encoding="utf-8-sig")) or {}
    project = config.get("project") or {}
    name = project.get("name")
    product_id = project.get("product_id")
    project_id = project.get("project_id")
    if not isinstance(name, str) or not name.strip():
        raise ValueError("project.name is required in config.yaml")
    if not isinstance(product_id, int) or product_id <= 0:
        raise ValueError("project.product_id must be a confirmed positive integer")
    if not isinstance(project_id, int) or project_id <= 0:
        raise ValueError("project.project_id must be a confirmed positive integer")
    aliases = (config.get("case_registry") or {}).get("module_aliases") or {}
    if not isinstance(aliases, dict):
        raise ValueError("case_registry.module_aliases must be a mapping")
    normalized_aliases = {str(key): str(value) for key, value in aliases.items()}
    metadata = {
        "name": name,
        "product_id": product_id,
        "project_id": project_id,
        "default_zentao_status": DEFAULT_ZENTAO_STATUS,
    }
    return metadata, normalized_aliases


def _parse_modules(text: str) -> dict[str, dict[str, Any]]:
    """从模块参考文档解析模块名到模块 ID 与路径的映射。"""
    result: dict[str, dict[str, Any]] = {}
    pattern = re.compile(r"^\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*(\d+)\s*\|")
    for line in text.splitlines():
        match = pattern.match(line)
        if not match:
            continue
        path, name, module_id = match.groups()
        if not module_id.isdigit() or name.strip() in {"模块名称", "---"}:
            continue
        result[name.strip()] = {"name": name.strip(), "id": int(module_id), "path": path.strip()}
    return result


def _resolve_module(
    module_name: str,
    modules: dict[str, dict[str, Any]],
    aliases: dict[str, str],
) -> dict[str, Any]:
    """按精确名称、项目配置别名或唯一后缀解析模块。"""
    if module_name in modules:
        return modules[module_name]
    alias_target = aliases.get(module_name)
    if alias_target in modules:
        return modules[alias_target]
    suffix_matches = [item for name, item in modules.items() if module_name.endswith(name)]
    if len(suffix_matches) == 1:
        return suffix_matches[0]
    raise ValueError(f"missing unambiguous module reference for {module_name}")


def _case_review_path(root: Path, tc_path: Path) -> str:
    """根据测试用例相对路径推导对应的用例评审产物相对路径。"""
    relative_path = tc_path.relative_to(root / "04_testcases")
    review_path = relative_path.with_name(
        f"REV_CASE_{relative_path.stem.removeprefix('TC_')}.yaml"
    )
    return (Path("05_case_review") / review_path).as_posix()


def build_registry(root: Path, output: Path | None = None) -> dict[str, Any]:
    """聚合目标项目测试用例与历史映射，构建项目级注册表。"""
    root = root.resolve()
    metadata, aliases = _load_project_config(root)
    tc_dir = root / "04_testcases"
    module_reference = root / "01_requirements" / "禅道模块id.md"
    output_path = output or (root / "module_case_map.json")
    if not output_path.is_absolute():
        output_path = root / output_path
    if not module_reference.is_file():
        raise FileNotFoundError(module_reference)
    modules = _parse_modules(module_reference.read_text(encoding="utf-8-sig"))
    if not modules:
        raise ValueError(f"no module mappings found in {module_reference}")

    existing_cases: dict[str, dict[str, Any]] = {}
    if output_path.is_file():
        try:
            previous = json.loads(output_path.read_text(encoding="utf-8-sig"))
            for group in (previous.get("modules_by_req_id") or {}).values():
                for previous_case in (group.get("cases") or {}).values():
                    if isinstance(previous_case, dict) and previous_case.get("case_id"):
                        existing_cases[str(previous_case["case_id"])] = previous_case
            for previous_case in previous.get("cases", []):
                if isinstance(previous_case, dict) and previous_case.get("case_id"):
                    existing_cases[str(previous_case["case_id"])] = previous_case
        except (OSError, ValueError, TypeError):
            existing_cases = {}

    groups: dict[str, dict[str, Any]] = {}
    source_files: list[str] = []
    for tc_path in sorted(tc_dir.rglob("TC_*.yaml")):
        review_relative_path = _case_review_path(root, tc_path)
        review_path = root / review_relative_path
        if not review_path.is_file():
            raise FileNotFoundError(review_path)
        document = yaml.safe_load(tc_path.read_text(encoding="utf-8-sig")) or {}
        req_id = str(document.get("req_id") or "")
        source_files.append(tc_path.relative_to(root).as_posix())
        module = _resolve_module(str(document.get("module") or ""), modules, aliases)
        module_value = {"name": module["name"], "id": module["id"], "path": module["path"]}
        group = groups.setdefault(req_id, {"req_id": req_id, "module": module_value, "source_yaml_module_id": module["id"], "source": {"testcase": tc_path.relative_to(root).as_posix(), "case_review": review_relative_path}, "cases": {}})
        if group["module"] != module_value:
            raise ValueError(f"multiple modules for req_id: {req_id}")
        for case in document.get("cases") or []:
            if not isinstance(case, dict):
                raise ValueError(f"invalid case object in {tc_path}")
            case_id = str(case.get("id") or "")
            if not case_id:
                raise ValueError(f"case without id: {tc_path}")
            previous_case = existing_cases.get(case_id, {})
            previous_zentao_status = previous_case.get("zentao_status") or DEFAULT_ZENTAO_STATUS
            if previous_zentao_status not in ZENTAO_STATUSES:
                raise ValueError(f"invalid zentao_status: {tc_path} {case_id} {previous_zentao_status!r}")
            raw_zentao_id = previous_case.get("zentao_case_id")
            if raw_zentao_id is not None and (not isinstance(raw_zentao_id, int) or raw_zentao_id <= 0):
                raise ValueError(f"invalid registered zentao_case_id: {tc_path} {case_id}")
            base_case = {
                "case_id": case_id,
                "title": case.get("title") or "",
                "zentao_case_id": raw_zentao_id,
                "zentao_status": previous_zentao_status,
                "mapping_status": "registered" if raw_zentao_id is not None else "pending_registry",
                "automation_status": "pending_implementation",
                "handler": None,
                "page_object": None,
                "data_contract": None,
                "check_id": None,
                "assertion_scope": None,
            }
            for field in ("zentao_status", "automation_status", "handler", "page_object", "data_contract", "check_id", "assertion_scope"):
                if field in previous_case:
                    base_case[field] = previous_case[field]
            group["cases"][case_id] = base_case

    all_cases = [case for group in groups.values() for case in group["cases"].values()]
    ids = [item["zentao_case_id"] for item in all_cases if item["zentao_case_id"] is not None]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate zentao_case_id values found")
    for group in groups.values():
        group["cases"] = dict(sorted(group["cases"].items(), key=lambda item: (item[1]["zentao_case_id"] is None, item[1]["zentao_case_id"] or 0, item[0])))
    implemented_count = sum(item["automation_status"] == "implemented" for item in all_cases)
    registered_count = sum(item["zentao_case_id"] is not None for item in all_cases)
    return {
        "schema_version": "2.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "project": metadata,
        "defaults": {"zentao_status": DEFAULT_ZENTAO_STATUS},
        "source": {
            "testcase_files": source_files,
            "module_reference": "01_requirements/禅道模块id.md",
            "historical_evidence": "06_zentao_sync/history/",
            "remote_readback": "historical_only",
        },
        "summary": {
            "total_cases": len(all_cases),
            "registered_cases": registered_count,
            "pending_registry": len(all_cases) - registered_count,
            "unique_zentao_case_ids": len(set(ids)),
            "automation_pending_implementation": len(all_cases) - implemented_count,
            "automation_implemented": implemented_count,
        },
        "modules_by_req_id": dict(sorted(groups.items())),
    }


def main(argv: list[str] | None = None) -> int:
    """解析命令行参数并生成或校验目标项目注册表。"""
    parser = argparse.ArgumentParser(description="构建本地 module_case_map.json 注册表。")
    parser.add_argument("--project", type=Path, default=Path.cwd(), help="项目根目录，默认当前目录")
    parser.add_argument("--output", type=Path, help="注册表输出路径，默认项目根 module_case_map.json")
    parser.add_argument("--check", action="store_true", help="只比较现有输出，不写入文件")
    args = parser.parse_args(argv)
    try:
        registry = build_registry(args.project, args.output)
    except (FileNotFoundError, ValueError) as exc:
        print(f"status=blocked reason={exc}")
        return 2
    content = json.dumps(registry, ensure_ascii=False, indent=2) + "\n"
    output_path = args.output or (args.project.resolve() / "module_case_map.json")
    if not output_path.is_absolute():
        output_path = args.project.resolve() / output_path
    if args.check:
        if not output_path.is_file():
            print("status=fail reason=registry_missing")
            return 1
        current = json.loads(output_path.read_text(encoding="utf-8-sig"))
        if current.get("modules_by_req_id") != registry.get("modules_by_req_id"):
            print("status=fail reason=registry_modules_out_of_date")
            return 1
        print(f"status=pass cases={registry['summary']['total_cases']} ids={registry['summary']['unique_zentao_case_ids']}")
        return 0
    output_path.write_text(content, encoding="utf-8")
    print(f"status=pass output={output_path} cases={registry['summary']['total_cases']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

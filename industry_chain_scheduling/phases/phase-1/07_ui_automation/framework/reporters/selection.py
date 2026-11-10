"""选择清单：RUN/selection.yaml。

记录本次 RUN 的完整本地范围、筛选条件、评审门禁快照与禅道同步历史证据，
回答"为什么是这些用例被执行"。
"""

from __future__ import annotations

from typing import Any

import yaml

from .. import case_source, options, registry as registry_mod


def build(orch) -> dict[str, Any]:
    """构造 selection.yaml 的完整文档。"""
    reg = registry_mod.load_registry()
    sources: dict[str, Any] = {}
    review_gates: dict[str, Any] = {}
    sync_evidence: dict[str, Any] = {}

    for req_id in orch.req_ids:
        path, _doc = case_source.load_testcase_doc(req_id)
        total, auto = case_source.load_testcase_count(req_id)
        sources[req_id] = {
            "source": _relative_source(path),
            "local_yaml_case_count": total,
            "local_auto_case_count": auto,
        }
        review_gates[req_id] = case_source.review_gate_summary(req_id)
        sync_evidence[req_id] = case_source.load_zentao_sync_evidence(req_id)

    records = orch.ordered_records()
    selected_ids = [str(item.get("case_id") or "") for item in records]
    selected_zentao = [int(item.get("zentao_case_id") or -1) for item in records]
    planned_entries = [entry for entry, _case in orch.planned.values()]
    fixed_count = sum(
        1 for entry in planned_entries if _zentao_of(entry) in registry_mod.FIXED_MAPPING_IDS
    )
    executed = sum(1 for item in records if not item.get("excluded") and item.get("status") not in ("excluded",))
    excluded = sum(1 for item in records if item.get("excluded"))
    first_source = next(iter(sources.values()), {}).get("source", "")

    return {
        "run_id": orch.run_id,
        "source": first_source,
        "sources": sources,
        "filter": orch.filter_desc,
        "requirement_ids": orch.req_ids,
        "module_names": orch.module_names,
        "local_yaml_case_count": sum(int(item.get("local_yaml_case_count") or 0) for item in sources.values()),
        "local_auto_case_count": sum(int(item.get("local_auto_case_count") or 0) for item in sources.values()),
        "selected_case_ids": selected_ids,
        "selected_zentao_case_ids": selected_zentao,
        "new_mapping_count": 0,
        "fixed_mapping_count": fixed_count,
        "executed_case_count": executed if not orch.dry_run else 0,
        "excluded_case_count": excluded,
        "pending_registry_count": reg.pending_registry_count,
        "environment": _environment(orch),
        "browser_started": orch.browser_started,
        "dry_run": orch.dry_run,
        "test_data_prefix": f"{options.TEST_DATA_PREFIX}{{run_id}}_",
        "review_gate": review_gates,
        "zentao_sync_evidence": sync_evidence,
        "generated_at": orch.started_at,
    }


def _relative_source(path) -> str:
    """把本地用例文件路径转为相对仓库根的路径；失败时返回原路径字符串。"""
    try:
        return path.resolve().relative_to(registry_mod.ROOT.resolve()).as_posix()
    except (ValueError, OSError):
        return str(path)


def _environment(orch) -> dict[str, Any]:
    """返回环境摘要；浏览器未启动时给出明确标记而非伪造 host。"""
    if orch.config_error or not orch.browser_started:
        host = "browser_not_started" if not orch.browser_started else "unresolved-host"
        return {"base_host": host, "headless": str(options.HEADLESS).lower()}
    settings = orch.settings_snapshot
    return settings


def _zentao_of(entry: dict) -> int:
    """返回条目的数字禅道用例编号，失败时返回 -1。"""
    try:
        return int(entry.get("zentao_case_id"))
    except (TypeError, ValueError):
        return -1


def write(orch, records: list[dict], bugs: list[dict]) -> None:
    """写出 selection.yaml。"""
    if orch.run_dir is None:
        return
    document = build(orch)
    document["executed_case_count"] = sum(1 for item in records if not item.get("excluded"))
    target = orch.run_dir / "selection.yaml"
    target.write_text(
        yaml.safe_dump(document, allow_unicode=True, sort_keys=False), encoding="utf-8"
    )

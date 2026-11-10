from __future__ import annotations

import argparse
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment

CASE_SHEET = "iot平台-全部用例"
BUG_SHEET = "iot二期开发-Bug"
CASE_COLUMNS = [
    "用例编号", "禅道编号", "所属产品", "所属模块", "用例名称", "前置条件", "步骤", "预期",
    "实际情况", "优先级", "用例类型", "用例状态", "执行人", "执行时间", "结果", "附件", "关联bug",
]
BUG_COLUMNS = [
    "Bug编号", "禅道Bug编号", "所属产品", "所属模块", "所属项目", "Bug标题", "严重程度", "优先级",
    "Bug类型", "重现步骤", "Bug状态", "由谁创建", "创建日期", "解决日期", "解决者", "由谁关闭",
    "关闭日期", "相关用例", "附件",
]
BODY_ALIGN = Alignment(vertical="top", wrap_text=True)
RESULT_TYPES = {"passed", "product_defect", "test_script_error", "test_case_error", "blocked", "excluded"}


def _markdown_cell(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip().replace("|", "\\|").replace("\r\n", "<br>").replace("\n", "<br>").replace("\r", "<br>")


def _read_workbook_rows(path: Path, sheet_name: str) -> tuple[list[str], list[list[str]]]:
    workbook = load_workbook(path, data_only=False, read_only=True)
    try:
        sheet = workbook[sheet_name]
        rows = [[_markdown_cell(value) for value in row] for row in sheet.iter_rows(values_only=True)]
    finally:
        workbook.close()
    if not rows:
        return [], []
    width = max(len(row) for row in rows)
    normalized = [row + [""] * (width - len(row)) for row in rows]
    return normalized[0], normalized[1:]


def _detail_lines(label: str, value: str) -> list[str]:
    if not value:
        return [f"**{label}**:"]
    parts = value.split("<br>")
    if len(parts) == 1:
        return [f"**{label}**: {parts[0]}"]
    return [f"**{label}**:", *(f"- {part}" for part in parts if part)]


def _rows_to_detail_markdown(path: Path, sheet_name: str, title_label: str) -> str:
    headers, rows = _read_workbook_rows(path, sheet_name)
    if not headers:
        return f"# {title_label}\n\n- 总数：**0**\n"
    blocks = [f"# {title_label}", "", f"- 总数：**{len(rows)}**", ""]
    for index, row in enumerate(rows, 1):
        record = dict(zip(headers, row))
        identifier = record.get("用例编号") or record.get("Bug编号") or f"记录-{index:03d}"
        blocks.extend([f"## {identifier}", ""])
        for header in headers:
            blocks.extend(_detail_lines(header, record.get(header, "")))
            blocks.append("")
    return "\n".join(blocks).rstrip() + "\n"


def _write_workbook_markdown(workbook_path: Path, markdown_path: Path, sheet_name: str) -> None:
    title = "测试结果" if sheet_name == CASE_SHEET else "缺陷结果"
    markdown_path.write_text(_rows_to_detail_markdown(workbook_path, sheet_name, title), encoding="utf-8")


def _template_path(template_path: Path | None = None) -> Path:
    configured = template_path or os.getenv("CASE_RESULTS_TEMPLATE")
    if configured:
        return Path(configured)
    candidates = [Path.cwd() / "references" / "case_result.xlsx", Path(__file__).resolve().parents[1] / "references" / "case_result.xlsx"]
    return next((candidate for candidate in candidates if candidate.is_file()), candidates[-1])


def _phase_root_from_ui_root(ui_root: Path) -> Path:
    return ui_root.parent


def _load_env_value(env_path: Path, key: str) -> str:
    if not env_path.is_file():
        return ""
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        if name.strip() == key:
            return value.strip().strip('"').strip("'")
    return ""


def _load_case_metadata(phase_root: Path, case_ids: list[str], req_id: str) -> dict[str, dict[str, Any]]:
    source = phase_root / "04_testcases" / f"TC_{req_id.split('-', 1)[-1]}.yaml"
    if not source.is_file():
        source = phase_root / "04_testcases" / f"TC_{req_id}.yaml"
    document = yaml.safe_load(source.read_text(encoding="utf-8")) if source.is_file() else {}
    common = {item.get("id"): item for item in document.get("common_preconditions", []) if isinstance(item, dict)}
    metadata: dict[str, dict[str, Any]] = {}
    for case in document.get("cases", []) if isinstance(document, dict) else []:
        if not isinstance(case, dict) or case.get("id") not in case_ids:
            continue
        preconditions = [str(value) for value in case.get("preconditions", [])]
        common_item = common.get(case.get("common_preconditions_ref"), {})
        common_steps: list[str] = []
        if common_item:
            preconditions.extend(str(value) for value in common_item.get("conditions", []))
            common_steps.extend(
                f"{step.get('action', '')}；{step.get('expected', '')}"
                for step in common_item.get("steps", [])
                if isinstance(step, dict) and (step.get("action") or step.get("expected"))
            )
        steps = [step for step in case.get("steps", []) if isinstance(step, dict)]
        metadata[case["id"]] = {
            "title": case.get("title", ""),
            "preconditions": "\n".join(value for value in preconditions if value),
            "common_precondition_steps": common_steps,
            "steps": steps,
            "priority": case.get("priority", ""),
            "case_type": case.get("type", ""),
            "feature": case.get("feature", ""),
            "auto": case.get("auto"),
        }
    return metadata


def _load_project_data(phase_root: Path, req_id: str, module_id: int | str, module_path: str | None, project_name: str | None) -> dict[str, Any]:
    config = yaml.safe_load((phase_root / "config.yaml").read_text(encoding="utf-8")) if (phase_root / "config.yaml").is_file() else {}
    registry = json.loads((phase_root / "module_case_map.json").read_text(encoding="utf-8-sig")) if (phase_root / "module_case_map.json").is_file() else {}
    project = registry.get("project", {})
    module = registry.get("modules_by_req_id", {}).get(req_id, {}).get("module", {})
    product_name = config.get("zentao_product_name") or project.get("name", "")
    product_id = config.get("zentao_product_id") or project.get("product_id", "")
    project_title = config.get("zentao_project_name") or ""
    project_id = config.get("zentao_project_id") or project.get("project_id", "")
    return {
        "product": f"{product_name}(#{product_id})" if product_id != "" else str(product_name),
        "project": project_name or (f"{project_title}(#{project_id})" if project_title and project_id != "" else project_title),
        "module": module_path or (f"{module.get('path', '')}(#{module.get('id', module_id)})" if module else str(module_id)),
        "module_name": module.get("name", ""),
        "module_id": module.get("id", module_id),
        "cases": registry.get("modules_by_req_id", {}).get(req_id, {}).get("cases", {}),
        "username": _load_env_value(phase_root / ".env", "UI_TEST_USERNAME") or "自动化",
    }


def _existing_evidence(run_dir: Path, evidence: dict[str, Any]) -> list[str]:
    values: list[str] = []
    for key in ("screenshots", "videos"):
        for raw in evidence.get(key, []) if isinstance(evidence, dict) else []:
            candidate = Path(str(raw))
            absolute = candidate if candidate.is_absolute() else run_dir / candidate
            if absolute.is_file():
                values.append(str(raw).replace("\\", "/"))
    return values


def _case_execution(case: dict[str, Any]) -> dict[str, Any]:
    execution = case.get("execution")
    return execution if isinstance(execution, dict) else case


def _case_evidence(case: dict[str, Any]) -> dict[str, Any]:
    evidence = _case_execution(case).get("evidence", {})
    return evidence if isinstance(evidence, dict) else {}


def _build_case_info(case_id: str, metadata: dict[str, Any], project: dict[str, Any]) -> dict[str, Any]:
    mapping = project.get("cases", {}).get(case_id, {})
    return {
        "case_number": case_id,
        "zentao_case_id": mapping.get("zentao_case_id"),
        "product": project.get("product", ""),
        "module": project.get("module", ""),
        "title": metadata.get("title", ""),
        "preconditions": metadata.get("preconditions", ""),
        "priority": metadata.get("priority", ""),
        "case_type": metadata.get("case_type", ""),
        "steps": [
            {"action": step.get("action", ""), "expected": step.get("expected", "")}
            for step in metadata.get("steps", [])
        ],
    }


def _build_execution(raw: dict[str, Any], run_dir: Path, executed_at: str, project: dict[str, Any], bug_id: str = "") -> dict[str, Any]:
    classification = raw.get("result", "test_script_error")
    status = "正常" if classification == "passed" else "阻塞" if classification == "blocked" else "失败"
    evidence = raw.get("evidence", {}) if isinstance(raw.get("evidence", {}), dict) else {}
    return {
        "reason": raw.get("reason", ""),
        "status": status,
        "executor": raw.get("executor", project.get("username", "自动化")),
        "executed_at": executed_at,
        "result": classification,
        "evidence": {
            "screenshots": [str(item).replace("\\", "/") for item in evidence.get("screenshots", [])],
            "videos": [str(item).replace("\\", "/") for item in evidence.get("videos", [])],
            "hashes": dict(evidence.get("hashes", {})) if isinstance(evidence.get("hashes", {}), dict) else {},
        },
        "related_bug": bug_id,
    }


def _format_case_preconditions(metadata: dict[str, Any], result: dict[str, Any]) -> str:
    preparation = [str(value) for value in str(metadata.get("preconditions", "")).splitlines() if str(value).strip()]
    steps = [str(value) for value in metadata.get("common_precondition_steps", []) if str(value).strip()]
    sections: list[tuple[str, list[str]]] = []
    if preparation:
        sections.append(("前置准备", preparation))
    if steps:
        sections.append(("前置步骤", steps))
    if not sections:
        fallback = str(result.get("preconditions", "")).strip()
        if fallback:
            sections.append(("前置准备", [fallback]))
    lines: list[str] = []
    for title, items in sections:
        if lines:
            lines.append("")
        lines.append(f"{title}：")
        lines.extend(f"{index}、{item}" for index, item in enumerate(items, start=1))
    return "\n".join(lines)


def _case_row(result: dict[str, Any], metadata: dict[str, Any], project: dict[str, Any], bug_map: dict[str, str], run_dir: Path, executed_at: str) -> list[Any]:
    case_id = result.get("case_id", "")
    execution = _case_execution(result)
    case_info = result.get("case_info") if isinstance(result.get("case_info"), dict) else _build_case_info(case_id, metadata, project)
    classification = execution.get("result", "test_script_error")
    outcome = "通过" if classification == "passed" else "阻塞" if classification == "blocked" else "失败"
    status = execution.get("status") or ("正常" if classification == "passed" else "阻塞" if classification == "blocked" else "失败")
    steps = case_info.get("steps", [])
    preconditions = _format_case_preconditions(metadata, result)
    step_text = "\n".join(f"{index}. {step.get('action', '')}" for index, step in enumerate(steps, 1) if step.get("action"))
    expected = "\n".join(f"{index}. {step.get('expected', '')}" for index, step in enumerate(steps, 1) if step.get("expected"))
    evidence = _existing_evidence(run_dir, _case_evidence(result))
    return [
        f"{case_id}\t", case_info.get("zentao_case_id"), case_info.get("product", project["product"]), case_info.get("module", project["module"]),
        case_info.get("title", ""), preconditions,
        step_text or "", expected, execution.get("reason", ""), case_info.get("priority", ""),
        case_info.get("case_type", ""), status, execution.get("executor", project["username"]),
        execution.get("executed_at", executed_at), outcome, "\n".join(evidence), execution.get("related_bug") or bug_map.get(case_id, ""),
    ]


def write_case_report(case_result: dict[str, Any], run_dir: Path) -> Path:
    """写出单个用例的标准 YAML 结果和证据索引。"""
    run_dir.mkdir(parents=True, exist_ok=True)
    result = dict(case_result)
    case_id = str(result.get("case_id", ""))
    execution = _case_execution(result)
    classification = execution.get("result", "test_script_error")
    evidence = _case_evidence(result)
    normalized_case = {
        "case_id": case_id,
        "case_info": result.get("case_info", {}),
        "execution": {
            "reason": execution.get("reason", ""),
            "status": execution.get("status", "失败"),
            "executor": execution.get("executor", "自动化"),
            "executed_at": execution.get("executed_at", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            "result": classification,
            "evidence": {
                "screenshots": list(evidence.get("screenshots", [])),
                "videos": list(evidence.get("videos", [])),
                "hashes": dict(evidence.get("hashes", {})),
            },
            "related_bug": execution.get("related_bug", ""),
        },
    }
    result_path = run_dir / "results.yaml"
    summary = {"total": 1, str(classification): 1}
    result_path.write_text(yaml.safe_dump({"run_id": run_dir.name, "summary": summary, "cases": [normalized_case], "headless": False, "remote_bug_created": False}, allow_unicode=True, sort_keys=False), encoding="utf-8")
    (run_dir / "hashes").mkdir(parents=True, exist_ok=True)
    (run_dir / "hashes" / "sha256.yaml").write_text(yaml.safe_dump(evidence.get("hashes", {}), allow_unicode=True, sort_keys=False), encoding="utf-8")
    return result_path


def write_case_results(path: Path, result: dict[str, Any] | list[dict[str, Any]], *, template_path: Path | None = None, project_name: str | None = None, module_path: str | None = None, preconditions: str | None = None, bug_map: dict[str, str] | None = None, metadata: dict[str, dict[str, Any]] | None = None, project: dict[str, Any] | None = None, run_dir: Path | None = None, executed_at: str | None = None) -> None:
    results = [result] if isinstance(result, dict) else result
    run_dir = run_dir or path.parent
    project = project or {"product": project_name or "", "module": module_path or "", "cases": {}, "username": "自动化"}
    metadata = metadata or {}
    bug_map = bug_map or {}
    executed_at = executed_at or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    template = _template_path(template_path)
    workbook = load_workbook(template) if template.is_file() else Workbook()
    if CASE_SHEET in workbook.sheetnames:
        sheet = workbook[CASE_SHEET]
        sheet.delete_rows(1, sheet.max_row)
    else:
        sheet = workbook.active
        sheet.title = CASE_SHEET
    sheet.append(CASE_COLUMNS)
    for row, item in enumerate(results, 2):
        item.setdefault("case_id", item.get("zentao_case_id", ""))
        for column, value in enumerate(_case_row(item, metadata.get(item.get("case_id", ""), {}), project, bug_map, run_dir, executed_at), 1):
            sheet.cell(row, column, value).alignment = BODY_ALIGN
    sheet.sheet_view.showGridLines = False
    path.parent.mkdir(parents=True, exist_ok=True)
    workbook.save(path)


def _format_bug_preconditions(metadata: dict[str, Any], result: dict[str, Any]) -> str:
    preparation = [str(value) for value in str(metadata.get("preconditions", "")).splitlines() if str(value).strip()]
    steps = metadata.get("common_precondition_steps") or []
    sections: list[tuple[str, list[str]]] = []
    if preparation:
        sections.append(("前置准备", preparation))
    if steps:
        sections.append(("前置步骤", [str(value) for value in steps if str(value).strip()]))
    if not sections:
        fallback = str(result.get("preconditions", "")).strip()
        if fallback:
            sections.append(("前置准备", [fallback]))
    lines: list[str] = []
    for title, items in sections:
        if lines:
            lines.append("")
        lines.append(f"{title}：")
        lines.extend(f"{index}、{item}" for index, item in enumerate(items, start=1))
    return "\n".join(lines)


def _bug_row(result: dict[str, Any], metadata: dict[str, Any], project: dict[str, Any], bug_id: str, run_dir: Path, username: str, created_at: str) -> list[Any]:
    case_id = result.get("case_id", "")
    execution = _case_execution(result)
    title = f"【{project.get('module_name') or project.get('module', '')}】{metadata.get('title') or case_id} {execution.get('reason', '')}"[:50]
    preconditions = _format_bug_preconditions(metadata, result)
    steps = metadata.get("steps", [])
    reproduce = "\n".join(f"[步骤] {step.get('action', '')}\n[结果] {execution.get('reason', '')}\n[期望] {step.get('expected', '')}" for step in steps)
    if not reproduce:
        reproduce = f"[步骤] 执行用例 {case_id}\n[结果] {execution.get('reason', '')}\n[期望] 符合测试用例预期。"
    if preconditions:
        reproduce = f"{preconditions}\n\n{reproduce}"
    evidence = "\n".join(_existing_evidence(run_dir, _case_evidence(result)))
    mapping = project["cases"].get(case_id, {})
    related = f"{metadata.get('title', case_id)}(#{mapping.get('zentao_case_id', '')})"
    return [bug_id, "", project.get("product", ""), project.get("module", ""), project.get("project", ""), title, "3", "3", "代码错误(#codeerror)", reproduce, "激活(#active)", username, created_at, "", "", "", "", related, evidence]


def write_bug_report(path: Path, *, case_results: list[dict[str, Any]], run_dir: Path, project: dict[str, Any], metadata: dict[str, dict[str, Any]], created_at: str | None = None) -> dict[str, str]:
    created_at = created_at or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    candidates = [item for item in case_results if _case_execution(item).get("result") == "product_defect"]
    bug_map = {item.get("case_id", ""): f"BUG-{index:06d}" for index, item in enumerate(candidates, 1)}
    template = run_dir / "bug.xlsx"
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = BUG_SHEET
    sheet.append(BUG_COLUMNS)
    for row, item in enumerate(candidates, 2):
        for column, value in enumerate(_bug_row(item, metadata.get(item.get("case_id", ""), {}), project, bug_map[item.get("case_id", "")], run_dir, project.get("username", "自动化"), created_at), 1):
            sheet.cell(row, column, value).alignment = BODY_ALIGN
    sheet.sheet_view.showGridLines = False
    path.parent.mkdir(parents=True, exist_ok=True)
    workbook.save(path)
    return bug_map


def _write_allure_results(run_dir: Path, req_id: str, case_results: list[dict[str, Any]], metadata: dict[str, dict[str, Any]]) -> Path:
    results_dir = run_dir / "allure-results"
    results_dir.mkdir(parents=True, exist_ok=True)
    for index, case in enumerate(case_results):
        execution = _case_execution(case)
        case_id = case.get("case_id", "")
        classification = execution.get("result", "test_script_error")
        status = "passed" if classification == "passed" else "failed" if classification == "product_defect" else "broken"
        payload = {
            "uuid": f"{run_dir.name}-{index}", "historyId": case_id, "name": metadata.get(case_id, {}).get("title", case_id),
            "status": status, "stage": "finished", "statusDetails": {"message": execution.get("reason", "")},
            "labels": [{"name": "suite", "value": req_id}, {"name": "testCaseId", "value": case_id}],
            "steps": [{"name": step.get("action", ""), "status": status} for step in metadata.get(case_id, {}).get("steps", [])],
            "attachments": [], "start": int(datetime.now().timestamp() * 1000), "stop": int(datetime.now().timestamp() * 1000),
        }
        (results_dir / f"{index}-{case_id or 'case'}-result.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return results_dir


def generate_allure_html(results_dir: Path, output_dir: Path) -> bool:
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    try:
        completed = subprocess.run(["allure", "generate", str(results_dir), "-o", str(output_dir), "--clean"], check=False, capture_output=True, text=True)
    except OSError:
        return False
    return completed.returncode == 0 and (output_dir / "index.html").is_file()


def write_review_reports(run_dir: Path, run_id: str, req_id: str, module_id: int | str, case_results: list[dict[str, Any]], summary: dict[str, int]) -> None:
    review = {
        "run_id": run_id,
        "req_id": req_id,
        "module_id": module_id,
        "remote_bug_created": False,
        "summary": summary,
        "cases": [{"case_id": item.get("case_id"), "result": _case_execution(item).get("result"), "reason": _case_execution(item).get("reason", "")} for item in case_results],
    }
    (run_dir / "bugs_review.yaml").write_text(yaml.safe_dump(review, allow_unicode=True, sort_keys=False), encoding="utf-8")


def write_module_handoff(ui_root: Path, run_id: str, req_id: str, module_id: int | str, module_name: str, case_ids: list[str], summary: dict[str, int], case_results: list[dict[str, Any]]) -> None:
    handoff_dir = ui_root / "HANDOFF"
    handoff_dir.mkdir(parents=True, exist_ok=True)
    defect_cases = [item for item in case_results if _case_execution(item).get("result") == "product_defect"]
    lines = [
        f"# {req_id} UI 自动化交接", "", f"- module_id：`{module_id if module_id not in (None, '') else 'module_id_missing'}`",
        f"- 模块：`{module_name}`", f"- 执行范围：`{', '.join(case_ids)}`", f"- RUN：`07_ui_automation/reports/{run_id}/`",
        f"- 统计：`{yaml.safe_dump(summary, allow_unicode=True, sort_keys=False).strip().replace(chr(10), '; ')}`",
        f"- 缺陷数量：`{len(defect_cases)}`", "- 远程 Bug：未创建", "- Allure 原始证据：`allure-results/`", "- 不在 RUN 目录生成 Handoff.md。", "",
    ]
    if defect_cases:
        lines.append("## 已确认产品缺陷")
        lines.extend(f"- `{item.get('case_id')}`：{_case_execution(item).get('reason', '')}" for item in defect_cases)
    else:
        lines.append("## 缺陷结论\n未确认产品行为缺陷。")
    (handoff_dir / f"{req_id}_HANDOFF.md").write_text("\\n".join(lines) + "\\n", encoding="utf-8")


def _load_results_file(path: Path) -> dict[str, Any]:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        raise ValueError(f"无法读取结构化执行结果：{path}：{type(exc).__name__}: {exc}") from exc
    if isinstance(value, list):
        return {"cases": value}
    if not isinstance(value, dict) or not isinstance(value.get("cases"), list):
        raise ValueError("结构化执行结果必须是包含 cases 列表的 YAML/JSON 对象")
    return value


def _normalize_results(case_ids: list[str], metadata: dict[str, dict[str, Any]], supplied: list[Any], run_id: str) -> list[dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}
    errors: dict[str, list[str]] = {}
    for raw in supplied:
        if not isinstance(raw, dict):
            errors.setdefault("<input>", []).append("结果项不是对象")
            continue
        case_id = str(raw.get("case_id", "")).strip()
        if not case_id:
            errors.setdefault("<input>", []).append("结果项缺少 case_id")
            continue
        if case_id not in metadata:
            errors.setdefault(case_id, []).append("case_id 不属于最新用例")
            continue
        if case_id in indexed:
            errors.setdefault(case_id, []).append("case_id 重复")
            continue
        indexed[case_id] = dict(raw)
    normalized: list[dict[str, Any]] = []
    for case_id in case_ids:
        item = metadata.get(case_id)
        if item is None:
            normalized.append({"case_id": case_id, "result": "test_case_error", "reason": "最新用例文件中不存在该 case_id", "evidence": {}})
            continue
        if item.get("auto") != "auto":
            normalized.append({"case_id": case_id, "result": "excluded", "reason": "auto 字段为 no，按资格规则排除", "evidence": {}})
            continue
        result = indexed.get(case_id)
        if result is None:
            normalized.append({"case_id": case_id, "result": "test_case_error", "reason": "结构化执行结果缺少该 auto 用例", "evidence": {}})
            continue
        result["case_id"] = case_id
        result.setdefault("reason", "")
        result.setdefault("evidence", {})
        if result.get("result") not in RESULT_TYPES:
            invalid_result = result.get("result", "")
            result["result"] = "test_case_error"
            result["reason"] = f"非法结果分类：{invalid_result}"
        if case_id in errors:
            result["result"] = "test_case_error"
            result["reason"] = "；".join(errors[case_id])
        normalized.append(result)
    for case_id, messages in errors.items():
        if case_id not in case_ids:
            normalized.append({"case_id": case_id, "run_id": run_id, "result": "test_case_error", "reason": "；".join(messages), "evidence": {}})
    return normalized


def run_cases(*, ui_root: Path, case_ids: list[str], req_id: str, module_id: int | str, module_name: str, results_file: Path, report_root: Path | None = None, template_path: Path | None = None, project_name: str | None = None, module_path: str | None = None, preconditions: str | None = None, headless: bool = False) -> tuple[str, Path, list[dict[str, Any]]]:
    if headless:
        raise ValueError("此执行器固定要求 headless=False")
    run_id = datetime.now(timezone.utc).strftime("RUN_%Y%m%dT%H%M%SZ")
    report_root = report_root or ui_root / "reports"
    run_dir = report_root / run_id
    metadata = _load_case_metadata(ui_root.parent, case_ids, req_id)
    payload = _load_results_file(results_file)
    case_results = _normalize_results(case_ids, metadata, payload["cases"], run_id)
    write_batch_report(case_results, run_dir, run_id=run_id, req_id=req_id, module_id=module_id, module_name=module_name, case_ids=case_ids, template_path=template_path, project_name=project_name, module_path=module_path, preconditions=preconditions)
    return run_id, run_dir, case_results


def write_batch_report(case_results: list[dict[str, Any]], run_dir: Path, *, run_id: str | None = None, req_id: str = "", module_id: int | str = "", module_name: str = "", case_ids: list[str] | None = None, template_path: Path | None = None, project_name: str | None = None, module_path: str | None = None, preconditions: str | None = None) -> None:
    """写出批量用例的完整汇总报告。"""
    write_run_report(
        run_dir=run_dir,
        run_id=run_id or run_dir.name,
        req_id=req_id,
        module_id=module_id,
        module_name=module_name,
        case_ids=case_ids or [str(item.get("case_id", "")) for item in case_results],
        case_results=case_results,
        template_path=template_path,
        project_name=project_name,
        module_path=module_path,
        preconditions=preconditions,
    )


def write_run_report(*, run_dir: Path, run_id: str, req_id: str, module_id: int | str, module_name: str, case_ids: list[str], case_results: list[dict[str, Any]], template_path: Path | None = None, project_name: str | None = None, module_path: str | None = None, preconditions: str | None = None) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    phase_root = run_dir.parent.parent.parent
    project = _load_project_data(phase_root, req_id, module_id, module_path, project_name)
    metadata = _load_case_metadata(phase_root, case_ids, req_id)
    executed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    bug_candidates = [item for item in case_results if item.get("result") == "product_defect"]
    bug_map = {item.get("case_id", ""): f"BUG-{index:06d}" for index, item in enumerate(bug_candidates, 1)}
    normalized_cases: list[dict[str, Any]] = []
    evidence = {"screenshots": [], "videos": [], "hashes": {}}
    for raw in case_results:
        case_id = str(raw.get("case_id", ""))
        classification = raw.get("result", "test_script_error")
        case_info = _build_case_info(case_id, metadata.get(case_id, {}), project)
        execution = _build_execution(raw, run_dir, executed_at, project, bug_map.get(case_id, ""))
        normalized_cases.append({"case_id": case_id, "case_info": case_info, "execution": execution})
        evidence["screenshots"].extend(execution["evidence"]["screenshots"])
        evidence["videos"].extend(execution["evidence"]["videos"])
        evidence["hashes"].update(execution["evidence"]["hashes"])
    summary: dict[str, int] = {"total": len(normalized_cases)}
    for case in normalized_cases:
        classification = case["execution"]["result"]
        summary[classification] = summary.get(classification, 0) + 1
    (run_dir / "selection.yaml").write_text(yaml.safe_dump({"run_id": run_id, "req_id": req_id, "module_id": module_id, "module_name": module_name, "selected_cases": case_ids, "headless": False, "remote_bug_creation": "forbidden"}, allow_unicode=True, sort_keys=False), encoding="utf-8")
    for directory in ("logs", "screenshots", "videos", "hashes"):
        (run_dir / directory).mkdir(exist_ok=True)
    (run_dir / "results.yaml").write_text(yaml.safe_dump({"run_id": run_id, "summary": summary, "cases": normalized_cases, "headless": False, "remote_bug_created": False}, allow_unicode=True, sort_keys=False), encoding="utf-8")
    (run_dir / "hashes" / "sha256.yaml").write_text(yaml.safe_dump(evidence["hashes"], allow_unicode=True, sort_keys=False), encoding="utf-8")
    _write_allure_results(run_dir, req_id, normalized_cases, metadata)
    generate_allure_html(run_dir / "allure-results", run_dir / "allure-report")
    write_bug_report(run_dir / "bug.xlsx", case_results=normalized_cases, run_dir=run_dir, project=project, metadata=metadata, created_at=executed_at)
    write_case_results(run_dir / "case_results.xlsx", normalized_cases, template_path=template_path, project_name=project_name, module_path=module_path, preconditions=preconditions, bug_map=bug_map, metadata=metadata, project=project, run_dir=run_dir, executed_at=executed_at)
    write_review_reports(run_dir, run_id, req_id, module_id, normalized_cases, summary)
    write_module_handoff(run_dir.parent.parent, run_id, req_id, module_id, module_name, case_ids, summary, normalized_cases)


def main() -> int:
    parser = argparse.ArgumentParser(description="消费结构化 UI 执行结果并生成 RUN 报告")
    parser.add_argument("--ui-root", required=True, type=Path)
    parser.add_argument("--results-file", required=True, type=Path)
    parser.add_argument("--report-root", type=Path)
    parser.add_argument("--template-path", type=Path)
    parser.add_argument("--req-id", required=True)
    parser.add_argument("--module-id", required=True)
    parser.add_argument("--module-name", required=True)
    parser.add_argument("--project-name")
    parser.add_argument("--module-path")
    parser.add_argument("case_ids", nargs="+")
    args = parser.parse_args()
    run_id, run_dir, results = run_cases(ui_root=args.ui_root, case_ids=args.case_ids, req_id=args.req_id, module_id=args.module_id, module_name=args.module_name, results_file=args.results_file, report_root=args.report_root, template_path=args.template_path, project_name=args.project_name, module_path=args.module_path, headless=False)
    summary: dict[str, int] = {"total": len(results)}
    for item in results:
        result = item.get("result", "test_script_error")
        summary[result] = summary.get(result, 0) + 1
    print(yaml.safe_dump({"run_id": run_id, "summary": summary, "report": str(run_dir), "allure_report": str(run_dir / "allure-report" / "index.html") if (run_dir / "allure-report" / "index.html").is_file() else None}, allow_unicode=True, sort_keys=False))
    return 0 if summary.get("passed", 0) == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())

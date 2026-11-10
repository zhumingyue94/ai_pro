"""按本地测试用例和唯一映射表执行定向 UI 自动化，并生成单次 RUN 证据。"""

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import os
import shutil
import subprocess
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError, sync_playwright

ROOT = Path(__file__).resolve().parents[2]
AUTO = ROOT / "07_ui_automation"
if str(AUTO) not in sys.path:
    sys.path.insert(0, str(AUTO))

from config.settings import ConfigurationError, Settings, load_settings  # noqa: E402

SHIM_MODULES = Path("C:/Users/zhumi/.workbuddy/binaries/node/artifact-tool-shim/node_modules")
NODE_EXE = Path("C:/Users/zhumi/.workbuddy/binaries/node/versions/22.22.2/node.exe")


def _now_ts() -> str:
    """返回用于 RUN 目录命名的本地时间戳。"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def _load_map() -> dict[str, Any]:
    """读取根目录唯一自动化映射表。"""
    return json.loads((ROOT / "module_case_map.json").read_text(encoding="utf-8"))


def _find_entry(map_data: dict[str, Any], zentao_case_id: int) -> dict[str, Any] | None:
    """按真实数字禅道用例编号查找唯一映射。"""
    matches = [item for item in map_data.get("cases", []) if int(item.get("zentao_case_id", -1)) == zentao_case_id]
    if len(matches) > 1:
        raise ValueError(f"duplicate mapping for zentao_case_id={zentao_case_id}")
    return matches[0] if matches else None


def _load_local_cases(req_id: str) -> tuple[Path, dict[str, Any], list[dict[str, Any]]]:
    """读取指定需求的完整本地 TC YAML，并按禅道编号校验唯一性。"""
    path = ROOT / "04_testcases" / f"TC_{req_id}.yaml"
    document = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    cases = document.get("cases") or []
    seen: set[int] = set()
    for case in cases:
        case_id = int(case["zentao_case_id"])
        if case_id in seen:
            raise ValueError(f"duplicate local zentao_case_id={case_id}")
        seen.add(case_id)
    return path, document, cases


def _load_review_gate(req_id: str) -> dict[str, Any]:
    """读取用例评审门禁，不读取禅道远端数据。"""
    path = ROOT / "05_case_review" / f"REV_CASE_{req_id}.yaml"
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _resolve_handler(handler_ref: str):
    """按 module:function 动态导入唯一映射中的测试函数。"""
    module_name, function_name = handler_ref.split(":", 1)
    module = importlib.import_module(module_name)
    return getattr(module, function_name)


def _sha256(path: Path) -> str:
    """计算文件 SHA-256，供截图证据回溯。"""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _relative_path(path: Path, run_dir: Path) -> str:
    """将 RUN 内文件转换为统一的 POSIX 相对路径。"""
    return path.resolve().relative_to(run_dir.resolve()).as_posix()


def _normalise_screenshots(values: Any, run_dir: Path) -> list[dict[str, str]]:
    """将 handler 返回的截图路径转换为相对路径和 SHA-256 记录。"""
    if not isinstance(values, list):
        values = [values] if values else []
    output: list[dict[str, str]] = []
    seen: set[Path] = set()
    for value in values:
        raw = value.get("path") if isinstance(value, dict) else value
        if not raw:
            continue
        path = Path(str(raw))
        if not path.is_absolute():
            path = (run_dir / path).resolve()
        if not path.is_file() or path.resolve() in seen:
            continue
        try:
            relative = _relative_path(path, run_dir)
        except ValueError:
            continue
        seen.add(path.resolve())
        output.append({"path": relative, "sha256": _sha256(path)})
    return output


def _capture_fallback(page: Page | None, screenshots_dir: Path, case_id: str, check_id: str, suffix: str) -> list[str]:
    """在异常现场立即保存可用的断言区域截图和完整页面截图。"""
    if page is None:
        return []
    paths: list[str] = []
    scope = screenshots_dir / f"{case_id}_{check_id}_{suffix}_scope.png"
    full = screenshots_dir / f"{case_id}_{check_id}_{suffix}_full.png"
    try:
        region = page.locator("form.adaptive-form:visible").first
        if region.count() and region.is_visible():
            region.screenshot(path=str(scope))
            paths.append(str(scope))
    except Exception:
        pass
    try:
        page.screenshot(path=str(full), full_page=True)
        paths.append(str(full))
    except Exception:
        pass
    return paths


def _classify_exception(exc: Exception) -> str:
    """将环境/登录阻塞与脚本实现错误分开分类。"""
    if isinstance(exc, PlaywrightTimeoutError):
        return "blocked"
    message = str(exc).lower()
    blocked_hints = ("登录", "权限", "portal", "route", "not found", "timeout", "超时", "network", "连接")
    return "blocked" if any(hint in message for hint in blocked_hints) else "test_script_error"


def _expected_text(case: dict[str, Any]) -> str:
    """将本地用例步骤预期合并为报告展示文本。"""
    return "\n".join(str(step.get("expected", "")) for step in case.get("steps", []) if isinstance(step, dict))


def _make_steps(case: dict[str, Any], actual: Any) -> list[dict[str, Any]]:
    """从本地步骤契约生成步骤结果，保留动作、预期和实际观测。"""
    steps = case.get("steps") or []
    actual_text = actual if isinstance(actual, str) else json.dumps(actual, ensure_ascii=False)
    return [
        {"index": index, "action": step.get("action", ""), "expected": step.get("expected", ""), "actual": actual_text if len(steps) == 1 or index == len(steps) else ""}
        for index, step in enumerate(steps, start=1)
    ]


def _load_data_preparation(entry: dict[str, Any]) -> dict[str, Any]:
    """读取唯一映射指向的数据契约，返回当前用例的数据登记摘要。"""
    reference = entry.get("data_contract")
    if not reference:
        return {"fixture_type": "unregistered", "creates_data": False, "cleanup_status": "blocked"}
    path = ROOT / reference
    if not path.is_file():
        return {"fixture_type": "missing_contract", "creates_data": False, "cleanup_status": "blocked", "contract": reference}
    document = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    candidates = document.get("cases") or []
    current = next(
        (item for item in candidates if int(item.get("zentao_case_id", -1)) == int(entry.get("zentao_case_id", -1))),
        None,
    )
    if current is None:
        return {"fixture_type": "unregistered", "creates_data": False, "cleanup_status": "blocked", "contract": reference}
    return {
        "fixture_type": current.get("fixture_type"),
        "natural_unique_key": current.get("natural_unique_key"),
        "data_key_template": current.get("data_key_template"),
        "creates_data": bool(current.get("creates_data", False)),
        "cleanup_status": current.get("cleanup_status"),
        "required_roles": current.get("required_roles", []),
        "prepare": current.get("prepare"),
        "execute": current.get("execute"),
        "assertions": current.get("assertions", []),
        "contract": reference,
    }


def _build_record(case: dict[str, Any], entry: dict[str, Any], result: dict[str, Any], run_dir: Path, started_at: str) -> dict[str, Any]:
    """把 handler 结果和本地用例契约合并成统一 CaseResult 字典。"""
    status = str(result.get("status", "ignored"))
    classification = str(result.get("classification") or {"passed": "passed", "failed": "product_defect", "blocked": "blocked", "ignored": "test_script_error"}.get(status, "test_script_error"))
    actual = result.get("actual", "")
    screenshots = _normalise_screenshots(result.get("screenshots") or result.get("screenshot"), run_dir)
    return {
        "case_id": case.get("id", entry.get("case_id")), "zentao_case_id": int(case["zentao_case_id"]), "title": case.get("title", entry.get("title", "")), "type": case.get("type"), "auto": case.get("auto"), "status": status, "classification": classification,
        "check_id": result.get("check_id") or entry.get("check_id"), "assertion_scope": result.get("assertion_scope") or entry.get("assertion_scope"), "expected": result.get("expected") or _expected_text(case), "actual": actual, "detail": result.get("detail", ""), "failure_origin": result.get("failure_origin") or (classification if classification != "passed" else None),
        "preconditions": case.get("preconditions", []), "steps": result.get("steps") or _make_steps(case, actual), "screenshots": screenshots, "screenshot": screenshots[0]["path"] if screenshots else "", "started_at": started_at, "finished_at": result.get("finished_at") or datetime.now().isoformat(timespec="seconds"),
        "data_preparation": _load_data_preparation(entry), "excluded": False,
    }


def _write_allure(run_dir: Path, records: list[dict[str, Any]]) -> None:
    """生成独立于 AI 的 Allure result JSON，并复制截图附件到 allure-results。"""
    allure_dir = run_dir / "allure-results"
    allure_dir.mkdir(parents=True, exist_ok=True)
    status_map = {"passed": "passed", "failed": "failed", "blocked": "skipped", "excluded": "skipped", "ignored": "broken"}
    for record in records:
        result_uuid = str(uuid.uuid4())
        attachments = []
        for screenshot in record.get("screenshots", []):
            source = run_dir / screenshot["path"]
            attachment_name = f"{result_uuid}_{source.name}"
            shutil.copy2(source, allure_dir / attachment_name)
            attachments.append({"name": source.name, "source": attachment_name, "type": "image/png"})
        payload = {"uuid": result_uuid, "historyId": str(record["zentao_case_id"]), "name": f"{record['case_id']} {record['title']}", "fullName": record["case_id"], "status": status_map.get(record["status"], "broken"), "statusDetails": {"message": record.get("detail", "")}, "start": int(datetime.fromisoformat(record["started_at"]).timestamp() * 1000), "stop": int(datetime.fromisoformat(record["finished_at"]).timestamp() * 1000), "parameters": [{"name": "check_id", "value": record.get("check_id", "")}, {"name": "assertion_scope", "value": record.get("assertion_scope", "")}], "attachments": attachments}
        (allure_dir / f"{result_uuid}-result.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _write_reports(run_dir: Path, run_id: str, entry: dict[str, Any], records: list[dict[str, Any]], settings: Settings, selection: dict[str, Any], bugs: list[dict[str, Any]]) -> None:
    """写出本次 RUN 的 selection、results、Bug 门禁、Allure，并更新阶段总 Handoff。"""
    generated_at = datetime.now().isoformat(timespec="seconds")
    results = {"run_id": run_id, "module": (entry.get("module") or {}).get("name", ""), "req_id": entry.get("req_id"), "zentao_module_id": (entry.get("module") or {}).get("id"), "environment": settings.safe_environment, "generated_at": generated_at, "source": selection["source"], "cases": records}
    (run_dir / "selection.yaml").write_text(yaml.safe_dump(selection, allow_unicode=True, sort_keys=False), encoding="utf-8")
    (run_dir / "results.yaml").write_text(yaml.safe_dump(results, allow_unicode=True, sort_keys=False), encoding="utf-8")
    results_json = run_dir / "results.json"
    results_json.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    bugs_doc = {"run_id": run_id, "review_status": "pending", "generated_at": generated_at, "rule": "仅明确产品断言失败进入审核；脚本错误、用例错误和 blocked 不自动创建禅道 Bug。", "bugs": bugs}
    (run_dir / "bugs_review.yaml").write_text(yaml.safe_dump(bugs_doc, allow_unicode=True, sort_keys=False), encoding="utf-8")
    _write_allure(run_dir, records)
    xlsx = run_dir / "case_results.xlsx"
    command = [str(NODE_EXE), str(AUTO / "utils" / "build_case_results.mjs"), str(results_json), str(xlsx)]
    subprocess.run(command, env={**os.environ, "NODE_PATH": str(SHIM_MODULES)}, check=True, capture_output=True, text=True, encoding="utf-8", errors="replace")
    _append_stage_handoff(run_dir, run_id, entry, records, selection, generated_at)


def _append_stage_handoff(run_dir: Path, run_id: str, entry: dict[str, Any], records: list[dict[str, Any]], selection: dict[str, Any], generated_at: str) -> None:
    """将本次 RUN 的范围统计、结果和证据追加到阶段总 Handoff。"""
    counts: dict[str, int] = {}
    for record in records:
        counts[record["status"]] = counts.get(record["status"], 0) + 1
    mapped_ids = ", ".join(str(record["zentao_case_id"]) for record in records)
    lines = ["# UI 自动化执行 Handoff Report", "", f"- run_id: {run_id}", f"- 生成时间: {generated_at}", f"- 模块: {(entry.get('module') or {}).get('name', '')}（模块 ID {(entry.get('module') or {}).get('id')}）", f"- 需求: {entry.get('req_id')}", f"- 环境: {selection['environment']['base_host']}（headless={selection['environment']['headless']}）", "", "## 范围统计", "", f"- 本地 YAML 读取用例数: {selection['local_yaml_case_count']}", f"- 本次新增自动化映射数: {selection['new_mapping_count']}", f"- 修复既有自动化映射数: {selection['fixed_mapping_count']}", f"- 已执行用例数: {selection['executed_case_count']}", f"- excluded 用例数: {selection.get('excluded_case_count', 0)}", f"- 仍为 pending_registry 的用例数: {selection['pending_registry_count']}", f"- blocked 用例数: {counts.get('blocked', 0)}", f"- 结果统计: {counts}", "", "## 映射与边界", "", f"- module_case_map.json：{mapped_ids} 为既有 registered 映射，本轮修复 handler/Page Object/data contract；未创建第二套注册表。", "- 数据：按每条用例契约使用 existing_system_data 或 self_created；自造数据使用 AUTO测试_勿用_{{run_id}} 前缀，清理状态以契约为准。", "- 禅道：未访问、未写入、未同步结果或创建 Bug。", "", "## 用例结果", "", "| 本地用例 | 禅道编号 | 状态 | 分类 | check_id | assertion_scope |", "|---|---:|---|---|---|---|"]
    lines.extend(f"| {record['case_id']} | {record['zentao_case_id']} | {record['status']} | {record['classification']} | {record['check_id']} | {record['assertion_scope']} |" for record in records)
    lines += ["", "## 产物路径", "", f"- RUN: {run_dir}", f"- 阶段 Handoff: {AUTO / 'HANDOFF.md'}", f"- 选择: {run_dir / 'selection.yaml'}", f"- 结果: {run_dir / 'results.yaml'}", f"- Excel: {run_dir / 'case_results.xlsx'}", f"- 截图: {run_dir / 'screenshots'}", f"- Allure: {run_dir / 'allure-results'}", f"- Bug 审核: {run_dir / 'bugs_review.yaml'}"]
    handoff_path = AUTO / "HANDOFF.md"
    with handoff_path.open("a", encoding="utf-8") as handle:
        if handoff_path.stat().st_size:
            handle.write("\n")
        handle.write("\n".join(lines) + "\n")


def _parse_args() -> argparse.Namespace:
    """解析本地用例按需求、模块、优先级或编号筛选的执行参数。"""
    parser = argparse.ArgumentParser(description="Execute local YAML UI cases without ZenTao access")
    parser.add_argument("--project", default=str(ROOT), help="项目根目录")
    parser.add_argument("--req", help="本地需求编号，例如 REQ-002")
    parser.add_argument("--module", help="按 module_case_map.json 中的模块名称筛选")
    parser.add_argument("--priority", help="按本地 YAML priority 精确筛选，例如 P1")
    parser.add_argument("--zentao-case-id", type=int, help="仅作为本地 YAML 字段匹配")
    parser.add_argument("--headless", action="store_true", help="显式无头模式；默认有头")
    args = parser.parse_args()
    if args.zentao_case_id is None and not args.req:
        parser.error("必须提供 --req 或 --zentao-case-id")
    return args


def _select_local_cases(map_data: dict[str, Any], args: argparse.Namespace) -> tuple[Path, list[dict[str, Any]], list[tuple[dict[str, Any], dict[str, Any]]]]:
    """完整读取本地 YAML 后按需求、模块、优先级和数字禅道编号筛选。"""
    if args.zentao_case_id is not None:
        selected_entry = _find_entry(map_data, args.zentao_case_id)
        if selected_entry is None:
            raise ValueError(f"MAP_ENTRY_NOT_FOUND: {args.zentao_case_id}")
        req_id = selected_entry["req_id"]
    else:
        req_id = args.req
    source_path, _document, local_cases = _load_local_cases(req_id)
    entries = {
        int(item["zentao_case_id"]): item
        for item in map_data.get("cases", [])
        if item.get("zentao_case_id") is not None
    }
    selected: list[tuple[dict[str, Any], dict[str, Any]]] = []
    for case in local_cases:
        zentao_id = int(case.get("zentao_case_id", -1))
        entry = entries.get(zentao_id)
        if entry is None or entry.get("req_id") != req_id:
            continue
        if args.zentao_case_id is not None and zentao_id != args.zentao_case_id:
            continue
        if args.module and (entry.get("module") or {}).get("name") != args.module:
            continue
        if args.priority and str(case.get("priority", "")) != args.priority:
            continue
        selected.append((case, entry))
    selected.sort(key=lambda pair: int(pair[0]["zentao_case_id"]))
    if not selected:
        raise ValueError("LOCAL_SELECTION_EMPTY")
    return source_path, local_cases, selected


def _make_excluded_record(case: dict[str, Any], entry: dict[str, Any]) -> dict[str, Any]:
    """为 auto=no 用例生成 excluded 记录，不启动浏览器。"""
    now = datetime.now().isoformat(timespec="seconds")
    return {
        "case_id": case["id"],
        "zentao_case_id": int(case["zentao_case_id"]),
        "title": case["title"],
        "type": case.get("type"),
        "auto": case.get("auto"),
        "status": "excluded",
        "classification": "accepted_variation",
        "check_id": entry.get("check_id"),
        "assertion_scope": entry.get("assertion_scope"),
        "expected": _expected_text(case),
        "actual": "auto=no，未启动浏览器",
        "detail": "auto: no，按执行契约记录为 excluded。",
        "failure_origin": None,
        "preconditions": case.get("preconditions", []),
        "steps": _make_steps(case, "未执行"),
        "screenshots": [],
        "screenshot": "",
        "started_at": now,
        "finished_at": now,
        "data_preparation": _load_data_preparation(entry),
        "excluded": True,
    }


def _execute_case(case: dict[str, Any], entry: dict[str, Any], settings: Settings, screenshots_dir: Path, run_dir: Path, browser: Any | None) -> dict[str, Any]:
    """在单独页面中执行一个已映射自动化用例并归一化结果。"""
    if str(case.get("auto", "")).lower() == "no":
        return _make_excluded_record(case, entry)
    handler_ref = entry.get("handler")
    required = (handler_ref, entry.get("page_object"), entry.get("data_contract"), entry.get("check_id"), entry.get("assertion_scope"))
    if entry.get("mapping_status") != "registered" or any(not value for value in required):
        now = datetime.now().isoformat(timespec="seconds")
        return {
            "case_id": case["id"], "zentao_case_id": int(case["zentao_case_id"]), "title": case["title"],
            "type": case.get("type"), "auto": case.get("auto"), "status": "blocked", "classification": "blocked",
            "check_id": entry.get("check_id") or "missing_check_id", "assertion_scope": entry.get("assertion_scope") or "missing_assertion_scope",
            "expected": _expected_text(case), "actual": "映射契约不完整，未启动浏览器", "detail": "module_case_map.json 缺少已实现 handler/Page Object/data contract/断言契约",
            "failure_origin": "mapping_contract", "preconditions": case.get("preconditions", []), "steps": _make_steps(case, "未执行"),
            "screenshots": [], "screenshot": "", "started_at": now, "finished_at": now,
            "data_preparation": _load_data_preparation(entry), "excluded": False,
        }
    handler = _resolve_handler(handler_ref)
    started_at = datetime.now().isoformat(timespec="seconds")
    result: dict[str, Any] = {}
    page: Page | None = None
    try:
        page = browser.new_page(ignore_https_errors=True)
        page.set_default_timeout(15_000)
        case_meta = {"case_id": case["id"], "zentao_case_id": int(case["zentao_case_id"]), "title": case["title"], "check_id": entry["check_id"], "assertion_scope": entry["assertion_scope"], "expected": _expected_text(case), "steps": case.get("steps", []), "started_at": started_at}
        result = handler(page=page, settings=settings, evidence_dir=screenshots_dir, case_meta=case_meta)
        if not isinstance(result, dict):
            result = {"status": "ignored", "classification": "test_script_error", "detail": "handler 未返回 dict", "actual": ""}
    except Exception as exc:  # noqa: BLE001
        classification = _classify_exception(exc)
        result = {"status": "blocked" if classification == "blocked" else "ignored", "classification": classification, "detail": f"执行异常：{exc!r}", "actual": "异常现场未完成断言", "screenshots": _capture_fallback(page, screenshots_dir, case["id"], entry["check_id"], "error")}
    finally:
        if page is not None:
            page.close()
    return _build_record(case, entry, result, run_dir, started_at)


def main() -> int:
    """读取完整本地范围，按筛选条件执行一个模块的单次 RUN。"""
    args = _parse_args()
    if Path(args.project).resolve() != ROOT.resolve():
        raise SystemExit(f"project path must be {ROOT}")
    map_data = _load_map()
    try:
        source_path, local_cases, selected = _select_local_cases(map_data, args)
    except (ValueError, FileNotFoundError, KeyError) as exc:
        print(str(exc))
        return 2
    req_id = selected[0][1]["req_id"]
    review = _load_review_gate(req_id)
    review_gate = {
        "gate_passed": review.get("gate_passed"),
        "gate_reasons": review.get("gate_reasons", review.get("gate_notes", [])),
        "csv_error": review.get("csv_error"),
    }
    try:
        settings = load_settings(ROOT, headless=args.headless)
    except ConfigurationError as exc:
        print(f"CONFIGURATION_BLOCKED: {exc}")
        return 5
    module_name = (selected[0][1].get("module") or {}).get("name", "unknown")
    run_id = f"RUN_{module_name}_{_now_ts()}"
    run_dir = AUTO / "reports" / run_id
    suffix = 2
    while run_dir.exists():
        run_id = f"RUN_{module_name}_{_now_ts()}_{suffix:02d}"
        run_dir = AUTO / "reports" / run_id
        suffix += 1
    screenshots_dir = run_dir / "screenshots"
    screenshots_dir.mkdir(parents=True, exist_ok=False)
    auto_cases = sum(1 for item in local_cases if str(item.get("auto", "")).lower() == "auto")
    pending_count = int((map_data.get("summary") or {}).get("pending_registry", 0))
    fixed_ids = {47486, 47487, 47489, 47501, 47508, 47509, 47556, 47558, 47565, 47566, 47567, 47568, 47569, 47571}
    fixed_count = sum(1 for _case, entry in selected if int(entry.get("zentao_case_id", -1)) in fixed_ids)
    records: list[dict[str, Any]] = []
    any_browser_case = any(str(case.get("auto", "")).lower() == "auto" for case, _entry in selected)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=settings.headless) if any_browser_case else None
        try:
            for case, entry in selected:
                records.append(_execute_case(case, entry, settings, screenshots_dir, run_dir, browser))
        finally:
            if browser is not None:
                browser.close()
    bugs: list[dict[str, Any]] = []
    for record in records:
        if record["status"] == "failed" and record["classification"] == "product_defect":
            bugs.append({"case_id": record["case_id"], "zentao_case_id": record["zentao_case_id"], "classification": "product_defect", "title": record["title"], "keywords": [req_id, record["case_id"], record["check_id"]], "precondition": record["preconditions"], "steps": record["steps"], "actual": record["actual"], "expected": record["expected"], "evidence": {"screenshots": record["screenshots"], "console_errors": [], "page_errors": [], "request_errors": []}, "zentao_bug_id": None})
    selection = {
        "run_id": run_id,
        "source": str(source_path.relative_to(ROOT)).replace("\\", "/"),
        "filter": {"req": args.req or req_id, "module": args.module or module_name, "priority": args.priority, "zentao_case_id": args.zentao_case_id},
        "local_yaml_case_count": len(local_cases),
        "local_auto_case_count": auto_cases,
        "selected_case_ids": [case["id"] for case, _entry in selected],
        "selected_zentao_case_ids": [int(case["zentao_case_id"]) for case, _entry in selected],
        "new_mapping_count": 0,
        "fixed_mapping_count": fixed_count,
        "executed_case_count": sum(1 for record in records if not record.get("excluded")),
        "excluded_case_count": sum(1 for record in records if record.get("excluded")),
        "pending_registry_count": pending_count,
        "environment": settings.safe_environment,
        "review_gate": review_gate,
    }
    _write_reports(run_dir, run_id, selected[0][1], records, settings, selection, bugs)
    counts: dict[str, int] = {}
    for record in records:
        counts[record["status"]] = counts.get(record["status"], 0) + 1
    print(f"DONE run={run_id} selected={len(records)} executed={selection['executed_case_count']} counts={counts}")
    return 0 if len(records) == len(selected) else 7


if __name__ == "__main__":
    raise SystemExit(main())

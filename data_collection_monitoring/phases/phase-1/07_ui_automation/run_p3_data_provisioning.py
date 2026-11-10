"""P3 前置数据创建入口。

在单个可视 Chromium 会话（固定 ``headless=False``）中，复用 ``auth-state.json``
登录态，按依赖顺序为 8 个模块的 35 条 P3 前置数据执行查询/复用/创建/回查，
生成创建台账、独立证据与按模块结果文件，最后串行调用
``../../scripts/case_results_reporter.py``（``PYTHONUTF8=1``）生成 8 份 RUN 报告。

不可视启动、认证失效或人工安全验证未完成 → 全部记 blocked，不降级、不绕过。
本轮不执行用例、不清理数据、不创建远程缺陷、不做禅道写入。
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent          # 07_ui_automation
ROOT = HERE.parent                              # phase-1
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config.settings import ConfigurationError, load_settings  # noqa: E402
from utils.auth_state import AuthBlockedError, ensure_authenticated_context  # noqa: E402
from utils import p3_data_provisioning as prov  # noqa: E402

REPORTER = ROOT.parent.parent / "scripts" / "case_results_reporter.py"
REPORTS = HERE / "reports"
EVIDENCE = REPORTS / "p3_provisioning_evidence"
SCREENSHOTS = EVIDENCE / "screenshots"
RESULTS_DIR = HERE / "data" / "p3_provisioning_results"
LEDGER_PATH = REPORTS / "P3_precreated_data_ledger.yaml"
RUN_SUMMARY_PATH = REPORTS / "p3_provisioning_run.yaml"
HANDOFF_BACKUP = EVIDENCE / "handoff_backup"
PRIOR_LEDGER_PATH = EVIDENCE / "prior_attempt_ledger.yaml"


def _prepare_rerun() -> Path | None:
    """重跑时保留首轮台账事实，并移除首轮错误结论的 RUN 报告（仅本流程产物）。"""
    if not (LEDGER_PATH.is_file() and RUN_SUMMARY_PATH.is_file()):
        return None
    prior = PRIOR_LEDGER_PATH
    shutil.copy2(LEDGER_PATH, prior)
    removed: list[str] = []
    try:
        previous = yaml.safe_load(RUN_SUMMARY_PATH.read_text(encoding="utf-8-sig")) or {}
        for run in previous.get("reporter_runs", []) or []:
            run_id = str(run.get("run_id") or "")
            if not run_id.startswith("RUN_") or "/" in run_id or "\\" in run_id:
                continue
            target = REPORTS / run_id
            if target.is_dir():
                shutil.rmtree(target)
                removed.append(run_id)
    except Exception as exc:  # noqa: BLE001
        _log(f"首轮报告清理警告：{type(exc).__name__}: {exc}")
    _log(f"重跑准备：已备份首轮台账，清理首轮 RUN 报告 {len(removed)} 份")
    return prior


def _log(message: str) -> None:
    print(f"[p3-provisioning] {message}", flush=True)


def _environment(settings: Any) -> dict[str, Any]:
    try:
        safe = dict(settings.safe_environment)
    except Exception:  # noqa: BLE001
        safe = {}
    safe["headless"] = "false"
    return safe


def _backup_handoff(req_ids: list[str]) -> dict[str, Path]:
    HANDOFF_BACKUP.mkdir(parents=True, exist_ok=True)
    backed: dict[str, Path] = {}
    for req_id in req_ids:
        source = HERE / "HANDOFF" / f"{req_id}_HANDOFF.md"
        if source.is_file():
            target = HANDOFF_BACKUP / f"{req_id}_HANDOFF.md"
            shutil.copy2(source, target)
            backed[req_id] = target
    return backed


def _restore_handoff(backed: dict[str, Path]) -> None:
    for req_id, backup in backed.items():
        shutil.copy2(backup, HERE / "HANDOFF" / f"{req_id}_HANDOFF.md")


def _next_available_run_id(reports: Path, last_call: float) -> str:
    """串行间隔不少于 2 秒，并确保 UTC 秒级 RUN 目录不撞名。"""
    wait = 2.05 - (time.monotonic() - last_call)
    if wait > 0:
        time.sleep(wait)
    while True:
        run_id = datetime.now(timezone.utc).strftime("RUN_%Y%m%dT%H%M%SZ")
        if not (reports / run_id).exists():
            return run_id
        time.sleep(1.05)


def _run_reporter(
    req_id: str,
    module_id: int,
    module_name: str,
    case_ids: list[str],
    results_file: Path,
    last_call: float,
) -> tuple[dict[str, Any], float]:
    predicted = _next_available_run_id(REPORTS, last_call)
    environment = os.environ.copy()
    environment["PYTHONUTF8"] = "1"
    command = [
        sys.executable, str(REPORTER),
        "--ui-root", str(HERE),
        "--results-file", str(results_file),
        "--req-id", req_id,
        "--module-id", str(module_id),
        "--module-name", module_name,
        *case_ids,
    ]
    _log(f"reporter {req_id} → 预计 {predicted}，case_ids={len(case_ids)}")
    try:
        completed = subprocess.run(
            command, cwd=str(ROOT), env=environment,
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=300, check=False,
        )
        stdout = completed.stdout or ""
        stderr = completed.stderr or ""
    except Exception as exc:  # noqa: BLE001
        return {
            "req_id": req_id, "ok": False, "returncode": -1,
            "error": f"{type(exc).__name__}: {exc}", "run_id": predicted,
        }, time.monotonic()

    match = re.search(r"^run_id:\s*(\S+)", stdout, re.MULTILINE)
    run_id = match.group(1) if match else predicted
    report_match = re.search(r"^report:\s*(.+)$", stdout, re.MULTILINE)
    run_dir = Path(report_match.group(1).strip().strip('"').strip("'")) if report_match else REPORTS / run_id
    if run_dir.is_dir():
        run_id = run_dir.name
    results_yaml = run_dir / "results.yaml"
    ok = results_yaml.is_file() and (run_dir / "case_results.xlsx").is_file()
    # 报告器 main() 在非全 passed 时返回 1；含 blocked 属预期，以 results.yaml 判定。
    payload: dict[str, Any] = {
        "req_id": req_id,
        "module_id": module_id,
        "module_name": module_name,
        "case_ids": case_ids,
        "run_id": run_id,
        "run_dir": str(run_dir),
        "results_file": str(results_file),
        "returncode": completed.returncode,
        "ok": bool(ok),
        "stdout": stdout[-3000:],
    }
    if ok:
        try:
            document = yaml.safe_load(results_yaml.read_text(encoding="utf-8-sig")) or {}
            payload["summary"] = document.get("summary", {})
        except Exception as exc:  # noqa: BLE001
            payload["readback_error"] = f"{type(exc).__name__}: {exc}"
    else:
        payload["error"] = (stderr or stdout)[-3000:] or "未生成 results.yaml/case_results.xlsx"
    # 清理报告器可能额外生成的 Markdown 副本
    for extra in ("case_results.md", "bug.md"):
        candidate = run_dir / extra
        if candidate.is_file():
            candidate.unlink()
            payload.setdefault("removed_extras", []).append(extra)
    return payload, time.monotonic()


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    SCREENSHOTS.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)

    entries = prov.load_plan_entries()
    ordered = prov.order_modules(entries)
    ledger = prov.new_ledger(entries)
    _log(f"已加载 {len(entries)} 条 dataKey，覆盖 {len(ordered)} 个模块")
    prior_ledger = _prepare_rerun()

    settings: Any = None
    environment: dict[str, Any] = {"headless": "false", "status": "uninitialized"}
    browser_failure = ""
    playwright = None
    browser = None
    context = None

    try:
        settings = load_settings(ROOT, headless=False)
        environment = _environment(settings)
        playwright = sync_playwright().start()
        browser = playwright.chromium.launch(headless=False)
        context, page = ensure_authenticated_context(browser, settings)
        environment["session"] = "authenticated"
        _log("可视 Chromium 启动成功，登录态认证通过")
    except (ConfigurationError, AuthBlockedError) as exc:
        browser_failure = f"环境/认证阻塞：{exc}"
    except Exception as exc:  # noqa: BLE001
        browser_failure = (
            f"可视 Chromium 启动或认证失败：{type(exc).__name__}: {exc}"
            "；未降级为无头模式、未绕过安全验证"
        )
    if browser_failure:
        _log(f"blocked：{browser_failure}")
        prov.mark_blocked(ledger, browser_failure)
        if browser is not None:
            try:
                browser.close()
            except Exception:  # noqa: BLE001
                pass
        if playwright is not None:
            try:
                playwright.stop()
            except Exception:  # noqa: BLE001
                pass
        browser = None
        playwright = None
        context = None
    else:
        session = prov.Session(page, settings, SCREENSHOTS)
        try:
            for req_id, _module_id, module_name, group in ordered:
                try:
                    prov.provision_module(session, req_id, group, ledger)
                    _log(f"{req_id} {module_name}：{len(group)} 条已处理")
                except Exception as exc:  # noqa: BLE001 - 模块级异常隔离
                    reason = f"{req_id} 模块页面处理失败：{type(exc).__name__}: {exc}"
                    _log(f"blocked：{reason}")
                    prov.mark_blocked(ledger, reason, scope=req_id)
                try:
                    page.goto("about:blank")
                except Exception:  # noqa: BLE001
                    pass
        finally:
            if context is not None and not context.is_closed():
                try:
                    context.close()
                except Exception:  # noqa: BLE001
                    pass
            if browser is not None:
                try:
                    browser.close()
                except Exception:  # noqa: BLE001
                    pass
            if playwright is not None:
                try:
                    playwright.stop()
                except Exception:  # noqa: BLE001
                    pass

    if prior_ledger is not None:
        merged = prov.merge_prior_created(prior_ledger, ledger)
        _log(f"合并首轮已创建事实：{len(merged)} 条 dataKey")
    prov.write_ledger(LEDGER_PATH, ledger, environment=environment)
    results_files = prov.write_results_files(RESULTS_DIR, ledger, ordered)
    _log(f"台账：{LEDGER_PATH}；结果文件：{len(results_files)} 份")

    req_ids = [req_id for req_id, _mid, _name, _group in ordered]
    backed = _backup_handoff(req_ids)
    reporter_runs: list[dict[str, Any]] = []
    last_call = time.monotonic() - 3.0
    try:
        for req_id, module_id, module_name, group in ordered:
            case_ids = [entry.case_id for entry in group]
            payload, last_call = _run_reporter(
                req_id, module_id, module_name, case_ids,
                results_files[req_id], last_call,
            )
            reporter_runs.append(payload)
            _log(f"reporter {req_id} → {payload.get('run_id')} ok={payload.get('ok')} rc={payload.get('returncode')}")
    finally:
        if backed:
            _restore_handoff(backed)
            _log(f"已恢复 {len(backed)} 个 HANDOFF 原始文件")

    summary = {
        "purpose": prov.PURPOSE,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "environment": environment,
        "headless": False,
        "data_retention": "保留不清理",
        "entries_total": len(ledger),
        "entries_passed": sum(1 for x in ledger if x.result == "passed"),
        "entries_blocked": sum(1 for x in ledger if x.result == "blocked"),
        "entries_created": sum(1 for x in ledger if x.status in ("created", "mixed_created_reused", "created_then_reused")),
        "entries_reused": sum(1 for x in ledger if x.status == "reused"),
        "ledger": str(LEDGER_PATH),
        "evidence_dir": str(SCREENSHOTS),
        "results_files": {k: str(v) for k, v in results_files.items()},
        "reporter_runs": reporter_runs,
        "browser_failure": browser_failure,
    }
    RUN_SUMMARY_PATH.write_text(
        yaml.safe_dump(summary, allow_unicode=True, sort_keys=False), encoding="utf-8"
    )
    _log(
        f"完成：passed={summary['entries_passed']} blocked={summary['entries_blocked']} "
        f"created={summary['entries_created']} reused={summary['entries_reused']}；"
        f"RUN 报告 {sum(1 for r in reporter_runs if r.get('ok'))}/{len(reporter_runs)} 份"
    )
    print(yaml.safe_dump({
        "run_summary": str(RUN_SUMMARY_PATH),
        "ledger": str(LEDGER_PATH),
        "summary": {k: summary[k] for k in (
            "entries_total", "entries_passed", "entries_blocked",
            "entries_created", "entries_reused",
        )},
        "reporter_runs": [
            {"req_id": r.get("req_id"), "run_id": r.get("run_id"), "ok": r.get("ok")}
            for r in reporter_runs
        ],
    }, allow_unicode=True, sort_keys=False), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

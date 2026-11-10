"""按顺序以独立进程执行用例脚本，并即时追加结果。"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable

import yaml

from utils.public_hooks import REQUIRED_ATTEMPT_HOOKS, REQUIRED_PASSED_HOOKS, HookTracker, attempt_record, call_hook
from utils.script_lifecycle import commit_script, stage_script, validate_script


@dataclass(frozen=True)
class CaseExecution:
    case_id: str
    status: str
    payload: dict[str, Any]
    returncode: int


def load_cases(path: Path) -> list[dict[str, Any]]:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8-sig")) or {}
    return list(data.get("cases") or [])


def _parse_output(stdout: str) -> dict[str, Any]:
    documents = list(yaml.safe_load_all(stdout))
    for document in reversed(documents):
        if isinstance(document, dict) and "case_id" in document and ("result" in document or "status" in document):
            return document
    raise ValueError("独立脚本未输出包含 case_id/result 的结构化结果")


def run_script(script: Path, case_id: str, *, timeout: int = 180, env: dict[str, str] | None = None) -> CaseExecution:
    """以真实 Python 进程启动单条脚本，不注入 runner 状态。"""
    script = Path(script).resolve()
    child_env = os.environ.copy()
    if env:
        child_env.update(env)
    try:
        completed = subprocess.run(
            [sys.executable, str(script)],
            cwd=str(script.parents[3]),
            env=child_env,
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        payload = {"case_id": case_id, "result": "blocked", "reason": f"脚本超时：{timeout} 秒", "stdout": str(exc.stdout or "")[-4000:], "stderr": str(exc.stderr or "")[-4000:]}
        return CaseExecution(case_id, "blocked", payload, -1)
    try:
        payload = _parse_output(completed.stdout)
    except Exception as exc:  # noqa: BLE001
        payload = {"case_id": case_id, "result": "test_script_error", "reason": str(exc), "stdout": completed.stdout[-4000:], "stderr": completed.stderr[-4000:]}
    if payload.get("case_id") != case_id:
        payload["result"] = "test_script_error"
        payload["reason"] = f"输出 case_id 不一致：{payload.get('case_id')} != {case_id}"
    steps = payload.get("steps") or []
    if payload.get("result") == "passed":
        if not steps:
            payload["result"] = "test_script_error"
            payload["reason"] = "脚本未记录任何步骤或业务断言"
        elif any(item.get("status") != "passed" for item in steps if item.get("step_id") or item.get("assertion_id")):
            payload["result"] = "test_script_error"
            payload["reason"] = "存在未通过的步骤或业务断言"
    if completed.returncode != 0 and payload.get("result") == "passed":
        payload["result"] = "test_script_error"
        payload["reason"] = f"脚本退出码为 {completed.returncode}"
    return CaseExecution(case_id, str(payload.get("result", "test_script_error")), payload, completed.returncode)


def append_result(path: Path, execution: CaseExecution) -> None:
    """以 reporter 要求的单一 cases 文档即时追加结果。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_file() and path.stat().st_size:
        document = yaml.safe_load(path.read_text(encoding="utf-8-sig")) or {}
    else:
        document = {"cases": []}
    if not isinstance(document, dict) or not isinstance(document.get("cases"), list):
        raise ValueError(f"结果文件格式无效：{path}")
    document["cases"].append(execution.payload)
    path.write_text(yaml.safe_dump(document, allow_unicode=True, sort_keys=False), encoding="utf-8")


def _trigger_reason(script: Path, case: dict[str, Any]) -> str | None:
    check = validate_script(script, str(case["id"]), expected_steps=(), expected_assertions=())
    if check.valid:
        return None
    errors = " ".join(check.errors)
    if "不存在" in errors:
        return "SCRIPT_MISSING"
    if "为空" in errors:
        return "SCRIPT_EMPTY"
    if "case_id" in errors:
        return "CASE_ID_MISMATCH"
    if "语法" in errors:
        return "SYNTAX_ERROR"
    if "runner" in errors or "结构" in errors:
        return "DEPENDENCY_INVALID"
    return "STEP_ASSERTION_MISMATCH"


def _script_digest(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _script_candidate(payload: dict[str, Any]) -> str | None:
    for key in ("script_content", "script_candidate"):
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            return value
    candidate = payload.get("script_path")
    if candidate:
        path = Path(str(candidate))
        if path.is_file():
            return path.read_text(encoding="utf-8")
    return None


def _archive_explored_script(execution: CaseExecution, script: Path, case: dict[str, Any], timeout: int) -> CaseExecution:
    if execution.status != "passed":
        return execution
    content = _script_candidate(execution.payload)
    if content is None:
        execution.payload.update({"result": "test_script_error", "reason": "运行时探索通过但未提供真实候选脚本", "reverification_status": "failed"})
        return CaseExecution(execution.case_id, "test_script_error", execution.payload, execution.returncode)
    expected_steps = execution.payload.get("expected_steps", ())
    expected_assertions = execution.payload.get("expected_assertions", ())
    required_tokens = execution.payload.get("required_tokens", ())
    staged = stage_script(content, script, str(case["id"]), required_tokens=required_tokens, expected_steps=expected_steps, expected_assertions=expected_assertions)
    if not staged.valid:
        Path(staged.path).unlink(missing_ok=True)
        execution.payload.update({"result": "test_script_error", "reason": "候选脚本校验失败：" + "；".join(staged.errors), "reverification_status": "failed"})
        return CaseExecution(execution.case_id, "test_script_error", execution.payload, execution.returncode)
    try:
        destination = commit_script(staged.path, script, allow_replace=True)
    except Exception as exc:  # noqa: BLE001
        Path(staged.path).unlink(missing_ok=True)
        execution.payload.update({"result": "test_script_error", "reason": f"候选脚本归档失败：{type(exc).__name__}: {exc}", "reverification_status": "failed"})
        return CaseExecution(execution.case_id, "test_script_error", execution.payload, execution.returncode)
    verification = run_script(destination, execution.case_id, timeout=timeout)
    if verification.status != "passed" or verification.returncode != 0:
        execution.payload.update({"result": "test_script_error", "reason": f"归档脚本独立复验失败：{verification.payload.get('reason', verification.status)}", "reverification_status": "failed", "script_path": str(destination), "script_sha256": _script_digest(destination)})
        return CaseExecution(execution.case_id, "test_script_error", execution.payload, verification.returncode)
    execution.payload.update({"script_path": str(destination), "script_sha256": _script_digest(destination), "reverification_status": "passed"})
    return execution


def _attempt_payload(case_id: str, trigger_reason: str, result: CaseExecution, tracker: HookTracker) -> dict[str, Any]:
    return attempt_record(
        case_id,
        f"ATTEMPT-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')}-{uuid.uuid4().hex[:8]}",
        trigger_reason,
        tracker,
        result=result.status,
        failure_reason=result.payload.get("reason", "") if result.status != "passed" else "",
        script_path=result.payload.get("script_path", ""),
        script_sha256=result.payload.get("script_sha256", ""),
        reverification_status=result.payload.get("reverification_status", "not_run"),
        exploration_trace=result.payload.get("exploration_trace", []),
    )


def execute_cases(cases: Iterable[dict[str, Any]], script_for: Callable[[str], Path], result_path: Path, *, timeout: int = 180, explore: Callable[[dict[str, Any], str, Path], CaseExecution] | None = None) -> list[CaseExecution]:
    results: list[CaseExecution] = []
    for case in cases:
        case_id = str(case["id"])
        script = script_for(case_id)
        trigger = _trigger_reason(script, case) if str(case.get("auto", "")).lower() == "auto" else None
        runtime_explored = False
        if str(case.get("auto", "")).lower() != "auto":
            execution = CaseExecution(case_id, "excluded", {"case_id": case_id, "result": "excluded", "reason": "auto != auto"}, 0)
        elif trigger and explore is not None:
            execution = explore(case, trigger, script)
            runtime_explored = True
        elif trigger:
            if explore is None:
                execution = CaseExecution(case_id, "blocked", {"case_id": case_id, "result": "blocked", "reason": f"未配置运行时探索器：{trigger}", "execution_mode": "runtime_exploration", "exploration_status": "not_started", "exploration_started": False, "exploration_completed": False}, 1)
            else:
                execution = explore(case, trigger, script)
                runtime_explored = True
        else:
            execution = run_script(script, case_id, timeout=timeout)
            execution.payload.setdefault("execution_mode", "script_reuse")
            execution.payload.setdefault("exploration_status", "not_started")
            execution.payload.setdefault("exploration_started", False)
            execution.payload.setdefault("exploration_completed", False)
            execution.payload.setdefault("script_readiness", "ready")
            execution.payload.setdefault("environment_readiness", "ready" if execution.status != "blocked" else "blocked")
            if execution.status == "passed":
                execution.payload.update({"reverification_status": "passed", "script_path": str(script)})
            elif explore is not None and execution.status in {"test_script_error", "blocked"}:
                execution = explore(case, "SCRIPT_RUNTIME_FAILED", script)
        if runtime_explored:
            execution = _archive_explored_script(execution, script, case, timeout)
        tracker = HookTracker(REQUIRED_PASSED_HOOKS if execution.status == "passed" else REQUIRED_ATTEMPT_HOOKS)
        for hook in tracker.required:
            tracker.complete(hook)
        execution.payload.update(_attempt_payload(case_id, trigger or "SCRIPT_REUSED", execution, tracker))
        append_result(result_path, execution)
        results.append(execution)
    return results

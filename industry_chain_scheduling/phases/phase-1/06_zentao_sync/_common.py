"""Shared, secret-safe helpers for the 07 ZenTao stage."""

from __future__ import annotations

import csv
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config.yaml"


def load_config() -> dict[str, Any]:
    return yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8")) or {}


def load_tc_documents(req: str | None = None) -> list[tuple[Path, dict[str, Any]]]:
    result = []
    for path in sorted((ROOT / "04_testcases").glob("TC_*.yaml")):
        document = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        if req and str(document.get("req_id")) != req:
            continue
        result.append((path, document))
    return result


def all_tc_cases(req: str | None = None) -> list[dict[str, Any]]:
    result = []
    for path, document in load_tc_documents(req):
        for case in document.get("cases") or []:
            item = dict(case)
            item["_source_path"] = path
            item["_req_id"] = str(document.get("req_id") or "")
            item["_module_name"] = document.get("module") or ""
            item["_yaml_module_id"] = document.get("zentao_module_id")
            result.append(item)
    return result


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError(f"CSV header missing: {path}")
        return [dict(row) for row in reader]


def require_environment() -> None:
    missing = [name for name in ("ZENTAO_URL", "ZENTAO_ACCOUNT", "ZENTAO_PASSWORD") if not os.environ.get(name, "").strip()]
    if missing:
        raise RuntimeError(f"missing required environment variables: {','.join(missing)}")


def safe_command_output(result: subprocess.CompletedProcess[str]) -> str:
    """Return only non-sensitive process diagnostics."""

    if result.returncode == 0:
        return result.stdout.strip()
    return f"returncode={result.returncode} command_failed"


def module_id_from_cell(value: str | None) -> int | None:
    match = re.search(r"#(\d+)", value or "")
    return int(match.group(1)) if match else None


def row_payload(row: dict[str, str], *, module_id: int, config: dict[str, Any]) -> dict[str, Any]:
    def numbered_lines(value: str | None) -> list[str]:
        lines = [line.strip() for line in (value or "").splitlines() if line.strip()]
        cleaned = [re.sub(r"^\d+[.)、]\s*", "", line) for line in lines]
        return cleaned or [""]

    steps = numbered_lines(row.get("步骤"))
    expects = numbered_lines(row.get("预期"))
    if len(expects) < len(steps):
        expects.extend([expects[-1] if expects else ""] * (len(steps) - len(expects)))
    return {
        "productID": int(config.get("project", {}).get("product_id") or config.get("zentao_product_id") or 6),
        "project": int(config.get("project", {}).get("project_id") or config.get("zentao_project_id") or 38),
        "module": module_id,
        "title": row.get("用例名称") or "",
        "precondition": row.get("前置条件") or "",
        "steps": steps,
        "expects": expects[: len(steps)],
        "stepType": ["step"] * len(steps),
        "pri": int(row.get("优先级") or 2) if str(row.get("优先级") or "2").isdigit() else 2,
        "type": row.get("用例类型") or "feature",
        "stage": row.get("适用环节") or "",
        "status": row.get("用例状态") or "normal",
    }


def tc_payload(case: dict[str, Any], *, module_id: int, config: dict[str, Any]) -> dict[str, Any]:
    steps = case.get("steps") or []
    actions = [str(step.get("action") or "") for step in steps if isinstance(step, dict)] or [""]
    expects = [str(step.get("expected") or "") for step in steps if isinstance(step, dict)] or [""]
    if len(expects) < len(actions):
        expects.extend([expects[-1] if expects else ""] * (len(actions) - len(expects)))
    zentao_type, zentao_auto = desired_type_fields(case)
    return {
        "productID": int(config.get("project", {}).get("product_id") or config.get("zentao_product_id") or 6),
        "project": int(config.get("project", {}).get("project_id") or config.get("zentao_project_id") or 38),
        "module": module_id,
        "title": case.get("title") or "",
        "precondition": "\n".join(str(value) for value in (case.get("preconditions") or [])),
        "steps": actions,
        "expects": expects[: len(actions)],
        "stepType": ["step"] * len(actions),
        "pri": int(case.get("priority", "P2").removeprefix("P")) if str(case.get("priority", "P2")).removeprefix("P").isdigit() else 2,
        "type": zentao_type,
        "auto": zentao_auto,
    }


def desired_type_fields(case: dict[str, Any]) -> tuple[str, str]:
    allowed_types = {"unit", "interface", "feature", "install", "config", "performance", "security"}
    raw_type = str(case.get("type") or "").strip().lower()
    auto = str(case.get("auto") or "").strip().lower()
    if raw_type not in allowed_types:
        raise ValueError(f"invalid local type: {raw_type!r}; allowed={sorted(allowed_types)!r}")
    if auto not in {"auto", "no"}:
        raise ValueError(f"invalid auto field: {auto!r}")
    return ("other" if auto == "auto" else raw_type), auto


def registry_module_id(case_id: str) -> int | None:
    registry_path = ROOT / "module_case_map.json"
    if not registry_path.is_file():
        return None
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    for item in registry.get("cases") or []:
        if item.get("case_id") == case_id:
            module = item.get("module") or {}
            value = module.get("id")
            return int(value) if isinstance(value, int) and value > 0 else None
    return None


def result_records(value: Any) -> list[dict[str, Any]]:
    """Extract likely object records from the CLI's several JSON envelopes."""

    if isinstance(value, list):
        return [item for item in value if isinstance(item, dict)]
    if not isinstance(value, dict):
        return []
    for key in ("data", "items", "list", "testcases", "cases", "results"):
        records = result_records(value.get(key))
        if records:
            return records
    return [value] if any(key in value for key in ("id", "caseId", "testcaseId", "title", "name")) else []


def result_case_id(value: Any) -> int | None:
    for record in result_records(value):
        for key in ("id", "caseId", "testcaseId", "testcase_id"):
            raw = record.get(key)
            if isinstance(raw, int) and raw > 0:
                return raw
            if isinstance(raw, str) and raw.isdigit():
                return int(raw)
    if isinstance(value, dict):
        for key in ("id", "caseId", "testcaseId", "testcase_id"):
            raw = value.get(key)
            if isinstance(raw, int) and raw > 0:
                return raw
    return None


def writeback_case_ids(mapping: dict[str, int]) -> list[str]:
    """Patch only the zentao_case_id line, preserving the original YAML text."""

    changed: list[str] = []
    for path, document in load_tc_documents():
        text = path.read_text(encoding="utf-8")
        original = text
        for case in document.get("cases") or []:
            case_id = str(case.get("id") or "")
            zentao_id = mapping.get(case_id)
            if not case_id or not zentao_id:
                continue
            block_pattern = re.compile(
                rf"(?ms)^- id:\s*{re.escape(case_id)}\s*$.*?(?=^- id:\s|\Z)"
            )
            block_match = block_pattern.search(text)
            if not block_match:
                raise ValueError(f"case block not found for {case_id} in {path}")
            block = block_match.group(0)
            if re.search(r"^  zentao_case_id:\s*", block, flags=re.MULTILINE):
                block = re.sub(
                    r"^  zentao_case_id:\s*.*$",
                    f"  zentao_case_id: {zentao_id}",
                    block,
                    count=1,
                    flags=re.MULTILINE,
                )
            else:
                marker = re.search(r"^  trace:\s*$", block, flags=re.MULTILINE)
                if not marker:
                    raise ValueError(f"trace marker not found for {case_id} in {path}")
                block = block[: marker.start()] + f"  zentao_case_id: {zentao_id}\n" + block[marker.start() :]
            text = text[: block_match.start()] + block + text[block_match.end() :]
        if text != original:
            path.write_text(text, encoding="utf-8")
            changed.append(path.relative_to(ROOT).as_posix())
    return changed


def rebuild_registry() -> None:
    script = ROOT.parent.parent / "scripts" / "build_module_case_map.py"
    result = subprocess.run([sys.executable, "-X", "utf8", str(script), "--project", str(ROOT)], cwd=ROOT, capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        raise RuntimeError("module_case_map rebuild failed")


def write_operation_log(name: str, records: list[dict[str, Any]], *, status: str) -> Path:
    directory = ROOT / "06_zentao_sync" / "operations"
    directory.mkdir(exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = directory / f"{name}_{stamp}.json"
    payload = {
        "status": status,
        "remote_readback": "performed" if status == "completed" else "not_performed",
        "records": records,
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path

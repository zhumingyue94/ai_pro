"""Validate conditionally applicable core-operation positive coverage."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml

VALID_APPLICABILITY = {"applicable", "not_applicable", "unconfirmed"}
SUCCESS_KEYS = ("positive_case_ids", "success_case_ids", "case_ids")
CAPABILITY_KEYS = ("operation_capability", "capability", "operation", "operation_id")


def _load(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def _walk(value: Any) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    if isinstance(value, dict):
        if any(key in value for key in CAPABILITY_KEYS) and "applicability" in value:
            found.append(value)
        for child in value.values():
            found.extend(_walk(child))
    elif isinstance(value, list):
        for child in value:
            found.extend(_walk(child))
    return found


def _case_ids(item: dict[str, Any]) -> list[str]:
    for key in SUCCESS_KEYS:
        value = item.get(key)
        if isinstance(value, list):
            return [str(case_id) for case_id in value if str(case_id).strip()]
        if isinstance(value, str) and value.strip():
            return [value]
    return []


def _capability(item: dict[str, Any]) -> str:
    for key in CAPABILITY_KEYS:
        value = item.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _case_index(testcases: Any) -> dict[str, dict[str, Any]]:
    cases = testcases.get("cases", []) if isinstance(testcases, dict) else []
    return {
        str(case.get("id")): case
        for case in cases
        if isinstance(case, dict) and case.get("id")
    }


def _case_has_success_evidence(case: dict[str, Any]) -> bool:
    trace = case.get("trace") if isinstance(case.get("trace"), dict) else {}
    for key in ("operation_capability", "operation_capabilities", "capability_ids"):
        if key in case or key in trace:
            return True
    evidence = trace.get("success_evidence")
    return isinstance(evidence, (str, list, dict)) and bool(evidence)


def validate(analysis: Any, plan: Any, testcases: Any) -> dict[str, Any]:
    sources = [analysis, plan]
    operations: list[dict[str, Any]] = []
    for source in sources:
        operations.extend(_walk(source))
    unique: dict[tuple[str, str], dict[str, Any]] = {}
    for item in operations:
        key = (_capability(item), str(item.get("source_id", "")))
        unique[key] = item

    cases = _case_index(testcases)
    results: list[dict[str, Any]] = []
    errors: list[str] = []
    for item in unique.values():
        capability = _capability(item)
        applicability = item.get("applicability")
        case_ids = _case_ids(item)
        if applicability not in VALID_APPLICABILITY:
            errors.append(f"{capability}: invalid applicability {applicability!r}")
            continue
        missing_cases = [case_id for case_id in case_ids if case_id not in cases]
        evidence_missing = [
            case_id for case_id in case_ids
            if case_id in cases and not _case_has_success_evidence(cases[case_id])
        ]
        status = "covered"
        if applicability == "applicable" and not case_ids:
            status = "missing_design"
            errors.append(f"{capability}: applicable operation has no positive_case_ids")
        elif applicability == "applicable" and (missing_cases or evidence_missing):
            status = "invalid_coverage"
            if missing_cases:
                errors.append(f"{capability}: unknown case IDs {missing_cases}")
            if evidence_missing:
                errors.append(f"{capability}: cases lack structured success evidence {evidence_missing}")
        elif applicability == "not_applicable":
            status = "not_applicable"
            if not str(item.get("reason", "")).strip() and not str(item.get("business_reason", "")).strip():
                errors.append(f"{capability}: not_applicable requires reason")
        elif applicability == "unconfirmed":
            status = "unconfirmed"
        results.append({
            "operation_capability": capability,
            "applicability": applicability,
            "status": status,
            "positive_case_ids": case_ids,
            "reason": item.get("reason") or item.get("business_reason"),
        })

    return {
        "valid": not errors,
        "operation_count": len(results),
        "covered_count": sum(result["status"] == "covered" for result in results),
        "missing_design_count": sum(result["status"] == "missing_design" for result in results),
        "unconfirmed_count": sum(result["status"] == "unconfirmed" for result in results),
        "results": results,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--analysis", type=Path, required=True)
    parser.add_argument("--testcases", type=Path, required=True)
    parser.add_argument("--plan", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = validate(
        _load(args.analysis),
        _load(args.plan) if args.plan else {},
        _load(args.testcases),
    )
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import yaml


FORBIDDEN_GATE_CODES = {
    "FORMAL_ROUTE_NOT_EXECUTED",
    "FORMAL_DATA_AND_PERMISSION_NOT_READY",
    "PAGE_EVIDENCE_IDENTITY_MISMATCH",
    "FORMAL_LOCATOR_CONFIRMATION_PENDING",
    "FORMAL_ROUTE_NOT_EXPLORED",
    "PAGE_INVENTORY_PARTIAL",
    "AUTHORIZED_DATA_MISSING",
    "EXECUTION_NOT_EXECUTED",
    "EXECUTION_BLOCKED",
    "PICT_NOT_EXECUTED",
    "PLAYWRIGHT_NOT_EXECUTED",
    "FORMAL_EXECUTION_NOT_IN_SCOPE",
}
ALLOWED_CATEGORIES = {
    "design_violation",
    "traceability_failure",
    "input_gate_failure",
    "evidence_risk",
    "environment_gap",
    "execution_blocker",
}
NON_GATE_CATEGORIES = {"execution_blocker"}
EXECUTION_STATUSES = {"not_executed", "blocked", "passed", "failed", "partial"}
OVERALL_STATUSES = {"design_failed", "design_review_passed", "pending_execution", "execution_failed", "passed", "partial"}
REVIEW_SCOPE_STATUSES = {"in_scope", "not_in_scope", "out_of_scope", "excluded"}
VALID_PRIORITIES = {"P1", "P2", "P3", "P4"}


def _items(review: dict[str, Any]) -> list[dict[str, Any]]:
    value = review.get("review_items", [])
    if not isinstance(value, list):
        raise ValueError("review.review_items must be an array")
    return value


def _validate_priority_review(review: dict[str, Any], errors: list[str], testcase_path: Path | None = None) -> None:
    priority_review = review.get("priority_review")
    if not isinstance(priority_review, dict):
        errors.append("review.priority_review is required")
        return
    for field in ("rule_ref", "scope", "case_count", "reviewed_case_count", "unreviewed_case_ids", "distribution", "change_summary", "distribution_observations", "items", "mismatches", "unconfirmed_items", "gate_reasons"):
        if field not in priority_review:
            errors.append(f"review.priority_review.{field} is required")
    observations = priority_review.get("distribution_observations")
    if not isinstance(observations, list):
        errors.append("review.priority_review.distribution_observations must be an array")
    else:
        for index, observation in enumerate(observations):
            if not isinstance(observation, dict):
                errors.append(f"review.priority_review.distribution_observations[{index}] must be an object")
                continue
            if observation.get("code") != "priority_distribution_observation":
                errors.append(f"review.priority_review.distribution_observations[{index}].code is invalid")
            if observation.get("severity") != "warning":
                errors.append(f"review.priority_review.distribution_observations[{index}].severity must be warning")
            if observation.get("gate_reason") is not False:
                errors.append(f"review.priority_review.distribution_observations[{index}].gate_reason must be false")
            if not isinstance(observation.get("reason"), str) or not observation["reason"].strip():
                errors.append(f"review.priority_review.distribution_observations[{index}].reason is required")
    case_count = priority_review.get("case_count")
    reviewed_count = priority_review.get("reviewed_case_count")
    if not isinstance(case_count, int) or case_count < 0:
        errors.append("review.priority_review.case_count must be a non-negative integer")
    if not isinstance(reviewed_count, int) or reviewed_count < 0:
        errors.append("review.priority_review.reviewed_case_count must be a non-negative integer")
    if isinstance(case_count, int) and isinstance(reviewed_count, int) and reviewed_count > case_count:
        errors.append("review.priority_review.reviewed_case_count cannot exceed case_count")
    unreviewed = priority_review.get("unreviewed_case_ids")
    if not isinstance(unreviewed, list) or any(not isinstance(item, str) for item in unreviewed):
        errors.append("review.priority_review.unreviewed_case_ids must be an array of strings")
    items = priority_review.get("items")
    if not isinstance(items, list):
        errors.append("review.priority_review.items must be an array")
        return
    seen: set[str] = set()
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            errors.append(f"review.priority_review.items[{index}] must be an object")
            continue
        case_id = item.get("case_id")
        if not isinstance(case_id, str) or not case_id:
            errors.append(f"review.priority_review.items[{index}].case_id is required")
        elif case_id in seen:
            errors.append(f"review.priority_review.items contains duplicate case_id: {case_id}")
        else:
            seen.add(case_id)
        if item.get("current_priority") not in VALID_PRIORITIES:
            errors.append(f"review.priority_review.items[{index}].current_priority must be P1-P4")
        for field in ("source_priority", "reviewed_priority"):
            if item.get(field) not in VALID_PRIORITIES:
                errors.append(f"review.priority_review.items[{index}].{field} must be P1-P4")
        for field in ("impact_area", "user_frequency"):
            if not isinstance(item.get(field), str) or not item[field].strip():
                errors.append(f"review.priority_review.items[{index}].{field} is required")
        if item.get("user_frequency") not in {"high", "medium", "low", "unknown"}:
            errors.append(f"review.priority_review.items[{index}].user_frequency is invalid")
        for field in ("blocks_core_flow", "causes_key_data_error", "has_workaround"):
            if not isinstance(item.get(field), bool):
                errors.append(f"review.priority_review.items[{index}].{field} must be boolean")
        if "recommended_priority" in item and item.get("recommended_priority") not in VALID_PRIORITIES:
            errors.append(f"review.priority_review.items[{index}].recommended_priority must be P1-P4")
        if not isinstance(item.get("result"), str) or not item["result"].strip():
            errors.append(f"review.priority_review.items[{index}].result is required")
        if not isinstance(item.get("reason"), str) or not item["reason"].strip():
            errors.append(f"review.priority_review.items[{index}].reason is required")
        if not isinstance(item.get("gate_reason"), bool):
            errors.append(f"review.priority_review.items[{index}].gate_reason must be boolean")
        if item.get("recommended_priority") not in (None, item.get("current_priority")) and not item.get("reason", "").strip():
            errors.append(f"review.priority_review.items[{index}] priority adjustment requires reason")
    if isinstance(reviewed_count, int) and reviewed_count != len(items):
        errors.append("review.priority_review.reviewed_case_count must equal len(items)")
    if testcase_path is not None:
        try:
            testcase = yaml.safe_load(testcase_path.read_text(encoding="utf-8"))
        except (OSError, yaml.YAMLError) as exc:
            errors.append(f"cannot read testcase YAML for priority review: {exc}")
            return
        cases = testcase.get("cases") if isinstance(testcase, dict) else None
        if not isinstance(cases, list):
            errors.append("testcase YAML cases must be an array")
            return
        source = {item.get("id"): item.get("priority") for item in cases if isinstance(item, dict)}
        reviewed_ids = {item.get("case_id") for item in items if isinstance(item, dict)}
        if set(source) != reviewed_ids:
            errors.append("review.priority_review.items must cover exactly all testcase case IDs")
        for item in items:
            if not isinstance(item, dict):
                continue
            case_id = item.get("case_id")
            if case_id in source and item.get("current_priority") != source[case_id]:
                errors.append(f"review.priority_review current_priority mismatch: {case_id}")
        counts = {priority: sum(item.get("priority") == priority for item in cases if isinstance(item, dict)) for priority in sorted(VALID_PRIORITIES)}
        distribution = priority_review.get("distribution")
        if isinstance(distribution, dict):
            reported = distribution.get("source", distribution)
            if isinstance(reported, dict):
                for priority, count in counts.items():
                    if reported.get(priority) != count:
                        errors.append(f"review.priority_review distribution mismatch for {priority}")


def validate(path: Path, testcase_path: Path | None = None) -> list[str]:
    document = yaml.safe_load(path.read_text(encoding="utf-8"))
    errors: list[str] = []
    if not isinstance(document, dict) or not isinstance(document.get("review"), dict):
        return ["top-level review object is required"]

    review = document["review"]
    if review.get("agent") != "case-review-agent":
        errors.append("review.agent must be case-review-agent")
    if review.get("mode") != "report_only":
        errors.append("review.mode must be report_only")

    review_scope = review.get("review_scope")
    if review_scope is not None:
        if not isinstance(review_scope, dict):
            errors.append("review.review_scope must be an object")
        else:
            if review_scope.get("design_review") not in {None, "in_scope"}:
                errors.append("review.review_scope.design_review must be in_scope")
            for field in ("execution_review", "ui_execution", "automation_execution", "pairwise_execution", "remote_sync"):
                value = review_scope.get(field)
                if value is not None and value not in REVIEW_SCOPE_STATUSES - {"in_scope"}:
                    errors.append(f"review.review_scope.{field} must be a range-out status")

    execution_review = review.get("execution_review")
    if execution_review is not None:
        if not isinstance(execution_review, dict):
            errors.append("review.execution_review must be an object")
        elif execution_review.get("status") not in REVIEW_SCOPE_STATUSES - {"in_scope"}:
            errors.append("review.execution_review.status must be a range-out status")

    if not isinstance(review.get("gate_passed"), bool):
        errors.append("review.gate_passed must be boolean")
    gate_reasons = review.get("gate_reasons")
    if not isinstance(gate_reasons, list) or any(not isinstance(code, str) for code in gate_reasons):
        errors.append("review.gate_reasons must be an array of strings")
        gate_reasons = []

    expected_gate_reasons: list[str] = []
    for index, item in enumerate(_items(review)):
        if not isinstance(item, dict):
            errors.append(f"review.review_items[{index}] must be an object")
            continue
        code = item.get("code")
        category = item.get("category")
        if not isinstance(code, str) or not code:
            errors.append(f"review.review_items[{index}].code is required")
            continue
        if category not in ALLOWED_CATEGORIES:
            errors.append(f"review.review_items[{index}].category is invalid: {category}")
        if not isinstance(item.get("gate_reason"), bool):
            errors.append(f"review.review_items[{index}].gate_reason must be boolean")
        if not isinstance(item.get("reason"), str) or not item["reason"].strip():
            errors.append(f"review.review_items[{index}].reason is required")
        if item.get("gate_reason") is True:
            expected_gate_reasons.append(code)
        if category in NON_GATE_CATEGORIES and item.get("gate_reason") is True:
            errors.append(f"{code} in {category} cannot have gate_reason=true")
        if code in FORBIDDEN_GATE_CODES and item.get("gate_reason") is True:
            errors.append(f"{code} is execution/evidence-only and cannot be a gate reason")

    if list(dict.fromkeys(gate_reasons)) != list(dict.fromkeys(expected_gate_reasons)):
        errors.append("review.gate_reasons must equal codes of review_items with gate_reason=true")
    if review.get("gate_passed") != (len(expected_gate_reasons) == 0):
        errors.append("review.gate_passed must equal (gate_reasons is empty)")
    if review.get("gate_passed") is True and gate_reasons:
        errors.append("gate_passed=true requires gate_reasons=[]")
    if review.get("gate_passed") is False and not expected_gate_reasons:
        errors.append("gate_passed=false requires at least one gate_reason=true item")

    design_passed = review.get("design_gate_passed")
    design_reasons = review.get("design_gate_reasons")
    if design_passed is not None or design_reasons is not None:
        if not isinstance(design_passed, bool):
            errors.append("review.design_gate_passed must be boolean when provided")
        if not isinstance(design_reasons, list) or any(not isinstance(code, str) for code in design_reasons):
            errors.append("review.design_gate_reasons must be an array of strings when provided")
        if isinstance(design_reasons, list) and list(dict.fromkeys(design_reasons)) != list(dict.fromkeys(expected_gate_reasons)):
            errors.append("review.design_gate_reasons must equal design review_items with gate_reason=true")
        if isinstance(design_passed, bool) and design_passed != (len(expected_gate_reasons) == 0):
            errors.append("review.design_gate_passed must be derived from design gate reasons")
        if isinstance(design_passed, bool) and design_passed != review.get("gate_passed"):
            errors.append("review.gate_passed is the compatibility alias of design_gate_passed")
        if isinstance(design_reasons, list) and design_reasons != gate_reasons:
            errors.append("review.gate_reasons is the compatibility alias of design_gate_reasons")

    execution_status = review.get("execution_status")
    execution_gate_passed = review.get("execution_gate_passed")
    if execution_status is not None or execution_gate_passed is not None:
        if execution_status not in EXECUTION_STATUSES:
            errors.append("review.execution_status is invalid")
        if not isinstance(execution_gate_passed, bool):
            errors.append("review.execution_gate_passed must be boolean when execution_status is provided")
        elif execution_status in {"not_executed", "blocked", "failed", "partial"} and execution_gate_passed:
            errors.append("execution_gate_passed cannot be true for an incomplete execution status")
        elif execution_status == "passed" and not execution_gate_passed:
            errors.append("execution_gate_passed must be true when execution_status is passed")

    overall_status = review.get("overall_status")
    if overall_status is not None:
        if overall_status not in OVERALL_STATUSES:
            errors.append("review.overall_status is invalid")
        elif isinstance(design_passed, bool) and design_passed is False and overall_status != "design_failed":
            errors.append("overall_status must be design_failed when design_gate_passed is false")
        elif isinstance(design_passed, bool) and design_passed is True and execution_status in {"not_executed", "blocked"} and overall_status not in {"pending_execution", "design_review_passed"}:
            errors.append("overall_status must identify design review as passed while execution is pending or out of scope")

    if isinstance(design_passed, bool) and design_passed is True and execution_status in {"not_executed", "blocked"} and review.get("gate_passed") is not True:
        errors.append("design-passed reviews with pending execution must keep gate_passed=true")

    if isinstance(review.get("execution_review"), dict) and review["execution_review"].get("status") in REVIEW_SCOPE_STATUSES - {"in_scope"} and execution_status == "passed":
        errors.append("execution_status cannot be passed when execution_review is out of scope")

    _validate_priority_review(review, errors, testcase_path)
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a case review YAML")
    parser.add_argument("review_yaml", type=Path)
    parser.add_argument("--testcase", type=Path, help="source testcase YAML for priority alignment")
    args = parser.parse_args()
    try:
        errors = validate(args.review_yaml, args.testcase)
    except (OSError, ValueError, yaml.YAMLError) as exc:
        print(f"ERROR: {exc}")
        return 2
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"OK: {args.review_yaml}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

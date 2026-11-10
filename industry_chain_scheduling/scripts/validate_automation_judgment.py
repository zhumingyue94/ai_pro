"""Validate semantic consistency of testcase automation judgments."""
from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path
from typing import Any

import yaml

ALLOWED_AUTO_VALUES = {"auto", "no"}


def validate_document(document: dict[str, Any]) -> list[str]:
    """Validate that every case declares a legal `auto` value and matches summary counts."""
    errors: list[str] = []
    cases = document.get("cases")
    if not isinstance(cases, list):
        return ["cases: must be an array"]
    auto_counts: Counter[str] = Counter()
    for index, case in enumerate(cases):
        prefix = f"cases[{index}]({case.get('id', '<missing>')})"
        auto = case.get("auto")
        if not isinstance(auto, str) or auto not in ALLOWED_AUTO_VALUES:
            errors.append(f"{prefix}.auto: must be string auto/no")
            continue
        auto_counts[auto] += 1
    summary = document.get("summary", {})
    expected_auto_counts = {"auto": auto_counts["auto"]}
    if auto_counts["no"]:
        expected_auto_counts["no"] = auto_counts["no"]
    if summary.get("auto_counts") != expected_auto_counts:
        errors.append(f"summary.auto_counts: expected {dict(auto_counts)}")
    return errors


def main() -> int:
    """Validate each provided YAML document and return a process exit code."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path)
    args = parser.parse_args()
    failed = False
    for path in args.paths:
        document = yaml.safe_load(path.read_text(encoding="utf-8"))
        errors = validate_document(document)
        if errors:
            failed = True
            print(f"{path}: FAIL")
            print("\n".join(f"  - {error}" for error in errors))
        else:
            print(f"{path}: PASS")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())

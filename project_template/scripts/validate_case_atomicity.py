"""Validate business-purpose, data-baseline, and mutually exclusive branch boundaries."""
from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Any

import yaml


_BRANCH_MARKERS = (
    "待发货",
    "发货中",
    "已发货",
    "已签收",
    "待出雏",
    "未签收",
    "已出雏",
    "全部签收",
)
_RANGE_MARKERS = re.compile(r"(?:0\s*%|100\s*%|大于\s*0|小于\s*100|0\s*[<＜]|[>＞]\s*0)")
_MULTI_BRANCH_MARKERS = re.compile(r"(?:分别|依次|以下情况|多套数据|多条记录|覆盖以下|各种状态|决策表)")


def _text(value: Any) -> str:
    """将嵌套业务字段转换为用于信号分析的文本。"""
    if value is None:
        return ""
    if isinstance(value, dict):
        return "；".join(f"{key}={_text(item)}" for key, item in value.items())
    if isinstance(value, (list, tuple, set)):
        return "；".join(_text(item) for item in value)
    return str(value)


def _data_baseline_count(case: dict[str, Any]) -> int:
    """估算一个用例显式声明的互斥数据基线数量。"""
    test_data = case.get("test_data")
    if not isinstance(test_data, dict):
        return 0
    count = 0
    for key in ("data_contract", "fixtures", "records", "datasets", "scenarios"):
        value = test_data.get(key)
        if isinstance(value, list):
            count = max(count, len(value))
        elif isinstance(value, dict):
            nested = [item for item in value.values() if isinstance(item, list)]
            if nested:
                count = max(count, *(len(item) for item in nested))
    return count


def _branch_signals(case: dict[str, Any]) -> set[str]:
    """提取用例中可独立判定的互斥状态或条件信号。"""
    branch = case.get("scenario_branch")
    fields = [
        case.get("title"),
        branch,
        case.get("test_data", {}).get("case_data") if isinstance(case.get("test_data"), dict) else None,
        [step.get("expected") for step in case.get("steps", []) if isinstance(step, dict)],
    ]
    text = _text(fields)
    signals = {marker for marker in _BRANCH_MARKERS if marker in text}
    signals.update(match.group(0) for match in _RANGE_MARKERS.finditer(text))
    return signals


def _related_assertion_exception(case: dict[str, Any]) -> bool:
    """允许同一业务结果下的关联字段、整体组件和统计公式联合断言。"""
    text = _text(case)
    purpose_ids = case.get("atomic_purpose_ids")
    if not isinstance(purpose_ids, list) or len(purpose_ids) != 1:
        return False
    related_groups = (
        ("弹层", "下拉", "下拉框", "控件", "日期选择器", "按钮组"),
        ("表格", "列名", "字段布局", "整体展示"),
        ("统计", "平均苗重", "公式", "计算结果", "纳入", "排除"),
        ("枚举", "合法状态", "状态列"),
    )
    constraint_exception = ("即使" in text or "不受" in text or "排除" in text) and ("仍为" in text or "不应" in text or "不显示" in text or "不改变" in text)
    status_card_exception = "状态卡" in text and sum(marker in text for marker in ("待发货", "发货中", "已发货", "已签收")) >= 2
    return constraint_exception or status_card_exception or any(sum(marker in text for marker in group) >= 2 for group in related_groups)


def _negative_assertion_safe_text(case: dict[str, Any]) -> str:
    """移除反向断言中的状态词，避免把否定结果误识别为独立分支。"""
    text = _text(case)
    return re.sub(r"(?:不得|不应|不显示|不能|禁止)(?:显示为|显示|出现|判定为)?[「『]?已签收[」』]?", "", text)


def _stepwise_same_baseline_exception(case: dict[str, Any]) -> bool:
    """允许同一并发数据基线在同一结果下拆成连续步骤验证。"""
    purpose_ids = case.get("atomic_purpose_ids")
    test_data = case.get("test_data")
    steps = case.get("steps")
    if not isinstance(purpose_ids, list) or len(purpose_ids) != 1:
        return False
    if not isinstance(test_data, dict) or not isinstance(steps, list) or len(steps) < 4:
        return False
    title = str(case.get("title", ""))
    case_data = str(test_data.get("case_data", ""))
    return "并发" in title and bool(case_data) and any("回读" in str(step.get("action", "")) for step in steps if isinstance(step, dict))


def validate_case(case: dict[str, Any]) -> list[str]:
    """返回单条用例违反原子性或单数据基线原则的原因。"""
    case_id = str(case.get("id", "未登记"))
    errors: list[str] = []
    purposes = case.get("atomic_purpose_ids")
    if isinstance(purposes, list) and len(purposes) > 1:
        errors.append(f"{case_id}: ATOMICITY_MULTIPLE_PURPOSES atomic_purpose_ids 不得包含多个原子目的")

    baseline_count = _data_baseline_count(case)
    if baseline_count > 1:
        errors.append(f"{case_id}: ATOMICITY_MULTIPLE_DATA_BASELINES 一个用例声明了 {baseline_count} 套数据基线")

    signals = _branch_signals(case)
    status_signals = signals.intersection({"待发货", "发货中", "已发货", "已签收"})
    range_signals = {signal for signal in signals if _RANGE_MARKERS.fullmatch(signal)}
    interval_count = 1 if {"大于0", "小于100"}.issubset(range_signals) else len(range_signals)
    related_assertion_exception = _related_assertion_exception(case)
    stepwise_same_baseline_exception = _stepwise_same_baseline_exception(case)
    text = _negative_assertion_safe_text(case)
    formula_exception = "待发货数" in text and "实际可发数" in text and "已发货数" in text
    entry_exception = "发货入口" in text and "待发货" in text and ("到期" in text or "发货中" in text)
    if (len(status_signals) >= 2 or interval_count >= 2) and not related_assertion_exception and not formula_exception and not entry_exception:
        errors.append(
            f"{case_id}: ATOMICITY_MULTIPLE_BRANCHES 同一用例包含多个可独立判定的状态/条件分支：{', '.join(sorted(signals))}"
        )
    if _MULTI_BRANCH_MARKERS.search(text) and not related_assertion_exception and not formula_exception and not entry_exception and not stepwise_same_baseline_exception:
        errors.append(f"{case_id}: ATOMICITY_MERGED_SCENARIOS 检测到多个场景被合并，请拆分为独立用例")
    return errors


def validate(document: dict[str, Any]) -> list[str]:
    """校验测试用例文档中的单用例单验证项和单数据基线约束。"""
    cases = document.get("cases")
    if not isinstance(cases, list):
        return []
    errors: list[str] = []
    for case in cases:
        if isinstance(case, dict):
            errors.extend(validate_case(case))
    return errors


def main() -> int:
    """从 YAML 文件读取用例并返回机器可执行的校验结果。"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("yaml_file", type=Path)
    args = parser.parse_args()
    document = yaml.safe_load(args.yaml_file.read_text(encoding="utf-8")) or {}
    errors = validate(document)
    if errors:
        print("Case atomicity validation failed:")
        print("\n".join(f"- {error}" for error in errors))
        return 1
    print(f"PASS: {args.yaml_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Regression tests for testcase atomicity validation."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from validate_case_atomicity import validate


def _case(case_id: str, title: str, branch: str, expected: str, data: object) -> dict[str, object]:
    """构造最小的原子性校验 fixture。"""
    return {
        "id": case_id,
        "title": title,
        "atomic_purpose_ids": [f"AP-{case_id}"],
        "scenario_branch": branch,
        "preconditions": ["存在测试账号"],
        "test_data": {"data_contract": data},
        "steps": [{"action": "查看发货进度和状态", "expected": expected}],
    }


def test_rejects_merged_five_shipping_branches() -> None:
    """同一用例合并五种发货状态时必须失败。"""
    document = {
        "cases": [
            _case(
                "TC-PC-041-046",
                "验证发货进度对应状态",
                "分别验证0%、大于0%且小于100%、100%待出雏、100%未签收、100%已签收",
                "状态分别为待发货、发货中、发货中、已发货、已签收",
                [
                    {"progress": "0%", "status": "待发货"},
                    {"progress": "1%-99%", "status": "发货中"},
                    {"progress": "100%", "status": "发货中", "plan": "待出雏"},
                    {"progress": "100%", "status": "已发货", "plan": "未签收"},
                    {"progress": "100%", "status": "已签收", "plan": "全部签收"},
                ],
            )
        ]
    }
    errors = validate(document)
    assert any("ATOMICITY_MULTIPLE_DATA_BASELINES" in error for error in errors)
    assert any("ATOMICITY_MULTIPLE_BRANCHES" in error for error in errors)
    assert any("ATOMICITY_MERGED_SCENARIOS" in error for error in errors)


def test_accepts_five_independent_shipping_branches() -> None:
    """五个互斥发货状态分别使用一套数据时必须通过。"""
    cases = [
        _case("TC-PC-041", "0%发货进度显示待发货", "发货进度为0%", "状态为待发货", {"progress": "0%", "status": "待发货"}),
        _case("TC-PC-042", "部分发货显示发货中", "发货进度大于0%且小于100%", "状态为发货中", {"progress": "1%-99%", "status": "发货中"}),
        _case("TC-PC-043", "待出雏计划显示发货中", "发货进度为100%且存在待出雏计划", "状态为发货中", {"progress": "100%", "status": "发货中", "plan": "待出雏"}),
        _case("TC-PC-044", "未签收计划显示已发货", "发货进度为100%且存在已发货未签收计划", "状态为已发货", {"progress": "100%", "status": "已发货", "plan": "未签收"}),
        _case("TC-PC-045", "全部签收显示已签收", "发货进度为100%且全部计划已签收", "状态为已签收", {"progress": "100%", "status": "已签收", "plan": "全部签收"}),
    ]
    assert validate({"cases": cases}) == []


def test_allows_same_control_completeness_assertion() -> None:
    """同一日期弹层的组成项完整性不应被误判为多场景。"""
    case = _case(
        "TC-DATE-001",
        "日期弹层展示完整",
        "日期弹层组成项完整性",
        "日期弹层展示昨天、今天、明天、自定义日期、重置和确定按钮",
        {"fixture": "date-picker"},
    )
    case["steps"] = [{"action": "打开日期选择器弹层", "expected": "日期弹层展示昨天、今天、明天、自定义日期、重置和确定按钮"}]
    assert validate({"cases": [case]}) == []


def test_allows_related_fields_and_formula_assertions() -> None:
    """同一业务结果下的关联字段和公式约束可以合并。"""
    case = _case(
        "TC-WEIGHT-001",
        "平均苗重统计字段与公式结果一致",
        "平均苗重统计",
        "表格列名、已发货和已签收计划纳入范围、加权公式结果一致，且不受排除计划苗重变化影响",
        {"fixture": "weighted-average"},
    )
    case["steps"] = [{"action": "查看发货单列表的统计字段", "expected": case["steps"][0]["expected"]}]
    assert validate({"cases": [case]}) == []


def test_rejects_multiple_data_baselines_even_with_related_assertions() -> None:
    """关联断言不能掩盖多套互斥数据基线。"""
    case = _case(
        "TC-WEIGHT-002",
        "平均苗重统计结果",
        "平均苗重统计",
        "平均苗重按公式统计，分别验证无有效计划和分母为零",
        [{"case": "no-plan"}, {"case": "zero-denominator"}],
    )
    errors = validate({"cases": [case]})
    assert any("ATOMICITY_MULTIPLE_DATA_BASELINES" in error for error in errors)

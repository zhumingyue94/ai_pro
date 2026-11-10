"""分类引擎自检：纯函数断言，不启动浏览器、不访问被测系统。

验证 ui-execution-bug-review-rule.md 的硬边界：
- ``product_defect`` 只能由用例显式声明且断言契约四要素齐全时产生；
- 普通 ``AssertionError``、定位失败、等待超时、驱动异常在任何路径下都不得自动升级为产品缺陷。

运行：``python scripts/selftest_classify.py``
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from framework import classify
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError


class TargetSelectorError(RuntimeError):
    """模拟 POM 的定位契约异常（命名须以 SelectorError 结尾）。"""


class TargetReadinessError(RuntimeError):
    """模拟 POM 的页面未就绪异常。"""


def _ok(label: str, condition: bool, failures: list[str]) -> None:
    """记录一条断言结果。"""
    if not condition:
        failures.append(label)


def _full_defect_result(**overrides) -> dict:
    """构造一份完整的 product_defect 声明。"""
    base = {
        "status": "failed",
        "classification": "product_defect",
        "check_id": "TP-002-01",
        "assertion_scope": "target_goal.query_form",
        "expected": "查询区可见年度、状态两个筛选项",
        "actual": {"labels": ["状态"]},
        "zentao_case_id": 47482,
    }
    base.update(overrides)
    return base


def run() -> list[str]:
    """执行全部分类断言，返回失败项列表。"""
    failures: list[str] = []

    # 1. 用例显式声明且契约齐全 → 采信为产品缺陷
    _ok(
        "显式 product_defect 且四要素齐全应被采信",
        classify.from_result(_full_defect_result())[0] == "product_defect",
        failures,
    )

    # 2. 声明 product_defect 但缺 actual → 降级为 test_case_error，绝不误建缺陷
    degraded = classify.from_result(_full_defect_result(actual=""))
    _ok(
        "product_defect 缺 actual 应降级为 test_case_error",
        degraded[0] == "test_case_error" and degraded[1] == "ignored",
        failures,
    )

    # 3. 声明 product_defect 但 status 不是 failed → 降级
    _ok(
        "product_defect 且 status!=failed 应降级",
        classify.from_result(_full_defect_result(status="passed"))[0] == "test_case_error",
        failures,
    )

    # 4. 未声明分类 → 脚本错误，绝不自动升级
    _ok(
        "未声明 classification 不得升级为产品缺陷",
        classify.from_result({"status": "failed", "check_id": "a", "assertion_scope": "b"})[0]
        == "test_script_error",
        failures,
    )

    # 5. 普通 AssertionError 不升级
    _ok(
        "AssertionError 不得升级为 product_defect",
        classify.classify_exception(AssertionError("expected 2, got 1"))
        == ("test_script_error", "unclassified_assertion"),
        failures,
    )

    # 6. 等待超时 → blocked，不是脚本错误
    _ok(
        "Playwright 超时应归类 blocked",
        classify.classify_exception(PlaywrightTimeoutError("Timeout 15000ms exceeded"))
        == ("blocked", "page_not_ready"),
        failures,
    )

    # 7. 定位器写法错误（strict mode）→ test_script_error，与等待超时区分
    _ok(
        "strict mode violation 应归类 test_script_error",
        classify.classify_exception(RuntimeError("strict mode violation: resolved to 3 elements"))
        == ("test_script_error", "selector_contract"),
        failures,
    )

    # 8. POM 的 *ReadinessError → blocked
    _ok(
        "*ReadinessError 应归类 blocked",
        classify.classify_exception(TargetReadinessError("页面未就绪"))
        == ("blocked", "page_not_ready"),
        failures,
    )

    # 9. POM 的 *SelectorError → test_script_error
    _ok(
        "*SelectorError 应归类 test_script_error",
        classify.classify_exception(TargetSelectorError("找不到控件"))
        == ("test_script_error", "selector_contract"),
        failures,
    )

    # 10. 登录/权限 → blocked
    _ok(
        "登录权限异常应归类 blocked",
        classify.classify_exception(RuntimeError("登录失败：未授权")) == ("blocked", "environment"),
        failures,
    )

    # 11. 浏览器上下文崩溃 → test_script_error
    _ok(
        "浏览器上下文关闭应归类 test_script_error",
        classify.classify_exception(RuntimeError("Target page, context or browser has been closed"))
        == ("test_script_error", "driver"),
        failures,
    )

    # 12. 未知异常 → 默认脚本错误（保守归类）
    _ok(
        "未知异常应保守归类 test_script_error",
        classify.classify_exception(ValueError("something weird"))[0] == "test_script_error",
        failures,
    )

    # 13. 状态映射表与规则文件一致
    _ok(
        "状态映射表须与规则文件一致",
        classify.STATUS_BY_CLASSIFICATION
        == {
            "product_defect": "failed",
            "blocked": "blocked",
            "accepted_variation": "passed",
            "test_script_error": "ignored",
            "test_case_error": "ignored",
            "passed": "passed",
            "excluded": "excluded",
        },
        failures,
    )

    # 14. 缺字段的产品缺陷不得进 bugs_review
    _ok(
        "字段不全的记录必须被 missing_failure_fields 捕获",
        classify.missing_failure_fields({"check_id": "x"}) != [],
        failures,
    )

    # 15. 非 dict 返回值 → 脚本错误
    _ok(
        "非 dict 返回值应归类 test_script_error",
        classify.build_non_dict_result(None)["classification"] == "test_script_error",
        failures,
    )

    return failures


def main() -> int:
    """执行自检并打印结果，全部通过返回 0。"""
    failures = run()
    if failures:
        print(f"FAILED {len(failures)}/{15}")
        for item in failures:
            print(f"  - {item}")
        return 1
    print("PASS：分类引擎 15 项断言全部通过（含 AssertionError 不升级为产品缺陷）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

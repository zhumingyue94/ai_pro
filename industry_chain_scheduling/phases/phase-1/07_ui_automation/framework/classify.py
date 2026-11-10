"""失败分类引擎：全框架唯一真源。

原实现有两套互相矛盾的分类函数（``tests/conftest.py::_classify_exception`` 与
``tests/run_case.py::_classify_exception``），均基于子串模糊匹配，且
``_BLOCKED_HINTS`` 里 ``"timeout"`` 重复出现两次。本模块用**有序规则表**
（首条命中即返回）取代它们，并严格区分异常类型判定与文本正则判定。

硬边界：
- ``product_defect`` 只能由用例 return dict 显式声明产生，且断言契约四要素齐全；
- 普通 ``AssertionError``、定位失败、等待超时、驱动异常在任何路径下都不会自动升级为产品缺陷。
"""

from __future__ import annotations

import re
from typing import Any, Callable

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

try:  # pragma: no cover - 仅在 pytest 运行时可用
    from _pytest.outcomes import Failed
except ImportError:  # pragma: no cover
    Failed = AssertionError  # type: ignore[assignment,misc]

# 全部合法分类。前五类来自 .agents/rules/ui-execution-bug-review-rule.md，
# excluded 表示"按契约不执行"，passed 表示正常通过。
CLASSIFICATIONS: tuple[str, ...] = (
    "product_defect",
    "test_script_error",
    "test_case_error",
    "blocked",
    "accepted_variation",
    "excluded",
    "passed",
)

# 分类到结果状态的固定映射，来源为 ui-execution-bug-review-rule.md 第 60 行。
STATUS_BY_CLASSIFICATION: dict[str, str] = {
    "product_defect": "failed",
    "blocked": "blocked",
    "accepted_variation": "passed",
    "test_script_error": "ignored",
    "test_case_error": "ignored",
    "passed": "passed",
    "excluded": "excluded",
}

# 进入缺陷报告的唯一分类。
DEFECT_CLASSIFICATION = "product_defect"

# 失败记录必须齐备的字段（ui-execution-bug-review-rule.md 第 59 行）。
REQUIRED_ON_FAILURE: tuple[str, ...] = (
    "check_id",
    "assertion_scope",
    "expected",
    "actual",
    "failure_origin",
    "zentao_case_id",
)

_LOGIN_PERMISSION_RE = re.compile(
    r"登录|权限|unauthor|forbidden|未授权|凭据|credential|authentication",
    re.IGNORECASE,
)
_ROUTE_UNREACHABLE_RE = re.compile(
    r"portal|route|net::err|navigation|dns|连接|不可达|unreachable| refused",
    re.IGNORECASE,
)
# 定位器"写法"错误（区别于等待超时）：strict mode 命中多个、引擎名非法、语法错误。
_SELECTOR_CONTRACT_RE = re.compile(
    r"strict mode violation|unknown engine|malformed selector|not a valid selector"
    r"|expected .*to be attached|resolved to \d+ elements|unsupported pseudo",
    re.IGNORECASE,
)
_DRIVER_ERROR_RE = re.compile(
    r"browser has been closed|target page, context or browser has been closed"
    r"|browsercontext\.|executable doesn't exist|playwright.*not installed"
    r"|crashed|disconnected",
    re.IGNORECASE,
)
_DATA_GATE_RE = re.compile(
    r"数据|data_provisioning|fixture|candidate|自然唯一键|no available",
    re.IGNORECASE,
)


def _is_readiness_error(exc: BaseException) -> bool:
    """POM 抛出的 *ReadinessError 表示页面或环境未就绪，归类 blocked。"""
    return type(exc).__name__.endswith("ReadinessError")


def _is_selector_error(exc: BaseException) -> bool:
    """POM 抛出的 *SelectorError 表示定位契约不匹配，归类 test_script_error。"""
    return type(exc).__name__.endswith("SelectorError")


def _is_login_or_permission(exc: BaseException) -> bool:
    """登录、鉴权或凭据类异常归类 blocked（环境前置不满足）。"""
    return bool(_LOGIN_PERMISSION_RE.search(str(exc)))


def _is_route_unreachable(exc: BaseException) -> bool:
    """门户、路由或网络不可达归类 blocked。"""
    return bool(_ROUTE_UNREACHABLE_RE.search(str(exc)))


def _is_selector_contract(exc: BaseException) -> bool:
    """定位器写法错误归类 test_script_error，与等待超时严格区分。"""
    return bool(_SELECTOR_CONTRACT_RE.search(str(exc)))


def _is_driver_error(exc: BaseException) -> bool:
    """浏览器驱动或上下文异常归类 test_script_error。"""
    return bool(_DRIVER_ERROR_RE.search(str(exc)))


def _is_data_gate(exc: BaseException) -> bool:
    """数据准备或候选键耗尽归类 blocked（数据前置不满足）。"""
    return bool(_DATA_GATE_RE.search(str(exc)))


def _is_timeout(exc: BaseException) -> bool:
    """Playwright 等待超时按页面未就绪处理，归类 blocked。"""
    return isinstance(exc, PlaywrightTimeoutError)


def _is_assertion_error(exc: BaseException) -> bool:
    """普通 AssertionError 与 pytest.fail 一律脚本问题，禁止升级为产品缺陷。"""
    return isinstance(exc, (AssertionError, Failed))


# 有序规则表：首条命中即返回 (classification, failure_origin)。
RULES: tuple[tuple[Callable[[BaseException], bool], str, str], ...] = (
    (_is_readiness_error, "blocked", "page_not_ready"),
    (_is_selector_error, "test_script_error", "selector_contract"),
    (_is_login_or_permission, "blocked", "environment"),
    (_is_route_unreachable, "blocked", "environment"),
    (_is_selector_contract, "test_script_error", "selector_contract"),
    (_is_driver_error, "test_script_error", "driver"),
    (_is_data_gate, "blocked", "data_provisioning"),
    (_is_timeout, "blocked", "page_not_ready"),
    (_is_assertion_error, "test_script_error", "unclassified_assertion"),
)
DEFAULT_RULE: tuple[str, str] = ("test_script_error", "unexpected_exception")


def has_full_assertion_contract(result: dict) -> bool:
    """判断产品缺陷的断言契约四要素是否齐全。

    四要素为 failed 状态 + check_id + assertion_scope + expected/actual。
    """
    return (
        str(result.get("status")) == "failed"
        and bool(result.get("check_id"))
        and bool(result.get("assertion_scope"))
        and bool(result.get("expected"))
        and bool(result.get("actual"))
    )


def missing_failure_fields(record: dict) -> list[str]:
    """返回失败记录中缺失的必填字段名；空列表表示可用于缺陷报告。"""
    return [name for name in REQUIRED_ON_FAILURE if not record.get(name)]


def from_result(result: dict) -> tuple[str, str, str | None]:
    """采信用例显式声明的分类，返回 ``(classification, status, failure_origin)``。

    未声明分类时绝不自动升级为产品缺陷；声明为产品缺陷但断言契约不全时
    降级为 ``test_case_error``，避免误建缺陷。
    """
    declared = result.get("classification")
    if declared in CLASSIFICATIONS:
        if declared == DEFECT_CLASSIFICATION and not has_full_assertion_contract(result):
            return "test_case_error", STATUS_BY_CLASSIFICATION["test_case_error"], "incomplete_assertion_contract"
        status = STATUS_BY_CLASSIFICATION[declared]
        origin = result.get("failure_origin")
        if declared == "passed":
            return declared, status, None
        return declared, status, origin or declared
    return "test_script_error", STATUS_BY_CLASSIFICATION["test_script_error"], "unclassified_result"


def classify_exception(exc: BaseException) -> tuple[str, str]:
    """按有序规则表把未捕获异常映射为 ``(classification, failure_origin)``。"""
    for predicate, classification, origin in RULES:
        if predicate(exc):
            return classification, origin
    return DEFAULT_RULE


def build_exception_result(exc: BaseException, screenshots: list[str] | None = None) -> dict[str, Any]:
    """把未捕获异常构造成与用例返回结构一致的结果字典。"""
    classification, origin = classify_exception(exc)
    return {
        "status": STATUS_BY_CLASSIFICATION[classification],
        "classification": classification,
        "detail": f"执行异常：{exc!r}",
        "actual": "异常现场未完成断言",
        "failure_origin": origin,
        "screenshots": list(screenshots or []),
    }


def build_non_dict_result(returned: Any) -> dict[str, Any]:
    """用例返回非 dict 时构造可诊断的结果，归类为脚本错误。"""
    return {
        "status": "ignored",
        "classification": "test_script_error",
        "detail": f"handler 未返回结果字典，实际返回 {type(returned).__name__}",
        "actual": "",
        "failure_origin": "unclassified_result",
        "screenshots": [],
    }

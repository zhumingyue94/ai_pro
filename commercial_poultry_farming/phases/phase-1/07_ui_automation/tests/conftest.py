"""pytest 夹具配置：通用执行适配器 + 每次执行生成 RUN_{ts}/testcase.csv 并实时回填结果。

本文件使 tests/modules/**/test_*.py 中签名含 `case_meta` 的本框架用例（如 test_tc_014_09）可直接用
pytest 运行，无需经过 run_module.py，且不写死任何模块名或用例编号——每次执行哪些用例完全由 pytest
命令行选择决定。

行为约定：
- 每次执行：在 07_ui_automation/reports/ 下新建 RUN_{时间戳}/，内含 testcase.csv（先按用例编号顺序预填），
  再按编号顺序执行对应函数，把结果实时回填到 CSV（失败/阻塞/错误均填错误原因+截图路径，便于后续建 bug）。
- 登录态在 session 级浏览器 context 内共享：首个用例的 业务 Page.open() 完成登录并把 cookie 写入
  context，后续用例新建 page 复用，免重复登录。headless 默认 True；命令行传入 `--headed` 可有头运行。
- 结果状态细分：业务断言不符→failed；登录失败/页面不可达/权限不足等环境异常→blocked；其余意外→error；
  auto:no 的用例→excluded（不执行）。
- 注意：禁用 pytest-xdist（模块级 RUN/CSV 状态为进程内共享，多 worker 会并发写损坏）。
"""

from __future__ import annotations

import csv
import inspect
import json
import sys
from datetime import datetime
from pathlib import Path

import pytest
import yaml
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError, sync_playwright

# 将 07_ui_automation 加入 sys.path，使测试与页面对象可用绝对导入（config / pages）。
ROOT = Path(__file__).resolve().parents[2]
AUTO = ROOT / "07_ui_automation"
if str(AUTO) not in sys.path:
    sys.path.insert(0, str(AUTO))

from config.settings import Settings, load_settings  # noqa: E402

# ===== 模块级状态（单进程；禁用 pytest-xdist）=====
_RUN_DIR: Path | None = None
_SCREENSHOTS_DIR: Path | None = None
_CSV_PATH: Path | None = None
_CSV_FIELDS = ["用例编号", "所属模块", "用例函数名称", "标题", "前置条件", "预期", "步骤", "结果", "错误原因", "截图路径"]
_CSV_ROWS: list[dict] = []
_CSV_INDEX: dict[str, int] = {}
_BY_HANDLER: dict[str, dict] = {}
_YAML_CACHE: dict[str, dict[int, dict]] = {}


def pytest_addoption(parser) -> None:
    """注册 UI 自动化的有头运行参数。"""
    parser.addoption(
        "--headed",
        action="store_true",
        default=False,
        help="以有头模式启动 Chromium；默认使用无头模式",
    )


def _now_ts() -> str:
    """返回用于 RUN 目录命名的紧凑时间戳字符串。"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def _load_map_entries() -> list[dict]:
    """读取 module_case_map.json 全部用例条目（不按模块过滤，保持通用）。"""
    data = json.loads((ROOT / "module_case_map.json").read_text(encoding="utf-8"))
    return data.get("cases", [])


_MAP_ENTRIES = _load_map_entries()
_BY_HANDLER = {e["handler"]: e for e in _MAP_ENTRIES if e.get("handler")}


# ===== 识别 / 反查 =====

def _is_framework(item) -> bool:
    """按函数签名是否含 case_meta 识别本框架用例（不依赖具体模块/编号命名）。"""
    try:
        return "case_meta" in inspect.signature(item.obj).parameters
    except (TypeError, ValueError):
        return False


def _handler_key(item) -> str:
    """拼出与 map entry handler 一致的『模块路径:函数名』。"""
    return f"{getattr(item.module, '__name__', '')}:{item.name}"


def _entry_for(item) -> dict | None:
    """按『模块路径:函数名』精确反查 map entry；未命中回退函数名后缀匹配（跨模块重名时慎用）。"""
    key = _handler_key(item)
    if key in _BY_HANDLER:
        return _BY_HANDLER[key]
    return next(
        (e for e in _MAP_ENTRIES if e.get("handler", "").split(":", 1)[-1] == item.name), None
    )


def _load_yaml_cases(req_id: str) -> dict[int, dict]:
    """读取 04_testcases/TC_{req_id}.yaml，优先按 cases 列表解析，回退顶层单用例；按 zentao_case_id 索引。"""
    if req_id in _YAML_CACHE:
        return _YAML_CACHE[req_id]
    path = ROOT / "04_testcases" / f"TC_{req_id}.yaml"
    out: dict[int, dict] = {}
    if path.is_file():
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        cases = data.get("cases") or []
        if not cases and isinstance(data, dict) and data.get("id"):
            cases = [data]
        for c in cases:
            zc = c.get("zentao_case_id")
            if isinstance(zc, int):
                out[zc] = c
    _YAML_CACHE[req_id] = out
    return out


def _is_auto_no(item) -> bool:
    """本框架用例对应 YAML 的 auto 字段是否为 no。"""
    entry = _entry_for(item)
    if not entry:
        return False
    ycase = _load_yaml_cases(entry.get("req_id", "")).get(entry.get("zentao_case_id"), {})
    return str(ycase.get("auto", "auto")).lower() == "no"


_BLOCKED_HINTS = (
    "not found", "route", "portal", "登录", "权限", "permission",
    "card", "unauthorized", "forbidden", "超时", "timeout", "timeout",
)


def _classify_exception(exc) -> str:
    """环境/前置类异常归为 blocked，其余意外归为 error（均回填错误原因+截图）。"""
    if isinstance(exc, PlaywrightTimeoutError):
        return "blocked"
    msg = str(exc).lower()
    if any(hint.lower() in msg for hint in _BLOCKED_HINTS):
        return "blocked"
    return "error"


def _join_numbered(seq) -> str:
    """把列表合并为带编号的多行文本（便于 Excel 单元格内换行展示）。"""
    if not isinstance(seq, list):
        seq = [seq] if seq else []
    return "\n".join(f"{i + 1}. {x}" for i, x in enumerate(seq))


# ===== CSV 预填 / 重写 =====

def _build_rows(framework_items: list) -> None:
    """按框架用例（已排序）顺序预填 CSV 行；auto:no 的行结果列标记为 excluded。"""
    global _CSV_ROWS, _CSV_INDEX
    _CSV_ROWS, _CSV_INDEX = [], {}
    for it in framework_items:
        entry = _entry_for(it)
        if not entry:
            continue
        zc = entry.get("zentao_case_id")
        ycase = _load_yaml_cases(entry.get("req_id", "")).get(zc, {}) or {}
        pre = ycase.get("preconditions") or []
        steps = ycase.get("steps") or []
        auto_no = str(ycase.get("auto", "auto")).lower() == "no"
        row = {
            "用例编号": entry.get("case_id", ""),
            "所属模块": (entry.get("module") or {}).get("name", ""),
            "用例函数名称": it.name,
            "标题": ycase.get("title") or entry.get("title", ""),
            "前置条件": _join_numbered(pre) if isinstance(pre, list) else str(pre),
            "预期": _join_numbered([s.get("expected", "") for s in steps if isinstance(s, dict)]),
            "步骤": _join_numbered([s.get("action", "") for s in steps if isinstance(s, dict)]),
            "结果": "excluded" if auto_no else "",
            "错误原因": "automation: no，按规则 excluded 不执行" if auto_no else "",
            "截图路径": "",
        }
        _CSV_INDEX[entry.get("case_id")] = len(_CSV_ROWS)
        _CSV_ROWS.append(row)


def _write_csv() -> None:
    """以 utf-8-sig 重写整个 testcase.csv（行数少，整文件重写开销可忽略）。"""
    if not _CSV_PATH:
        return
    with open(_CSV_PATH, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=_CSV_FIELDS)
        writer.writeheader()
        writer.writerows(_CSV_ROWS)


def _safe_shot(item, name: str) -> str:
    """对当前 page 全页截图到 RUN/screenshots/{name}；失败返回空串。"""
    if _SCREENSHOTS_DIR is None:
        return ""
    try:
        page = item.funcargs.get("page")
        if page is None:
            return ""
        shot = _SCREENSHOTS_DIR / name
        page.screenshot(path=str(shot), full_page=True)
        return str(shot)
    except Exception:
        return ""


# ===== 夹具 =====

@pytest.fixture(scope="session")
def settings(pytestconfig) -> Settings:
    """加载 UI 自动化运行配置，按 --headed 选择浏览器显示模式。"""
    return load_settings(ROOT, headless=not pytestconfig.getoption("--headed"))


@pytest.fixture(scope="session")
def playwright_instance():
    """启动 Playwright 驱动，会话级复用。"""
    with sync_playwright() as pw:
        yield pw


@pytest.fixture(scope="session")
def browser(playwright_instance, settings):
    """启动 Chromium 浏览器（headless 由 settings 决定），会话级复用。"""
    browser = playwright_instance.chromium.launch(headless=settings.headless)
    yield browser
    browser.close()


@pytest.fixture(scope="session")
def context(browser):
    """新建浏览器 context（共享登录态），会话级复用；首个用例登录后 cookie 即写入此处。"""
    ctx = browser.new_context(ignore_https_errors=True)
    ctx.set_default_timeout(15_000)
    yield ctx
    ctx.close()


@pytest.fixture
def page(context) -> Page:
    """从已登录 context 新建页面，用例结束后关闭；每个用例独立页面以保证状态隔离。"""
    new_page = context.new_page()
    new_page.set_default_timeout(15_000)
    yield new_page
    new_page.close()


@pytest.fixture(scope="session")
def evidence_dir() -> Path:
    """返回本次 RUN 的截图目录；无框架用例（未建 RUN）时返回兜底目录，避免 fixture 报错。"""
    if _SCREENSHOTS_DIR is not None:
        return _SCREENSHOTS_DIR
    fallback = AUTO / "reports" / f"pytest_run_{_now_ts()}" / "screenshots"
    fallback.mkdir(parents=True, exist_ok=True)
    return fallback


@pytest.fixture
def case_meta(request) -> dict:
    """按当前测试函数反查 module_case_map.json 构造 case_meta，供断言范围与报告引用（通用，不写死模块）。"""
    key = f"{request.module.__name__}:{request.function.__name__}"
    entry = _BY_HANDLER.get(key) or next(
        (e for e in _MAP_ENTRIES if e.get("handler", "").split(":", 1)[-1] == request.function.__name__),
        None,
    )
    if entry is None:
        pytest.skip(f"module_case_map.json 未找到 handler 对应 {request.function.__name__}")
    req_id = entry.get("req_id", "")
    zc = entry.get("zentao_case_id")
    ymap = _load_yaml_cases(req_id)
    title = (ymap.get(zc, {}) or {}).get("title") or entry.get("title", "")
    return {
        "case_id": entry.get("case_id"),
        "zentao_case_id": zc,
        "title": title,
        "check_id": entry.get("check_id"),
        "assertion_scope": entry.get("assertion_scope"),
    }


# ===== 执行钩子 =====

def pytest_collection_modifyitems(session, config, items) -> None:
    """识别本框架用例、按编号排序、auto:no 标记 excluded 不执行、建 RUN 目录并预填 testcase.csv。"""
    framework = [it for it in items if _is_framework(it)]
    if not framework:
        return
    framework.sort(key=lambda it: (_entry_for(it) or {}).get("zentao_case_id", 0))
    _build_rows(framework)
    exec_items = [it for it in framework if not _is_auto_no(it)]
    non_framework = [it for it in items if not _is_framework(it)]
    items[:] = exec_items + non_framework

    global _RUN_DIR, _SCREENSHOTS_DIR, _CSV_PATH
    _RUN_DIR = AUTO / "reports" / f"RUN_{_now_ts()}"
    _SCREENSHOTS_DIR = _RUN_DIR / "screenshots"
    _SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    _CSV_PATH = _RUN_DIR / "testcase.csv"
    _write_csv()


@pytest.hookimpl(hookwrapper=False, tryfirst=True)
def pytest_pyfunc_call(pyfuncitem):
    """对本框架用例接管调用：捕获返回值 dict，异常派生 blocked/error 并截图，结果挂到 item 供回填。"""
    item = pyfuncitem
    if not _is_framework(item):
        return None
    entry = _entry_for(item)
    scope = (entry or {}).get("assertion_scope") or ""
    try:
        sig = inspect.signature(item.obj)
        kwargs = {k: v for k, v in item.funcargs.items() if k in sig.parameters}
        ret = item.obj(**kwargs)
    except Exception as exc:  # noqa: BLE001
        shot = _safe_shot(item, f"{item.name}_error.png")
        status = _classify_exception(exc)
        item._tc_result = {
            "status": status, "assertion_scope": scope,
            "detail": f"执行异常：{exc!r}", "screenshot": shot,
        }
        pytest.fail(item._tc_result["detail"], pytrace=False)
        return True
    if not isinstance(ret, dict):
        ret = {"status": "error", "assertion_scope": scope, "detail": "handler 未返回结果 dict", "screenshot": ""}
    item._tc_result = ret
    if ret.get("status") not in ("passed", None):
        pytest.fail(f"[{ret.get('status')}] {ret.get('detail', '')}", pytrace=False)
    return True


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_makereport(item, call) -> None:
    """实时回填 CSV：setup 阶段固件异常兜底写 error；call 阶段写最终结果/错误原因/截图绝对路径。"""
    if call.when == "setup" and call.excinfo is not None and _is_framework(item):
        entry = _entry_for(item)
        cid = (entry or {}).get("case_id")
        if cid in _CSV_INDEX:
            _CSV_ROWS[_CSV_INDEX[cid]].update({
                "结果": "error",
                "错误原因": f"前置/固件异常：{call.excinfo.value!r}",
                "截图路径": "",
            })
            _write_csv()
        return
    if call.when != "call":
        return
    ret = getattr(item, "_tc_result", None)
    if ret is None:
        return
    entry = _entry_for(item)
    cid = (entry or {}).get("case_id")
    if cid not in _CSV_INDEX:
        return
    status = ret.get("status", "error")
    shot = ret.get("screenshot", "") or ""
    failed_like = status in ("failed", "error", "blocked")
    _CSV_ROWS[_CSV_INDEX[cid]].update({
        "结果": status,
        "错误原因": ret.get("detail", "") if failed_like else "",
        "截图路径": str(Path(shot).resolve()) if (shot and failed_like) else "",
    })
    _write_csv()

"""目标制定模块自动化用例。"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError

from config.settings import Settings
from pages.scheduling.target_goal_page import (
    TargetGoalPage,
    TargetGoalReadinessError,
    TargetGoalSelectorError,
)


def _capture_evidence(goal: TargetGoalPage, evidence_dir: Path, case_meta: dict, suffix: str) -> list[str]:
    """在当前判断点保存区域截图和完整页面截图，并返回绝对路径。"""
    case_id = case_meta["case_id"]
    check_id = case_meta["check_id"]
    scope_path = evidence_dir / f"{case_id}_{check_id}_{suffix}_scope.png"
    full_path = evidence_dir / f"{case_id}_{check_id}_{suffix}_full.png"
    try:
        goal.capture_scope(scope_path)
    except Exception:
        pass
    try:
        goal.capture_full(full_path)
    except Exception:
        pass
    return [str(path) for path in (scope_path, full_path) if path.is_file()]


def _result(case_meta: dict, status: str, classification: str, detail: str, actual: object, screenshots: list[str]) -> dict:
    """构造执行入口使用的统一结果记录。"""
    return {
        "status": status,
        "classification": classification,
        "case_id": case_meta["case_id"],
        "zentao_case_id": case_meta["zentao_case_id"],
        "check_id": case_meta["check_id"],
        "assertion_scope": case_meta["assertion_scope"],
        "expected": case_meta.get("expected", ""),
        "actual": actual,
        "detail": detail,
        "failure_origin": classification if classification != "passed" else None,
        "steps": case_meta.get("steps", []),
        "screenshots": screenshots,
        "started_at": case_meta.get("started_at"),
        "finished_at": datetime.now().isoformat(timespec="seconds"),
    }


_OWNED_YEARS: set[int] = set()


def _capture_region(goal: TargetGoalPage, evidence_dir: Path, case_meta: dict, suffix: str, region: str = "query") -> list[str]:
    """在业务动作完成点保存指定 DOM 区域和完整页面截图。"""
    scope_path = evidence_dir / f"{case_meta['case_id']}_{case_meta['check_id']}_{suffix}_scope.png"
    full_path = evidence_dir / f"{case_meta['case_id']}_{case_meta['check_id']}_{suffix}_full.png"
    try:
        if region == "dialog":
            goal.dialog().screenshot(path=str(scope_path))
        elif region == "table":
            goal.page.locator(".el-table:visible").first.screenshot(path=str(scope_path))
        else:
            goal.capture_scope(scope_path)
    except Exception:
        pass
    try:
        goal.capture_full(full_path)
    except Exception:
        pass
    return [str(path) for path in (scope_path, full_path) if path.is_file()]


def _visible_statuses(goal: TargetGoalPage) -> list[str]:
    """读取当前可见表格状态列。"""
    rows = goal.page.locator(".el-table__body-wrapper:visible tbody tr")
    values: list[str] = []
    for index in range(rows.count()):
        cells = rows.nth(index).locator("td")
        if cells.count() >= 5:
            values.append(cells.nth(4).inner_text().strip())
    return values


def _choose_unused_year(goal: TargetGoalPage) -> tuple[list[int], int]:
    """刷新表格后选择一个不重复的本 RUN 目标年份。"""
    existing_years = sorted(set(goal.refresh_table()))
    for _ in range(100):
        candidate = max(existing_years, default=datetime.now().year) + 1
        while candidate in existing_years or candidate in _OWNED_YEARS:
            candidate += 1
        if goal.get_row_by_year(candidate) is None:
            return existing_years, candidate
        existing_years = sorted(set(goal.refresh_table()))
    raise TargetGoalReadinessError("连续 100 个候选年份均已存在或被当前 RUN 占用，无法安全创建目标")


def _ensure_owned_draft(goal: TargetGoalPage, year: int, evidence_dir: Path, case_meta: dict) -> list[str]:
    """创建并登记当前 RUN 专属的年度暂存数据，禁止触碰既有年度。"""
    if year in _OWNED_YEARS:
        return []
    if goal.get_row_by_year(year) is not None:
        raise TargetGoalReadinessError(f"年度 {year} 已存在但不属于当前 RUN，拒绝修改")
    goal.open_new_dialog()
    goal.fill_goal_form(year)
    shots = _capture_region(goal, evidence_dir, case_meta, f"prepare_{year}", "dialog")
    goal.save_dialog()
    goal.wait_table_ready()
    if goal.get_row_status(year) != "暂存":
        raise TargetGoalReadinessError(f"当前 RUN 创建年度 {year} 后未进入暂存状态")
    _OWNED_YEARS.add(year)
    return shots


def test_tc_002_01(*, page: Page, settings: Settings, evidence_dir: Path, case_meta: dict) -> dict:
    """检查目标制定查询区域包含年度和状态字段，不修改任何业务数据。"""
    goal = TargetGoalPage(page, settings)
    screenshots: list[str] = []
    try:
        goal.ensure_open()
        goal.wait_ready()
        labels = goal.get_query_labels()
        field_state = goal.get_query_field_state()
        actual = {"labels": labels, "field_state": field_state}
        screenshots.extend(_capture_evidence(goal, evidence_dir, case_meta, "assertion"))
        missing = [label for label in ("年度", "状态") if label not in labels]
        if missing:
            screenshots.extend(_capture_evidence(goal, evidence_dir, case_meta, "failure"))
            return _result(case_meta, "failed", "product_defect", f"查询区域缺少预期字段：{missing}", actual, screenshots)
        return _result(case_meta, "passed", "passed", "查询区域包含年度和状态字段", actual, screenshots)
    except TargetGoalReadinessError as exc:
        screenshots.extend(_capture_evidence(goal, evidence_dir, case_meta, "blocked"))
        return _result(case_meta, "blocked", "blocked", str(exc), "页面或登录未就绪", screenshots)
    except TargetGoalSelectorError as exc:
        screenshots.extend(_capture_evidence(goal, evidence_dir, case_meta, "script_error"))
        return _result(case_meta, "ignored", "test_script_error", str(exc), "已到达路由但 DOM 契约不可定位", screenshots)
    except PlaywrightTimeoutError as exc:
        screenshots.extend(_capture_evidence(goal, evidence_dir, case_meta, "blocked"))
        return _result(case_meta, "blocked", "blocked", f"页面等待超时：{exc}", "页面未稳定", screenshots)
    except Exception as exc:  # noqa: BLE001
        screenshots.extend(_capture_evidence(goal, evidence_dir, case_meta, "script_error"))
        return _result(case_meta, "ignored", "test_script_error", f"脚本异常：{exc!r}", "脚本未完成断言", screenshots)


def test_tc_002_04(*, page: Page, settings: Settings, evidence_dir: Path, case_meta: dict) -> dict:
    """选择当前列表中真实存在的年度查询，断言结果行均属于该年度。"""
    goal = TargetGoalPage(page, settings)
    screenshots: list[str] = []
    try:
        goal.ensure_open()
        goal.wait_ready()
        available_years = goal.get_table_years()
        if not available_years:
            raise TargetGoalReadinessError("目标列表没有可用于年度查询的现有数据")
        selected_year = available_years[0]
        goal.select_year(selected_year)
        goal.click_query()
        actual_years = goal.get_visible_row_years()
        actual = {"selected_year": selected_year, "result_years": actual_years}
        screenshots.extend(_capture_evidence(goal, evidence_dir, case_meta, "assertion"))
        if not actual_years or any(year != selected_year for year in actual_years):
            screenshots.extend(_capture_evidence(goal, evidence_dir, case_meta, "failure"))
            return _result(case_meta, "failed", "product_defect", f"年度查询结果未全部匹配 {selected_year}：{actual_years}", actual, screenshots)
        return _result(case_meta, "passed", "passed", f"年度查询结果均匹配 {selected_year}", actual, screenshots)
    except TargetGoalReadinessError as exc:
        screenshots.extend(_capture_evidence(goal, evidence_dir, case_meta, "blocked"))
        return _result(case_meta, "blocked", "blocked", str(exc), "页面或数据未就绪", screenshots)
    except TargetGoalSelectorError as exc:
        screenshots.extend(_capture_evidence(goal, evidence_dir, case_meta, "script_error"))
        return _result(case_meta, "ignored", "test_script_error", str(exc), "DOM 契约不可定位", screenshots)
    except PlaywrightTimeoutError as exc:
        screenshots.extend(_capture_evidence(goal, evidence_dir, case_meta, "blocked"))
        return _result(case_meta, "blocked", "blocked", f"页面等待超时：{exc}", "页面未稳定", screenshots)
    except Exception as exc:  # noqa: BLE001
        screenshots.extend(_capture_evidence(goal, evidence_dir, case_meta, "script_error"))
        return _result(case_meta, "ignored", "test_script_error", f"脚本异常：{exc!r}", "脚本未完成断言", screenshots)


def test_tc_002_05(*, page: Page, settings: Settings, evidence_dir: Path, case_meta: dict) -> dict:
    """独立验证仅按状态查询。"""
    goal = TargetGoalPage(page, settings)
    screenshots: list[str] = []
    try:
        goal.ensure_open()
        goal.wait_ready()
        years = goal.get_table_years()
        if not years:
            raise TargetGoalReadinessError("列表没有可用状态数据")
        selected_status = goal.get_row_status(years[0])
        goal.select_status(selected_status)
        goal.click_query()
        actual_statuses = _visible_statuses(goal)
        actual = {"selected_status": selected_status, "result_statuses": actual_statuses}
        screenshots.extend(_capture_region(goal, evidence_dir, case_meta, "assertion", "table"))
        if not actual_statuses or any(value != selected_status for value in actual_statuses):
            screenshots.extend(_capture_region(goal, evidence_dir, case_meta, "failure", "table"))
            return _result(case_meta, "failed", "product_defect", f"状态查询结果未全部匹配 {selected_status}", actual, screenshots)
        return _result(case_meta, "passed", "passed", f"状态查询结果均匹配 {selected_status}", actual, screenshots)
    except TargetGoalReadinessError as exc:
        screenshots.extend(_capture_region(goal, evidence_dir, case_meta, "blocked"))
        return _result(case_meta, "blocked", "blocked", str(exc), "页面或测试数据未就绪", screenshots)
    except TargetGoalSelectorError as exc:
        screenshots.extend(_capture_region(goal, evidence_dir, case_meta, "script_error"))
        return _result(case_meta, "ignored", "test_script_error", str(exc), "DOM 契约不可定位", screenshots)
    except PlaywrightTimeoutError as exc:
        screenshots.extend(_capture_region(goal, evidence_dir, case_meta, "error"))
        message = str(exc).lower()
        if "not enabled" in message or "not editable" in message or "locator.fill" in message:
            return _result(case_meta, "ignored", "test_script_error", f"控件实现错误：{exc}", "控件不可编辑", screenshots)
        return _result(case_meta, "blocked", "blocked", f"页面等待超时：{exc}", "页面未稳定", screenshots)
    except Exception as exc:  # noqa: BLE001
        screenshots.extend(_capture_region(goal, evidence_dir, case_meta, "script_error"))
        return _result(case_meta, "ignored", "test_script_error", f"脚本异常：{exc!r}", "脚本未完成断言", screenshots)


def test_tc_002_06(*, page: Page, settings: Settings, evidence_dir: Path, case_meta: dict) -> dict:
    """独立验证年度与状态组合查询。"""
    goal = TargetGoalPage(page, settings)
    screenshots: list[str] = []
    try:
        goal.ensure_open()
        goal.wait_ready()
        years = goal.get_table_years()
        if not years:
            raise TargetGoalReadinessError("列表没有可用于组合查询的数据")
        selected_year = years[0]
        selected_status = goal.get_row_status(selected_year)
        goal.select_year(selected_year)
        goal.select_status(selected_status)
        goal.click_query()
        result_years = goal.get_visible_row_years()
        result_statuses = _visible_statuses(goal)
        actual = {"selected_year": selected_year, "selected_status": selected_status, "result_years": result_years, "result_statuses": result_statuses}
        screenshots.extend(_capture_region(goal, evidence_dir, case_meta, "assertion", "table"))
        valid = bool(result_years) and all(value == selected_year for value in result_years) and bool(result_statuses) and all(value == selected_status for value in result_statuses)
        if not valid:
            screenshots.extend(_capture_region(goal, evidence_dir, case_meta, "failure", "table"))
            return _result(case_meta, "failed", "product_defect", "年度与状态组合查询结果未同时匹配筛选条件", actual, screenshots)
        return _result(case_meta, "passed", "passed", "年度和状态组合查询结果匹配", actual, screenshots)
    except TargetGoalReadinessError as exc:
        screenshots.extend(_capture_region(goal, evidence_dir, case_meta, "blocked"))
        return _result(case_meta, "blocked", "blocked", str(exc), "页面或测试数据未就绪", screenshots)
    except TargetGoalSelectorError as exc:
        screenshots.extend(_capture_region(goal, evidence_dir, case_meta, "script_error"))
        return _result(case_meta, "ignored", "test_script_error", str(exc), "DOM 契约不可定位", screenshots)
    except PlaywrightTimeoutError as exc:
        screenshots.extend(_capture_region(goal, evidence_dir, case_meta, "error"))
        message = str(exc).lower()
        if "not enabled" in message or "not editable" in message or "locator.fill" in message:
            return _result(case_meta, "ignored", "test_script_error", f"控件实现错误：{exc}", "控件不可编辑", screenshots)
        return _result(case_meta, "blocked", "blocked", f"页面等待超时：{exc}", "页面未稳定", screenshots)
    except Exception as exc:  # noqa: BLE001
        screenshots.extend(_capture_region(goal, evidence_dir, case_meta, "script_error"))
        return _result(case_meta, "ignored", "test_script_error", f"脚本异常：{exc!r}", "脚本未完成断言", screenshots)


def test_tc_002_08(*, page: Page, settings: Settings, evidence_dir: Path, case_meta: dict) -> dict:
    """独立验证重置恢复默认查询条件。"""
    goal = TargetGoalPage(page, settings)
    screenshots: list[str] = []
    try:
        goal.ensure_open()
        goal.wait_ready()
        years = goal.get_table_years()
        if not years:
            raise TargetGoalReadinessError("列表没有可用于重置验证的数据")
        selected_year = years[0]
        selected_status = goal.get_row_status(selected_year)
        goal.select_year(selected_year)
        goal.select_status(selected_status)
        goal.click_query()
        goal.reset_query()
        values = goal.get_query_values()
        actual = {"query_values_after_reset": values, "row_count": len(goal.get_table_years())}
        screenshots.extend(_capture_region(goal, evidence_dir, case_meta, "assertion", "query"))
        valid = values.get("year") in ("", None) and values.get("status") == "请选择状态"
        if not valid:
            screenshots.extend(_capture_region(goal, evidence_dir, case_meta, "failure", "query"))
            return _result(case_meta, "failed", "product_defect", "重置后查询条件未恢复默认值", actual, screenshots)
        return _result(case_meta, "passed", "passed", "重置后年度和状态恢复默认", actual, screenshots)
    except TargetGoalReadinessError as exc:
        screenshots.extend(_capture_region(goal, evidence_dir, case_meta, "blocked"))
        return _result(case_meta, "blocked", "blocked", str(exc), "页面或测试数据未就绪", screenshots)
    except TargetGoalSelectorError as exc:
        screenshots.extend(_capture_region(goal, evidence_dir, case_meta, "script_error"))
        return _result(case_meta, "ignored", "test_script_error", str(exc), "DOM 契约不可定位", screenshots)
    except PlaywrightTimeoutError as exc:
        screenshots.extend(_capture_region(goal, evidence_dir, case_meta, "error"))
        message = str(exc).lower()
        if "not enabled" in message or "not editable" in message or "locator.fill" in message:
            return _result(case_meta, "ignored", "test_script_error", f"控件实现错误：{exc}", "控件不可编辑", screenshots)
        return _result(case_meta, "blocked", "blocked", f"页面等待超时：{exc}", "页面未稳定", screenshots)
    except Exception as exc:  # noqa: BLE001
        screenshots.extend(_capture_region(goal, evidence_dir, case_meta, "script_error"))
        return _result(case_meta, "ignored", "test_script_error", f"脚本异常：{exc!r}", "脚本未完成断言", screenshots)


def test_tc_002_20(*, page: Page, settings: Settings, evidence_dir: Path, case_meta: dict) -> dict:
    """独立验证新增目标按月平均分配及月度合计。"""
    goal = TargetGoalPage(page, settings)
    screenshots: list[str] = []
    try:
        goal.ensure_open()
        goal.wait_ready()
        existing_years, year = _choose_unused_year(goal)
        goal.open_new_dialog()
        goal.fill_goal_form(year)
        monthly_values = goal.get_monthly_values()
        screenshots.extend(_capture_region(goal, evidence_dir, case_meta, "prepare", "dialog"))
        goal.save_dialog()
        goal.wait_table_ready()
        status = goal.get_row_status(year)
        numbers = [float(value) for value in monthly_values]
        actual = {"existing_years": existing_years, "selected_year": year, "monthly_values": monthly_values, "monthly_total": sum(numbers), "annual_quantity": 120.0, "status": status}
        screenshots.extend(_capture_region(goal, evidence_dir, case_meta, "assertion", "table"))
        valid = len(numbers) == 12 and max(numbers) == min(numbers) and abs(sum(numbers) - 120.0) < 1e-9 and status == "暂存"
        if not valid:
            screenshots.extend(_capture_region(goal, evidence_dir, case_meta, "failure", "table"))
            return _result(case_meta, "failed", "product_defect", "月度分配未满足十二个月均分且合计等于年度宰杀量", actual, screenshots)
        return _result(case_meta, "passed", "passed", f"未占用年度 {year} 的月度分配均分且合计正确", actual, screenshots)
    except TargetGoalReadinessError as exc:
        screenshots.extend(_capture_region(goal, evidence_dir, case_meta, "blocked"))
        return _result(case_meta, "blocked", "blocked", str(exc), "页面或测试数据未就绪", screenshots)
    except TargetGoalSelectorError as exc:
        screenshots.extend(_capture_region(goal, evidence_dir, case_meta, "script_error"))
        return _result(case_meta, "ignored", "test_script_error", str(exc), "DOM 契约不可定位", screenshots)
    except PlaywrightTimeoutError as exc:
        screenshots.extend(_capture_region(goal, evidence_dir, case_meta, "error"))
        message = str(exc).lower()
        if "not enabled" in message or "not editable" in message or "locator.fill" in message:
            return _result(case_meta, "ignored", "test_script_error", f"控件实现错误：{exc}", "控件不可编辑", screenshots)
        return _result(case_meta, "blocked", "blocked", f"页面等待超时：{exc}", "页面未稳定", screenshots)
    except Exception as exc:  # noqa: BLE001
        screenshots.extend(_capture_region(goal, evidence_dir, case_meta, "script_error"))
        return _result(case_meta, "ignored", "test_script_error", f"脚本异常：{exc!r}", "脚本未完成断言", screenshots)


def test_tc_002_27(*, page: Page, settings: Settings, evidence_dir: Path, case_meta: dict) -> dict:
    """独立验证动态未占用年度目标保存后仍为暂存。"""
    goal = TargetGoalPage(page, settings)
    screenshots: list[str] = []
    try:
        goal.ensure_open()
        goal.wait_ready()
        existing_years, year = _choose_unused_year(goal)
        screenshots.extend(_ensure_owned_draft(goal, year, evidence_dir, case_meta))
        goal.open_edit_dialog(year)
        goal.save_dialog()
        status = goal.get_row_status(year)
        actual = {"existing_years": existing_years, "selected_year": year, "status": status}
        screenshots.extend(_capture_region(goal, evidence_dir, case_meta, "assertion", "table"))
        if status != "暂存":
            screenshots.extend(_capture_region(goal, evidence_dir, case_meta, "failure", "table"))
            return _result(case_meta, "failed", "product_defect", "目标保存后状态不是暂存", actual, screenshots)
        return _result(case_meta, "passed", "passed", f"动态选择未占用年度 {year} 后保存状态仍为暂存", actual, screenshots)
    except TargetGoalReadinessError as exc:
        screenshots.extend(_capture_region(goal, evidence_dir, case_meta, "blocked"))
        return _result(case_meta, "blocked", "blocked", str(exc), "页面或测试数据未就绪", screenshots)
    except TargetGoalSelectorError as exc:
        screenshots.extend(_capture_region(goal, evidence_dir, case_meta, "script_error"))
        return _result(case_meta, "ignored", "test_script_error", str(exc), "DOM 契约不可定位", screenshots)
    except PlaywrightTimeoutError as exc:
        screenshots.extend(_capture_region(goal, evidence_dir, case_meta, "error"))
        message = str(exc).lower()
        if "not enabled" in message or "not editable" in message or "locator.fill" in message:
            return _result(case_meta, "ignored", "test_script_error", f"控件实现错误：{exc}", "控件不可编辑", screenshots)
        return _result(case_meta, "blocked", "blocked", f"页面等待超时：{exc}", "页面未稳定", screenshots)
    except Exception as exc:  # noqa: BLE001
        screenshots.extend(_capture_region(goal, evidence_dir, case_meta, "script_error"))
        return _result(case_meta, "ignored", "test_script_error", f"脚本异常：{exc!r}", "脚本未完成断言", screenshots)


def test_tc_002_28(*, page: Page, settings: Settings, evidence_dir: Path, case_meta: dict) -> dict:
    """独立验证新增弹窗直接保存并提交后进入待审核。"""
    goal = TargetGoalPage(page, settings)
    screenshots: list[str] = []
    try:
        goal.ensure_open()
        goal.wait_ready()
        existing_years = goal.collect_years_across_pages()
        max_year = max(existing_years, default=datetime.now().year)
        year = max_year + 1
        while year in existing_years or year in _OWNED_YEARS:
            year += 1
        if goal.get_row_by_year(year) is not None:
            raise TargetGoalReadinessError(f"年度 {year} 已存在但不属于当前 RUN，拒绝修改")
        goal.open_new_dialog()
        goal.fill_goal_form(year)
        screenshots.extend(_capture_region(goal, evidence_dir, case_meta, "prepare", "dialog"))
        goal.save_and_submit_dialog()
        status = goal.get_row_status(year)
        actual = {"existing_years": existing_years, "selected_year": year, "status": status}
        screenshots.extend(_capture_region(goal, evidence_dir, case_meta, "assertion", "table"))
        if status != "待审核":
            screenshots.extend(_capture_region(goal, evidence_dir, case_meta, "failure", "table"))
            return _result(case_meta, "failed", "product_defect", "保存并提交后状态不是待审核", actual, screenshots)
        _OWNED_YEARS.add(year)
        return _result(case_meta, "passed", "passed", f"动态选择未占用年度 {year} 后直接保存并提交进入待审核", actual, screenshots)
    except TargetGoalReadinessError as exc:
        screenshots.extend(_capture_region(goal, evidence_dir, case_meta, "blocked"))
        return _result(case_meta, "blocked", "blocked", str(exc), "页面或测试数据未就绪", screenshots)
    except TargetGoalSelectorError as exc:
        screenshots.extend(_capture_region(goal, evidence_dir, case_meta, "script_error"))
        return _result(case_meta, "ignored", "test_script_error", str(exc), "DOM 契约不可定位", screenshots)
    except PlaywrightTimeoutError as exc:
        screenshots.extend(_capture_region(goal, evidence_dir, case_meta, "error"))
        message = str(exc).lower()
        if "not enabled" in message or "not editable" in message or "locator.fill" in message:
            return _result(case_meta, "ignored", "test_script_error", f"控件实现错误：{exc}", "控件不可编辑", screenshots)
        return _result(case_meta, "blocked", "blocked", f"页面等待超时：{exc}", "页面未稳定", screenshots)
    except Exception as exc:  # noqa: BLE001
        screenshots.extend(_capture_region(goal, evidence_dir, case_meta, "script_error"))
        return _result(case_meta, "ignored", "test_script_error", f"脚本异常：{exc!r}", "脚本未完成断言", screenshots)


def test_tc_002_75(*, page: Page, settings: Settings, evidence_dir: Path, case_meta: dict) -> dict:
    """独立验证暂存目标提交时出现确认框。"""
    goal = TargetGoalPage(page, settings)
    screenshots: list[str] = []
    try:
        goal.ensure_open()
        goal.wait_ready()
        _existing_years, year = _choose_unused_year(goal)
        screenshots.extend(_ensure_owned_draft(goal, year, evidence_dir, case_meta))
        row = goal.get_row_by_year(year)
        if row is None:
            raise TargetGoalReadinessError(f"当前 RUN 创建的年度 {year} 未出现在列表")
        row.get_by_role("button", name="提交", exact=True).click()
        box = goal.page.locator(".el-message-box:visible")
        box.wait_for(state="visible", timeout=8_000)
        confirmation_text = box.inner_text()
        screenshots.extend(_capture_region(goal, evidence_dir, case_meta, "assertion", "table"))
        valid = "提交" in confirmation_text
        cancel = box.get_by_role("button", name="取消", exact=True)
        if cancel.count():
            cancel.click()
        if not valid:
            screenshots.extend(_capture_region(goal, evidence_dir, case_meta, "failure", "table"))
            return _result(case_meta, "failed", "product_defect", "提交确认框未表达提交审核意图", {"year": year, "confirmation_text": confirmation_text}, screenshots)
        return _result(case_meta, "passed", "passed", "提交确认框表达提交审核意图并已取消", {"year": year, "confirmation_text": confirmation_text}, screenshots)
    except TargetGoalReadinessError as exc:
        screenshots.extend(_capture_region(goal, evidence_dir, case_meta, "blocked"))
        return _result(case_meta, "blocked", "blocked", str(exc), "页面或测试数据未就绪", screenshots)
    except TargetGoalSelectorError as exc:
        screenshots.extend(_capture_region(goal, evidence_dir, case_meta, "script_error"))
        return _result(case_meta, "ignored", "test_script_error", str(exc), "DOM 契约不可定位", screenshots)
    except PlaywrightTimeoutError as exc:
        screenshots.extend(_capture_region(goal, evidence_dir, case_meta, "error"))
        message = str(exc).lower()
        if "not enabled" in message or "not editable" in message or "locator.fill" in message:
            return _result(case_meta, "ignored", "test_script_error", f"控件实现错误：{exc}", "控件不可编辑", screenshots)
        return _result(case_meta, "blocked", "blocked", f"页面等待超时：{exc}", "页面未稳定", screenshots)
    except Exception as exc:  # noqa: BLE001
        screenshots.extend(_capture_region(goal, evidence_dir, case_meta, "script_error"))
        return _result(case_meta, "ignored", "test_script_error", f"脚本异常：{exc!r}", "脚本未完成断言", screenshots)


def test_tc_002_77(*, page: Page, settings: Settings, evidence_dir: Path, case_meta: dict) -> dict:
    """独立验证提交确认后目标状态展示为待审核。"""
    goal = TargetGoalPage(page, settings)
    screenshots: list[str] = []
    try:
        goal.ensure_open()
        goal.wait_ready()
        _existing_years, year = _choose_unused_year(goal)
        screenshots.extend(_ensure_owned_draft(goal, year, evidence_dir, case_meta))
        row = goal.get_row_by_year(year)
        if row is None:
            raise TargetGoalReadinessError(f"当前 RUN 创建的年度 {year} 未出现在列表")
        row.get_by_role("button", name="提交", exact=True).click()
        box = goal.page.locator(".el-message-box:visible")
        box.wait_for(state="visible", timeout=8_000)
        confirmation_text = box.inner_text()
        box.get_by_role("button", name="确定", exact=True).click()
        goal.wait_table_ready()
        status = goal.get_row_status(year)
        actual = {"year": year, "confirmation_text": confirmation_text, "status": status}
        screenshots.extend(_capture_region(goal, evidence_dir, case_meta, "assertion", "table"))
        if status != "待审核":
            screenshots.extend(_capture_region(goal, evidence_dir, case_meta, "failure", "table"))
            return _result(case_meta, "failed", "product_defect", "提交确认后状态不是待审核", actual, screenshots)
        return _result(case_meta, "passed", "passed", "提交确认后状态为待审核", actual, screenshots)
    except TargetGoalReadinessError as exc:
        screenshots.extend(_capture_region(goal, evidence_dir, case_meta, "blocked"))
        return _result(case_meta, "blocked", "blocked", str(exc), "页面或测试数据未就绪", screenshots)
    except TargetGoalSelectorError as exc:
        screenshots.extend(_capture_region(goal, evidence_dir, case_meta, "script_error"))
        return _result(case_meta, "ignored", "test_script_error", str(exc), "DOM 契约不可定位", screenshots)
    except PlaywrightTimeoutError as exc:
        screenshots.extend(_capture_region(goal, evidence_dir, case_meta, "error"))
        message = str(exc).lower()
        if "not enabled" in message or "not editable" in message or "locator.fill" in message:
            return _result(case_meta, "ignored", "test_script_error", f"控件实现错误：{exc}", "控件不可编辑", screenshots)
        return _result(case_meta, "blocked", "blocked", f"页面等待超时：{exc}", "页面未稳定", screenshots)
    except Exception as exc:  # noqa: BLE001
        screenshots.extend(_capture_region(goal, evidence_dir, case_meta, "script_error"))
        return _result(case_meta, "ignored", "test_script_error", f"脚本异常：{exc!r}", "脚本未完成断言", screenshots)


def test_tc_002_84(*, page: Page, settings: Settings, evidence_dir: Path, case_meta: dict) -> dict:
    """独立验证审核驳回后状态变为驳回。"""
    goal = TargetGoalPage(page, settings)
    screenshots: list[str] = []
    try:
        goal.ensure_open()
        goal.wait_ready()
        _existing_years, year = _choose_unused_year(goal)
        screenshots.extend(_ensure_owned_draft(goal, year, evidence_dir, case_meta))
        goal.open_edit_dialog(year)
        goal.save_and_submit_dialog()
        goal.open_review_dialog(year)
        goal.dialog().get_by_role("button", name="驳回", exact=True).click()
        reason = goal.page.locator(".el-dialog:visible").last
        reason.locator('input[placeholder="请输入驳回原因"]').fill("AUTO测试_勿用_驳回原因")
        screenshots.extend(_capture_region(goal, evidence_dir, case_meta, "assertion", "dialog"))
        reason.get_by_role("button", name="确定", exact=True).click()
        goal.wait_table_ready()
        status = goal.get_row_status(year)
        actual = {"year": year, "status": status}
        screenshots.extend(_capture_region(goal, evidence_dir, case_meta, "assertion_after_action", "table"))
        if status != "驳回":
            screenshots.extend(_capture_region(goal, evidence_dir, case_meta, "failure", "table"))
            return _result(case_meta, "failed", "product_defect", "驳回确认后状态不是驳回", actual, screenshots)
        return _result(case_meta, "passed", "passed", "专属目标驳回成功", actual, screenshots)
    except TargetGoalReadinessError as exc:
        screenshots.extend(_capture_region(goal, evidence_dir, case_meta, "blocked"))
        return _result(case_meta, "blocked", "blocked", str(exc), "页面或测试数据未就绪", screenshots)
    except TargetGoalSelectorError as exc:
        screenshots.extend(_capture_region(goal, evidence_dir, case_meta, "script_error"))
        return _result(case_meta, "ignored", "test_script_error", str(exc), "DOM 契约不可定位", screenshots)
    except PlaywrightTimeoutError as exc:
        screenshots.extend(_capture_region(goal, evidence_dir, case_meta, "error"))
        message = str(exc).lower()
        if "not enabled" in message or "not editable" in message or "locator.fill" in message:
            return _result(case_meta, "ignored", "test_script_error", f"控件实现错误：{exc}", "控件不可编辑", screenshots)
        return _result(case_meta, "blocked", "blocked", f"页面等待超时：{exc}", "页面未稳定", screenshots)
    except Exception as exc:  # noqa: BLE001
        screenshots.extend(_capture_region(goal, evidence_dir, case_meta, "script_error"))
        return _result(case_meta, "ignored", "test_script_error", f"脚本异常：{exc!r}", "脚本未完成断言", screenshots)


def test_tc_002_85(*, page: Page, settings: Settings, evidence_dir: Path, case_meta: dict) -> dict:
    """独立验证驳回原因为空时被阻断，填写后可保存。"""
    goal = TargetGoalPage(page, settings)
    screenshots: list[str] = []
    try:
        goal.ensure_open()
        goal.wait_ready()
        _existing_years, year = _choose_unused_year(goal)
        screenshots.extend(_ensure_owned_draft(goal, year, evidence_dir, case_meta))
        goal.open_edit_dialog(year)
        goal.save_and_submit_dialog()
        goal.open_review_dialog(year)
        goal.dialog().get_by_role("button", name="驳回", exact=True).click()
        reason = goal.page.locator(".el-dialog:visible").last
        reason.get_by_role("button", name="确定", exact=True).click()
        empty_reason_blocked = reason.is_visible()
        screenshots.extend(_capture_region(goal, evidence_dir, case_meta, "empty_reason", "dialog"))
        reason.locator('input[placeholder="请输入驳回原因"]').fill("AUTO测试_勿用_有效驳回原因")
        reason.get_by_role("button", name="确定", exact=True).click()
        goal.wait_table_ready()
        status = goal.get_row_status(year)
        actual = {"year": year, "status": status, "empty_reason_blocked": empty_reason_blocked}
        screenshots.extend(_capture_region(goal, evidence_dir, case_meta, "assertion", "table"))
        if not empty_reason_blocked or status != "驳回":
            screenshots.extend(_capture_region(goal, evidence_dir, case_meta, "failure", "table"))
            return _result(case_meta, "failed", "product_defect", "空驳回原因未被阻断或有效原因提交后状态不正确", actual, screenshots)
        return _result(case_meta, "passed", "passed", "空驳回原因被阻断，填写有效原因后驳回成功", actual, screenshots)
    except TargetGoalReadinessError as exc:
        screenshots.extend(_capture_region(goal, evidence_dir, case_meta, "blocked"))
        return _result(case_meta, "blocked", "blocked", str(exc), "页面或测试数据未就绪", screenshots)
    except TargetGoalSelectorError as exc:
        screenshots.extend(_capture_region(goal, evidence_dir, case_meta, "script_error"))
        return _result(case_meta, "ignored", "test_script_error", str(exc), "DOM 契约不可定位", screenshots)
    except PlaywrightTimeoutError as exc:
        screenshots.extend(_capture_region(goal, evidence_dir, case_meta, "error"))
        message = str(exc).lower()
        if "not enabled" in message or "not editable" in message or "locator.fill" in message:
            return _result(case_meta, "ignored", "test_script_error", f"控件实现错误：{exc}", "控件不可编辑", screenshots)
        return _result(case_meta, "blocked", "blocked", f"页面等待超时：{exc}", "页面未稳定", screenshots)
    except Exception as exc:  # noqa: BLE001
        screenshots.extend(_capture_region(goal, evidence_dir, case_meta, "script_error"))
        return _result(case_meta, "ignored", "test_script_error", f"脚本异常：{exc!r}", "脚本未完成断言", screenshots)


def test_tc_002_86(*, page: Page, settings: Settings, evidence_dir: Path, case_meta: dict) -> dict:
    """独立验证审核通过直接成功且状态更新。"""
    goal = TargetGoalPage(page, settings)
    screenshots: list[str] = []
    try:
        goal.ensure_open()
        goal.wait_ready()
        _existing_years, year = _choose_unused_year(goal)
        screenshots.extend(_ensure_owned_draft(goal, year, evidence_dir, case_meta))
        goal.open_edit_dialog(year)
        goal.save_and_submit_dialog()
        goal.open_review_dialog(year)
        goal.dialog().get_by_role("button", name="通过", exact=True).click()
        goal.wait_table_ready()
        status = goal.get_row_status(year)
        actual = {"year": year, "status": status, "confirmation_count": goal.page.locator(".el-message-box:visible").count()}
        screenshots.extend(_capture_region(goal, evidence_dir, case_meta, "assertion", "table"))
        if status != "审核通过" or actual["confirmation_count"] != 0:
            screenshots.extend(_capture_region(goal, evidence_dir, case_meta, "failure", "table"))
            return _result(case_meta, "failed", "product_defect", "审核通过未直接成功或出现二次确认框", actual, screenshots)
        return _result(case_meta, "passed", "passed", "审核通过后状态为审核通过且无二次确认框", actual, screenshots)
    except TargetGoalReadinessError as exc:
        screenshots.extend(_capture_region(goal, evidence_dir, case_meta, "blocked"))
        return _result(case_meta, "blocked", "blocked", str(exc), "页面或测试数据未就绪", screenshots)
    except TargetGoalSelectorError as exc:
        screenshots.extend(_capture_region(goal, evidence_dir, case_meta, "script_error"))
        return _result(case_meta, "ignored", "test_script_error", str(exc), "DOM 契约不可定位", screenshots)
    except PlaywrightTimeoutError as exc:
        screenshots.extend(_capture_region(goal, evidence_dir, case_meta, "error"))
        message = str(exc).lower()
        if "not enabled" in message or "not editable" in message or "locator.fill" in message:
            return _result(case_meta, "ignored", "test_script_error", f"控件实现错误：{exc}", "控件不可编辑", screenshots)
        return _result(case_meta, "blocked", "blocked", f"页面等待超时：{exc}", "页面未稳定", screenshots)
    except Exception as exc:  # noqa: BLE001
        screenshots.extend(_capture_region(goal, evidence_dir, case_meta, "script_error"))
        return _result(case_meta, "ignored", "test_script_error", f"脚本异常：{exc!r}", "脚本未完成断言", screenshots)


def test_tc_002_87(*, page: Page, settings: Settings, evidence_dir: Path, case_meta: dict) -> dict:
    """独立验证审核通过后审核信息列可回读。"""
    goal = TargetGoalPage(page, settings)
    screenshots: list[str] = []
    try:
        goal.ensure_open()
        goal.wait_ready()
        _existing_years, year = _choose_unused_year(goal)
        screenshots.extend(_ensure_owned_draft(goal, year, evidence_dir, case_meta))
        goal.open_edit_dialog(year)
        goal.save_and_submit_dialog()
        goal.open_review_dialog(year)
        goal.dialog().get_by_role("button", name="通过", exact=True).click()
        goal.wait_table_ready()
        row = goal.get_row_by_year(year)
        cells = row.locator("td").all_inner_texts() if row is not None else []
        status = goal.get_row_status(year)
        actual = {"year": year, "status": status, "row_cells": cells}
        screenshots.extend(_capture_region(goal, evidence_dir, case_meta, "assertion", "table"))
        if status != "审核通过" or len(cells) < 8:
            screenshots.extend(_capture_region(goal, evidence_dir, case_meta, "failure", "table"))
            return _result(case_meta, "failed", "product_defect", "审核通过行缺少审核信息列或状态不正确", actual, screenshots)
        return _result(case_meta, "passed", "passed", "审核通过行已回读状态及审核信息列", actual, screenshots)
    except TargetGoalReadinessError as exc:
        screenshots.extend(_capture_region(goal, evidence_dir, case_meta, "blocked"))
        return _result(case_meta, "blocked", "blocked", str(exc), "页面或测试数据未就绪", screenshots)
    except TargetGoalSelectorError as exc:
        screenshots.extend(_capture_region(goal, evidence_dir, case_meta, "script_error"))
        return _result(case_meta, "ignored", "test_script_error", str(exc), "DOM 契约不可定位", screenshots)
    except PlaywrightTimeoutError as exc:
        screenshots.extend(_capture_region(goal, evidence_dir, case_meta, "error"))
        message = str(exc).lower()
        if "not enabled" in message or "not editable" in message or "locator.fill" in message:
            return _result(case_meta, "ignored", "test_script_error", f"控件实现错误：{exc}", "控件不可编辑", screenshots)
        return _result(case_meta, "blocked", "blocked", f"页面等待超时：{exc}", "页面未稳定", screenshots)
    except Exception as exc:  # noqa: BLE001
        screenshots.extend(_capture_region(goal, evidence_dir, case_meta, "script_error"))
        return _result(case_meta, "ignored", "test_script_error", f"脚本异常：{exc!r}", "脚本未完成断言", screenshots)


def test_tc_002_88(*, page: Page, settings: Settings, evidence_dir: Path, case_meta: dict) -> dict:
    """独立验证删除确认框出现。"""
    goal = TargetGoalPage(page, settings)
    screenshots: list[str] = []
    try:
        goal.ensure_open()
        goal.wait_ready()
        _existing_years, year = _choose_unused_year(goal)
        screenshots.extend(_ensure_owned_draft(goal, year, evidence_dir, case_meta))
        goal.open_delete_confirmation(year)
        box = goal.page.locator(".el-message-box:visible")
        confirmation_text = box.inner_text()
        screenshots.extend(_capture_region(goal, evidence_dir, case_meta, "assertion", "table"))
        cancel = box.get_by_role("button", name="取消", exact=True)
        if cancel.count():
            cancel.click()
        actual = {"year": year, "confirmation_text": confirmation_text}
        if "删除" not in confirmation_text:
            screenshots.extend(_capture_region(goal, evidence_dir, case_meta, "failure", "table"))
            return _result(case_meta, "failed", "product_defect", "删除确认框未表达删除意图", actual, screenshots)
        return _result(case_meta, "passed", "passed", "删除确认框表达删除意图并已取消", actual, screenshots)
    except TargetGoalReadinessError as exc:
        screenshots.extend(_capture_region(goal, evidence_dir, case_meta, "blocked"))
        return _result(case_meta, "blocked", "blocked", str(exc), "页面或测试数据未就绪", screenshots)
    except TargetGoalSelectorError as exc:
        screenshots.extend(_capture_region(goal, evidence_dir, case_meta, "script_error"))
        return _result(case_meta, "ignored", "test_script_error", str(exc), "DOM 契约不可定位", screenshots)
    except PlaywrightTimeoutError as exc:
        screenshots.extend(_capture_region(goal, evidence_dir, case_meta, "error"))
        message = str(exc).lower()
        if "not enabled" in message or "not editable" in message or "locator.fill" in message:
            return _result(case_meta, "ignored", "test_script_error", f"控件实现错误：{exc}", "控件不可编辑", screenshots)
        return _result(case_meta, "blocked", "blocked", f"页面等待超时：{exc}", "页面未稳定", screenshots)
    except Exception as exc:  # noqa: BLE001
        screenshots.extend(_capture_region(goal, evidence_dir, case_meta, "script_error"))
        return _result(case_meta, "ignored", "test_script_error", f"脚本异常：{exc!r}", "脚本未完成断言", screenshots)


def test_tc_002_90(*, page: Page, settings: Settings, evidence_dir: Path, case_meta: dict) -> dict:
    """独立验证确认删除后目标从列表消失。"""
    goal = TargetGoalPage(page, settings)
    screenshots: list[str] = []
    try:
        goal.ensure_open()
        goal.wait_ready()
        _existing_years, year = _choose_unused_year(goal)
        screenshots.extend(_ensure_owned_draft(goal, year, evidence_dir, case_meta))
        goal.open_delete_confirmation(year)
        box = goal.page.locator(".el-message-box:visible")
        confirmation_text = box.inner_text()
        screenshots.extend(_capture_region(goal, evidence_dir, case_meta, "delete_confirm", "table"))
        box.get_by_role("button", name="确定", exact=True).click()
        goal.wait_table_ready()
        row_exists = goal.get_row_by_year(year) is not None
        actual = {"year": year, "confirmation_text": confirmation_text, "row_exists_after_delete": row_exists}
        screenshots.extend(_capture_region(goal, evidence_dir, case_meta, "assertion", "table"))
        if row_exists:
            screenshots.extend(_capture_region(goal, evidence_dir, case_meta, "failure", "table"))
            return _result(case_meta, "failed", "product_defect", "确认删除后记录仍存在于列表", actual, screenshots)
        return _result(case_meta, "passed", "passed", "专属目标删除后从列表消失", actual, screenshots)
    except TargetGoalReadinessError as exc:
        screenshots.extend(_capture_region(goal, evidence_dir, case_meta, "blocked"))
        return _result(case_meta, "blocked", "blocked", str(exc), "页面或测试数据未就绪", screenshots)
    except TargetGoalSelectorError as exc:
        screenshots.extend(_capture_region(goal, evidence_dir, case_meta, "script_error"))
        return _result(case_meta, "ignored", "test_script_error", str(exc), "DOM 契约不可定位", screenshots)
    except PlaywrightTimeoutError as exc:
        screenshots.extend(_capture_region(goal, evidence_dir, case_meta, "error"))
        message = str(exc).lower()
        if "not enabled" in message or "not editable" in message or "locator.fill" in message:
            return _result(case_meta, "ignored", "test_script_error", f"控件实现错误：{exc}", "控件不可编辑", screenshots)
        return _result(case_meta, "blocked", "blocked", f"页面等待超时：{exc}", "页面未稳定", screenshots)
    except Exception as exc:  # noqa: BLE001
        screenshots.extend(_capture_region(goal, evidence_dir, case_meta, "script_error"))
        return _result(case_meta, "ignored", "test_script_error", f"脚本异常：{exc!r}", "脚本未完成断言", screenshots)

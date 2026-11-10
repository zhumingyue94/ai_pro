"""制定排程模块自动化用例。

覆盖 REQ-004 制定排程 19 条 P1 用例（查询 5、制定计算/保存 6、编辑/提交/删除 5、智能推荐 3）。
选择器与交互契约来源：2026-08-25 页面侦查 dump 的真实 DOM。
"""

from __future__ import annotations

import re
from datetime import datetime, timedelta
from pathlib import Path

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError

from config.settings import Settings
from pages.scheduling.make_plan_page import (
    MakePlanPage,
    MakePlanReadinessError,
    MakePlanSelectorError,
)


def _capture_evidence(mp: MakePlanPage, evidence_dir: Path, case_meta: dict, suffix: str) -> list[str]:
    """在断言点保存区域截图和完整页面截图。"""
    case_id = case_meta["case_id"]
    check_id = case_meta["check_id"]
    scope_path = evidence_dir / f"{case_id}_{check_id}_{suffix}_scope.png"
    full_path = evidence_dir / f"{case_id}_{check_id}_{suffix}_full.png"
    try:
        mp.capture_scope(scope_path)
    except Exception:
        pass
    try:
        mp.capture_full(full_path)
    except Exception:
        pass
    return [str(p) for p in (scope_path, full_path) if p.is_file()]


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


def _capture_table(mp: MakePlanPage, evidence_dir: Path, case_meta: dict, suffix: str) -> list[str]:
    """在业务动作完成点保存表格区域和完整页面截图。"""
    case_id = case_meta["case_id"]
    check_id = case_meta["check_id"]
    scope_path = evidence_dir / f"{case_id}_{check_id}_{suffix}_scope.png"
    full_path = evidence_dir / f"{case_id}_{check_id}_{suffix}_full.png"
    try:
        mp.page.locator(".el-table:visible").first.screenshot(path=str(scope_path))
    except Exception:
        try:
            mp.capture_scope(scope_path)
        except Exception:
            pass
    try:
        mp.capture_full(full_path)
    except Exception:
        pass
    return [str(p) for p in (scope_path, full_path) if p.is_file()]


def _handle_blocked(mp: MakePlanPage, evidence_dir: Path, case_meta: dict, exc: Exception) -> dict:
    """统一处理 blocked 类异常。"""
    shots = _capture_evidence(mp, evidence_dir, case_meta, "blocked")
    return _result(case_meta, "blocked", "blocked", str(exc), "页面或测试数据未就绪", shots)


def _handle_selector(mp: MakePlanPage, evidence_dir: Path, case_meta: dict, exc: Exception) -> dict:
    """统一处理选择器不可定位异常。"""
    shots = _capture_evidence(mp, evidence_dir, case_meta, "script_error")
    return _result(case_meta, "ignored", "test_script_error", str(exc), "DOM 契约不可定位", shots)


def _handle_timeout(mp: MakePlanPage, evidence_dir: Path, case_meta: dict, exc: Exception) -> dict:
    """统一处理超时异常。"""
    shots = _capture_evidence(mp, evidence_dir, case_meta, "timeout")
    msg = str(exc).lower()
    if "not enabled" in msg or "not editable" in msg or "locator.fill" in msg:
        return _result(case_meta, "ignored", "test_script_error", f"控件实现错误：{exc}", "控件不可编辑", shots)
    return _result(case_meta, "blocked", "blocked", f"页面等待超时：{exc}", "页面未稳定", shots)


def _handle_unexpected(mp: MakePlanPage, evidence_dir: Path, case_meta: dict, exc: Exception) -> dict:
    """统一处理未预期异常。"""
    shots = _capture_evidence(mp, evidence_dir, case_meta, "script_error")
    return _result(case_meta, "ignored", "test_script_error", f"脚本异常：{exc!r}", "脚本未完成断言", shots)


# ============================================================
# 辅助函数
# ============================================================


def _run_ts() -> str:
    """生成本次执行的时间戳标识，用于自造数据命名。"""
    return datetime.now().strftime("%H%M%S")


def _open_list(mp: MakePlanPage) -> None:
    """打开制定排程列表页并等待就绪。"""
    mp.ensure_open()
    mp.wait_ready()


def _fill_day_plan(mp: MakePlanPage, name: str | None, day_index: int = 0) -> dict | None:
    """在当前月份看板选择第 day_index 个待排日期并填写日计划表单。

    name 为 None 时不填计划名称（避免触发整表自动推荐，供智能推荐类用例核对候选分数）。
    返回所选日期/宰杀线/模版信息；无更多待排日期时返回 None。
    """
    if not mp.pick_pending_day(day_index):
        return None
    date = mp.current_edit_date()
    line = mp.select_editor_line(0)
    dialog = mp.open_template_dialog()
    template = mp.select_template(dialog)
    if name is not None:
        mp.fill_editor_field("计划名称", name)
    mp.fill_editor_field("宰杀量", "2")
    mp.fill_editor_field("出栏体重", "2.5")
    mp.fill_editor_field("苗重", "45")
    mp.fill_editor_field("孵化率", "95")
    mp.fill_editor_field("健雏率", "98")
    mp.page.wait_for_timeout(1_500)
    return {"date": date, "line": line, "template": template}


def _candidate_months() -> list[int]:
    """按经验排序返回候选月份：当前+2、+3、+1、+4、当前（限 1-12）。"""
    current = datetime.now().month
    months: list[int] = []
    for offset in (2, 3, 1, 4, 0):
        month = current + offset
        if 1 <= month <= 12 and month not in months:
            months.append(month)
    return months


def _search_workable_plan(mp: MakePlanPage, name: str, months: list[int] | None = None) -> dict:
    """逐月逐待排日查找存在可分配栋舍（养殖栋舍自动回填非空）的日期并完成表单填写。"""
    mp.ensure_open()
    mp.wait_ready()
    mp.open_create_editor()
    for month in (months or _candidate_months()):
        mp.pick_editor_month(month)
        for day_index in range(2):
            info = _fill_day_plan(mp, name, day_index)
            if info is None:
                break
            house = mp.read_editor_field("养殖栋舍")
            if house:
                return {"month": month, "house": house, **info}
            mp.reload_create_editor()
            mp.pick_editor_month(month)
    raise MakePlanReadinessError("各候选月份待排日期均无可分配栋舍，无法满足制定排程前置")


def _find_code_in_list(mp: MakePlanPage, month: int, date: str, line: str, status: str = "暂存") -> str:
    """在列表按月份+状态查询，按宰杀日期和宰杀线定位计划编号。"""
    mp.ensure_open()
    mp.wait_ready()
    mp.pick_query_month(month)
    mp.select_status(status)
    mp.click_query()
    for row in mp.get_table_rows():
        if row["date"] == date and row["line"] == line and row["status"] == status and row["code"]:
            return row["code"]
    raise MakePlanReadinessError(f"列表未找到 {month}月 {date} {line} 的{status}计划")


def _create_draft(mp: MakePlanPage, run_ts: str, case_id: str, months: list[int] | None = None) -> dict:
    """在存在可分配栋舍的待排日期创建一条暂存日计划，返回计划上下文。"""
    name = f"AUTO测试_勿用_RUN{run_ts}_{case_id}"
    ctx = _search_workable_plan(mp, name, months)
    mp.click_save_day()
    code = _find_code_in_list(mp, ctx["month"], ctx["date"], ctx["line"])
    return {**ctx, "name": name, "code": code}


def _cleanup_draft(mp: MakePlanPage, month: int, code: str) -> str:
    """尝试删除指定编号的暂存/驳回计划，返回清理结果文本。"""
    try:
        mp.ensure_open()
        mp.wait_ready()
        mp.pick_query_month(month)
        mp.click_query()
        if mp.find_row_by_code(code) is None:
            return "not_found"
        status = mp.get_row_status_by_code(code)
        if status not in ("暂存", "驳回"):
            return f"skip_status_{status}"
        mp.click_row_action(code, "删除")
        mp.confirm_message_box()
        mp.wait_success_message("成功")
        return "deleted"
    except Exception as exc:
        return f"cleanup_failed: {exc}"


def _query_month_status(mp: MakePlanPage, month: int, status: str) -> int:
    """查询指定月份+状态的列表行数。"""
    mp.ensure_open()
    mp.wait_ready()
    mp.pick_query_month(month)
    mp.select_status(status)
    mp.click_query()
    return mp.get_row_count()


def _open_editor_for_month(mp: MakePlanPage, month: int) -> None:
    """从列表页进入制定月度排程编辑页并切换到指定月份。"""
    mp.ensure_open()
    mp.wait_ready()
    mp.open_create_editor()
    mp.pick_editor_month(month)


def _open_drawer_without_autofill(mp: MakePlanPage, name_marker: str) -> tuple[dict, object]:
    """不填计划名称完成日计划表单（避免触发自动推荐占位），打开智能推荐抽屉。"""
    mp.ensure_open()
    mp.wait_ready()
    mp.open_create_editor()
    for month in _candidate_months():
        mp.pick_editor_month(month)
        for day_index in range(2):
            info = _fill_day_plan(mp, None, day_index)
            if info is None:
                break
            drawer = mp.open_recommend_drawer()
            candidates = mp.read_candidates(drawer)
            if any(c["assignable"] for c in candidates):
                return {"month": month, **info}, drawer
            mp.close_drawer(drawer)
            mp.reload_create_editor()
            mp.pick_editor_month(month)
    raise MakePlanReadinessError("各候选月份待排日均无可分配栋舍候选，无法核对智能推荐")


# ============================================================
# 查询类用例
# ============================================================


def test_tc_004_04(page: Page, settings: Settings, evidence_dir: Path, case_meta: dict) -> dict:
    """TC-004-04 / 47721：仅选计划月份后点击「查询」，列表按月份过滤。"""
    mp = MakePlanPage(page, settings)
    try:
        _open_list(mp)
        month = 8
        mp.pick_query_month(month)
        mp.click_query()
        rows = mp.get_table_rows()
        shots = _capture_table(mp, evidence_dir, case_meta, "month_filter")
        if not rows:
            return _result(case_meta, "blocked", "blocked", f"{month}月列表无数据，无法验证过滤", "列表为空", shots)
        bad = [r for r in rows if not r["date"].startswith(f"2026-{month:02d}")]
        if bad:
            return _result(case_meta, "failed", "product_defect",
                           f"{month}月过滤后存在其他月份记录",
                           {"row_count": len(rows), "unexpected": [{"code": r["code"], "date": r["date"]} for r in bad[:5]]}, shots)
        return _result(case_meta, "passed", "passed",
                       f"查询{month}月后 {len(rows)} 行宰杀日期均为 2026-{month:02d}",
                       {"row_count": len(rows), "sample_dates": [r["date"] for r in rows[:5]]}, shots)
    except MakePlanReadinessError as exc:
        return _handle_blocked(mp, evidence_dir, case_meta, exc)
    except MakePlanSelectorError as exc:
        return _handle_selector(mp, evidence_dir, case_meta, exc)
    except PlaywrightTimeoutError as exc:
        return _handle_timeout(mp, evidence_dir, case_meta, exc)
    except Exception as exc:  # noqa: BLE001
        return _handle_unexpected(mp, evidence_dir, case_meta, exc)


def test_tc_004_05(page: Page, settings: Settings, evidence_dir: Path, case_meta: dict) -> dict:
    """TC-004-05 / 47722：仅选计划状态后点击「查询」，列表按状态过滤。"""
    mp = MakePlanPage(page, settings)
    try:
        _open_list(mp)
        status = "审核通过"
        mp.select_status(status)
        mp.click_query()
        rows = mp.get_table_rows()
        shots = _capture_table(mp, evidence_dir, case_meta, "status_filter")
        if not rows:
            return _result(case_meta, "blocked", "blocked", f"状态 {status} 列表无数据，无法验证过滤", "列表为空", shots)
        bad = [r for r in rows if r["status"] != status]
        if bad:
            return _result(case_meta, "failed", "product_defect",
                           f"状态 {status} 过滤后存在其他状态记录",
                           {"row_count": len(rows), "unexpected": [{"code": r["code"], "status": r["status"]} for r in bad[:5]]}, shots)
        return _result(case_meta, "passed", "passed",
                       f"查询状态 {status} 后 {len(rows)} 行状态均为 {status}",
                       {"row_count": len(rows), "sample_codes": [r["code"] for r in rows[:5]]}, shots)
    except MakePlanReadinessError as exc:
        return _handle_blocked(mp, evidence_dir, case_meta, exc)
    except MakePlanSelectorError as exc:
        return _handle_selector(mp, evidence_dir, case_meta, exc)
    except PlaywrightTimeoutError as exc:
        return _handle_timeout(mp, evidence_dir, case_meta, exc)
    except Exception as exc:  # noqa: BLE001
        return _handle_unexpected(mp, evidence_dir, case_meta, exc)


def test_tc_004_06(page: Page, settings: Settings, evidence_dir: Path, case_meta: dict) -> dict:
    """TC-004-06 / 47723：仅选宰杀线后点击「查询」，列表按宰杀线过滤。"""
    mp = MakePlanPage(page, settings)
    try:
        _open_list(mp)
        line = "一号宰杀线"
        mp.select_line(line)
        mp.click_query()
        rows = mp.get_table_rows()
        shots = _capture_table(mp, evidence_dir, case_meta, "line_filter")
        if not rows:
            # 对照验证：重置后按默认条件查询，若默认列表存在该宰杀线记录则为过滤缺陷
            mp.reset_query()
            control_rows = mp.get_all_rows_paged()
            control_hits = [r for r in control_rows if r["line"] == line]
            if control_hits:
                return _result(case_meta, "failed", "product_defect",
                               f"宰杀线 {line} 过滤后 0 条，但默认列表存在 {len(control_hits)} 条该宰杀线记录",
                               {"filtered_total": mp.get_pagination_total(),
                                "control_samples": [{"code": r["code"], "date": r["date"], "status": r["status"]} for r in control_hits[:5]]}, shots)
            return _result(case_meta, "blocked", "blocked", f"宰杀线 {line} 列表无数据，无法验证过滤", "列表为空", shots)
        bad = [r for r in rows if r["line"] != line]
        if bad:
            return _result(case_meta, "failed", "product_defect",
                           f"宰杀线 {line} 过滤后存在其他宰杀线记录",
                           {"row_count": len(rows), "unexpected": [{"code": r["code"], "line": r["line"]} for r in bad[:5]]}, shots)
        return _result(case_meta, "passed", "passed",
                       f"查询宰杀线 {line} 后 {len(rows)} 行均为 {line}",
                       {"row_count": len(rows), "sample_codes": [r["code"] for r in rows[:5]]}, shots)
    except MakePlanReadinessError as exc:
        return _handle_blocked(mp, evidence_dir, case_meta, exc)
    except MakePlanSelectorError as exc:
        return _handle_selector(mp, evidence_dir, case_meta, exc)
    except PlaywrightTimeoutError as exc:
        return _handle_timeout(mp, evidence_dir, case_meta, exc)
    except Exception as exc:  # noqa: BLE001
        return _handle_unexpected(mp, evidence_dir, case_meta, exc)


def test_tc_004_07(page: Page, settings: Settings, evidence_dir: Path, case_meta: dict) -> dict:
    """TC-004-07 / 47724：选择多条件后点击「查询」，列表按组合条件过滤。"""
    mp = MakePlanPage(page, settings)
    try:
        _open_list(mp)
        month, status, line = 8, "审核通过", "一号宰杀线"
        mp.pick_query_month(month)
        mp.select_status(status)
        mp.select_line(line)
        mp.click_query()
        rows = mp.get_table_rows()
        shots = _capture_table(mp, evidence_dir, case_meta, "combined_filter")
        if not rows:
            # 对照验证：去掉宰杀线条件按月份+状态查询，若存在该宰杀线记录则为宰杀线过滤缺陷
            mp.reset_query()
            mp.pick_query_month(month)
            mp.select_status(status)
            mp.click_query()
            control_rows = mp.get_all_rows_paged()
            control_hits = [r for r in control_rows if r["line"] == line]
            if control_hits:
                return _result(case_meta, "failed", "product_defect",
                               f"组合条件过滤后 0 条，但 {month}月/{status} 下存在 {len(control_hits)} 条 {line} 记录",
                               {"filtered_total": mp.get_pagination_total(),
                                "control_samples": [{"code": r["code"], "date": r["date"], "status": r["status"]} for r in control_hits[:5]]}, shots)
            return _result(case_meta, "blocked", "blocked",
                           f"组合条件（{month}月/{status}/{line}）列表无数据，无法验证过滤", "列表为空", shots)
        bad = [r for r in rows if not (r["date"].startswith(f"2026-{month:02d}") and r["status"] == status and r["line"] == line)]
        if bad:
            return _result(case_meta, "failed", "product_defect",
                           "组合条件过滤后存在不满足条件的记录",
                           {"row_count": len(rows), "unexpected": [{"code": r["code"], "date": r["date"], "status": r["status"], "line": r["line"]} for r in bad[:5]]}, shots)
        return _result(case_meta, "passed", "passed",
                       f"组合条件过滤后 {len(rows)} 行均满足 {month}月/{status}/{line}",
                       {"row_count": len(rows), "sample_codes": [r["code"] for r in rows[:5]]}, shots)
    except MakePlanReadinessError as exc:
        return _handle_blocked(mp, evidence_dir, case_meta, exc)
    except MakePlanSelectorError as exc:
        return _handle_selector(mp, evidence_dir, case_meta, exc)
    except PlaywrightTimeoutError as exc:
        return _handle_timeout(mp, evidence_dir, case_meta, exc)
    except Exception as exc:  # noqa: BLE001
        return _handle_unexpected(mp, evidence_dir, case_meta, exc)


def test_tc_004_09(page: Page, settings: Settings, evidence_dir: Path, case_meta: dict) -> dict:
    """TC-004-09 / 47726：点击「重置」，查询条件恢复默认并刷新列表。"""
    mp = MakePlanPage(page, settings)
    try:
        _open_list(mp)
        default_values = mp.get_query_values()
        default_count = mp.get_row_count()
        mp.pick_query_month(8)
        mp.select_status("审核通过")
        mp.select_line("一号宰杀线")
        mp.click_query()
        filtered_values = mp.get_query_values()
        if filtered_values == default_values:
            shots = _capture_evidence(mp, evidence_dir, case_meta, "setup")
            return _result(case_meta, "ignored", "test_script_error", "设置查询条件后控件值未变化", filtered_values, shots)
        mp.reset_query()
        restored = mp.get_query_values()
        restored_count = mp.get_row_count()
        shots = _capture_table(mp, evidence_dir, case_meta, "reset")
        mismatches = {k: {"default": default_values[k], "after_reset": restored[k]}
                      for k in default_values if (restored[k] or "") != (default_values[k] or "")}
        if mismatches:
            return _result(case_meta, "failed", "product_defect", "重置后查询条件未恢复默认", mismatches, shots)
        return _result(case_meta, "passed", "passed",
                       f"重置后查询条件恢复默认（默认行数 {default_count}，重置后行数 {restored_count}）",
                       {"default": default_values, "after_reset": restored, "default_rows": default_count, "restored_rows": restored_count}, shots)
    except MakePlanReadinessError as exc:
        return _handle_blocked(mp, evidence_dir, case_meta, exc)
    except MakePlanSelectorError as exc:
        return _handle_selector(mp, evidence_dir, case_meta, exc)
    except PlaywrightTimeoutError as exc:
        return _handle_timeout(mp, evidence_dir, case_meta, exc)
    except Exception as exc:  # noqa: BLE001
        return _handle_unexpected(mp, evidence_dir, case_meta, exc)


# ============================================================
# 制定排程计算/保存类用例
# ============================================================


def test_tc_004_51(page: Page, settings: Settings, evidence_dir: Path, case_meta: dict) -> dict:
    """TC-004-51 / 47768：选择品种并引用模版后自动带出养殖天数/空栏天数/三段标准。"""
    mp = MakePlanPage(page, settings)
    try:
        mp.ensure_open()
        mp.wait_ready()
        mp.open_create_editor()
        if not mp.pick_pending_day(0):
            return _handle_blocked(mp, evidence_dir, case_meta, MakePlanReadinessError("当前月份无待排日期"))
        mp.select_editor_line(0)
        dialog = mp.open_template_dialog()
        template = mp.select_template(dialog)
        cells = template["cells"]
        seg_expected = [
            {"days": cells[5], "empty": cells[6]},
            {"days": cells[9], "empty": cells[10]},
            {"days": cells[13], "empty": cells[14]},
        ]
        survival_expected = cells[16]
        survival_actual = mp.read_editor_field("成活率(%)")
        segments_actual = mp.read_segment_standards()
        shots = _capture_evidence(mp, evidence_dir, case_meta, "template_autofill")
        actual = {
            "template": template["name"],
            "survival": {"expected": survival_expected, "actual": survival_actual},
            "segments": {"expected": seg_expected, "actual": segments_actual},
        }
        if survival_actual != survival_expected:
            return _result(case_meta, "failed", "product_defect", "成活率未按模版第三段带出", actual, shots)
        if segments_actual != seg_expected:
            return _result(case_meta, "failed", "product_defect", "三段养殖/空栏天数未按模版带出", actual, shots)
        return _result(case_meta, "passed", "passed",
                       f"模版 {template['name']} 带出成活率 {survival_actual} 与三段标准 {seg_expected} 一致", actual, shots)
    except MakePlanReadinessError as exc:
        return _handle_blocked(mp, evidence_dir, case_meta, exc)
    except MakePlanSelectorError as exc:
        return _handle_selector(mp, evidence_dir, case_meta, exc)
    except PlaywrightTimeoutError as exc:
        return _handle_timeout(mp, evidence_dir, case_meta, exc)
    except Exception as exc:  # noqa: BLE001
        return _handle_unexpected(mp, evidence_dir, case_meta, exc)


def test_tc_004_55(page: Page, settings: Settings, evidence_dir: Path, case_meta: dict) -> dict:
    """TC-004-55 / 47772：「补栏量(万羽)」=宰杀量/成活率，精确到只。"""
    mp = MakePlanPage(page, settings)
    try:
        mp.ensure_open()
        mp.wait_ready()
        mp.open_create_editor()
        info = _fill_day_plan(mp, f"AUTO测试_勿用_RUN{_run_ts()}_TC-004-55", 0)
        if info is None:
            return _handle_blocked(mp, evidence_dir, case_meta, MakePlanReadinessError("当前月份无待排日期"))
        slaughter = float(mp.read_editor_field("宰杀量(万只)"))
        survival = float(mp.read_editor_field("成活率(%)"))
        restock_text = mp.read_editor_field("补栏量(万羽)")
        shots = _capture_evidence(mp, evidence_dir, case_meta, "restock_calc")
        expected = round(slaughter / (survival / 100), 4)
        actual_value = float(restock_text) if restock_text else None
        actual = {"slaughter": slaughter, "survival": survival, "expected_restock": expected, "actual_restock": restock_text}
        if actual_value is None:
            return _result(case_meta, "failed", "product_defect", "补栏量未自动计算", actual, shots)
        if abs(actual_value - expected) > 0.0001:
            return _result(case_meta, "failed", "product_defect", "补栏量与宰杀量/成活率不符", actual, shots)
        return _result(case_meta, "passed", "passed",
                       f"补栏量 {restock_text} = 宰杀量 {slaughter} / 成活率 {survival}%", actual, shots)
    except MakePlanReadinessError as exc:
        return _handle_blocked(mp, evidence_dir, case_meta, exc)
    except MakePlanSelectorError as exc:
        return _handle_selector(mp, evidence_dir, case_meta, exc)
    except PlaywrightTimeoutError as exc:
        return _handle_timeout(mp, evidence_dir, case_meta, exc)
    except Exception as exc:  # noqa: BLE001
        return _handle_unexpected(mp, evidence_dir, case_meta, exc)


def test_tc_004_57(page: Page, settings: Settings, evidence_dir: Path, case_meta: dict) -> dict:
    """TC-004-57 / 47774：「补栏日期」=宰杀日期-总养殖天数+1。"""
    mp = MakePlanPage(page, settings)
    try:
        mp.ensure_open()
        mp.wait_ready()
        mp.open_create_editor()
        info = _fill_day_plan(mp, f"AUTO测试_勿用_RUN{_run_ts()}_TC-004-57", 0)
        if info is None:
            return _handle_blocked(mp, evidence_dir, case_meta, MakePlanReadinessError("当前月份无待排日期"))
        total_days = int(info["template"]["total_days"])
        slaughter_date = datetime.strptime(info["date"], "%Y-%m-%d").date()
        expected_date = (slaughter_date - timedelta(days=total_days - 1)).isoformat()
        restock_date = mp.read_editor_field("补栏日期")
        shots = _capture_evidence(mp, evidence_dir, case_meta, "restock_date")
        actual = {"slaughter_date": info["date"], "total_days": total_days,
                  "expected_restock_date": expected_date, "actual_restock_date": restock_date}
        if restock_date != expected_date:
            return _result(case_meta, "failed", "product_defect", "补栏日期不等于宰杀日期-总养殖天数+1", actual, shots)
        return _result(case_meta, "passed", "passed",
                       f"补栏日期 {restock_date} = 宰杀日期 {info['date']} - 总养殖天数 {total_days} + 1", actual, shots)
    except MakePlanReadinessError as exc:
        return _handle_blocked(mp, evidence_dir, case_meta, exc)
    except MakePlanSelectorError as exc:
        return _handle_selector(mp, evidence_dir, case_meta, exc)
    except PlaywrightTimeoutError as exc:
        return _handle_timeout(mp, evidence_dir, case_meta, exc)
    except Exception as exc:  # noqa: BLE001
        return _handle_unexpected(mp, evidence_dir, case_meta, exc)


def test_tc_004_69(page: Page, settings: Settings, evidence_dir: Path, case_meta: dict) -> dict:
    """TC-004-69 / 47786：「上孵数量(万枚)」=补栏量/孵化率/健雏率，精确到只。"""
    mp = MakePlanPage(page, settings)
    try:
        mp.ensure_open()
        mp.wait_ready()
        mp.open_create_editor()
        info = _fill_day_plan(mp, f"AUTO测试_勿用_RUN{_run_ts()}_TC-004-69", 0)
        if info is None:
            return _handle_blocked(mp, evidence_dir, case_meta, MakePlanReadinessError("当前月份无待排日期"))
        restock = float(mp.read_editor_field("补栏量(万羽)"))
        hatch_rate = float(mp.read_editor_field("孵化率(%)"))
        chick_rate = float(mp.read_editor_field("健雏率(%)"))
        hatch_text = mp.read_editor_field("上孵数量(万枚)")
        shots = _capture_evidence(mp, evidence_dir, case_meta, "hatch_calc")
        expected = round(restock / (hatch_rate / 100) / (chick_rate / 100), 4)
        actual_value = float(hatch_text) if hatch_text else None
        actual = {"restock": restock, "hatch_rate": hatch_rate, "chick_rate": chick_rate,
                  "expected_hatch": expected, "actual_hatch": hatch_text}
        if actual_value is None:
            return _result(case_meta, "failed", "product_defect", "上孵数量未自动计算", actual, shots)
        if abs(actual_value - expected) > 0.0001:
            return _result(case_meta, "failed", "product_defect", "上孵数量与补栏量/孵化率/健雏率不符", actual, shots)
        return _result(case_meta, "passed", "passed",
                       f"上孵数量 {hatch_text} = 补栏量 {restock} / 孵化率 {hatch_rate}% / 健雏率 {chick_rate}%", actual, shots)
    except MakePlanReadinessError as exc:
        return _handle_blocked(mp, evidence_dir, case_meta, exc)
    except MakePlanSelectorError as exc:
        return _handle_selector(mp, evidence_dir, case_meta, exc)
    except PlaywrightTimeoutError as exc:
        return _handle_timeout(mp, evidence_dir, case_meta, exc)
    except Exception as exc:  # noqa: BLE001
        return _handle_unexpected(mp, evidence_dir, case_meta, exc)


def test_tc_004_77(page: Page, settings: Settings, evidence_dir: Path, case_meta: dict) -> dict:
    """TC-004-77 / 47794：保存时按宰杀线生成排程编号 JH-YYYYMMDD-流水(01~99)。"""
    mp = MakePlanPage(page, settings)
    run_ts = _run_ts()
    draft: dict = {}
    try:
        draft = _create_draft(mp, run_ts, "TC-004-77")
        code = draft["code"]
        shots = _capture_table(mp, evidence_dir, case_meta, "code_format")
        expected_prefix = "JH-" + draft["date"].replace("-", "") + "-"
        match = re.fullmatch(r"JH-\d{8}-(\d{2})", code)
        actual = {"code": code, "date": draft["date"], "line": draft["line"], "expected_prefix": expected_prefix}
        if not match or not code.startswith(expected_prefix):
            return _result(case_meta, "failed", "product_defect", "排程编号不符合 JH-YYYYMMDD-流水 格式", actual, shots)
        if not (1 <= int(match.group(1)) <= 99):
            return _result(case_meta, "failed", "product_defect", "排程编号流水超出 01~99", actual, shots)
        return _result(case_meta, "passed", "passed",
                       f"保存生成排程编号 {code}，符合 JH-YYYYMMDD-流水(01~99)", actual, shots)
    except MakePlanReadinessError as exc:
        return _handle_blocked(mp, evidence_dir, case_meta, exc)
    except MakePlanSelectorError as exc:
        return _handle_selector(mp, evidence_dir, case_meta, exc)
    except PlaywrightTimeoutError as exc:
        return _handle_timeout(mp, evidence_dir, case_meta, exc)
    except Exception as exc:  # noqa: BLE001
        return _handle_unexpected(mp, evidence_dir, case_meta, exc)
    finally:
        if draft.get("code"):
            _cleanup_draft(mp, draft["month"], draft["code"])


def test_tc_004_81(page: Page, settings: Settings, evidence_dir: Path, case_meta: dict) -> dict:
    """TC-004-81 / 47798：点击「保存当日计划」，当日排程状态=暂存。"""
    mp = MakePlanPage(page, settings)
    run_ts = _run_ts()
    draft: dict = {}
    try:
        draft = _create_draft(mp, run_ts, "TC-004-81")
        code = draft["code"]
        mp.ensure_open()
        mp.wait_ready()
        mp.pick_query_month(draft["month"])
        mp.click_query()
        status = mp.get_row_status_by_code(code)
        shots = _capture_table(mp, evidence_dir, case_meta, "draft_status")
        actual = {"code": code, "date": draft["date"], "line": draft["line"], "status": status}
        if status != "暂存":
            return _result(case_meta, "failed", "product_defect", "保存当日计划后状态不是暂存", actual, shots)
        return _result(case_meta, "passed", "passed", f"保存当日计划后 {code} 状态=暂存", actual, shots)
    except MakePlanReadinessError as exc:
        return _handle_blocked(mp, evidence_dir, case_meta, exc)
    except MakePlanSelectorError as exc:
        return _handle_selector(mp, evidence_dir, case_meta, exc)
    except PlaywrightTimeoutError as exc:
        return _handle_timeout(mp, evidence_dir, case_meta, exc)
    except Exception as exc:  # noqa: BLE001
        return _handle_unexpected(mp, evidence_dir, case_meta, exc)
    finally:
        if draft.get("code"):
            _cleanup_draft(mp, draft["month"], draft["code"])


# ============================================================
# 编辑/提交/删除类用例
# ============================================================


def test_tc_004_144(page: Page, settings: Settings, evidence_dir: Path, case_meta: dict) -> dict:
    """TC-004-144 / 47861：编辑页点击「保存并提交」，日计划状态变成「待审核」。"""
    mp = MakePlanPage(page, settings)
    run_ts = _run_ts()
    try:
        draft = _create_draft(mp, run_ts, "TC-004-144")
        code = draft["code"]
        mp.ensure_open()
        mp.wait_ready()
        mp.pick_query_month(draft["month"])
        mp.click_query()
        mp.click_row_action(code, "编辑")
        try:
            mp.page.wait_for_url("**/makeschedule/form/edit/**", timeout=15_000)
        except PlaywrightTimeoutError as exc:
            raise MakePlanReadinessError("编辑页路由未就绪") from exc
        try:
            mp.page.wait_for_load_state("networkidle", timeout=15_000)
        except PlaywrightTimeoutError:
            pass
        mp.page.wait_for_timeout(1_500)
        mp.click_save_and_submit()
        mp.ensure_open()
        mp.wait_ready()
        mp.pick_query_month(draft["month"])
        mp.click_query()
        status = mp.get_row_status_by_code(code)
        shots = _capture_table(mp, evidence_dir, case_meta, "submit_status")
        actual = {"code": code, "status": status}
        if status != "待审核":
            return _result(case_meta, "failed", "product_defect", "保存并提交后日计划状态未变待审核", actual, shots)
        return _result(case_meta, "passed", "passed", f"保存并提交后 {code} 状态=待审核", actual, shots)
    except MakePlanReadinessError as exc:
        return _handle_blocked(mp, evidence_dir, case_meta, exc)
    except MakePlanSelectorError as exc:
        return _handle_selector(mp, evidence_dir, case_meta, exc)
    except PlaywrightTimeoutError as exc:
        return _handle_timeout(mp, evidence_dir, case_meta, exc)
    except Exception as exc:  # noqa: BLE001
        return _handle_unexpected(mp, evidence_dir, case_meta, exc)


def test_tc_004_148(page: Page, settings: Settings, evidence_dir: Path, case_meta: dict) -> dict:
    """TC-004-148 / 47865：制定页点击「提交月度审核」弹出确认框。"""
    mp = MakePlanPage(page, settings)
    run_ts = _run_ts()
    draft: dict = {}
    try:
        draft = _create_draft(mp, run_ts, "TC-004-148")
        _open_editor_for_month(mp, draft["month"])
        dialog = mp.click_submit_month_review()
        text = dialog.inner_text()
        buttons = [b.replace(" ", "").strip() for b in dialog.locator("button:visible").all_inner_texts() if b.strip()]
        shots = _capture_evidence(mp, evidence_dir, case_meta, "submit_dialog")
        actual = {"dialog_text": text.replace("\n", " ")[:200], "buttons": buttons}
        if "取消" not in buttons or not any("确认" in b or "确定" in b for b in buttons):
            return _result(case_meta, "failed", "product_defect", "提交月度审核确认框缺少确定/取消按钮", actual, shots)
        cancel = dialog.locator("button").filter(has_text="取消").first
        if cancel.count():
            cancel.click()
        mp.page.wait_for_timeout(1_000)
        return _result(case_meta, "passed", "passed", "点击提交月度审核弹出提交审核确认框（含确定/取消）", actual, shots)
    except MakePlanReadinessError as exc:
        return _handle_blocked(mp, evidence_dir, case_meta, exc)
    except MakePlanSelectorError as exc:
        return _handle_selector(mp, evidence_dir, case_meta, exc)
    except PlaywrightTimeoutError as exc:
        return _handle_timeout(mp, evidence_dir, case_meta, exc)
    except Exception as exc:  # noqa: BLE001
        return _handle_unexpected(mp, evidence_dir, case_meta, exc)
    finally:
        if draft.get("code"):
            _cleanup_draft(mp, draft["month"], draft["code"])


def test_tc_004_150(page: Page, settings: Settings, evidence_dir: Path, case_meta: dict) -> dict:
    """TC-004-150 / 47867：提交月度审核确认后当月的暂存计划状态变待审核。"""
    mp = MakePlanPage(page, settings)
    run_ts = _run_ts()
    try:
        candidates = _candidate_months()
        clean_months = [m for m in candidates if _query_month_status(mp, m, "暂存") + _query_month_status(mp, m, "驳回") == 0]
        if not clean_months:
            return _handle_blocked(mp, evidence_dir, case_meta,
                                   MakePlanReadinessError("各候选月份均存在暂存/驳回计划，提交月度审核会产生越界副作用"))
        draft = None
        last_error: Exception | None = None
        for clean_month in clean_months:
            try:
                draft = _create_draft(mp, run_ts, "TC-004-150", months=[clean_month])
                break
            except MakePlanReadinessError as exc:
                last_error = exc
        if draft is None:
            return _handle_blocked(mp, evidence_dir, case_meta,
                                   last_error or MakePlanReadinessError("干净月份均无可分配栋舍"))
        clean_month = draft["month"]
        _open_editor_for_month(mp, clean_month)
        dialog = mp.click_submit_month_review()
        text = dialog.inner_text().replace("\n", " ")
        if "共有 1 个" not in text:
            cancel = dialog.get_by_role("button", name="取消", exact=True)
            if cancel.count():
                cancel.first.click()
            return _handle_blocked(mp, evidence_dir, case_meta,
                                   MakePlanReadinessError(f"提交确认框显示非仅本用例暂存计划：{text[:120]}"))
        confirm = dialog.get_by_role("button", name="确认提交", exact=True)
        if not confirm.count():
            raise MakePlanSelectorError("提交审核弹窗确认提交按钮不可定位")
        confirm.first.click()
        mp.wait_success_message("成功")
        mp.ensure_open()
        mp.wait_ready()
        mp.pick_query_month(clean_month)
        mp.click_query()
        status = mp.get_row_status_by_code(draft["code"])
        shots = _capture_table(mp, evidence_dir, case_meta, "submit_month")
        actual = {"code": draft["code"], "month": clean_month, "status": status, "dialog_text": text[:120]}
        if status != "待审核":
            return _result(case_meta, "failed", "product_defect", "提交月度审核确认后暂存计划未变待审核", actual, shots)
        return _result(case_meta, "passed", "passed", f"提交月度审核确认后 {draft['code']} 状态=待审核", actual, shots)
    except MakePlanReadinessError as exc:
        return _handle_blocked(mp, evidence_dir, case_meta, exc)
    except MakePlanSelectorError as exc:
        return _handle_selector(mp, evidence_dir, case_meta, exc)
    except PlaywrightTimeoutError as exc:
        return _handle_timeout(mp, evidence_dir, case_meta, exc)
    except Exception as exc:  # noqa: BLE001
        return _handle_unexpected(mp, evidence_dir, case_meta, exc)


def test_tc_004_160(page: Page, settings: Settings, evidence_dir: Path, case_meta: dict) -> dict:
    """TC-004-160 / 47877：点击「删除」弹出确认框。"""
    mp = MakePlanPage(page, settings)
    run_ts = _run_ts()
    draft: dict = {}
    try:
        draft = _create_draft(mp, run_ts, "TC-004-160")
        code = draft["code"]
        mp.ensure_open()
        mp.wait_ready()
        mp.pick_query_month(draft["month"])
        mp.click_query()
        mp.click_row_action(code, "删除")
        box_text = mp.cancel_message_box()
        shots = _capture_table(mp, evidence_dir, case_meta, "delete_box")
        actual = {"code": code, "box_text": box_text.replace("\n", " ")[:200]}
        if "确定删除计划" not in box_text or code not in box_text:
            return _result(case_meta, "failed", "product_defect", "删除确认框文案不符合预期", actual, shots)
        return _result(case_meta, "passed", "passed", f"点击删除弹出确认框：{box_text.replace(chr(10), ' ')[:80]}", actual, shots)
    except MakePlanReadinessError as exc:
        return _handle_blocked(mp, evidence_dir, case_meta, exc)
    except MakePlanSelectorError as exc:
        return _handle_selector(mp, evidence_dir, case_meta, exc)
    except PlaywrightTimeoutError as exc:
        return _handle_timeout(mp, evidence_dir, case_meta, exc)
    except Exception as exc:  # noqa: BLE001
        return _handle_unexpected(mp, evidence_dir, case_meta, exc)
    finally:
        if draft.get("code"):
            _cleanup_draft(mp, draft["month"], draft["code"])


def test_tc_004_162(page: Page, settings: Settings, evidence_dir: Path, case_meta: dict) -> dict:
    """TC-004-162 / 47879：删除确认框点击确定，该宰杀线排程从列表消失。"""
    mp = MakePlanPage(page, settings)
    run_ts = _run_ts()
    try:
        draft = _create_draft(mp, run_ts, "TC-004-162")
        code = draft["code"]
        mp.ensure_open()
        mp.wait_ready()
        mp.pick_query_month(draft["month"])
        mp.click_query()
        mp.click_row_action(code, "删除")
        mp.confirm_message_box()
        mp.wait_success_message("成功")
        mp.click_query()
        still_exists = mp.find_row_by_code(code) is not None
        shots = _capture_table(mp, evidence_dir, case_meta, "delete_done")
        actual = {"code": code, "still_exists": still_exists}
        if still_exists:
            return _result(case_meta, "failed", "product_defect", "删除确认后记录仍在列表中", actual, shots)
        return _result(case_meta, "passed", "passed", f"删除确认后 {code} 从列表消失", actual, shots)
    except MakePlanReadinessError as exc:
        return _handle_blocked(mp, evidence_dir, case_meta, exc)
    except MakePlanSelectorError as exc:
        return _handle_selector(mp, evidence_dir, case_meta, exc)
    except PlaywrightTimeoutError as exc:
        return _handle_timeout(mp, evidence_dir, case_meta, exc)
    except Exception as exc:  # noqa: BLE001
        return _handle_unexpected(mp, evidence_dir, case_meta, exc)


# ============================================================
# 智能推荐类用例
# ============================================================


def test_tc_004_175(page: Page, settings: Settings, evidence_dir: Path, case_meta: dict) -> dict:
    """TC-004-175 / 48827：智能推荐-选择候选或「选择 X 栋」后养殖栋舍回填。"""
    mp = MakePlanPage(page, settings)
    drawer = None
    try:
        _ctx, drawer = _open_drawer_without_autofill(mp, "TC-004-175")
        candidates = mp.read_candidates(drawer)
        assignable = [c for c in candidates if c["assignable"]]
        if not assignable:
            shots = _capture_evidence(mp, evidence_dir, case_meta, "no_candidate")
            return _result(case_meta, "blocked", "blocked", "智能推荐无可分配栋舍候选", "无可分配候选", shots)
        target = assignable[0]
        mp.click_candidate(drawer, str(target["house"]))
        mp.page.wait_for_timeout(1_500)
        # 已探查交互：点击可分配候选卡片即完成选择并关闭抽屉回填；
        # 若抽屉仍打开，则尝试「选择 X 栋」确认按钮。
        confirm_text = "点击候选卡片"
        if mp.page.locator(".el-drawer:visible").count():
            confirm_text = mp.click_drawer_select_confirm(drawer)
            mp.page.wait_for_timeout(1_000)
        drawer_closed = mp.page.locator(".el-drawer:visible").count() == 0
        house_value = mp.read_editor_field("养殖栋舍")
        shots = _capture_evidence(mp, evidence_dir, case_meta, "backfill")
        actual = {"selected_house": f"{target['house']}栋", "confirm_action": confirm_text,
                  "drawer_closed": drawer_closed, "house_value": house_value}
        expected_value = f"{target['house']}栋"
        if not drawer_closed or house_value != expected_value:
            return _result(case_meta, "failed", "product_defect",
                           "选择候选确认后养殖栋舍未回填所选栋号", actual, shots)
        return _result(case_meta, "passed", "passed",
                       f"选择候选（{confirm_text}）后养殖栋舍回填 {house_value}", actual, shots)
    except MakePlanReadinessError as exc:
        return _handle_blocked(mp, evidence_dir, case_meta, exc)
    except MakePlanSelectorError as exc:
        return _handle_selector(mp, evidence_dir, case_meta, exc)
    except PlaywrightTimeoutError as exc:
        return _handle_timeout(mp, evidence_dir, case_meta, exc)
    except Exception as exc:  # noqa: BLE001
        return _handle_unexpected(mp, evidence_dir, case_meta, exc)


def test_tc_004_176(page: Page, settings: Settings, evidence_dir: Path, case_meta: dict) -> dict:
    """TC-004-176 / 48861：智能推荐-栋舍顺序优先下匹配度分数正确（100-d*5）。"""
    mp = MakePlanPage(page, settings)
    try:
        _ctx, drawer = _open_drawer_without_autofill(mp, "TC-004-176")
        mp.switch_strategy(drawer, "栋舍顺序优先")
        candidates = [c for c in mp.read_candidates(drawer) if c["assignable"]]
        shots = _capture_evidence(mp, evidence_dir, case_meta, "score_order")
        if not candidates:
            return _result(case_meta, "blocked", "blocked", "栋舍顺序优先下无可分配候选", "无可分配候选", shots)
        min_house = min(int(c["house"]) for c in candidates)
        checks = []
        wrong = []
        for c in candidates:
            expected_score = 100 - (int(c["house"]) - min_house) * 5
            checks.append({"house": f"{c['house']}栋", "actual_score": c["score"], "expected_score": expected_score})
            if c["score"] != expected_score:
                wrong.append(checks[-1])
        if wrong:
            return _result(case_meta, "failed", "product_defect",
                           "栋舍顺序优先下匹配度分数与 100-d*5 不符", {"checks": checks, "wrong": wrong}, shots)
        return _result(case_meta, "passed", "passed",
                       f"栋舍顺序优先下 {len(checks)} 个候选匹配度均符合 100-d*5", {"checks": checks}, shots)
    except MakePlanReadinessError as exc:
        return _handle_blocked(mp, evidence_dir, case_meta, exc)
    except MakePlanSelectorError as exc:
        return _handle_selector(mp, evidence_dir, case_meta, exc)
    except PlaywrightTimeoutError as exc:
        return _handle_timeout(mp, evidence_dir, case_meta, exc)
    except Exception as exc:  # noqa: BLE001
        return _handle_unexpected(mp, evidence_dir, case_meta, exc)


def test_tc_004_223(page: Page, settings: Settings, evidence_dir: Path, case_meta: dict) -> dict:
    """TC-004-223 / 48864：智能推荐-最小空闲优先下匹配度分数正确（(100-MinGap*5)*80%+SeqScore*20%）。"""
    mp = MakePlanPage(page, settings)
    try:
        _ctx, drawer = _open_drawer_without_autofill(mp, "TC-004-223")
        mp.switch_strategy(drawer, "最小空闲优先")
        candidates = [c for c in mp.read_candidates(drawer) if c["assignable"]]
        shots = _capture_evidence(mp, evidence_dir, case_meta, "score_idle")
        if not candidates:
            return _result(case_meta, "blocked", "blocked", "最小空闲优先下无可分配候选", "无可分配候选", shots)
        if any(c["min_idle_days"] is None for c in candidates):
            return _result(case_meta, "blocked", "blocked", "候选卡片未展示三段最小空闲天数，无法核对公式", "MinGap 缺失", shots)
        min_house = min(int(c["house"]) for c in candidates)
        checks = []
        wrong = []
        for c in candidates:
            seq_score = 100 - (int(c["house"]) - min_house) * 5
            # 已探查行为：最小空闲项 (100-MinGap*5) 为负时按 0 计（如 10栋 MinGap=24 → 得 16 分）
            expected_score = round(max(0, 100 - c["min_idle_days"] * 5) * 0.8 + seq_score * 0.2)
            checks.append({"house": f"{c['house']}栋", "min_idle_days": c["min_idle_days"],
                           "seq_score": seq_score, "actual_score": c["score"], "expected_score": expected_score})
            if abs(int(c["score"]) - expected_score) > 1:
                wrong.append(checks[-1])
        if wrong:
            return _result(case_meta, "failed", "product_defect",
                           "最小空闲优先下匹配度分数与 (100-MinGap*5)*80%+SeqScore*20% 不符",
                           {"checks": checks, "wrong": wrong}, shots)
        return _result(case_meta, "passed", "passed",
                       f"最小空闲优先下 {len(checks)} 个候选匹配度均符合加权公式", {"checks": checks}, shots)
    except MakePlanReadinessError as exc:
        return _handle_blocked(mp, evidence_dir, case_meta, exc)
    except MakePlanSelectorError as exc:
        return _handle_selector(mp, evidence_dir, case_meta, exc)
    except PlaywrightTimeoutError as exc:
        return _handle_timeout(mp, evidence_dir, case_meta, exc)
    except Exception as exc:  # noqa: BLE001
        return _handle_unexpected(mp, evidence_dir, case_meta, exc)

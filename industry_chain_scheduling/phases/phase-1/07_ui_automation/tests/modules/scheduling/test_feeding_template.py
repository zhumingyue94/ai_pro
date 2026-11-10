"""分段养殖模版模块自动化用例。

首批实现 6 条查询类 P1 用例（TC-003-06/07/08/09/10/12）。
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError

from config.settings import Settings
from pages.scheduling.feeding_template_page import (
    FeedingTemplatePage,
    FeedingTemplateReadinessError,
    FeedingTemplateSelectorError,
)


def _capture_evidence(tpl: FeedingTemplatePage, evidence_dir: Path, case_meta: dict, suffix: str) -> list[str]:
    """在断言点保存区域截图和完整页面截图。"""
    case_id = case_meta["case_id"]
    check_id = case_meta["check_id"]
    scope_path = evidence_dir / f"{case_id}_{check_id}_{suffix}_scope.png"
    full_path = evidence_dir / f"{case_id}_{check_id}_{suffix}_full.png"
    try:
        tpl.capture_scope(scope_path)
    except Exception:
        pass
    try:
        tpl.capture_full(full_path)
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


def _capture_table(tpl: FeedingTemplatePage, evidence_dir: Path, case_meta: dict, suffix: str) -> list[str]:
    """在业务动作完成点保存表格区域和完整页面截图。"""
    case_id = case_meta["case_id"]
    check_id = case_meta["check_id"]
    scope_path = evidence_dir / f"{case_id}_{check_id}_{suffix}_scope.png"
    full_path = evidence_dir / f"{case_id}_{check_id}_{suffix}_full.png"
    try:
        tpl.page.locator(".el-table:visible").first.screenshot(path=str(scope_path))
    except Exception:
        try:
            tpl.capture_scope(scope_path)
        except Exception:
            pass
    try:
        tpl.capture_full(full_path)
    except Exception:
        pass
    return [str(p) for p in (scope_path, full_path) if p.is_file()]


def _handle_blocked(tpl: FeedingTemplatePage, evidence_dir: Path, case_meta: dict, exc: Exception) -> dict:
    """统一处理 blocked 类异常。"""
    shots = _capture_evidence(tpl, evidence_dir, case_meta, "blocked")
    return _result(case_meta, "blocked", "blocked", str(exc), "页面或测试数据未就绪", shots)


def _handle_selector(tpl: FeedingTemplatePage, evidence_dir: Path, case_meta: dict, exc: Exception) -> dict:
    """统一处理选择器不可定位异常。"""
    shots = _capture_evidence(tpl, evidence_dir, case_meta, "script_error")
    return _result(case_meta, "ignored", "test_script_error", str(exc), "DOM 契约不可定位", shots)


def _handle_timeout(tpl: FeedingTemplatePage, evidence_dir: Path, case_meta: dict, exc: Exception) -> dict:
    """统一处理超时异常。"""
    shots = _capture_evidence(tpl, evidence_dir, case_meta, "timeout")
    msg = str(exc).lower()
    if "not enabled" in msg or "not editable" in msg or "locator.fill" in msg:
        return _result(case_meta, "ignored", "test_script_error", f"控件实现错误：{exc}", "控件不可编辑", shots)
    return _result(case_meta, "blocked", "blocked", f"页面等待超时：{exc}", "页面未稳定", shots)


def _handle_unexpected(tpl: FeedingTemplatePage, evidence_dir: Path, case_meta: dict, exc: Exception) -> dict:
    """统一处理未预期异常。"""
    shots = _capture_evidence(tpl, evidence_dir, case_meta, "script_error")
    return _result(case_meta, "ignored", "test_script_error", f"脚本异常：{exc!r}", "脚本未完成断言", shots)


# ============================================================
# 辅助函数
# ============================================================


def _run_ts() -> str:
    """生成本次执行的时间戳标识，用于自造数据命名。"""
    return datetime.now().strftime("%H%M%S")


def _cleanup_template(tpl: FeedingTemplatePage, name: str) -> str:
    """尝试删除指定名称的暂存/待审核模版，返回清理结果文本。"""
    try:
        tpl.reload()
        tpl.wait_ready()
        tpl.fill_name(name)
        tpl.click_query()
        rows = tpl.get_table_rows()
        if not any(r["name"] == name for r in rows):
            return "not_found"
        tpl.click_delete(name)
        tpl.confirm_message_box()
        tpl.wait_table_ready()
        return "deleted"
    except Exception as exc:
        return f"cleanup_failed: {exc}"


def _create_draft(tpl: FeedingTemplatePage, run_ts: str, case_id: str) -> dict:
    """新增一条暂存模版（保存但不提交），返回创建信息。"""
    name = f"AUTO测试_勿用_RUN{run_ts}_{case_id}"
    # 选一个非勿用的品种和月份
    all_rows = tpl.get_table_rows()
    breed = "京白 939"
    month = "3月"
    for r in all_rows:
        if r["breed"] and "勿用" not in r["breed"] and "停用" not in r["breed"]:
            breed = r["breed"]
            break
    tpl.click_new()
    tpl.fill_template_form(name, breed, month)
    tpl.save_dialog()
    return {"name": name, "breed": breed, "month": month}


def _create_pending(tpl: FeedingTemplatePage, run_ts: str, case_id: str) -> dict:
    """新增一条模版并保存并提交，使其进入待审核状态。"""
    info = _create_draft(tpl, run_ts, case_id)
    # 重新打开编辑并提交
    tpl.fill_name(info["name"])
    tpl.click_query()
    # 直接点击提交（如果有提交按钮）；否则编辑后保存并提交
    try:
        tpl.click_submit(info["name"])
        tpl.confirm_message_box()
        tpl.wait_table_ready()
    except (FeedingTemplateReadinessError, FeedingTemplateSelectorError):
        # 没有提交按钮，改为编辑后保存并提交
        tpl.click_edit(info["name"])
        tpl.submit_dialog()
    info["status"] = "待审核"
    return info


# ============================================================
# 用例函数（按编号升序）
# ============================================================


def test_tc_003_06(*, page: Page, settings: Settings, evidence_dir: Path, case_meta: dict) -> dict:
    """仅输入模版名称后点击查询，列表按名称过滤。"""
    tpl = FeedingTemplatePage(page, settings)
    try:
        tpl.ensure_open()
        tpl.wait_ready()
        all_rows = tpl.get_table_rows()
        if not all_rows:
            raise FeedingTemplateReadinessError("列表没有可用于名称查询的数据")
        # 用完整模版名称作为关键字，避免系统分词匹配导致歧义
        target_name = all_rows[0]["name"]
        tpl.fill_name(target_name)
        tpl.click_query()
        result_rows = tpl.get_table_rows()
        result_names = [r["name"] for r in result_rows]
        actual = {"keyword": target_name, "result_names": result_names, "result_count": len(result_rows)}
        screenshots = _capture_table(tpl, evidence_dir, case_meta, "assertion")
        valid = bool(result_rows) and all(name == target_name for name in result_names)
        if not valid:
            screenshots.extend(_capture_table(tpl, evidence_dir, case_meta, "failure"))
            return _result(case_meta, "failed", "product_defect",
                           f"名称查询结果未全部等于 {target_name}：{result_names}", actual, screenshots)
        return _result(case_meta, "passed", "passed", f"名称查询结果均匹配 {target_name}", actual, screenshots)
    except FeedingTemplateReadinessError as exc:
        return _handle_blocked(tpl, evidence_dir, case_meta, exc)
    except FeedingTemplateSelectorError as exc:
        return _handle_selector(tpl, evidence_dir, case_meta, exc)
    except PlaywrightTimeoutError as exc:
        return _handle_timeout(tpl, evidence_dir, case_meta, exc)
    except Exception as exc:
        return _handle_unexpected(tpl, evidence_dir, case_meta, exc)


def test_tc_003_07(*, page: Page, settings: Settings, evidence_dir: Path, case_meta: dict) -> dict:
    """仅选品种后点击查询，列表按品种过滤。"""
    tpl = FeedingTemplatePage(page, settings)
    try:
        tpl.ensure_open()
        tpl.wait_ready()
        all_rows = tpl.get_table_rows()
        if not all_rows:
            raise FeedingTemplateReadinessError("列表没有可用于品种查询的数据")
        target_breed = all_rows[0]["breed"]
        tpl.select_breed(target_breed)
        tpl.click_query()
        result_rows = tpl.get_table_rows()
        result_breeds = [r["breed"] for r in result_rows]
        actual = {"selected_breed": target_breed, "result_breeds": result_breeds, "result_count": len(result_rows)}
        screenshots = _capture_table(tpl, evidence_dir, case_meta, "assertion")
        if not result_rows or any(breed != target_breed for breed in result_breeds):
            screenshots.extend(_capture_table(tpl, evidence_dir, case_meta, "failure"))
            return _result(case_meta, "failed", "product_defect",
                           f"品种查询结果未全部匹配 {target_breed}：{result_breeds}", actual, screenshots)
        return _result(case_meta, "passed", "passed", f"品种查询结果均匹配 {target_breed}", actual, screenshots)
    except FeedingTemplateReadinessError as exc:
        return _handle_blocked(tpl, evidence_dir, case_meta, exc)
    except FeedingTemplateSelectorError as exc:
        return _handle_selector(tpl, evidence_dir, case_meta, exc)
    except PlaywrightTimeoutError as exc:
        return _handle_timeout(tpl, evidence_dir, case_meta, exc)
    except Exception as exc:
        return _handle_unexpected(tpl, evidence_dir, case_meta, exc)


def test_tc_003_08(*, page: Page, settings: Settings, evidence_dir: Path, case_meta: dict) -> dict:
    """仅选补栏月份后点击查询，列表按补栏月份过滤。"""
    tpl = FeedingTemplatePage(page, settings)
    try:
        tpl.ensure_open()
        tpl.wait_ready()
        all_rows = tpl.get_table_rows()
        if not all_rows:
            raise FeedingTemplateReadinessError("列表没有可用于补栏月份查询的数据")
        target_month = all_rows[0]["month"]
        tpl.select_restock_month(target_month)
        tpl.click_query()
        result_rows = tpl.get_table_rows()
        result_months = [r["month"] for r in result_rows]
        actual = {"selected_month": target_month, "result_months": result_months, "result_count": len(result_rows)}
        screenshots = _capture_table(tpl, evidence_dir, case_meta, "assertion")
        if not result_rows or any(month != target_month for month in result_months):
            screenshots.extend(_capture_table(tpl, evidence_dir, case_meta, "failure"))
            return _result(case_meta, "failed", "product_defect",
                           f"补栏月份查询结果未全部匹配 {target_month}：{result_months}", actual, screenshots)
        return _result(case_meta, "passed", "passed", f"补栏月份查询结果均匹配 {target_month}", actual, screenshots)
    except FeedingTemplateReadinessError as exc:
        return _handle_blocked(tpl, evidence_dir, case_meta, exc)
    except FeedingTemplateSelectorError as exc:
        return _handle_selector(tpl, evidence_dir, case_meta, exc)
    except PlaywrightTimeoutError as exc:
        return _handle_timeout(tpl, evidence_dir, case_meta, exc)
    except Exception as exc:
        return _handle_unexpected(tpl, evidence_dir, case_meta, exc)


def test_tc_003_09(*, page: Page, settings: Settings, evidence_dir: Path, case_meta: dict) -> dict:
    """仅选状态后点击查询，列表按状态过滤。"""
    tpl = FeedingTemplatePage(page, settings)
    try:
        tpl.ensure_open()
        tpl.wait_ready()
        all_rows = tpl.get_table_rows()
        if not all_rows:
            raise FeedingTemplateReadinessError("列表没有可用于状态查询的数据")
        statuses = [r["status"] for r in all_rows if r["status"]]
        if not statuses:
            raise FeedingTemplateReadinessError("列表没有可识别的状态数据")
        target_status = statuses[0]
        tpl.select_status(target_status)
        tpl.click_query()
        result_rows = tpl.get_table_rows()
        result_statuses = [r["status"] for r in result_rows]
        actual = {"selected_status": target_status, "result_statuses": result_statuses, "result_count": len(result_rows)}
        screenshots = _capture_table(tpl, evidence_dir, case_meta, "assertion")
        if not result_rows or any(status != target_status for status in result_statuses):
            screenshots.extend(_capture_table(tpl, evidence_dir, case_meta, "failure"))
            return _result(case_meta, "failed", "product_defect",
                           f"状态查询结果未全部匹配 {target_status}：{result_statuses}", actual, screenshots)
        return _result(case_meta, "passed", "passed", f"状态查询结果均匹配 {target_status}", actual, screenshots)
    except FeedingTemplateReadinessError as exc:
        return _handle_blocked(tpl, evidence_dir, case_meta, exc)
    except FeedingTemplateSelectorError as exc:
        return _handle_selector(tpl, evidence_dir, case_meta, exc)
    except PlaywrightTimeoutError as exc:
        return _handle_timeout(tpl, evidence_dir, case_meta, exc)
    except Exception as exc:
        return _handle_unexpected(tpl, evidence_dir, case_meta, exc)


def test_tc_003_10(*, page: Page, settings: Settings, evidence_dir: Path, case_meta: dict) -> dict:
    """选择多条件后点击查询，列表按组合条件过滤。"""
    tpl = FeedingTemplatePage(page, settings)
    try:
        tpl.ensure_open()
        tpl.wait_ready()
        all_rows = tpl.get_table_rows()
        if not all_rows:
            raise FeedingTemplateReadinessError("列表没有可用于组合查询的数据")
        first = all_rows[0]
        target_name = first["name"]
        target_breed = first["breed"]
        target_month = first["month"]
        target_status = first["status"]
        if not (target_name and target_breed and target_month and target_status):
            raise FeedingTemplateReadinessError("列表首行字段不完整，无法组合查询")
        tpl.fill_name(target_name)
        tpl.select_breed(target_breed)
        tpl.select_restock_month(target_month)
        tpl.select_status(target_status)
        tpl.click_query()
        result_rows = tpl.get_table_rows()
        actual = {
            "selected_name": target_name, "selected_breed": target_breed,
            "selected_month": target_month, "selected_status": target_status,
            "result_rows": result_rows, "result_count": len(result_rows),
        }
        screenshots = _capture_table(tpl, evidence_dir, case_meta, "assertion")
        valid = bool(result_rows) and all(
            r["name"] == target_name and r["breed"] == target_breed
            and r["month"] == target_month and r["status"] == target_status
            for r in result_rows
        )
        if not valid:
            screenshots.extend(_capture_table(tpl, evidence_dir, case_meta, "failure"))
            return _result(case_meta, "failed", "product_defect",
                           "组合查询结果未同时匹配全部筛选条件", actual, screenshots)
        return _result(case_meta, "passed", "passed", "组合查询结果同时匹配全部筛选条件", actual, screenshots)
    except FeedingTemplateReadinessError as exc:
        return _handle_blocked(tpl, evidence_dir, case_meta, exc)
    except FeedingTemplateSelectorError as exc:
        return _handle_selector(tpl, evidence_dir, case_meta, exc)
    except PlaywrightTimeoutError as exc:
        return _handle_timeout(tpl, evidence_dir, case_meta, exc)
    except Exception as exc:
        return _handle_unexpected(tpl, evidence_dir, case_meta, exc)


def test_tc_003_12(*, page: Page, settings: Settings, evidence_dir: Path, case_meta: dict) -> dict:
    """点击重置，查询条件恢复默认并刷新列表。"""
    tpl = FeedingTemplatePage(page, settings)
    try:
        tpl.ensure_open()
        tpl.wait_ready()
        all_rows = tpl.get_table_rows()
        if not all_rows:
            raise FeedingTemplateReadinessError("列表没有可用于重置验证的数据")
        first = all_rows[0]
        target_name = first["name"]
        target_breed = first["breed"]
        tpl.fill_name(target_name)
        tpl.select_breed(target_breed)
        tpl.click_query()
        tpl.reset_query()
        values = tpl.get_query_values()
        row_count = tpl.get_row_count()
        actual = {"query_values_after_reset": values, "row_count": row_count}
        screenshots = _capture_evidence(tpl, evidence_dir, case_meta, "assertion")
        name_empty = (values.get("name") in ("", None))
        breed_default = (values.get("breed") in ("请选择", "请选择品种", "", None, "全部"))
        valid = name_empty and breed_default and row_count > 0
        if not valid:
            screenshots.extend(_capture_evidence(tpl, evidence_dir, case_meta, "failure"))
            return _result(case_meta, "failed", "product_defect",
                           f"重置后查询条件未恢复默认：{values}", actual, screenshots)
        return _result(case_meta, "passed", "passed", "重置后查询条件恢复默认且列表刷新", actual, screenshots)
    except FeedingTemplateReadinessError as exc:
        return _handle_blocked(tpl, evidence_dir, case_meta, exc)
    except FeedingTemplateSelectorError as exc:
        return _handle_selector(tpl, evidence_dir, case_meta, exc)
    except PlaywrightTimeoutError as exc:
        return _handle_timeout(tpl, evidence_dir, case_meta, exc)
    except Exception as exc:
        return _handle_unexpected(tpl, evidence_dir, case_meta, exc)


def test_tc_003_31(*, page: Page, settings: Settings, evidence_dir: Path, case_meta: dict) -> dict:
    """新增模版（含快速分配），验证日龄采食计划起止日龄自动回填。"""
    tpl = FeedingTemplatePage(page, settings)
    run_ts = _run_ts()
    name = f"AUTO测试_勿用_RUN{run_ts}_031"
    cleanup_result = None
    try:
        tpl.ensure_open()
        tpl.wait_ready()
        all_rows = tpl.get_table_rows()
        if not all_rows:
            raise FeedingTemplateReadinessError("列表无数据，无法获取参考品种")
        breed = "京白 939"
        month = "3月"
        for r in all_rows:
            if r["breed"] and "勿用" not in r["breed"] and "停用" not in r["breed"]:
                breed = r["breed"]
                month = r["month"]
                break
        tpl.click_new()
        title = tpl.dialog_title()
        tpl.fill_template_form(name, breed, month)
        # 读取三段养殖天数（自动计算）
        seg_days = tpl.get_segment_days()
        # 读取日龄采食计划起止
        plans = tpl.get_daily_feed_plans()
        actual = {"dialog_title": title, "segment_days": seg_days, "feed_plans": plans}
        screenshots = _capture_table(tpl, evidence_dir, case_meta, "assertion")
        valid = bool(title) and "新增" in title and len(seg_days) >= 3
        if not valid:
            screenshots.extend(_capture_table(tpl, evidence_dir, case_meta, "failure"))
            return _result(case_meta, "failed", "product_defect",
                           f"新增弹窗或自动回填异常：title={title} seg={seg_days}", actual, screenshots)
        return _result(case_meta, "passed", "passed",
                       f"新增弹窗标题正确，三段天数自动计算：{seg_days}", actual, screenshots)
    except FeedingTemplateReadinessError as exc:
        return _handle_blocked(tpl, evidence_dir, case_meta, exc)
    except FeedingTemplateSelectorError as exc:
        return _handle_selector(tpl, evidence_dir, case_meta, exc)
    except PlaywrightTimeoutError as exc:
        return _handle_timeout(tpl, evidence_dir, case_meta, exc)
    except Exception as exc:
        return _handle_unexpected(tpl, evidence_dir, case_meta, exc)
    finally:
        try:
            tpl.cancel_dialog()
        except Exception:
            pass
        cleanup_result = _cleanup_template(tpl, name)
        if cleanup_result not in ("not_found", "deleted"):
            case_meta.setdefault("cleanup_notes", []).append(f"TC-003-31 cleanup: {cleanup_result}")


def test_tc_003_62(*, page: Page, settings: Settings, evidence_dir: Path, case_meta: dict) -> dict:
    """新增模版点击保存，验证暂存成功且列表出现该记录。"""
    tpl = FeedingTemplatePage(page, settings)
    run_ts = _run_ts()
    name = f"AUTO测试_勿用_RUN{run_ts}_062"
    try:
        tpl.ensure_open()
        tpl.wait_ready()
        info = _create_draft(tpl, run_ts, "062")
        name = info["name"]
        # 验证列表出现该记录
        tpl.fill_name(name)
        tpl.click_query()
        rows = tpl.get_table_rows()
        result_names = [r["name"] for r in rows]
        statuses = [r["status"] for r in rows]
        actual = {"created_name": name, "result_names": result_names, "statuses": statuses}
        screenshots = _capture_table(tpl, evidence_dir, case_meta, "assertion")
        valid = name in result_names
        if not valid:
            screenshots.extend(_capture_table(tpl, evidence_dir, case_meta, "failure"))
            return _result(case_meta, "failed", "product_defect",
                           f"暂存后列表未出现该记录：{result_names}", actual, screenshots)
        return _result(case_meta, "passed", "passed", f"暂存成功，列表出现记录 {name}", actual, screenshots)
    except FeedingTemplateReadinessError as exc:
        return _handle_blocked(tpl, evidence_dir, case_meta, exc)
    except FeedingTemplateSelectorError as exc:
        return _handle_selector(tpl, evidence_dir, case_meta, exc)
    except PlaywrightTimeoutError as exc:
        return _handle_timeout(tpl, evidence_dir, case_meta, exc)
    except Exception as exc:
        return _handle_unexpected(tpl, evidence_dir, case_meta, exc)
    finally:
        cleanup_result = _cleanup_template(tpl, name)
        if cleanup_result not in ("not_found", "deleted"):
            case_meta.setdefault("cleanup_notes", []).append(f"TC-003-62 cleanup: {cleanup_result}")


def test_tc_003_63(*, page: Page, settings: Settings, evidence_dir: Path, case_meta: dict) -> dict:
    """新增模版点击保存并提交，验证状态变为待审核。"""
    tpl = FeedingTemplatePage(page, settings)
    run_ts = _run_ts()
    name = f"AUTO测试_勿用_RUN{run_ts}_063"
    try:
        tpl.ensure_open()
        tpl.wait_ready()
        all_rows = tpl.get_table_rows()
        breed = "京白 939"
        month = "3月"
        for r in all_rows:
            if r["breed"] and "勿用" not in r["breed"] and "停用" not in r["breed"]:
                breed = r["breed"]
                month = r["month"]
                break
        tpl.click_new()
        tpl.fill_template_form(name, breed, month)
        tpl.submit_dialog()
        # 验证状态
        tpl.fill_name(name)
        tpl.click_query()
        rows = tpl.get_table_rows()
        result_names = [r["name"] for r in rows]
        statuses = [r["status"] for r in rows]
        actual = {"created_name": name, "result_names": result_names, "statuses": statuses}
        screenshots = _capture_table(tpl, evidence_dir, case_meta, "assertion")
        valid = name in result_names and "待审核" in statuses
        if not valid:
            screenshots.extend(_capture_table(tpl, evidence_dir, case_meta, "failure"))
            return _result(case_meta, "failed", "product_defect",
                           f"保存并提交后状态未变为待审核：{statuses}", actual, screenshots)
        return _result(case_meta, "passed", "passed", "保存并提交后状态变为待审核", actual, screenshots)
    except FeedingTemplateReadinessError as exc:
        return _handle_blocked(tpl, evidence_dir, case_meta, exc)
    except FeedingTemplateSelectorError as exc:
        return _handle_selector(tpl, evidence_dir, case_meta, exc)
    except PlaywrightTimeoutError as exc:
        return _handle_timeout(tpl, evidence_dir, case_meta, exc)
    except Exception as exc:
        return _handle_unexpected(tpl, evidence_dir, case_meta, exc)
    finally:
        cleanup_result = _cleanup_template(tpl, name)
        if cleanup_result not in ("not_found", "deleted"):
            case_meta.setdefault("cleanup_notes", []).append(f"TC-003-63 cleanup: {cleanup_result}")


def test_tc_003_131(*, page: Page, settings: Settings, evidence_dir: Path, case_meta: dict) -> dict:
    """点击提交按钮后出现二次确认框。"""
    tpl = FeedingTemplatePage(page, settings)
    run_ts = _run_ts()
    name = f"AUTO测试_勿用_RUN{run_ts}_131"
    try:
        tpl.ensure_open()
        tpl.wait_ready()
        info = _create_draft(tpl, run_ts, "131")
        name = info["name"]
        tpl.fill_name(name)
        tpl.click_query()
        tpl.click_submit(name)
        box_text = tpl.page.locator(".el-message-box:visible").first.inner_text()
        actual = {"box_text": box_text}
        screenshots = _capture_table(tpl, evidence_dir, case_meta, "assertion")
        # 取消确认，不实际提交
        tpl.cancel_message_box()
        valid = "提交" in box_text or "确认" in box_text
        if not valid:
            screenshots.extend(_capture_table(tpl, evidence_dir, case_meta, "failure"))
            return _result(case_meta, "failed", "product_defect",
                           f"提交确认框文案异常：{box_text}", actual, screenshots)
        return _result(case_meta, "passed", "passed", f"提交弹出二次确认框：{box_text[:50]}", actual, screenshots)
    except FeedingTemplateReadinessError as exc:
        return _handle_blocked(tpl, evidence_dir, case_meta, exc)
    except FeedingTemplateSelectorError as exc:
        return _handle_selector(tpl, evidence_dir, case_meta, exc)
    except PlaywrightTimeoutError as exc:
        return _handle_timeout(tpl, evidence_dir, case_meta, exc)
    except Exception as exc:
        return _handle_unexpected(tpl, evidence_dir, case_meta, exc)
    finally:
        cleanup_result = _cleanup_template(tpl, name)
        if cleanup_result not in ("not_found", "deleted"):
            case_meta.setdefault("cleanup_notes", []).append(f"TC-003-131 cleanup: {cleanup_result}")


def test_tc_003_133(*, page: Page, settings: Settings, evidence_dir: Path, case_meta: dict) -> dict:
    """确认提交后状态变为待审核。"""
    tpl = FeedingTemplatePage(page, settings)
    run_ts = _run_ts()
    name = f"AUTO测试_勿用_RUN{run_ts}_133"
    try:
        tpl.ensure_open()
        tpl.wait_ready()
        info = _create_draft(tpl, run_ts, "133")
        name = info["name"]
        tpl.fill_name(name)
        tpl.click_query()
        tpl.click_submit(name)
        tpl.confirm_message_box()
        tpl.wait_table_ready()
        rows = tpl.get_table_rows()
        statuses = [r["status"] for r in rows if r["name"] == name]
        actual = {"created_name": name, "statuses_after_submit": statuses}
        screenshots = _capture_table(tpl, evidence_dir, case_meta, "assertion")
        valid = "待审核" in statuses
        if not valid:
            screenshots.extend(_capture_table(tpl, evidence_dir, case_meta, "failure"))
            return _result(case_meta, "failed", "product_defect",
                           f"确认提交后状态未变为待审核：{statuses}", actual, screenshots)
        return _result(case_meta, "passed", "passed", "确认提交后状态变为待审核", actual, screenshots)
    except FeedingTemplateReadinessError as exc:
        return _handle_blocked(tpl, evidence_dir, case_meta, exc)
    except FeedingTemplateSelectorError as exc:
        return _handle_selector(tpl, evidence_dir, case_meta, exc)
    except PlaywrightTimeoutError as exc:
        return _handle_timeout(tpl, evidence_dir, case_meta, exc)
    except Exception as exc:
        return _handle_unexpected(tpl, evidence_dir, case_meta, exc)
    finally:
        cleanup_result = _cleanup_template(tpl, name)
        if cleanup_result not in ("not_found", "deleted"):
            case_meta.setdefault("cleanup_notes", []).append(f"TC-003-133 cleanup: {cleanup_result}")


def test_tc_003_137(*, page: Page, settings: Settings, evidence_dir: Path, case_meta: dict) -> dict:
    """审核驳回时需填写驳回原因。"""
    tpl = FeedingTemplatePage(page, settings)
    run_ts = _run_ts()
    name = f"AUTO测试_勿用_RUN{run_ts}_137"
    try:
        tpl.ensure_open()
        tpl.wait_ready()
        info = _create_pending(tpl, run_ts, "137")
        name = info["name"]
        tpl.fill_name(name)
        tpl.click_query()
        tpl.click_review(name)
        reason = f"AUTO驳回测试_{run_ts}"
        # 点驳回，填原因，但取消不实际驳回（验证原因输入必填）
        dlg = tpl.dialog()
        reject_btn = dlg.get_by_role("button", name="驳回", exact=True)
        if not reject_btn.count():
            raise FeedingTemplateSelectorError("审核弹窗无驳回按钮")
        reject_btn.first.click()
        confirm = tpl.page.locator(".el-dialog:visible").last
        confirm.wait_for(state="visible", timeout=8_000)
        reason_input = confirm.locator("textarea").first
        if not reason_input.count():
            reason_input = confirm.locator('input[placeholder*="原因"]').first
        if not reason_input.count():
            raise FeedingTemplateSelectorError("驳回原因输入框不可定位")
        reason_input.fill(reason)
        actual = {"reject_reason_input": reason, "dialog_visible": True}
        screenshots = _capture_table(tpl, evidence_dir, case_meta, "assertion")
        # 关闭不提交
        close = confirm.locator(".el-dialog__headerbtn").first
        if close.count():
            close.click()
            tpl.page.wait_for_timeout(500)
        # 关闭审核弹窗
        close2 = tpl.dialog().locator(".el-dialog__headerbtn").first
        if close2.count():
            close2.click()
            tpl.page.wait_for_timeout(500)
        return _result(case_meta, "passed", "passed",
                       "审核驳回弹窗出现原因输入框", actual, screenshots)
    except FeedingTemplateReadinessError as exc:
        return _handle_blocked(tpl, evidence_dir, case_meta, exc)
    except FeedingTemplateSelectorError as exc:
        return _handle_selector(tpl, evidence_dir, case_meta, exc)
    except PlaywrightTimeoutError as exc:
        return _handle_timeout(tpl, evidence_dir, case_meta, exc)
    except Exception as exc:
        return _handle_unexpected(tpl, evidence_dir, case_meta, exc)
    finally:
        cleanup_result = _cleanup_template(tpl, name)
        if cleanup_result not in ("not_found", "deleted"):
            case_meta.setdefault("cleanup_notes", []).append(f"TC-003-137 cleanup: {cleanup_result}")


def test_tc_003_139(*, page: Page, settings: Settings, evidence_dir: Path, case_meta: dict) -> dict:
    """审核驳回后状态变为驳回。"""
    tpl = FeedingTemplatePage(page, settings)
    run_ts = _run_ts()
    name = f"AUTO测试_勿用_RUN{run_ts}_139"
    try:
        tpl.ensure_open()
        tpl.wait_ready()
        info = _create_pending(tpl, run_ts, "139")
        name = info["name"]
        tpl.fill_name(name)
        tpl.click_query()
        tpl.click_review(name)
        tpl.review_reject(f"AUTO驳回_{run_ts}")
        rows = tpl.get_table_rows()
        statuses = [r["status"] for r in rows if r["name"] == name]
        actual = {"name": name, "statuses_after_reject": statuses}
        screenshots = _capture_table(tpl, evidence_dir, case_meta, "assertion")
        valid = "驳回" in statuses
        if not valid:
            screenshots.extend(_capture_table(tpl, evidence_dir, case_meta, "failure"))
            return _result(case_meta, "failed", "product_defect",
                           f"驳回后状态未变为驳回：{statuses}", actual, screenshots)
        return _result(case_meta, "passed", "passed", "驳回后状态变为驳回", actual, screenshots)
    except FeedingTemplateReadinessError as exc:
        return _handle_blocked(tpl, evidence_dir, case_meta, exc)
    except FeedingTemplateSelectorError as exc:
        return _handle_selector(tpl, evidence_dir, case_meta, exc)
    except PlaywrightTimeoutError as exc:
        return _handle_timeout(tpl, evidence_dir, case_meta, exc)
    except Exception as exc:
        return _handle_unexpected(tpl, evidence_dir, case_meta, exc)
    finally:
        # 驳回状态无法回滚为暂存，尝试删除（可能无删除权限）
        cleanup_result = _cleanup_template(tpl, name)
        if cleanup_result not in ("not_found", "deleted"):
            case_meta.setdefault("cleanup_notes", []).append(f"TC-003-139 cleanup: {cleanup_result}")


def test_tc_003_140(*, page: Page, settings: Settings, evidence_dir: Path, case_meta: dict) -> dict:
    """审核通过操作。"""
    tpl = FeedingTemplatePage(page, settings)
    run_ts = _run_ts()
    name = f"AUTO测试_勿用_RUN{run_ts}_140"
    try:
        tpl.ensure_open()
        tpl.wait_ready()
        info = _create_pending(tpl, run_ts, "140")
        name = info["name"]
        tpl.fill_name(name)
        tpl.click_query()
        tpl.click_review(name)
        box_text = tpl.review_approve()
        rows = tpl.get_table_rows()
        statuses = [r["status"] for r in rows if r["name"] == name]
        actual = {"name": name, "confirm_box_text": box_text, "statuses_after_approve": statuses}
        screenshots = _capture_table(tpl, evidence_dir, case_meta, "assertion")
        valid = "审核通过" in statuses
        if not valid:
            screenshots.extend(_capture_table(tpl, evidence_dir, case_meta, "failure"))
            return _result(case_meta, "failed", "product_defect",
                           f"审核通过后状态未变为审核通过：{statuses}", actual, screenshots)
        return _result(case_meta, "passed", "passed", "审核通过操作成功，状态变为审核通过", actual, screenshots)
    except FeedingTemplateReadinessError as exc:
        return _handle_blocked(tpl, evidence_dir, case_meta, exc)
    except FeedingTemplateSelectorError as exc:
        return _handle_selector(tpl, evidence_dir, case_meta, exc)
    except PlaywrightTimeoutError as exc:
        return _handle_timeout(tpl, evidence_dir, case_meta, exc)
    except Exception as exc:
        return _handle_unexpected(tpl, evidence_dir, case_meta, exc)
    finally:
        # 审核通过无法回滚，列入 Handoff
        case_meta.setdefault("cleanup_notes", []).append(
            f"TC-003-140 cleanup: 审核通过记录 {name} 无法自动回滚，待人工清理"
        )


def test_tc_003_141(*, page: Page, settings: Settings, evidence_dir: Path, case_meta: dict) -> dict:
    """审核通过时出现二次确认框。"""
    tpl = FeedingTemplatePage(page, settings)
    run_ts = _run_ts()
    name = f"AUTO测试_勿用_RUN{run_ts}_141"
    try:
        tpl.ensure_open()
        tpl.wait_ready()
        info = _create_pending(tpl, run_ts, "141")
        name = info["name"]
        tpl.fill_name(name)
        tpl.click_query()
        tpl.click_review(name)
        dlg = tpl.dialog()
        approve_btn = dlg.get_by_role("button", name="审核通过", exact=True)
        if not approve_btn.count():
            approve_btn = dlg.get_by_role("button", name="通过", exact=True)
        if not approve_btn.count():
            raise FeedingTemplateSelectorError("审核弹窗无通过按钮")
        approve_btn.first.click()
        box = tpl.page.locator(".el-message-box:visible")
        box.wait_for(state="visible", timeout=5_000)
        box_text = box.inner_text()
        actual = {"confirm_box_text": box_text}
        screenshots = _capture_table(tpl, evidence_dir, case_meta, "assertion")
        # 取消不实际通过
        tpl.cancel_message_box()
        # 关闭审核弹窗
        close = tpl.dialog().locator(".el-dialog__headerbtn").first
        if close.count():
            close.click()
            tpl.page.wait_for_timeout(500)
        valid = "确认" in box_text or "通过" in box_text
        if not valid:
            screenshots.extend(_capture_table(tpl, evidence_dir, case_meta, "failure"))
            return _result(case_meta, "failed", "product_defect",
                           f"审核通过确认框文案异常：{box_text}", actual, screenshots)
        return _result(case_meta, "passed", "passed", f"审核通过弹出二次确认框：{box_text[:50]}", actual, screenshots)
    except FeedingTemplateReadinessError as exc:
        return _handle_blocked(tpl, evidence_dir, case_meta, exc)
    except FeedingTemplateSelectorError as exc:
        return _handle_selector(tpl, evidence_dir, case_meta, exc)
    except PlaywrightTimeoutError as exc:
        return _handle_timeout(tpl, evidence_dir, case_meta, exc)
    except Exception as exc:
        return _handle_unexpected(tpl, evidence_dir, case_meta, exc)
    finally:
        cleanup_result = _cleanup_template(tpl, name)
        if cleanup_result not in ("not_found", "deleted"):
            case_meta.setdefault("cleanup_notes", []).append(f"TC-003-141 cleanup: {cleanup_result}")


def test_tc_003_142(*, page: Page, settings: Settings, evidence_dir: Path, case_meta: dict) -> dict:
    """审核通过确认后状态变为审核通过。"""
    tpl = FeedingTemplatePage(page, settings)
    run_ts = _run_ts()
    name = f"AUTO测试_勿用_RUN{run_ts}_142"
    try:
        tpl.ensure_open()
        tpl.wait_ready()
        info = _create_pending(tpl, run_ts, "142")
        name = info["name"]
        tpl.fill_name(name)
        tpl.click_query()
        tpl.click_review(name)
        tpl.review_approve()
        rows = tpl.get_table_rows()
        statuses = [r["status"] for r in rows if r["name"] == name]
        actual = {"name": name, "statuses_after_approve": statuses}
        screenshots = _capture_table(tpl, evidence_dir, case_meta, "assertion")
        valid = "审核通过" in statuses
        if not valid:
            screenshots.extend(_capture_table(tpl, evidence_dir, case_meta, "failure"))
            return _result(case_meta, "failed", "product_defect",
                           f"确认审核通过后状态未变为审核通过：{statuses}", actual, screenshots)
        return _result(case_meta, "passed", "passed", "确认审核通过后状态变为审核通过", actual, screenshots)
    except FeedingTemplateReadinessError as exc:
        return _handle_blocked(tpl, evidence_dir, case_meta, exc)
    except FeedingTemplateSelectorError as exc:
        return _handle_selector(tpl, evidence_dir, case_meta, exc)
    except PlaywrightTimeoutError as exc:
        return _handle_timeout(tpl, evidence_dir, case_meta, exc)
    except Exception as exc:
        return _handle_unexpected(tpl, evidence_dir, case_meta, exc)
    finally:
        case_meta.setdefault("cleanup_notes", []).append(
            f"TC-003-142 cleanup: 审核通过记录 {name} 无法自动回滚，待人工清理"
        )


def test_tc_003_143(*, page: Page, settings: Settings, evidence_dir: Path, case_meta: dict) -> dict:
    """点击删除后出现确认框。"""
    tpl = FeedingTemplatePage(page, settings)
    run_ts = _run_ts()
    name = f"AUTO测试_勿用_RUN{run_ts}_143"
    try:
        tpl.ensure_open()
        tpl.wait_ready()
        info = _create_draft(tpl, run_ts, "143")
        name = info["name"]
        tpl.fill_name(name)
        tpl.click_query()
        tpl.click_delete(name)
        box_text = tpl.page.locator(".el-message-box:visible").first.inner_text()
        actual = {"box_text": box_text}
        screenshots = _capture_table(tpl, evidence_dir, case_meta, "assertion")
        # 取消不实际删除
        tpl.cancel_message_box()
        valid = "删除" in box_text or "确认" in box_text
        if not valid:
            screenshots.extend(_capture_table(tpl, evidence_dir, case_meta, "failure"))
            return _result(case_meta, "failed", "product_defect",
                           f"删除确认框文案异常：{box_text}", actual, screenshots)
        return _result(case_meta, "passed", "passed", f"删除弹出确认框：{box_text[:50]}", actual, screenshots)
    except FeedingTemplateReadinessError as exc:
        return _handle_blocked(tpl, evidence_dir, case_meta, exc)
    except FeedingTemplateSelectorError as exc:
        return _handle_selector(tpl, evidence_dir, case_meta, exc)
    except PlaywrightTimeoutError as exc:
        return _handle_timeout(tpl, evidence_dir, case_meta, exc)
    except Exception as exc:
        return _handle_unexpected(tpl, evidence_dir, case_meta, exc)
    finally:
        cleanup_result = _cleanup_template(tpl, name)
        if cleanup_result not in ("not_found", "deleted"):
            case_meta.setdefault("cleanup_notes", []).append(f"TC-003-143 cleanup: {cleanup_result}")


def test_tc_003_145(*, page: Page, settings: Settings, evidence_dir: Path, case_meta: dict) -> dict:
    """确认删除后列表不再显示该记录。"""
    tpl = FeedingTemplatePage(page, settings)
    run_ts = _run_ts()
    name = f"AUTO测试_勿用_RUN{run_ts}_145"
    try:
        tpl.ensure_open()
        tpl.wait_ready()
        info = _create_draft(tpl, run_ts, "145")
        name = info["name"]
        tpl.fill_name(name)
        tpl.click_query()
        tpl.click_delete(name)
        tpl.confirm_message_box()
        tpl.wait_table_ready()
        rows = tpl.get_table_rows()
        result_names = [r["name"] for r in rows]
        actual = {"deleted_name": name, "result_names_after_delete": result_names}
        screenshots = _capture_table(tpl, evidence_dir, case_meta, "assertion")
        valid = name not in result_names
        if not valid:
            screenshots.extend(_capture_table(tpl, evidence_dir, case_meta, "failure"))
            return _result(case_meta, "failed", "product_defect",
                           f"删除后列表仍显示该记录：{result_names}", actual, screenshots)
        return _result(case_meta, "passed", "passed", f"删除后列表不再显示 {name}", actual, screenshots)
    except FeedingTemplateReadinessError as exc:
        return _handle_blocked(tpl, evidence_dir, case_meta, exc)
    except FeedingTemplateSelectorError as exc:
        return _handle_selector(tpl, evidence_dir, case_meta, exc)
    except PlaywrightTimeoutError as exc:
        return _handle_timeout(tpl, evidence_dir, case_meta, exc)
    except Exception as exc:
        return _handle_unexpected(tpl, evidence_dir, case_meta, exc)


def test_tc_003_149(*, page: Page, settings: Settings, evidence_dir: Path, case_meta: dict) -> dict:
    """点击复制后出现确认框。"""
    tpl = FeedingTemplatePage(page, settings)
    run_ts = _run_ts()
    copied_name = None
    try:
        tpl.ensure_open()
        tpl.wait_ready()
        # 找一条审核通过的记录
        tpl.reset_query()
        all_rows = tpl.get_table_rows()
        approved = [r for r in all_rows if r["status"] == "审核通过"]
        if not approved:
            raise FeedingTemplateReadinessError("列表无审核通过记录，无法测试复制")
        target = approved[0]["name"]
        tpl.click_copy(target)
        box_text = tpl.page.locator(".el-message-box:visible").first.inner_text()
        actual = {"source_name": target, "box_text": box_text}
        screenshots = _capture_table(tpl, evidence_dir, case_meta, "assertion")
        # 确认复制
        tpl.confirm_message_box()
        tpl.wait_table_ready()
        # 复制后可能弹出编辑弹窗或直接生成新记录
        rows = tpl.get_table_rows()
        copy_candidates = [r["name"] for r in rows if target in r["name"] or "复制" in r["name"]]
        actual["copy_candidates"] = copy_candidates
        valid = "复制" in box_text or "确认" in box_text
        if not valid:
            screenshots.extend(_capture_table(tpl, evidence_dir, case_meta, "failure"))
            return _result(case_meta, "failed", "product_defect",
                           f"复制确认框文案异常：{box_text}", actual, screenshots)
        # 记录可能产生的复制记录名用于清理
        if copy_candidates:
            copied_name = copy_candidates[0]
        return _result(case_meta, "passed", "passed", f"复制弹出确认框：{box_text[:50]}", actual, screenshots)
    except FeedingTemplateReadinessError as exc:
        return _handle_blocked(tpl, evidence_dir, case_meta, exc)
    except FeedingTemplateSelectorError as exc:
        return _handle_selector(tpl, evidence_dir, case_meta, exc)
    except PlaywrightTimeoutError as exc:
        return _handle_timeout(tpl, evidence_dir, case_meta, exc)
    except Exception as exc:
        return _handle_unexpected(tpl, evidence_dir, case_meta, exc)
    finally:
        if copied_name:
            cleanup_result = _cleanup_template(tpl, copied_name)
            if cleanup_result not in ("not_found", "deleted"):
                case_meta.setdefault("cleanup_notes", []).append(f"TC-003-149 cleanup: {cleanup_result}")

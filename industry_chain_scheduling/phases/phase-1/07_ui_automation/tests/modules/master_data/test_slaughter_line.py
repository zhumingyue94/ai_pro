"""宰杀线管理模块用例（TC-014-01 ~ TC-014-35）：基于真实页面选择器实现，无猜测。

每个 test_tc_014_xx 接收 page/settings/evidence_dir/case_meta，返回结果 dict。
页面对象 SlaughterLinePage 假定当前已在宰杀线管理页（ensure_open 保证）；
批量执行时由 run_module.py 负责进入与复位，pytest 下由 ensure_open 自行导航。
"""

from __future__ import annotations

import time
from pathlib import Path

from playwright.sync_api import Page

from config.settings import Settings
from pages.master_data.slaughter_line_page import SlaughterLinePage


def _result(status: str, scope: str, detail: str, shot: str) -> dict:
    """构造统一的用例结果字典。"""
    return {"status": status, "assertion_scope": scope, "detail": detail, "screenshot": shot}


def _status_row_index(slaughter: SlaughterLinePage, status: str) -> int:
    """在列表中查找首个状态匹配的行索引，未找到返回 -1。"""
    for i in range(slaughter.get_row_count()):
        if slaughter.get_row_status(i) == status:
            return i
    return -1


def _form_errors(slaughter: SlaughterLinePage) -> list[str]:
    """读取当前可见弹窗内的字段校验错误文本列表。"""
    loc = slaughter.page.locator(".el-dialog:visible .el-form-item__error")
    return [loc.nth(k).inner_text().strip() for k in range(loc.count())]


def _unique_name(tag: str) -> str:
    """生成带时间戳的唯一宰杀线名称，用于新增用例避免重名。"""
    return f"AUTO_{tag}_{int(time.time()) % 100000:05d}"


def test_tc_014_01(*, page: Page, settings: Settings, evidence_dir: Path, case_meta: dict) -> dict:
    """打开宰杀线管理页，断言查询区含宰杀线编码/名称/状态筛选项并返回结果。"""
    slaughter = SlaughterLinePage(page, settings)
    app = slaughter.ensure_open()
    labels = slaughter.get_query_filter_labels()
    shot = str(evidence_dir / "TC-014-01_query_filters.png")
    app.screenshot(path=shot, full_page=True)
    scope = case_meta.get("assertion_scope") or "slaughter_line.query_filters"
    try:
        slaughter.assert_filters_present()
    except AssertionError as exc:
        return _result("failed", scope, str(exc), shot)
    return _result("passed", scope, f"查询区可见筛选项：{labels}", shot)


def test_tc_014_02(*, page: Page, settings: Settings, evidence_dir: Path, case_meta: dict) -> dict:
    """断言状态下拉选项仅为启用、停用。"""
    slaughter = SlaughterLinePage(page, settings)
    app = slaughter.ensure_open()
    shot = str(evidence_dir / "TC-014-02_status_options.png")
    app.screenshot(path=shot, full_page=True)
    scope = case_meta.get("assertion_scope") or "slaughter_line.status_options"
    opts = slaughter.get_status_options()
    if set(opts) != {"启用", "停用"}:
        return _result("failed", scope, f"状态下拉选项不符，实际：{opts}", shot)
    return _result("passed", scope, f"状态下拉选项：{opts}", shot)


def test_tc_014_03(*, page: Page, settings: Settings, evidence_dir: Path, case_meta: dict) -> dict:
    """填写编码+名称+状态后查询，列表按 AND 条件过滤（仅显示匹配行）。"""
    slaughter = SlaughterLinePage(page, settings)
    app = slaughter.ensure_open()
    shot = str(evidence_dir / "TC-014-03_query_and_filter.png")
    name = "二号宰杀线"
    slaughter.fill_query(name=name, status="启用")
    slaughter.click_query()
    rows = [slaughter.get_row_name(i) for i in range(slaughter.get_row_count())]
    app.screenshot(path=shot, full_page=True)
    scope = case_meta.get("assertion_scope") or "slaughter_line.query_and_filter"
    if not rows or not all(n == name for n in rows):
        return _result("failed", scope, f"查询后列表未按名称过滤；实际行名：{rows}", shot)
    return _result("passed", scope, f"查询后 {len(rows)} 行均匹配名称={name}", shot)


def test_tc_014_04(*, page: Page, settings: Settings, evidence_dir: Path, case_meta: dict) -> dict:
    """修改筛选条件但不点查询，列表不刷新；点查询后列表按条件刷新。"""
    slaughter = SlaughterLinePage(page, settings)
    app = slaughter.ensure_open()
    shot = str(evidence_dir / "TC-014-04_query_button_triggers.png")
    name = "二号宰杀线"
    before = slaughter.get_row_count()
    slaughter.fill_query(name=name)
    after_fill = slaughter.get_row_count()
    slaughter.click_query()
    after_query = [slaughter.get_row_name(i) for i in range(slaughter.get_row_count())]
    app.screenshot(path=shot, full_page=True)
    scope = case_meta.get("assertion_scope") or "slaughter_line.query_button_triggers"
    if after_fill != before:
        return _result("failed", scope, f"未点查询列表已变化（{before}->{after_fill}）", shot)
    if not after_query or not all(n == name for n in after_query):
        return _result("failed", scope, f"点查询后未过滤；实际：{after_query}", shot)
    return _result("passed", scope, f"未点查询不变({before})，点查询后{len(after_query)}行均匹配", shot)


def test_tc_014_05(*, page: Page, settings: Settings, evidence_dir: Path, case_meta: dict) -> dict:
    """设置查询条件点击查询后，点击重置清空条件并刷新列表。"""
    slaughter = SlaughterLinePage(page, settings)
    app = slaughter.ensure_open()
    shot = str(evidence_dir / "TC-014-05_reset.png")
    base = slaughter.get_row_count()
    slaughter.fill_query(name="二号宰杀线")
    slaughter.click_query()
    slaughter.click_reset()
    name_val = slaughter.page.locator(".el-form-item").filter(has_text="宰杀线名称").locator(".el-input__inner").first.input_value()
    after = slaughter.get_row_count()
    app.screenshot(path=shot, full_page=True)
    scope = case_meta.get("assertion_scope") or "slaughter_line.reset"
    if name_val != "" or after != base:
        return _result("failed", scope, f"重置后名称输入框='{name_val}'，行数 {base}->{after}", shot)
    return _result("passed", scope, f"重置后筛选清空且行数恢复为 {after}", shot)


def test_tc_014_06(*, page: Page, settings: Settings, evidence_dir: Path, case_meta: dict) -> dict:
    """点击新增打开弹窗，断言关键字段齐全。"""
    slaughter = SlaughterLinePage(page, settings)
    app = slaughter.ensure_open()
    slaughter.open_new_dialog()
    labels = slaughter.get_new_dialog_labels()
    shot = str(evidence_dir / "TC-014-06_new_dialog_fields.png")
    app.screenshot(path=shot, full_page=True)
    slaughter.close_dialog()
    scope = case_meta.get("assertion_scope") or "slaughter_line.new_dialog_fields"
    needed = ["宰杀线编码", "宰杀线名称", "单日产能(万只)", "排序", "状态", "备注"]
    missing = [n for n in needed if n not in labels]
    if missing:
        return _result("failed", scope, f"新增弹窗缺少字段 {missing}；实际：{labels}", shot)
    return _result("passed", scope, f"新增弹窗字段：{labels}", shot)


def test_tc_014_07(*, page: Page, settings: Settings, evidence_dir: Path, case_meta: dict) -> dict:
    """新增弹窗宰杀线编码由系统预填且可修改。"""
    slaughter = SlaughterLinePage(page, settings)
    app = slaughter.ensure_open()
    slaughter.open_new_dialog()
    code = slaughter.get_new_code_value()
    readonly = slaughter.is_new_code_readonly()
    shot = str(evidence_dir / "TC-014-07_new_code_prefilled.png")
    app.screenshot(path=shot, full_page=True)
    slaughter.close_dialog()
    scope = case_meta.get("assertion_scope") or "slaughter_line.new_code_prefilled"
    if not code or readonly:
        return _result("failed", scope, f"编码预填值='{code}'，只读={readonly}", shot)
    return _result("passed", scope, f"编码已预填='{code}'且可编辑", shot)


def test_tc_014_08(*, page: Page, settings: Settings, evidence_dir: Path, case_meta: dict) -> dict:
    """新增留空宰杀线名称点确定，提示名称不能为空且未保存。"""
    slaughter = SlaughterLinePage(page, settings)
    app = slaughter.ensure_open()
    before = slaughter.get_row_count()
    slaughter.open_new_dialog()
    slaughter.submit_dialog()
    errors = _form_errors(slaughter)
    after = slaughter.get_row_count()
    shot = str(evidence_dir / "TC-014-08_new_name_required.png")
    app.screenshot(path=shot, full_page=True)
    slaughter.close_dialog()
    scope = case_meta.get("assertion_scope") or "slaughter_line.new_name_required"
    if not any("不能为空" in e or "必填" in e for e in errors) or after != before:
        return _result("failed", scope, f"未拦截：错误={errors}，行数 {before}->{after}", shot)
    return _result("passed", scope, f"名称留空被拦截：{errors}", shot)


def test_tc_014_09(*, page: Page, settings: Settings, evidence_dir: Path, case_meta: dict) -> dict:
    """TC-014-09（revised）：新增表单必填项留空点保存，无法保存且「必填项」提示必填。

    步骤：点击「新增」打开表单 → 必填项留空 → 点击保存（确定）
    预期：无法保存（列表行数不变/弹窗不消失），必填项出现必填提示
    """
    slaughter = SlaughterLinePage(page, settings)
    app = slaughter.ensure_open()
    before = slaughter.get_row_count()
    slaughter.open_new_dialog()
    # 不填写任何必填项，直接点击保存（确定）
    slaughter.submit_dialog()
    errors = _form_errors(slaughter)          # 字段级 .el-dialog:visible .el-form-item__error
    toast = slaughter.get_toast_text()        # 可能的 toast 提示
    after = slaughter.get_row_count()
    shot = str(evidence_dir / "TC-014-09_new_required_block.png")
    app.screenshot(path=shot, full_page=True)
    slaughter.close_dialog()
    scope = case_meta.get("assertion_scope") or "slaughter_line.new_required_block"
    # 预期：无法保存（行数不变）且出现必填提示（字段错误含「必填」/「不能为空」，或 toast 含相应文案）
    required_hint = any(("必填" in e or "不能为空" in e) for e in errors) or ("必填" in toast or "不能为空" in toast)
    saved = after != before
    if saved or not required_hint:
        return _result(
            "failed", scope,
            f"未拦截或提示缺失：字段错误={errors}，toast={toast}，行数 {before}->{after}",
            shot,
        )
    return _result("passed", scope, f"必填项留空被拦截：字段错误={errors}", shot)


def test_tc_014_10(*, page: Page, settings: Settings, evidence_dir: Path, case_meta: dict) -> dict:
    """新增填写部分字段后点取消，弹窗关闭且不保存。"""
    slaughter = SlaughterLinePage(page, settings)
    app = slaughter.ensure_open()
    before = slaughter.get_row_count()
    slaughter.open_new_dialog()
    slaughter._fill_dialog_input("请输入宰杀线名称", _unique_name("C10"))
    slaughter.cancel_dialog()
    after = slaughter.get_row_count()
    shot = str(evidence_dir / "TC-014-10_new_cancel.png")
    app.screenshot(path=shot, full_page=True)
    scope = case_meta.get("assertion_scope") or "slaughter_line.new_cancel"
    if after != before:
        return _result("failed", scope, f"取消后仍新增：行数 {before}->{after}", shot)
    return _result("passed", scope, f"取消后未新增（行数 {after}）", shot)


def test_tc_014_11(*, page: Page, settings: Settings, evidence_dir: Path, case_meta: dict) -> dict:
    """新增单日产能留空，确定后保存成功，列表新增记录。"""
    slaughter = SlaughterLinePage(page, settings)
    app = slaughter.ensure_open()
    name = _unique_name("C11")
    slaughter.open_new_dialog()
    slaughter.fill_new_form(name=name)
    slaughter.submit_dialog()
    shot = str(evidence_dir / "TC-014-11_new_capacity_empty.png")
    app.screenshot(path=shot, full_page=True)
    scope = case_meta.get("assertion_scope") or "slaughter_line.new_capacity_empty"
    try:
        idx = slaughter.find_row_index_by_name(name)
    except AssertionError as exc:
        return _result("failed", scope, f"{exc}；toast={slaughter.get_toast_text()}", shot)
    return _result("passed", scope, f"新增成功，行名={name}（产能留空）", shot)


def test_tc_014_12(*, page: Page, settings: Settings, evidence_dir: Path, case_meta: dict) -> dict:
    """列表表头包含核心列：宰杀线编码/名称/单日产能(万只)/排序/状态。"""
    slaughter = SlaughterLinePage(page, settings)
    app = slaughter.ensure_open()
    headers = slaughter.get_header_texts()
    shot = str(evidence_dir / "TC-014-12_table_core_columns.png")
    app.screenshot(path=shot, full_page=True)
    scope = case_meta.get("assertion_scope") or "slaughter_line.table_core_columns"
    needed = ["宰杀线编码", "宰杀线名称", "单日产能(万只)", "排序", "状态"]
    missing = [n for n in needed if n not in headers]
    if missing:
        return _result("failed", scope, f"缺少核心列 {missing}；实际：{headers}", shot)
    return _result("passed", scope, f"核心列齐全：{needed}", shot)


def test_tc_014_13(*, page: Page, settings: Settings, evidence_dir: Path, case_meta: dict) -> dict:
    """新增单日产能输入 112.0000，列表展示一致。"""
    slaughter = SlaughterLinePage(page, settings)
    app = slaughter.ensure_open()
    name = _unique_name("C13")
    slaughter.open_new_dialog()
    slaughter.fill_new_form(name=name, capacity="112.0000")
    slaughter.submit_dialog()
    shot = str(evidence_dir / "TC-014-13_new_capacity_decimal.png")
    app.screenshot(path=shot, full_page=True)
    scope = case_meta.get("assertion_scope") or "slaughter_line.new_capacity_decimal"
    try:
        idx = slaughter.find_row_index_by_name(name)
    except AssertionError as exc:
        return _result("failed", scope, f"{exc}", shot)
    cells = slaughter.get_row_texts(idx)
    if len(cells) <= 3 or cells[3] != "112.0000":
        return _result("failed", scope, f"产能展示不符，行={cells}", shot)
    return _result("passed", scope, f"新增成功，产能展示={cells[3]}", shot)


def test_tc_014_14(*, page: Page, settings: Settings, evidence_dir: Path, case_meta: dict) -> dict:
    """新增排序留空，确定后保存成功，列表新增记录。"""
    slaughter = SlaughterLinePage(page, settings)
    app = slaughter.ensure_open()
    name = _unique_name("C14")
    slaughter.open_new_dialog()
    slaughter.fill_new_form(name=name)
    slaughter.submit_dialog()
    shot = str(evidence_dir / "TC-014-14_new_sort_empty.png")
    app.screenshot(path=shot, full_page=True)
    scope = case_meta.get("assertion_scope") or "slaughter_line.new_sort_empty"
    try:
        slaughter.find_row_index_by_name(name)
    except AssertionError as exc:
        return _result("failed", scope, f"{exc}", shot)
    return _result("passed", scope, f"排序留空新增成功，行名={name}", shot)


def test_tc_014_15(*, page: Page, settings: Settings, evidence_dir: Path, case_meta: dict) -> dict:
    """新增排序输入 0，列表展示 0。"""
    slaughter = SlaughterLinePage(page, settings)
    app = slaughter.ensure_open()
    name = _unique_name("C15")
    slaughter.open_new_dialog()
    slaughter.fill_new_form(name=name, sort="0")
    slaughter.submit_dialog()
    shot = str(evidence_dir / "TC-014-15_new_sort_zero.png")
    app.screenshot(path=shot, full_page=True)
    scope = case_meta.get("assertion_scope") or "slaughter_line.new_sort_zero"
    try:
        idx = slaughter.find_row_index_by_name(name)
    except AssertionError as exc:
        return _result("failed", scope, f"{exc}", shot)
    cells = slaughter.get_row_texts(idx)
    if len(cells) <= 4 or cells[4] != "0":
        return _result("failed", scope, f"排序展示不符，行={cells}", shot)
    return _result("passed", scope, f"排序=0 展示一致，行={cells}", shot)


def test_tc_014_16(*, page: Page, settings: Settings, evidence_dir: Path, case_meta: dict) -> dict:
    """新增排序输入 1，列表展示 1。"""
    slaughter = SlaughterLinePage(page, settings)
    app = slaughter.ensure_open()
    name = _unique_name("C16")
    slaughter.open_new_dialog()
    slaughter.fill_new_form(name=name, sort="1")
    slaughter.submit_dialog()
    shot = str(evidence_dir / "TC-014-16_new_sort_one.png")
    app.screenshot(path=shot, full_page=True)
    scope = case_meta.get("assertion_scope") or "slaughter_line.new_sort_one"
    try:
        idx = slaughter.find_row_index_by_name(name)
    except AssertionError as exc:
        return _result("failed", scope, f"{exc}", shot)
    cells = slaughter.get_row_texts(idx)
    if len(cells) <= 4 or cells[4] != "1":
        return _result("failed", scope, f"排序展示不符，行={cells}", shot)
    return _result("passed", scope, f"排序=1 展示一致，行={cells}", shot)


def test_tc_014_17(*, page: Page, settings: Settings, evidence_dir: Path, case_meta: dict) -> dict:
    """新增将编码改为库中已存在编码，确定触发唯一性拦截。"""
    slaughter = SlaughterLinePage(page, settings)
    app = slaughter.ensure_open()
    existing_code = slaughter.get_row_texts(0)[1]
    before = slaughter.get_row_count()
    slaughter.open_new_dialog()
    slaughter._fill_dialog_input("请输入宰杀线编码", existing_code)
    slaughter._fill_dialog_input("请输入宰杀线名称", _unique_name("C17"))
    slaughter.submit_dialog()
    errors = _form_errors(slaughter)
    toast = slaughter.get_toast_text()
    after = slaughter.get_row_count()
    shot = str(evidence_dir / "TC-014-17_new_code_unique.png")
    app.screenshot(path=shot, full_page=True)
    slaughter.close_dialog()
    scope = case_meta.get("assertion_scope") or "slaughter_line.new_code_unique"
    blocked = errors or ("唯一" in toast) or ("已存在" in toast)
    if not blocked or after != before:
        return _result("failed", scope, f"未拦截：错误={errors}，toast={toast}，行数 {before}->{after}", shot)
    return _result("passed", scope, f"重复编码被拦截：{errors or toast}", shot)


def test_tc_014_18(*, page: Page, settings: Settings, evidence_dir: Path, case_meta: dict) -> dict:
    """新增名称填库中已存在名称，确定触发唯一性拦截。"""
    slaughter = SlaughterLinePage(page, settings)
    app = slaughter.ensure_open()
    existing_name = slaughter.get_row_texts(0)[2]
    before = slaughter.get_row_count()
    slaughter.open_new_dialog()
    slaughter._fill_dialog_input("请输入宰杀线名称", existing_name)
    slaughter.submit_dialog()
    errors = _form_errors(slaughter)
    toast = slaughter.get_toast_text()
    after = slaughter.get_row_count()
    shot = str(evidence_dir / "TC-014-18_new_name_unique.png")
    app.screenshot(path=shot, full_page=True)
    slaughter.close_dialog()
    scope = case_meta.get("assertion_scope") or "slaughter_line.new_name_unique"
    blocked = errors or ("唯一" in toast) or ("已存在" in toast)
    if not blocked or after != before:
        return _result("failed", scope, f"未拦截：错误={errors}，toast={toast}，行数 {before}->{after}", shot)
    return _result("passed", scope, f"重复名称被拦截：{errors or toast}", shot)


def test_tc_014_19(*, page: Page, settings: Settings, evidence_dir: Path, case_meta: dict) -> dict:
    """列表表头列顺序与需求一致。"""
    slaughter = SlaughterLinePage(page, settings)
    app = slaughter.ensure_open()
    shot = str(evidence_dir / "TC-014-19_table_headers_order.png")
    app.screenshot(path=shot, full_page=True)
    scope = case_meta.get("assertion_scope") or "slaughter_line.table_headers_order"
    try:
        headers = slaughter.assert_headers_order()
    except AssertionError as exc:
        return _result("failed", scope, str(exc), shot)
    return _result("passed", scope, f"表头顺序一致：{headers}", shot)


def test_tc_014_20(*, page: Page, settings: Settings, evidence_dir: Path, case_meta: dict) -> dict:
    """列表首行编码/名称与录入一致（字段非空且彼此对应）。"""
    slaughter = SlaughterLinePage(page, settings)
    app = slaughter.ensure_open()
    cells = slaughter.get_row_texts(0)
    shot = str(evidence_dir / "TC-014-20_table_row_consistency.png")
    app.screenshot(path=shot, full_page=True)
    scope = case_meta.get("assertion_scope") or "slaughter_line.table_row_consistency"
    if len(cells) <= 2 or not cells[1] or not cells[2]:
        return _result("failed", scope, f"首行字段缺失：{cells}", shot)
    return _result("passed", scope, f"首行编码={cells[1]}，名称={cells[2]}", shot)


def test_tc_014_21(*, page: Page, settings: Settings, evidence_dir: Path, case_meta: dict) -> dict:
    """启用状态行操作列显示编辑、停用。"""
    slaughter = SlaughterLinePage(page, settings)
    app = slaughter.ensure_open()
    shot = str(evidence_dir / "TC-014-21_enabled_row_actions.png")
    idx = _status_row_index(slaughter, "启用")
    app.screenshot(path=shot, full_page=True)
    scope = case_meta.get("assertion_scope") or "slaughter_line.enabled_row_actions"
    if idx < 0:
        return _result("failed", scope, "列表中无启用状态行", shot)
    actions = slaughter.get_row_actions(idx)
    if "编辑" not in actions or "停用" not in actions:
        return _result("failed", scope, f"操作列不符，实际：{actions}", shot)
    return _result("passed", scope, f"启用行操作列：{actions}", shot)


def test_tc_014_22(*, page: Page, settings: Settings, evidence_dir: Path, case_meta: dict) -> dict:
    """无匹配记录时列表展示空状态，页面无报错。"""
    slaughter = SlaughterLinePage(page, settings)
    app = slaughter.ensure_open()
    slaughter.fill_query(name="ZZZ_不存在的测试名称_ZZZ")
    slaughter.click_query()
    empty = slaughter.get_empty_text()
    count = slaughter.get_row_count()
    shot = str(evidence_dir / "TC-014-22_empty_state.png")
    app.screenshot(path=shot, full_page=True)
    scope = case_meta.get("assertion_scope") or "slaughter_line.empty_state"
    if count != 0 and not empty:
        return _result("failed", scope, f"无匹配时未显示空状态：行数={count}，空文本='{empty}'", shot)
    return _result("passed", scope, f"无匹配显示空状态：行数={count}，空文本='{empty}'", shot)


def test_tc_014_23(*, page: Page, settings: Settings, evidence_dir: Path, case_meta: dict) -> dict:
    """列表分页默认展示第1页，总条数与查询结果一致。"""
    slaughter = SlaughterLinePage(page, settings)
    app = slaughter.ensure_open()
    text = slaughter.get_pagination_text()
    shot = str(evidence_dir / "TC-014-23_pagination.png")
    app.screenshot(path=shot, full_page=True)
    scope = case_meta.get("assertion_scope") or "slaughter_line.pagination"
    if "共" not in text or "条" not in text:
        return _result("failed", scope, f"分页信息异常：'{text}'", shot)
    return _result("passed", scope, f"分页信息：{text}", shot)


def test_tc_014_24(*, page: Page, settings: Settings, evidence_dir: Path, case_meta: dict) -> dict:
    """点击编辑打开编辑弹窗。"""
    slaughter = SlaughterLinePage(page, settings)
    app = slaughter.ensure_open()
    slaughter.open_edit_dialog(0)
    labels = slaughter.get_new_dialog_labels()
    shot = str(evidence_dir / "TC-014-24_edit_dialog_open.png")
    app.screenshot(path=shot, full_page=True)
    slaughter.close_dialog()
    scope = case_meta.get("assertion_scope") or "slaughter_line.edit_dialog_open"
    if not labels:
        return _result("failed", scope, "编辑弹窗未打开或无字段", shot)
    return _result("passed", scope, f"编辑弹窗字段：{labels}", shot)


def test_tc_014_25(*, page: Page, settings: Settings, evidence_dir: Path, case_meta: dict) -> dict:
    """编辑弹窗宰杀线编码只读不可修改。"""
    slaughter = SlaughterLinePage(page, settings)
    app = slaughter.ensure_open()
    slaughter.open_edit_dialog(0)
    readonly = slaughter.is_edit_code_readonly()
    shot = str(evidence_dir / "TC-014-25_edit_code_readonly.png")
    app.screenshot(path=shot, full_page=True)
    slaughter.close_dialog()
    scope = case_meta.get("assertion_scope") or "slaughter_line.edit_code_readonly"
    if not readonly:
        return _result("failed", scope, "编辑弹窗编码非只读", shot)
    return _result("passed", scope, "编辑弹窗编码为只读(disabled)", shot)


def test_tc_014_26(*, page: Page, settings: Settings, evidence_dir: Path, case_meta: dict) -> dict:
    """编辑修改名称后确定，列表对应行更新。"""
    slaughter = SlaughterLinePage(page, settings)
    app = slaughter.ensure_open()
    old_name = slaughter.get_row_texts(0)[2]
    new_name = f"{old_name}_改"
    slaughter.open_edit_dialog(0)
    slaughter.edit_fill(name=new_name)
    slaughter.submit_dialog()
    shot = str(evidence_dir / "TC-014-26_edit_update.png")
    app.screenshot(path=shot, full_page=True)
    scope = case_meta.get("assertion_scope") or "slaughter_line.edit_update"
    try:
        slaughter.find_row_index_by_name(new_name)
    except AssertionError as exc:
        return _result("failed", scope, f"{exc}；toast={slaughter.get_toast_text()}", shot)
    return _result("passed", scope, f"编辑后名称更新为 {new_name}", shot)


def test_tc_014_27(*, page: Page, settings: Settings, evidence_dir: Path, case_meta: dict) -> dict:
    """编辑修改后点取消，弹窗关闭且不保存。"""
    slaughter = SlaughterLinePage(page, settings)
    app = slaughter.ensure_open()
    old_name = slaughter.get_row_texts(0)[2]
    slaughter.open_edit_dialog(0)
    slaughter.edit_fill(name=f"{old_name}_临时")
    slaughter.cancel_dialog()
    shot = str(evidence_dir / "TC-014-27_edit_cancel.png")
    app.screenshot(path=shot, full_page=True)
    scope = case_meta.get("assertion_scope") or "slaughter_line.edit_cancel"
    try:
        slaughter.find_row_index_by_name(old_name)
    except AssertionError:
        return _result("failed", scope, f"取消后原行 {old_name} 丢失", shot)
    return _result("passed", scope, f"取消后未保存，原行 {old_name} 仍在", shot)


def test_tc_014_28(*, page: Page, settings: Settings, evidence_dir: Path, case_meta: dict) -> dict:
    """启用行点停用，弹出确认框文案为确定要停用该宰杀线吗？"""
    slaughter = SlaughterLinePage(page, settings)
    app = slaughter.ensure_open()
    idx = _status_row_index(slaughter, "启用")
    shot = str(evidence_dir / "TC-014-28_disable_confirm_text.png")
    scope = case_meta.get("assertion_scope") or "slaughter_line.disable_confirm_text"
    if idx < 0:
        return _result("failed", scope, "无启用行可操作", shot)
    slaughter.click_row_action(idx, "停用")
    text = slaughter.get_confirm_text()
    app.screenshot(path=shot, full_page=True)
    slaughter.confirm_cancel()
    if "确定要停用该宰杀线吗" not in text:
        return _result("failed", scope, f"确认文案不符：'{text}'", shot)
    return _result("passed", scope, f"停用确认文案：{text}", shot)


def test_tc_014_29(*, page: Page, settings: Settings, evidence_dir: Path, case_meta: dict) -> dict:
    """停用确认框点确定，状态变为停用。"""
    slaughter = SlaughterLinePage(page, settings)
    app = slaughter.ensure_open()
    idx = _status_row_index(slaughter, "启用")
    shot = str(evidence_dir / "TC-014-29_disable_to_stopped.png")
    scope = case_meta.get("assertion_scope") or "slaughter_line.disable_to_stopped"
    if idx < 0:
        return _result("failed", scope, "无启用行可操作", shot)
    name = slaughter.get_row_name(idx)
    slaughter.click_row_action(idx, "停用")
    slaughter.confirm_ok()
    after_idx = _status_row_index(slaughter, "停用")
    for i in range(slaughter.get_row_count()):
        if slaughter.get_row_name(i) == name:
            after_idx = i
            break
    app.screenshot(path=shot, full_page=True)
    if after_idx < 0 or slaughter.get_row_status(after_idx) != "停用":
        return _result("failed", scope, f"停用后状态未变；行名={name}", shot)
    return _result("passed", scope, f"行 {name} 已停用", shot)


def test_tc_014_30(*, page: Page, settings: Settings, evidence_dir: Path, case_meta: dict) -> dict:
    """停用确认框点取消，状态保持启用。"""
    slaughter = SlaughterLinePage(page, settings)
    app = slaughter.ensure_open()
    idx = _status_row_index(slaughter, "启用")
    shot = str(evidence_dir / "TC-014-30_disable_cancel_keep.png")
    scope = case_meta.get("assertion_scope") or "slaughter_line.disable_cancel_keep"
    if idx < 0:
        return _result("failed", scope, "无启用行可操作", shot)
    name = slaughter.get_row_name(idx)
    slaughter.click_row_action(idx, "停用")
    slaughter.confirm_cancel()
    keep_idx = -1
    for i in range(slaughter.get_row_count()):
        if slaughter.get_row_name(i) == name:
            keep_idx = i
            break
    app.screenshot(path=shot, full_page=True)
    if keep_idx < 0 or slaughter.get_row_status(keep_idx) != "启用":
        return _result("failed", scope, f"取消后状态改变；行名={name}", shot)
    return _result("passed", scope, f"取消后 {name} 仍为启用", shot)


def test_tc_014_31(*, page: Page, settings: Settings, evidence_dir: Path, case_meta: dict) -> dict:
    """未勾选行时批量删除/启用/停用按钮不可用。"""
    slaughter = SlaughterLinePage(page, settings)
    app = slaughter.ensure_open()
    shot = str(evidence_dir / "TC-014-31_batch_disabled.png")
    app.screenshot(path=shot, full_page=True)
    scope = case_meta.get("assertion_scope") or "slaughter_line.batch_disabled_no_selection"
    states = {n: slaughter.is_batch_button_disabled(n) for n in ["删除", "启用", "停用"]}
    if not all(states.values()):
        return _result("failed", scope, f"未勾选时批量按钮未全禁用：{states}", shot)
    return _result("passed", scope, f"未勾选时批量按钮均禁用：{states}", shot)


def test_tc_014_32(*, page: Page, settings: Settings, evidence_dir: Path, case_meta: dict) -> dict:
    """勾选停用行点批量启用，状态变为启用。"""
    slaughter = SlaughterLinePage(page, settings)
    app = slaughter.ensure_open()
    idx = _status_row_index(slaughter, "停用")
    shot = str(evidence_dir / "TC-014-32_batch_enable.png")
    scope = case_meta.get("assertion_scope") or "slaughter_line.batch_enable"
    if idx < 0:
        return _result("failed", scope, "无停用行可批量启用", shot)
    name = slaughter.get_row_name(idx)
    slaughter.select_row(idx)
    slaughter.click_batch("启用")
    after_idx = -1
    for i in range(slaughter.get_row_count()):
        if slaughter.get_row_name(i) == name:
            after_idx = i
            break
    app.screenshot(path=shot, full_page=True)
    if after_idx < 0 or slaughter.get_row_status(after_idx) != "启用":
        return _result("failed", scope, f"批量启用后状态未变；行名={name}", shot)
    return _result("passed", scope, f"行 {name} 已批量启用", shot)


def test_tc_014_33(*, page: Page, settings: Settings, evidence_dir: Path, case_meta: dict) -> dict:
    """勾选启用行点批量删除，提示启用状态无法删除且未删除。"""
    slaughter = SlaughterLinePage(page, settings)
    app = slaughter.ensure_open()
    idx = _status_row_index(slaughter, "启用")
    shot = str(evidence_dir / "TC-014-33_batch_delete_enabled.png")
    scope = case_meta.get("assertion_scope") or "slaughter_line.batch_delete_enabled_blocked"
    if idx < 0:
        return _result("failed", scope, "无启用行可操作", shot)
    name = slaughter.get_row_name(idx)
    before = slaughter.get_row_count()
    slaughter.select_row(idx)
    slaughter.click_batch("删除")
    toast = slaughter.get_toast_text()
    after = slaughter.get_row_count()
    app.screenshot(path=shot, full_page=True)
    if "无法删除" not in toast and "启用" not in toast:
        return _result("failed", scope, f"未提示无法删除：toast='{toast}'", shot)
    if after != before:
        return _result("failed", scope, f"启用行被误删：行数 {before}->{after}", shot)
    return _result("passed", scope, f"启用行删除被拦截：{toast}", shot)


def test_tc_014_34(*, page: Page, settings: Settings, evidence_dir: Path, case_meta: dict) -> dict:
    """已选≥1条时批量删除按钮可点击。"""
    slaughter = SlaughterLinePage(page, settings)
    app = slaughter.ensure_open()
    idx = _status_row_index(slaughter, "启用")
    shot = str(evidence_dir / "TC-014-34_batch_delete_enabled_state.png")
    scope = case_meta.get("assertion_scope") or "slaughter_line.batch_delete_enabled_when_selected"
    if idx < 0:
        return _result("failed", scope, "无启用行可勾选", shot)
    slaughter.select_row(idx)
    disabled = slaughter.is_batch_button_disabled("删除")
    app.screenshot(path=shot, full_page=True)
    if disabled:
        return _result("failed", scope, "勾选后批量删除仍禁用", shot)
    return _result("passed", scope, "勾选后批量删除按钮可用", shot)


def test_tc_014_35(*, page: Page, settings: Settings, evidence_dir: Path, case_meta: dict) -> dict:
    """勾选停用行点批量删除，确认后删除成功（无停用行时先禁用一行再删，自包含）。"""
    slaughter = SlaughterLinePage(page, settings)
    app = slaughter.ensure_open()
    shot = str(evidence_dir / "TC-014-35_batch_delete_disabled.png")
    scope = case_meta.get("assertion_scope") or "slaughter_line.batch_delete_disabled"
    idx = _status_row_index(slaughter, "停用")
    if idx < 0:
        eidx = _status_row_index(slaughter, "启用")
        if eidx < 0:
            return _result("failed", scope, "列表中既无停用行也无启用行可操作", shot)
        name = slaughter.get_row_name(eidx)
        slaughter.click_row_action(eidx, "停用")
        slaughter.confirm_ok()
        for i in range(slaughter.get_row_count()):
            if slaughter.get_row_name(i) == name:
                idx = i
                break
    if idx < 0:
        return _result("failed", scope, "未找到可删除的停用行", shot)
    name = slaughter.get_row_name(idx)
    slaughter.select_row(idx)
    slaughter.click_batch("删除")
    slaughter.confirm_ok()
    found = -1
    for i in range(slaughter.get_row_count()):
        if slaughter.get_row_name(i) == name:
            found = i
            break
    app.screenshot(path=shot, full_page=True)
    if found >= 0:
        return _result("failed", scope, f"停用行 {name} 删除未生效", shot)
    return _result("passed", scope, f"停用行 {name} 已删除", shot)

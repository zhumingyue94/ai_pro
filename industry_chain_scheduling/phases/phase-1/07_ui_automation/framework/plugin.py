"""pytest 钩子实现：把执行与产物流水线全部挂载到标准 pytest 生命周期。

产物流水线原来只存在于自研 runner ``tests/run_case.py`` 中，与 pytest 路径完全割裂；
这里把它下沉为 pytest 钩子，使一条 ``pytest`` 命令即可产出全部六类产物。

产物写出的三层保障：
1. ``pytest_sessionfinish`` —— 主写点（键盘中断也会执行）；
2. ``pytest_unconfigure`` —— 唯一无条件执行的兜底；
3. ``atexit`` —— 进程退出前的最后安全网。
三者之间通过 ``orch.finalized`` 做幂等互斥。
"""

from __future__ import annotations

import inspect
from typing import Any

import pytest

from . import case_source, classify, contract, evidence, integrity, registry as registry_mod, run_layout
from .options import SelectionFilter
from .orchestrator import get_orch
from .reporters import allure as allure_reporter
from .reporters import bugs_review, csv_live, defect_report, excel, handoff, registry_yaml, results, selection


def _is_framework(item) -> bool:
    """判断条目是否为本框架用例（注册表中存在映射条目）。"""
    return registry_mod.is_framework_item(item)


def _nodeid_narrowed(config) -> bool:
    """判断用户是否用具体文件或 nodeid 收窄了收集范围。"""
    for arg in getattr(config, "args", None) or []:
        text = str(arg)
        if "::" in text or text.endswith(".py"):
            return True
    return False


def _local_case_of(entry: dict) -> dict:
    """按注册表条目读取对应的本地用例定义。"""
    req_id = str(entry.get("req_id") or "")
    try:
        zentao_id = int(entry.get("zentao_case_id"))
    except (TypeError, ValueError):
        return {}
    return case_source.load_testcases(req_id).get(zentao_id) or {}


def _executable(entry: dict, local_case: dict) -> tuple[bool, str]:
    """判断条目是否允许启动浏览器执行，返回 ``(是否执行, 不执行原因)``。"""
    test_type = str(local_case.get("type", "")).lower()
    auto_flag = str(local_case.get("auto", "auto")).lower()
    if local_case and test_type and test_type != "auto":
        return False, f"type={test_type!r}，仅 type: auto 允许执行；当前记录为 excluded。"
    if auto_flag == "no":
        return False, "automation: no，按规则 excluded 不执行。"
    if entry.get("mapping_status") != "registered":
        return False, f"mapping_status={entry.get('mapping_status')!r}，未完成注册映射。"
    required = (
        entry.get("handler"),
        entry.get("page_object"),
        entry.get("data_contract"),
        entry.get("check_id"),
        entry.get("assertion_scope"),
    )
    if any(not value for value in required):
        return False, "module_case_map.json 缺少已实现 handler/Page Object/data contract/断言契约。"
    return True, ""


def pytest_configure(config) -> None:
    """创建会话编排器并做全局前置校验。"""
    from .orchestrator import create

    create(config)
    config.addinivalue_line("markers", "ui_case: 本框架 return-dict 用例（由 framework 自动标记）")
    if config.pluginmanager.hasplugin("xdist"):
        workers = getattr(config.option, "numprocesses", None)
        if workers and int(workers) > 1:
            pytest.exit(
                "UI 自动化禁用 pytest-xdist：RUN 目录与浏览器上下文为进程内共享状态。",
                returncode=integrity.EXIT_USAGE,
            )


def pytest_collection_modifyitems(session, config, items) -> None:
    """筛选、排序、推导 run_id、创建 RUN 目录并预填结果表。"""
    orch = get_orch(config)
    registry = registry_mod.load_registry()
    filt = SelectionFilter.from_config(config)

    framework = [item for item in items if _is_framework(item)]
    others = [item for item in items if not _is_framework(item)]
    if not framework:
        return

    matched: list[tuple[Any, dict, dict]] = []
    for item in framework:
        entry = registry.entry_for_item(item)
        local_case = _local_case_of(entry)
        if str(local_case.get("zentao_status") or "normal") != "normal":
            continue
        if not filt.match(entry, local_case):
            continue
        matched.append((item, entry, local_case))
    matched.sort(key=lambda triple: int(triple[1].get("zentao_case_id") or 0))

    exec_items: list[Any] = []
    non_exec: list[dict] = []
    for item, entry, local_case in matched:
        allowed, reason = _executable(entry, local_case)
        if not allowed:
            non_exec.append(contract.build_excluded_record(entry, local_case, reason))
            continue
        orch.plan(item.nodeid, entry, local_case)
        exec_items.append(item)

    # 注册表中已实现但无法收集到的条目（例如 handler 指向不存在的模块），
    # 仅在未用 nodeid 收窄范围时登记为 blocked，避免静默遗漏。
    if not _nodeid_narrowed(config):
        seen = {int(entry.get("zentao_case_id") or -1) for _item, entry, _case in matched}
        for entry in registry.cases:
            if not entry.get("handler"):
                continue
            try:
                zentao_id = int(entry.get("zentao_case_id"))
            except (TypeError, ValueError):
                continue
            if zentao_id in seen:
                continue
            local_case = _local_case_of(entry)
            if str(local_case.get("zentao_status") or "normal") != "normal":
                continue
            if not filt.match(entry, local_case):
                continue
            if registry.handler_importable(entry):
                continue
            non_exec.append(
                contract.build_blocked_record(
                    entry,
                    local_case,
                    "mapping_contract",
                    f"handler 模块不可导入：{entry.get('handler')}；未启动浏览器。",
                )
            )

    if not exec_items and not non_exec:
        if config.getoption("--allow-empty"):
            orch.exit_code = integrity.EXIT_OK
            items[:] = others
            return
        pytest.exit(
            "NO_MATCHED_CASES：当前 nodeid 与 --req/--module/--priority/--zentao-case-id 的交集为空；"
            "可用 --allow-empty 静默退出。",
            returncode=integrity.EXIT_USAGE,
        )

    _derive_scope(orch, exec_items, non_exec)

    if orch.collect_only:
        items[:] = exec_items + others
        return

    orch.run_id, orch.run_dir, orch.screenshots_dir = run_layout.create_run_dir(orch.label)
    run_layout.write_status(
        orch.run_dir,
        {
            "run_id": orch.run_id,
            "complete": False,
            "dry_run": orch.dry_run,
            "started_at": orch.started_at,
            "heartbeat": run_layout.now_iso(),
            "note": "RUN 创建时写入；若过程异常终止，本文件将保持 complete=false。",
        },
    )

    if orch.dry_run:
        for nodeid, (entry, local_case) in orch.planned.items():
            non_exec.append(contract.build_dry_run_record(entry, local_case, orch.run_id))
        orch.planned.clear()
        exec_items = []

    orch.non_executed_records = non_exec
    orch.expected_record_count = len(orch.planned) + len(non_exec)
    for item in exec_items:
        item.add_marker(pytest.mark.ui_case)
    items[:] = exec_items + others
    csv_live.prefill(orch)
    selection.write(orch, orch.ordered_records(), [])


def _derive_scope(orch, exec_items: list[Any], non_exec: list[dict]) -> None:
    """从选中条目推导需求、模块与 RUN 标签。"""
    req_ids: list[str] = []
    modules: list[str] = []
    for entry, _case in orch.planned.values():
        if entry.get("req_id") and entry["req_id"] not in req_ids:
            req_ids.append(str(entry["req_id"]))
    for record in non_exec:
        if record.get("req_id") and record["req_id"] not in req_ids:
            req_ids.append(str(record["req_id"]))
    for entry, _case in orch.planned.values():
        name = registry_mod.module_name_of(entry)
        if name not in modules:
            modules.append(name)
    for record in non_exec:
        if record.get("module") and record["module"] not in modules:
            modules.append(str(record["module"]))
    req_ids.sort()
    orch.req_ids = req_ids
    orch.module_names = modules
    explicit = orch.config.getoption("--run-label")
    orch.label = str(explicit) if explicit else run_layout.derive_label(modules)
    orch.filter_desc = SelectionFilter.from_config(orch.config).describe()


def pytest_runtest_setup(item) -> None:
    """记录单条用例的开始时间。"""
    orch = get_orch(item.config)
    if _is_framework(item):
        orch.record_started_at(item.nodeid, run_layout.now_iso())


@pytest.hookimpl(tryfirst=True)
def pytest_pyfunc_call(pyfuncitem):
    """接管 return-dict 用例的调用，捕获返回值或异常，不抛错改写 pytest 状态。"""
    orch = get_orch(pyfuncitem.config)
    if not _is_framework(pyfuncitem):
        return None
    started = orch.started_at_of(pyfuncitem.nodeid) or run_layout.now_iso()
    try:
        signature = inspect.signature(pyfuncitem.obj)
        kwargs = {
            name: value
            for name, value in pyfuncitem.funcargs.items()
            if name in signature.parameters
        }
        returned = pyfuncitem.obj(**kwargs)
    except Exception as exc:  # noqa: BLE001 - 任何异常都要转成可分类的结果
        entry = orch.entry_of(pyfuncitem.nodeid) or {}
        shots = evidence.capture_fallback(
            pyfuncitem.funcargs.get("page"),
            orch.screenshots_dir,
            str(entry.get("case_id") or ""),
            str(entry.get("check_id") or ""),
            "error",
        )
        returned = classify.build_exception_result(exc, shots)
    if not isinstance(returned, dict):
        returned = classify.build_non_dict_result(returned)
    orch.records[pyfuncitem.nodeid] = returned
    orch.record_started_at(pyfuncitem.nodeid, started)
    return True


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    """把用例返回值转成完整记录，并重写 pytest 报告对象避免统计失真。"""
    outcome = yield
    if call.when != "call":
        return
    orch = get_orch(item.config)
    raw = orch.records.get(item.nodeid)
    if raw is None or isinstance(raw, dict) and raw.get("__final_record__"):
        return
    entry = orch.entry_of(item.nodeid) or {}
    local_case = orch.local_case_of(item.nodeid) or {}
    record = contract.build_record(
        entry, local_case, raw, orch.run_dir, orch.started_at_of(item.nodeid)
    )
    record["__final_record__"] = True
    orch.records[item.nodeid] = record
    orch.append_jsonl(record)

    report = outcome.get_result()
    status = str(record.get("status") or "")
    summary = f"[{record.get('classification')}/{status}] {record.get('detail') or record.get('actual')}"
    location = getattr(item, "location", None) or ("", 0, "")
    if status == "passed":
        report.outcome = "passed"
        report.longrepr = None
    elif status == "failed":
        report.outcome = "failed"
        report.longrepr = summary
    else:
        # skipped 报告必须使用 (path, lineno, reason) 三元组，pytest 终端对其做了类型断言。
        report.outcome = "skipped"
        report.longrepr = (str(location[0]), int(location[1] or 0), summary)
    report.sections.append(
        (
            "UI 自动化分类",
            "\n".join(
                [
                    f"case_id: {record.get('case_id')}",
                    f"zentao_case_id: {record.get('zentao_case_id')}",
                    f"check_id: {record.get('check_id')}",
                    f"assertion_scope: {record.get('assertion_scope')}",
                    f"classification: {record.get('classification')}",
                    f"failure_origin: {record.get('failure_origin')}",
                ]
            ),
        )
    )


def pytest_keyboard_interrupt(excinfo) -> None:
    """标记被键盘中断，使 RUN 不得作为完整结果交付。"""
    try:
        from .orchestrator import get_orch

        config = getattr(excinfo, "config", None)
        if config is not None and hasattr(config, "stash"):
            get_orch(config).interrupted = True
    except Exception:  # noqa: BLE001 - 中断处理不得再抛错
        pass


def finalize(orch, session, resilient: bool = False) -> None:
    """幂等地写出全部产物、更新数据登记与 Handoff，并决定退出码。"""
    if orch.finalized:
        return
    if orch.run_dir is None:
        # 未创建 RUN 目录（仅收集、--allow-empty 或空选择）：不写产物，
        # 仅在 pytest 因"未收集到测试"返回 5 时归一化为框架约定的退出码。
        orch.finalized = True
        if session is not None and session.exitstatus in (0, 5):
            session.exitstatus = orch.exit_code
        return
    orch.finalized = True
    orch.finished_at = run_layout.now_iso()

    records = orch.ordered_records()
    records = [{key: value for key, value in rec.items() if key != "__final_record__"} for rec in records]
    bugs = bugs_review.collect_bugs(records)

    # 阶段一：执行完整性（不含产物存在性，产物此时尚未写出）。
    # dry_run / self_test 会由 check 直接返回原因，provisional 自然为 False。
    exec_reasons = list(integrity.check(orch, records)[1])
    provisional = not exec_reasons

    # 下列写出器闭包引用的 complete / reasons 采用后期绑定：
    # 先按阶段一结论写一遍，产物齐备性校验后再用最终结论重写一次。
    writers = (
        ("selection.yaml", lambda: selection.write(orch, records, bugs)),
        ("results.yaml", lambda: results.write_yaml(orch, records, bugs, complete, reasons)),
        ("results.json", lambda: results.write_json(orch, records, bugs, complete, reasons)),
        ("bugs_review.yaml", lambda: bugs_review.write(orch, records, bugs)),
        ("缺陷报告.md", lambda: defect_report.write(orch, records, bugs, complete, reasons)),
        ("case_results.xlsx", lambda: excel.write(orch, records, bugs, complete, reasons)),
        ("allure-results", lambda: allure_reporter.write(orch, records)),
        ("testcase.csv", lambda: csv_live.write_final(orch, records)),
    )
    complete, reasons = provisional, exec_reasons
    for name, writer in writers:
        try:
            writer()
        except Exception as exc:  # noqa: BLE001 - 单个产物失败不得拖累其他产物
            orch.note_writer_error(name, exc)
            if not resilient:
                raise

    # 阶段二：产物写出后补齐产物存在性校验；结论变化时重写承载完整性的产物。
    final_reasons = exec_reasons + integrity.check_artifacts(orch)
    complete = not final_reasons and not orch.writer_errors
    reasons = final_reasons
    if complete != provisional:
        for name, writer in (
            ("results.yaml", lambda: results.write_yaml(orch, records, bugs, complete, reasons)),
            ("results.json", lambda: results.write_json(orch, records, bugs, complete, reasons)),
            ("缺陷报告.md", lambda: defect_report.write(orch, records, bugs, complete, reasons)),
            ("case_results.xlsx", lambda: excel.write(orch, records, bugs, complete, reasons)),
        ):
            try:
                writer()
            except Exception as exc:  # noqa: BLE001
                orch.note_writer_error(f"{name}(重写)", exc)

    if orch.dry_run or orch.self_test:
        _safe(orch, "registry preview", lambda: registry_yaml.preview(orch, records))
        _safe(orch, "handoff preview", lambda: handoff.preview(orch, records, bugs, complete, reasons))
    else:
        if not orch.config.getoption("--no-update-registry"):
            _safe(orch, "registry yaml", lambda: registry_yaml.update(orch, records))
        if not orch.config.getoption("--no-handoff"):
            _safe(orch, "handoff", lambda: handoff.update(orch, records, bugs, complete, reasons))

    orch.exit_code = integrity.decide_exit_code(orch, records, complete)
    run_layout.write_status(
        orch.run_dir, integrity.status_payload(orch, records, complete, reasons)
    )
    if session is not None:
        session.exitstatus = orch.exit_code


def _safe(orch, name: str, action) -> None:
    """执行可失败动作并登记错误，不向外抛出。"""
    try:
        action()
    except Exception as exc:  # noqa: BLE001
        orch.note_writer_error(name, exc)


def pytest_sessionfinish(session, exitstatus) -> None:
    """主写点：写出全部产物并设置退出码。"""
    config = getattr(session, "config", None)
    if config is None or not hasattr(config, "stash"):
        return
    try:
        orch = get_orch(config)
    except KeyError:
        return
    finalize(orch, session, resilient=True)


def pytest_unconfigure(config) -> None:
    """无条件兜底：确保即使 sessionfinish 未触发也至少写出一次产物。"""
    try:
        orch = get_orch(config)
    except (KeyError, AttributeError):
        return
    if orch.finalized or orch.run_dir is None:
        return
    finalize(orch, None, resilient=True)


def pytest_terminal_summary(terminalreporter) -> None:
    """在终端输出一屏中文摘要，便于快速判断本次 RUN 是否可信。"""
    config = getattr(terminalreporter, "config", None)
    if config is None or not hasattr(config, "stash"):
        return
    try:
        orch = get_orch(config)
    except KeyError:
        return
    if orch.run_dir is None:
        terminalreporter.write_sep("=", "UI 自动化：本次未创建 RUN 目录（无匹配用例或仅收集）")
        return
    records = [
        {key: value for key, value in rec.items() if key != "__final_record__"}
        for rec in orch.ordered_records()
    ]
    counts: dict[str, int] = {}
    for record in records:
        status = str(record.get("status") or "unknown")
        counts[status] = counts.get(status, 0) + 1
    bugs = bugs_review.collect_bugs(records)
    complete, reasons = integrity.check(orch, records)
    terminalreporter.write_sep("=", "UI 自动化执行摘要")
    terminalreporter.write_line(f"run_id        : {orch.run_id}")
    terminalreporter.write_line(f"需求 / 模块   : {'、'.join(orch.req_ids)} / {'、'.join(orch.module_names)}")
    terminalreporter.write_line(f"计划 / 执行   : {len(orch.planned)} / {orch.executed_count()}")
    terminalreporter.write_line(f"结果统计      : {counts}")
    terminalreporter.write_line(f"产品缺陷      : {len(bugs)}（review_status=pending，未创建禅道 Bug）")
    terminalreporter.write_line(f"完整性        : {'完整' if complete else '⚠ 不完整：' + '；'.join(reasons)}")
    terminalreporter.write_line(f"产物目录      : {orch.run_dir}")
    if orch.writer_errors:
        terminalreporter.write_line(f"产物写出错误  : {orch.writer_errors}")
    if not complete:
        terminalreporter.write_line("提示：不完整的 RUN 不得作为最终交付报告；重跑必须使用新的 run_id。")

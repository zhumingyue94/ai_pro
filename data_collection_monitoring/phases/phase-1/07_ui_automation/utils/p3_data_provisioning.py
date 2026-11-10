"""P3 前置数据创建编排层。

只读解析 ``data/*.json`` 中的 precreatedData 契约，按方案清单逐条执行
「查询 → 复用/创建 → 回查 → 登记台账」，生成创建台账与 reporter 所需的结果文件。

约束：
- 不依赖 ``utils.test_data``（该文件当前为空，``pagination_precreated`` 导入会失败）；
- 不执行任何清理/删除，创建的数据保留在测试环境；
- 不伪造数据：页面无创建能力或契约字段不可设置时，真实探测后记 blocked。
"""

from __future__ import annotations

import importlib
import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
UI_ROOT = ROOT / "07_ui_automation"
DATA_DIR = UI_ROOT / "data"
PLAN_PATH = UI_ROOT / "P3_precreated_data_creation_plan.md"

# 方案第 3 节依赖顺序：分类 → 产品 → 设备 → 分组 → 目标/消息 → 告警规则 → 任务 → 告警配置
MODULE_ORDER: tuple[tuple[str, int, str, str, str], ...] = (
    ("REQ-002", 731, "产品分类", "req002_test_data.json", "pages.req002.product_category_page"),
    ("REQ-003", 732, "产品管理", "req003_test_data.json", "pages.req003.product_management_page"),
    ("REQ-005", 734, "设备管理", "req005_test_data.json", "pages.req005.device_management_page"),
    ("REQ-004", 733, "设备分组", "req004_test_data.json", "pages.req004.device_group_page"),
    ("REQ-008", 746, "数据推送", "req008_test_data.json", "pages.req008.data_push_page"),
    ("REQ-007", 745, "数据监听", "req007_test_data.json", "pages.req007.data_monitor_page"),
    ("REQ-009", 747, "数据采集", "req009_test_data.json", "pages.req009.data_crawl_page"),
    ("REQ-011", 749, "告警记录", "req011_test_data.json", "pages.req011.alert_record_page"),
)

META_KEYS = {
    "dataKey", "records", "minimumPages", "stableTotal",
    "recordsMustNotChangeDuringTest", "timeBoundary",
}
STATUS_LABELS = {"enabled": "开启", "disabled": "关闭"}
# 系统/后端/验收元数据字段，UI 表单无法设置
UNSETTABLE_HINTS = {
    "createdAt", "tenant", "taskId", "ruleId", "recordKey", "processed",
    "script", "restartPolicy", "memory", "pluginId", "deviceId",
    "conditions", "actions", "triggers", "parentDevice", "product",
    "moreConfig", "status", "protocol", "level", "alertConfig", "cron",
    "productKey", "serialNumber", "deviceKey",
}
# 指向外部实体/批准样本的字段，需先有依赖数据才能创建
DEPENDENCY_HINTS = {"categoryName", "productKey", "pluginId", "deviceId", "product", "script", "timeZone"}


def _external_dependencies(entry: PlanEntry) -> list[str]:
    found: list[str] = []
    for rec in entry.records:
        for key, value in rec.items():
            if key not in DEPENDENCY_HINTS or key in found:
                continue
            text = json.dumps(value, ensure_ascii=False) if isinstance(value, (dict, list)) else str(value)
            if "AUTO_REQ" in text or "approved-" in text:
                found.append(key)
    for key in ("productIcon", "productImage"):
        nested = entry.precreated.get("moreConfig") or {}
        if isinstance(nested, dict) and str(nested.get(key, "")).startswith("approved-"):
            if key not in found:
                found.append(key)
    return found
PURPOSE = "【P3前置数据创建】本轮仅创建/核对前置数据，未执行用例"


@dataclass(frozen=True)
class PlanEntry:
    req_id: str
    module_id: int
    module_name: str
    source: str
    case_id: str
    data_type: str
    data_key: str
    precreated: dict[str, Any]
    provisioning: dict[str, Any]
    page_module: str

    @property
    def records(self) -> list[dict[str, Any]]:
        raw = self.precreated.get("records")
        if isinstance(raw, list) and raw:
            return [dict(item) for item in raw if isinstance(item, dict)]
        return [{k: v for k, v in self.precreated.items() if k not in META_KEYS}]

    @property
    def business_fields(self) -> list[str]:
        fields = self.provisioning.get("businessFields")
        if isinstance(fields, list) and fields:
            return [str(v) for v in fields]
        return sorted({k for rec in self.records for k in rec})


@dataclass
class LedgerEntry:
    data_key: str
    source: str
    case_id: str
    req_id: str
    module_id: int
    data_type: str = ""
    status: str = "blocked"  # created | reused | blocked
    result: str = "blocked"  # passed | blocked
    record_ids: list[str] = field(default_factory=list)
    tenant: str = ""
    created_at: str = ""
    readback: str = "not_run"
    blocked_reason: str = "尚未执行"
    evidence: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "data_key": self.data_key,
            "source": self.source,
            "case_id": self.case_id,
            "req_id": self.req_id,
            "module_id": self.module_id,
            "data_type": self.data_type,
            "status": self.status,
            "result": self.result,
            "record_ids": list(self.record_ids),
            "tenant": self.tenant,
            "created_at": self.created_at,
            "readback": self.readback,
            "blocked_reason": self.blocked_reason,
            "evidence": list(self.evidence),
            "notes": list(self.notes),
        }


def _norm(value: Any) -> str:
    """归一化列表/契约文本：忽略空白、Element UI 换行占位符与分隔符差异。"""
    return re.sub(r"[\s/／|]+", "", str(value or ""))


def _safe_key(value: str) -> str:
    return re.sub(r"[^\w.-]", "-", value)


def load_plan_entries() -> list[PlanEntry]:
    """从方案文档取 35 条清单，从 ``data/*.json`` 取完整契约。"""
    text = PLAN_PATH.read_text(encoding="utf-8-sig")
    plan_rows: list[tuple[str, str, str, str]] = []
    heading = ""
    for line in text.splitlines():
        match = re.match(r"^###\s+\d+\.\s+`([^`]+)`", line)
        if match:
            heading = match.group(1)
            continue
        source = re.match(
            r"^- 来源：`([^`]+)`；用例：`([^`]+)`；数据类型：`([^`]+)`", line
        )
        if source and heading:
            plan_rows.append((heading, source.group(1), source.group(2), source.group(3)))
            heading = ""

    cache: dict[str, list[dict[str, Any]]] = {}

    def cases_for(filename: str) -> list[dict[str, Any]]:
        if filename not in cache:
            cache[filename] = json.loads((DATA_DIR / filename).read_text(encoding="utf-8-sig"))
        return cache[filename]

    meta = {req: (mid, name, page) for req, mid, name, _src, page in MODULE_ORDER}
    entries: list[PlanEntry] = []
    for data_key, source, case_id, data_type in plan_rows:
        req_id = next(
            (req for req, _mid, _name, src, _page in MODULE_ORDER if src == source),
            "",
        )
        if not req_id:
            raise ValueError(f"方案条目来源文件未映射到模块：{source}")
        contract: dict[str, Any] | None = None
        provisioning: dict[str, Any] = {}
        for case in cases_for(source):
            if case.get("caseId") != case_id:
                continue
            for td in case.get("testData", []):
                data = td.get("data") or {}
                pc = data.get("precreatedData")
                if isinstance(pc, dict) and pc.get("dataKey") == data_key:
                    contract = pc
                    provisioning = data.get("provisioning") or {}
                    break
            if contract is not None:
                break
        if contract is None:
            raise ValueError(f"数据契约缺失：{source} / {case_id} / {data_key}")
        module_id, module_name, page_module = meta[req_id]
        entries.append(PlanEntry(
            req_id=req_id, module_id=module_id, module_name=module_name,
            source=source, case_id=case_id, data_type=data_type,
            data_key=data_key, precreated=contract, provisioning=provisioning,
            page_module=page_module,
        ))
    return entries


def order_modules(entries: list[PlanEntry]) -> list[tuple[str, int, str, list[PlanEntry]]]:
    ordered: list[tuple[str, int, str, list[PlanEntry]]] = []
    for req_id, module_id, module_name, _src, _page in MODULE_ORDER:
        group = [e for e in entries if e.req_id == req_id]
        if group:
            ordered.append((req_id, module_id, module_name, group))
    return ordered


def new_ledger(entries: list[PlanEntry]) -> list[LedgerEntry]:
    return [LedgerEntry(
        data_key=e.data_key, source=e.source, case_id=e.case_id,
        req_id=e.req_id, module_id=e.module_id, data_type=e.data_type,
    ) for e in entries]


def mark_blocked(entries: list[LedgerEntry], reason: str, *, scope: str | None = None) -> None:
    for item in entries:
        if scope and item.req_id != scope:
            continue
        item.status = "blocked"
        item.result = "blocked"
        item.readback = "not_run"
        item.blocked_reason = reason


class Session:
    """持有单个有头浏览器会话，负责页面侦察、截图与证据登记。"""

    def __init__(self, page: Any, settings: Any, evidence_dir: Path) -> None:
        self.page = page
        self.settings = settings
        self.evidence_dir = evidence_dir
        self.evidence_dir.mkdir(parents=True, exist_ok=True)
        self.modules: dict[str, Any] = {}
        self.last_query_error = ""

    def module(self, path: str) -> Any:
        if path not in self.modules:
            self.modules[path] = importlib.import_module(path)
        return self.modules[path]

    def shot(self, case_id: str, tag: str) -> str:
        target = self.evidence_dir / f"{case_id}__{_safe_key(tag)}.png"
        try:
            self.page.screenshot(path=str(target), full_page=True, timeout=15_000)
            return str(target)
        except Exception:  # noqa: BLE001 - 截图失败不影响数据创建结论
            return ""

    def visible_buttons(self) -> list[str]:
        try:
            return [t.strip() for t in self.page.get_by_role("button").all_inner_texts() if t.strip()]
        except Exception:  # noqa: BLE001
            return []

    def dialog_fields(self) -> list[str]:
        """只读收集可见弹窗内的输入控件标签/占位符。"""
        dialog = self.page.locator(".el-dialog:visible, .el-drawer:visible").first
        if not dialog.count():
            return []
        labels: list[str] = []
        try:
            for i in range(dialog.locator(".el-form-item__label").count()):
                text = dialog.locator(".el-form-item__label").nth(i).inner_text().strip()
                if text:
                    labels.append(text)
        except Exception:  # noqa: BLE001
            pass
        try:
            for i in range(dialog.locator("input, textarea").count()):
                node = dialog.locator("input, textarea").nth(i)
                placeholder = (node.get_attribute("placeholder") or "").strip()
                readonly = node.get_attribute("readonly") is not None
                disabled = node.is_disabled()
                labels.append(f"{placeholder or '(无占位符)'}{'[只读]' if readonly else ''}{'[禁用]' if disabled else ''}")
        except Exception:  # noqa: BLE001
            pass
        return labels

    def open_page(self, page_module: str) -> None:
        mod = self.module(page_module)
        mod.open_page(self.page, self.settings)

    def query_by_name(self, page_module: str, name: str) -> list[list[str]]:
        mod = self.module(page_module)
        self.last_query_error = ""
        try:
            if page_module.endswith("req002.product_category_page"):
                mod.query(self.page, name)
            elif page_module.endswith("req003.product_management_page"):
                mod.query(self.page, name=name)
            elif hasattr(mod, "name_filter"):
                mod.name_filter(self.page).fill(name)
                mod.query(self.page)
            else:
                # REQ-011 无名称筛选，退回全表扫描
                return [list(row) for row in mod.row_values(self.page)]
            return [list(row) for row in mod.row_values(self.page)]
        except Exception as exc:  # noqa: BLE001
            self.last_query_error = f"{type(exc).__name__}: {exc}"
            try:
                return [list(row) for row in mod.row_values(self.page)]
            except Exception:  # noqa: BLE001
                return []

    def find_records(self, page_module: str, record: dict[str, Any]) -> list[list[str]]:
        """按名称查询；特殊字符名称查询为空时回退到前缀查询并本地过滤。"""
        name = str(record.get("name") or record.get("recordKey") or "")
        rows = self.query_by_name(page_module, name)
        first_error = self.last_query_error
        if any(_row_matches(row, record) for row in rows):
            return [row for row in rows if _row_matches(row, record)]
        prefix_match = re.match(r"^(AUTO_REQ\d{3}(?:_[A-Z]+){0,2})", name)
        if prefix_match and prefix_match.group(1) != name:
            fallback = self.query_by_name(page_module, prefix_match.group(1))
            hits = [row for row in fallback if _row_matches(row, record)]
            if hits:
                return hits
        self.last_query_error = first_error or self.last_query_error
        return []

    def tenant(self) -> str:
        try:
            return str(getattr(self.settings, "tenant", "") or "")
        except Exception:  # noqa: BLE001
            return ""


def _row_matches(row: list[str], record: dict[str, Any]) -> bool:
    """按名称 + 描述判定列表行是否命中契约记录（状态/排序不可由列表稳定核对）。"""
    name = str(record.get("name") or record.get("recordKey") or "")
    if not name or not row:
        return False
    joined = _norm("|".join(row))
    if _norm(name) not in joined:
        return False
    description = record.get("description")
    if description is None:
        return True
    if _norm(description) == "":
        return True  # 空描述页面可能显示 "-"/占位符
    return _norm(description) in joined


def _record_id(row: list[str]) -> str:
    return row[0].strip() if row else ""


def _unsettable_fields(entry: PlanEntry) -> list[str]:
    found: list[str] = []
    for rec in entry.records:
        for key in rec:
            if key in UNSETTABLE_HINTS and key not in found:
                found.append(key)
    for key in ("minimumPages", "stableTotal", "recordsMustNotChangeDuringTest", "timeBoundary"):
        if key in entry.precreated and key not in found:
            found.append(key)
    return found


def _ok(item: LedgerEntry, session: Session, status: str, reason: str) -> None:
    item.status = status
    item.result = "passed"
    item.readback = "passed"
    item.created_at = datetime.now(timezone.utc).isoformat()
    item.tenant = session.tenant()
    item.blocked_reason = ""
    item.notes.append(reason)


def _block(item: LedgerEntry, session: Session, reason: str) -> None:
    item.status = "blocked"
    item.result = "blocked"
    item.readback = "not_run"
    item.created_at = datetime.now(timezone.utc).isoformat()
    item.tenant = session.tenant()
    item.blocked_reason = reason


def _add_shot(item: LedgerEntry, path: str) -> None:
    if path and path not in item.evidence:
        item.evidence.append(path)


STATUS_SYNONYMS = {
    "enabled": ("开启", "启用", "正常"),
    "disabled": ("关闭", "停用", "禁用"),
}


def _req002_status_labels(session: Session, mod: Any) -> list[str]:
    """只读打开一次新增弹窗，侦察页面实际状态单选标签（不提交、不写入）。"""
    cached = getattr(session, "status_labels", None)
    if cached is not None:
        return cached  # type: ignore[return-value]
    labels: list[str] = []
    try:
        dialog = mod.open_add_dialog(session.page)
        radios = dialog.locator(".el-radio")
        labels = [radios.nth(i).inner_text().strip() for i in range(radios.count())]
        mod.cancel_dialog(session.page, dialog)
    except Exception:  # noqa: BLE001
        labels = []
    session.status_labels = labels  # type: ignore[attr-defined]
    return labels


def _status_label(value: str, labels: list[str]) -> str:
    preferred = STATUS_LABELS.get(value, "开启")
    if not labels or preferred in labels:
        return preferred
    for synonym in STATUS_SYNONYMS.get(value, (preferred,)):
        if synonym in labels:
            return synonym
    return preferred


def _provision_req002(session: Session, entry: PlanEntry, item: LedgerEntry) -> None:
    """REQ-002：页面对象具备完整 create_category 封装，真实创建/复用并回查。"""
    mod = session.module(entry.page_module)
    if entry.provisioning.get("whenMissing") != "auto_create":
        _block(item, session, f"provisioning.whenMissing={entry.provisioning.get('whenMissing')}，非 auto_create，未获自动创建授权")
        return
    created = 0
    reused = 0
    status_labels = _req002_status_labels(session, mod)
    if status_labels:
        item.notes.append(f"页面状态单选真实标签：{', '.join(status_labels)}")
    for record in entry.records:
        name = str(record.get("name", ""))
        if not name:
            _block(item, session, "契约记录缺少 name，无法按业务字段定位")
            return
        matched = session.find_records(entry.page_module, record)
        if matched:
            reused += 1
            item.record_ids.append(_record_id(matched[0]))
            item.notes.append(f"{name}：查询命中，复用已存在记录")
            _add_shot(item, session.shot(entry.case_id, f"{entry.data_key}-reused-{_safe_key(name)}"))
            continue
        if session.last_query_error:
            item.notes.append(f"{name}：查询控件异常 {session.last_query_error}")
        if entry.provisioning.get("onCreateFailure") == "blocked" and session.last_query_error:
            _add_shot(item, session.shot(entry.case_id, f"{entry.data_key}-query-error"))
            _block(item, session, f"{name}：无法确认记录是否已存在（查询控件异常），按 onCreateFailure=blocked 不重复创建")
            return
        try:
            toast = mod.create_category(
                session.page,
                name=name,
                sort=str(record.get("sort", "")),
                description=str(record.get("description", "") or ""),
                status=_status_label(str(record.get("status", "enabled")), status_labels),
            )
        except Exception as exc:  # noqa: BLE001
            _add_shot(item, session.shot(entry.case_id, f"{entry.data_key}-create-failed"))
            _block(item, session, f"{name}：新增提交失败或被表单校验拦截：{type(exc).__name__}: {exc}")
            return
        matched = session.find_records(entry.page_module, record)
        if not matched:
            _add_shot(item, session.shot(entry.case_id, f"{entry.data_key}-readback-failed"))
            query_note = f"；查询控件异常：{session.last_query_error}" if session.last_query_error else ""
            _block(item, session, f"{name}：新增后回查未命中（提示={toast}{query_note}），不判定数据已就绪")
            return
        created += 1
        item.record_ids.append(_record_id(matched[0]))
        item.notes.append(f"{name}：新增成功并回查通过，提示={toast}")
        _add_shot(item, session.shot(entry.case_id, f"{entry.data_key}-created-{_safe_key(name)}"))
    item.readback = "passed"
    status = "created" if created and not reused else "reused" if reused and not created else "mixed_created_reused"
    _ok(item, session, status, f"共 {len(entry.records)} 条记录：新增 {created}、复用 {reused}；数据保留不清理")


def _probe_create_dialog(session: Session, entry: PlanEntry, item: LedgerEntry) -> tuple[bool, list[str], list[str]]:
    """真实打开新增表单做只读侦察，不提交任何写入。返回 (有无新增入口, 字段清单, 按钮清单)。"""
    mod = session.module(entry.page_module)
    buttons = session.visible_buttons()
    has_entry = any("新增" in b for b in buttons)
    fields: list[str] = []
    opener = getattr(mod, "open_create", None)
    if opener is None and hasattr(mod, "toolbar"):
        # REQ-003 无 open_create 封装，用 toolbar 的「新增」真实打开表单做只读侦察
        def opener(page: Any) -> None:  # noqa: ANN401
            mod.toolbar(page, "新增").click()
            page.locator(".el-dialog:visible, .el-drawer:visible").first.wait_for(state="visible", timeout=8_000)

    if opener is None and has_entry:
        # 页面对象无新增封装时，按可见新增按钮真实点击一次（只侦察，不提交）
        def opener(page: Any) -> None:  # noqa: ANN401
            page.get_by_role("button", name=re.compile(r"新\s*增")).first.click(timeout=8_000)
            page.locator(".el-dialog:visible, .el-drawer:visible").first.wait_for(state="visible", timeout=8_000)

    if callable(opener):
        try:
            opener(session.page)
            fields = session.dialog_fields()
            _add_shot(item, session.shot(entry.case_id, f"{entry.data_key}-dialog-probe"))
        except Exception as exc:  # noqa: BLE001
            item.notes.append(f"真实尝试打开新增表单失败：{type(exc).__name__}: {exc}")
        finally:
            cancel = getattr(mod, "cancel", None) or getattr(mod, "cancel_dialog", None)
            if callable(cancel):
                try:
                    cancel(session.page)
                except Exception:  # noqa: BLE001
                    pass
            else:
                try:
                    session.page.keyboard.press("Escape")
                except Exception:  # noqa: BLE001
                    pass
    return has_entry, fields, buttons


def _provision_blocked_module(session: Session, entry: PlanEntry, item: LedgerEntry) -> None:
    """其余模块：先按名称查询复用；未命中则真实探测新增能力后逐条记 blocked。"""
    hits: list[list[str]] = []
    query_note = ""
    for rec in entry.records:
        found = session.find_records(entry.page_module, rec)
        if session.last_query_error:
            query_note = f"；查询控件异常：{session.last_query_error}"
        if not found:
            hits = []
            break
        hits.extend(found)
    if hits:
        item.readback = "passed"
        item.record_ids = [_record_id(row) for row in hits]
        _ok(item, session, "reused", f"查询命中已存在数据（{len(hits)} 行），按业务字段复用，未发生业务写入")
        _add_shot(item, session.shot(entry.case_id, f"{entry.data_key}-reused"))
        return

    _add_shot(item, session.shot(entry.case_id, f"{entry.data_key}-page"))
    has_entry, fields, buttons = _probe_create_dialog(session, entry, item)
    unsettable = _unsettable_fields(entry)
    dependencies = _external_dependencies(entry)
    when_missing = entry.provisioning.get("whenMissing")
    reasons = [
        f"whenMissing={when_missing}；按 businessFields "
        f"({', '.join(entry.business_fields) or '无'}) 查询未命中{query_note}，无可复用的已存在记录",
        f"契约含 UI 表单不可设置字段：{', '.join(unsettable) if unsettable else '无'}",
    ]
    if dependencies:
        reasons.append(
            f"缺少外部依赖/批准样本：{', '.join(dependencies)}"
            "（引用 AUTO_REQ* 实体或 approved-* 图片文件，工作区未提供且环境未确认存在）"
        )
    if not has_entry:
        reasons.append(f"页面无新增入口（可见按钮：{', '.join(buttons[:12]) or '未读取到'}）")
    else:
        field_text = ", ".join(fields[:14]) or "未读取到"
        if entry.req_id == "REQ-003":
            reasons.append(
                "页面对象虽具备新增产品能力（create_product），但契约要求指定 productKey、"
                "moreConfig 图标/图片与引用的产品分类；ProductKey 由系统自动生成且现有封装只读回读，"
                "approved-icon.png/approved-image.png 在工作区不存在，故无法按契约字段完整创建；"
                f"真实探测到的表单字段：{field_text}；按不伪造口径不提交字段不完整的业务数据"
            )
        else:
            reasons.append(
                "页面存在新增入口，但现有页面对象无完整字段级创建/提交封装，"
                f"真实探测到的表单字段为：{field_text}；"
                "按不伪造口径不提交字段不完整的业务数据"
            )
    _block(item, session, "；".join(reasons))
    item.notes.append(f"{PURPOSE}；dataKey={entry.data_key}")


def provision_module(session: Session, req_id: str, group: list[PlanEntry], ledger: list[LedgerEntry]) -> None:
    by_case = {item.case_id: item for item in ledger}
    session.open_page(group[0].page_module)
    for entry in group:
        item = by_case[entry.case_id]
        try:
            if req_id == "REQ-002":
                _provision_req002(session, entry, item)
            else:
                _provision_blocked_module(session, entry, item)
        except Exception as exc:  # noqa: BLE001 - 单条异常不影响后续条目
            _add_shot(item, session.shot(entry.case_id, f"{entry.data_key}-exception"))
            _block(item, session, f"该条前置数据处理异常：{type(exc).__name__}: {exc}")


def merge_prior_created(path: Path, ledger: list[LedgerEntry]) -> dict[str, Any]:
    """合并上一轮台账中已真实创建的记录事实（数据保留不清理，本轮按业务字段复用）。

    仅用于重跑场景：首轮因编排层异常把「创建成功并回查通过」误记为 blocked，
    但业务数据确实已在测试环境创建并保留。
    """
    if not path.is_file():
        return {}
    try:
        previous = yaml.safe_load(path.read_text(encoding="utf-8-sig")) or {}
    except Exception:  # noqa: BLE001
        return {}
    created: dict[str, dict[str, Any]] = {}
    for old in previous.get("entries", []) or []:
        notes = [str(n) for n in (old.get("notes") or [])]
        ids = [str(i) for i in (old.get("record_ids") or []) if str(i)]
        if ids and any("新增成功并回查通过" in n for n in notes):
            created[str(old.get("data_key"))] = {
                "case_id": old.get("case_id"),
                "record_ids": ids,
                "created_at": old.get("created_at"),
                "evidence": [str(e) for e in (old.get("evidence") or []) if str(e)],
                "notes": notes,
            }
    for item in ledger:
        prior = created.get(item.data_key)
        if not prior:
            continue
        item.notes.append(
            "首轮真实创建并回查通过 "
            f"({len(prior['record_ids'])} 条记录，ID={', '.join(prior['record_ids'])})；"
            "数据按要求保留不清理，本轮按业务字段复用核对"
        )
        for rid in prior["record_ids"]:
            if rid not in item.record_ids:
                item.record_ids.append(rid)
        for evidence in prior["evidence"]:
            _add_shot(item, evidence)
        if item.status == "reused" and item.result == "passed":
            item.status = "created_then_reused"
    return created


def write_ledger(path: Path, ledger: list[LedgerEntry], *, environment: dict[str, Any]) -> None:
    summary = {"total": len(ledger), "passed": 0, "blocked": 0, "created": 0, "reused": 0}
    for item in ledger:
        summary[item.result] = summary.get(item.result, 0) + 1
        if item.status in ("created", "mixed_created_reused", "created_then_reused"):
            summary["created"] += 1
        elif item.status == "reused":
            summary["reused"] += 1
    payload = {
        "purpose": PURPOSE,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "environment": environment,
        "data_retention": "保留不清理；方案文档第 5 步 cleanupCreatedRecord 条款本轮不执行",
        "summary": summary,
        "entries": [item.to_dict() for item in ledger],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(payload, allow_unicode=True, sort_keys=False), encoding="utf-8")


def write_results_files(directory: Path, ledger: list[LedgerEntry], ordered: list[tuple[str, int, str, list[PlanEntry]]]) -> dict[str, Path]:
    by_case = {item.case_id: item for item in ledger}
    directory.mkdir(parents=True, exist_ok=True)
    paths: dict[str, Path] = {}
    for req_id, _module_id, _module_name, group in ordered:
        cases: list[dict[str, Any]] = []
        for entry in group:
            item = by_case[entry.case_id]
            if item.result == "passed":
                detail = "；".join(item.notes) or "前置数据已就绪"
                reason = f"{PURPOSE}；dataKey={entry.data_key}；status={item.status}；{detail}"
            else:
                reason = f"{PURPOSE}；dataKey={entry.data_key}；blocked：{item.blocked_reason}"
            cases.append({
                "case_id": entry.case_id,
                "result": item.result,
                "reason": reason,
                "evidence": {},
            })
        target = directory / f"{req_id}.yaml"
        target.write_text(
            yaml.safe_dump({"cases": cases}, allow_unicode=True, sort_keys=False),
            encoding="utf-8",
        )
        paths[req_id] = target
    return paths

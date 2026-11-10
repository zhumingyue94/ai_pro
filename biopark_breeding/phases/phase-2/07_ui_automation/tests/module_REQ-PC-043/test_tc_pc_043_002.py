"""TC-PC-043-002：查看有效上孵计划时展示计划字段和出雏结果。"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest
from playwright.sync_api import Page

ROOT = Path(__file__).resolve().parents[3]
AUTOMATION_ROOT = ROOT / "07_ui_automation"
if str(AUTOMATION_ROOT) not in sys.path:
    sys.path.insert(0, str(AUTOMATION_ROOT))

from config.settings import ConfigurationError, load_settings
from pages.common.chick_delivery_page import ChickDeliveryPage
from pages.common.portal_navigation import PortalNavigation


def _load_page_object(filename: str, module_name: str):
    path = AUTOMATION_ROOT / "pages" / "module_REQ-PC-043" / filename
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"无法加载页面对象：{path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


_plan_module = _load_page_object("incubation_plan_page.py", "req_pc_043_incubation_plan_page")
_delivery_module = _load_page_object("delivery_list_page.py", "req_pc_043_delivery_list_page")
_detail_module = _load_page_object("delivery_detail_page.py", "req_pc_043_delivery_detail_page")
IncubationPlanPage = _plan_module.IncubationPlanPage
DeliveryListPage = _delivery_module.DeliveryListPage
DeliveryDetailPage = _detail_module.DeliveryDetailPage


@pytest.mark.req_pc_043
@pytest.mark.case_id("TC-PC-043-002")
def test_tc_pc_043_002(page: Page) -> None:
    """复用公共持久化登录态后执行完整业务核对。"""
    try:
        settings = load_settings(ROOT, headless=False)
    except ConfigurationError as exc:
        pytest.skip(f"blocked: {exc}")

    app_page = PortalNavigation(page, settings).open_portal_app()
    navigation = PortalNavigation(app_page, settings)
    navigation.open_plan_menu_item("上孵计划")
    plan_page = IncubationPlanPage(app_page)
    baseline = plan_page.discover_baseline()

    ChickDeliveryPage(app_page).open_and_set_recent_half_year(navigation)
    delivery_list = DeliveryListPage(app_page)
    detail_page = delivery_list.find_and_open_detail(baseline)
    DeliveryDetailPage(detail_page).assert_baseline(baseline)

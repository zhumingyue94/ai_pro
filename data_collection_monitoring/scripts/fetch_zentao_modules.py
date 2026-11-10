"""通过 Playwright 登录禅道并读取目标项目产品的模块树。

项目根目录由 ``--project`` 指定，项目名称、产品名称、产品 ID 和项目 ID
均从该项目的 ``config.yaml`` 读取。脚本不会在源码中写入具体业务值。

凭据只从环境变量 ``ZENTAO_URL``、``ZENTAO_ACCOUNT``、
``ZENTAO_PASSWORD`` 读取；浏览器始终以可视模式运行。
"""

from __future__ import annotations

import argparse
import html as html_module
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml
from playwright.sync_api import TimeoutError as PWTimeoutError
from playwright.sync_api import sync_playwright


DEFAULT_TIMEOUT = 30_000


def _load_project_config(root: Path) -> dict[str, Any]:
    """读取项目名称、产品名称和禅道 ID，并拒绝未确认的占位配置。"""
    path = root / "config.yaml"
    if not path.is_file():
        raise ValueError(f"missing project config: {path}")
    config = yaml.safe_load(path.read_text(encoding="utf-8-sig")) or {}
    project = config.get("project") or {}
    project_name = str(project.get("name") or "").strip()
    product_name = str(config.get("zentao_product_name") or "").strip()
    product_id = config.get("zentao_product_id")
    project_id = config.get("zentao_project_id")
    if not project_name or project_name.startswith("<"):
        raise ValueError("project.name is not confirmed in config.yaml")
    if not product_name or product_name in {"待确认", "<product_name>"}:
        raise ValueError("zentao_product_name is not confirmed in config.yaml")
    if not isinstance(product_id, int) or product_id <= 0:
        raise ValueError("zentao_product_id must be a confirmed positive integer")
    if not isinstance(project_id, int) or project_id <= 0:
        raise ValueError("zentao_project_id must be a confirmed positive integer")
    return {
        "project_name": project_name,
        "product_name": product_name,
        "product_id": product_id,
        "project_id": project_id,
    }


def _read_env() -> tuple[str, str, str] | None:
    """从环境变量读取禅道连接配置，不保存凭据内容。"""
    required = ("ZENTAO_URL", "ZENTAO_ACCOUNT", "ZENTAO_PASSWORD")
    missing = [name for name in required if not os.environ.get(name, "").strip()]
    if missing:
        print(f"status=blocked reason=missing_env variables={','.join(missing)}")
        return None
    return os.environ["ZENTAO_URL"], os.environ["ZENTAO_ACCOUNT"], os.environ["ZENTAO_PASSWORD"]


def _product_frame(page):
    """获取禅道产品应用 iframe。"""
    return page.frame_locator("#appIframe-product, iframe[name='app-product']").first


def step1_login(page, url: str, account: str, password: str) -> bool:
    """登录禅道并确认页面已离开登录页。"""
    print("步骤 1：登录禅道")
    page.goto(url, wait_until="domcontentloaded", timeout=DEFAULT_TIMEOUT)
    try:
        page.wait_for_load_state("networkidle", timeout=DEFAULT_TIMEOUT)
    except PWTimeoutError:
        pass
    if "login" in page.url.lower():
        account_input = page.locator("input[type='text'], input[name='account'], input[name='username']").first
        password_input = page.locator("input[type='password']").first
        account_input.fill(account)
        password_input.fill(password)
        page.locator("button:has-text('登录'), button[type='submit'], input[type='submit']").first.click()
        try:
            page.wait_for_load_state("networkidle", timeout=DEFAULT_TIMEOUT)
        except PWTimeoutError:
            pass
        page.wait_for_timeout(1000)
        if "login" in page.url.lower():
            print("  login_failed")
            return False
    print("  login_ok")
    return True


def step2_click_product_menu(page) -> None:
    """进入禅道产品菜单。"""
    print("步骤 2：点击左侧产品菜单")
    page.locator('#menuMainNav a[data-app="product"]').wait_for(state="visible", timeout=DEFAULT_TIMEOUT)
    page.locator('#menuMainNav a[data-app="product"]').click()
    page.wait_for_timeout(2000)


def step3_click_top_product(page, frame) -> None:
    """回到产品列表。"""
    print("步骤 3：回到产品列表")
    selectors = ["a[href*='product&f=all']", "a[href*='product-all']", "a:has-text('产品')"]
    for selector in selectors:
        try:
            link = frame.locator(selector).first
            if link.is_visible(timeout=3000):
                link.click()
                page.wait_for_timeout(2000)
                return
        except Exception:
            continue
    print("  ! 未找到产品列表入口，继续使用当前页面")


def step4_click_product(page, frame, product_name: str, product_id: int) -> bool:
    """从产品列表进入配置指定的产品。"""
    print(f"步骤 4：进入配置产品（ID={product_id}）")
    selectors = [
        f'a[href*="productID={product_id}"]',
        f'a[href*="product-{product_id}"]',
        f'a:has-text("{product_name}")',
    ]
    for selector in selectors:
        try:
            link = frame.locator(selector).first
            if link.is_visible(timeout=5000):
                link.click()
                page.wait_for_timeout(3000)
                print("  product_page_ok")
                return True
        except Exception:
            continue
    print("  product_not_found")
    return False


def step5_click_rd_stories(page, frame) -> bool:
    """进入研发需求页面。"""
    print("步骤 5：进入研发需求")
    selectors = [
        'a:has-text("研发需求")',
        'a:has-text("需求")',
        'a[href*="product&f=browse"]',
        'a[href*="story"]',
        'li:has-text("需求") a',
    ]
    for selector in selectors:
        try:
            link = frame.locator(selector).first
            if link.is_visible(timeout=5000):
                link.click()
                page.wait_for_timeout(3000)
                print("  rd_story_page_ok")
                return True
        except Exception:
            continue
    print("  rd_story_page_not_found")
    return False


def step6_read_module_tree(page, frame, debug_html: Path | None = None) -> list[dict[str, str]]:
    """读取研发需求页面模块树并返回模块 ID、名称和层级路径。"""
    print("步骤 6：读取模块树")
    try:
        toggles = frame.locator(".tree .tree-toggle, .tree .collapsed, .tree-item .caret, .tree .icon-expand, .tree .expand")
        for index in range(toggles.count()):
            try:
                toggles.nth(index).click(timeout=2000)
                page.wait_for_timeout(100)
            except Exception:
                pass
        page.wait_for_timeout(1000)
    except Exception:
        pass

    body_html = frame.locator("body").inner_html(timeout=5000)
    if debug_html is not None:
        debug_html.parent.mkdir(parents=True, exist_ok=True)
        debug_html.write_text(body_html, encoding="utf-8")
    modules = _parse_modules_from_html(body_html)
    print(f"  modules_fetched={len(modules)}")
    return modules


def _parse_modules_from_html(body_html: str) -> list[dict[str, str]]:
    """解析禅道模块树 JSON，失败时回退到链接解析。"""
    if not body_html:
        return []
    match = re.search(r'zui-create-tree="([^"]*)"', body_html)
    if not match:
        return _parse_modules_from_links(body_html)
    try:
        tree_data = json.loads(html_module.unescape(match.group(1)))
    except json.JSONDecodeError:
        return _parse_modules_from_links(body_html)
    modules: list[dict[str, str]] = []
    _walk_tree(tree_data.get("items", []), [], [], modules)
    return modules


def _walk_tree(items: list[dict[str, Any]], paths: list[str], ids: list[str], modules: list[dict[str, str]]) -> None:
    """递归遍历模块树。"""
    for item in items:
        module_id = str(item.get("key", ""))
        name = str(item.get("text", "")).strip()
        children = item.get("items", []) or []
        if not name or module_id == "0":
            _walk_tree(children, paths, ids, modules)
            continue
        parent_id = ids[-1] if ids else "页面未提供"
        paths.append(name)
        ids.append(module_id)
        modules.append({"name": name, "id": module_id, "path": " / ".join(paths), "parent_id": parent_id})
        _walk_tree(children, paths, ids, modules)
        paths.pop()
        ids.pop()


def _parse_modules_from_links(body_html: str) -> list[dict[str, str]]:
    """从模块链接中回退解析模块 ID。"""
    modules: list[dict[str, str]] = []
    seen: set[str] = set()
    pattern = re.compile(r'<a\s+class="item-title"[^>]*href="([^"]*param=(\d+)[^"]*)"[^>]*>([^<]+)</a>', re.IGNORECASE)
    for match in pattern.finditer(body_html):
        module_id = match.group(2)
        name = match.group(3).strip()
        if name and module_id != "0" and module_id not in seen:
            seen.add(module_id)
            modules.append({"name": name, "id": module_id, "path": name, "parent_id": "页面未提供"})
    return modules


def _write_output(root: Path, metadata: dict[str, Any], modules: list[dict[str, str]], source_page: str) -> Path:
    """将模块树写入目标项目的 01_requirements/禅道模块id.md。"""
    output = root / "01_requirements" / "禅道模块id.md"
    output.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        "# 禅道产品模块树",
        "",
        f"**查询时间**：{now}",
        f"**项目名称**：{metadata['project_name']}",
        f"**项目 ID**：{metadata['project_id']}",
        f"**产品名称**：{metadata['product_name']}",
        f"**产品 ID**：{metadata['product_id']}",
        f"**来源页面**：{source_page}",
        "",
        "## 模块树表格",
        "",
        "| 模块路径 | 模块名称 | 模块 ID | 父模块 ID |",
        "|---|---|---:|---|",
    ]
    pending: list[str] = []
    if modules:
        for module in modules:
            module_id = module.get("id") or "页面未提供"
            lines.append(f"| {module.get('path', '')} | {module.get('name', '')} | {module_id} | {module.get('parent_id', '页面未提供')} |")
    else:
        lines.append("| （产品尚未创建模块，模块树为空） | - | - | - |")
        pending.append("模块树为空：产品当前未定义任何模块")
    lines.extend(["", "## 未读取或待确认节点", ""])
    lines.extend(f"- {item}" for item in pending) if pending else lines.append("- 无")
    lines.extend([
        "",
        "## 敏感信息保护说明",
        "",
        "- 本文件不包含账号、密码、Token、Cookie 或登录状态内容。",
        "- 禅道凭据通过环境变量读取，未写入本文件。",
        "- 获取脚本：`../../scripts/fetch_zentao_modules.py --project .`",
        "",
    ])
    output.write_text("\n".join(lines), encoding="utf-8")
    print(f"输出文件：{output}")
    return output


def main(argv: list[str] | None = None) -> int:
    """读取项目配置后，以可视浏览器获取模块树。"""
    parser = argparse.ArgumentParser(description="读取已配置项目的禅道模块树。")
    parser.add_argument("--project", type=Path, default=Path.cwd(), help="项目根目录，默认当前目录")
    parser.add_argument("--timeout-ms", type=int, default=DEFAULT_TIMEOUT)
    parser.add_argument("--debug-html", type=Path, help="可选调试 HTML 路径；任务结束后需手动清理")
    args = parser.parse_args(argv)
    root = args.project.resolve()
    try:
        metadata = _load_project_config(root)
    except ValueError as exc:
        print(f"status=blocked reason={exc}")
        return 2
    env = _read_env()
    if env is None:
        return 2
    url, account, password = env
    debug_html = args.debug_html
    if debug_html is not None and not debug_html.is_absolute():
        debug_html = root / debug_html

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.set_default_timeout(args.timeout_ms)
        try:
            if not step1_login(page, url, account, password):
                return 2
            step2_click_product_menu(page)
            frame = _product_frame(page)
            step3_click_top_product(page, frame)
            if not step4_click_product(page, frame, metadata["product_name"], metadata["product_id"]):
                return 1
            if not step5_click_rd_stories(page, frame):
                return 1
            modules = step6_read_module_tree(page, frame, debug_html)
            source = f"{url.rstrip('/')}/index.php?m=product&f=browse&productID={metadata['product_id']}&type=byModule"
            _write_output(root, metadata, modules, source)
            return 0
        except Exception as exc:
            print(f"status=error reason={exc}")
            return 1
        finally:
            context.close()
            browser.close()


if __name__ == "__main__":
    sys.exit(main())

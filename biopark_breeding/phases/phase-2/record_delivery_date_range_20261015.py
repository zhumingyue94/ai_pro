import re
from playwright.sync_api import Playwright, sync_playwright, expect


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page.goto("http://192.168.6.163:66/portal")
    with page.expect_popup() as page1_info:
        page.get_by_role("button", name="打开应用 种禽孵化管理系统").click()
    page1 = page1_info.value
    page1.locator("div").filter(has_text=re.compile(r"^计划管理$")).click()
    page1.get_by_text("雏苗发货").click()
    page1.get_by_role("combobox", name="开始日期").click()
    page1.get_by_text("15", exact=True).first.click()
    page1.get_by_role("button", name="上个月").click()
    page1.get_by_role("button", name="上个月").click()
    page1.get_by_role("button", name="上个月").click()
    page1.get_by_role("button", name="上个月").click()
    page1.get_by_role("button", name="上个月").click()
    page1.get_by_role("button", name="上个月").click()
    page1.get_by_text("15", exact=True).first.click()
    page1.get_by_role("button", name="查询").click()

    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)

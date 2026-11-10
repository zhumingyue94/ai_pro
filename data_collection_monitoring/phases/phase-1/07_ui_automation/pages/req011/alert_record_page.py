"""REQ-011 告警记录页面对象。"""
from __future__ import annotations
import re
from playwright.sync_api import Locator, Page
PAGE_PATH='/biopark-iot/iot/alert/record'; ROW_SELECTOR='.el-table__body-wrapper table tbody tr'
def wait_loaded(page:Page)->None:
    page.locator('.el-loading-mask').first.wait_for(state='hidden',timeout=15000)
    page.locator(f'{ROW_SELECTOR}, .el-table__empty-text').first.wait_for(state='visible',timeout=20000)
def open_page(page:Page,settings)->None:
    page.goto(f'{settings.portal_url}{PAGE_PATH}',wait_until='domcontentloaded',timeout=30000); wait_loaded(page)
def rows(page:Page)->Locator:return page.locator(ROW_SELECTOR)
def row_values(page:Page)->list[list[str]]:
    r=rows(page); out=[]
    for i in range(r.count()):
        t=r.nth(i).locator('td'); out.append([t.nth(j).inner_text().strip().replace('\n',' / ') for j in range(t.count())])
    return out
def headers(page:Page)->list[str]:
    t=page.locator('.el-table__header-wrapper th'); return [t.nth(i).inner_text().strip() for i in range(t.count())]
def empty_text(page:Page)->str:
    x=page.locator('.el-table__empty-text'); return x.first.inner_text().strip() if x.count() else ''
def date_input(page:Page,which:str)->Locator:return page.get_by_placeholder(which).first
def query(page:Page)->None:page.get_by_role('button',name='查询',exact=True).click(); wait_loaded(page)
def reset(page:Page)->None:page.get_by_role('button',name='重置',exact=True).click(); wait_loaded(page)
def total_count(page:Page)->int:
    x=page.locator('.el-pagination__total'); raw=x.first.inner_text() if x.count() else ''; d=re.sub(r'\D','',raw); return int(d) if d else -1

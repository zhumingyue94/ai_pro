"""REQ-008 数据推送页面对象。"""
from __future__ import annotations
import re
from playwright.sync_api import Locator, Page
PAGE_PATH='/biopark-iot/iot/data/sink'; ROW_SELECTOR='.el-table__body-wrapper table tbody tr'
def wait_loaded(page:Page)->None:
    page.locator('.el-loading-mask').first.wait_for(state='hidden',timeout=15000)
    page.locator(f'{ROW_SELECTOR}, .el-table__empty-text').first.wait_for(state='visible',timeout=20000)
def open_page(page:Page,settings)->None:
    page.goto(f'{settings.portal_url}{PAGE_PATH}',wait_until='domcontentloaded',timeout=30000); wait_loaded(page)
def rows(page:Page)->Locator:return page.locator(ROW_SELECTOR)
def cells(row:Locator)->list[str]:
    t=row.locator('td'); return [t.nth(i).inner_text().strip().replace('\n',' / ') for i in range(t.count())]
def row_values(page:Page)->list[list[str]]:
    r=rows(page); return [cells(r.nth(i)) for i in range(r.count())]
def headers(page:Page)->list[str]:
    t=page.locator('.el-table__header-wrapper th'); return [t.nth(i).inner_text().strip() for i in range(t.count())]
def index(page:Page,name:str)->int:return headers(page).index(name)
def column_values(page:Page,name:str)->list[str]:
    i=index(page,name); return [r[i] for r in row_values(page) if len(r)>i]
def name_filter(page:Page)->Locator:return page.get_by_role('textbox',name='目标名称').first
def select_filter(page:Page,label:str)->Locator:return page.locator('.el-form-item').filter(has_text=label).locator('.el-select').first
def select_option(page:Page,label:str,value:str)->None:
    select_filter(page,label).click(); page.locator('.el-select-dropdown:visible .el-select-dropdown__item').filter(has_text=value).first.click(); page.wait_for_timeout(250)
def query(page:Page)->None:page.get_by_role('button',name='查询',exact=True).click(); wait_loaded(page)
def reset(page:Page)->None:page.get_by_role('button',name='重置',exact=True).click(); wait_loaded(page)
def refresh(page:Page)->None:page.get_by_role('button',name='刷新',exact=True).click(); wait_loaded(page)
def empty_text(page:Page)->str:
    x=page.locator('.el-table__empty-text'); return x.first.inner_text().strip() if x.count() else ''
def total_count(page:Page)->int:
    x=page.locator('.el-pagination__total'); d=re.sub(r'\D','',x.first.inner_text()) if x.count() else ''; return int(d) if d else -1
def active_page(page:Page)->str:
    x=page.locator('.el-pager li.is-active'); return x.first.inner_text().strip() if x.count() else ''
def jump(page:Page,n:int)->None:
    x=page.locator('.el-pagination__jump input'); x.fill(str(n)); x.press('Enter'); wait_loaded(page)
def find_row(page:Page,header:str,value:str)->Locator|None:
    i=index(page,header); r=rows(page)
    for n in range(r.count()):
        row=r.nth(n); vals=cells(row)
        if len(vals)>i and vals[i]==value:return row
    return None
def close_dropdown(page:Page)->None:page.keyboard.press('Escape'); page.wait_for_timeout(200)

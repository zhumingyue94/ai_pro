"""REQ-010 告警配置页面对象。"""
from __future__ import annotations
import re
from playwright.sync_api import Locator, Page
PAGE_PATH='/biopark-iot/iot/alert/config'; ROW_SELECTOR='.el-table__body-wrapper table tbody tr'
def wait_loaded(page:Page)->None:
    page.locator('.el-loading-mask').first.wait_for(state='hidden',timeout=15000)
    page.locator(f'{ROW_SELECTOR}, .el-table__empty-text').first.wait_for(state='visible',timeout=20000)
def open_page(page:Page,settings)->None:
    page.goto(f'{settings.portal_url}{PAGE_PATH}',wait_until='domcontentloaded',timeout=30000); wait_loaded(page)
def rows(page:Page)->Locator:return page.locator(ROW_SELECTOR)
def row_cells(row:Locator)->list[str]:
    cells=row.locator('td'); return [cells.nth(i).inner_text().strip().replace('\n',' / ') for i in range(cells.count())]
def visible_rows(page:Page)->list[list[str]]:
    r=rows(page); return [row_cells(r.nth(i)) for i in range(r.count())]
def headers(page:Page)->list[str]:
    t=page.locator('.el-table__header-wrapper th'); return [t.nth(i).inner_text().strip() for i in range(t.count())]
def empty_text(page:Page)->str:
    x=page.locator('.el-table__empty-text'); return x.first.inner_text().strip() if x.count() else ''
def query(page:Page)->None:page.get_by_role('button',name='查询',exact=True).click(); wait_loaded(page)
def reset(page:Page)->None:page.get_by_role('button',name='重置',exact=True).click(); wait_loaded(page)
def total_count(page:Page)->int:
    x=page.locator('.el-pagination__total'); raw=x.first.inner_text() if x.count() else ''; d=re.sub(r'\D','',raw); return int(d) if d else -1
def name_filter(page:Page)->Locator:return page.get_by_placeholder('请输入配置名称',exact=True).first
def open_add(page:Page)->None:page.get_by_role('button',name='新增',exact=True).click(); page.get_by_text('新增',exact=True).last.wait_for(state='visible')
def add_dialog(page:Page)->Locator:return page.locator('.el-dialog').filter(has_text='新增').last
def dialog_name(page:Page)->Locator:return add_dialog(page).get_by_placeholder('请输入配置名称',exact=True).first
def dialog_description(page:Page)->Locator:return add_dialog(page).get_by_placeholder('请输入配置描述',exact=True).first
def cancel_dialog(page:Page)->None:add_dialog(page).get_by_role('button',name='取 消',exact=True).click()
def select_receiver(page:Page,count:int=1)->list[str]:
    dialog=add_dialog(page); dialog.get_by_text('请选择接收的用户',exact=True).click(); opts=page.locator('.el-select-dropdown:visible .el-select-dropdown__item'); values=[opts.nth(i).inner_text().strip() for i in range(min(count,opts.count()))];
    for value in values: page.locator('.el-select-dropdown:visible .el-select-dropdown__item').filter(has_text=value).first.click()
    page.keyboard.press('Escape')
    return values

"""TC-REQ-003-020：新增产品名称为空时检查必填提示。"""
from __future__ import annotations
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from pages.req003 import product_management_page as product
from utils import standalone_case
CASE_ID="TC-REQ-003-020"
CASE_STEPS={"AP-020-S1","AP-020-S2"}
CASE_ASSERTIONS={"AP-020-A1","AP-020-A2"}
def run_case(page, settings, steps, _):
    product.toolbar(page,"新增").click(); page.wait_for_timeout(1800)
    assert product.dialog(page).is_visible()
    product.submit_dialog(page)
    errors=product.dialog_error_texts(page)
    assert errors and any("名称" in text or "必填" in text for text in errors)
    standalone_case.record(steps,"打开新增产品并保持名称为空","passed","新增表单保持打开",step_id="AP-020-S1",actual={"errors":errors})
    standalone_case.record(steps,"提交空名称表单","passed","显示产品名称必填提示",step_id="AP-020-S2",assertion_id="AP-020-A1",expected="产品名称必填提示",actual=errors)
    product.cancel_dialog(page)
    standalone_case.record(steps,"断言未保存空名称产品","passed","未产生业务写入",assertion_id="AP-020-A2",expected="列表不出现空名称产品",actual={"cleanup":"cancelled"})
def main():
    standalone_case.run_standalone(CASE_ID,run_case,expected_step_ids=CASE_STEPS,expected_assertion_ids=CASE_ASSERTIONS,data_impact={"created":[],"updated":[],"deleted":[],"notes":"表单校验后取消，未保存业务数据"})
if __name__=="__main__": raise SystemExit(main())

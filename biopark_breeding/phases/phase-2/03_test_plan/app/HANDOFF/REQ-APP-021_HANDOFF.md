# REQ-APP-021 测试计划交接

## 计划产物
- YAML：`03_test_plan/app/TEST_PLAN_REQ-APP-021.yaml`
- Markdown：`03_test_plan/app/TEST_PLAN_REQ-APP-021.md`
- 下一阶段：`testcase-generation-agent`

## 交接范围
覆盖 `/m/orders` 的默认列表、日期、栋舍、状态、搜索、卡片入口、已发货/已签收和返回条件。页面事实仅引用 page.json 的 `app-chick-shipping-list`、`app021-*` 状态及已采集元素。

## 风险与待确认
page.json Schema 状态为 `input_missing`、采集状态为 `partial_corrected`；正式路由、权限、统计口径、签收来源和稳定定位器待确认。不得从缺失证据推断元素或定位器。

## 数据与安全
本模块为只读规划，不执行发货变更。数据须脱敏，凭据、Token、Cookie 和原始搜索值不得进入计划或证据。

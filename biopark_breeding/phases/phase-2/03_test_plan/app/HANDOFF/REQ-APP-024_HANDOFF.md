# REQ-APP-024 测试计划交接

## 计划产物
- YAML：`03_test_plan/app/TEST_PLAN_REQ-APP-024.yaml`
- Markdown：`03_test_plan/app/TEST_PLAN_REQ-APP-024.md`
- 下一阶段：`testcase-generation-agent`

## 交接范围
覆盖上孵计划发货记录的待发货、发货中、已发货、已签收、空态、未找到、数量进度、多位置、排序、签收和折叠边界。仅引用 page.json 已采集的 `app024-*` 状态和元素。

## 风险与待确认
page.json 为 `input_missing`/`partial_corrected`；页面与 APP-023 共享结构，原型无折叠/展开控件，签收来源与正式路由待确认。mock 状态不证明服务端事实。

## 数据与安全
页面查询不变更业务数据；签收样本须脱敏，凭据、Token、Cookie 和未授权业务结果不得进入证据。

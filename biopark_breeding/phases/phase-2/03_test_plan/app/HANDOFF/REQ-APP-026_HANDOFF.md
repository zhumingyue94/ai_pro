# REQ-APP-026 测试计划交接

## 计划产物
- YAML：`03_test_plan/app/TEST_PLAN_REQ-APP-026.yaml`
- Markdown：`03_test_plan/app/TEST_PLAN_REQ-APP-026.md`
- 下一阶段：`testcase-generation-agent`

## 交接范围
规划存发苗间库存查询、批次/上孵计划/出库追溯、自动出库扣减、不负库存、并发读一致性和一期复用契约。二期未发现专属 APP 页面证据，当前保持 blocked。

## 风险与待确认
不得虚构库存页面、路由、状态、字段、按钮、菜单、定位器或错误码。一期复用范围、查询契约、权限和发货后数据一致性时点待确认。

## 数据与安全
查询本身为只读；发货联动会产生业务变更，需授权并登记回读、责任人和清理状态。证据须脱敏，不保存凭据、Token 或 Cookie。

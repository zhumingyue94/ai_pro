# REQ-APP-024 APP上孵计划发货记录

## 范围与规则
覆盖上孵计划详情、实际可发、累计发货、待分配、进度、状态和历史发货记录，不覆盖发货确认或库存维护。状态和数量以服务端查询结果为准；未收到外部系统明确签收结果不得显示“已签收”。历史记录按提交时间倒序，一条记录可含多个列/层位置。默认折叠 3 条，点击展开全部展示全部有效或历史记录；无效计划号显示未找到。

## 页面契约（page.json）
页面 `app-plan-shipment-records`，路由 `/m/orders/{发货单号}/plan-shipments/{上孵计划内部ID}`。状态包括 `app024-empty-notfound`、`app024-pending-hp021`、`app024-shipping-hp022`、`app024-shipped-hp071`、`app024-shipped-hp072`、`app024-shipping-record-expanded`、`app024-hp011-not-found`。元素包括 `notfound-page`、`notfound-text`、`pending-page`、`pending-plan-no`、`pending-status`、`pending-progress`、`shipping-page`、`shipping-status`、`shipping-progress`、`shipping-records`、`record1-status`、`record1-pos1`、`shipped-page`、`shipped-status`、`shipped-progress`、`shipped-record`、`record-complete`、`position-detail`、`hp072-records`、`hp072-record1-complete`、`hp072-record2-incomplete`、`hp072-position-accum`、`shipping-record-no-collapse-btn`。

## 边界、依赖与风险
需区分未找到、待发货、发货中、已发货、外部确认后的已签收，以及空记录、1～3 条、超过 3 条、多位置和完成/未完成混合记录。依赖上孵计划、发货记录、外部签收、列层和发货单服务。原型 `shipping-record-no-collapse-btn` 显示没有折叠/展开控件且默认全部展开，与需求变动冲突；同时需防止累计数量和签收来源口径不一致。模块只读，联调数据须由测试数据负责人清理并记录状态。

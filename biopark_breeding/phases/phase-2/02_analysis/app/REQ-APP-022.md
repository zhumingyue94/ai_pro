# REQ-APP-022 APP发货执行

## 1. 范围
覆盖发货执行页的计划汇总、发货弹窗、列层选择、数量和备注录入、服务端校验、确认后的刷新与状态更新。不覆盖列表筛选及记录页展示。

## 2. 业务规则
发货列、层来自园区基础数据且必须选择；数量必须为正整数，不得超过提交时服务端最新实际可发/待分配数量。备注最多支持 15 字。后端负责防抖、重复提交和并发校验。确认成功后刷新页面、统计、进度和状态；结果未知时应支持重新查询。上孵计划部分发货且待发货数大于 0 时，不生成存发苗间出库记录且库存不减少；最后一次有效发货使待发货数归零时，才触发自动出库和库存扣减，出库数量及库存变动数量等于多次发货累计数，即上孵计划实际可发数。出库记录字段及库存查询结果分别由 REQ-APP-025、REQ-APP-026 只读回读验证，本模块负责验证联动触发时机和数量。

## 3. 页面契约（page.json）
页面 `app-chick-shipment-execute`，路由 `/m/orders/{发货单号}/execute`。状态为 `app022-exec-default`、`app022-ship-dialog`、`app022-validation-no-quantity`、`app022-validation-exceed-quantity`、`app022-validation-no-position`、`app022-remark-15-limit`、`app022-execute-shipped`、`app022-execute-bl02`、`app022-bl02-ship-dialog`。核心元素为 `exec-page`、`exec-progress`、`exec-stat-actual`、`exec-stat-accum`、`exec-stat-pending`、`plan-list`、`plan01-record-btn`、`plan01-ship-btn`、`ship-dialog`、`ship-dialog-column`、`ship-dialog-row`、`ship-dialog-quantity`、`ship-dialog-remark`、`ship-dialog-confirm`、`ship-dialog-error-no-qty`、`ship-dialog-error-exceed`、`ship-success-toast`、`ship-dialog-remark-truncated`。

## 4. 边界、依赖与风险
数量边界包括空、0、负数、小数、1、等于待发、超过待发及并发后超发；位置边界包括空值和有效园区列层；备注包括 15 字及超长输入。原型 `app022-validation-no-position` 未体现列层空值必填校验，需以前后端契约为准。成功提示、实际落库、统计刷新和自动出库必须可关联。依赖发货单、上孵计划、园区列层、库存和状态服务。

## 5. 环境与安全
需要授权角色、待分配数量大于零的计划、有效列层及可核对库存关联。确认发货是业务数据变更，责任边界为授权发货操作人和测试数据负责人，需记录结果、清理责任和清理状态。不得记录账号、密码、Token、Cookie 或未经授权业务数据。

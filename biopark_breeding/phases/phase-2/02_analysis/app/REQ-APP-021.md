# REQ-APP-021 APP雏苗发货列表与筛选

## 1. 范围
覆盖 `/m/orders` 的任务日期、栋舍、状态卡、发货单号/孵化计划号搜索、列表展示、排序和卡片内入口。发货执行、记录详情、存发苗间维护不属于本模块。

## 2. 角色与规则
角色为现场发货填报人、发货组长、场长及系统管理配置的授权角色。默认日期按系统时间取当天；日期选择支持昨天、今天、明天和自定义日期，点击确认后才生效。状态统计、状态卡和列表必须使用同一口径，状态筛选仅通过状态卡切换。列表排序为最后更新时间、计划发货日期、发货单号。无关联上孵计划的发货单不显示发货和明细操作；“去发货/继续发货”必须位于对应卡片内。未得到外部系统明确签收结果不得显示“已签收”。移动端不分页。

## 3. 页面契约（page.json）
页面 `app-chick-shipping-list`，路由 `/m/orders`。状态包括 `app021-default`、`app021-date-picker`、`app021-date-yesterday-result`、`app021-house-all`、`app021-house-filter`、`app021-search-empty`、`app021-search-result-input`、`app021-progress`、`app021-shipped`、`app021-signed`。元素包括 `date-filter`、`house-filter`、`search-entry`、`status-tabs`、`order-card-pending`、`shipment-record-entry`、`ship-entry`、`date-dialog`、`date-reset`、`date-confirm`、`house-dialog`、`house-option-3`、`house-all-option`、`search-form`、`search-input`、`search-empty-text`、`search-result-matched-card`、`search-result-ship-btn` 等。

## 4. 接口与依赖
需要服务端返回任务日期结果、发货单、上孵计划关联、状态统计、栋舍基础数据和最新状态。依赖孵化排程计划、雏苗发货单、上孵计划、栋舍基础数据和外部签收结果。接口字段、错误码、权限码和不分页响应格式仍需服务端确认。

## 5. 边界与风险
需覆盖日期取消/重置、零统计、空搜索、精确匹配、无匹配、各状态切换、栋舍全选/单选及返回条件保留。主要风险是统计与列表口径不一致、服务端数据更新后列表过期、原型与设计映射部分匹配。

## 6. 环境与安全
需要授权角色、可关联上孵计划的发货单和可验证日期/状态数据。本模块分析不执行数据变更；联调数据由测试数据负责人负责并记录清理状态。不得在页面清单、截图、日志或报告中记录账号、密码、Token、Cookie 或未经授权业务数据；搜索值保持脱敏。

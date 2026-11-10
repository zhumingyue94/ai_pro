# REQ-011 告警记录交接说明

## 交接状态

- 模块：告警记录
- `module_id`：`REQ-011`
- 禅道模块路径：`iot平台/告警中心/告警记录`
- 禅道模块 ID：`749`；父模块 ID：`729`
- 优先顺序：`11`（`P1`）
- 运行时路由：`/biopark-iot/iot/alert/record`
- 页面：`alert_record`
- 当前状态：`blocked_scoped_readonly_ui_verification`
- 分析文件：`02_analysis/REQ-011.yaml`、`02_analysis/REQ-011.md`

## 已确认规则

1. 记录编号由系统生成，唯一、不可修改；查询和排序使用该编号。
2. 每个告警事件有唯一事件标识；重复事件关联同一事件；记录绑定触发时生效的规则版本。
3. 触发时间、创建时间和数据来源时间口径不同，页面按当前用户时区显示和筛选。
4. 历史记录保存触发时告警配置快照，后续配置停用、删除或修改不影响历史记录。
5. 是否处理只有“是/否”；新记录为“否”，处理完成为“是”。
6. 仅记录“否→是”、操作人、操作时间和备注；不涉及确认、关闭、重开、转派和批量操作。
7. 当前页面不展示阈值、实际值、单位、时间序列、位置、质量码、原始消息、通知状态和处理备注详情。
8. 产品和设备支持级联筛选；失效、删除或无权限对象不能选择，历史记录保留原对象信息。
9. 最新记录在前，重复事件按事件标识关联，刷新不重复；默认按创建时间倒序，筛选、分页和刷新后保持。
10. 记录、处理记录、历史快照和处理信息默认长期保存；有权限用户可归档和删除，删除后不可恢复。
11. 详情按权限展示；设备标识、位置和测量值按业务需要展示；联系人、通知内容和触发消息敏感信息脱敏。

## page.json 页面证据

### `alert_record_default`

- `alert_record_config`
- `alert_record_level`
- `alert_record_product`
- `alert_record_query`
- `alert_record_reset`
- `alert_record_expand`
- `alert_record_refresh`
- `alert_record_columns`
- `alert_record_view`
- `alert_record_handle`
- `alert_record_page_size`
- `alert_record_prev`
- `alert_record_next`
- `alert_record_jump`
- 表格：`alert_record_table`、`alert_record_table_element`

### `alert_record_filter_expanded`

- `alert_record_device`
- `alert_record_handled`
- `alert_record_start`
- `alert_record_end`

### `alert_record_dialogs_partial`

- `alert_record_dialog`，定位器缺失，详情/处理字段和反馈不作为已确认页面事实。

脱敏截图：

- `02_analysis/page_inventory/screenshots/req011-default.png`
- `02_analysis/page_inventory/screenshots/req011-filter-expanded.png`

## 后续准入和禁止项

允许在明确授权后执行限定范围只读验证：

- 复用 `07_ui_automation/pages/common/login_page.py`；
- 复用 `07_ui_automation/pages/common/portal_navigation.py`；
- 进入“数据采集 → 告警中心 → 告警记录”；
- 检查路由、标题、列表、筛选、排序、分页、脱敏列和无数据提示；
- 在入口和定位器稳定时打开查看/处理/归档/删除确认层后取消。

禁止：

- 提交处理；
- 确认归档；
- 确认删除；
- 制造或触发告警；
- 跨租户访问；
- 捕获 endpoint、认证信息或载荷；
- 读取联系人、触发消息原文或通知内容；
- 绕过权限。

## 阻塞项

1. 详情和处理表单字段、成功/失败、异步状态及稳定定位器不完整；
2. 归档/删除入口、确认层和不可恢复提示未闭合；
3. 角色/租户权限矩阵及权限提示定位器缺失；
4. 事件标识、三类时间、并发幂等和错误码契约未确认；
5. 长期留存、归档和删除清理责任未闭合；
6. 正式 PDF REQ-011 页码追溯待补。

## 数据安全与责任边界

地址、项目、账号、密码和租户仅从 `.env`、`config.yaml` 或运行时配置读取，本文件不记录具体值。账号、密码、Token、Cookie、设备标识、位置、测量值、联系人、触发消息、通知内容和未经授权业务数据不得写入页面清单、截图、日志、DOM、报告或下载文件。

本阶段不产生数据变更，清理状态：`not_applicable`。未来若获批隔离事件或副作用操作，责任人为测试负责人、告警记录负责人、数据监听负责人及权限/租户负责人；必须预先确认停止条件、回滚或不可恢复确认、留存和清理结果。

## 交接结论

REQ-011 已依据最新确认项和 `page.json` 页面证据重建。当前仅交接限定范围只读 UI/行为规划，不代表处理、归档、删除、事件生成、长期留存或接口验收完成。

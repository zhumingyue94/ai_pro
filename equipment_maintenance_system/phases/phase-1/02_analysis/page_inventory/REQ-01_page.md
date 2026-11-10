# REQ-01 页面清单

> 本文件为 `page.json` 的可读版摘要，页面事实以同级 `page.json` 为准。

## 1. 采集概况

| 项目 | 内容 |
|---|---|
| 需求编号 | REQ-01 |
| 页面标识 | `req01-arrival-acceptance` |
| 页面标题 | 设备生命周期管理 |
| 菜单路径 | 设备资产管理 > 设备生命周期管理 > 到货验收 |
| 路由 | `/biopark-eam/eam/lifecycle` |
| 禅道模块 | 763 |
| PRD映射 | RQ-EAM-LC-001 |
| 采集工具 | `agent-browser CLI` |
| 浏览器 | Chromium |
| 浏览器模式 | 可视模式，`headless=false` |
| 采集时间 | 2026-11-10 08:30:00 UTC |
| 采集状态 | `partial` |
| Capture ID | `PAGE-REQ01-20261110` |

## 2. 证据文件

### 截图

- [默认页面](screenshots/req-01-default.png)
- [新增采购单弹窗](screenshots/req-01-new-dialog.png)
- [历史操作记录弹窗](screenshots/req-01-history-dialog.png)
- [到货验收弹窗](screenshots/req-01-accept-dialog.png)

### 脱敏 DOM / 可访问性快照

- [默认页面 DOM](dom/req-01-default.txt)
- [新增采购单弹窗 DOM](dom/req-01-new-dialog.txt)
- [历史操作记录弹窗 DOM](dom/req-01-history-dialog.txt)
- [到货验收弹窗 DOM](dom/req-01-accept-dialog.txt)

## 3. 页面默认状态

### 3.1 页面元素

| 元素 ID | 类型 | 名称/文本 | 初始状态 | 定位器候选 |
|---|---|---|---|---|
| `page_root` | 页面 | 到货验收页面 / 设备生命周期管理 | 可见、启用 | 文本：`设备生命周期管理` |
| `arrival_tab` | Tab | 到货验收 | 可见、选中 | Role：`tab=到货验收` |
| `id_filter` | 输入框 | ID | 可见、启用、为空 | Role：`textbox=ID` |
| `material_filter` | 输入框 | 物料名称 | 可见、启用、为空 | Role：`textbox=物料名称` |
| `status_filter` | 下拉框 | 验收状态 | 默认“全部” | Label：`验收状态` |
| `query_button` | 按钮 | 查询 | 可见、启用 | Role：`button=查询` |
| `reset_button` | 按钮 | 重置 | 可见、启用 | Role：`button=重置` |
| `new_po_button` | 按钮 | 新增采购单 | 可见、启用 | Role：`button=新增采购单` |
| `refresh_button` | 按钮 | 刷新 | 可见、启用 | Role：`button=刷新` |
| `header_settings` | 按钮 | 表头设置 | 可见、启用、未选中 | Role：`button=表头设置` |
| `history_action` | 行操作 | 历史操作记录 | 按数据状态显示 | Role：`button=历史操作记录` |
| `start_accept_action` | 行操作 | 发起验收 | 按数据状态显示 | Role：`button=发起验收` |
| `repeat_accept_action` | 行操作 | 再次验收 | 按数据状态显示 | Role：`button=再次验收` |
| `pagination` | 分页 | 20条/页，第1页 | 可见、启用 | CSS：`.el-pagination` |

### 3.2 表格

表格 ID：`arrival_table`

| 列 ID | 列名 |
|---|---|
| `po_number` | 采购单号 |
| `material_name` | 物料名称 |
| `spec` | 规格型号 |
| `detail_qty` | 明细数量 |
| `accepted_qty` | 验收数量 |
| `accept_status` | 验收状态 |
| `operator` | 操作人 |
| `operation_time` | 操作时间 |
| `actions` | 操作 |

表格关联控件：

- 筛选：`id_filter`、`material_filter`、`status_filter`
- 分页：`pagination`
- 行操作：`start_accept_action`、`repeat_accept_action`、`history_action`

## 4. 派生状态

### 4.1 验收状态下拉

操作：打开 `status_filter`。

预期/观察范围：

- 全部
- 待验收
- 部分验收
- 通过
- 不通过

操作完成后关闭下拉，避免遮挡其他页面控件。

### 4.2 表头设置

操作：打开 `header_settings`。

观察到页面提供表头配置面板，用于列显示、宽度或固定位置等配置。具体列配置的持久化行为需在后续执行中继续回读确认。

## 5. 新增采购单弹窗

状态 ID：`req01_new_dialog_initial`

弹窗元素 ID：`new_po_dialog`

| 元素 ID | 字段 | 控件类型 | 默认值 | 必填 | 可编辑/状态 |
|---|---|---|---|---|---|
| `new_material_name` | 物料名称 | 文本框 | 空 | 是 | 可编辑 |
| `new_spec` | 规格型号 | 文本框 | 空 | 否 | 可编辑 |
| `new_detail_qty` | 明细数量（台） | 数字框 | `1` | 是 | 可编辑 |
| `new_total_price` | 价税合计 | 数字框 | `0` | 是 | 可编辑 |
| `new_delivery_date` | 交货日期 | 日期控件 | 当前日期 | 是 | 可编辑 |
| `new_cancel` | 取消 | 按钮 | - | 否 | 可用 |
| `new_submit` | 新增测试数据 | 按钮 | - | 否 | 可用 |

已探索交互：

1. 打开新增采购单弹窗。
2. 记录字段、默认值、必填状态和按钮。
3. 空表单提交，验证必填校验状态。
4. 使用 `AUTO测试_勿用_` 前缀创建测试采购数据。
5. 创建后回到列表并回读数据。

表单 ID：`new_po_form`

- 字段：`new_material_name`、`new_spec`、`new_detail_qty`、`new_total_price`、`new_delivery_date`
- 提交按钮：`new_submit`
- 取消按钮：`new_cancel`

## 6. 历史操作记录弹窗

状态 ID：`req01_history_dialog`

弹窗 ID：`history_dialog`

- 标题：历史操作记录
- 类型：只读弹窗
- 实际观察状态：无记录/空状态
- 可执行操作：查看、刷新、关闭
- 证据：[历史操作记录截图](screenshots/req-01-history-dialog.png)

## 7. 到货验收弹窗

状态 ID：`req01_accept_dialog_initial`

弹窗 ID：`accept_dialog`

| 元素 ID | 字段 | 控件类型 | 默认状态 | 可编辑/状态 |
|---|---|---|---|---|
| `accept_org` | 验收组织 | 文本框 | 已脱敏 | 禁用、只读 |
| `accept_pass` | 通过 | 单选框 | 默认选中 | 可选 |
| `accept_fail` | 不通过 | 单选框 | 未选中 | 可选 |
| `accept_qty` | 验收数量 | 数字框 | 已脱敏 | 可编辑 |
| `accept_remark` | 备注 | 文本域 | 空 | 可编辑 |
| `accept_operator` | 操作人 | 文本框 | 已脱敏 | 禁用、只读 |
| `accept_cancel` | 取消 | 按钮 | - | 可用 |
| `accept_submit` | 提交验收 | 按钮 | - | 可用 |

表单 ID：`accept_form`

- 字段：`accept_org`、`accept_pass`、`accept_fail`、`accept_qty`、`accept_remark`、`accept_operator`
- 提交按钮：`accept_submit`
- 取消按钮：`accept_cancel`

已探索交互：

1. 从待验收记录打开“发起验收”。
2. 记录验收组织、操作人禁用只读状态。
3. 记录“通过”默认选中和“不通过”可选状态。
4. 填写验收数量和备注。
5. 提交验收并返回列表。
6. 实际观察到提交后列表仍显示发起验收入口，后端状态变化需要进一步回读确认。

## 8. 交互链路

| 序号 | 操作 | 目标 | 结果/观察 |
|---:|---|---|---|
| 1 | 查看 | `page_root` | 页面标题、到货验收 Tab、筛选区、表格和分页可见 |
| 2 | 打开 | `status_filter` | 展开验收状态选项 |
| 3 | 打开 | `header_settings` | 展开表头设置面板 |
| 4 | 打开 | `new_po_button` | 打开新增测试采购单弹窗 |
| 5 | 打开 | `history_action` | 打开历史操作记录弹窗，显示空状态 |
| 6 | 打开 | `start_accept_action` | 打开到货验收弹窗 |
| 7 | 提交 | `new_submit` | 使用授权前缀创建测试采购数据 |
| 8 | 提交 | `accept_submit` | 提交测试采购单验收信息 |

## 9. 有副作用操作与清理责任

| 操作 | 数据范围 | 授权 | 结果记录 |
|---|---|---|---|
| 新增采购单 | 仅使用 `AUTO测试_勿用_` 前缀数据 | 已授权 | 已提交并回读列表 |
| 提交验收 | 仅针对本轮测试数据 | 已授权 | 已提交；状态变化需后续回读确认 |
| 编辑 | 本页面未发现入口 | 不适用 | 未发现 |
| 删除 | 本页面未发现入口 | 不适用 | 未发现 |
| 启用/停用 | 本页面未发现入口 | 不适用 | 未发现 |
| 清理测试数据 | 应由后续执行阶段负责 | 已授权 | 当前页面未发现明确删除入口，清理状态需后续确认 |

## 10. 未完成项与风险

页面清单整体状态为 `partial`，原因如下：

1. 页面未发现编辑、删除、启用或停用入口，无法在本页面验证这些操作。
2. 提交验收后页面仍显示“发起验收”入口，需要后续通过列表刷新或后端状态回读确认。
3. 表头设置的具体列变更及持久化行为需要进一步回读。
4. 横向滚动、分页边界、排序和不同验收状态的完整按钮差异需要后续执行阶段补充证据。
5. 测试数据清理入口未在本页面发现，清理责任和最终结果需单独记录，不得伪造为已清理。

## 11. 脱敏说明

已脱敏或不写入本清单的信息：

- 账号、密码、Token、Cookie、认证态
- 业务人员和租户敏感信息
- 既有业务采购单号和具体时间
- 测试环境内部地址

原始结构化数据详见同级文件 [`page.json`](page.json)。

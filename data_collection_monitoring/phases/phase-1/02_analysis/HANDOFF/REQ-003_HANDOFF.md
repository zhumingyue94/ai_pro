# REQ-003 产品管理交接说明

## 交接状态

- `module_id`：`REQ-003`
- 模块：产品管理
- 禅道模块：`iot平台/设备接入/产品管理`，模块 ID `732`，父模块 ID `727`
- 页面对象：`product_management`
- page.json 路由：`/biopark-iot/iot/device/product`
- 模块清单路由：`/iot/device/product`
- 标题：`数据采集 - 产品管理`
- 默认状态：`product_management_default`
- 采集状态：`partial`
- 当前状态：`ready_for_scoped_readonly_ui_verification`
- 分析文件：`02_analysis/REQ-003.yaml`、`02_analysis/REQ-003.md`

## 源需求编号

《需求变动.md》当前纳入分析的实际编号为：`REQ-003-001` 至 `REQ-003-010`、`REQ-003-011` 至 `REQ-003-013`、`REQ-003-014` 至 `REQ-003-015`。未将未登记的旧编号作为源需求编号。

## 已确认规则

1. 产品名称必填，同租户唯一；编辑可修改但继续校验唯一性；其他限制按系统默认规则。
2. `ProductKey` 自动生成但允许修改；长度、字符、租户范围、唯一性和并发冲突按系统默认规则。
3. 分类必填且只能选择启用分类；停用分类保留已有产品原分类；删除分类前处理关联；改名同步关联名称。
4. 支持直连设备、网关子设备和网关设备；建立后设备类型不可修改。
5. 图标和图片可为空，支持常见图片格式，上传数量、大小和尺寸按系统默认，允许替换；上传失败需提示。
6. 状态流程为未发布→已发布→撤回→停用；停用后可再次发布；状态关联当前版本；失败回退原状态。
7. 物模型支持查看、编辑和按版本发布；发布后生成新版本，新版本需兼容已有设备；失败回滚且不影响在线设备。
8. 有设备、采集任务、推送配置或告警规则关联时禁止删除；确认规则允许编辑、停用、改分类和发布，但 `REQ-003-015` 同时明确本模块没有停用功能，需以运行时页面为准。
9. 导出字段与当前浏览器表格展示字段及筛选结果一致；隐藏敏感信息不导出；失败提示；临时文件使用后清理。
10. 默认创建时间倒序，筛选、分页和刷新后保持倒序。
11. 页面级验证不做接口测试，只补充实际字段、筛选结果、状态反馈、物模型入口和导出控件。

## 已登记页面事实

- 默认列表：`product_management_default`
- 目标：`product_management_state`，`css=body`
- 表格：`product_management_table` / `product_management_table_element`
- 筛选：`product_management_name`、`product_management_key`
- 查询/重置/刷新：`product_management_query`、`product_management_reset`、`product_management_refresh`
- 表头/导出/新增：`product_management_columns`、`product_management_export`、`product_management_add`
- 行操作：`product_management_view`、`product_management_edit`、`product_management_model`、`product_management_delete`
- 分页：`product_management_page_size`、`product_management_prev`、`product_management_page`、`product_management_next`
- 表头设置：`product_management_columns_expanded`
- 编辑页：`product_management_edit`、`product_management_edit_page`、`product_management_edit_form`
- 编辑字段：`product_management_product_key`、`product_management_regenerate`、`product_management_name`、`product_management_category`、`product_management_direct`、`product_management_sub_device`、`product_management_gateway`、`product_management_network`、`product_management_ip_location`、`product_management_report_location`、`product_management_manual_location`、`product_management_alink`、`product_management_more`、`product_management_confirm`、`product_management_cancel`
- 更多配置：`product_management_more_expanded`、`product_management_description`
- 部分弹窗：`product_management_dialogs_partial`、`product_management_dialog`，定位状态 `missing`

表格列为 `ProductKey`、产品名称、产品分类、设备类型、产品图标、产品图片、状态、创建时间、操作。新增、查看、物模型和删除弹窗尚未形成稳定完整契约。

## 允许的只读验证

- 复用 `login_page.py` 和 `portal_navigation.py`，确认路由、标题、菜单和页面就绪状态。
- 只读查看默认列表、表头设置、名称/ProductKey筛选、查询/重置/刷新、分页、排序和导出控件。
- 打开编辑页、展开更多配置并取消，不提交更新。
- 仅当弹层定位稳定且取消安全时打开新增、查看、物模型或删除确认层并取消。
- 记录实际字段、筛选结果、状态反馈、物模型入口和导出控件与规则的差异；数据不足时记录无法验证。

## 禁止与停止条件

禁止提交新增、保存编辑、发布、撤回、停用、确认删除、上传图片、修改物模型、导出/下载业务数据、接口写入、造数或绕过权限/安全验证。配置缺失、登录失败或人工验证、主机不匹配、权限失败、关键内容缺失、加载失败、内容不稳定、意外写入提示或未授权数据暴露时停止。

## 待补证据

1. 正式 PDF 的 REQ-003 章节逐条追溯。
2. 新增/查看/物模型/删除、状态、导出、上传、加载和错误提示稳定定位器。
3. 状态、版本、物模型兼容性、发布失败回滚及在线设备保护证据。
4. 分类启停/改名/删除与产品关联的页面反馈。
5. 产品关联时删除阻止及其他允许操作的页面反馈。
6. 权限与租户矩阵，包括查看、新增、编辑、发布、撤回、停用、删除、导出和物模型。
7. 导出字段、当前筛选、敏感过滤、数据量上限、失败提示和临时清理契约。
8. 产品列表、分类、增改删、状态/版本、物模型、图片、导出、权限、审计和留存接口契约。
9. 隔离测试数据、写操作批准人、停止条件、回滚/删除方案和清理责任。

《需求变动.md》中现有 REQ-003 确认项已覆盖本次分析候选，未发现需要重复追加的新待确认项，因此保持原文不变。

## 数据安全责任

仅引用 `.env`/`config.yaml` 配置键名，不将地址、项目、账号、密码、租户、Token、Cookie、ProductKey、产品名称或未经授权业务数据写入产物。本次数据变更为无，清理状态为 `not_applicable`。

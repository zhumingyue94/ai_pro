# REQ-002 产品分类交接说明



## 交接状态



- `module_id`：`REQ-002`

- 模块：产品分类

- 禅道模块：`iot平台/设备接入/产品分类`，模块 ID `731`，父模块 ID `727`

- 页面对象：`product_category`

- page.json 路由：`/biopark-iot/iot/device/product-category`

- page.json 标题：`数据采集 - 产品分类`

- 默认状态：`product_category_default`

- 采集状态：`partial`

- 当前状态：`ready_for_scoped_readonly_ui_verification`

- 分析文件：`02_analysis/REQ-002.yaml`、`02_analysis/REQ-002.md`



## 源需求编号



当前《需求变动.md》实际登记并纳入分析的编号为：`REQ-002-001` 至 `REQ-002-010`、`REQ-002-011` 至 `REQ-002-013`、`REQ-002-014`。未将未登记的旧编号作为源需求编号。



## 已确认规则



1. 名称必填，只校验不能为空；长度和字符不限制；同租户允许重名且不提示。

2. 描述非必填，支持空值、换行、空白和常见特殊字符。

3. 状态包括启用、停用、删除；停用阻止新产品选择，已有产品保留原分类。

4. 创建时间按用户时区显示，格式 `YYYY-MM-DD HH:mm:ss`；列表按排序字段升序；排序只允许正整数且可重复。

5. 产品数量按当前分类下未删除产品统计，包含停用、不包含已删除；进入页面或手动刷新更新；当前六列表格不增加数量列。

6. 已使用分类允许改名且历史记录同步；删除前处理全部关联产品。

7. 列表六列为编号、名称、描述、状态、创建时间、操作；空字段显示 `-`；加载失败提示。

8. 新增默认启用、编辑回显、取消关闭、保存中禁用且只处理一次、失败保留输入、并发提示刷新重试、删除失败保留数据并说明原因。

9. 分类与产品、设备分组及首页统计按唯一编号关联，页面重新进入或手动刷新时更新。

10. 表头设置保存到当前用户，重新进入、切换页面或重新登录后保留。



## 已登记页面事实



- 状态：`product_category_default`、`product_category_columns_expanded`、`product_category_add_form`、`product_category_add_validation_error`、`product_category_edit_form`、`product_category_delete_confirm`

- 列表控件：`product_category_name`、`product_category_query`、`product_category_reset`、`product_category_refresh`、`product_category_columns`

- 操作控件：`product_category_add`、`product_category_edit`、`product_category_delete`

- 分页控件：`product_category_page_size`、`product_category_prev`、`product_category_page_1`、`product_category_page_2`、`product_category_next`、`product_category_jump`

- 新增字段：`product_category_add_name`、`product_category_add_sort`、`product_category_add_on`、`product_category_add_off`、`product_category_add_desc`

- 编辑字段：`product_category_edit_name`、`product_category_edit_sort`、`product_category_edit_on`、`product_category_edit_off`、`product_category_edit_desc`

- 新增按钮：`product_category_add_submit`、`product_category_add_cancel`

- 编辑按钮：`product_category_edit_submit`、`product_category_edit_cancel`

- 删除对话框：`product_category_delete_dialog`、`product_category_delete_cancel`、`product_category_delete_confirm`、`product_category_delete_close`

- 表格：`product_category_table`、`product_category_table_element`



## 后续允许的只读验证



- 运行时确认路由、标题、菜单路径和页面状态。

- 复用公共登录与门户导航脚本，只读进入产品分类页面。

- 查看名称筛选、查询、重置、刷新、分页、空字段显示和列表排序。

- 打开并取消新增、编辑和删除确认层，检查新增默认启用、编辑回显和校验状态，但不提交。

- 记录停用/删除关联规则、跨模块刷新、产品数量追踪、错误反馈和权限证据的存在性；数据不足时记录无法验证。



## 禁止与停止条件



禁止真实新增、保存、编辑、停用、删除、导入、导出、接口写入、表头持久化、造数、下载和绕过权限/安全验证。运行配置缺失、登录失败或人工验证、主机不匹配、权限失败、关键内容缺失、意外写入提示或未授权数据暴露时停止。



## 待补证据



1. 正式 PDF 的 REQ-002 章节逐条追溯。

2. 排序正整数输入与后端字段、升序稳定性的证据。

3. 产品数量统计与当前六列表格之间的追踪证据。

4. 停用/删除关联阻断及分类改名后的跨模块刷新。

5. 失败、并发、重复提交和权限反馈的稳定定位与契约。

6. 当前用户表头设置的存储和恢复证据。

7. 权限、租户、接口字段、错误码、幂等和审计契约。



《需求变动.md》中现有 REQ-002 确认回答已覆盖本次分析候选，未发现新的待确认项，因此保持原文不变。



## 数据安全责任



仅引用 `.env`/`config.yaml` 配置键名，不将地址、项目、账号、密码、租户、Token、Cookie、分类名称或未经授权业务数据写入产物。本次数据变更为无，清理状态为 `not_applicable`。



## 2026-10-23 变更
- 补充 TC-REQ-002-044 至 TC-REQ-002-051，覆盖新增、编辑、删除及启停状态流转核心闭环。
- 写入执行条件不足，统一记录 execution_blocker。

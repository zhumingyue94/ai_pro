# 测试用例 Markdown 公共流水线

测试用例以 YAML 为事实源，Markdown 为派生交付物。统一使用公共模板和脚本：

```powershell
python scripts/render_testcase_markdown.py <cases.yaml> <cases.md>
python scripts/validate_testcase_markdown.py <cases.yaml> <cases.md>
python scripts/validate_testcase_template.py <cases.yaml> <cases.md>
```

`validate_testcase_template.py` 是兼容 YAML/Markdown 模板合同和公共前置引用的通用校验器；当前阶段配置中的 Markdown 派生物校验仍使用 `validate_testcase_markdown.py`。项目可按需调用上述任一公共脚本，不要求项目存在 `reference/` 目录。

校验失败返回非零状态，禁止将 Markdown 交接给下游阶段。生成器使用临时文件后原子替换输出文件，不会修改 YAML。

## 禅道模块数据读取

公共脚本 `fetch_zentao_module_cases.py` 只读获取指定产品、项目和模块下的禅道测试用例，支持分页以及 JSON/Markdown 输出：

```powershell
python scripts/fetch_zentao_module_cases.py --product 1 --project 29 --module 715 --format json --output cases.json
```

该脚本只调用 `zentao testcase` 读取数据，不执行创建、更新或删除操作。`fetch_zentao_modules.py` 的职责是采集产品模块树；两者分别负责模块用例和模块结构，不应混用。

测试：

```powershell
python -m pytest scripts/test_markdown_contract.py
```

## Python 文件清单

以下清单覆盖 `scripts/` 目录下全部 Python 文件。函数名后的说明描述其主要职责；测试文件中的函数为测试用例，不是生产接口。

### 公共工具与禅道同步

| 文件 | 主要作用 | 顶层函数、类及作用 |
|---|---|---|
| `build_module_case_map.py` | 根据配置、模块参考文档和测试用例构建或校验 `module_case_map.json`，不访问禅道。 | `_load_project_config` 读取配置；`_parse_modules` 解析模块文档；`_resolve_module` 解析用例所属模块；`_case_review_path` 推导评审文件；`build_registry` 构建注册表；`main` 执行命令。 |
| `check_zentao_sync_entrypoint.py` | 检查项目同步脚本是否绕过公共禅道入口或包含违规调用。 | `project_files` 查找项目同步脚本；`check_file` 检查单文件；`main` 执行检查。 |
| `export_zentao_csv.py` | 将评审通过的 Harness 用例 YAML 导出为禅道 CSV，并回写摘要与哈希。 | `parse_args` 解析参数；`load_yaml` 读取 YAML；`sha256_bytes` 计算摘要；`canonical_review_hash` 计算评审哈希；`normalize_module_path` 规范模块路径；`resolve_module` 解析模块；`validate_case_mapping` 校验映射；`text_lines` 转换多行文本；`step_text` 提取步骤文本；`default_csv_name` 生成文件名；`safe_csv_name` 校验文件名；`_find_project_artifact` 查找产物；`export_csv` 导出 CSV；`write_csv_error` 写入错误；`main` 执行导出。 |
| `fetch_zentao_modules.py` | 通过 Playwright 登录禅道并采集产品模块树，写入项目参考文档。 | `_load_project_config` 读取配置；`_read_env` 读取环境变量；`_product_frame` 获取产品 iframe；`step1_login` 登录；`step2_click_product_menu` 进入产品菜单；`step3_click_top_product` 返回产品列表；`step4_click_product` 进入指定产品；`step5_click_rd_stories` 进入研发需求；`step6_read_module_tree` 读取模块树；`_parse_modules_from_html` 解析页面树；`_walk_tree` 遍历树；`_parse_modules_from_links` 从链接回退解析；`_write_output` 写参考文档；`main` 执行采集。 |
| `fetch_zentao_module_cases.py` | 通过 `zentao-cli` 只读获取指定产品、项目和模块下的测试用例，支持 JSON/Markdown。 | `parse_args` 解析参数；`run_cli` 查询并解析一页数据；`fetch_cases` 分页筛选模块用例；`case_id` 提取用例 ID；`markdown` 渲染 Markdown；`main` 执行查询和输出。 |
| `login_zentao.py` | 通过可视 Chromium 完成禅道登录，不保存凭据或登录状态。 | `LoginControls` 保存登录控件；`_build_parser` 构建参数；`_read_environment` 读取凭据；`_safe_location` 脱敏 URL；`_roots` 获取页面框架；`_visible` 判断控件可见性；`_attribute_signature` 生成控件特征；`_score_account` 评分账号框；`_score_submit` 评分提交按钮；`_choose_unique` 选择控件；`_discover_controls` 发现控件；`_visible_body_text` 获取页面文本；`_has_challenge` 检测验证码；`_has_visible_password` 检测密码框；`_has_visible_login_button` 检测登录按钮；`_login_succeeded` 判断登录结果；`_run` 执行登录；`main` 处理入口。 |
| `migrate_registry_to_req_groups.py` | 将旧注册表迁移为按 `req_id` 隔离的 v2 结构。 | `load` 读取 JSON；`migrate` 转换结构；`main` 执行迁移。 |
| `update_module_case_map.py` | 按需求隔离维护模块用例注册表，支持增删改、摘要刷新和隔离校验。 | `load_json` 读取 JSON；`dump_json` 写 JSON；`modules` 获取模块分组；`all_cases` 遍历用例；`refresh_summary` 刷新摘要；`validate_registry` 校验注册表；`validate_case` 校验单用例；`payload_cases` 提取载荷用例；`check_isolation` 校验隔离；`apply_operation` 执行变更；`persist` 持久化审计结果；`main` 执行维护。 |
| `zentao_create_testcase.py` | 按评审 YAML 创建或更新禅道用例，回读校验并更新注册表；支持 dry-run 以及带明确 ID、范围核对和确认参数的真实删除。真实删除成功并回读确认目标不存在后，直接移除注册表当前映射，历史结果保留在同步证据中。 | `SyncError` 同步异常；`sha256_file` 计算文件摘要；`load_yaml` 读取 YAML；`validate_shared_sync_config` 校验公共入口；`parse_module_reference` 解析模块参考；`resolve_module` 解析目标模块；`selected_cases` 选择用例；`load_case_details` 加载用例详情；`relative_to_project` 转换相对路径；`update_registry` 更新注册表；`build_common_preconditions_index` 建立前置条件索引；`_condition_key` 生成比较键；`_is_generic_access_data_condition` 识别泛化条件；`merge_precondition_items` 合并前置条件；`build_precondition_text` 生成前置文本；`build_create_payload` 生成创建载荷；`build_create_command` 生成创建命令；`build_update_command` 生成更新命令；`run_json` 执行命令并解析 JSON；`zentao_command` 定位 CLI；`remote_readback` 回读用例；`build_delete_command` 生成删除命令；`registry_delete_entry` 移除注册表当前映射；`is_remote_not_found` 识别明确不存在响应；`confirm_remote_deleted` 回读确认删除；`validate_delete_context` 校验删除归属；`validate_readback` 校验回读；`main` 执行同步流程。 |

### 测试、渲染与校验

| 文件 | 主要作用 | 顶层函数、类及作用 |
|---|---|---|
| `render_testcase_markdown.py` | 将测试用例 YAML 渲染为统一 Markdown 文档。 | `text` 转展示文本；`items` 转字符串列表；`condition_key` 生成去重键；`merged_preconditions` 合并前置条件；`metadata` 生成元数据；`render_case` 渲染单用例；`render` 渲染全文；`write_atomic` 原子写入；`main` 执行渲染。 |
| `validate_automation_judgment.py` | 校验自动化判定、原因码、命中条件和汇总信息的一致性。 | `validate_document` 校验文档；`main` 执行校验。 |
| `validate_case_atomicity.py` | 校验用例是否只有单一业务目的、数据基线和清晰分支。 | `_text` 规范化文本；`_data_baseline_count` 统计数据基线；`_branch_signals` 识别分支；`_related_assertion_exception` 判断相关断言例外；`_negative_assertion_safe_text` 提取负向断言；`_stepwise_same_baseline_exception` 判断同一基线；`validate_case` 校验单用例；`validate` 校验文档；`main` 执行校验。 |
| `validate_case_review.py` | 校验评审 YAML 的待同步清单、优先级和用例引用。 | `_items` 提取评审条目；`_validate_priority_review` 校验优先级及源文件一致性；`validate` 校验文件；`main` 执行校验。 |
| `validate_testcase_markdown.py` | 校验 Markdown 结构及其与源 YAML 的字段一致性。 | `value` 转展示值；`normalized` 规范化文本；`case_block` 提取用例区块；`validate` 执行校验；`main` 处理入口。 |
| `validate_testcase_template.py` | 校验测试用例 YAML、公共前置条件及可选 Markdown 是否符合模板约束。 | `ValidationError` 模板异常；`fail` 抛出校验错误；`require_mapping` 要求映射结构；`validate_common_preconditions` 校验前置条件；`validate_yaml` 校验 YAML；`validate_markdown` 校验 Markdown 引用；`main` 执行校验。 |
| `__init__.py` | 将 `scripts` 标记为 Python 包。 | 无顶层函数、类或方法。 |

### 测试文件

| 文件 | 主要作用 | 测试函数作用 |
|---|---|---|
| `test_automation_judgment.py` | 测试自动化判定校验器的有效、无效和汇总不一致场景。 | `case`/`document` 构造夹具；其余 `test_*` 函数分别验证 blocked、partial、手工用例、判定冲突和汇总冲突。 |
| `test_case_atomicity.py` | 回归测试多业务分支、数据基线和断言边界。 | `_case` 构造夹具；各 `test_*` 函数分别验证合并分支拒绝、独立分支接受、相关断言例外和多基线拒绝。 |
| `test_markdown_contract.py` | 测试 Markdown 渲染与校验契约。 | `document` 提供夹具；`test_render_and_validate` 验证渲染结果；其他测试验证占位符、字段不一致、旧索引格式和 YAML 可解析性。 |
| `test_schema_contracts.py` | 测试页面、设计和用例 JSON Schema 的结构契约。 | `load_schema` 加载 Schema；`valid_page_document`、`valid_design_document`、`valid_testcase` 创建夹具；各 `test_*` 函数验证有效结构及非法节点、坐标来源、无头采集和定位策略拒绝。 |
| `test_zentao_create_testcase_encoding.py` | 测试禅道同步载荷的 UTF-8、换行、特殊字符、前置条件和 BOM 解码。 | 各 `test_*` 函数分别验证字符保留、前置条件合并去重、非法引用/定义校验及 UTF-8 BOM 处理。 |

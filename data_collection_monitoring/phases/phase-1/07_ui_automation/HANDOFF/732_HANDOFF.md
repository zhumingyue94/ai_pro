# 732 UI 自动化交接（REQ-003）

- module_id：`732`
- 模块：`产品管理`
- RUN：`07_ui_automation/reports/RUN_20261102T015724Z/`
- 执行顺序（29 条）：`TC-REQ-003-002, TC-REQ-003-003, TC-REQ-003-004, TC-REQ-003-005, TC-REQ-003-006, TC-REQ-003-007, TC-REQ-003-010, TC-REQ-003-011, TC-REQ-003-016, TC-REQ-003-017, TC-REQ-003-018, TC-REQ-003-019, TC-REQ-003-020, TC-REQ-003-022, TC-REQ-003-026, TC-REQ-003-028, TC-REQ-003-030, TC-REQ-003-036, TC-REQ-003-037, TC-REQ-003-039, TC-REQ-003-040, TC-REQ-003-042, TC-REQ-003-045, TC-REQ-003-048, TC-REQ-003-049, TC-REQ-003-050, TC-REQ-003-051, TC-REQ-003-052, TC-REQ-003-053`
- 统计：total=29, passed=26, blocked=1, product_defect=1, excluded=1
- 缺陷数量：`1`（仅写入 `bug.xlsx`、`bugs_review.yaml` 与本文件，未创建远程 Bug）
- 阻塞数量：`1`；排除数量：`1`
- Allure 原始证据：`allure-results/`；仅当 Allure CLI 实际生成成功时保留 `allure-report/index.html`
- RUN 目录内不生成 Handoff.md

## 结果明细

- `TC-REQ-003-002`：passed — 九列表头正确，空字段以“-”占位，上传的图标与图片在列表和放大查看中均与源文件一致（['http://192.168.6.163:29000/sndao/20261102/req003-icon_1793584659444.png', 'http://192.168.6.163:29000/sndao/20261102/req003-image_1793584661971.png']）
- `TC-REQ-003-003`：passed — 按已知产品名称“照明灯”查询后仅返回 1 条匹配记录（默认 11 条）
- `TC-REQ-003-004`：passed — 按已知 ProductKey“D1Saayibq97IR6eG”查询后仅返回 1 条匹配记录（默认 11 条）
- `TC-REQ-003-005`：passed — 不存在条件（name=REQ-003-不存在的产品ZZZ999, key=REQ-003-NO-SUCH-KEY-ZZZ999）查询后列表为空并显示“暂无数据”，默认数据 11 条未展示
- `TC-REQ-003-006`：passed — 筛选条件（风扇 + 7jN3p）查询后 1 条，点击重置后名称与 ProductKey 均清空并恢复默认 11 条
- `TC-REQ-003-007`：passed — 点击刷新后列表重新加载，仍停留在第 1 页、/biopark-iot/iot/device/product 页面内共 11 条且记录一致
- `TC-REQ-003-010`：passed — 每页条数在 20/10 之间切换后行数分别符合 11/10 条，跳转页码 2 后当前页与列表同步更新
- `TC-REQ-003-011`：passed — 默认列表共 11 条，创建时间从 2026-10-30 15:25:31 到 2026-09-10 10:28:22 严格倒序，最新记录在最前
- `TC-REQ-003-016`：passed — 产品“排气扇”编辑页点击更多配置后，产品描述与产品图标、产品图片两个配置区域均可见（{'产品描述': True, '产品图标': True, '产品图片': True}）
- `TC-REQ-003-017`：passed — 编辑页回显产品“排气扇”信息，点击取消后关闭并返回列表，目标产品可见字段未变化
- `TC-REQ-003-018`：passed — 产品“排气扇”编辑页设备类型保持原值“直连设备”且全部选项禁用不可修改
- `TC-REQ-003-019`：passed — 新增产品分类下拉共 12 项，与启用分类 ['开关', '传感器', '表计', '灯', '网关', '风扇', '门磁', '产品分类-孵化设备', '养殖环控设备', '区域汇聚设备', '环境监测设备', '测试设备'] 一致，停用分类 ['智能插座', '饲喂饮水设备', '停用的产品分类'] 均不可选
- `TC-REQ-003-020`：passed — 产品名称留空提交后提示“产品名称不能为空”，表单保持打开未保存成功，列表仍为 共 11 条
- `TC-REQ-003-022`：passed — 产品“排气扇”编辑页 ProductKey 为 rp1XZJZj1ZWMe1sZ 且只读，重新生成按钮禁用不可点击
- `TC-REQ-003-026`：blocked — 未获得产品查看人员（只读）账号与已批准的查看/维护角色权限矩阵，无法验证只读账号可见查询但无新增/编辑/删除的权限边界；当前账号可用操作=['查询=True', '重置=True', '刷新=True', '表头设置=True', '导出=True', '新增=True']，行操作=['', '查看', '编辑', '物模型', '删除']，保持 blocked
- `TC-REQ-003-028`：passed — 状态列取值仅为“已发布/未发布”（['已发布', '未发布']），抽查 {'室外气象站': '已发布', '排气扇': '未发布'} 与物模型发布状态一致
- `TC-REQ-003-030`：passed — 分类“REQ-003-分类原名”改名为“REQ-003-分类新名”后，产品“REQ-003-分类同步”的产品分类字段同步显示新名称
- `TC-REQ-003-036`：passed — 租户 测试园区A 可见 11 条产品，租户 测试园区B 可见 1 条产品 ['孵化机（无线型）']，两侧无交集；跨租户隔离矩阵仍待批准矩阵确认（仅记录运行时可见范围）
- `TC-REQ-003-037`：passed — 名称与 ProductKey 同时匹配时仅返回 1 条（照明灯/D1Saayibq97IR6eG），名称不匹配时 0 条，默认 11 条
- `TC-REQ-003-039`：passed — ProductKey rp1XZJZj1ZWMe1sZ 的大写与小写输入均返回相同结果 ['排气扇']，页面采用大小写不敏感匹配
- `TC-REQ-003-040`：passed — 组合筛选后 1 条，点击重置两个条件均清空且恢复默认 11 条
- `TC-REQ-003-042`：passed — 物模型页面点击发布后提示“发布成功”，列表状态由“未发布”更新为“已发布”
- `TC-REQ-003-045`：passed — 点击确定后观察到保存中状态 ['loading', 'mask', 'disabled']（loading=True disabled=True mask=True），保存成功后列表回读一条记录
- `TC-REQ-003-048`：passed — 新增成功提示可见，回读 ProductKey BwqmpQAMOaWyPyxU、名称、分类 传感器、设备类型与未发布状态均一致，总数 11→12
- `TC-REQ-003-049`：passed — 修改成功提示可见，ProductKey u7aVITSZz0RmkN5Z 未变，名称与描述更新为新值且其他字段保持不变
- `TC-REQ-003-050`：passed — 删除确认层提示“是否删除所选中数据”，确认后显示删除成功，产品不可见且其他 11 条数据不受影响
- `TC-REQ-003-051`：passed — 撤销发布提示可见，产品状态由“已发布”回到“未发布”并保持列表可见
- `TC-REQ-003-052`：product_defect — 点击导出并确认后浏览器未生成可打开的导出文件（download_error=TimeoutError: Timeout 20000ms exceeded while waiting for event "download"，接口响应={'url': 'http://192.168.6.163:66/admin-api/iot/product/export-excel?pageNo=1&pageSize=10&name=%E7%85%A7
- `TC-REQ-003-053`：excluded — 用例 auto 字段为 no，按范围规则不纳入执行（未执行、不保留执行脚本）

## 已确认产品缺陷

- `TC-REQ-003-052`：点击导出并确认后浏览器未生成可打开的导出文件（download_error=TimeoutError: Timeout 20000ms exceeded while waiting for event "download"，接口响应={'url': 'http://192.168.6.163:66/admin-api/iot/product/export-excel?pageNo=1&pageSize=10&name=%E7%85%A7%E6%98%8E%E7%81%AF', 'status': 200, 'content_type': 'application/json', 'body_head': '{"code":500,"msg":"系统异常","data":null}'}）

## 阻塞与排除

- `TC-REQ-003-026`：未获得产品查看人员（只读）账号与已批准的查看/维护角色权限矩阵，无法验证只读账号可见查询但无新增/编辑/删除的权限边界；当前账号可用操作=['查询=True', '重置=True', '刷新=True', '表头设置=True', '导出=True', '新增=True']，行操作=['', '查看', '编辑', '物模型', '删除']，保持 blocked
- `TC-REQ-003-053`：用例 auto 字段为 no，按范围规则不纳入执行（未执行、不保留执行脚本）

## 证据路径

- 截图：`07_ui_automation/reports/RUN_20261102T015724Z/screenshots/`
- 视频：`07_ui_automation/reports/RUN_20261102T015724Z/videos/`
- 日志：`07_ui_automation/reports/RUN_20261102T015724Z/logs/`
- 哈希：`07_ui_automation/reports/RUN_20261102T015724Z/hashes/sha256.yaml`
- 结果：`07_ui_automation/reports/RUN_20261102T015724Z/results.yaml`


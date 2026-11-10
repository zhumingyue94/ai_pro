# REQ-PC-013 库存管理 / 二级蛋库 / 盘点记录 需求分析

> Analyze 阶段产物；不包含测试点、测试用例、CSV 或 UI 脚本。

## 1. 追溯与范围

- REQ-ID：`REQ-PC-013`
- 原型：`http://127.0.0.1:5500/`；页面树：57 页。
- 范围基线：`REQ-PC-013`；一致；对应原型第 41 页“盘点记录”。
- 页面捕获状态：`observed`；实际捕获 1 页。

## 2. 页面契约

| 页面 | frame URL | 板块数 | 控件数 | 弹窗数 | 注释数 |
|---|---|---:|---:|---:|---:|
| 盘点记录 | `http://127.0.0.1:5500/%E7%9B%98%E7%82%B9%E8%AE%B0%E5%BD%95_1.html` | 0 | 28 | 0 | 4 |

### 盘点记录

- 标题：盘点记录
- 正文行数：598
- 页面板块：
- 观察到的控件：
  - `u15889_input` INPUT/checkbox：checkbox
  - `u15890_input` INPUT/checkbox：checkbox
  - `u15891_input` INPUT/checkbox：checkbox
  - `u15892_input` INPUT/checkbox：checkbox
  - `u15893_input` INPUT/checkbox：checkbox
  - `u15894_input` INPUT/checkbox：checkbox
  - `u15895_input` INPUT/checkbox：checkbox
  - `u15896_input` INPUT/checkbox：checkbox
  - `u15897_input` INPUT/checkbox：checkbox
  - `u15898_input` INPUT/checkbox：checkbox
  - `u15899_input` INPUT/checkbox：checkbox
  - `u15905_input` SELECT/select-one：全部 是 否
  - `u15909_input` SELECT/select-one：全部养殖场 养殖场一 养殖场二 养殖场三
  - `u15912_input` SELECT/select-one：全部品种 AA 利丰
  - `u15914_input` INPUT/text：请输入周龄
  - `u15916_input` INPUT/date：
  - `u15917_input` INPUT/date：
  - `u15920_input` INPUT/date：
  - `u15921_input` INPUT/date：
  - `u15924_input` INPUT/text：请输入操作人
  - `u15926_input` SELECT/select-one：全部孵化场 孵化一场 孵化二场
  - `u15928_input` SELECT/select-one：全部仓库类型 二级蛋蛋库
  - `u15929_input` INPUT/text：请输入养殖批次
  - `u15931_input` SELECT/select-one：全部种蛋类型 二级蛋
  - `u15933_input` SELECT/select-one：全部蛋重类型 大 中 小
  - `u15935_input` INPUT/text：请输入平均蛋重
  - `u15937_input` SELECT/select-one：全部仓库 北一号仓库 北二号仓库 南一号仓库
  - `u15939_input` INPUT/text：请输入库位号
- 弹窗/状态面板：未捕获当前页面真实弹窗
- 页面注释：
  - 库位号：盘点记录如果是因为同一个库位号同时混装了多种蛋，产生了虚拟库位的，则此处记录的库位号为当时的虚拟库位号，并且标记“混”。
  - 该页面为登录账号权限范围下所有仓库，盘点记录页。
  - 是否差异、差异数量： 1、是否差异：展示盘点数量与库存数量是否有差异； 2、差异数量：比较盘点数量与库存数量之间的差异值，盘点入库为正数，盘点出库为负数，盘点一致为0.
  - 关于筛选条件的说明： 1、孵化场、仓库可多选（待研发情况定）； 2、孵化场、养殖场为树形结构选择； 3、库位号、养殖批次为关键字查询，输入过程中查询现有关键字匹配库位号、养殖批次，下拉推荐选择项，可快速选择； 4、种蛋类型：默认只有合格蛋（此处待研发情况确定，如果入库时不做明确限制，此处可保留筛选，如果做了明确限制，则无种蛋类型筛选）； 是否差异： 全部 是 否 搜索 重置 养殖场： 全部养殖场 养殖场一 养殖场二 养殖场三 养殖批次： 品种： 全部品种 AA 利丰 周龄： 产蛋日期： ~ 盘点日期： ~ 操作人： 孵化场： 全部孵化场 孵化一场 孵化二场 仓库类型： 全部仓库类型 二级蛋蛋库 种蛋类型： 全部种蛋类型 二级蛋 蛋重类型： 全部蛋重类型 大 中 小 平均蛋重： 仓库： 全部仓库 北一号仓库 北二号仓库 南一号仓库 库位号：

## 3. interfaces

| 名称 | 类型 | 来源/目标 | 说明 |
|---|---|---|---|
| 依赖模块 | module_dependency | REQ-PC-010 | 依赖字段、状态和权限由依赖模块确认 |
| 依赖模块 | module_dependency | REQ-PC-012 | 依赖字段、状态和权限由依赖模块确认 |
| 页面内导航 | prototype_navigation | live prototype | ['上孵计划列表', '仓库全景图（待定）', '仓库管理', '出入库记录', '出雏器全景图（待定）', '出雏器管理', '受健率标准管理', '品种管理', '存发苗间管理', '孵化周期管理', '孵化器全景图（待定）', '孵化器管理', '库存查询', '生产报表', '盘点记录', '种蛋上孵任务', '种蛋出雏任务', '种蛋照蛋任务', '蛋重类型管理'] |

## 4. cross_module_refs

| 字段 | 来源模块 | 外部数据 |
|---|---|---|
| 盘点记录 | REQ-PC-010 | ['依赖模块'] |
| 盘点记录 | REQ-PC-012 | ['依赖模块'] |
| 页面内导航 | live prototype | ['上孵计划列表', '仓库全景图（待定）', '仓库管理', '出入库记录', '出雏器全景图（待定）', '出雏器管理', '受健率标准管理', '品种管理', '存发苗间管理', '孵化周期管理', '孵化器全景图（待定）', '孵化器管理', '库存查询', '生产报表', '盘点记录', '种蛋上孵任务', '种蛋出雏任务', '种蛋照蛋任务', '蛋重类型管理'] |

## 5. business_rules

- **BR-001**：库位号：盘点记录如果是因为同一个库位号同时混装了多种蛋，产生了虚拟库位的，则此处记录的库位号为当时的虚拟库位号，并且标记“混”。（live prototype annotation / related requirement page）
- **BR-002**：该页面为登录账号权限范围下所有仓库，盘点记录页。（live prototype annotation / related requirement page）
- **BR-003**：是否差异、差异数量： 1、是否差异：展示盘点数量与库存数量是否有差异； 2、差异数量：比较盘点数量与库存数量之间的差异值，盘点入库为正数，盘点出库为负数，盘点一致为0.（live prototype annotation / related requirement page）
- **BR-004**：关于筛选条件的说明： 1、孵化场、仓库可多选（待研发情况定）； 2、孵化场、养殖场为树形结构选择； 3、库位号、养殖批次为关键字查询，输入过程中查询现有关键字匹配库位号、养殖批次，下拉推荐选择项，可快速选择； 4、种蛋类型：默认只有合格蛋（此处待研发情况确定，如果入库时不做明确限制，此处可保留筛选，如果做了明确限制，则无种蛋类型筛选）； 是否差异： 全部 是 否 搜索 重置 养殖场： 全部养殖场 养殖场一 养殖场二 养殖场三 养殖批次： 品种： 全部品种 AA 利丰 周龄： 产蛋日期： ~ 盘点日期： ~ 操作人： 孵化场： 全部孵化场 孵化一场 孵化二场 仓库类型： 全部仓库类型 二级蛋蛋库 种蛋类型： 全部种蛋类型 二级蛋 蛋重类型： 全部蛋重类型 大 中 小 平均蛋重： 仓库： 全部仓库 北一号仓库 北二号仓库 南一号仓库 库位号：（live prototype annotation / related requirement page）

## 6. open_questions

- **OQ-001**：真实接口、权限、异常提示和字段校验规则是什么？；影响：影响正式契约与下游测试点；阻塞：True

## 7. Handoff Report

- **Agent**: analyze-agent
- **Project**: 种禽孵化管理系统
- **Req ID**: REQ-PC-013
- **Outputs**: `02_analysis/pc/REQ-PC-013.yaml`; `02_analysis/pc/REQ-PC-013_盘点记录.md`
- **Gate**: passed
- **Next Agent**: testpoint-agent
- **Blockers**: none

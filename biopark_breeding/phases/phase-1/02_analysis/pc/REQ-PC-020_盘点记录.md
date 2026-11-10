# REQ-PC-020 库存管理 / 次品库 / 盘点记录 需求分析

> Analyze 阶段产物；不包含测试点、测试用例、CSV 或 UI 脚本。

## 1. 追溯与范围

- REQ-ID：`REQ-PC-020`
- 原型：`http://127.0.0.1:5500/`；页面树：57 页。
- 范围基线：`REQ-PC-020`；一致；对应原型第 46 页“盘点记录”。
- 页面捕获状态：`observed`；实际捕获 1 页。

## 2. 页面契约

| 页面 | frame URL | 板块数 | 控件数 | 弹窗数 | 注释数 |
|---|---|---:|---:|---:|---:|
| 盘点记录 | `http://127.0.0.1:5500/%E7%9B%98%E7%82%B9%E8%AE%B0%E5%BD%95_2.html` | 0 | 18 | 0 | 3 |

### 盘点记录

- 标题：盘点记录
- 正文行数：361
- 页面板块：
- 观察到的控件：
  - `u18082_input` SELECT/select-one：全部仓库 北一号仓库 北二号仓库 南一号仓库
  - `u18206_input` INPUT/checkbox：checkbox
  - `u18207_input` INPUT/checkbox：checkbox
  - `u18208_input` INPUT/checkbox：checkbox
  - `u18209_input` INPUT/checkbox：checkbox
  - `u18210_input` INPUT/checkbox：checkbox
  - `u18211_input` INPUT/checkbox：checkbox
  - `u18212_input` INPUT/checkbox：checkbox
  - `u18213_input` INPUT/checkbox：checkbox
  - `u18214_input` INPUT/checkbox：checkbox
  - `u18215_input` INPUT/checkbox：checkbox
  - `u18216_input` INPUT/checkbox：checkbox
  - `u18218_input` SELECT/select-one：全部 是 否
  - `u18220_input` INPUT/date：
  - `u18221_input` INPUT/date：
  - `u18224_input` INPUT/text：请输入操作人
  - `u18226_input` SELECT/select-one：全部类型 无精蛋 死胚蛋 毛蛋 大蛋 小蛋 破损蛋 弱雏
  - `u18228_input` SELECT/select-one：全部孵化场 孵化一场 孵化二场
- 弹窗/状态面板：未捕获当前页面真实弹窗
- 页面注释：
  - 该页面为登录账号权限范围下所有仓库，盘点记录页。
  - 是否差异、差异数量： 1、是否差异：展示盘点数量与库存数量是否有差异； 2、差异数量：比较盘点数量与库存数量之间的差异值，盘点入库为正数，盘点出库为负数，盘点一致为0.
  - 关于筛选条件的说明： 1、孵化场、仓库可多选（待研发情况定）； 2、孵化场、养殖场为树形结构选择；

## 3. interfaces

| 名称 | 类型 | 来源/目标 | 说明 |
|---|---|---|---|
| 依赖模块 | module_dependency | REQ-PC-017 | 依赖字段、状态和权限由依赖模块确认 |
| 依赖模块 | module_dependency | REQ-PC-019 | 依赖字段、状态和权限由依赖模块确认 |
| 页面内导航 | prototype_navigation | live prototype | ['上孵计划列表', '仓库全景图（待定）', '仓库管理', '出入库记录', '出雏器全景图（待定）', '出雏器管理', '受健率标准管理', '品种管理', '存发苗间管理', '孵化周期管理', '孵化器全景图（待定）', '孵化器管理', '库存查询', '生产报表', '盘点记录', '种蛋上孵任务', '种蛋出雏任务', '种蛋照蛋任务', '蛋重类型管理'] |

## 4. cross_module_refs

| 字段 | 来源模块 | 外部数据 |
|---|---|---|
| 盘点记录 | REQ-PC-017 | ['依赖模块'] |
| 盘点记录 | REQ-PC-019 | ['依赖模块'] |
| 页面内导航 | live prototype | ['上孵计划列表', '仓库全景图（待定）', '仓库管理', '出入库记录', '出雏器全景图（待定）', '出雏器管理', '受健率标准管理', '品种管理', '存发苗间管理', '孵化周期管理', '孵化器全景图（待定）', '孵化器管理', '库存查询', '生产报表', '盘点记录', '种蛋上孵任务', '种蛋出雏任务', '种蛋照蛋任务', '蛋重类型管理'] |

## 5. business_rules

- **BR-001**：该页面为登录账号权限范围下所有仓库，盘点记录页。（live prototype annotation / related requirement page）
- **BR-002**：是否差异、差异数量： 1、是否差异：展示盘点数量与库存数量是否有差异； 2、差异数量：比较盘点数量与库存数量之间的差异值，盘点入库为正数，盘点出库为负数，盘点一致为0.（live prototype annotation / related requirement page）
- **BR-003**：关于筛选条件的说明： 1、孵化场、仓库可多选（待研发情况定）； 2、孵化场、养殖场为树形结构选择；（live prototype annotation / related requirement page）

## 6. open_questions

- **OQ-001**：真实接口、权限、异常提示和字段校验规则是什么？；影响：影响正式契约与下游测试点；阻塞：True

## 7. Handoff Report

- **Agent**: analyze-agent
- **Project**: 种禽孵化管理系统
- **Req ID**: REQ-PC-020
- **Outputs**: `02_analysis/pc/REQ-PC-020.yaml`; `02_analysis/pc/REQ-PC-020_盘点记录.md`
- **Gate**: passed
- **Next Agent**: testpoint-agent
- **Blockers**: none

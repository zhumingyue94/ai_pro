# REQ-PC-016 库存管理 / 存发苗间 / 盘点记录 需求分析

> Analyze 阶段产物；不包含测试点、测试用例、CSV 或 UI 脚本。

## 1. 追溯与范围

- REQ-ID：`REQ-PC-016`
- 原型：`http://127.0.0.1:5500/`；页面树：57 页。
- 范围基线：`REQ-PC-016`；一致；对应原型第 49 页“盘点记录”。
- 页面捕获状态：`observed`；实际捕获 1 页。

## 2. 页面契约

| 页面 | frame URL | 板块数 | 控件数 | 弹窗数 | 注释数 |
|---|---|---:|---:|---:|---:|
| 盘点记录 | `http://127.0.0.1:5500/%E7%9B%98%E7%82%B9%E8%AE%B0%E5%BD%95_3.html` | 0 | 24 | 0 | 3 |

### 盘点记录

- 标题：盘点记录
- 正文行数：482
- 页面板块：
- 观察到的控件：
  - `u19466_input` SELECT/select-one：全部仓库 北一号仓库 北二号仓库 南一号仓库
  - `u19468_input` SELECT/select-one：全部养殖场 养殖场一 养殖场二 养殖场三
  - `u19471_input` SELECT/select-one：全部品种 AA 利丰
  - `u19650_input` INPUT/checkbox：checkbox
  - `u19651_input` INPUT/checkbox：checkbox
  - `u19652_input` INPUT/checkbox：checkbox
  - `u19653_input` INPUT/checkbox：checkbox
  - `u19654_input` INPUT/checkbox：checkbox
  - `u19655_input` INPUT/checkbox：checkbox
  - `u19656_input` INPUT/checkbox：checkbox
  - `u19657_input` INPUT/checkbox：checkbox
  - `u19658_input` INPUT/checkbox：checkbox
  - `u19659_input` INPUT/checkbox：checkbox
  - `u19660_input` INPUT/checkbox：checkbox
  - `u19662_input` SELECT/select-one：全部 是 否
  - `u19664_input` INPUT/date：
  - `u19665_input` INPUT/date：
  - `u19668_input` INPUT/text：请输入操作人
  - `u19670_input` SELECT/select-one：全部类型 健雏
  - `u19672_input` SELECT/select-one：全部孵化场 孵化一场 孵化二场
  - `u19673_input` INPUT/text：请输入养殖批次
  - `u19675_input` INPUT/date：
  - `u19676_input` INPUT/date：
  - `u19679_input` INPUT/text：请输入养殖批次
- 弹窗/状态面板：未捕获当前页面真实弹窗
- 页面注释：
  - 鸡苗类型：只有健雏。
  - 出苗日期：种蛋出雏任务完成日期。
  - 是否差异、差异数量： 1、是否差异：展示盘点数量与库存数量是否有差异； 2、差异数量：比较盘点数量与库存数量之间的差异值，盘点入库为正数，盘点出库为负数，盘点一致为0.

## 3. interfaces

| 名称 | 类型 | 来源/目标 | 说明 |
|---|---|---|---|
| 依赖模块 | module_dependency | REQ-PC-014 | 依赖字段、状态和权限由依赖模块确认 |
| 依赖模块 | module_dependency | REQ-PC-015 | 依赖字段、状态和权限由依赖模块确认 |
| 页面内导航 | prototype_navigation | live prototype | ['上孵计划列表', '仓库全景图（待定）', '仓库管理', '出入库记录', '出雏器全景图（待定）', '出雏器管理', '受健率标准管理', '品种管理', '存发苗间管理', '孵化周期管理', '孵化器全景图（待定）', '孵化器管理', '库存查询', '生产报表', '盘点记录', '种蛋上孵任务', '种蛋出雏任务', '种蛋照蛋任务', '蛋重类型管理'] |

## 4. cross_module_refs

| 字段 | 来源模块 | 外部数据 |
|---|---|---|
| 盘点记录 | REQ-PC-014 | ['依赖模块'] |
| 盘点记录 | REQ-PC-015 | ['依赖模块'] |
| 页面内导航 | live prototype | ['上孵计划列表', '仓库全景图（待定）', '仓库管理', '出入库记录', '出雏器全景图（待定）', '出雏器管理', '受健率标准管理', '品种管理', '存发苗间管理', '孵化周期管理', '孵化器全景图（待定）', '孵化器管理', '库存查询', '生产报表', '盘点记录', '种蛋上孵任务', '种蛋出雏任务', '种蛋照蛋任务', '蛋重类型管理'] |

## 5. business_rules

- **BR-001**：鸡苗类型：只有健雏。（live prototype annotation / related requirement page）
- **BR-002**：出苗日期：种蛋出雏任务完成日期。（live prototype annotation / related requirement page）
- **BR-003**：是否差异、差异数量： 1、是否差异：展示盘点数量与库存数量是否有差异； 2、差异数量：比较盘点数量与库存数量之间的差异值，盘点入库为正数，盘点出库为负数，盘点一致为0.（live prototype annotation / related requirement page）

## 6. open_questions

- **OQ-001**：真实接口、权限、异常提示和字段校验规则是什么？；影响：影响正式契约与下游测试点；阻塞：True

## 7. Handoff Report

- **Agent**: analyze-agent
- **Project**: 种禽孵化管理系统
- **Req ID**: REQ-PC-016
- **Outputs**: `02_analysis/pc/REQ-PC-016.yaml`; `02_analysis/pc/REQ-PC-016_盘点记录.md`
- **Gate**: passed
- **Next Agent**: testpoint-agent
- **Blockers**: none

# REQ-PC-015 库存管理 / 存发苗间 / 出入库记录 需求分析

> Analyze 阶段产物；不包含测试点、测试用例、CSV 或 UI 脚本。

## 1. 追溯与范围

- REQ-ID：`REQ-PC-015`
- 原型：`http://127.0.0.1:5500/`；页面树：57 页。
- 范围基线：`REQ-PC-015`；一致；禅道节点与原型页面可直接对齐，原型第 48 页。
- 页面捕获状态：`observed`；实际捕获 1 页。

## 2. 页面契约

| 页面 | frame URL | 板块数 | 控件数 | 弹窗数 | 注释数 |
|---|---|---:|---:|---:|---:|
| 出入库记录 | `http://127.0.0.1:5500/%E5%87%BA%E5%85%A5%E5%BA%93%E8%AE%B0%E5%BD%95_3.html` | 0 | 27 | 0 | 5 |

### 出入库记录

- 标题：出入库记录
- 正文行数：536
- 页面板块：
- 观察到的控件：
  - `u19323_input` INPUT/checkbox：checkbox
  - `u19324_input` INPUT/checkbox：checkbox
  - `u19325_input` INPUT/checkbox：checkbox
  - `u19326_input` INPUT/checkbox：checkbox
  - `u19327_input` INPUT/checkbox：checkbox
  - `u19328_input` INPUT/checkbox：checkbox
  - `u19329_input` INPUT/checkbox：checkbox
  - `u19330_input` INPUT/checkbox：checkbox
  - `u19331_input` INPUT/checkbox：checkbox
  - `u19332_input` INPUT/checkbox：checkbox
  - `u19333_input` INPUT/checkbox：checkbox
  - `u19340_input` SELECT/select-one：全部类型 入库 出库
  - `u19342_input` SELECT/select-one：全部方式 自动 手动
  - `u19344_input` INPUT/date：
  - `u19345_input` INPUT/date：
  - `u19350_input` SELECT/select-one：全部仓库 北一号仓库 北二号仓库 南一号仓库
  - `u19352_input` SELECT/select-one：全部养殖场 养殖场一 养殖场二 养殖场三
  - `u19355_input` SELECT/select-one：全部品种 AA 利丰
  - `u19357_input` INPUT/text：请输入操作人
  - `u19359_input` INPUT/text：请输入上孵计划号
  - `u19361_input` SELECT/select-one：全部孵化场 孵化一场 孵化二场
  - `u19363_input` SELECT/select-one：全部原因 鸡苗挑选 其他
  - `u19365_input` SELECT/select-one：全部类型 健雏
  - `u19366_input` INPUT/text：请输入养殖批次
  - `u19370_input` INPUT/date：
  - `u19371_input` INPUT/date：
  - `u19374_input` INPUT/text：请输入养殖批次
- 弹窗/状态面板：未捕获当前页面真实弹窗
- 页面注释：
  - 关于操作类型、方式、原因的说明： 1、操作类型：入库、出库； 2、方式：手动、自动；①手动：在仓库中点击出入库进行的入库操作数据；②自动：盘点及任务执行过程中系统自动进行的出入库操作数据； 3、原因：出入库的原因，不同操作类型、方式对应的原因不同： ①入库——手动：种蛋出雏、其他； ②入库——自动：种蛋出雏、盘点； ③出库——手动：销售、其他； ④出库——自动：盘点。
  - 上孵计划号：如果是来自计划任务的出入库，有上孵计划号，否则没有上孵计划号。 出苗日期： ~ 平均苗重：
  - 鸡苗类型：只有健雏。
  - 出苗日期：种蛋出雏任务完成日期。
  - 养殖客户：只有出库的时候有养殖客户，入库没有。

## 3. interfaces

| 名称 | 类型 | 来源/目标 | 说明 |
|---|---|---|---|
| 依赖模块 | module_dependency | REQ-PC-014 | 依赖字段、状态和权限由依赖模块确认 |
| 依赖模块 | module_dependency | REQ-PC-005 | 依赖字段、状态和权限由依赖模块确认 |
| 页面内导航 | prototype_navigation | live prototype | ['上孵计划列表', '仓库全景图（待定）', '仓库管理', '出入库记录', '出雏器全景图（待定）', '出雏器管理', '受健率标准管理', '品种管理', '存发苗间管理', '孵化周期管理', '孵化器全景图（待定）', '孵化器管理', '库存查询', '生产报表', '盘点记录', '种蛋上孵任务', '种蛋出雏任务', '种蛋照蛋任务', '蛋重类型管理'] |

## 4. cross_module_refs

| 字段 | 来源模块 | 外部数据 |
|---|---|---|
| 出入库记录 | REQ-PC-014 | ['依赖模块'] |
| 出入库记录 | REQ-PC-005 | ['依赖模块'] |
| 页面内导航 | live prototype | ['上孵计划列表', '仓库全景图（待定）', '仓库管理', '出入库记录', '出雏器全景图（待定）', '出雏器管理', '受健率标准管理', '品种管理', '存发苗间管理', '孵化周期管理', '孵化器全景图（待定）', '孵化器管理', '库存查询', '生产报表', '盘点记录', '种蛋上孵任务', '种蛋出雏任务', '种蛋照蛋任务', '蛋重类型管理'] |

## 5. business_rules

- **BR-001**：关于操作类型、方式、原因的说明： 1、操作类型：入库、出库； 2、方式：手动、自动；①手动：在仓库中点击出入库进行的入库操作数据；②自动：盘点及任务执行过程中系统自动进行的出入库操作数据； 3、原因：出入库的原因，不同操作类型、方式对应的原因不同： ①入库——手动：种蛋出雏、其他； ②入库——自动：种蛋出雏、盘点； ③出库——手动：销售、其他； ④出库——自动：盘点。（live prototype annotation / related requirement page）
- **BR-002**：上孵计划号：如果是来自计划任务的出入库，有上孵计划号，否则没有上孵计划号。 出苗日期： ~ 平均苗重：（live prototype annotation / related requirement page）
- **BR-003**：鸡苗类型：只有健雏。（live prototype annotation / related requirement page）
- **BR-004**：出苗日期：种蛋出雏任务完成日期。（live prototype annotation / related requirement page）
- **BR-005**：养殖客户：只有出库的时候有养殖客户，入库没有。（live prototype annotation / related requirement page）

## 6. open_questions

- **OQ-001**：真实接口、权限、异常提示和字段校验规则是什么？；影响：影响正式契约与下游测试点；阻塞：True

## 7. Handoff Report

- **Agent**: analyze-agent
- **Project**: 种禽孵化管理系统
- **Req ID**: REQ-PC-015
- **Outputs**: `02_analysis/pc/REQ-PC-015.yaml`; `02_analysis/pc/REQ-PC-015_出入库记录.md`
- **Gate**: passed
- **Next Agent**: testpoint-agent
- **Blockers**: none

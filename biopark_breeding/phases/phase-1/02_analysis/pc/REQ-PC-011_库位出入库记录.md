# REQ-PC-011 库存管理 / 二级蛋库 / 库位出入库记录 需求分析

> Analyze 阶段产物；不包含测试点、测试用例、CSV 或 UI 脚本。

## 1. 追溯与范围

- REQ-ID：`REQ-PC-011`
- 原型：`http://127.0.0.1:5500/`；页面树：57 页。
- 范围基线：`REQ-PC-011`；原型单独提供“库位出入库记录”；禅道仅有“出入库记录”节点，建议拆为独立需求。
- 页面捕获状态：`observed`；实际捕获 1 页。

## 2. 页面契约

| 页面 | frame URL | 板块数 | 控件数 | 弹窗数 | 注释数 |
|---|---|---:|---:|---:|---:|
| 库位出入库记录 | `http://127.0.0.1:5500/%E5%BA%93%E4%BD%8D%E5%87%BA%E5%85%A5%E5%BA%93%E8%AE%B0%E5%BD%95_1.html` | 0 | 18 | 0 | 6 |

### 库位出入库记录

- 标题：库位出入库记录
- 正文行数：574
- 页面板块：
- 观察到的控件：
  - `u15177_input` INPUT/checkbox：checkbox
  - `u15178_input` INPUT/checkbox：checkbox
  - `u15179_input` INPUT/checkbox：checkbox
  - `u15180_input` INPUT/checkbox：checkbox
  - `u15181_input` INPUT/checkbox：checkbox
  - `u15182_input` INPUT/checkbox：checkbox
  - `u15183_input` INPUT/checkbox：checkbox
  - `u15184_input` INPUT/checkbox：checkbox
  - `u15185_input` INPUT/checkbox：checkbox
  - `u15186_input` INPUT/checkbox：checkbox
  - `u15187_input` INPUT/checkbox：checkbox
  - `u15195_input` SELECT/select-one：全部类型 入库 出库
  - `u15197_input` SELECT/select-one：全部方式 自动 手动
  - `u15199_input` INPUT/date：
  - `u15200_input` INPUT/date：
  - `u15205_input` SELECT/select-one：全部原因 种蛋上孵 鸡苗挑选 销售
  - `u15207_input` INPUT/text：请输入操作人
  - `u15209_input` INPUT/text：请输入上孵计划号
- 弹窗/状态面板：未捕获当前页面真实弹窗
- 页面注释：
  - 原因，根据类型、方式对应变动选项。 搜索 重置 出/入库： 全部类型 入库 出库 方式： 全部方式 自动 手动 出入库日期： ~ 出入库记录 原因： 全部原因 种蛋上孵 鸡苗挑选 销售 操作人： 计划号：
  - 库位号：出入库记录如果是因为同一个库位号同时混装了多种蛋，产生了虚拟库位的记录，则此处记录的库位号为当时的虚拟库位号，并且标记“混”。
  - 关于操作类型、方式、原因的说明： 1、操作类型：入库、出库； 2、方式：手动、自动；①手动：在仓库中点击出入库进行的入库操作数据；②自动：盘点及任务执行过程中系统自动进行的出入库操作数据； 3、原因：出入库的原因，不同操作类型、方式对应的原因不同： ①入库——手动：种蛋挑选、其他； ②入库——自动：盘点；（目前功能范围中，没有任务过程中的自动入库） ③出库——手动：种蛋上孵、销售、更换仓库、其他； ④出库——自动：种蛋上孵、盘点。
  - 上孵计划号：如果是来自计划任务的地总出入库，有上孵计划号，否则没有上孵计划号。
  - 出入库记录，按照出入库类型、时间、种蛋、库位号独立生成操作记录。
  - 该页面为某一库位出入库记录页。

## 3. interfaces

| 名称 | 类型 | 来源/目标 | 说明 |
|---|---|---|---|
| 依赖模块 | module_dependency | REQ-PC-010 | 依赖字段、状态和权限由依赖模块确认 |
| 依赖模块 | module_dependency | REQ-PC-031 | 依赖字段、状态和权限由依赖模块确认 |
| 页面内导航 | prototype_navigation | live prototype | ['上孵计划列表', '仓库全景图（待定）', '仓库管理', '出入库记录', '出雏器全景图（待定）', '出雏器管理', '受健率标准管理', '品种管理', '存发苗间管理', '孵化周期管理', '孵化器全景图（待定）', '孵化器管理', '库存查询', '生产报表', '盘点记录', '种蛋上孵任务', '种蛋出雏任务', '种蛋照蛋任务', '蛋重类型管理'] |

## 4. cross_module_refs

| 字段 | 来源模块 | 外部数据 |
|---|---|---|
| 库位出入库记录 | REQ-PC-010 | ['依赖模块'] |
| 库位出入库记录 | REQ-PC-031 | ['依赖模块'] |
| 页面内导航 | live prototype | ['上孵计划列表', '仓库全景图（待定）', '仓库管理', '出入库记录', '出雏器全景图（待定）', '出雏器管理', '受健率标准管理', '品种管理', '存发苗间管理', '孵化周期管理', '孵化器全景图（待定）', '孵化器管理', '库存查询', '生产报表', '盘点记录', '种蛋上孵任务', '种蛋出雏任务', '种蛋照蛋任务', '蛋重类型管理'] |

## 5. business_rules

- **BR-001**：原因，根据类型、方式对应变动选项。 搜索 重置 出/入库： 全部类型 入库 出库 方式： 全部方式 自动 手动 出入库日期： ~ 出入库记录 原因： 全部原因 种蛋上孵 鸡苗挑选 销售 操作人： 计划号：（live prototype annotation / related requirement page）
- **BR-002**：库位号：出入库记录如果是因为同一个库位号同时混装了多种蛋，产生了虚拟库位的记录，则此处记录的库位号为当时的虚拟库位号，并且标记“混”。（live prototype annotation / related requirement page）
- **BR-003**：关于操作类型、方式、原因的说明： 1、操作类型：入库、出库； 2、方式：手动、自动；①手动：在仓库中点击出入库进行的入库操作数据；②自动：盘点及任务执行过程中系统自动进行的出入库操作数据； 3、原因：出入库的原因，不同操作类型、方式对应的原因不同： ①入库——手动：种蛋挑选、其他； ②入库——自动：盘点；（目前功能范围中，没有任务过程中的自动入库） ③出库——手动：种蛋上孵、销售、更换仓库、其他； ④出库——自动：种蛋上孵、盘点。（live prototype annotation / related requirement page）
- **BR-004**：上孵计划号：如果是来自计划任务的地总出入库，有上孵计划号，否则没有上孵计划号。（live prototype annotation / related requirement page）
- **BR-005**：出入库记录，按照出入库类型、时间、种蛋、库位号独立生成操作记录。（live prototype annotation / related requirement page）
- **BR-006**：该页面为某一库位出入库记录页。（live prototype annotation / related requirement page）

## 6. open_questions

- **OQ-001**：真实接口、权限、异常提示和字段校验规则是什么？；影响：影响正式契约与下游测试点；阻塞：True

## 7. Handoff Report

- **Agent**: analyze-agent
- **Project**: 种禽孵化管理系统
- **Req ID**: REQ-PC-011
- **Outputs**: `02_analysis/pc/REQ-PC-011.yaml`; `02_analysis/pc/REQ-PC-011_库位出入库记录.md`
- **Gate**: passed
- **Next Agent**: testpoint-agent
- **Blockers**: none

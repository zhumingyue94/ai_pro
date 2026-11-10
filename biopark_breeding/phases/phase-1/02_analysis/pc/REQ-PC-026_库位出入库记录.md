# REQ-PC-026 出雏器管理 / 库位出入库记录 需求分析

> Analyze 阶段产物；不包含测试点、测试用例、CSV 或 UI 脚本。

## 1. 追溯与范围

- REQ-ID：`REQ-PC-026`
- 原型：`http://127.0.0.1:5500/`；页面树：57 页。
- 范围基线：`REQ-PC-026`；原型单独提供“库位出入库记录”；禅道仅有“出入库记录”节点，建议拆为独立需求。
- 页面捕获状态：`observed`；实际捕获 1 页。

## 2. 页面契约

| 页面 | frame URL | 板块数 | 控件数 | 弹窗数 | 注释数 |
|---|---|---:|---:|---:|---:|
| 库位出入库记录 | `http://127.0.0.1:5500/%E5%BA%93%E4%BD%8D%E5%87%BA%E5%85%A5%E5%BA%93%E8%AE%B0%E5%BD%95_3.html` | 0 | 16 | 0 | 6 |

### 库位出入库记录

- 标题：库位出入库记录
- 正文行数：545
- 页面板块：
- 观察到的控件：
  - `u22801_input` INPUT/checkbox：checkbox
  - `u22802_input` INPUT/checkbox：checkbox
  - `u22803_input` INPUT/checkbox：checkbox
  - `u22804_input` INPUT/checkbox：checkbox
  - `u22805_input` INPUT/checkbox：checkbox
  - `u22806_input` INPUT/checkbox：checkbox
  - `u22807_input` INPUT/checkbox：checkbox
  - `u22808_input` INPUT/checkbox：checkbox
  - `u22809_input` INPUT/checkbox：checkbox
  - `u22810_input` INPUT/checkbox：checkbox
  - `u22811_input` INPUT/checkbox：checkbox
  - `u22816_input` SELECT/select-one：全部类型 入库 出库
  - `u22818_input` INPUT/date：
  - `u22819_input` INPUT/date：
  - `u22826_input` INPUT/text：请输入上孵计划号
  - `u22828_input` INPUT/text：请输入操作人
- 弹窗/状态面板：未捕获当前页面真实弹窗
- 页面注释：
  - 出雏器的出入库均为自动出入库，入库：种蛋照蛋；出库：种蛋出雏。
  - 库位号：出入库记录如果是因为同一个库位号同时混装了多种蛋，产生了虚拟库位的记录，则此处记录的库位号为当时的虚拟库位号，并且标记“混”。
  - 关于操作类型、方式、原因的说明： 1、操作类型：入库、出库； 2、方式：自动；出雏器只有自动出入库，没有手动出入库，自动盘点及任务执行过程中系统自动进行的出入库操作数据； 3、原因：出入库的原因，不同操作类型、方式对应的原因不同： ①入库——自动：种蛋照蛋； ②出库——自动：种蛋出雏。
  - 上孵计划号：所有出入库记录均来自上孵计划的任务，所有总有上孵计划号。
  - 出入库记录，按照出入库类型、时间、种蛋、库位号独立生成操作记录。
  - 该页面为某一库位出入库记录页。

## 3. interfaces

| 名称 | 类型 | 来源/目标 | 说明 |
|---|---|---|---|
| 依赖模块 | module_dependency | REQ-PC-025 | 依赖字段、状态和权限由依赖模块确认 |
| 依赖模块 | module_dependency | REQ-PC-034 | 依赖字段、状态和权限由依赖模块确认 |
| 页面内导航 | prototype_navigation | live prototype | ['上孵计划列表', '仓库全景图（待定）', '仓库管理', '出入库记录', '出雏器全景图（待定）', '出雏器管理', '受健率标准管理', '品种管理', '存发苗间管理', '孵化周期管理', '孵化器全景图（待定）', '孵化器管理', '库存查询', '生产报表', '盘点记录', '种蛋上孵任务', '种蛋出雏任务', '种蛋照蛋任务', '蛋重类型管理'] |

## 4. cross_module_refs

| 字段 | 来源模块 | 外部数据 |
|---|---|---|
| 库位出入库记录 | REQ-PC-025 | ['依赖模块'] |
| 库位出入库记录 | REQ-PC-034 | ['依赖模块'] |
| 页面内导航 | live prototype | ['上孵计划列表', '仓库全景图（待定）', '仓库管理', '出入库记录', '出雏器全景图（待定）', '出雏器管理', '受健率标准管理', '品种管理', '存发苗间管理', '孵化周期管理', '孵化器全景图（待定）', '孵化器管理', '库存查询', '生产报表', '盘点记录', '种蛋上孵任务', '种蛋出雏任务', '种蛋照蛋任务', '蛋重类型管理'] |

## 5. business_rules

- **BR-001**：出雏器的出入库均为自动出入库，入库：种蛋照蛋；出库：种蛋出雏。（live prototype annotation / related requirement page）
- **BR-002**：库位号：出入库记录如果是因为同一个库位号同时混装了多种蛋，产生了虚拟库位的记录，则此处记录的库位号为当时的虚拟库位号，并且标记“混”。（live prototype annotation / related requirement page）
- **BR-003**：关于操作类型、方式、原因的说明： 1、操作类型：入库、出库； 2、方式：自动；出雏器只有自动出入库，没有手动出入库，自动盘点及任务执行过程中系统自动进行的出入库操作数据； 3、原因：出入库的原因，不同操作类型、方式对应的原因不同： ①入库——自动：种蛋照蛋； ②出库——自动：种蛋出雏。（live prototype annotation / related requirement page）
- **BR-004**：上孵计划号：所有出入库记录均来自上孵计划的任务，所有总有上孵计划号。（live prototype annotation / related requirement page）
- **BR-005**：出入库记录，按照出入库类型、时间、种蛋、库位号独立生成操作记录。（live prototype annotation / related requirement page）
- **BR-006**：该页面为某一库位出入库记录页。（live prototype annotation / related requirement page）

## 6. open_questions

- **OQ-001**：真实接口、权限、异常提示和字段校验规则是什么？；影响：影响正式契约与下游测试点；阻塞：True

## 7. Handoff Report

- **Agent**: analyze-agent
- **Project**: 种禽孵化管理系统
- **Req ID**: REQ-PC-026
- **Outputs**: `02_analysis/pc/REQ-PC-026.yaml`; `02_analysis/pc/REQ-PC-026_库位出入库记录.md`
- **Gate**: passed
- **Next Agent**: testpoint-agent
- **Blockers**: none

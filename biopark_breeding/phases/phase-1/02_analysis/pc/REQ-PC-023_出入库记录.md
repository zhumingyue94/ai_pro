# REQ-PC-023 孵化器管理 / 出入库记录 需求分析

> Analyze 阶段产物；不包含测试点、测试用例、CSV 或 UI 脚本。

## 1. 追溯与范围

- REQ-ID：`REQ-PC-023`
- 原型：`http://127.0.0.1:5500/`；页面树：57 页。
- 范围基线：`REQ-PC-023`；一致但禅道模块覆盖两个原型页面，原型第 52 页“出入库记录”。
- 页面捕获状态：`observed`；实际捕获 1 页。

## 2. 页面契约

| 页面 | frame URL | 板块数 | 控件数 | 弹窗数 | 注释数 |
|---|---|---:|---:|---:|---:|
| 出入库记录 | `http://127.0.0.1:5500/%E5%87%BA%E5%85%A5%E5%BA%93%E8%AE%B0%E5%BD%95_4.html` | 0 | 30 | 0 | 7 |

### 出入库记录

- 标题：出入库记录
- 正文行数：607
- 页面板块：
- 观察到的控件：
  - `u20980_input` INPUT/checkbox：checkbox
  - `u20981_input` INPUT/checkbox：checkbox
  - `u20982_input` INPUT/checkbox：checkbox
  - `u20983_input` INPUT/checkbox：checkbox
  - `u20984_input` INPUT/checkbox：checkbox
  - `u20985_input` INPUT/checkbox：checkbox
  - `u20986_input` INPUT/checkbox：checkbox
  - `u20987_input` INPUT/checkbox：checkbox
  - `u20988_input` INPUT/checkbox：checkbox
  - `u20989_input` INPUT/checkbox：checkbox
  - `u20990_input` INPUT/checkbox：checkbox
  - `u20994_input` INPUT/text：请输入平均蛋重
  - `u20996_input` SELECT/select-one：全部孵化器 北一号孵化箱 北二号孵化箱 南一号孵化箱
  - `u20999_input` SELECT/select-one：全部养殖场 养殖场一 养殖场二 养殖场三
  - `u21001_input` SELECT/select-one：全部品种 AA 利丰
  - `u21003_input` SELECT/select-one：全部种蛋类型 合格蛋 二级蛋
  - `u21005_input` INPUT/text：请输入周龄
  - `u21007_input` SELECT/select-one：全部蛋重类型 大 中 小
  - `u21009_input` INPUT/date：
  - `u21010_input` INPUT/date：
  - `u21013_input` INPUT/text：请输入上孵计划号
  - `u21016_input` INPUT/text：请输入操作人
  - `u21018_input` SELECT/select-one：全部孵化场 孵化一场 孵化二场
  - `u21020_input` INPUT/text：请输入养殖批次
  - `u21021_input` INPUT/date：
  - `u21022_input` INPUT/date：
  - `u21025_input` SELECT/select-one：全部类型 入库 出库
  - `u21026_input` INPUT/text：请输入库位号
  - `u21028_input` SELECT/select-one：全部方式 自动
  - `u21030_input` SELECT/select-one：全部原因 种蛋上孵 种蛋照蛋
- 弹窗/状态面板：未捕获当前页面真实弹窗
- 页面注释：
  - 方式：只有一种自动。
  - 该页面为登录账号权限范围下所有孵化器，出入库记录页。
  - 孵化器的出入库均为自动出入库，入库：上孵任务；出库：种蛋照蛋。
  - 库位号：出入库记录如果是因为同一个库位号同时混装了多种蛋，产生了虚拟库位的记录，则此处记录的库位号为当时的虚拟库位号，并且标记“混”。
  - 关于操作类型、方式、原因的说明： 1、操作类型：入库、出库； 2、方式：自动；孵化器只有自动出入库，没有手动出入库，自动盘点及任务执行过程中系统自动进行的出入库操作数据； 3、原因：出入库的原因，不同操作类型、方式对应的原因不同： ①入库——自动：种蛋上孵； ②出库——自动：种蛋照蛋。
  - 上孵计划号：所有出入库记录均来自上孵计划的任务，所有总有上孵计划号。
  - 出入库记录，按照出入库类型、时间、种蛋、库位号独立生成操作记录。

## 3. interfaces

| 名称 | 类型 | 来源/目标 | 说明 |
|---|---|---|---|
| 依赖模块 | module_dependency | REQ-PC-021 | 依赖字段、状态和权限由依赖模块确认 |
| 依赖模块 | module_dependency | REQ-PC-033 | 依赖字段、状态和权限由依赖模块确认 |
| 页面内导航 | prototype_navigation | live prototype | ['上孵计划列表', '仓库全景图（待定）', '仓库管理', '出入库记录', '出雏器全景图（待定）', '出雏器管理', '受健率标准管理', '品种管理', '存发苗间管理', '孵化周期管理', '孵化器全景图（待定）', '孵化器管理', '库存查询', '生产报表', '盘点记录', '种蛋上孵任务', '种蛋出雏任务', '种蛋照蛋任务', '蛋重类型管理'] |

## 4. cross_module_refs

| 字段 | 来源模块 | 外部数据 |
|---|---|---|
| 出入库记录 | REQ-PC-021 | ['依赖模块'] |
| 出入库记录 | REQ-PC-033 | ['依赖模块'] |
| 页面内导航 | live prototype | ['上孵计划列表', '仓库全景图（待定）', '仓库管理', '出入库记录', '出雏器全景图（待定）', '出雏器管理', '受健率标准管理', '品种管理', '存发苗间管理', '孵化周期管理', '孵化器全景图（待定）', '孵化器管理', '库存查询', '生产报表', '盘点记录', '种蛋上孵任务', '种蛋出雏任务', '种蛋照蛋任务', '蛋重类型管理'] |

## 5. business_rules

- **BR-001**：方式：只有一种自动。（live prototype annotation / related requirement page）
- **BR-002**：该页面为登录账号权限范围下所有孵化器，出入库记录页。（live prototype annotation / related requirement page）
- **BR-003**：孵化器的出入库均为自动出入库，入库：上孵任务；出库：种蛋照蛋。（live prototype annotation / related requirement page）
- **BR-004**：库位号：出入库记录如果是因为同一个库位号同时混装了多种蛋，产生了虚拟库位的记录，则此处记录的库位号为当时的虚拟库位号，并且标记“混”。（live prototype annotation / related requirement page）
- **BR-005**：关于操作类型、方式、原因的说明： 1、操作类型：入库、出库； 2、方式：自动；孵化器只有自动出入库，没有手动出入库，自动盘点及任务执行过程中系统自动进行的出入库操作数据； 3、原因：出入库的原因，不同操作类型、方式对应的原因不同： ①入库——自动：种蛋上孵； ②出库——自动：种蛋照蛋。（live prototype annotation / related requirement page）
- **BR-006**：上孵计划号：所有出入库记录均来自上孵计划的任务，所有总有上孵计划号。（live prototype annotation / related requirement page）
- **BR-007**：出入库记录，按照出入库类型、时间、种蛋、库位号独立生成操作记录。（live prototype annotation / related requirement page）

## 6. open_questions

- **OQ-001**：真实接口、权限、异常提示和字段校验规则是什么？；影响：影响正式契约与下游测试点；阻塞：True

## 7. Handoff Report

- **Agent**: analyze-agent
- **Project**: 种禽孵化管理系统
- **Req ID**: REQ-PC-023
- **Outputs**: `02_analysis/pc/REQ-PC-023.yaml`; `02_analysis/pc/REQ-PC-023_出入库记录.md`
- **Gate**: passed
- **Next Agent**: testpoint-agent
- **Blockers**: none

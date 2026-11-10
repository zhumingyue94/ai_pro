# REQ-PC-027 出雏器管理 / 出入库记录 需求分析

> Analyze 阶段产物；不包含测试点、测试用例、CSV 或 UI 脚本。

## 1. 追溯与范围

- REQ-ID：`REQ-PC-027`
- 原型：`http://127.0.0.1:5500/`；页面树：57 页。
- 范围基线：`REQ-PC-027`；一致但禅道模块覆盖两个原型页面，原型第 56 页“出入库记录”。
- 页面捕获状态：`observed`；实际捕获 1 页。

## 2. 页面契约

| 页面 | frame URL | 板块数 | 控件数 | 弹窗数 | 注释数 |
|---|---|---:|---:|---:|---:|
| 出入库记录 | `http://127.0.0.1:5500/%E5%87%BA%E5%85%A5%E5%BA%93%E8%AE%B0%E5%BD%95_5.html` | 0 | 30 | 0 | 7 |

### 出入库记录

- 标题：出入库记录
- 正文行数：607
- 页面板块：
- 观察到的控件：
  - `u23142_input` INPUT/checkbox：checkbox
  - `u23143_input` INPUT/checkbox：checkbox
  - `u23144_input` INPUT/checkbox：checkbox
  - `u23145_input` INPUT/checkbox：checkbox
  - `u23146_input` INPUT/checkbox：checkbox
  - `u23147_input` INPUT/checkbox：checkbox
  - `u23148_input` INPUT/checkbox：checkbox
  - `u23149_input` INPUT/checkbox：checkbox
  - `u23150_input` INPUT/checkbox：checkbox
  - `u23151_input` INPUT/checkbox：checkbox
  - `u23152_input` INPUT/checkbox：checkbox
  - `u23162_input` INPUT/text：请输入平均蛋重
  - `u23164_input` SELECT/select-one：全部出雏器 北一号出雏器 北二号出雏器 南一号出雏器
  - `u23167_input` SELECT/select-one：全部养殖场 养殖场一 养殖场二 养殖场三
  - `u23169_input` SELECT/select-one：全部品种 AA 利丰
  - `u23171_input` SELECT/select-one：全部种蛋类型 合格蛋 二级蛋
  - `u23173_input` INPUT/text：请输入周龄
  - `u23175_input` SELECT/select-one：全部蛋重类型 大 中 小
  - `u23177_input` INPUT/date：
  - `u23178_input` INPUT/date：
  - `u23181_input` INPUT/text：请输入上孵计划号
  - `u23184_input` INPUT/text：请输入操作人
  - `u23186_input` SELECT/select-one：全部孵化场 孵化一场 孵化二场
  - `u23188_input` INPUT/text：请输入养殖批次
  - `u23189_input` INPUT/date：
  - `u23190_input` INPUT/date：
  - `u23193_input` SELECT/select-one：全部类型 入库 出库
  - `u23194_input` INPUT/text：请输入库位号
  - `u23196_input` SELECT/select-one：全部方式 自动
  - `u23198_input` SELECT/select-one：全部原因 种蛋照蛋 种蛋出雏
- 弹窗/状态面板：未捕获当前页面真实弹窗
- 页面注释：
  - 该页面为登录账号权限范围下所有出雏器，出入库记录页。
  - 出雏器的出入库均为自动出入库，入库：种蛋照蛋；出库：种蛋出雏。
  - 库位号：出入库记录如果是因为同一个库位号同时混装了多种蛋，产生了虚拟库位的记录，则此处记录的库位号为当时的虚拟库位号，并且标记“混”。
  - 关于操作类型、方式、原因的说明： 1、操作类型：入库、出库； 2、方式：自动；出雏器只有自动出入库，没有手动出入库，自动盘点及任务执行过程中系统自动进行的出入库操作数据； 3、原因：出入库的原因，不同操作类型、方式对应的原因不同： ①入库——自动：种蛋照蛋； ②出库——自动：种蛋出雏。
  - 上孵计划号：所有出入库记录均来自上孵计划的任务，所有总有上孵计划号。
  - 出入库记录，按照出入库类型、时间、种蛋、库位号独立生成操作记录。 搜索 重置 平均蛋重： 出雏器： 全部出雏器 北一号出雏器 北二号出雏器 南一号出雏器 库位号： 养殖场： 全部养殖场 养殖场一 养殖场二 养殖场三 品种： 全部品种 AA 利丰 种蛋类型： 全部种蛋类型 合格蛋 二级蛋 周龄： 蛋重类型： 全部蛋重类型 大 中 小 产蛋日期： ~ 计划号： 出入库日期： 操作人： 孵化场： 全部孵化场 孵化一场 孵化二场 养殖批次： ~ 出/入库： 全部类型 入库 出库 方式： 全部方式 自动 原因： 全部原因 种蛋照蛋 种蛋出雏
  - 方式：只有一种自动。

## 3. interfaces

| 名称 | 类型 | 来源/目标 | 说明 |
|---|---|---|---|
| 依赖模块 | module_dependency | REQ-PC-025 | 依赖字段、状态和权限由依赖模块确认 |
| 依赖模块 | module_dependency | REQ-PC-034 | 依赖字段、状态和权限由依赖模块确认 |
| 页面内导航 | prototype_navigation | live prototype | ['上孵计划列表', '仓库全景图（待定）', '仓库管理', '出入库记录', '出雏器全景图（待定）', '出雏器管理', '受健率标准管理', '品种管理', '存发苗间管理', '孵化周期管理', '孵化器全景图（待定）', '孵化器管理', '库存查询', '生产报表', '盘点记录', '种蛋上孵任务', '种蛋出雏任务', '种蛋照蛋任务', '蛋重类型管理'] |

## 4. cross_module_refs

| 字段 | 来源模块 | 外部数据 |
|---|---|---|
| 出入库记录 | REQ-PC-025 | ['依赖模块'] |
| 出入库记录 | REQ-PC-034 | ['依赖模块'] |
| 页面内导航 | live prototype | ['上孵计划列表', '仓库全景图（待定）', '仓库管理', '出入库记录', '出雏器全景图（待定）', '出雏器管理', '受健率标准管理', '品种管理', '存发苗间管理', '孵化周期管理', '孵化器全景图（待定）', '孵化器管理', '库存查询', '生产报表', '盘点记录', '种蛋上孵任务', '种蛋出雏任务', '种蛋照蛋任务', '蛋重类型管理'] |

## 5. business_rules

- **BR-001**：该页面为登录账号权限范围下所有出雏器，出入库记录页。（live prototype annotation / related requirement page）
- **BR-002**：出雏器的出入库均为自动出入库，入库：种蛋照蛋；出库：种蛋出雏。（live prototype annotation / related requirement page）
- **BR-003**：库位号：出入库记录如果是因为同一个库位号同时混装了多种蛋，产生了虚拟库位的记录，则此处记录的库位号为当时的虚拟库位号，并且标记“混”。（live prototype annotation / related requirement page）
- **BR-004**：关于操作类型、方式、原因的说明： 1、操作类型：入库、出库； 2、方式：自动；出雏器只有自动出入库，没有手动出入库，自动盘点及任务执行过程中系统自动进行的出入库操作数据； 3、原因：出入库的原因，不同操作类型、方式对应的原因不同： ①入库——自动：种蛋照蛋； ②出库——自动：种蛋出雏。（live prototype annotation / related requirement page）
- **BR-005**：上孵计划号：所有出入库记录均来自上孵计划的任务，所有总有上孵计划号。（live prototype annotation / related requirement page）
- **BR-006**：出入库记录，按照出入库类型、时间、种蛋、库位号独立生成操作记录。 搜索 重置 平均蛋重： 出雏器： 全部出雏器 北一号出雏器 北二号出雏器 南一号出雏器 库位号： 养殖场： 全部养殖场 养殖场一 养殖场二 养殖场三 品种： 全部品种 AA 利丰 种蛋类型： 全部种蛋类型 合格蛋 二级蛋 周龄： 蛋重类型： 全部蛋重类型 大 中 小 产蛋日期： ~ 计划号： 出入库日期： 操作人： 孵化场： 全部孵化场 孵化一场 孵化二场 养殖批次： ~ 出/入库： 全部类型 入库 出库 方式： 全部方式 自动 原因： 全部原因 种蛋照蛋 种蛋出雏（live prototype annotation / related requirement page）
- **BR-007**：方式：只有一种自动。（live prototype annotation / related requirement page）

## 6. open_questions

- **OQ-001**：真实接口、权限、异常提示和字段校验规则是什么？；影响：影响正式契约与下游测试点；阻塞：True

## 7. Handoff Report

- **Agent**: analyze-agent
- **Project**: 种禽孵化管理系统
- **Req ID**: REQ-PC-027
- **Outputs**: `02_analysis/pc/REQ-PC-027.yaml`; `02_analysis/pc/REQ-PC-027_出入库记录.md`
- **Gate**: passed
- **Next Agent**: testpoint-agent
- **Blockers**: none

# REQ-PC-018 库存管理 / 次品库 / 单类型出入库记录 需求分析

> Analyze 阶段产物；不包含测试点、测试用例、CSV 或 UI 脚本。

## 1. 追溯与范围

- REQ-ID：`REQ-PC-018`
- 原型：`http://127.0.0.1:5500/`；页面树：57 页。
- 范围基线：`REQ-PC-018`；差异：原型页面名为“单类型出入库记录”，禅道节点名为“出入库记录”；建议保留为该节点下的独立需求。
- 页面捕获状态：`observed`；实际捕获 1 页。

## 2. 页面契约

| 页面 | frame URL | 板块数 | 控件数 | 弹窗数 | 注释数 |
|---|---|---:|---:|---:|---:|
| 单类型出入库记录 | `http://127.0.0.1:5500/%E5%8D%95%E7%B1%BB%E5%9E%8B%E5%87%BA%E5%85%A5%E5%BA%93%E8%AE%B0%E5%BD%95.html` | 0 | 18 | 0 | 4 |

### 单类型出入库记录

- 标题：单类型出入库记录
- 正文行数：493
- 页面板块：
- 观察到的控件：
  - `u17625_input` INPUT/checkbox：checkbox
  - `u17626_input` INPUT/checkbox：checkbox
  - `u17627_input` INPUT/checkbox：checkbox
  - `u17628_input` INPUT/checkbox：checkbox
  - `u17629_input` INPUT/checkbox：checkbox
  - `u17630_input` INPUT/checkbox：checkbox
  - `u17631_input` INPUT/checkbox：checkbox
  - `u17632_input` INPUT/checkbox：checkbox
  - `u17633_input` INPUT/checkbox：checkbox
  - `u17634_input` INPUT/checkbox：checkbox
  - `u17635_input` INPUT/checkbox：checkbox
  - `u17642_input` SELECT/select-one：全部类型 入库 出库
  - `u17644_input` SELECT/select-one：全部方式 自动 手动
  - `u17646_input` INPUT/date：
  - `u17647_input` INPUT/date：
  - `u17653_input` SELECT/select-one：全部原因 种蛋挑选 其他
  - `u17655_input` INPUT/text：请输入操作人
  - `u17657_input` INPUT/text：请输入上孵计划号
- 弹窗/状态面板：未捕获当前页面真实弹窗
- 页面注释：
  - 原因，根据方式对应变动选项。 原因： 全部原因 种蛋挑选 其他 操作人： 计划号：
  - 关于操作类型、方式、原因的说明： 1、操作类型：入库、出库； 2、方式：手动、自动；①手动：在仓库中点击出入库进行的入库操作数据；②自动：盘点及任务执行过程中系统自动进行的出入库操作数据； 3、原因：出入库的原因，不同操作类型、方式对应的原因不同： ①入库——手动：种蛋挑选、种蛋照蛋、种蛋出雏、其他； ②入库——自动：种蛋照蛋、种蛋出雏、盘点； ③出库——手动：销售、销毁、更换仓库、其他； ④出库——自动：盘点。
  - 上孵计划号：如果是来自计划任务的地总出入库，有上孵计划号，否则没有上孵计划号。
  - 该页面为某一类型出入库记录页。

## 3. interfaces

| 名称 | 类型 | 来源/目标 | 说明 |
|---|---|---|---|
| 依赖模块 | module_dependency | REQ-PC-017 | 依赖字段、状态和权限由依赖模块确认 |
| 依赖模块 | module_dependency | REQ-PC-005 | 依赖字段、状态和权限由依赖模块确认 |
| 页面内导航 | prototype_navigation | live prototype | ['上孵计划列表', '仓库全景图（待定）', '仓库管理', '出入库记录', '出雏器全景图（待定）', '出雏器管理', '受健率标准管理', '品种管理', '存发苗间管理', '孵化周期管理', '孵化器全景图（待定）', '孵化器管理', '库存查询', '生产报表', '盘点记录', '种蛋上孵任务', '种蛋出雏任务', '种蛋照蛋任务', '蛋重类型管理'] |

## 4. cross_module_refs

| 字段 | 来源模块 | 外部数据 |
|---|---|---|
| 单类型出入库记录 | REQ-PC-017 | ['依赖模块'] |
| 单类型出入库记录 | REQ-PC-005 | ['依赖模块'] |
| 页面内导航 | live prototype | ['上孵计划列表', '仓库全景图（待定）', '仓库管理', '出入库记录', '出雏器全景图（待定）', '出雏器管理', '受健率标准管理', '品种管理', '存发苗间管理', '孵化周期管理', '孵化器全景图（待定）', '孵化器管理', '库存查询', '生产报表', '盘点记录', '种蛋上孵任务', '种蛋出雏任务', '种蛋照蛋任务', '蛋重类型管理'] |

## 5. business_rules

- **BR-001**：原因，根据方式对应变动选项。 原因： 全部原因 种蛋挑选 其他 操作人： 计划号：（live prototype annotation / related requirement page）
- **BR-002**：关于操作类型、方式、原因的说明： 1、操作类型：入库、出库； 2、方式：手动、自动；①手动：在仓库中点击出入库进行的入库操作数据；②自动：盘点及任务执行过程中系统自动进行的出入库操作数据； 3、原因：出入库的原因，不同操作类型、方式对应的原因不同： ①入库——手动：种蛋挑选、种蛋照蛋、种蛋出雏、其他； ②入库——自动：种蛋照蛋、种蛋出雏、盘点； ③出库——手动：销售、销毁、更换仓库、其他； ④出库——自动：盘点。（live prototype annotation / related requirement page）
- **BR-003**：上孵计划号：如果是来自计划任务的地总出入库，有上孵计划号，否则没有上孵计划号。（live prototype annotation / related requirement page）
- **BR-004**：该页面为某一类型出入库记录页。（live prototype annotation / related requirement page）

## 6. open_questions

- **OQ-001**：真实接口、权限、异常提示和字段校验规则是什么？；影响：影响正式契约与下游测试点；阻塞：True

## 7. Handoff Report

- **Agent**: analyze-agent
- **Project**: 种禽孵化管理系统
- **Req ID**: REQ-PC-018
- **Outputs**: `02_analysis/pc/REQ-PC-018.yaml`; `02_analysis/pc/REQ-PC-018_单类型出入库记录.md`
- **Gate**: passed
- **Next Agent**: testpoint-agent
- **Blockers**: none

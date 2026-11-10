# REQ-PC-035 基础数据 / 受健率标准管理 需求分析

> Analyze 阶段产物；不包含测试点、测试用例、CSV 或 UI 脚本。

## 1. 追溯与范围

- REQ-ID：`REQ-PC-035`
- 原型：`http://127.0.0.1:5500/`；页面树：57 页。
- 范围基线：`REQ-PC-035`；一致；原型和需求均存在“受健率标准管理”。
- 页面捕获状态：`observed`；实际捕获 1 页。

## 2. 页面契约

| 页面 | frame URL | 板块数 | 控件数 | 弹窗数 | 注释数 |
|---|---|---:|---:|---:|---:|
| 受健率标准管理 | `http://127.0.0.1:5500/%E5%8F%97%E5%81%A5%E7%8E%87%E6%A0%87%E5%87%86%E7%AE%A1%E7%90%86.html` | 0 | 8 | 3 | 2 |

### 受健率标准管理

- 标题：受健率标准管理
- 正文行数：189
- 页面板块：
- 观察到的控件：
  - `u3884_input` INPUT/checkbox：checkbox
  - `u3885_input` INPUT/checkbox：checkbox
  - `u3886_input` INPUT/checkbox：checkbox
  - `u3970_input` INPUT/text：请输入周龄
  - `u3979_input` SELECT/select-one：2026年 2025年 2024年 2023年 2022年
  - `u3982_input` INPUT/checkbox：checkbox
  - `u3983_input` INPUT/checkbox：checkbox
  - `u3985_input` SELECT/select-one：孵化一场 孵化二场 孵化三场
- 弹窗/状态面板：品种新建/编辑/删除弹框、修改品种、删除品种
- 页面注释：
  - 关键字查询 年份： 2026年 2025年 2024年 2023年 2022年 修改 修改 孵化场： 孵化一场 孵化二场 孵化三场
  - 表格固定，周龄范围就是固定25-64

## 3. interfaces

| 名称 | 类型 | 来源/目标 | 说明 |
|---|---|---|---|
| 依赖模块 | module_dependency | REQ-PC-029 | 依赖字段、状态和权限由依赖模块确认 |
| 依赖模块 | module_dependency | REQ-PC-030 | 依赖字段、状态和权限由依赖模块确认 |
| 页面内导航 | prototype_navigation | live prototype | ['上孵计划列表', '仓库全景图（待定）', '仓库管理', '出入库记录', '出雏器全景图（待定）', '出雏器管理', '受健率标准管理', '品种管理', '存发苗间管理', '孵化周期管理', '孵化器全景图（待定）', '孵化器管理', '库存查询', '生产报表', '盘点记录', '种蛋上孵任务', '种蛋出雏任务', '种蛋照蛋任务', '蛋重类型管理'] |

## 4. cross_module_refs

| 字段 | 来源模块 | 外部数据 |
|---|---|---|
| 受健率标准管理 | REQ-PC-029 | ['依赖模块'] |
| 受健率标准管理 | REQ-PC-030 | ['依赖模块'] |
| 页面内导航 | live prototype | ['上孵计划列表', '仓库全景图（待定）', '仓库管理', '出入库记录', '出雏器全景图（待定）', '出雏器管理', '受健率标准管理', '品种管理', '存发苗间管理', '孵化周期管理', '孵化器全景图（待定）', '孵化器管理', '库存查询', '生产报表', '盘点记录', '种蛋上孵任务', '种蛋出雏任务', '种蛋照蛋任务', '蛋重类型管理'] |

## 5. business_rules

- **BR-001**：关键字查询 年份： 2026年 2025年 2024年 2023年 2022年 修改 修改 孵化场： 孵化一场 孵化二场 孵化三场（live prototype annotation / related requirement page）
- **BR-002**：表格固定，周龄范围就是固定25-64（live prototype annotation / related requirement page）

## 6. open_questions

- **OQ-001**：真实接口、权限、异常提示和字段校验规则是什么？；影响：影响正式契约与下游测试点；阻塞：True

## 7. Handoff Report

- **Agent**: analyze-agent
- **Project**: 种禽孵化管理系统
- **Req ID**: REQ-PC-035
- **Outputs**: `02_analysis/pc/REQ-PC-035.yaml`; `02_analysis/pc/REQ-PC-035_受健率标准管理.md`
- **Gate**: passed
- **Next Agent**: testpoint-agent
- **Blockers**: none

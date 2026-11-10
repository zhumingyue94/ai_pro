# REQ-PC-002 计划管理 / 生产报表 需求分析

> Analyze 阶段产物；不包含测试点、测试用例、CSV 或 UI 脚本。

## 1. 追溯与范围

- REQ-ID：`REQ-PC-002`
- 原型：`http://127.0.0.1:5500/`；页面树：57 页。
- 范围基线：`REQ-PC-002`；一致；对应原型“生产报表”，需求 P003。
- 页面捕获状态：`observed`；实际捕获 1 页。

## 2. 页面契约

| 页面 | frame URL | 板块数 | 控件数 | 弹窗数 | 注释数 |
|---|---|---:|---:|---:|---:|
| 生产报表 | `http://127.0.0.1:5500/%E7%94%9F%E4%BA%A7%E6%8A%A5%E8%A1%A8.html` | 0 | 21 | 0 | 2 |

### 生产报表

- 标题：生产报表
- 正文行数：429
- 页面板块：
- 观察到的控件：
  - `u1809_input` INPUT/checkbox：checkbox
  - `u1810_input` INPUT/checkbox：checkbox
  - `u1811_input` INPUT/checkbox：checkbox
  - `u1940_input` INPUT/date：
  - `u1944_input` SELECT/select-one：请选择种蛋类型 合格蛋 二级蛋
  - `u1947_input` INPUT/date：
  - `u1948_input` INPUT/date：
  - `u1951_input` INPUT/text：请输入养殖批次
  - `u1953_input` SELECT/select-one：全部孵化场 孵化一场 孵化二场
  - `u1955_input` SELECT/select-one：全部养殖场 益兴一场 益兴二场
  - `u1957_input` SELECT/select-one：全部品种 AA 利丰
  - `u1959_input` INPUT/text：请输入创建人
  - `u1961_input` INPUT/date：
  - `u1962_input` INPUT/date：
  - `u1965_input` INPUT/date：
  - `u1966_input` INPUT/date：
  - `u1969_input` INPUT/date：
  - `u1970_input` INPUT/date：
  - `u1973_input` SELECT/select-one：请选择蛋重类型 大 中 小 特小
  - `u1975_input` INPUT/text：请输入平均蛋重
  - `u1977_input` INPUT/text：请输入周龄
- 弹窗/状态面板：未捕获当前页面真实弹窗
- 页面注释：
  - 生产报表，回填计划完成的数据，并且支持批量导出。 产蛋日期： ~ 养殖批次： 孵化场： 全部孵化场 孵化一场 孵化二场 养殖场： 全部养殖场 益兴一场 益兴二场 品种： 全部品种 AA 利丰 创建人： 上孵日期： ~ 照蛋日期： ~ 出雏日期： ~ 蛋重类型： 请选择蛋重类型 大 中 小 特小 平均蛋重： 周龄：
  - 导出，点击弹框选择，①导出明细表②导出统计报表；统计报表导出需要选择到年份、月份、孵化场

## 3. interfaces

| 名称 | 类型 | 来源/目标 | 说明 |
|---|---|---|---|
| 依赖模块 | module_dependency | REQ-PC-001 | 依赖字段、状态和权限由依赖模块确认 |
| 页面内导航 | prototype_navigation | live prototype | ['上孵计划列表', '仓库全景图（待定）', '仓库管理', '出入库记录', '出雏器全景图（待定）', '出雏器管理', '受健率标准管理', '品种管理', '存发苗间管理', '孵化周期管理', '孵化器全景图（待定）', '孵化器管理', '库存查询', '生产报表', '盘点记录', '种蛋上孵任务', '种蛋出雏任务', '种蛋照蛋任务', '蛋重类型管理'] |

## 4. cross_module_refs

| 字段 | 来源模块 | 外部数据 |
|---|---|---|
| 生产报表 | REQ-PC-001 | ['依赖模块'] |
| 页面内导航 | live prototype | ['上孵计划列表', '仓库全景图（待定）', '仓库管理', '出入库记录', '出雏器全景图（待定）', '出雏器管理', '受健率标准管理', '品种管理', '存发苗间管理', '孵化周期管理', '孵化器全景图（待定）', '孵化器管理', '库存查询', '生产报表', '盘点记录', '种蛋上孵任务', '种蛋出雏任务', '种蛋照蛋任务', '蛋重类型管理'] |

## 5. business_rules

- **BR-001**：生产报表，回填计划完成的数据，并且支持批量导出。 产蛋日期： ~ 养殖批次： 孵化场： 全部孵化场 孵化一场 孵化二场 养殖场： 全部养殖场 益兴一场 益兴二场 品种： 全部品种 AA 利丰 创建人： 上孵日期： ~ 照蛋日期： ~ 出雏日期： ~ 蛋重类型： 请选择蛋重类型 大 中 小 特小 平均蛋重： 周龄：（live prototype annotation / related requirement page）
- **BR-002**：导出，点击弹框选择，①导出明细表②导出统计报表；统计报表导出需要选择到年份、月份、孵化场（live prototype annotation / related requirement page）

## 6. open_questions

- **OQ-001**：真实接口、权限、异常提示和字段校验规则是什么？；影响：影响正式契约与下游测试点；阻塞：True

## 7. Handoff Report

- **Agent**: analyze-agent
- **Project**: 种禽孵化管理系统
- **Req ID**: REQ-PC-002
- **Outputs**: `02_analysis/pc/REQ-PC-002.yaml`; `02_analysis/pc/REQ-PC-002_生产报表.md`
- **Gate**: passed
- **Next Agent**: testpoint-agent
- **Blockers**: none

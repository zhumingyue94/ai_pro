# 测试用例 — APP上孵计划发货记录 (REQ-APP-024)

- 用例数：**41**
- 需求编号：REQ-APP-024
- 测试计划：TEST_PLAN-REQ-APP-024
- 版本：3
- 追溯状态：redesigned_after_rev_case
- 来源评审：REV_CASE_REQ-APP-024

## 覆盖与审核信息

- 项目：种禽孵化管理系统
- 模块：APP上孵计划发货记录
- 需求：REQ-APP-024
- 测试计划：TEST_PLAN-REQ-APP-024
- 页面/入口：未登记
- 覆盖范围：COV-APP024-ACTUAL-AVAILABLE, COV-APP024-BACK-PAGE, COV-APP024-BACK-PLAN-CONTEXT, COV-APP024-BACK-SHIPMENT-CONTEXT, COV-APP024-CHICK-INFO, COV-APP024-CUMULATIVE-SHIPPED, COV-APP024-MULTI-POSITION, COV-APP024-MULTI-POSITION-QTY, COV-APP024-OPERATOR, COV-APP024-PENDING-ASSIGN, COV-APP024-PENDING-FIELDS, COV-APP024-PLAN-NO, COV-APP024-POSITION-DETAIL, COV-APP024-POSITION-REMARK, COV-APP024-PROGRESS, COV-APP024-RECORD-COUNT, COV-APP024-RECORD-FIELDS, COV-APP024-RECORD-SORT, COV-APP024-RECORD-STATUS, COV-APP024-RECORD-TIME, COV-APP024-RECORDS-EMPTY, COV-APP024-RECORDS-PERFORMANCE, COV-APP024-REMAINING-SHIPMENT, COV-APP024-SHIPMENT-NO, COV-APP024-SHIPMENT-POSITION-COUNT, COV-APP024-SHIPPING-RECORDS, COV-APP024-SIGN-UNCONFIRMED, COV-APP024-STATUS-PENDING, COV-APP024-STATUS-SHIPPED, COV-APP024-STATUS-SHIPPING, COV-APP024-STATUS-SIGNED
- 审核结论：待评审；生成器仅完成结构化派生

## 用例总览

- 总用例数：**41**
- 自动化用例数：**41**
- 功能/手工用例数：**41**
- P1：**11**
- P2：**24**
- P3：**6**
- P4：**0**

## TC-APP-024-003 / 未登记 [P2] auto=auto

**标题**: 待发货计划展示计划号和待发货状态

**原子测试目的**: AP-APP024-PENDING-IDENTITY

**状态/条件分支**: 常规业务场景

**auto**: auto

**type**: feature

**功能**: 上孵计划详情

**追溯**: 需求=REQ-APP-024；测试计划=未登记；项目=种禽孵化管理系统；版本=2；状态=designed_with_evidence_boundary

**前置条件**:

- 授权查询角色可用
- 已准备待发货计划
- 已准备可切换的目标孵化场

**公共前置引用**: `app_shipment_plan_records_access`

**步骤**:

1. 查看待发货计划的发货记录页面并查看计划详情区域
   - 预期：计划详情区域展示当前上孵计划号，计划状态显示为待发货

## TC-APP-024-004 / 未登记 [P2] auto=auto

**标题**: 待发货计划展示实际可发、累计、待分配和进度

**原子测试目的**: AP-APP024-PENDING-METRICS

**状态/条件分支**: 常规业务场景

**auto**: auto

**type**: feature

**功能**: 数量指标

**追溯**: 需求=REQ-APP-024；测试计划=未登记；项目=种禽孵化管理系统；版本=2；状态=designed_with_evidence_boundary

**前置条件**:

- 授权查询角色可用
- 已准备实际可发数可核对的待发货计划
- 已准备可切换的目标孵化场
- 已准备累计发货数可核对的计划
- 已准备待分配数可核对的计划
- 已准备进度值可核对的计划

**公共前置引用**: `app_shipment_plan_records_access`

**步骤**:

1. 在计划详情区域查看实际可发、累计发货、待分配和发货进度
   - 预期：实际可发数、累计发货数、待分配数和发货进度均与准备的可核对数据一致

## TC-APP-024-005 / 未登记 [P2] auto=auto

**标题**: 无历史记录时展示空状态

**原子测试目的**: AP-APP024-RECORDS-EMPTY

**状态/条件分支**: 常规业务场景

**auto**: auto

**type**: feature

**功能**: 历史发货记录

**追溯**: 需求=REQ-APP-024；测试计划=未登记；项目=种禽孵化管理系统；版本=2；状态=designed_with_evidence_boundary

**前置条件**:

- 授权查询角色可用
- 已准备无历史发货记录的有效计划
- 已准备可切换的目标孵化场

**公共前置引用**: `app_shipment_plan_records_access`

**步骤**:

1. 在计划发货记录页面查看历史记录区域
   - 预期：历史记录区域显示暂无发货记录

## TC-APP-024-006 / 未登记 [P2] auto=auto

**标题**: 发货中计划展示发货中状态和历史记录

**原子测试目的**: AP-APP024-SHIPPING-STATUS-RECORDS

**状态/条件分支**: 常规业务场景

**auto**: auto

**type**: feature

**功能**: 计划状态

**追溯**: 需求=REQ-APP-024；测试计划=未登记；项目=种禽孵化管理系统；版本=2；状态=designed_with_evidence_boundary

**前置条件**:

- 授权查询角色可用
- 已准备发货中的计划
- 已准备可切换的目标孵化场
- 已准备发货中计划和历史发货记录

**公共前置引用**: `app_shipment_plan_records_access`

**步骤**:

1. 查看发货中计划的状态和历史记录区域
   - 预期：计划状态显示为发货中，历史记录区域展示该计划的发货记录列表

## TC-APP-024-007 / 未登记 [P2] auto=auto

**标题**: 已发货计划展示已发货状态

**原子测试目的**: AP-APP024-STATUS-SHIPPED

**状态/条件分支**: 常规业务场景

**auto**: auto

**type**: feature

**功能**: 计划状态

**追溯**: 需求=REQ-APP-024；测试计划=未登记；项目=种禽孵化管理系统；版本=2；状态=blocked_contract

**前置条件**:

- 授权查询角色可用
- 已准备已发货的计划
- 已准备可切换的目标孵化场

**公共前置引用**: `app_shipment_plan_records_access`

**步骤**:

1. 查看已发货计划的发货记录页面并查看计划状态
   - 预期：计划状态显示为已发货

## TC-APP-024-008 / 未登记 [P2] auto=auto

**标题**: 已签收计划仅在外部明确确认后显示已签收

**原子测试目的**: AP-APP024-STATUS-SIGNED

**状态/条件分支**: 常规业务场景

**auto**: auto

**type**: feature

**功能**: 签收状态

**追溯**: 需求=REQ-APP-024；测试计划=未登记；项目=种禽孵化管理系统；版本=2；状态=blocked_contract

**前置条件**:

- 授权查询角色可用
- 已准备外部系统明确确认签收的计划
- 已准备可切换的目标孵化场

**公共前置引用**: `app_shipment_plan_records_access`

**步骤**:

1. 查看外部系统已明确确认签收的计划发货记录页面并查看计划状态
   - 预期：计划状态显示为已签收

## TC-APP-024-009 / 未登记 [P2] auto=auto

**标题**: 外部未确认签收时不显示已签收

**原子测试目的**: AP-APP024-SIGN-UNCONFIRMED

**状态/条件分支**: 常规业务场景

**auto**: auto

**type**: feature

**功能**: 签收状态

**追溯**: 需求=REQ-APP-024；测试计划=未登记；项目=种禽孵化管理系统；版本=2；状态=blocked_contract

**前置条件**:

- 授权查询角色可用
- 已准备外部系统未明确确认签收的计划
- 已准备可切换的目标孵化场

**公共前置引用**: `app_shipment_plan_records_access`

**步骤**:

1. 查看外部系统未明确确认签收的计划发货记录页面并查看计划状态
   - 预期：计划状态不显示为已签收

## TC-APP-024-010 / 未登记 [P3] auto=auto

**标题**: 单条记录展示提交时间倒序中的首条记录

**原子测试目的**: AP-APP024-RECORD-SORT

**状态/条件分支**: 常规业务场景

**auto**: auto

**type**: feature

**功能**: 历史发货记录

**追溯**: 需求=REQ-APP-024；测试计划=未登记；项目=种禽孵化管理系统；版本=2；状态=designed_with_evidence_boundary

**前置条件**:

- 授权查询角色可用
- 已准备至少两条提交时间不同的历史发货记录
- 已准备可切换的目标孵化场

**公共前置引用**: `app_shipment_plan_records_access`

**步骤**:

1. 在历史发货记录区域查看记录列表的首条记录
   - 预期：首条记录的提交时间晚于其后记录的提交时间

## TC-APP-024-011 / 未登记 [P3] auto=auto

**标题**: 记录展示列层位置明细（含多位置）

**原子测试目的**: AP-APP024-POSITION-DETAIL

**状态/条件分支**: 常规业务场景

**auto**: auto

**type**: feature

**功能**: 位置明细

**追溯**: 需求=REQ-APP-024；测试计划=未登记；项目=种禽孵化管理系统；版本=2；状态=designed_with_evidence_boundary

**前置条件**:

- 授权查询角色可用
- 已准备包含列层位置的历史发货记录
- 已准备可切换的目标孵化场
- 已准备包含多个列层位置的单条发货记录

**公共前置引用**: `app_shipment_plan_records_access`

**步骤**:

1. 在历史发货记录中查看目标记录的列层位置明细
   - 预期：目标记录展示对应的列层位置，多位置记录展示每个列层位置及其对应数量

## TC-APP-024-012 / 未登记 [P3] auto=auto

**标题**: 多位置记录数量合计与记录数量一致

**原子测试目的**: AP-APP024-MULTI-POSITION-QTY

**状态/条件分支**: 常规业务场景

**auto**: auto

**type**: feature

**功能**: 位置明细

**追溯**: 需求=REQ-APP-024；测试计划=未登记；项目=种禽孵化管理系统；版本=2；状态=designed_with_evidence_boundary

**前置条件**:

- 授权查询角色可用
- 已准备位置数量可计算的发货记录
- 已准备可切换的目标孵化场

**公共前置引用**: `app_shipment_plan_records_access`

**步骤**:

1. 对照目标记录的各列层数量与记录数量
   - 预期：各列层数量合计等于该条发货记录数量

## TC-APP-024-016 / 未登记 [P3] auto=auto

**标题**: 大数据量历史记录在两秒内完成加载

**原子测试目的**: AP-APP024-RECORDS-PERFORMANCE

**状态/条件分支**: 常规业务场景

**auto**: auto

**type**: feature

**功能**: 历史发货记录

**追溯**: 需求=REQ-APP-024；测试计划=未登记；项目=种禽孵化管理系统；版本=2；状态=open_evidence

**前置条件**:

- 授权查询角色可用
- 已准备大数据量历史发货记录和约定的计时环境
- 已准备可切换的目标孵化场

**公共前置引用**: `app_shipment_plan_records_access`

**步骤**:

1. 打开包含大数据量历史记录的计划发货记录页面并观察记录区域加载
   - 预期：历史记录区域在两秒内完成加载并可查看记录

## TC-APP-024-019 / 未登记 [P2] auto=auto

**标题**: 返回按钮回到发货执行页

**原子测试目的**: AP-APP024-BACK-PAGE

**状态/条件分支**: 常规业务场景

**auto**: auto

**type**: feature

**功能**: 返回执行页

**追溯**: 需求=REQ-APP-024；测试计划=未登记；项目=种禽孵化管理系统；版本=2；状态=designed_with_evidence_boundary

**前置条件**:

- 授权查询角色可用
- 已准备有效发货单和有效上孵计划
- 已准备可切换的目标孵化场

**公共前置引用**: `app_shipment_plan_records_access`

**步骤**:

1. 点击页面上的"返回"
   - 预期：返回发货执行页

## TC-APP-024-020 / 未登记 [P3] auto=auto

**标题**: 返回后保留发货单上下文

**原子测试目的**: AP-APP024-BACK-SHIPMENT-CONTEXT

**状态/条件分支**: 常规业务场景

**auto**: auto

**type**: feature

**功能**: 返回执行页

**追溯**: 需求=REQ-APP-024；测试计划=未登记；项目=种禽孵化管理系统；版本=2；状态=open_evidence

**前置条件**:

- 授权查询角色可用
- 已准备有效发货单和有效上孵计划
- 已准备可切换的目标孵化场

**公共前置引用**: `app_shipment_plan_records_access`

**步骤**:

1. 点击页面上的"返回"
   - 预期：返回页面显示原发货单信息

## TC-APP-024-021 / 未登记 [P3] auto=auto

**标题**: 返回后保留上孵计划上下文

**原子测试目的**: AP-APP024-BACK-PLAN-CONTEXT

**状态/条件分支**: 常规业务场景

**auto**: auto

**type**: feature

**功能**: 返回执行页

**追溯**: 需求=REQ-APP-024；测试计划=未登记；项目=种禽孵化管理系统；版本=3；状态=open_evidence

**前置条件**:

- 授权查询角色可用
- 已准备有效发货单和有效上孵计划
- 已准备可切换的目标孵化场

**公共前置引用**: `app_shipment_plan_records_access`

**步骤**:

1. 点击页面上的"返回"
   - 预期：返回后仍显示原上孵计划

## TC-APP-024-025 / 未登记 [P1] auto=auto

**标题**: 发货单号与进入路径一致

**原子测试目的**: AP-APP024-SHIPMENT-NO

**状态/条件分支**: 常规业务场景

**auto**: auto

**type**: feature

**功能**: 发货单号

**追溯**: 需求=REQ-APP-024；测试计划=未登记；项目=种禽孵化管理系统；版本=3；状态=designed_with_evidence_boundary

**前置条件**:

- 已准备可核对发货单号的有效发货单

**公共前置引用**: `app_shipment_plan_records_access`

**步骤**:

1. 记录发货执行页目标发货单号并点击目标上孵计划的记录入口
   - 预期：进入对应上孵计划发货记录页面
2. 查看页面顶部发货单号
   - 预期：页面发货单号与进入路径记录的发货单号完全一致

## TC-APP-024-027 / 未登记 [P2] auto=auto

**标题**: 平均苗重取出雏任务

**原子测试目的**: AP-APP024-AVERAGE-CHICK-WEIGHT

**状态/条件分支**: 常规业务场景

**auto**: auto

**type**: feature

**功能**: 雏苗信息

**追溯**: 需求=REQ-APP-024；测试计划=未登记；项目=种禽孵化管理系统；版本=3；状态=designed_with_evidence_boundary

**前置条件**:

- 已准备出雏任务平均苗重基准

**公共前置引用**: `app_shipment_plan_records_access`

**步骤**:

1. 查看目标上孵计划发货记录页面并查看平均苗重
   - 预期：平均苗重等于对应上孵计划出雏任务的平均苗重

## TC-APP-024-028 / 未登记 [P2] auto=auto

**标题**: 养殖场取计划管理数据

**原子测试目的**: AP-APP024-FARM

**状态/条件分支**: 常规业务场景

**auto**: auto

**type**: feature

**功能**: 雏苗信息

**追溯**: 需求=REQ-APP-024；测试计划=未登记；项目=种禽孵化管理系统；版本=3；状态=designed_with_evidence_boundary

**前置条件**:

- 已准备 PC 端计划管理上孵计划养殖场基准

**公共前置引用**: `app_shipment_plan_records_access`

**步骤**:

1. 查看页面养殖场字段
   - 预期：养殖场等于 PC 端计划管理对应上孵计划的养殖场

## TC-APP-024-029 / 未登记 [P2] auto=auto

**标题**: 养殖批次取计划管理数据

**原子测试目的**: AP-APP024-BATCH

**状态/条件分支**: 常规业务场景

**auto**: auto

**type**: feature

**功能**: 雏苗信息

**追溯**: 需求=REQ-APP-024；测试计划=未登记；项目=种禽孵化管理系统；版本=3；状态=designed_with_evidence_boundary

**前置条件**:

- 已准备 PC 端计划管理上孵计划养殖批次基准

**公共前置引用**: `app_shipment_plan_records_access`

**步骤**:

1. 查看页面养殖批次字段
   - 预期：养殖批次等于 PC 端计划管理对应上孵计划的养殖批次

## TC-APP-024-030 / 未登记 [P2] auto=auto

**标题**: 周龄取计划管理数据

**原子测试目的**: AP-APP024-AGE

**状态/条件分支**: 常规业务场景

**auto**: auto

**type**: feature

**功能**: 雏苗信息

**追溯**: 需求=REQ-APP-024；测试计划=未登记；项目=种禽孵化管理系统；版本=3；状态=designed_with_evidence_boundary

**前置条件**:

- 已准备 PC 端计划管理上孵计划周龄基准

**公共前置引用**: `app_shipment_plan_records_access`

**步骤**:

1. 查看页面周龄字段
   - 预期：周龄等于 PC 端计划管理对应上孵计划的周龄

## TC-APP-024-031 / 未登记 [P2] auto=auto

**标题**: 平均蛋重取计划管理数据

**原子测试目的**: AP-APP024-AVERAGE-EGG-WEIGHT

**状态/条件分支**: 常规业务场景

**auto**: auto

**type**: feature

**功能**: 雏苗信息

**追溯**: 需求=REQ-APP-024；测试计划=未登记；项目=种禽孵化管理系统；版本=3；状态=designed_with_evidence_boundary

**前置条件**:

- 已准备 PC 端计划管理上孵计划平均蛋重基准

**公共前置引用**: `app_shipment_plan_records_access`

**步骤**:

1. 查看页面平均蛋重字段
   - 预期：平均蛋重等于 PC 端计划管理对应上孵计划的平均蛋重

## TC-APP-024-032 / 未登记 [P2] auto=auto

**标题**: 蛋重类型取计划管理数据

**原子测试目的**: AP-APP024-EGG-WEIGHT-TYPE

**状态/条件分支**: 常规业务场景

**auto**: auto

**type**: feature

**功能**: 雏苗信息

**追溯**: 需求=REQ-APP-024；测试计划=未登记；项目=种禽孵化管理系统；版本=3；状态=designed_with_evidence_boundary

**前置条件**:

- 已准备 PC 端计划管理上孵计划蛋重类型基准

**公共前置引用**: `app_shipment_plan_records_access`

**步骤**:

1. 查看页面蛋重类型字段
   - 预期：蛋重类型等于 PC 端计划管理对应上孵计划的蛋重类型

## TC-APP-024-033 / 未登记 [P2] auto=auto

**标题**: 产蛋日期取计划管理数据

**原子测试目的**: AP-APP024-EGG-DATE

**状态/条件分支**: 常规业务场景

**auto**: auto

**type**: feature

**功能**: 雏苗信息

**追溯**: 需求=REQ-APP-024；测试计划=未登记；项目=种禽孵化管理系统；版本=3；状态=designed_with_evidence_boundary

**前置条件**:

- 已准备 PC 端计划管理上孵计划产蛋日期基准

**公共前置引用**: `app_shipment_plan_records_access`

**步骤**:

1. 查看页面产蛋日期字段
   - 预期：产蛋日期等于 PC 端计划管理对应上孵计划的产蛋日期

## TC-APP-024-034 / 未登记 [P2] auto=auto

**标题**: 出雏日期取计划管理数据

**原子测试目的**: AP-APP024-HATCH-DATE

**状态/条件分支**: 常规业务场景

**auto**: auto

**type**: feature

**功能**: 雏苗信息

**追溯**: 需求=REQ-APP-024；测试计划=未登记；项目=种禽孵化管理系统；版本=3；状态=designed_with_evidence_boundary

**前置条件**:

- 已准备 PC 端计划管理上孵计划出雏日期基准

**公共前置引用**: `app_shipment_plan_records_access`

**步骤**:

1. 查看页面出雏日期字段
   - 预期：出雏日期等于 PC 端计划管理对应上孵计划的出雏日期

## TC-APP-024-035 / 未登记 [P2] auto=auto

**标题**: 计划备注取计划管理数据

**原子测试目的**: AP-APP024-PLAN-REMARK

**状态/条件分支**: 常规业务场景

**auto**: auto

**type**: feature

**功能**: 雏苗信息

**追溯**: 需求=REQ-APP-024；测试计划=未登记；项目=种禽孵化管理系统；版本=3；状态=designed_with_evidence_boundary

**前置条件**:

- 已准备 PC 端计划管理上孵计划备注基准

**公共前置引用**: `app_shipment_plan_records_access`

**步骤**:

1. 查看页面计划备注字段
   - 预期：备注等于 PC 端计划管理对应上孵计划的备注

## TC-APP-024-036 / 未登记 [P1] auto=auto

**标题**: 记录显示本次发货数量

**原子测试目的**: AP-APP024-THIS-SHIPMENT

**状态/条件分支**: 常规业务场景

**auto**: auto

**type**: feature

**功能**: 发货记录字段

**追溯**: 需求=REQ-APP-024；测试计划=未登记；项目=种禽孵化管理系统；版本=3；状态=designed_with_evidence_boundary

**前置条件**:

- 已准备可核对本次发货数量的历史记录

**公共前置引用**: `app_shipment_plan_records_access`

**步骤**:

1. 查看目标发货记录的本次发货字段
   - 预期：本次发货字段显示该记录提交的本次发货数量

## TC-APP-024-037 / 未登记 [P1] auto=auto

**标题**: 记录剩余发货按提交时待发货计算

**原子测试目的**: AP-APP024-REMAINING-SHIPMENT

**状态/条件分支**: 常规业务场景

**auto**: auto

**type**: feature

**功能**: 发货记录字段

**追溯**: 需求=REQ-APP-024；测试计划=未登记；项目=种禽孵化管理系统；版本=3；状态=designed_with_evidence_boundary

**前置条件**:

- 已准备提交时待发货数和本次发货数量均可核对的历史记录

**公共前置引用**: `app_shipment_plan_records_access`

**步骤**:

1. 查看目标记录的剩余发货字段并按提交时待发货数减本次发货数复核
   - 预期：剩余发货等于提交当时待发货数减去本次发货数量

## TC-APP-024-038 / 未登记 [P2] auto=auto

**标题**: 发货位置显示位置数量

**原子测试目的**: AP-APP024-POSITION-COUNT

**状态/条件分支**: 常规业务场景

**auto**: auto

**type**: feature

**功能**: 发货记录字段

**追溯**: 需求=REQ-APP-024；测试计划=未登记；项目=种禽孵化管理系统；版本=3；状态=designed_with_evidence_boundary

**前置条件**:

- 已准备本次发货涉及位置数量可核对的记录

**公共前置引用**: `app_shipment_plan_records_access`

**步骤**:

1. 查看目标记录的发货位置字段
   - 预期：发货位置显示为“n处”，n等于本次发货数量大于零的位置数

## TC-APP-024-039 / 未登记 [P2] auto=auto

**标题**: 操作人显示发货提交用户

**原子测试目的**: AP-APP024-OPERATOR

**状态/条件分支**: 常规业务场景

**auto**: auto

**type**: feature

**功能**: 发货记录字段

**追溯**: 需求=REQ-APP-024；测试计划=未登记；项目=种禽孵化管理系统；版本=3；状态=designed_with_evidence_boundary

**前置条件**:

- 已准备可核对完成本次发货用户的记录

**公共前置引用**: `app_shipment_plan_records_access`

**步骤**:

1. 查看目标发货记录的操作人字段
   - 预期：操作人等于完成该次发货提交的用户

## TC-APP-024-040 / 未登记 [P2] auto=auto

**标题**: 有备注位置显示备注行

**原子测试目的**: AP-APP024-POSITION-REMARK-YES

**状态/条件分支**: 常规业务场景

**auto**: auto

**type**: feature

**功能**: 位置备注

**追溯**: 需求=REQ-APP-024；测试计划=未登记；项目=种禽孵化管理系统；版本=3；状态=designed_with_evidence_boundary

**前置条件**:

- 已准备带备注的位置发货记录

**公共前置引用**: `app_shipment_plan_records_access`

**步骤**:

1. 查看带备注位置的明细
   - 预期：对应位置行下方插入备注行，备注内容与该位置提交备注一致

## TC-APP-024-041 / 未登记 [P2] auto=auto

**标题**: 无备注位置隐藏备注行

**原子测试目的**: AP-APP024-POSITION-REMARK-NO

**状态/条件分支**: 常规业务场景

**auto**: auto

**type**: feature

**功能**: 位置备注

**追溯**: 需求=REQ-APP-024；测试计划=未登记；项目=种禽孵化管理系统；版本=3；状态=designed_with_evidence_boundary

**前置条件**:

- 已准备无备注的位置发货记录

**公共前置引用**: `app_shipment_plan_records_access`

**步骤**:

1. 查看无备注位置的明细区域
   - 预期：不显示备注行和空备注占位内容

## TC-APP-024-042 / 未登记 [P2] auto=auto

**标题**: 历史记录保留提交时剩余发货快照

**原子测试目的**: AP-APP024-REMAINING-SNAPSHOT

**状态/条件分支**: 常规业务场景

**auto**: auto

**type**: feature

**功能**: 发货记录字段

**追溯**: 需求=REQ-APP-024；测试计划=未登记；项目=种禽孵化管理系统；版本=3；状态=designed_with_evidence_boundary

**前置条件**:

- 已准备同一计划先后提交的两条发货记录

**公共前置引用**: `app_shipment_plan_records_access`

**步骤**:

1. 对照第一次记录提交时的剩余发货基准查看第一次记录
   - 预期：第一次记录的剩余发货保持其提交时计算结果，不被后续记录改写

## TC-APP-024-043 / 未登记 [P1] auto=auto

**标题**: 上孵计划号与入口计划一致

**原子测试目的**: AP-APP024-PLAN-NO

**状态/条件分支**: 常规业务场景

**auto**: auto

**type**: feature

**功能**: 上孵计划号

**追溯**: 需求=REQ-APP-024；测试计划=未登记；项目=种禽孵化管理系统；版本=3；状态=designed_with_evidence_boundary

**前置条件**:

- 已准备可核对上孵计划号的有效计划

**公共前置引用**: `app_shipment_plan_records_access`

**步骤**:

1. 查看目标计划发货记录页面顶部计划号
   - 预期：目标计划号与入口点击的目标计划号一致
2. 查看页面顶部上孵计划号
   - 预期：页面计划号与入口点击的目标计划号一致

## TC-APP-024-044 / 未登记 [P1] auto=auto

**标题**: 未发完计划状态显示发货中

**原子测试目的**: AP-APP024-STATUS-UNFINISHED-MAPPING

**状态/条件分支**: 常规业务场景

**auto**: auto

**type**: feature

**功能**: 计划状态

**追溯**: 需求=REQ-APP-024；测试计划=未登记；项目=种禽孵化管理系统；版本=3；状态=designed_with_evidence_boundary

**前置条件**:

- 已准备发货执行页状态为未发完的计划

**公共前置引用**: `app_shipment_plan_records_access`

**步骤**:

1. 查看计划状态
   - 预期：记录页严格显示发货中，不显示已发完

## TC-APP-024-045 / 未登记 [P1] auto=auto

**标题**: 实际可发等于健雏数

**原子测试目的**: AP-APP024-ACTUAL-AVAILABLE-SOURCE

**状态/条件分支**: 常规业务场景

**auto**: auto

**type**: feature

**功能**: 数量指标

**追溯**: 需求=REQ-APP-024；测试计划=未登记；项目=种禽孵化管理系统；版本=3；状态=designed_with_evidence_boundary

**前置条件**:

- 已准备出雏任务健雏数基准

**公共前置引用**: `app_shipment_plan_records_access`

**步骤**:

1. 查看计划详情实际可发
   - 预期：实际可发等于对应出雏任务的健雏数

## TC-APP-024-046 / 未登记 [P1] auto=auto

**标题**: 已发货等于本次发货合计

**原子测试目的**: AP-APP024-SHIPPED-SUM

**状态/条件分支**: 常规业务场景

**auto**: auto

**type**: feature

**功能**: 数量指标

**追溯**: 需求=REQ-APP-024；测试计划=未登记；项目=种禽孵化管理系统；版本=3；状态=designed_with_evidence_boundary

**前置条件**:

- 已准备至少两条本次发货数量可核对的历史记录

**公共前置引用**: `app_shipment_plan_records_access`

**步骤**:

1. 逐条读取历史记录本次发货并求和后查看已发货
   - 预期：已发货等于全部历史记录本次发货数量之和

## TC-APP-024-047 / 未登记 [P1] auto=auto

**标题**: 待发货数按实际可发数减已发货数计算

**原子测试目的**: AP-APP024-PENDING-DIFF

**状态/条件分支**: 常规业务场景

**auto**: auto

**type**: feature

**功能**: 数量指标

**追溯**: 需求=REQ-APP-024；测试计划=未登记；项目=种禽孵化管理系统；版本=3；状态=designed_with_evidence_boundary

**前置条件**:

- 已准备实际可发和已发货基准

**公共前置引用**: `app_shipment_plan_records_access`

**步骤**:

1. 用实际可发减已发货后核对待发货
   - 预期：待发货等于实际可发减已发货

## TC-APP-024-048 / 未登记 [P1] auto=auto

**标题**: 发货进度按已发货数除以实际可发数计算

**原子测试目的**: AP-APP024-PROGRESS-RATIO

**状态/条件分支**: 常规业务场景

**auto**: auto

**type**: feature

**功能**: 数量指标

**追溯**: 需求=REQ-APP-024；测试计划=未登记；项目=种禽孵化管理系统；版本=3；状态=designed_with_evidence_boundary

**前置条件**:

- 已准备实际可发大于0且已发货小于等于实际可发的基准数据

**公共前置引用**: `app_shipment_plan_records_access`

**步骤**:

1. 回读页面显示的已发货和实际可发，按已发货除以实际可发乘以100%核对进度
   - 预期：进度等于已发货/实际可发×100%，按整数四舍五入并显示百分号

## TC-APP-024-049 / 未登记 [P2] auto=auto

**标题**: 记录标题数量与列表一致

**原子测试目的**: AP-APP024-RECORD-COUNT

**状态/条件分支**: 常规业务场景

**auto**: auto

**type**: feature

**功能**: 记录列表标题

**追溯**: 需求=REQ-APP-024；测试计划=未登记；项目=种禽孵化管理系统；版本=3；状态=designed_with_evidence_boundary

**前置条件**:

- 已准备记录数量可核对的有效计划

**公共前置引用**: `app_shipment_plan_records_access`

**步骤**:

1. 查看历史记录区域标题并统计完整记录列表数量
   - 预期：标题右侧显示“共 n 条”，n等于完整历史记录数量

## TC-APP-024-050 / 未登记 [P2] auto=auto

**标题**: 发货时间取提交时间并按年月日时分秒格式显示

**原子测试目的**: AP-APP024-TIME-FORMAT

**状态/条件分支**: 常规业务场景

**auto**: auto

**type**: feature

**功能**: 发货记录字段

**追溯**: 需求=REQ-APP-024；测试计划=未登记；项目=种禽孵化管理系统；版本=3；状态=designed_with_evidence_boundary

**前置条件**:

- 已准备可核对提交时间的历史记录

**公共前置引用**: `app_shipment_plan_records_access`

**步骤**:

1. 查看每条历史记录的发货时间并对照提交时间
   - 预期：发货时间等于提交时间，且格式严格为YYYY-MM-DD HH:SS

## TC-APP-024-051 / 未登记 [P1] auto=auto

**标题**: 记录状态按剩余发货判断

**原子测试目的**: AP-APP024-RECORD-STATUS-RULE

**状态/条件分支**: 常规业务场景

**auto**: auto

**type**: feature

**功能**: 发货记录状态

**追溯**: 需求=REQ-APP-024；测试计划=未登记；项目=种禽孵化管理系统；版本=3；状态=designed_with_evidence_boundary

**前置条件**:

- 已准备剩余发货大于零和等于零的记录

**公共前置引用**: `app_shipment_plan_records_access`

**步骤**:

1. 查看一条剩余发货大于零的记录和一条剩余发货等于零的记录
   - 预期：剩余发货大于零显示未发完，等于零显示已发完

## TC-APP-024-052 / 未登记 [P1] auto=auto

**标题**: 位置明细展示字段并按位置数量公式计算

**原子测试目的**: AP-APP024-POSITION-FIELDS

**状态/条件分支**: 常规业务场景

**auto**: auto

**type**: feature

**功能**: 位置明细

**追溯**: 需求=REQ-APP-024；测试计划=未登记；项目=种禽孵化管理系统；版本=3；状态=designed_with_evidence_boundary

**前置条件**:

- 已准备含历史累计和本次新增的多位置记录

**公共前置引用**: `app_shipment_plan_records_access`

**步骤**:

1. 查看每个位置的层列、位置累计和新增
   - 预期：层列严格为m列n层；位置累计等于历史累计加本次发货；新增等于当前位置本次发货数量

## 结论

- 用例交付状态：已生成待评审
- 未覆盖项/待确认项：无
- 备注：来源 YAML：REQ-APP-024；Markdown 由公共渲染器生成。

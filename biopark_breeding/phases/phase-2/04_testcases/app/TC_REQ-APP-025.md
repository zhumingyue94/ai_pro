# 测试用例 — APP存发苗间出入库记录 (REQ-APP-025)

- 用例数：**10**
- 需求编号：REQ-APP-025
- 测试计划：TEST_PLAN-REQ-APP-025
- 版本：4
- 追溯状态：redesigned_after_rev_case
- 来源评审：REV_CASE_REQ-APP-025

## 覆盖与审核信息

- 项目：种禽孵化管理系统
- 模块：APP存发苗间出入库记录
- 需求：REQ-APP-025
- 测试计划：TEST_PLAN-REQ-APP-025
- 页面/入口：未登记
- 覆盖范围：COV-APP025-AUTO-ATTRIBUTES, COV-APP025-AUTO-CREATE, COV-APP025-QUANTITY, COV-APP025-QUERY, COV-APP025-RECORD-FIELDS, COV-APP025-RECORD-IDEMPOTENCY
- 审核结论：待评审；生成器仅完成结构化派生

## 用例总览

- 总用例数：**10**
- 自动化用例数：**10**
- 功能/手工用例数：**1**
- P1：**2**
- P2：**4**
- P3：**4**
- P4：**0**

## TC-APP-025-001 / TEST_PLAN-REQ-APP-025 [P3] auto=auto

**标题**: 自动出库记录类型为出库、方式为自动、单位为只

**原子测试目的**: AP-APP025-TYPE-METHOD-UNIT

**状态/条件分支**: 常规业务场景

**auto**: auto

**type**: interface

**功能**: 自动出库记录

**追溯**: 需求=REQ-APP-025；测试计划=TEST_PLAN-REQ-APP-025；项目=种禽孵化管理系统；版本=4；状态=blocked_contract

**前置条件**:

- 已批准发货确认变更窗口
- 已准备可回读的发货记录和自动出库记录
- 已准备可回读的自动出库记录

**公共前置引用**: `app_inventory_records_access`

**步骤**:

1. 完成一次有效发货确认并回读对应自动出库记录的类型和方式
   - 预期：自动出库记录的类型显示为“出库”，方式显示为“自动”。

## TC-APP-025-002 / TEST_PLAN-REQ-APP-025 [P3] auto=auto

**标题**: 自动出库记录批次取上孵计划批次

**原子测试目的**: AP-APP025-BATCH

**状态/条件分支**: 常规业务场景

**auto**: auto

**type**: interface

**功能**: 自动出库记录

**追溯**: 需求=REQ-APP-025；测试计划=TEST_PLAN-REQ-APP-025；项目=种禽孵化管理系统；版本=4；状态=blocked_contract

**前置条件**:

- 已批准发货确认变更窗口
- 已准备带明确上孵计划批次的发货记录和自动出库记录

**公共前置引用**: `app_inventory_records_access`

**步骤**:

1. 完成有效发货确认并对照上孵计划批次与自动出库记录批次
   - 预期：自动出库记录批次与本次发货关联的上孵计划批次一致

## TC-APP-025-003 / TEST_PLAN-REQ-APP-025 [P1] auto=auto

**标题**: 自动出库数量等于本次发货数量

**原子测试目的**: AP-APP025-QUANTITY

**状态/条件分支**: 常规业务场景

**auto**: auto

**type**: interface

**功能**: 自动出库记录

**追溯**: 需求=REQ-APP-025；测试计划=TEST_PLAN-REQ-APP-025；项目=种禽孵化管理系统；版本=4；状态=blocked_contract

**前置条件**:

- 已批准发货确认变更窗口
- 已准备可回读且数量明确的发货记录和自动出库记录

**公共前置引用**: `app_inventory_records_access`

**步骤**:

1. 完成一次有效的发货确认，发货数=上孵计划剩余可发
   - 预期：发货确认成功，且本次发货数量等于上孵计划剩余可发数量。
2. 对照本次发货数量与自动出库数量
   - 预期：自动出库数量与本次发货数量相等。

## TC-APP-025-007 / TEST_PLAN-REQ-APP-025 [P2] auto=auto

**标题**: 发货确认后生成一笔对应自动出库记录

**原子测试目的**: AP-APP025-RECORD-CREATED

**状态/条件分支**: 常规业务场景

**auto**: auto

**type**: interface

**功能**: 自动出库记录

**追溯**: 需求=REQ-APP-025；测试计划=TEST_PLAN-REQ-APP-025；项目=种禽孵化管理系统；版本=4；状态=blocked_contract

**前置条件**:

- 已批准发货确认变更窗口
- 已准备可回读的发货记录
- 发货确认前不存在与本次发货对应的自动出库记录

**公共前置引用**: `app_inventory_records_access`

**步骤**:

1. 完成一次有效发货确认并回读对应自动出库记录
   - 预期：新增一笔与本次发货确认对应的自动出库记录

## TC-APP-025-008 / TEST_PLAN-REQ-APP-025 [P3] auto=auto

**标题**: 自动出库操作人、操作时间取发货记录，养殖客户取当前园区

**原子测试目的**: AP-APP025-OPERATOR-TIME-CUSTOMER

**状态/条件分支**: 常规业务场景

**auto**: auto

**type**: interface

**功能**: 自动出库记录

**追溯**: 需求=REQ-APP-025；测试计划=TEST_PLAN-REQ-APP-025；项目=种禽孵化管理系统；版本=4；状态=blocked_contract

**前置条件**:

- 已批准发货确认变更窗口
- 已准备操作人明确的发货记录和可回读的自动出库记录
- 已准备操作时间明确的发货记录和可回读的自动出库记录
- 已准备当前园区和养殖客户明确的发货记录
- 已准备可回读的自动出库记录

**公共前置引用**: `app_inventory_records_access`

**步骤**:

1. 完成一次有效发货确认并对照发货记录操作人和操作时间
   - 预期：自动出库记录的操作人与本次雏苗发货记录的操作人一致，操作时间与本次雏苗发货记录的操作时间一致。
2. 对照当前园区与自动出库记录的养殖客户
   - 预期：自动出库记录的养殖客户为当前园区对应的养殖客户。

## TC-APP-025-009 / TEST_PLAN-REQ-APP-025 [P2] auto=auto

**标题**: 库存充足时出库存发苗间取上孵计划关联

**原子测试目的**: AP-APP025-ROOM-SOURCE

**状态/条件分支**: 常规业务场景

**auto**: auto

**type**: interface

**功能**: 自动出库记录

**追溯**: 需求=REQ-APP-025；测试计划=TEST_PLAN-REQ-APP-025；项目=种禽孵化管理系统；版本=4；状态=blocked_contract

**前置条件**:

- 已批准发货确认变更窗口
- 已准备仅关联一个存发苗间且库存充足的上孵计划
- 已准备可回读的自动出库记录

**公共前置引用**: `app_inventory_records_access`

**步骤**:

1. 在单库存发苗间且库存充足条件下完成发货确认并回读自动出库记录的存发苗间
   - 预期：自动出库记录的存发苗间与上孵计划关联的存发苗间一致

## TC-APP-025-011 / TEST_PLAN-REQ-APP-025 [P3] auto=auto

**标题**: 出入库记录列表可见本次自动出库

**原子测试目的**: AP-APP025-QUERY-RECORD

**状态/条件分支**: 常规业务场景

**auto**: auto

**type**: feature

**功能**: 出入库记录查询

**追溯**: 需求=REQ-APP-025；测试计划=TEST_PLAN-REQ-APP-025；项目=种禽孵化管理系统；版本=4；状态=blocked_contract

**前置条件**:

- 授权存发苗间管理角色可用
- 已批准发货确认变更窗口
- 已准备一次有效发货确认后可对照的自动出库记录
- 已准备可切换的目标孵化场

**公共前置引用**: `app_inventory_records_access`

**步骤**:

1. 在出入库记录列表中查找本次发货确认对应的自动出库记录
   - 预期：列表中存在与本次发货确认对应的自动出库记录

## TC-APP-025-017 / TEST_PLAN-REQ-APP-025 [P2] auto=auto

**标题**: 发货数量为零时不生成自动出库记录

**原子测试目的**: AP-APP025-QUANTITY-ZERO

**状态/条件分支**: 常规业务场景

**auto**: auto

**type**: interface

**功能**: 自动出库数量边界

**追溯**: 需求=REQ-APP-025；测试计划=TEST_PLAN-REQ-APP-025；项目=种禽孵化管理系统；版本=4；状态=blocked_contract

**前置条件**:

- 已批准发货确认变更窗口
- 已准备发货数量为零且可回读结果的样本

**公共前置引用**: `app_inventory_records_access`

**步骤**:

1. 在发货数量为零的条件下完成发货确认并查询对应自动出库结果
   - 预期：发货确认结果符合待确认的零数量处理契约，且不生成数量大于零的自动出库记录

## TC-APP-025-019 / TEST_PLAN-REQ-APP-025 [P1] auto=auto

**标题**: 发货完成后出入库记录数量字段展示正确

**原子测试目的**: AP-APP025-RECORD-QUANTITY

**状态/条件分支**: 常规业务场景

**auto**: auto

**type**: interface

**功能**: 出入库记录字段展示

**追溯**: 需求=REQ-APP-025；测试计划=TEST_PLAN-REQ-APP-025；项目=种禽孵化管理系统；版本=6；状态=blocked_contract

**前置条件**:

- 已准备发货完成后的出入库记录和字段回读证据

**公共前置引用**: `app_inventory_records_access`

**步骤**:

1. 在发货执行已完成联动的条件下查询出入库记录
   - 预期：出入库记录的数量字段展示正确；本用例不验证生成时机、库存扣减时机或库存变动数量

## TC-APP-025-022 / TEST_PLAN-REQ-APP-025 [P2] auto=auto

**标题**: 两个客户端查询同一出入库记录不重复展示

**原子测试目的**: AP-APP025-RECORD-QUERY-IDEMPOTENCY

**状态/条件分支**: 常规业务场景

**auto**: auto

**type**: interface

**功能**: 出入库记录查询幂等

**追溯**: 需求=REQ-APP-025；测试计划=TEST_PLAN-REQ-APP-025；项目=种禽孵化管理系统；版本=6；状态=blocked_contract

**前置条件**:

- 已准备同一出入库记录和并发查询样本
- 查询幂等规则已标记待确认

**公共前置引用**: `app_inventory_records_access`

**步骤**:

1. 使用两个客户端查询同一出入库记录并回读列表
   - 预期：记录仅展示一次，查询结果符合待确认的幂等展示契约；本用例不验证发货确认、出库生成或库存扣减

## 结论

- 用例交付状态：已生成待评审
- 未覆盖项/待确认项：无
- 备注：来源 YAML：REQ-APP-025；Markdown 由公共渲染器生成。

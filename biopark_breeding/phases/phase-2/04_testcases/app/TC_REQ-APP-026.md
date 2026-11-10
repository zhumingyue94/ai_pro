# 测试用例 — APP存发苗间库存查询 (REQ-APP-026)

- 用例数：**3**
- 需求编号：REQ-APP-026
- 测试计划：TEST_PLAN-REQ-APP-026
- 版本：4
- 追溯状态：redesigned_after_rev_case
- 来源评审：REV_CASE_REQ-APP-026

## 覆盖与审核信息

- 项目：种禽孵化管理系统
- 模块：APP存发苗间库存查询
- 需求：REQ-APP-026
- 测试计划：TEST_PLAN-REQ-APP-026
- 页面/入口：未登记
- 覆盖范围：COV-APP026-DECREMENT, COV-APP026-QUERY, COV-APP026-ZERO
- 审核结论：待评审；生成器仅完成结构化派生

## 用例总览

- 总用例数：**3**
- 自动化用例数：**3**
- 功能/手工用例数：**2**
- P1：**1**
- P2：**0**
- P3：**2**
- P4：**0**

## TC-APP-026-001 / TEST_PLAN-REQ-APP-026 [P1] auto=auto

**标题**: 查询库存等于原库存减本次出库数量

**原子测试目的**: AP-APP026-DECREMENT

**状态/条件分支**: 常规业务场景

**auto**: auto

**type**: interface

**功能**: 库存联动

**追溯**: 需求=REQ-APP-026；测试计划=TEST_PLAN-REQ-APP-026；项目=种禽孵化管理系统；版本=4；状态=blocked_contract

**前置条件**:

- 已批准发货确认和库存变更窗口
- 已准备变更前库存、本次自动出库数量和可回读的库存查询结果

**公共前置引用**: `app_inventory_query_access`

**步骤**:

1. 完成一次有效发货确认并回读目标存发苗间的库存数量
   - 预期：查询到的库存数量等于变更前库存减去本次自动出库数量

## TC-APP-026-007 / TEST_PLAN-REQ-APP-026 [P3] auto=auto

**标题**: 查询展示目标存发苗间库存数量

**原子测试目的**: AP-APP026-QUERY-QUANTITY

**状态/条件分支**: 常规业务场景

**auto**: auto

**type**: feature

**功能**: 库存查询

**追溯**: 需求=REQ-APP-026；测试计划=TEST_PLAN-REQ-APP-026；项目=种禽孵化管理系统；版本=4；状态=blocked_contract

**前置条件**:

- 授权查询角色可用
- 已准备库存数量明确且大于零的存发苗间
- 已准备可切换的目标孵化场

**公共前置引用**: `app_inventory_query_access`

**步骤**:

1. 查看目标存发苗间
   - 预期：页面展示该存发苗间的库存数量

## TC-APP-026-008 / TEST_PLAN-REQ-APP-026 [P3] auto=auto

**标题**: 零库存显示为0

**原子测试目的**: AP-APP026-ZERO

**状态/条件分支**: 常规业务场景

**auto**: auto

**type**: feature

**功能**: 库存查询

**追溯**: 需求=REQ-APP-026；测试计划=TEST_PLAN-REQ-APP-026；项目=种禽孵化管理系统；版本=4；状态=blocked_contract

**前置条件**:

- 授权查询角色可用
- 已准备库存为零且无在途出库的存发苗间
- 已准备可切换的目标孵化场

**步骤**:

1. 查看该存发苗间的库存数量
   - 预期：该存发苗间的库存数量显示为0

## 结论

- 用例交付状态：已生成待评审
- 未覆盖项/待确认项：无
- 备注：来源 YAML：REQ-APP-026；Markdown 由公共渲染器生成。

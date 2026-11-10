# P3 用例前置数据创建方案

> 依据 `07_ui_automation/data/*.json` 与 `04_testcases/TC_REQ-*.md`，覆盖所有优先级为 P3 且定义了 `dataType=precreated_*`（或内含 `precreatedData`）的数据项。本文只描述创建方案，不执行写入。

## 1. 总体规则

1. 按依赖顺序创建：分类 → 产品 → 设备 → 分组关系 → 目标/消息 → 告警规则 → 任务/脚本 → 告警配置。
2. 以 `dataKey` 去重；重复引用复用同一条基线，分页集合整体创建。
3. 创建前按 `businessFields` 查询；字段一致则复用，字段冲突不得覆盖，标记 `blocked`。
4. 记录创建 ID、租户、创建时间和创建者；仅清理本次创建的数据，不删除原始 fixture 或共享关系。
5. 创建后回查关键字段、租户和外键；失败按 `onCreateFailure=blocked` 处理。

## 2. 前置数据逐条清单

### 1. `category_readonly`
- 来源：`req002_test_data.json`；用例：`TC-REQ-002-013`；数据类型：`precreated_normal`

#### 前置数据内容
```json
{
  "dataKey": "category_readonly",
  "name": "AUTO_REQ002_READONLY",
  "sort": 200,
  "status": "enabled",
  "description": "产品分类查询基线数据"
}
```

#### 创建步骤
1. 切换测试租户，按 `dataKey` 与业务字段查询；完全匹配则登记并复用。
2. 未命中时按 `records` 逐条创建；没有 `records` 时按对象字段创建单条业务记录。
3. 校验状态、时间、产品/设备/规则/消息等外键存在且属于当前租户。
4. 重新查询并逐字段核对。
5. 登记记录 ID；测试完成按 `cleanupCreatedRecord` 逆序清理，本次关系按需解除。

#### provisioning 约束
```json
{
  "whenMissing": "auto_create",
  "matchBy": "business_fields",
  "businessFields": [
    "name",
    "sort",
    "status",
    "description"
  ],
  "recordCreatedByTest": true,
  "onCreateFailure": "blocked",
  "cleanupCreatedRecord": true
}
```

### 2. `category_deletable`
- 来源：`req002_test_data.json`；用例：`TC-REQ-002-015`；数据类型：`precreated_normal`

#### 前置数据内容
```json
{
  "dataKey": "category_deletable",
  "name": "AUTO_REQ002_DELETABLE",
  "sort": 600,
  "status": "enabled",
  "description": "可删除产品分类"
}
```

#### 创建步骤
1. 切换测试租户，按 `dataKey` 与业务字段查询；完全匹配则登记并复用。
2. 未命中时按 `records` 逐条创建；没有 `records` 时按对象字段创建单条业务记录。
3. 校验状态、时间、产品/设备/规则/消息等外键存在且属于当前租户。
4. 重新查询并逐字段核对。
5. 登记记录 ID；测试完成按 `cleanupCreatedRecord` 逆序清理，本次关系按需解除。

#### provisioning 约束
```json
{
  "whenMissing": "auto_create",
  "matchBy": "business_fields",
  "businessFields": [
    "name",
    "sort",
    "status",
    "description"
  ],
  "recordCreatedByTest": true,
  "onCreateFailure": "blocked",
  "cleanupCreatedRecord": true
}
```

### 3. `category_special_name`
- 来源：`req002_test_data.json`；用例：`TC-REQ-002-027`；数据类型：`precreated_special`

#### 前置数据内容
```json
{
  "dataKey": "category_special_name",
  "name": "AUTO_REQ002_特殊分类_#@!",
  "sort": 800,
  "status": "enabled",
  "description": "特殊名称分类"
}
```

#### 创建步骤
1. 切换测试租户，按 `dataKey` 与业务字段查询；完全匹配则登记并复用。
2. 未命中时按 `records` 逐条创建；没有 `records` 时按对象字段创建单条业务记录。
3. 校验状态、时间、产品/设备/规则/消息等外键存在且属于当前租户。
4. 重新查询并逐字段核对。
5. 登记记录 ID；测试完成按 `cleanupCreatedRecord` 逆序清理，本次关系按需解除。

#### provisioning 约束
```json
{
  "whenMissing": "auto_create",
  "matchBy": "business_fields",
  "businessFields": [
    "name",
    "sort",
    "status",
    "description"
  ],
  "recordCreatedByTest": true,
  "onCreateFailure": "blocked",
  "cleanupCreatedRecord": true
}
```

### 4. `category_same_name_a/b`
- 来源：`req002_test_data.json`；用例：`TC-REQ-002-028`；数据类型：`precreated_special`

#### 前置数据内容
```json
{
  "dataKey": "category_same_name_a/b",
  "records": [
    {
      "name": "AUTO_REQ002_SAME_NAME",
      "sort": 810,
      "status": "enabled",
      "description": "同名分类A"
    },
    {
      "name": "AUTO_REQ002_SAME_NAME",
      "sort": 820,
      "status": "disabled",
      "description": "同名分类B"
    }
  ]
}
```

#### 创建步骤
1. 切换测试租户，按 `dataKey` 与业务字段查询；完全匹配则登记并复用。
2. 未命中时按 `records` 逐条创建；没有 `records` 时按对象字段创建单条业务记录。
3. 校验状态、时间、产品/设备/规则/消息等外键存在且属于当前租户。
4. 重新查询并逐字段核对。
5. 登记记录 ID；测试完成按 `cleanupCreatedRecord` 逆序清理，本次关系按需解除。

#### provisioning 约束
```json
{
  "whenMissing": "auto_create",
  "matchBy": "business_fields",
  "businessFields": [
    "name",
    "sort",
    "status",
    "description"
  ],
  "recordCreatedByTest": true,
  "onCreateFailure": "blocked",
  "cleanupCreatedRecord": true
}
```

### 5. `category_special_description`
- 来源：`req002_test_data.json`；用例：`TC-REQ-002-029`；数据类型：`precreated_special`

#### 前置数据内容
```json
{
  "dataKey": "category_special_description",
  "name": "AUTO_REQ002_SPECIAL_DESCRIPTION",
  "sort": 830,
  "status": "enabled",
  "description": "特殊描述\n第二行\t空白"
}
```

#### 创建步骤
1. 切换测试租户，按 `dataKey` 与业务字段查询；完全匹配则登记并复用。
2. 未命中时按 `records` 逐条创建；没有 `records` 时按对象字段创建单条业务记录。
3. 校验状态、时间、产品/设备/规则/消息等外键存在且属于当前租户。
4. 重新查询并逐字段核对。
5. 登记记录 ID；测试完成按 `cleanupCreatedRecord` 逆序清理，本次关系按需解除。

#### provisioning 约束
```json
{
  "whenMissing": "auto_create",
  "matchBy": "business_fields",
  "businessFields": [
    "name",
    "sort",
    "status",
    "description"
  ],
  "recordCreatedByTest": true,
  "onCreateFailure": "blocked",
  "cleanupCreatedRecord": true
}
```

### 6. `category_empty_description`
- 来源：`req002_test_data.json`；用例：`TC-REQ-002-030`；数据类型：`precreated_special`

#### 前置数据内容
```json
{
  "dataKey": "category_empty_description",
  "name": "AUTO_REQ002_EMPTY_DESCRIPTION",
  "sort": 100,
  "status": "enabled",
  "description": ""
}
```

#### 创建步骤
1. 切换测试租户，按 `dataKey` 与业务字段查询；完全匹配则登记并复用。
2. 未命中时按 `records` 逐条创建；没有 `records` 时按对象字段创建单条业务记录。
3. 校验状态、时间、产品/设备/规则/消息等外键存在且属于当前租户。
4. 重新查询并逐字段核对。
5. 登记记录 ID；测试完成按 `cleanupCreatedRecord` 逆序清理，本次关系按需解除。

#### provisioning 约束
```json
{
  "whenMissing": "auto_create",
  "matchBy": "business_fields",
  "businessFields": [
    "name",
    "sort",
    "status",
    "description"
  ],
  "recordCreatedByTest": true,
  "onCreateFailure": "blocked",
  "cleanupCreatedRecord": true
}
```

### 7. `category_same_sort_a/b`
- 来源：`req002_test_data.json`；用例：`TC-REQ-002-033`；数据类型：`precreated_special`

#### 前置数据内容
```json
{
  "dataKey": "category_same_sort_a/b",
  "records": [
    {
      "name": "AUTO_REQ002_SAME_SORT_A",
      "sort": 840,
      "status": "enabled",
      "description": "相同排序分类A"
    },
    {
      "name": "AUTO_REQ002_SAME_SORT_B",
      "sort": 840,
      "status": "enabled",
      "description": "相同排序分类B"
    }
  ]
}
```

#### 创建步骤
1. 切换测试租户，按 `dataKey` 与业务字段查询；完全匹配则登记并复用。
2. 未命中时按 `records` 逐条创建；没有 `records` 时按对象字段创建单条业务记录。
3. 校验状态、时间、产品/设备/规则/消息等外键存在且属于当前租户。
4. 重新查询并逐字段核对。
5. 登记记录 ID；测试完成按 `cleanupCreatedRecord` 逆序清理，本次关系按需解除。

#### provisioning 约束
```json
{
  "whenMissing": "auto_create",
  "matchBy": "business_fields",
  "businessFields": [
    "name",
    "sort",
    "status",
    "description"
  ],
  "recordCreatedByTest": true,
  "onCreateFailure": "blocked",
  "cleanupCreatedRecord": true
}
```

### 8. `product_editable`
- 来源：`req003_test_data.json`；用例：`TC-REQ-003-016`；数据类型：`precreated_normal`

#### 前置数据内容
```json
{
  "dataKey": "product_editable",
  "name": "AUTO_REQ003_EDITABLE_CONFIG",
  "productKey": "AUTO_REQ003_EDITABLE_KEY",
  "categoryName": "AUTO_REQ003_ENABLED_CATEGORY",
  "deviceType": "直连设备",
  "description": "可编辑产品描述",
  "moreConfig": {
    "productIcon": "approved-icon.png",
    "productImage": "approved-image.png"
  }
}
```

#### 创建步骤
1. 切换测试租户，按 `dataKey` 与业务字段查询；完全匹配则登记并复用。
2. 未命中时按 `records` 逐条创建；没有 `records` 时按对象字段创建单条业务记录。
3. 校验状态、时间、产品/设备/规则/消息等外键存在且属于当前租户。
4. 重新查询并逐字段核对。
5. 登记记录 ID；测试完成按 `cleanupCreatedRecord` 逆序清理，本次关系按需解除。

#### provisioning 约束
```json
{
  "whenMissing": "auto_create",
  "matchBy": "business_fields",
  "businessFields": [
    "name",
    "productKey",
    "categoryName",
    "deviceType",
    "description",
    "moreConfig"
  ],
  "recordCreatedByTest": true,
  "onCreateFailure": "blocked",
  "cleanupCreatedRecord": true
}
```

### 9. `product_filter_target`
- 来源：`req003_test_data.json`；用例：`TC-REQ-003-039`；数据类型：`precreated_normal`

#### 前置数据内容
```json
{
  "dataKey": "product_filter_target",
  "name": "AUTO_REQ003_CASE_TARGET",
  "productKey": "AUTO_REQ003_CASE_KEY",
  "categoryName": "AUTO_REQ003_ENABLED_CATEGORY",
  "deviceType": "直连设备"
}
```

#### 创建步骤
1. 切换测试租户，按 `dataKey` 与业务字段查询；完全匹配则登记并复用。
2. 未命中时按 `records` 逐条创建；没有 `records` 时按对象字段创建单条业务记录。
3. 校验状态、时间、产品/设备/规则/消息等外键存在且属于当前租户。
4. 重新查询并逐字段核对。
5. 登记记录 ID；测试完成按 `cleanupCreatedRecord` 逆序清理，本次关系按需解除。

#### provisioning 约束
```json
{
  "whenMissing": "auto_create",
  "matchBy": "business_fields",
  "businessFields": [
    "name",
    "productKey",
    "categoryName",
    "deviceType"
  ],
  "recordCreatedByTest": true,
  "onCreateFailure": "blocked",
  "cleanupCreatedRecord": true
}
```

### 10. `group_009`
- 来源：`req004_test_data.json`；用例：`TC-REQ-004-009`；数据类型：`precreated_normal`

#### 前置数据内容
```json
{
  "dataKey": "group_009",
  "records": [
    {
      "name": "AUTO_REQ004_GROUP_009",
      "description": "REQ004 fixture",
      "status": "enabled",
      "createdAt": "2026-01-01T10:00:00Z"
    }
  ]
}
```

#### 创建步骤
1. 切换测试租户，按 `dataKey` 与业务字段查询；完全匹配则登记并复用。
2. 未命中时按 `records` 逐条创建；没有 `records` 时按对象字段创建单条业务记录。
3. 校验状态、时间、产品/设备/规则/消息等外键存在且属于当前租户。
4. 重新查询并逐字段核对。
5. 登记记录 ID；测试完成按 `cleanupCreatedRecord` 逆序清理，本次关系按需解除。

#### provisioning 约束
```json
{
  "whenMissing": "approved_fixture_or_auto_create",
  "matchBy": "business_fields",
  "businessFields": [
    "name",
    "description",
    "status"
  ],
  "recordCreatedByTest": true,
  "onCreateFailure": "blocked",
  "cleanupCreatedRecord": true
}
```

### 11. `group_016`
- 来源：`req004_test_data.json`；用例：`TC-REQ-004-016`；数据类型：`precreated_special`

#### 前置数据内容
```json
{
  "dataKey": "group_016",
  "records": [
    {
      "name": "AUTO_REQ004_GROUP_016",
      "description": "REQ004 fixture",
      "status": "enabled",
      "createdAt": "2026-01-01T10:00:00Z"
    }
  ]
}
```

#### 创建步骤
1. 切换测试租户，按 `dataKey` 与业务字段查询；完全匹配则登记并复用。
2. 未命中时按 `records` 逐条创建；没有 `records` 时按对象字段创建单条业务记录。
3. 校验状态、时间、产品/设备/规则/消息等外键存在且属于当前租户。
4. 重新查询并逐字段核对。
5. 登记记录 ID；测试完成按 `cleanupCreatedRecord` 逆序清理，本次关系按需解除。

#### provisioning 约束
```json
{
  "whenMissing": "approved_fixture_or_auto_create",
  "matchBy": "business_fields",
  "businessFields": [
    "name",
    "description",
    "status"
  ],
  "recordCreatedByTest": true,
  "onCreateFailure": "blocked",
  "cleanupCreatedRecord": true
}
```

### 12. `group_020`
- 来源：`req004_test_data.json`；用例：`TC-REQ-004-020`；数据类型：`precreated_pagination`

#### 前置数据内容
```json
{
  "dataKey": "group_020",
  "records": [
    {
      "name": "AUTO_REQ004_GROUP_020",
      "description": "REQ004 fixture",
      "status": "enabled",
      "createdAt": "2026-01-01T10:00:00Z"
    }
  ],
  "minimumPages": 2,
  "stableTotal": true,
  "recordsMustNotChangeDuringTest": true
}
```

#### 创建步骤
1. 切换测试租户，按 `dataKey` 与业务字段查询；完全匹配则登记并复用。
2. 未命中时按 `records` 逐条创建；没有 `records` 时按对象字段创建单条业务记录。
3. 校验状态、时间、产品/设备/规则/消息等外键存在且属于当前租户。
4. 创建完整集合，验证 `minimumPages`、`stableTotal`、`recordsMustNotChangeDuringTest`。
5. 登记记录 ID；测试完成按 `cleanupCreatedRecord` 逆序清理，本次关系按需解除。

#### provisioning 约束
```json
{
  "whenMissing": "approved_fixture_or_auto_create",
  "matchBy": "business_fields",
  "businessFields": [
    "name",
    "description",
    "status"
  ],
  "recordCreatedByTest": true,
  "onCreateFailure": "blocked",
  "cleanupCreatedRecord": true
}
```

### 13. `group_022`
- 来源：`req004_test_data.json`；用例：`TC-REQ-004-022`；数据类型：`precreated_normal`

#### 前置数据内容
```json
{
  "dataKey": "group_022",
  "records": [
    {
      "name": "AUTO_REQ004_GROUP_022",
      "description": "REQ004 fixture",
      "status": "enabled",
      "createdAt": "2026-01-01T10:00:00Z"
    }
  ]
}
```

#### 创建步骤
1. 切换测试租户，按 `dataKey` 与业务字段查询；完全匹配则登记并复用。
2. 未命中时按 `records` 逐条创建；没有 `records` 时按对象字段创建单条业务记录。
3. 校验状态、时间、产品/设备/规则/消息等外键存在且属于当前租户。
4. 重新查询并逐字段核对。
5. 登记记录 ID；测试完成按 `cleanupCreatedRecord` 逆序清理，本次关系按需解除。

#### provisioning 约束
```json
{
  "whenMissing": "approved_fixture_or_auto_create",
  "matchBy": "business_fields",
  "businessFields": [
    "name",
    "description",
    "status"
  ],
  "recordCreatedByTest": true,
  "onCreateFailure": "blocked",
  "cleanupCreatedRecord": true
}
```

### 14. `group_023`
- 来源：`req004_test_data.json`；用例：`TC-REQ-004-023`；数据类型：`precreated_normal`

#### 前置数据内容
```json
{
  "dataKey": "group_023",
  "records": [
    {
      "name": "AUTO_REQ004_GROUP_023",
      "description": "REQ004 fixture",
      "status": "enabled",
      "createdAt": "2026-01-01T10:00:00Z"
    }
  ]
}
```

#### 创建步骤
1. 切换测试租户，按 `dataKey` 与业务字段查询；完全匹配则登记并复用。
2. 未命中时按 `records` 逐条创建；没有 `records` 时按对象字段创建单条业务记录。
3. 校验状态、时间、产品/设备/规则/消息等外键存在且属于当前租户。
4. 重新查询并逐字段核对。
5. 登记记录 ID；测试完成按 `cleanupCreatedRecord` 逆序清理，本次关系按需解除。

#### provisioning 约束
```json
{
  "whenMissing": "approved_fixture_or_auto_create",
  "matchBy": "business_fields",
  "businessFields": [
    "name",
    "description",
    "status"
  ],
  "recordCreatedByTest": true,
  "onCreateFailure": "blocked",
  "cleanupCreatedRecord": true
}
```

### 15. `group_024`
- 来源：`req004_test_data.json`；用例：`TC-REQ-004-024`；数据类型：`precreated_normal`

#### 前置数据内容
```json
{
  "dataKey": "group_024",
  "records": [
    {
      "name": "AUTO_REQ004_GROUP_024",
      "description": "REQ004 fixture",
      "status": "enabled",
      "createdAt": "2026-01-01T10:00:00Z"
    }
  ]
}
```

#### 创建步骤
1. 切换测试租户，按 `dataKey` 与业务字段查询；完全匹配则登记并复用。
2. 未命中时按 `records` 逐条创建；没有 `records` 时按对象字段创建单条业务记录。
3. 校验状态、时间、产品/设备/规则/消息等外键存在且属于当前租户。
4. 重新查询并逐字段核对。
5. 登记记录 ID；测试完成按 `cleanupCreatedRecord` 逆序清理，本次关系按需解除。

#### provisioning 约束
```json
{
  "whenMissing": "approved_fixture_or_auto_create",
  "matchBy": "business_fields",
  "businessFields": [
    "name",
    "description",
    "status"
  ],
  "recordCreatedByTest": true,
  "onCreateFailure": "blocked",
  "cleanupCreatedRecord": true
}
```

### 16. `group_025`
- 来源：`req004_test_data.json`；用例：`TC-REQ-004-025`；数据类型：`precreated_normal`

#### 前置数据内容
```json
{
  "dataKey": "group_025",
  "records": [
    {
      "name": "AUTO_REQ004_GROUP_025",
      "description": "REQ004 fixture",
      "status": "enabled",
      "createdAt": "2026-01-01T10:00:00Z"
    }
  ]
}
```

#### 创建步骤
1. 切换测试租户，按 `dataKey` 与业务字段查询；完全匹配则登记并复用。
2. 未命中时按 `records` 逐条创建；没有 `records` 时按对象字段创建单条业务记录。
3. 校验状态、时间、产品/设备/规则/消息等外键存在且属于当前租户。
4. 重新查询并逐字段核对。
5. 登记记录 ID；测试完成按 `cleanupCreatedRecord` 逆序清理，本次关系按需解除。

#### provisioning 约束
```json
{
  "whenMissing": "approved_fixture_or_auto_create",
  "matchBy": "business_fields",
  "businessFields": [
    "name",
    "description",
    "status"
  ],
  "recordCreatedByTest": true,
  "onCreateFailure": "blocked",
  "cleanupCreatedRecord": true
}
```

### 17. `group_026`
- 来源：`req004_test_data.json`；用例：`TC-REQ-004-026`；数据类型：`precreated_normal`

#### 前置数据内容
```json
{
  "dataKey": "group_026",
  "records": [
    {
      "name": "AUTO_REQ004_GROUP_026",
      "description": "REQ004 fixture",
      "status": "enabled",
      "createdAt": "2026-01-01T10:00:00Z"
    }
  ]
}
```

#### 创建步骤
1. 切换测试租户，按 `dataKey` 与业务字段查询；完全匹配则登记并复用。
2. 未命中时按 `records` 逐条创建；没有 `records` 时按对象字段创建单条业务记录。
3. 校验状态、时间、产品/设备/规则/消息等外键存在且属于当前租户。
4. 重新查询并逐字段核对。
5. 登记记录 ID；测试完成按 `cleanupCreatedRecord` 逆序清理，本次关系按需解除。

#### provisioning 约束
```json
{
  "whenMissing": "approved_fixture_or_auto_create",
  "matchBy": "business_fields",
  "businessFields": [
    "name",
    "description",
    "status"
  ],
  "recordCreatedByTest": true,
  "onCreateFailure": "blocked",
  "cleanupCreatedRecord": true
}
```

### 18. `device_010`
- 来源：`req005_test_data.json`；用例：`TC-REQ-005-010`；数据类型：`precreated_normal`

#### 前置数据内容
```json
{
  "dataKey": "device_010",
  "records": [
    {
      "name": "AUTO_REQ005_DEVICE_010",
      "serialNumber": "AUTO_REQ005_SN_010",
      "product": "AUTO_REQ005_PRODUCT",
      "deviceType": "approved_device_type",
      "status": "online",
      "parentDevice": null,
      "remark": "REQ005 test baseline"
    }
  ]
}
```

#### 创建步骤
1. 切换测试租户，按 `dataKey` 与业务字段查询；完全匹配则登记并复用。
2. 未命中时按 `records` 逐条创建；没有 `records` 时按对象字段创建单条业务记录。
3. 校验状态、时间、产品/设备/规则/消息等外键存在且属于当前租户。
4. 重新查询并逐字段核对。
5. 登记记录 ID；测试完成按 `cleanupCreatedRecord` 逆序清理，本次关系按需解除。

#### provisioning 约束
```json
{
  "whenMissing": "approved_fixture_or_auto_create",
  "matchBy": "business_fields",
  "businessFields": [
    "name",
    "serialNumber",
    "product"
  ],
  "recordCreatedByTest": true,
  "onCreateFailure": "blocked",
  "cleanupCreatedRecord": true
}
```

### 19. `device_011`
- 来源：`req005_test_data.json`；用例：`TC-REQ-005-011`；数据类型：`precreated_normal`

#### 前置数据内容
```json
{
  "dataKey": "device_011",
  "records": [
    {
      "name": "AUTO_REQ005_DEVICE_011",
      "serialNumber": "AUTO_REQ005_SN_011",
      "product": "AUTO_REQ005_PRODUCT",
      "deviceType": "approved_device_type",
      "status": "online",
      "parentDevice": null,
      "remark": "REQ005 test baseline"
    }
  ]
}
```

#### 创建步骤
1. 切换测试租户，按 `dataKey` 与业务字段查询；完全匹配则登记并复用。
2. 未命中时按 `records` 逐条创建；没有 `records` 时按对象字段创建单条业务记录。
3. 校验状态、时间、产品/设备/规则/消息等外键存在且属于当前租户。
4. 重新查询并逐字段核对。
5. 登记记录 ID；测试完成按 `cleanupCreatedRecord` 逆序清理，本次关系按需解除。

#### provisioning 约束
```json
{
  "whenMissing": "approved_fixture_or_auto_create",
  "matchBy": "business_fields",
  "businessFields": [
    "name",
    "serialNumber",
    "product"
  ],
  "recordCreatedByTest": true,
  "onCreateFailure": "blocked",
  "cleanupCreatedRecord": true
}
```

### 20. `device_021`
- 来源：`req005_test_data.json`；用例：`TC-REQ-005-021`；数据类型：`precreated_special`

#### 前置数据内容
```json
{
  "dataKey": "device_021",
  "records": [
    {
      "name": "AUTO_REQ005_DEVICE_021",
      "serialNumber": "AUTO_REQ005_SN_021",
      "product": "AUTO_REQ005_PRODUCT",
      "deviceType": "approved_device_type",
      "status": "online",
      "parentDevice": null,
      "remark": "REQ005 test baseline"
    }
  ]
}
```

#### 创建步骤
1. 切换测试租户，按 `dataKey` 与业务字段查询；完全匹配则登记并复用。
2. 未命中时按 `records` 逐条创建；没有 `records` 时按对象字段创建单条业务记录。
3. 校验状态、时间、产品/设备/规则/消息等外键存在且属于当前租户。
4. 重新查询并逐字段核对。
5. 登记记录 ID；测试完成按 `cleanupCreatedRecord` 逆序清理，本次关系按需解除。

#### provisioning 约束
```json
{
  "whenMissing": "approved_fixture_or_auto_create",
  "matchBy": "business_fields",
  "businessFields": [
    "name",
    "serialNumber",
    "product"
  ],
  "recordCreatedByTest": true,
  "onCreateFailure": "blocked",
  "cleanupCreatedRecord": true
}
```

### 21. `device_037`
- 来源：`req005_test_data.json`；用例：`TC-REQ-005-037`；数据类型：`precreated_normal`

#### 前置数据内容
```json
{
  "dataKey": "device_037",
  "records": [
    {
      "name": "AUTO_REQ005_DEVICE_037",
      "serialNumber": "AUTO_REQ005_SN_037",
      "product": "AUTO_REQ005_PRODUCT",
      "deviceType": "approved_device_type",
      "status": "online",
      "parentDevice": null,
      "remark": "REQ005 test baseline"
    }
  ]
}
```

#### 创建步骤
1. 切换测试租户，按 `dataKey` 与业务字段查询；完全匹配则登记并复用。
2. 未命中时按 `records` 逐条创建；没有 `records` 时按对象字段创建单条业务记录。
3. 校验状态、时间、产品/设备/规则/消息等外键存在且属于当前租户。
4. 重新查询并逐字段核对。
5. 登记记录 ID；测试完成按 `cleanupCreatedRecord` 逆序清理，本次关系按需解除。

#### provisioning 约束
```json
{
  "whenMissing": "approved_fixture_or_auto_create",
  "matchBy": "business_fields",
  "businessFields": [
    "name",
    "serialNumber",
    "product"
  ],
  "recordCreatedByTest": true,
  "onCreateFailure": "blocked",
  "cleanupCreatedRecord": true
}
```

### 22. `device_038`
- 来源：`req005_test_data.json`；用例：`TC-REQ-005-038`；数据类型：`precreated_normal`

#### 前置数据内容
```json
{
  "dataKey": "device_038",
  "records": [
    {
      "name": "AUTO_REQ005_DEVICE_038",
      "serialNumber": "AUTO_REQ005_SN_038",
      "product": "AUTO_REQ005_PRODUCT",
      "deviceType": "approved_device_type",
      "status": "online",
      "parentDevice": null,
      "remark": "REQ005 test baseline"
    }
  ]
}
```

#### 创建步骤
1. 切换测试租户，按 `dataKey` 与业务字段查询；完全匹配则登记并复用。
2. 未命中时按 `records` 逐条创建；没有 `records` 时按对象字段创建单条业务记录。
3. 校验状态、时间、产品/设备/规则/消息等外键存在且属于当前租户。
4. 重新查询并逐字段核对。
5. 登记记录 ID；测试完成按 `cleanupCreatedRecord` 逆序清理，本次关系按需解除。

#### provisioning 约束
```json
{
  "whenMissing": "approved_fixture_or_auto_create",
  "matchBy": "business_fields",
  "businessFields": [
    "name",
    "serialNumber",
    "product"
  ],
  "recordCreatedByTest": true,
  "onCreateFailure": "blocked",
  "cleanupCreatedRecord": true
}
```

### 23. `device_041`
- 来源：`req005_test_data.json`；用例：`TC-REQ-005-041`；数据类型：`precreated_special`

#### 前置数据内容
```json
{
  "dataKey": "device_041",
  "records": [
    {
      "name": "AUTO_REQ005_DEVICE_041",
      "serialNumber": "AUTO_REQ005_SN_041",
      "product": "AUTO_REQ005_PRODUCT",
      "deviceType": "approved_device_type",
      "status": "online",
      "parentDevice": null,
      "remark": "REQ005 test baseline"
    }
  ]
}
```

#### 创建步骤
1. 切换测试租户，按 `dataKey` 与业务字段查询；完全匹配则登记并复用。
2. 未命中时按 `records` 逐条创建；没有 `records` 时按对象字段创建单条业务记录。
3. 校验状态、时间、产品/设备/规则/消息等外键存在且属于当前租户。
4. 重新查询并逐字段核对。
5. 登记记录 ID；测试完成按 `cleanupCreatedRecord` 逆序清理，本次关系按需解除。

#### provisioning 约束
```json
{
  "whenMissing": "approved_fixture_or_auto_create",
  "matchBy": "business_fields",
  "businessFields": [
    "name",
    "serialNumber",
    "product"
  ],
  "recordCreatedByTest": true,
  "onCreateFailure": "blocked",
  "cleanupCreatedRecord": true
}
```

### 24. `device_042`
- 来源：`req005_test_data.json`；用例：`TC-REQ-005-042`；数据类型：`precreated_special`

#### 前置数据内容
```json
{
  "dataKey": "device_042",
  "records": [
    {
      "name": "AUTO_REQ005_DEVICE_042",
      "serialNumber": "AUTO_REQ005_SN_042",
      "product": "AUTO_REQ005_PRODUCT",
      "deviceType": "approved_device_type",
      "status": "online",
      "parentDevice": null,
      "remark": "REQ005 test baseline"
    }
  ]
}
```

#### 创建步骤
1. 切换测试租户，按 `dataKey` 与业务字段查询；完全匹配则登记并复用。
2. 未命中时按 `records` 逐条创建；没有 `records` 时按对象字段创建单条业务记录。
3. 校验状态、时间、产品/设备/规则/消息等外键存在且属于当前租户。
4. 重新查询并逐字段核对。
5. 登记记录 ID；测试完成按 `cleanupCreatedRecord` 逆序清理，本次关系按需解除。

#### provisioning 约束
```json
{
  "whenMissing": "approved_fixture_or_auto_create",
  "matchBy": "business_fields",
  "businessFields": [
    "name",
    "serialNumber",
    "product"
  ],
  "recordCreatedByTest": true,
  "onCreateFailure": "blocked",
  "cleanupCreatedRecord": true
}
```

### 25. `rule_008`
- 来源：`req007_test_data.json`；用例：`TC-REQ-007-008`；数据类型：`input`

#### 前置数据内容
```json
{
  "dataKey": "rule_008",
  "records": [
    {
      "name": "AUTO_REQ007_RULE_008",
      "ruleId": "AUTO_REQ007_RULE_ID_008",
      "status": "enabled",
      "conditions": [
        "device.status=online"
      ],
      "actions": [
        "raise_alert"
      ],
      "triggers": [
        "device_event"
      ],
      "tenant": "AUTO_REQ007_TENANT"
    }
  ]
}
```

#### 创建步骤
1. 切换测试租户，按 `dataKey` 与业务字段查询；完全匹配则登记并复用。
2. 未命中时按 `records` 逐条创建；没有 `records` 时按对象字段创建单条业务记录。
3. 校验状态、时间、产品/设备/规则/消息等外键存在且属于当前租户。
4. 重新查询并逐字段核对。
5. 登记记录 ID；测试完成按 `cleanupCreatedRecord` 逆序清理，本次关系按需解除。

#### provisioning 约束
```json
{
  "whenMissing": "approved_fixture_or_auto_create",
  "matchBy": "business_fields",
  "businessFields": [
    "name",
    "status",
    "conditions",
    "actions",
    "triggers"
  ],
  "recordCreatedByTest": true,
  "onCreateFailure": "blocked",
  "cleanupCreatedRecord": true
}
```

### 26. `rule_020`
- 来源：`req007_test_data.json`；用例：`TC-REQ-007-020`；数据类型：`precreated_normal`

#### 前置数据内容
```json
{
  "dataKey": "rule_020",
  "records": [
    {
      "name": "AUTO_REQ007_RULE_020",
      "ruleId": "AUTO_REQ007_RULE_ID_020",
      "status": "enabled",
      "conditions": [
        "device.status=online"
      ],
      "actions": [
        "raise_alert"
      ],
      "triggers": [
        "device_event"
      ],
      "tenant": "AUTO_REQ007_TENANT"
    }
  ]
}
```

#### 创建步骤
1. 切换测试租户，按 `dataKey` 与业务字段查询；完全匹配则登记并复用。
2. 未命中时按 `records` 逐条创建；没有 `records` 时按对象字段创建单条业务记录。
3. 校验状态、时间、产品/设备/规则/消息等外键存在且属于当前租户。
4. 重新查询并逐字段核对。
5. 登记记录 ID；测试完成按 `cleanupCreatedRecord` 逆序清理，本次关系按需解除。

#### provisioning 约束
```json
{
  "whenMissing": "approved_fixture_or_auto_create",
  "matchBy": "business_fields",
  "businessFields": [
    "name",
    "status",
    "conditions",
    "actions",
    "triggers"
  ],
  "recordCreatedByTest": true,
  "onCreateFailure": "blocked",
  "cleanupCreatedRecord": true
}
```

### 27. `rule_029`
- 来源：`req007_test_data.json`；用例：`TC-REQ-007-029`；数据类型：`precreated_normal`

#### 前置数据内容
```json
{
  "dataKey": "rule_029",
  "records": [
    {
      "name": "AUTO_REQ007_RULE_029",
      "ruleId": "AUTO_REQ007_RULE_ID_029",
      "status": "enabled",
      "conditions": [
        "device.status=online"
      ],
      "actions": [
        "raise_alert"
      ],
      "triggers": [
        "device_event"
      ],
      "tenant": "AUTO_REQ007_TENANT"
    }
  ]
}
```

#### 创建步骤
1. 切换测试租户，按 `dataKey` 与业务字段查询；完全匹配则登记并复用。
2. 未命中时按 `records` 逐条创建；没有 `records` 时按对象字段创建单条业务记录。
3. 校验状态、时间、产品/设备/规则/消息等外键存在且属于当前租户。
4. 重新查询并逐字段核对。
5. 登记记录 ID；测试完成按 `cleanupCreatedRecord` 逆序清理，本次关系按需解除。

#### provisioning 约束
```json
{
  "whenMissing": "approved_fixture_or_auto_create",
  "matchBy": "business_fields",
  "businessFields": [
    "name",
    "status",
    "conditions",
    "actions",
    "triggers"
  ],
  "recordCreatedByTest": true,
  "onCreateFailure": "blocked",
  "cleanupCreatedRecord": true
}
```

### 28. `target_002`
- 来源：`req008_test_data.json`；用例：`TC-REQ-008-002`；数据类型：`precreated_normal`

#### 前置数据内容
```json
{
  "dataKey": "target_002",
  "records": [
    {
      "name": "AUTO_REQ008_TARGET_002",
      "protocol": "HTTP",
      "status": "enabled",
      "createdAt": "2026-01-01T10:00:00Z",
      "address": "http://127.0.0.1:18080/req008",
      "topic": "AUTO_REQ008_TOPIC",
      "description": "REQ008 fixture"
    }
  ]
}
```

#### 创建步骤
1. 切换测试租户，按 `dataKey` 与业务字段查询；完全匹配则登记并复用。
2. 未命中时按 `records` 逐条创建；没有 `records` 时按对象字段创建单条业务记录。
3. 校验状态、时间、产品/设备/规则/消息等外键存在且属于当前租户。
4. 重新查询并逐字段核对。
5. 登记记录 ID；测试完成按 `cleanupCreatedRecord` 逆序清理，本次关系按需解除。

#### provisioning 约束
```json
{
  "whenMissing": "approved_fixture_or_auto_create",
  "matchBy": "business_fields",
  "businessFields": [
    "name",
    "protocol",
    "status"
  ],
  "recordCreatedByTest": true,
  "onCreateFailure": "blocked",
  "cleanupCreatedRecord": true
}
```

### 29. `target_003`
- 来源：`req008_test_data.json`；用例：`TC-REQ-008-003`；数据类型：`precreated_normal`

#### 前置数据内容
```json
{
  "dataKey": "target_003",
  "records": [
    {
      "name": "AUTO_REQ008_TARGET_003",
      "protocol": "HTTP",
      "status": "enabled",
      "createdAt": "2026-01-01T10:00:00Z",
      "address": "http://127.0.0.1:18080/req008",
      "topic": "AUTO_REQ008_TOPIC",
      "description": "REQ008 fixture"
    }
  ]
}
```

#### 创建步骤
1. 切换测试租户，按 `dataKey` 与业务字段查询；完全匹配则登记并复用。
2. 未命中时按 `records` 逐条创建；没有 `records` 时按对象字段创建单条业务记录。
3. 校验状态、时间、产品/设备/规则/消息等外键存在且属于当前租户。
4. 重新查询并逐字段核对。
5. 登记记录 ID；测试完成按 `cleanupCreatedRecord` 逆序清理，本次关系按需解除。

#### provisioning 约束
```json
{
  "whenMissing": "approved_fixture_or_auto_create",
  "matchBy": "business_fields",
  "businessFields": [
    "name",
    "protocol",
    "status"
  ],
  "recordCreatedByTest": true,
  "onCreateFailure": "blocked",
  "cleanupCreatedRecord": true
}
```

### 30. `target_004`
- 来源：`req008_test_data.json`；用例：`TC-REQ-008-004`；数据类型：`precreated_normal`

#### 前置数据内容
```json
{
  "dataKey": "target_004",
  "records": [
    {
      "name": "AUTO_REQ008_TARGET_004",
      "protocol": "HTTP",
      "status": "enabled",
      "createdAt": "2026-01-01T10:00:00Z",
      "address": "http://127.0.0.1:18080/req008",
      "topic": "AUTO_REQ008_TOPIC",
      "description": "REQ008 fixture"
    }
  ]
}
```

#### 创建步骤
1. 切换测试租户，按 `dataKey` 与业务字段查询；完全匹配则登记并复用。
2. 未命中时按 `records` 逐条创建；没有 `records` 时按对象字段创建单条业务记录。
3. 校验状态、时间、产品/设备/规则/消息等外键存在且属于当前租户。
4. 重新查询并逐字段核对。
5. 登记记录 ID；测试完成按 `cleanupCreatedRecord` 逆序清理，本次关系按需解除。

#### provisioning 约束
```json
{
  "whenMissing": "approved_fixture_or_auto_create",
  "matchBy": "business_fields",
  "businessFields": [
    "name",
    "protocol",
    "status"
  ],
  "recordCreatedByTest": true,
  "onCreateFailure": "blocked",
  "cleanupCreatedRecord": true
}
```

### 31. `target_005`
- 来源：`req008_test_data.json`；用例：`TC-REQ-008-005`；数据类型：`precreated_normal`

#### 前置数据内容
```json
{
  "dataKey": "target_005",
  "records": [
    {
      "name": "AUTO_REQ008_TARGET_005",
      "protocol": "HTTP",
      "status": "enabled",
      "createdAt": "2026-01-01T10:00:00Z",
      "address": "http://127.0.0.1:18080/req008",
      "topic": "AUTO_REQ008_TOPIC",
      "description": "REQ008 fixture"
    }
  ]
}
```

#### 创建步骤
1. 切换测试租户，按 `dataKey` 与业务字段查询；完全匹配则登记并复用。
2. 未命中时按 `records` 逐条创建；没有 `records` 时按对象字段创建单条业务记录。
3. 校验状态、时间、产品/设备/规则/消息等外键存在且属于当前租户。
4. 重新查询并逐字段核对。
5. 登记记录 ID；测试完成按 `cleanupCreatedRecord` 逆序清理，本次关系按需解除。

#### provisioning 约束
```json
{
  "whenMissing": "approved_fixture_or_auto_create",
  "matchBy": "business_fields",
  "businessFields": [
    "name",
    "protocol",
    "status"
  ],
  "recordCreatedByTest": true,
  "onCreateFailure": "blocked",
  "cleanupCreatedRecord": true
}
```

### 32. `target_006`
- 来源：`req008_test_data.json`；用例：`TC-REQ-008-006`；数据类型：`precreated_normal`

#### 前置数据内容
```json
{
  "dataKey": "target_006",
  "records": [
    {
      "name": "AUTO_REQ008_TARGET_006",
      "protocol": "HTTP",
      "status": "enabled",
      "createdAt": "2026-01-01T10:00:00Z",
      "address": "http://127.0.0.1:18080/req008",
      "topic": "AUTO_REQ008_TOPIC",
      "description": "REQ008 fixture"
    }
  ]
}
```

#### 创建步骤
1. 切换测试租户，按 `dataKey` 与业务字段查询；完全匹配则登记并复用。
2. 未命中时按 `records` 逐条创建；没有 `records` 时按对象字段创建单条业务记录。
3. 校验状态、时间、产品/设备/规则/消息等外键存在且属于当前租户。
4. 重新查询并逐字段核对。
5. 登记记录 ID；测试完成按 `cleanupCreatedRecord` 逆序清理，本次关系按需解除。

#### provisioning 约束
```json
{
  "whenMissing": "approved_fixture_or_auto_create",
  "matchBy": "business_fields",
  "businessFields": [
    "name",
    "protocol",
    "status"
  ],
  "recordCreatedByTest": true,
  "onCreateFailure": "blocked",
  "cleanupCreatedRecord": true
}
```

### 33. `target_date_pagination_set`
- 来源：`req008_test_data.json`；用例：`TC-REQ-008-008`；数据类型：`precreated_pagination`

#### 前置数据内容
```json
{
  "dataKey": "target_date_pagination_set",
  "records": [
    {
      "name": "AUTO_REQ008_TARGET_OLD",
      "protocol": "HTTP",
      "status": "enabled",
      "createdAt": "2026-01-01T10:00:00Z"
    },
    {
      "name": "AUTO_REQ008_TARGET_NEW",
      "protocol": "MQTT",
      "status": "disabled",
      "createdAt": "2026-02-01T10:00:00Z"
    }
  ],
  "minimumPages": 2,
  "stableTotal": true,
  "recordsMustNotChangeDuringTest": true
}
```

#### 创建步骤
1. 切换测试租户，按 `dataKey` 与业务字段查询；完全匹配则登记并复用。
2. 未命中时按 `records` 逐条创建；没有 `records` 时按对象字段创建单条业务记录。
3. 校验状态、时间、产品/设备/规则/消息等外键存在且属于当前租户。
4. 创建完整集合，验证 `minimumPages`、`stableTotal`、`recordsMustNotChangeDuringTest`。
5. 登记记录 ID；测试完成按 `cleanupCreatedRecord` 逆序清理，本次关系按需解除。

#### provisioning 约束
```json
{
  "whenMissing": "approved_fixture_or_auto_create",
  "matchBy": "business_fields",
  "businessFields": [
    "name",
    "protocol",
    "status"
  ],
  "recordCreatedByTest": true,
  "onCreateFailure": "blocked",
  "cleanupCreatedRecord": true
}
```

### 34. `task_025`
- 来源：`req009_test_data.json`；用例：`TC-REQ-009-025`；数据类型：`precreated_normal`

#### 前置数据内容
```json
{
  "dataKey": "task_025",
  "records": [
    {
      "name": "AUTO_REQ009_TASK_025",
      "taskId": "AUTO_REQ009_TASK_ID_025",
      "status": "created",
      "pluginId": "AUTO_REQ009_PLUGIN_025",
      "cron": "0 0 * * *",
      "script": "return true",
      "restartPolicy": "never",
      "memory": "256Mi",
      "createdAt": "2026-01-01T10:00:00Z"
    }
  ]
}
```

#### 创建步骤
1. 切换测试租户，按 `dataKey` 与业务字段查询；完全匹配则登记并复用。
2. 未命中时按 `records` 逐条创建；没有 `records` 时按对象字段创建单条业务记录。
3. 校验状态、时间、产品/设备/规则/消息等外键存在且属于当前租户。
4. 重新查询并逐字段核对。
5. 登记记录 ID；测试完成按 `cleanupCreatedRecord` 逆序清理，本次关系按需解除。

#### provisioning 约束
```json
{
  "whenMissing": "approved_fixture_or_auto_create",
  "matchBy": "business_fields",
  "businessFields": [
    "name",
    "taskId",
    "status"
  ],
  "recordCreatedByTest": true,
  "onCreateFailure": "blocked",
  "cleanupCreatedRecord": true
}
```

### 35. `alert_012`
- 来源：`req011_test_data.json`；用例：`TC-REQ-011-012`；数据类型：`precreated_special`

#### 前置数据内容
```json
{
  "dataKey": "alert_012",
  "records": [
    {
      "recordKey": "AUTO_REQ011_ALERT_012",
      "alertConfig": "AUTO_REQ011_CONFIG_012",
      "level": "high",
      "product": "AUTO_REQ011_PRODUCT_012",
      "deviceId": "AUTO_REQ011_DEVICE_012",
      "processed": false,
      "createdAt": "2026-03-01T00:00:00Z",
      "tenant": "AUTO_REQ011_TENANT"
    }
  ],
  "timeBoundary": true
}
```

#### 创建步骤
1. 切换测试租户，按 `dataKey` 与业务字段查询；完全匹配则登记并复用。
2. 未命中时按 `records` 逐条创建；没有 `records` 时按对象字段创建单条业务记录。
3. 校验状态、时间、产品/设备/规则/消息等外键存在且属于当前租户。
4. 重新查询并逐字段核对。
5. 登记记录 ID；测试完成按 `cleanupCreatedRecord` 逆序清理，本次关系按需解除。

#### provisioning 约束
```json
{
  "whenMissing": "approved_fixture_or_auto_create",
  "matchBy": "business_fields",
  "businessFields": [
    "recordKey",
    "alertConfig",
    "product",
    "deviceId",
    "processed"
  ],
  "recordCreatedByTest": true,
  "onCreateFailure": "blocked",
  "cleanupCreatedRecord": true
}
```

## 3. 跨模块创建顺序
1. REQ-002：分类及分页/同名/同排序基线。
2. REQ-003：引用启用分类，图片使用批准 fixture。
3. REQ-005：引用产品创建设备。
4. REQ-004：创建分组并建立设备关系。
5. REQ-008：创建目标、消息和日期分页集合。
6. REQ-007：创建告警规则。
7. REQ-009：确认插件、设备、脚本后创建任务。
8. REQ-011：最后创建产品/设备/消息/时区/规则引用均可解析的告警配置。

## 4. 验收与清理
- 所有 `dataKey` 可唯一定位，字段和引用关系回查通过。
- 分页集合总数稳定，测试期间不被其他用例修改。
- 按创建登记表逆序清理；保留 approved fixture 和原有数据。
- 字段冲突、外键缺失、跨租户可见、总数漂移、创建失败均阻塞相关 P3 用例。

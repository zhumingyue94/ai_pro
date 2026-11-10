# REQ-PC-046 表格分段截图记录

- 页面：`库存管理 / 合格蛋蛋库 / 出入库记录`
- URL: `http://192.168.6.163:66/biopark-breeding/breeding/stock/pass/firsteggrecord`
- 浏览器模式：headed（可见浏览器，headless=false）
- 采集方式：agent-browser CLI，视口截图（非 full-page），未使用 CSS `zoom`、`body.style.zoom` 或任何页面压缩

## 视口与表格尺寸

- 浏览器视口：`1258 x 622` CSS px
- 表格横向滚动容器：`.el-table__body-wrapper .el-scrollbar__wrap`（DOM 中 `.el-scrollbar__wrap` 索引 3）
- 表格内容宽度：`2675` px
- 表格可视宽度：`959` px
- 最大横向滚动距离：`1716` px（`scrollWidth - clientWidth`）
- 查询结果：`20` 行（20 条/页，共 3 页），孵化场筛选固定为 `南京孵化场`

## 横向滚动条定位说明

初次采集时误用 `document.querySelector('.el-scrollbar__wrap')`，命中的是左侧菜单滚动容器（`scrollWidth = clientWidth = 220`，不可横向滚动），导致三次截图内容完全一致。

修正后通过遍历所有 `.el-scrollbar__wrap` 并比对 `scrollWidth / clientWidth`，定位到索引 3 的表格横向滚动容器（`2675 / 959`），设置 `scrollLeft` 后生效并可稳定保持。

## 表头字段（19 个，顺序与 DOM 一致）

`库位号 / 出/入库 / 孵化场 / 仓库 / 仓库类型 / 养殖场 / 养殖批次 / 品种 / 产蛋日期 / 蛋重类型 / 平均蛋重 / 周龄 / 种蛋类型 / 数量 / 方式 / 原因 / 时间 / 上孵计划号 / 备注`

## 分段截图覆盖

| 截图 | scrollLeft | 覆盖内容区间 | 可见表头 |
|---|---|---|---|
| `req-pc-046-table-left.png` | `0` | `0 ~ 959` | 出/入库、孵化场、仓库、仓库类型、库位号、养殖场 |
| `req-pc-046-table-middle.png` | `858` | `858 ~ 1817` | 库位号、品种、产蛋日期、蛋重类型、平均蛋重、周龄、种蛋类型 |
| `req-pc-046-table-right.png` | `1716` | `1716 ~ 2675` | 养殖场、数量、方式、原因、时间、上孵计划号、备注 |

三段区间相互重叠，`0 ~ 2675` 全部覆盖，表头随表格横向滚动同步显示（Element Plus 表格滚动同步行为）。

## 页面可见控件（只读探索）

`查询`、`重置`、`展开`、`刷新`、`表头设置`、`导出`、`查看全部`

本次仅执行登录、进入页面、选择孵化场、查询、读取表格与横向滚动；未执行新增、编辑、删除、提交、导出确认或任何业务数据变更。

"use strict";
/* 将同一批 results.json 生成 Summary、Case Results、Steps & Evidence 三张表。 */

import fs from "fs";
import { createRequire } from "module";

const require = createRequire(import.meta.url);
const { Workbook, SpreadsheetFile } = require("@oai/artifact-tool");

function cell(value) {
  // Return a spreadsheet-safe display value.
  if (value === null || value === undefined) return "";
  if (typeof value === "object") return JSON.stringify(value, null, 2);
  return String(value);
}

function styleHeader(sheet, columnCount) {
  // Apply readable formatting to a worksheet header.
  sheet.getRangeByIndexes(0, 0, 1, columnCount).format = {
    fill: "#305496",
    font: { color: "#FFFFFF", bold: true },
    horizontalAlignment: "center",
    verticalAlignment: "center",
    wrapText: true,
  };
}

function writeTable(sheet, headers, rows, tableName) {
  // Write a table and apply stable header/body formatting.
  sheet.getRangeByIndexes(0, 0, 1, headers.length).values = [headers];
  if (rows.length > 0) sheet.getRangeByIndexes(1, 0, rows.length, headers.length).values = rows;
  styleHeader(sheet, headers.length);
  if (rows.length > 0) sheet.getRangeByIndexes(1, 0, rows.length, headers.length).format = { verticalAlignment: "top", wrapText: true };
  sheet.tables.add(`A1:${String.fromCharCode(64 + headers.length)}${rows.length + 1}`, true, tableName);
  sheet.freezePanes.freezeRows(1);
  sheet.showGridLines = false;
}

async function main() {
  // Read results JSON and export the required case-results workbook.
  const [inputPath, outputPath] = process.argv.slice(2);
  if (!inputPath || !outputPath) {
    console.error("usage: node build_case_results.mjs <results.json> <output.xlsx>");
    process.exit(1);
  }
  const data = JSON.parse(fs.readFileSync(inputPath, "utf-8"));
  const cases = Array.isArray(data.cases) ? data.cases : [];
  const wb = Workbook.create();

  const summary = wb.worksheets.add("Summary");
  const counts = {};
  cases.forEach((item) => { counts[item.status] = (counts[item.status] || 0) + 1; });
  const summaryRows = [
    ["RUN", cell(data.run_id)], ["需求", cell(data.req_id)], ["模块", cell(data.module)],
    ["模块ID", cell(data.zentao_module_id)], ["环境", cell(data.environment)], ["生成时间", cell(data.generated_at)],
    ["用例总数", cases.length], ["状态统计", JSON.stringify(counts)], ["来源文件", cell(data.source)],
  ];
  writeTable(summary, ["字段", "值"], summaryRows, "SummaryTable");

  const caseSheet = wb.worksheets.add("Case Results");
  const caseHeaders = ["本地用例ID", "禅道用例ID", "标题", "类型", "自动化", "状态", "失败分类", "check_id", "assertion_scope", "预期", "实际情况", "错误来源", "截图相对路径", "截图SHA-256", "开始时间", "结束时间", "数据准备"];
  const caseRows = cases.map((item) => {
    const shots = Array.isArray(item.screenshots) ? item.screenshots : [];
    return [item.case_id, item.zentao_case_id, item.title, item.type, item.auto, item.status, item.classification, item.check_id, item.assertion_scope, cell(item.expected), cell(item.actual), item.failure_origin || "", shots.map((shot) => shot.path).join("\n"), shots.map((shot) => shot.sha256).join("\n"), item.started_at || "", item.finished_at || "", cell(item.data_preparation)];
  });
  writeTable(caseSheet, caseHeaders, caseRows, "CaseResultsTable");

  const evidence = wb.worksheets.add("Steps & Evidence");
  const evidenceHeaders = ["本地用例ID", "禅道用例ID", "check_id", "assertion_scope", "步骤序号", "动作", "预期", "实际观测", "截图路径", "截图SHA-256"];
  const evidenceRows = [];
  cases.forEach((item) => {
    const shots = Array.isArray(item.screenshots) ? item.screenshots : [];
    const steps = Array.isArray(item.steps) && item.steps.length ? item.steps : [{ action: "", expected: "", actual: "" }];
    steps.forEach((step, index) => {
      const shot = shots[index] || shots[0] || {};
      evidenceRows.push([item.case_id, item.zentao_case_id, item.check_id, item.assertion_scope, step.index || index + 1, step.action || "", step.expected || "", cell(step.actual), shot.path || "", shot.sha256 || ""]);
    });
  });
  writeTable(evidence, evidenceHeaders, evidenceRows, "StepsEvidenceTable");

  const file = await SpreadsheetFile.exportXlsx(wb);
  await file.save(outputPath);
  console.log("xlsx written: " + outputPath);
}

main().catch((error) => {
  console.error("xlsx generation failed:", error);
  process.exit(1);
});

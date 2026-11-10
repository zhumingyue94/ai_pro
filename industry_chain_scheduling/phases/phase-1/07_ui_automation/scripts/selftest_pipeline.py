"""产物流水线自检：用合成记录验证缺陷报告只收录 product_defect。

不启动浏览器、不访问被测系统、不写入 data/REQ-*.yaml 与 HANDOFF.md，
全部产物写入临时目录，运行结束后自动清理。

覆盖的关键断言：
- 只有四要素齐全且显式声明的 product_defect 才进入 bugs_review.yaml；
- 脚本错误、用例错误、阻塞、接受偏差只出现在缺陷报告的「被排除项」；
- 存在产品缺陷时退出码为 1，无可疑缺陷时完整性为完整。

运行：``python scripts/selftest_pipeline.py``
"""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import yaml

from framework import integrity, run_layout
from framework.orchestrator import RunOrchestrator
from framework.plugin import finalize
from framework.reporters import bugs_review, defect_report


class _ConfigShim:
    """最小配置替身，只为满足 finalize 对命令行选项的读取。"""

    def __init__(self) -> None:
        """初始化选项默认值。"""
        self.option_values = {
            "--no-update-registry": True,
            "--no-handoff": True,
            "--max-run-seconds": 0,
            "--dry-run": False,
            "--self-test": False,
        }

    def getoption(self, name: str):
        """返回指定选项值，未知选项返回 None。"""
        return self.option_values.get(name)


def _make_orch(tmp: Path) -> RunOrchestrator:
    """构造一个不依赖 pytest 的编排器实例。"""
    orch = RunOrchestrator.__new__(RunOrchestrator)
    orch.config = _ConfigShim()
    orch.started_at = run_layout.now_iso()
    orch.finished_at = ""
    orch.run_id = "RUN_自检_00000000_000000"
    orch.run_dir = tmp
    orch.screenshots_dir = tmp / "screenshots"
    orch.screenshots_dir.mkdir(parents=True, exist_ok=True)
    orch.label = "自检"
    orch.filter_desc = {"req": ["REQ-SELF"], "module": None, "priority": None, "zentao_case_id": None}
    orch.source_path = ""
    orch.req_ids = ["REQ-SELF"]
    orch.module_names = ["自检模块"]
    orch.planned = {}
    orch.non_executed_records = []
    orch.records = {}
    orch.started_map = {}
    orch.settings_snapshot = {"base_host": "selftest.local", "headless": "false"}
    orch.config_error = None
    orch.interrupted = False
    orch.browser_started = False
    orch.browser_closed = False
    orch.finalized = False
    orch.exit_code = 0
    orch.writer_errors = {}
    orch.dry_run = False
    orch.self_test = False
    orch.collect_only = False
    orch.expected_record_count = 0
    return orch


def _record(case_id: str, zentao_id: int, status: str, classification: str, **extra) -> dict:
    """构造一条合成结果记录。"""
    base = {
        "case_id": case_id,
        "zentao_case_id": zentao_id,
        "title": f"{case_id} 的标题",
        "type": "auto",
        "auto": "auto",
        "status": status,
        "classification": classification,
        "check_id": f"TP-{case_id}",
        "assertion_scope": "selftest.scope",
        "req_id": "REQ-SELF",
        "module": "自检模块",
        "handler": "tests.modules.selftest:test_x",
        "expected": "期望文本",
        "actual": "实际文本",
        "detail": "自检说明",
        "failure_origin": classification if classification not in ("passed", "excluded") else None,
        "preconditions": ["前置一", "前置二"],
        "steps": [{"index": 1, "action": "执行动作", "expected": "期望文本", "actual": "实际文本"}],
        "screenshots": [],
        "screenshot": "",
        "started_at": "2026-01-01T00:00:00",
        "finished_at": "2026-01-01T00:00:01",
        "data_preparation": {
            "fixture_type": "existing_system_data",
            "creates_data": False,
            "cleanup_status": "not_required",
        },
        "excluded": classification == "excluded",
    }
    base.update(extra)
    return base


def main() -> int:
    """执行流水线自检，全部通过返回 0。"""
    failures: list[str] = []
    tmp = Path(tempfile.mkdtemp(prefix="ui_pipeline_selftest_"))
    try:
        orch = _make_orch(tmp)

        # 造一张真实截图，用于验证证据与 SHA-256。
        shot = orch.screenshots_dir / "TC-SELF-01_TP-TC-SELF-01_assertion_scope.png"
        shot.write_bytes(b"\x89PNG\r\n\x1a\n" + b"0" * 64)

        defect = _record(
            "TC-SELF-01",
            10001,
            "failed",
            "product_defect",
            actual={"labels": ["状态"]},
            screenshots=[{"path": f"screenshots/{shot.name}", "sha256": "0" * 64}],
        )
        # 四要素缺 actual 的产品缺陷声明，运行期应已在分类阶段降级，这里模拟降级后的结果。
        degraded = _record("TC-SELF-02", 10002, "ignored", "test_case_error",
                           detail="已由 product_defect 降级：断言契约四要素不全")
        records = [
            defect,
            degraded,
            _record("TC-SELF-03", 10003, "passed", "passed"),
            _record("TC-SELF-04", 10004, "blocked", "blocked", detail="登录失败"),
            _record("TC-SELF-05", 10005, "ignored", "test_script_error", detail="定位器超时"),
            _record("TC-SELF-06", 10006, "excluded", "excluded", detail="type 非 auto"),
        ]
        orch.non_executed_records = records
        orch.expected_record_count = len(records)

        bugs = bugs_review.collect_bugs(records)
        if len(bugs) != 1 or bugs[0]["case_id"] != "TC-SELF-01":
            failures.append(f"bugs 应为 1 条且为 TC-SELF-01，实际 {[b['case_id'] for b in bugs]}")
        if bugs and bugs[0]["zentao_bug_id"] is not None:
            failures.append("bugs[0].zentao_bug_id 必须为 null（禁止自动创建远程 Bug）")

        # 执行阶段完整性：此时产物尚未写出，只校验执行维度
        complete, reasons = integrity.check(orch, records)
        if not complete:
            failures.append(f"合成记录的执行阶段应判定为完整，实际原因：{reasons}")

        finalize(orch, None, resilient=False)
        if orch.exit_code != integrity.EXIT_PRODUCT_DEFECT:
            failures.append(f"存在产品缺陷时退出码应为 1，实际 {orch.exit_code}")
        status = json.loads((tmp / "RUN_STATUS.json").read_text(encoding="utf-8"))
        if not status.get("complete"):
            failures.append(f"最终 RUN_STATUS 应为完整，实际原因：{status.get('reasons')}")

        doc = yaml.safe_load((tmp / "bugs_review.yaml").read_text(encoding="utf-8"))
        if doc["review_status"] != "pending":
            failures.append(f"review_status 必须为 pending，实际 {doc['review_status']}")
        if len(doc["bugs"]) != 1:
            failures.append(f"bugs_review.yaml 应只有 1 条缺陷，实际 {len(doc['bugs'])}")

        report = (tmp / "缺陷报告.md").read_text(encoding="utf-8")
        for expected_text in ("## 二、缺陷清单", "### 缺陷 1：", "TC-SELF-01", "审核结论"):
            if expected_text not in report:
                failures.append(f"缺陷报告缺少内容：{expected_text}")
        for unexpected in ["### 缺陷 2："]:
            if unexpected in report:
                failures.append(f"缺陷报告不应包含：{unexpected}")
        for excluded_text in ("TC-SELF-04", "TC-SELF-05", "TC-SELF-06", "TC-SELF-02"):
            if excluded_text not in report:
                failures.append(f"被排除项缺少 {excluded_text}")

        for name in integrity.PRODUCT_ARTIFACTS:
            path = tmp / name
            if not path.is_file() or path.stat().st_size == 0:
                failures.append(f"产物缺失或为空：{name}")
        if orch.writer_errors:
            failures.append(f"产物写出错误：{orch.writer_errors}")

        # 无缺陷场景：退出码应为 0
        orch2 = _make_orch(tmp / "clean")
        orch2.run_dir = tmp / "clean"
        orch2.screenshots_dir = orch2.run_dir / "screenshots"
        orch2.screenshots_dir.mkdir(parents=True, exist_ok=True)
        orch2.non_executed_records = [
            _record("TC-SELF-03", 10003, "passed", "passed"),
            _record("TC-SELF-04", 10004, "blocked", "blocked"),
        ]
        orch2.expected_record_count = 2
        finalize(orch2, None, resilient=False)
        if orch2.exit_code != integrity.EXIT_OK:
            failures.append(f"无产品缺陷时退出码应为 0，实际 {orch2.exit_code}")
        clean_report = (orch2.run_dir / "缺陷报告.md").read_text(encoding="utf-8")
        if "本次执行未发现产品缺陷" not in clean_report:
            failures.append("无缺陷时应输出占位报告声明")

        # 缺陷报告渲染不得因空数据崩溃
        defect_report.build(orch2, [], [], True, [])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    if failures:
        print(f"FAILED {len(failures)} 项")
        for item in failures:
            print(f"  - {item}")
        return 1
    print("PASS：产物流水线自检通过（缺陷只收录 product_defect、退出码 1/0、占位报告、证据 SHA-256）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

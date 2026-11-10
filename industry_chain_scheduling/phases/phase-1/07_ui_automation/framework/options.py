"""命令行选项定义与筛选条件解析。

所有 ``--*`` 选项集中在此注册，避免钩子与夹具里散落解析逻辑。
按项目硬约束，本模块**不注册** ``--headed`` / ``--headless`` / ``--browser`` / ``--output``，
浏览器显示模式恒为可视（headless=False），不可通过命令行切换。
"""

from __future__ import annotations

from dataclasses import dataclass, field

# 固定可视浏览器；无法启动可视浏览器时必须标记 blocked，严禁切换无头模式。
HEADLESS = False

# 自造测试数据前缀，来源于项目 AGENTS.md 的 data_prefix 约定。
TEST_DATA_PREFIX = "AUTO测试_勿用_"


def _split_values(raw: list[str]) -> list[str]:
    """把可重复传入的选项值按逗号展开并去除空白，丢弃空项。"""
    out: list[str] = []
    for item in raw or []:
        for part in str(item).split(","):
            text = part.strip()
            if text:
                out.append(text)
    return out


def add_options(parser) -> None:
    """向 pytest 注册 UI 自动化的全部命令行选项。"""
    group = parser.getgroup("ui-automation", "产业链生产排程系统 UI 自动化")
    group.addoption(
        "--req",
        action="append",
        default=[],
        metavar="REQ-ID",
        help="需求编号，可重复传入或用逗号分隔，例如 REQ-002,REQ-003",
    )
    group.addoption(
        "--module",
        action="append",
        default=[],
        metavar="NAME",
        help="按 module_case_map.json 中的 module.name 精确匹配模块名",
    )
    group.addoption(
        "--priority",
        action="append",
        default=[],
        metavar="P",
        help="按本地用例 YAML 的 priority 精确匹配，例如 P1",
    )
    group.addoption(
        "--zentao-case-id",
        action="append",
        default=[],
        metavar="ID",
        help="数字禅道用例编号，可重复传入或用逗号分隔，仅作为本地字段匹配",
    )
    group.addoption(
        "--run-label",
        default=None,
        metavar="LABEL",
        help="强制指定 RUN 目录名中的模块标签；缺省时按选中用例所属模块自动推导",
    )
    group.addoption(
        "--dry-run",
        action="store_true",
        default=False,
        help="不启动浏览器、不执行用例，仅验证筛选与全部产物写出链路",
    )
    group.addoption(
        "--self-test",
        action="store_true",
        default=False,
        help="框架自检：用桩替代浏览器（不访问被测系统、不造数据），仅验证执行与产物链路；"
        "自动等价于追加 --no-update-registry --no-handoff",
    )
    group.addoption(
        "--allow-empty",
        action="store_true",
        default=False,
        help="无匹配用例时静默退出 0 且不创建 RUN 目录；缺省为报错退出 4",
    )
    group.addoption(
        "--max-run-seconds",
        type=int,
        default=0,
        metavar="N",
        help="超过该秒数时标记 RUN 不完整；0 表示不限制",
    )
    group.addoption(
        "--no-update-registry",
        action="store_true",
        default=False,
        help="本次执行不更新 data/REQ-{req_id}.yaml 数据登记索引",
    )
    group.addoption(
        "--no-handoff",
        action="store_true",
        default=False,
        help="本次执行不更新 HANDOFF.md",
    )


@dataclass(frozen=True)
class SelectionFilter:
    """一次执行的选择条件；字段为空列表表示该条件不参与过滤。"""

    reqs: list[str] = field(default_factory=list)
    modules: list[str] = field(default_factory=list)
    priorities: list[str] = field(default_factory=list)
    zentao_ids: list[int] = field(default_factory=list)

    @classmethod
    def from_config(cls, config) -> "SelectionFilter":
        """从 pytest 配置对象读取全部筛选选项并构造不可变条件对象。"""
        opt = config.getoption
        return cls(
            reqs=_split_values(opt("--req")),
            modules=_split_values(opt("--module")),
            priorities=_split_values(opt("--priority")),
            zentao_ids=[int(value) for value in _split_values(opt("--zentao-case-id"))],
        )

    def is_empty(self) -> bool:
        """返回是否未指定任何筛选条件；为空时由 nodeid 选择独立决定候选集。"""
        return not (self.reqs or self.modules or self.priorities or self.zentao_ids)

    def match(self, entry: dict, local_case: dict) -> bool:
        """判断单条用例是否同时满足全部已指定的筛选条件（条件之间为与关系）。"""
        if self.reqs and str(entry.get("req_id", "")) not in self.reqs:
            return False
        if self.modules and str((entry.get("module") or {}).get("name", "")) not in self.modules:
            return False
        if self.priorities and str((local_case or {}).get("priority", "")) not in self.priorities:
            return False
        if self.zentao_ids:
            try:
                if int(entry.get("zentao_case_id", -1)) not in self.zentao_ids:
                    return False
            except (TypeError, ValueError):
                return False
        return True

    def describe(self) -> dict:
        """返回筛选条件的可序列化描述，供 selection.yaml 记录。"""
        return {
            "req": self.reqs or None,
            "module": self.modules or None,
            "priority": self.priorities or None,
            "zentao_case_id": self.zentao_ids or None,
        }

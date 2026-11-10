"""07_ui_automation 根目录 conftest：注册命令行选项。

夹具与钩子分别由 ``framework.fixtures`` 与 ``framework.plugin`` 提供，
两者通过 ``pytest.ini`` 的 ``-p`` 加载，本文件只负责选项注册，保持职责单一。

执行示例（工作目录 07_ui_automation）：
    pytest --req REQ-002
    pytest --req REQ-004 --priority P1
    pytest tests/modules/scheduling/test_target_goal.py::test_tc_002_01
    pytest --self-test          # 框架自检：不访问被测系统
    pytest --dry-run            # 只验证筛选与产物链路，不执行用例
"""

from __future__ import annotations

from framework import options


def pytest_addoption(parser) -> None:
    """注册 UI 自动化的全部命令行选项。"""
    options.add_options(parser)

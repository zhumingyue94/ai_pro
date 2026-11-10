"""模块级 UI 执行入口占位。

本项目尚未落地业务 Page Object；请先按实页探查实现 pages/，
再参考 execute-agent 补齐模块级批量执行逻辑。当前请使用
tests/run_case.py 或 pytest 定向执行已实现的用例。
"""

from __future__ import annotations


def main() -> int:
    """打印占位说明并返回非零退出码，避免误当作可执行入口。"""
    print(
        "run_module.py is a placeholder for 商品禽养殖系统. "
        "Implement business Page Objects first, then wire module runners."
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

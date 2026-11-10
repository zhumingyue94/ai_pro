"""产物写出器集合：一文件一产物，每个写出器独立容错。

每个模块暴露统一的写入入口，由 ``framework.plugin.finalize`` 统一编排；
单个产物写出失败只记入 ``RUN_STATUS.json.writer_errors``，不影响其他产物。
"""

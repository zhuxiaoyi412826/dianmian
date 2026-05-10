
"""
兼容模块 - 解决 coze_coding_utils 导入 utils.log.loop_trace 的问题
实际使用正确的 coze_coding_utils.log.loop_trace 模块
"""
from coze_coding_utils.log.loop_trace import init_run_config, init_agent_config

__all__ = [
    'init_run_config',
    'init_agent_config'
]

"""
模拟面试官 Agent
根据用户输入的岗位JD，进行专业的连环追问面试
支持：语音对话 | 简历分析 | 面试评估报告
"""
import os
import json
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langgraph.graph import MessagesState
from langchain_core.messages import AnyMessage
from storage.memory.memory_saver import get_memory_saver
from tools.voice_tools import text_to_speech, speech_to_text, speech_to_text_base64
from tools.resume_tools import analyze_resume_text, extract_resume_highlights
from tools.evaluation_tools import generate_interview_report, export_report_markdown

LLM_CONFIG = "config/agent_llm_config.json"

# DeepSeek API 配置
DEEPSEEK_API_KEY = "sk-0ab12c9e84ae4d75b5b78fc6a4f2edab"
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_MODEL = "deepseek-chat"

# 可用工具列表
TOOLS = [
    text_to_speech,
    speech_to_text,
    speech_to_text_base64,
    analyze_resume_text,
    extract_resume_highlights,
    generate_interview_report,
    export_report_markdown,
]

def build_agent(ctx=None):
    """
    构建模拟面试官 Agent
    具备以下能力：
    1. 接收并分析岗位JD
    2. 根据JD设计面试问题
    3. 对用户回答进行追问
    4. 多轮对话记忆
    5. 语音对话（语音输入+语音输出）
    6. 简历智能分析
    7. 面试评估报告
    """
    # 使用当前文件的相对路径找 config 目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_path = os.path.abspath(os.path.join(current_dir, '..', '..'))
    config_path = os.path.join(workspace_path, LLM_CONFIG)

    with open(config_path, 'r', encoding='utf-8') as f:
        cfg = json.load(f)

    # 使用 DeepSeek API
    llm = ChatOpenAI(
        model=DEEPSEEK_MODEL,
        api_key=DEEPSEEK_API_KEY,
        base_url=DEEPSEEK_BASE_URL,
        temperature=cfg['config'].get('temperature', 0.7),
        streaming=True,
        timeout=cfg['config'].get('timeout', 600),
    )

    # 使用标准MessagesState，checkpointer会自动管理对话历史
    return create_agent(
        model=llm,
        system_prompt=cfg.get("sp"),
        tools=TOOLS,
        checkpointer=get_memory_saver(),
        state_schema=MessagesState,
    )

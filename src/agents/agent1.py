"""
模拟面试官 Agent
根据用户输入的岗位JD，进行专业的连环追问面试
支持：语音对话 | 简历分析 | 面试评估报告
"""
import os
import json
from langchain_openai import ChatOpenAI
from langgraph.graph import MessagesState, StateGraph, END
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from storage.memory.memory_saver import get_memory_saver

LLM_CONFIG = "config/agent_llm_config.json"

# DeepSeek API 配置
DEEPSEEK_API_KEY = "sk-0ab12c9e84ae4d75b5b78fc6a4f2edab"
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_MODEL = "deepseek-chat"

def build_agent(ctx=None):
    """
    构建模拟面试官 Agent
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

    # 创建提示模板
    system_prompt = cfg.get("sp", "")
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="messages"),
    ])

    # 创建简单的链
    chain = prompt | llm

    # 创建 langgraph 工作流
    def chat_node(state):
        messages = state.get("messages", [])
        response = chain.invoke({"messages": messages})
        return {"messages": [response]}

    graph_builder = StateGraph(MessagesState)
    graph_builder.add_node("chat", chat_node)
    graph_builder.set_entry_point("chat")
    graph_builder.add_edge("chat", END)

    # 编译图
    graph = graph_builder.compile(checkpointer=get_memory_saver())
    
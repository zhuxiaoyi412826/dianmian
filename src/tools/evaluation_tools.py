"""
面试评估报告生成工具
"""
import json
from typing import Dict, Any, List
from langchain.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI


# 评估报告生成的System Prompt
EVALUATION_PROMPT = """你是一个资深的技术面试官，拥有10年以上的面试评估经验。请根据以下面试对话记录，对候选人的表现进行专业评估。

面试记录：
{conversation_history}

候选人背景：
{candidate_background}

请生成一份结构化的面试评估报告，包含以下内容：

1. **基本信息**
   - 候选人姓名/编号
   - 面试岗位
   - 面试时长
   - 评估日期

2. **技术能力评估**（1-10分）
   - 评分及理由
   - 掌握的技能
   - 需要加强的领域

3. **各维度评分**
   - 技术深度：X/10
   - 项目经验：X/10
   - 逻辑思维：X/10
   - 沟通表达：X/10
   - 学习能力：X/10
   - 抗压能力：X/10

4. **面试问答摘要**
   - 主要讨论的技术话题
   - 候选人的回答亮点
   - 存在的不足

5. **综合评价**
   - 总体评价（2-3句话）
   - 录用建议：强烈推荐/推荐/待定/不推荐

6. **改进建议**
   - 具体可执行的改进建议（3-5条）

请确保评估客观公正，评分有理有据。输出格式为清晰的Markdown。"""


def _get_text_content(response) -> str:
    """安全地获取响应的文本内容"""
    if hasattr(response, 'content'):
        content = response.content
        if isinstance(content, str):
            return content
        elif isinstance(content, list):
            # 处理list类型，提取文本
            parts = []
            for item in content:
                if isinstance(item, dict):
                    if 'text' in item:
                        parts.append(item['text'])
                    elif 'type' in item and item['type'] == 'text':
                        parts.append(str(item))
                else:
                    parts.append(str(item))
            return '\n'.join(parts)
        else:
            return str(content)
    return str(response)


@tool
def generate_interview_report(
    conversation_history: str,
    candidate_background: str = ""
) -> str:
    """
    根据面试对话记录生成评估报告。
    
    Args:
        conversation_history: 完整的面试对话记录
        candidate_background: 候选人背景信息（如简历分析结果）
    
    Returns:
        Markdown格式的面试评估报告
    """
    try:
        api_key = "sk-0ab12c9e84ae4d75b5b78fc6a4f2edab"
        base_url = "https://api.deepseek.com"
        
        llm = ChatOpenAI(
            model="deepseek-chat",
            api_key=api_key,
            base_url=base_url,
            temperature=0.5,
            max_tokens=3000
        )
        
        # 构建提示
        prompt = EVALUATION_PROMPT.format(
            conversation_history=conversation_history,
            candidate_background=candidate_background or "无详细背景信息"
        )
        
        messages = [
            SystemMessage(content="你是一个专业、客观的面试评估专家。"),
            HumanMessage(content=prompt)
        ]
        
        response = llm.invoke(messages)
        raw_content = _get_text_content(response)
        return raw_content
        
    except Exception as e:
        return f"""# 面试评估报告生成失败

抱歉，评估报告生成过程中出现错误：{str(e)}

## 建议

请稍后重试，或手动整理面试记录进行评估。
"""


@tool
def generate_quick_score(conversation_history: str) -> str:
    """
    快速生成面试评分（轻量版评估）。
    
    Args:
        conversation_history: 面试对话记录
    
    Returns:
        JSON格式的快速评分结果
    """
    try:
        api_key = "sk-0ab12c9e84ae4d75b5b78fc6a4f2edab"
        base_url = "https://api.deepseek.com"
        
        llm = ChatOpenAI(
            model="deepseek-chat",
            api_key=api_key,
            base_url=base_url,
            temperature=0.3,
            max_tokens=500
        )
        
        score_prompt = f"""请根据以下面试对话，快速评估候选人在各维度的表现（1-10分）。

面试记录：
{conversation_history}

请以JSON格式输出：
{{
    "technical_depth": {{"score": 分数, "reason": "评分理由"}},
    "project_experience": {{"score": 分数, "reason": "评分理由"}},
    "logical_thinking": {{"score": 分数, "reason": "评分理由"}},
    "communication": {{"score": 分数, "reason": "评分理由"}},
    "learning_ability": {{"score": 分数, "reason": "评分理由"}},
    "overall_score": 平均分,
    "recommendation": "强烈推荐/推荐/待定/不推荐"
}}

只输出JSON，不要其他文字。"""
        
        messages = [HumanMessage(content=score_prompt)]
        
        response = llm.invoke(messages)
        raw_content = _get_text_content(response)
        
        # 提取JSON
        content = raw_content
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]
        
        # 确保返回的是字符串
        result = content.strip() if content else "{}"
        return result
        
    except Exception as e:
        return json.dumps({
            "error": str(e),
            "recommendation": "评估失败"
        }, ensure_ascii=False)


@tool
def export_report_markdown(report_content: str, filename: str = "interview_report.md") -> str:
    """
    将评估报告保存为Markdown文件。
    
    Args:
        report_content: 报告内容（Markdown格式）
        filename: 保存的文件名
    
    Returns:
        格式: "success|filepath" 或 "error|message"
    """
    import os
    
    try:
        # 确保目录存在
        output_dir = "/tmp/interview_reports"
        os.makedirs(output_dir, exist_ok=True)
        
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        return f"success|报告已保存至: {filepath}"
        
    except Exception as e:
        return f"error|保存失败: {str(e)}"
